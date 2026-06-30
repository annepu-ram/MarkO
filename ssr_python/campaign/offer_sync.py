"""
Offer → ContentItem materialization.

Strategy imp.md decision 1: campaign offer content and the Content Library are
ONE store, not two. A campaign's offer fields (offer/CTAs/benefits/proof_points/
objections/faqs) are persisted as typed ``ContentItem`` rows — the same durable
records the Library shows and the RAG path reads — instead of living only as
opaque JSON on ``CampaignOffer``.

This module generalizes the message→ContentItem mapping that
``routes/brand.py::save_from_campaign`` already does for kept messages, so both
the offer PATCH and the "save from campaign" action share one code path.

Design:
  * **Idempotent upsert.** Re-running the sync after a debounced offer save does
    not create duplicates: each (campaign, category, content) maps to at most one
    campaign-sourced item. Items whose source content disappeared from the offer
    are pruned (only campaign-sourced ones for this campaign+category).
  * **Typed via the canonical registry.** Categories are catalog keys
    (``benefit``/``proof``/``objection``/``faq``/``offer``/``cta``) and slots use
    the registry's slot schema via ``slots_from_content`` /
    ``derive_content_from_slots`` (composite FAQ/objection carry both fields).
  * **Provenance.** ``source='campaign'``, ``source_campaign_id``,
    ``channel='landing_page'``, brand/product inherited from the campaign.
"""

import hashlib

from extensions import db
from models import ContentItem
from campaign.content_type_catalog import slots_from_content, derive_content_from_slots


def build_campaign_content_item(campaign, category, content, slots, *,
                                source_message_id=None, product_id=None,
                                is_pinned=False, status="approved"):
    """Construct (but do not add) a campaign-sourced ``ContentItem``.

    The single shared constructor for campaign→Library materialization, used by
    both the offer sync (per offer field) and ``save_from_campaign`` (per kept
    message). Centralizes provenance tagging (source/channel/brand/product/tone)
    so the two paths cannot drift.

    Args:
        campaign: Campaign ORM instance.
        category: catalog content type (e.g. ``benefit``, ``faq``).
        content: primary display string.
        slots: slot dict for the type (composite parts, cta role/style, ...).
        source_message_id: link back to a CampaignMessage when materializing a
            kept message; None for offer-field materialization.
        product_id: explicit product attribution; defaults to the campaign's
            single attached product when unambiguous.
        is_pinned: pin the item in the Library.
        status: ContentItem status (default 'approved').
    """
    item = ContentItem(
        org_id=campaign.org_id,
        brand_id=campaign.brand_id,
        product_id=product_id if product_id is not None else _single_product_id(campaign),
        category=category,
        status=status,
        source="campaign",
        channel="landing_page",
        content=content,
        title=f"Campaign: {campaign.name}",
        source_campaign_id=campaign.id,
        source_message_id=source_message_id,
        tone=campaign.brand.tone if campaign.brand else None,
        is_pinned=is_pinned,
    )
    item.set_slots(slots or {})
    return item


def _single_product_id(campaign):
    """The campaign's product id when exactly one is attached, else None.

    Mirrors save_from_campaign: ambiguous multi-product campaigns leave
    product_id unset so items stay brand-scoped rather than mis-attributed.
    """
    product_ids = [
        cp.product_id for cp in (campaign.campaign_products or [])
        if cp.product_id
    ]
    return product_ids[0] if len(product_ids) == 1 else None


def _content_hash(category, content, slots):
    """Stable identity for an offer-derived item (dedupe / upsert key).

    Hashes category + primary content + composite slot parts so editing a FAQ's
    answer (not just its question) produces a distinct identity.
    """
    parts = [category, str(content or "")]
    for key in sorted((slots or {}).keys()):
        parts.append(f"{key}={slots[key]}")
    raw = "".join(parts)
    return hashlib.sha1(raw.encode("utf-8")).hexdigest()


