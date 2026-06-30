"""
Canonical content-type registry — the single source of truth for content types.

Historically the codebase carried TWO diverging content-type vocabularies:

  * ``campaign/vocabulary.py`` CONTENT_TYPE / COMPOSITE_TYPES / GROUP_KEY_TO_TYPE
    — the ontology the recipe engine, validators, content normalization, and
    content-ref resolver read from (uses names like ``title``, ``feature``,
    ``form_spec`` plus the campaign atoms ``pain_point`` / ``promise``).
  * ``campaign/content_type_catalog.py`` CONTENT_TYPES — the Content Library
    catalog with slot schemas backing the UI + ``ContentItem.category`` (uses
    names like ``headline``, ``product_feature``, ``form`` plus channel-asset
    types like ``ad_copy``).

Both are now DERIVED from this registry. Each concept is declared once, with the
name it carries in each view (``catalog_key`` / ``ontology_key``), so the two
naming systems stay reconciled. Add a content type here once; both views update.

A registry entry:

  concept           unique registry id (== catalog_key when present, else ontology_key)
  catalog_key       key in the Content Library catalog / ``ContentItem.category``,
                    or None when the concept is ontology-only (primitives, atoms)
  ontology_key      key in ``vocabulary.CONTENT_TYPE``, or None when the concept is
                    a catalog/channel-asset type the ontology does not model
  label             human-facing label
  family            catalog family grouping key
  description       short catalog description
  composite         True when the ontology treats this as a composite type
                    (extra fields stored in slots)
  group_key         campaign shorthand plural key for grouped content input
                    (e.g. ``benefits`` -> benefit), or None
  channel_affinity  channels this type renders to (catalog metadata)
  page_usable       can appear on a landing page (catalog metadata)
  proof_sensitive   carries claims that need provenance (catalog metadata)
  slot_schema       raw slot-field definitions for composite catalog types
                    (normalized by content_type_catalog at import time)

See ``docs/CONTENT_TYPES_AUDIT.md`` for the reconciliation rationale.
"""

# --- registry data ------------------------------------------------------------

CONTENT_REGISTRY = [
    # --- core message ---------------------------------------------------------
    {
        "concept": "headline",
        "catalog_key": "headline",
        "ontology_key": "title",
        "label": "Headline",
        "family": "core_message",
        "description": "Primary campaign or section headline.",
        "composite": False,
        "group_key": None,
        "channel_affinity": ["landing_page", "general"],
        "page_usable": True,
        "proof_sensitive": False,
        "slot_schema": [
            {"key": "headline", "label": "Headline", "type": "text", "primitive_type": "headline", "required": False, "placeholder": "Your primary message to visitors", "help_text": "Short, clear headline copy."},
        ],
    },
    {
        "concept": "subheadline",
        "catalog_key": "subheadline",
        "ontology_key": "subheadline",
        "label": "Subheadline",
        "family": "core_message",
        "description": "Supporting line that expands the headline.",
        "composite": False,
        "group_key": None,
        "channel_affinity": ["landing_page", "general"],
        "page_usable": True,
        "proof_sensitive": False,
        "slot_schema": [
            {"key": "subheadline", "label": "Subheadline", "type": "textarea", "primitive_type": "paragraph", "required": False, "placeholder": "1-2 sentences expanding the headline", "help_text": "Supporting copy that explains the promise."},
        ],
    },
    {
        "concept": "tagline",
        "catalog_key": "tagline",
        "ontology_key": "tagline",
        "label": "Tagline",
        "family": "core_message",
        "description": "Short reusable brand or product tagline.",
        "composite": False,
        "group_key": None,
        "channel_affinity": ["general", "landing_page"],
        "page_usable": True,
        "proof_sensitive": False,
        "slot_schema": [
            {"key": "tagline", "label": "Tagline", "type": "text", "primitive_type": "headline", "required": False, "placeholder": "A short reusable brand or product line", "help_text": "Compact positioning line used across pages and campaigns."},
        ],
    },
    {
        "concept": "value_proposition",
        "catalog_key": "value_proposition",
        "ontology_key": "value_proposition",
        "label": "Value proposition",
        "family": "core_message",
        "description": "Clear statement of the value delivered to the audience.",
        "composite": True,
        "group_key": None,
        "channel_affinity": ["general", "landing_page", "email", "ad"],
        "page_usable": True,
        "proof_sensitive": False,
        "slot_schema": [
            {"key": "headline", "label": "Headline", "primitive_type": "headline", "required": False, "help_text": "Short value-led heading."},
            {"key": "paragraph", "label": "Paragraph", "primitive_type": "paragraph", "required": False, "help_text": "One or two sentences explaining the value."},
            {"key": "supporting_points", "label": "Supporting points", "primitive_type": "paragraph", "required": False, "help_text": "Optional bullets or short supporting points."},
        ],
    },
    {
        "concept": "benefit",
        "catalog_key": "benefit",
        "ontology_key": "benefit",
        "label": "Benefit",
        "family": "core_message",
        "description": "Outcome or advantage the audience receives.",
        "composite": True,
        "group_key": "benefits",
        "channel_affinity": ["general", "landing_page", "email", "ad"],
        "page_usable": True,
        "proof_sensitive": False,
        "slot_schema": [
            {"key": "headline", "label": "Headline", "primitive_type": "headline", "required": False, "help_text": "Benefit heading."},
            {"key": "paragraph", "label": "Paragraph", "primitive_type": "paragraph", "required": False, "help_text": "Benefit explanation."},
        ],
    },
    {
        "concept": "cta",
        "catalog_key": "cta",
        "ontology_key": "cta",
        "label": "CTA",
        "family": "core_message",
        "description": "Call-to-action copy such as a button or final prompt.",
        "composite": True,
        "group_key": "calls_to_action",
        "channel_affinity": ["general", "landing_page", "email", "ad"],
        "page_usable": True,
        "proof_sensitive": False,
        "slot_schema": [
            {"key": "headline", "label": "Headline", "primitive_type": "headline", "required": False, "help_text": "Prompt or conversion headline."},
            {"key": "paragraph", "label": "Paragraph", "primitive_type": "paragraph", "required": False, "help_text": "Short supporting reason to act."},
            {"key": "button_label", "label": "Button label", "primitive_type": "cta_label", "required": False, "help_text": "Action text for the button.", "max_length": 80},
            {"key": "link", "label": "Link", "primitive_type": "url", "required": False, "help_text": "Button destination."},
        ],
    },
    # --- offer ----------------------------------------------------------------
    {
        "concept": "offer",
        "catalog_key": "offer",
        "ontology_key": "offer",
        "label": "Offer",
        "family": "offer",
        "description": "Specific deal, package, incentive, or conversion offer.",
        "composite": True,
        "group_key": "offers",
        "channel_affinity": ["general", "landing_page", "email", "ad", "ecommerce"],
        "page_usable": True,
        "proof_sensitive": False,
        "slot_schema": [
            {"key": "headline", "label": "Headline", "primitive_type": "headline", "required": False, "help_text": "Offer heading."},
            {"key": "details", "label": "Details", "primitive_type": "paragraph", "required": False, "help_text": "What is included in the offer."},
            {"key": "code", "label": "Code", "primitive_type": "text", "required": False, "help_text": "Optional promo or redemption code."},
            {"key": "expiry_note", "label": "Expiry note", "primitive_type": "paragraph", "required": False, "help_text": "Optional deadline or eligibility note."},
            {"key": "cta_label", "label": "CTA label", "primitive_type": "cta_label", "required": False, "help_text": "Action text for the offer."},
        ],
    },
    {
        "concept": "promotion",
        "catalog_key": "promotion",
        "ontology_key": None,
        "label": "Promotion",
        "family": "offer",
        "description": "Time-bound promotion or campaign-specific incentive.",
        "composite": False,
        "group_key": None,
        "channel_affinity": ["landing_page", "email", "ad", "social", "ecommerce"],
        "page_usable": True,
        "proof_sensitive": False,
        "slot_schema": [
            {"key": "headline", "label": "Promotion headline", "type": "text", "primitive_type": "headline", "required": False, "placeholder": "e.g., Summer launch offer"},
            {"key": "details", "label": "Promotion details", "type": "textarea", "primitive_type": "paragraph", "required": False, "placeholder": "What is included, who it is for, and why it matters"},
            {"key": "expiry_note", "label": "Expiry or eligibility note", "type": "text", "primitive_type": "text", "required": False, "placeholder": "e.g., Ends June 30"},
            {"key": "cta_label", "label": "CTA label", "type": "text", "primitive_type": "cta_label", "required": False, "placeholder": "e.g., Claim offer", "max_length": 80},
        ],
    },
    {
        "concept": "guarantee",
        "catalog_key": "guarantee",
        "ontology_key": "guarantee",
        "label": "Guarantee",
        "family": "offer",
        "description": "Risk reversal or guarantee statement.",
        "composite": True,
        "group_key": "guarantees",
        "channel_affinity": ["general", "landing_page", "email", "ad"],
        "page_usable": True,
        "proof_sensitive": True,
        "slot_schema": [
            {"key": "statement", "label": "Guarantee statement", "type": "textarea", "primitive_type": "paragraph", "required": False, "placeholder": "State the guarantee or risk reversal clearly"},
            {"key": "conditions", "label": "Conditions", "type": "textarea", "primitive_type": "paragraph", "required": False, "placeholder": "Optional terms, eligibility, or limitations"},
        ],
    },
    {
        "concept": "announcement",
        "catalog_key": "announcement",
        "ontology_key": "announcement",
        "label": "Announcement",
        "family": "offer",
        "description": "Launch, update, event, or timely business announcement.",
        "composite": True,
        "group_key": None,
        "channel_affinity": ["general", "landing_page", "email", "social"],
        "page_usable": True,
        "proof_sensitive": False,
        "slot_schema": [
            {"key": "headline", "label": "Announcement headline", "type": "text", "primitive_type": "headline", "required": False, "placeholder": "e.g., New location now open"},
            {"key": "details", "label": "Details", "type": "textarea", "primitive_type": "paragraph", "required": False, "placeholder": "What changed, when it happens, and why it matters"},
            {"key": "date_note", "label": "Date or timing note", "type": "text", "primitive_type": "text", "required": False, "placeholder": "e.g., Starting July 1"},
        ],
    },
    # --- proof ----------------------------------------------------------------
    {
        "concept": "proof",
        "catalog_key": "proof",
        "ontology_key": "proof",
        "label": "Proof",
        "family": "proof",
        "description": "Credibility claim, metric, credential, or evidence.",
        "composite": True,
        "group_key": "proof",
        "channel_affinity": ["general", "landing_page", "email", "ad"],
        "page_usable": True,
        "proof_sensitive": True,
        "slot_schema": [
            {"key": "claim", "label": "Claim", "type": "textarea", "primitive_type": "proof", "required": False, "placeholder": "Credibility claim, metric, credential, or evidence"},
            {"key": "metric", "label": "Metric", "type": "text", "primitive_type": "stat", "required": False, "placeholder": "e.g., 98% satisfaction"},
            {"key": "source_note", "label": "Source note", "type": "text", "primitive_type": "text", "required": False, "placeholder": "Where the proof came from"},
        ],
    },
    {
        "concept": "testimonial",
        "catalog_key": "testimonial",
        "ontology_key": "testimonial",
        "label": "Testimonial",
        "family": "proof",
        "description": "Customer quote or endorsement.",
        "composite": True,
        "group_key": "testimonials",
        "channel_affinity": ["general", "landing_page", "email", "ad"],
        "page_usable": True,
        "proof_sensitive": True,
        "slot_schema": [
            {"key": "quote", "label": "Quote", "primitive_type": "quote", "required": False, "help_text": "Customer quote or endorsement."},
            {"key": "author", "label": "Author", "primitive_type": "text", "required": False, "help_text": "Person credited for the quote."},
            {"key": "author_role", "label": "Author role", "primitive_type": "text", "required": False, "help_text": "Optional role or title."},
            {"key": "company", "label": "Company", "primitive_type": "text", "required": False, "help_text": "Optional company name."},
            {"key": "rating", "label": "Rating", "primitive_type": "stat", "required": False, "help_text": "Optional numeric rating."},
        ],
    },
    {
        "concept": "case_study",
        "catalog_key": "case_study",
        "ontology_key": "case_study",
        "label": "Case study",
        "family": "proof",
        "description": "Customer story, result, or mini case study.",
        "composite": True,
        "group_key": None,
        "channel_affinity": ["general", "landing_page", "email"],
        "page_usable": True,
        "proof_sensitive": True,
        "slot_schema": [
            {"key": "customer", "label": "Customer", "type": "text", "primitive_type": "text", "required": False, "placeholder": "Customer, segment, or company"},
            {"key": "problem", "label": "Problem", "type": "textarea", "primitive_type": "paragraph", "required": False, "placeholder": "What challenge did they face?"},
            {"key": "result", "label": "Result", "type": "textarea", "primitive_type": "proof", "required": False, "placeholder": "What changed after using the offer?"},
            {"key": "quote", "label": "Quote", "type": "textarea", "primitive_type": "quote", "required": False, "placeholder": "Optional customer quote"},
        ],
    },
    # --- objections & FAQ -----------------------------------------------------
    {
        "concept": "faq",
        "catalog_key": "faq",
        "ontology_key": "faq",
        "label": "FAQ",
        "family": "objections",
        "description": "Frequently asked question and answer.",
        "composite": True,
        "group_key": "faqs",
        "channel_affinity": ["general", "landing_page"],
        "page_usable": True,
        "proof_sensitive": False,
        "slot_schema": [
            {"key": "question", "label": "Question", "primitive_type": "question", "required": False, "help_text": "The question being answered."},
            {"key": "answer", "label": "Answer", "primitive_type": "answer", "required": False, "help_text": "Clear answer to the question."},
        ],
    },
    {
        "concept": "objection",
        "catalog_key": "objection",
        "ontology_key": "objection",
        "label": "Objection",
        "family": "objections",
        "description": "Buyer concern and response.",
        "composite": True,
        "group_key": "objections",
        "channel_affinity": ["general", "landing_page", "email", "ad"],
        "page_usable": True,
        "proof_sensitive": False,
        "slot_schema": [
            {"key": "concern", "label": "Concern", "primitive_type": "question", "required": False, "help_text": "Buyer concern or objection."},
            {"key": "response", "label": "Response", "primitive_type": "answer", "required": False, "help_text": "Response to the concern."},
        ],
    },
    # --- product --------------------------------------------------------------
    {
        "concept": "product_feature",
        "catalog_key": "product_feature",
        "ontology_key": "feature",
        "label": "Product feature",
        "family": "product",
        "description": "Capability, service detail, or feature.",
        "composite": True,
        "group_key": "features",
        "channel_affinity": ["general", "landing_page", "email", "ad", "ecommerce"],
        "page_usable": True,
        "proof_sensitive": False,
        "slot_schema": [
            {"key": "headline", "label": "Headline", "primitive_type": "headline", "required": False, "help_text": "Feature heading."},
            {"key": "paragraph", "label": "Paragraph", "primitive_type": "paragraph", "required": False, "help_text": "Feature explanation."},
            {"key": "proof_note", "label": "Proof note", "primitive_type": "proof", "required": False, "help_text": "Optional proof or evidence note."},
        ],
    },
    {
        "concept": "product_spec",
        "catalog_key": "product_spec",
        "ontology_key": None,
        "label": "Product spec",
        "family": "product",
        "description": "Technical specification, SKU detail, or product fact.",
        "composite": False,
        "group_key": None,
        "channel_affinity": ["general", "landing_page", "ecommerce"],
        "page_usable": True,
        "proof_sensitive": False,
        "slot_schema": [
            {"key": "name", "label": "Spec name", "type": "text", "primitive_type": "text", "required": False, "placeholder": "e.g., Battery life"},
            {"key": "value", "label": "Spec value", "type": "text", "primitive_type": "text", "required": False, "placeholder": "e.g., Up to 18 hours"},
            {"key": "note", "label": "Note", "type": "textarea", "primitive_type": "paragraph", "required": False, "placeholder": "Optional details or context"},
        ],
    },
    {
        "concept": "comparison",
        "catalog_key": "comparison",
        "ontology_key": "comparison",
        "label": "Comparison",
        "family": "product",
        "description": "Comparison against alternatives, plans, or competitors.",
        "composite": True,
        "group_key": None,
        "channel_affinity": ["general", "landing_page", "email"],
        "page_usable": True,
        "proof_sensitive": True,
        "slot_schema": [
            {"key": "subject", "label": "Subject", "primitive_type": "text", "required": False, "help_text": "What is being compared."},
            {"key": "alternative", "label": "Alternative", "primitive_type": "text", "required": False, "help_text": "The alternative, plan, or competitor."},
            {"key": "differentiator", "label": "Differentiator", "primitive_type": "paragraph", "required": False, "help_text": "How this option is different."},
            {"key": "proof_note", "label": "Proof note", "primitive_type": "proof", "required": False, "help_text": "Optional evidence for the comparison."},
        ],
    },
    {
        "concept": "form",
        "catalog_key": "form",
        "ontology_key": "form_spec",
        "label": "Form",
        "family": "product",
        "description": "Form specification or lead capture requirement.",
        "composite": True,
        "group_key": None,
        "channel_affinity": ["landing_page"],
        "page_usable": True,
        "proof_sensitive": False,
        "slot_schema": [
            {"key": "form_title", "label": "Form heading", "type": "text", "primitive_type": "headline", "required": False, "placeholder": "e.g., Request a quote"},
            {"key": "form_subtext", "label": "Supporting text", "type": "textarea", "primitive_type": "paragraph", "required": False, "placeholder": "What happens after someone submits?"},
            {"key": "form_fields", "label": "Fields to collect", "type": "text", "primitive_type": "text", "required": False, "placeholder": "e.g., Name, Email, Phone, Message"},
            {"key": "submit_text", "label": "Submit button text", "type": "text", "primitive_type": "cta_label", "required": False, "placeholder": "e.g., Send request", "max_length": 80},
        ],
    },
    # --- brand / company ------------------------------------------------------
    {
        "concept": "about",
        "catalog_key": "about",
        "ontology_key": None,
        "label": "About",
        "family": "brand",
        "description": "Company, founder, team, or origin story copy.",
        "composite": False,
        "group_key": None,
        "channel_affinity": ["general", "landing_page"],
        "page_usable": True,
        "proof_sensitive": False,
        "slot_schema": [
            {"key": "story", "label": "Story", "type": "textarea", "primitive_type": "paragraph", "required": False, "placeholder": "How you started, what you do, and what makes you different"},
            {"key": "since_year", "label": "Year established", "type": "text", "primitive_type": "text", "required": False, "placeholder": "e.g., 2018"},
            {"key": "team_note", "label": "Team note", "type": "text", "primitive_type": "text", "required": False, "placeholder": "e.g., Family-owned, 12-person team"},
        ],
    },
    {
        "concept": "boilerplate",
        "catalog_key": "boilerplate",
        "ontology_key": None,
        "label": "Boilerplate",
        "family": "brand",
        "description": "Reusable official company description.",
        "composite": False,
        "group_key": None,
        "channel_affinity": ["general", "landing_page", "email"],
        "page_usable": True,
        "proof_sensitive": False,
        "slot_schema": [
            {"key": "description", "label": "Company description", "type": "textarea", "primitive_type": "paragraph", "required": False, "placeholder": "Official reusable company description"},
        ],
    },
    # --- channel assets -------------------------------------------------------
    {
        "concept": "seo_meta",
        "catalog_key": "seo_meta",
        "ontology_key": None,
        "label": "SEO meta",
        "family": "channel_assets",
        "description": "SEO title, description, or search snippet copy.",
        "composite": False,
        "group_key": None,
        "channel_affinity": ["landing_page", "general"],
        "page_usable": False,
        "proof_sensitive": False,
        "slot_schema": [
            {"key": "seo_title", "label": "SEO title", "type": "text", "primitive_type": "headline", "required": False, "placeholder": "Search result title", "max_length": 70},
            {"key": "meta_description", "label": "Meta description", "type": "textarea", "primitive_type": "paragraph", "required": False, "placeholder": "150-160 character search snippet", "max_length": 180},
        ],
    },
    {
        "concept": "ad_copy",
        "catalog_key": "ad_copy",
        "ontology_key": None,
        "label": "Ad copy",
        "family": "channel_assets",
        "description": "Paid ad headline or body variant.",
        "composite": False,
        "group_key": None,
        "channel_affinity": ["ad"],
        "page_usable": False,
        "proof_sensitive": False,
        "slot_schema": [
            {"key": "headline", "label": "Ad headline", "type": "text", "primitive_type": "headline", "required": False, "placeholder": "Short paid ad headline", "max_length": 90},
            {"key": "body", "label": "Ad body", "type": "textarea", "primitive_type": "paragraph", "required": False, "placeholder": "Primary ad copy"},
            {"key": "cta_label", "label": "CTA label", "type": "text", "primitive_type": "cta_label", "required": False, "placeholder": "e.g., Learn more", "max_length": 80},
        ],
    },
    {
        "concept": "email_subject",
        "catalog_key": "email_subject",
        "ontology_key": None,
        "label": "Email subject",
        "family": "channel_assets",
        "description": "Email subject line or preview text.",
        "composite": False,
        "group_key": None,
        "channel_affinity": ["email"],
        "page_usable": False,
        "proof_sensitive": False,
        "slot_schema": [
            {"key": "subject", "label": "Subject line", "type": "text", "primitive_type": "headline", "required": False, "placeholder": "Email subject line", "max_length": 120},
            {"key": "preview_text", "label": "Preview text", "type": "text", "primitive_type": "paragraph", "required": False, "placeholder": "Inbox preview text", "max_length": 160},
        ],
    },
    {
        "concept": "social_post",
        "catalog_key": "social_post",
        "ontology_key": None,
        "label": "Social post",
        "family": "channel_assets",
        "description": "Social media post copy.",
        "composite": False,
        "group_key": None,
        "channel_affinity": ["social"],
        "page_usable": False,
        "proof_sensitive": False,
        "slot_schema": [
            {"key": "post_copy", "label": "Post copy", "type": "textarea", "primitive_type": "paragraph", "required": False, "placeholder": "Social media caption or post text"},
            {"key": "hashtags", "label": "Hashtags", "type": "text", "primitive_type": "text", "required": False, "placeholder": "e.g., #launch #localbusiness"},
            {"key": "cta_label", "label": "CTA", "type": "text", "primitive_type": "cta_label", "required": False, "placeholder": "e.g., Shop now"},
        ],
    },
    # --- ontology-only primitives (no Library category) -----------------------
    {"concept": "eyebrow", "catalog_key": None, "ontology_key": "eyebrow", "label": "Eyebrow", "family": "core_message", "composite": False, "group_key": None},
    {"concept": "paragraph", "catalog_key": None, "ontology_key": "paragraph", "label": "Paragraph", "family": "core_message", "composite": False, "group_key": None},
    {"concept": "cta_label", "catalog_key": None, "ontology_key": "cta_label", "label": "CTA label", "family": "core_message", "composite": False, "group_key": None},
    {"concept": "link", "catalog_key": None, "ontology_key": "link", "label": "Link", "family": "core_message", "composite": False, "group_key": None},
    {"concept": "stat", "catalog_key": None, "ontology_key": "stat", "label": "Stat", "family": "proof", "composite": False, "group_key": "statistics"},
    {"concept": "rating", "catalog_key": None, "ontology_key": "rating", "label": "Rating", "family": "proof", "composite": False, "group_key": None},
    {"concept": "quote", "catalog_key": None, "ontology_key": "quote", "label": "Quote", "family": "proof", "composite": False, "group_key": None},
    {"concept": "image_ref", "catalog_key": None, "ontology_key": "image_ref", "label": "Image reference", "family": "channel_assets", "composite": False, "group_key": None},
    {"concept": "icon_ref", "catalog_key": None, "ontology_key": "icon_ref", "label": "Icon reference", "family": "channel_assets", "composite": False, "group_key": None},
    {"concept": "badge_label", "catalog_key": None, "ontology_key": "badge_label", "label": "Badge label", "family": "core_message", "composite": False, "group_key": None},
    {"concept": "question", "catalog_key": None, "ontology_key": "question", "label": "Question", "family": "objections", "composite": False, "group_key": None},
    {"concept": "answer", "catalog_key": None, "ontology_key": "answer", "label": "Answer", "family": "objections", "composite": False, "group_key": None},
    # --- ontology-only campaign atoms + composites ----------------------------
    {"concept": "pain_point", "catalog_key": None, "ontology_key": "pain_point", "label": "Pain point", "family": "core_message", "composite": False, "group_key": "pain_points"},
    {"concept": "promise", "catalog_key": None, "ontology_key": "promise", "label": "Promise", "family": "core_message", "composite": False, "group_key": "promises"},
    {"concept": "narrative", "catalog_key": None, "ontology_key": "narrative", "label": "Narrative", "family": "brand", "composite": True, "group_key": None},
]