def _iter_offer_content(offer):
    """Yield (category, content, slots) tuples for every non-empty offer field.

    Composite types (faq/objection) carry their structured parts in slots;
    primitives use the registry's primary slot. Empty values are skipped.
    """
    if offer is None:
        return

    # Primary offer statement + CTAs.
    if (offer.offer or "").strip():
        yield "offer", offer.offer.strip(), slots_from_content("offer", offer.offer)
    if (offer.primary_cta or "").strip():
        yield "cta", offer.primary_cta.strip(), {
            **slots_from_content("cta", offer.primary_cta), "role": "primary", "style": "direct",
        }
    if (offer.secondary_cta or "").strip():
        yield "cta", offer.secondary_cta.strip(), {
            **slots_from_content("cta", offer.secondary_cta), "role": "secondary", "style": "soft",
        }

    # List fields.
    for benefit in offer.get_benefits():
        text = str(benefit or "").strip()
        if text:
            yield "benefit", text, slots_from_content("benefit", text)
    for proof in offer.get_proof_points():
        text = str(proof or "").strip()
        if text:
            yield "proof", text, slots_from_content("proof", text)

    # Object fields — objections + faqs carry both parts in slots.
    for obj in offer.get_objections():
        concern, response = _objection_parts(obj)
        if concern:
            yield "objection", concern, {"concern": concern, "response": response}
    for faq in offer.get_faqs():
        if isinstance(faq, dict):
            question = str(faq.get("question") or "").strip()
            answer = str(faq.get("answer") or "").strip()
            if question:
                yield "faq", question, {"question": question, "answer": answer}


def _objection_parts(obj):
    """Extract (concern, response) from an objection entry (str or dict)."""
    if isinstance(obj, dict):
        concern = str(obj.get("concern") or obj.get("content") or "").strip()
        response = str(obj.get("response") or "").strip()
        return concern, response
    return str(obj or "").strip(), ""


def sync_offer_to_content_items(campaign, *, commit=False):
    """Materialize a campaign's offer fields as typed ``ContentItem`` rows.

    Idempotent: safe to call after every offer PATCH. Creates missing items,
    leaves matching ones untouched, and prunes campaign-sourced items whose
    source field was removed from the offer.

    Args:
        campaign: Campaign ORM instance (with ``offer`` loaded).
        commit: when True, commit the session; otherwise the caller commits.

    Returns:
        dict: {created: int, kept: int, pruned: int, items: [ContentItem]} —
        ``items`` is the full current set of offer-derived items for the campaign.
    """
    offer = campaign.offer
    org_id = campaign.org_id

    # Existing campaign-sourced items for this campaign, keyed by content hash.
    # Only offer-derived items (no source_message_id) participate in this sync,
    # so save_from_campaign's message-derived items are never pruned here.
    existing = ContentItem.query.filter_by(
        org_id=org_id,
        source="campaign",
        source_campaign_id=campaign.id,
        source_message_id=None,
    ).all()
    existing_by_hash = {
        _content_hash(it.category, it.content, it.get_slots()): it
        for it in existing
    }

    desired = {}  # hash -> (category, content, slots)
    for category, content, slots in _iter_offer_content(offer):
        derived = derive_content_from_slots(category, slots) or content
        h = _content_hash(category, derived, slots)
        desired[h] = (category, derived, slots)

    created, kept, items = 0, 0, []
    for h, (category, content, slots) in desired.items():
        item = existing_by_hash.get(h)
        if item is not None:
            kept += 1
            items.append(item)
            continue
        item = build_campaign_content_item(campaign, category, content, slots)
        db.session.add(item)
        created += 1
        items.append(item)

    # Prune campaign-sourced items no longer backed by the offer.
    pruned = 0
    for h, item in existing_by_hash.items():
        if h not in desired:
            db.session.delete(item)
            pruned += 1

    if commit:
        db.session.commit()

    return {"created": created, "kept": kept, "pruned": pruned, "items": items}