# Catalog content types the Campaign Studio form authors (messages + offer).
# This is the subset of the Library catalog that campaign and content share as a
# single store (strategy imp.md, decision 1). Offer-field materialization
# (campaign/offer_sync.py) uses a subset of these.
CAMPAIGN_CONTENT_TYPES = (
    "headline", "subheadline", "benefit", "proof", "testimonial",
    "offer", "faq", "objection", "cta", "about", "value_proposition",
)


def campaign_content_types():
    """Catalog keys the campaign form materializes into the Content Library."""
    return frozenset(CAMPAIGN_CONTENT_TYPES)


# --- derived lookups ----------------------------------------------------------

_BY_CONCEPT = {e["concept"]: e for e in CONTENT_REGISTRY}
_BY_CATALOG_KEY = {e["catalog_key"]: e for e in CONTENT_REGISTRY if e.get("catalog_key")}
_BY_ONTOLOGY_KEY = {e["ontology_key"]: e for e in CONTENT_REGISTRY if e.get("ontology_key")}


def entries():
    """All registry entries (live references — do not mutate)."""
    return CONTENT_REGISTRY


def catalog_entries():
    """Entries that are Content Library catalog types (have a catalog_key)."""
    return [e for e in CONTENT_REGISTRY if e.get("catalog_key")]


def ontology_keys():
    """The ontology CONTENT_TYPE set (vocabulary.CONTENT_TYPE)."""
    return {e["ontology_key"] for e in CONTENT_REGISTRY if e.get("ontology_key")}


def composite_ontology_keys():
    """The ontology COMPOSITE_TYPES set."""
    return {
        e["ontology_key"] for e in CONTENT_REGISTRY
        if e.get("ontology_key") and e.get("composite")
    }


def group_key_to_ontology_type():
    """The GROUP_KEY_TO_TYPE shorthand map (group plural -> ontology type)."""
    return {
        e["group_key"]: e["ontology_key"]
        for e in CONTENT_REGISTRY
        if e.get("group_key") and e.get("ontology_key")
    }


def catalog_keys():
    """The Content Library catalog key set (== ContentItem categories)."""
    return set(_BY_CATALOG_KEY.keys())


def to_ontology_type(key):
    """Map any content key (catalog or ontology) to its ontology type name.

    Returns the ontology key for the concept, or the input unchanged when it is
    already an ontology key or has no ontology mapping. Used to bridge an ORM
    ``ContentItem.category`` (catalog key) to the recipe engine's type names.
    """
    if key in _BY_ONTOLOGY_KEY:
        return key
    entry = _BY_CATALOG_KEY.get(key)
    if entry and entry.get("ontology_key"):
        return entry["ontology_key"]
    return key


def to_catalog_key(key):
    """Map any content key (ontology or catalog) to its catalog key.

    Returns the catalog key for the concept, or None when the concept is
    ontology-only (e.g. ``pain_point``, ``paragraph``).
    """
    if key in _BY_CATALOG_KEY:
        return key
    entry = _BY_ONTOLOGY_KEY.get(key)
    if entry:
        return entry.get("catalog_key")
    return None


# --- ORM ContentItem -> normalized item bridge --------------------------------

def normalize_content_item(item, idx=0):
    """Turn an ORM ``ContentItem`` into the normalized dict the recipe engine,
    ``content.group_by_type``, and ``content_refs`` consume.

    Mirrors the shape produced by ``campaign/content.py::_make_item`` so a stored
    library item resolves through ``content_refs.resolve_ref`` exactly like
    transient campaign content. The item's catalog ``category`` is mapped to its
    ontology type name so refs such as ``content.benefits`` resolve.

    Args:
        item: ORM ContentItem (duck-typed: ``.category``, ``.content``,
            ``.get_slots()``, optional ``.id``/``.source``).
        idx: positional index within its type group (for the synthetic id).

    Returns:
        dict: {id, type, content, truth_level, source, slots?, tags?}
    """
    category = getattr(item, "category", "") or ""
    ctype = to_ontology_type(category)

    slots = {}
    if hasattr(item, "get_slots"):
        slots = item.get_slots() or {}

    normalized = {
        "id": getattr(item, "id", None) or f"content_{ctype}_{idx}",
        "type": ctype,
        "content": getattr(item, "content", "") or "",
        "truth_level": "approved",
        "source": getattr(item, "source", None) or "human_input",
    }
    if slots:
        normalized["slots"] = {k: v for k, v in slots.items() if v is not None}

    tags = item.get_tags() if hasattr(item, "get_tags") else None
    if tags:
        normalized["tags"] = tags
    return normalized


def normalize_content_items(items):
    """Normalize a list of ORM ``ContentItem`` rows into typed-item dicts.

    Indexes are assigned per ontology type so synthetic ids stay unique and
    ``content.<group>[idx]`` refs line up with insertion order.
    """
    out = []
    counts = {}
    for item in items or []:
        ctype = to_ontology_type(getattr(item, "category", "") or "")
        idx = counts.get(ctype, 0)
        counts[ctype] = idx + 1
        out.append(normalize_content_item(item, idx))
    return out
