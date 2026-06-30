"""
Campaign CRUD API — org-scoped via guards.

Endpoints:
  POST   /api/campaigns              Create a draft campaign
  GET    /api/campaigns              List campaigns for org
  GET    /api/campaigns/<id>         Full campaign with brief, offer, messages
  PATCH  /api/campaigns/<id>         Update campaign fields
  DELETE /api/campaigns/<id>         Delete campaign + cascade

  PATCH  /api/campaigns/<id>/brief   Update campaign brief
  PATCH  /api/campaigns/<id>/offer   Update campaign offer

  GET    /api/campaigns/<id>/messages          List messages
  POST   /api/campaigns/<id>/messages          Add message(s)
  PATCH  /api/campaigns/<id>/messages/<msg_id> Update a message
  DELETE /api/campaigns/<id>/messages/<msg_id> Delete a message

  POST   /api/campaigns/<id>/compile           Compile campaign to builder input
"""
import json
from datetime import datetime
from flask import Blueprint, g, jsonify, request
from extensions import db
from models import (
    Brand, Campaign, CampaignBrief, CampaignOffer, CampaignMessage,
    CampaignProduct, Product, ContentItem, MediaAsset,
)
from guards import require_role

campaign_bp = Blueprint('campaign', __name__)


# =============================================================================
# Pre-Auth Stub — same pattern as site_bp
# =============================================================================

@campaign_bp.before_request
def set_default_org():
    """Temporary: hardcode default org until auth is implemented."""
    from models import Organization
    default_org = Organization.query.filter_by(slug='default').first()
    g.current_org_id = default_org.id if default_org else None
    g.current_role = 'owner'


# =============================================================================
# Helpers
# =============================================================================

def _get_campaign_or_404(campaign_id):
    campaign = Campaign.query.filter_by(id=campaign_id, org_id=g.current_org_id).first()
    if not campaign:
        from flask import abort
        abort(404)
    return campaign


def _serialize_brief(brief):
    if not brief:
        return None
    return {
        'product_or_service': brief.product_or_service,
        'description': brief.description,
        'target_audience': brief.target_audience,
        'problem_or_desire': brief.problem_or_desire,
        'awareness_level': brief.awareness_level,
        'buying_stage': brief.buying_stage,
        'location_or_segment': brief.location_or_segment,
    }


def _serialize_offer(offer):
    if not offer:
        return None
    return {
        'offer': offer.offer,
        'primary_cta': offer.primary_cta,
        'secondary_cta': offer.secondary_cta,
        'benefits': offer.get_benefits(),
        'proof_points': offer.get_proof_points(),
        'objections': offer.get_objections(),
        'faqs': offer.get_faqs(),
    }


def _serialize_message(msg):
    return {
        'id': msg.id,
        'category': msg.category,
        'content': msg.content,
        'is_kept': msg.is_kept,
        'used_in_section': msg.used_in_section,
        'sort_order': msg.sort_order,
        'created_at': msg.created_at.isoformat() if msg.created_at else None,
    }


def _serialize_campaign_summary(c):
    return {
        'id': c.id,
        'name': c.name,
        'status': c.status,
        'goal': c.goal,
        'brand_id': c.brand_id,
        'brand': c.brand.to_dict() if c.brand else None,
        'product_ids': [cp.product_id for cp in (c.campaign_products or [])],
        'site_id': c.site_id,
        'created_at': c.created_at.isoformat() if c.created_at else None,
        'updated_at': c.updated_at.isoformat() if c.updated_at else None,
    }


def _serialize_campaign_full(c):
    result = _serialize_campaign_summary(c)
    result['brief'] = _serialize_brief(c.brief)
    result['offer'] = _serialize_offer(c.offer)
    result['messages'] = [_serialize_message(m) for m in c.messages]
    result['products'] = [
        cp.product.to_dict()
        for cp in (c.campaign_products or [])
        if cp.product
    ]
    return result


def _validate_brand_id(brand_id):
    if not brand_id:
        return None, None
    brand = Brand.query.filter_by(id=brand_id, org_id=g.current_org_id).first()
    if not brand:
        return None, 'Selected brand was not found.'
    return brand.id, None


def _validate_product_ids(product_ids):
    if product_ids in (None, ''):
        return None, None
    if not isinstance(product_ids, list):
        return None, 'product_ids must be an array.'
    ids = [str(item) for item in product_ids if item]
    if not ids:
        return [], None
    products = Product.query.filter(
        Product.org_id == g.current_org_id,
        Product.id.in_(ids),
    ).all()
    if len(products) != len(set(ids)):
        return None, 'One or more selected products were not found.'
    return list(dict.fromkeys(ids)), None


def _sync_campaign_products(campaign, product_ids):
    if product_ids is None:
        return
    existing = {cp.product_id: cp for cp in campaign.campaign_products}
    desired = set(product_ids)

    for product_id, link in list(existing.items()):
        if product_id not in desired:
            db.session.delete(link)

    for index, product_id in enumerate(product_ids):
        if product_id not in existing:
            db.session.add(CampaignProduct(
                campaign_id=campaign.id,
                product_id=product_id,
                role='promoted',
                sort_order=index,
            ))
        else:
            existing[product_id].sort_order = index


# =============================================================================
# Campaign CRUD
# =============================================================================

@campaign_bp.route('/api/campaigns', methods=['POST'])
@require_role('editor')
def create_campaign():
    """Create a new draft campaign.

    Request JSON: { name?, goal?, brief?: {...} }
    """
    data = request.get_json(silent=True) or {}

    # A real, meaningful name is required up front so reporting/analytics can
    # identify the campaign. No silent "Untitled Campaign" fallback.
    name = (data.get('name') or '').strip()
    if not name:
        return jsonify({'error': 'Campaign name is required.'}), 400
    goal = (data.get('goal') or '').strip() or None
    brand_id, brand_error = _validate_brand_id(data.get('brand_id'))
    if brand_error:
        return jsonify({'error': brand_error}), 400
    product_ids, product_error = _validate_product_ids(data.get('product_ids'))
    if product_error:
        return jsonify({'error': product_error}), 400

    if goal and goal not in Campaign.VALID_GOALS:
        return jsonify({'error': f'Invalid goal. Must be one of: {", ".join(sorted(Campaign.VALID_GOALS))}'}), 400

    campaign = Campaign(
        org_id=g.current_org_id,
        brand_id=brand_id,
        name=name[:200],
        goal=goal,
    )
    db.session.add(campaign)
    db.session.flush()

    brief = CampaignBrief(campaign_id=campaign.id)
    brief_data = data.get('brief') or {}
    if brief_data:
        _apply_brief_fields(brief, brief_data)
    db.session.add(brief)

    offer = CampaignOffer(campaign_id=campaign.id)
    db.session.add(offer)
    _sync_campaign_products(campaign, product_ids)

    db.session.commit()

    return jsonify(_serialize_campaign_full(campaign)), 201


@campaign_bp.route('/api/campaigns', methods=['GET'])
def list_campaigns():
    """List all campaigns for the current org."""
    status_filter = request.args.get('status')
    query = Campaign.query.filter_by(org_id=g.current_org_id)
    if status_filter and status_filter in Campaign.VALID_STATUSES:
        query = query.filter_by(status=status_filter)
    campaigns = query.order_by(Campaign.updated_at.desc()).all()
    return jsonify([_serialize_campaign_summary(c) for c in campaigns])


@campaign_bp.route('/api/campaigns/<campaign_id>', methods=['GET'])
def get_campaign(campaign_id):
    """Get full campaign with brief, offer, and messages."""
    campaign = _get_campaign_or_404(campaign_id)
    return jsonify(_serialize_campaign_full(campaign))


@campaign_bp.route('/api/campaigns/<campaign_id>', methods=['PATCH'])
@require_role('editor')
def update_campaign(campaign_id):
    """Update campaign top-level fields (name, status, goal, brand/products).

    Request JSON: { name?, status?, goal?, brand_id?, product_ids? }
    """
    campaign = _get_campaign_or_404(campaign_id)
    data = request.get_json(silent=True)
    if not data:
        return jsonify({'error': 'JSON body required.'}), 400

    if 'name' in data:
        name = (data['name'] or '').strip()
        if not name:
            return jsonify({'error': 'Campaign name cannot be empty.'}), 400
        campaign.name = name[:200]

    if 'status' in data:
        status = (data['status'] or '').strip()
        if status not in Campaign.VALID_STATUSES:
            return jsonify({'error': f'Invalid status. Must be one of: {", ".join(sorted(Campaign.VALID_STATUSES))}'}), 400
        campaign.status = status

    if 'goal' in data:
        goal = (data['goal'] or '').strip() or None
        if goal and goal not in Campaign.VALID_GOALS:
            return jsonify({'error': f'Invalid goal. Must be one of: {", ".join(sorted(Campaign.VALID_GOALS))}'}), 400
        campaign.goal = goal

    if 'brand_id' in data:
        brand_id, error = _validate_brand_id(data.get('brand_id'))
        if error:
            return jsonify({'error': error}), 400
        campaign.brand_id = brand_id

    if 'product_ids' in data:
        product_ids, error = _validate_product_ids(data.get('product_ids'))
        if error:
            return jsonify({'error': error}), 400
        _sync_campaign_products(campaign, product_ids)

    campaign.updated_at = datetime.utcnow()
    db.session.commit()
    return jsonify({'ok': True})


@campaign_bp.route('/api/campaigns/<campaign_id>', methods=['DELETE'])
@require_role('editor')
def delete_campaign(campaign_id):
    """Delete campaign and all related data."""
    campaign = _get_campaign_or_404(campaign_id)
    db.session.delete(campaign)
    db.session.commit()
    return jsonify({'ok': True})


# =============================================================================
# Brief
# =============================================================================

def _apply_brief_fields(brief, data):
    """Apply validated fields to a CampaignBrief instance."""
    text_fields = ['product_or_service', 'description', 'target_audience',
                   'problem_or_desire', 'location_or_segment']
    for field in text_fields:
        if field in data:
            setattr(brief, field, (data[field] or '').strip() or None)

    if 'awareness_level' in data:
        val = (data['awareness_level'] or '').strip() or None
        if val and val not in CampaignBrief.VALID_AWARENESS_LEVELS:
            return f'Invalid awareness_level. Must be one of: {", ".join(sorted(CampaignBrief.VALID_AWARENESS_LEVELS))}'
        brief.awareness_level = val

    if 'buying_stage' in data:
        val = (data['buying_stage'] or '').strip() or None
        if val and val not in CampaignBrief.VALID_BUYING_STAGES:
            return f'Invalid buying_stage. Must be one of: {", ".join(sorted(CampaignBrief.VALID_BUYING_STAGES))}'
        brief.buying_stage = val

    return None


@campaign_bp.route('/api/campaigns/<campaign_id>/brief', methods=['PATCH'])
@require_role('editor')
def update_brief(campaign_id):
    """Update campaign brief fields.

    Request JSON: { product_or_service?, description?, target_audience?,
                    problem_or_desire?, awareness_level?, buying_stage?,
                    location_or_segment? }
    """
    campaign = _get_campaign_or_404(campaign_id)
    data = request.get_json(silent=True)
    if not data:
        return jsonify({'error': 'JSON body required.'}), 400

    if not campaign.brief:
        campaign.brief = CampaignBrief(campaign_id=campaign.id)
        db.session.add(campaign.brief)

    error = _apply_brief_fields(campaign.brief, data)
    if error:
        return jsonify({'error': error}), 400

    campaign.updated_at = datetime.utcnow()
    db.session.commit()
    return jsonify({'ok': True, 'brief': _serialize_brief(campaign.brief)})


# =============================================================================
# Offer
# =============================================================================

@campaign_bp.route('/api/campaigns/<campaign_id>/offer', methods=['PATCH'])
@require_role('editor')
def update_offer(campaign_id):
    """Update campaign offer fields.

    Request JSON: { offer?, primary_cta?, secondary_cta?,
                    benefits?, proof_points?, objections?, faqs? }
    """
    campaign = _get_campaign_or_404(campaign_id)
    data = request.get_json(silent=True)
    if not data:
        return jsonify({'error': 'JSON body required.'}), 400

    if not campaign.offer:
        campaign.offer = CampaignOffer(campaign_id=campaign.id)
        db.session.add(campaign.offer)

    offer = campaign.offer

    if 'offer' in data:
        offer.offer = (data['offer'] or '').strip() or None
    if 'primary_cta' in data:
        offer.primary_cta = (data['primary_cta'] or '').strip()[:200] or None
    if 'secondary_cta' in data:
        offer.secondary_cta = (data['secondary_cta'] or '').strip()[:200] or None

    if 'benefits' in data:
        if not isinstance(data['benefits'], list):
            return jsonify({'error': 'benefits must be an array.'}), 400
        offer.set_benefits(data['benefits'])

    if 'proof_points' in data:
        if not isinstance(data['proof_points'], list):
            return jsonify({'error': 'proof_points must be an array.'}), 400
        offer.set_proof_points(data['proof_points'])

    if 'objections' in data:
        if not isinstance(data['objections'], list):
            return jsonify({'error': 'objections must be an array.'}), 400
        offer.set_objections(data['objections'])

    if 'faqs' in data:
        if not isinstance(data['faqs'], list):
            return jsonify({'error': 'faqs must be an array of {question, answer} objects.'}), 400
        for item in data['faqs']:
            if not isinstance(item, dict) or 'question' not in item or 'answer' not in item:
                return jsonify({'error': 'Each FAQ must have "question" and "answer" fields.'}), 400
        offer.set_faqs(data['faqs'])

    # Dual-write: materialize the offer fields as typed ContentItems so campaign
    # and Library share one store (strategy imp.md decision 1). The CampaignOffer
    # columns remain the read source during the transition; offer_sync is
    # idempotent so debounced saves never duplicate. Library auto-populates here.
    from campaign.offer_sync import sync_offer_to_content_items
    sync_offer_to_content_items(campaign)

    campaign.updated_at = datetime.utcnow()
    db.session.commit()
    return jsonify({'ok': True, 'offer': _serialize_offer(campaign.offer)})


# =============================================================================
# Messages
# =============================================================================

@campaign_bp.route('/api/campaigns/<campaign_id>/messages', methods=['GET'])
def list_messages(campaign_id):
    """List all messages for a campaign, optionally filtered by category."""
    campaign = _get_campaign_or_404(campaign_id)
    category_filter = request.args.get('category')
    query = CampaignMessage.query.filter_by(campaign_id=campaign.id)
    if category_filter and category_filter in CampaignMessage.VALID_CATEGORIES:
        query = query.filter_by(category=category_filter)
    messages = query.order_by(CampaignMessage.sort_order).all()
    return jsonify([_serialize_message(m) for m in messages])


@campaign_bp.route('/api/campaigns/<campaign_id>/messages', methods=['POST'])
@require_role('editor')
def add_messages(campaign_id):
    """Add one or more messages to a campaign.

    Request JSON: { messages: [{ category, content, is_kept?, used_in_section? }] }
    Or single: { category, content, is_kept?, used_in_section? }
    """
    campaign = _get_campaign_or_404(campaign_id)
    data = request.get_json(silent=True)
    if not data:
        return jsonify({'error': 'JSON body required.'}), 400

    items = data.get('messages') if 'messages' in data else [data]
    if not isinstance(items, list) or not items:
        return jsonify({'error': 'Provide messages array or single message object.'}), 400

    max_order = db.session.query(db.func.max(CampaignMessage.sort_order)) \
        .filter_by(campaign_id=campaign.id).scalar() or 0

    created = []
    for i, item in enumerate(items):
        category = (item.get('category') or '').strip()
        content = (item.get('content') or '').strip()

        if not category or category not in CampaignMessage.VALID_CATEGORIES:
            return jsonify({
                'error': f'Invalid category at index {i}. Must be one of: {", ".join(sorted(CampaignMessage.VALID_CATEGORIES))}'
            }), 400
        if not content:
            return jsonify({'error': f'Message content cannot be empty (index {i}).'}), 400

        msg = CampaignMessage(
            campaign_id=campaign.id,
            category=category,
            content=content,
            is_kept=bool(item.get('is_kept', False)),
            used_in_section=(item.get('used_in_section') or '').strip() or None,
            sort_order=max_order + i + 1,
        )
        db.session.add(msg)
        created.append(msg)

    campaign.updated_at = datetime.utcnow()
    db.session.commit()
    return jsonify([_serialize_message(m) for m in created]), 201


@campaign_bp.route('/api/campaigns/<campaign_id>/messages/<message_id>', methods=['PATCH'])
@require_role('editor')
def update_message(campaign_id, message_id):
    """Update a single message.

    Request JSON: { content?, is_kept?, used_in_section?, sort_order?, category? }
    """
    campaign = _get_campaign_or_404(campaign_id)
    msg = CampaignMessage.query.filter_by(id=message_id, campaign_id=campaign.id).first()
    if not msg:
        from flask import abort
        abort(404)

    data = request.get_json(silent=True)
    if not data:
        return jsonify({'error': 'JSON body required.'}), 400

    if 'content' in data:
        content = (data['content'] or '').strip()
        if not content:
            return jsonify({'error': 'Message content cannot be empty.'}), 400
        msg.content = content

    if 'category' in data:
        category = (data['category'] or '').strip()
        if category not in CampaignMessage.VALID_CATEGORIES:
            return jsonify({'error': f'Invalid category. Must be one of: {", ".join(sorted(CampaignMessage.VALID_CATEGORIES))}'}), 400
        msg.category = category

    if 'is_kept' in data:
        msg.is_kept = bool(data['is_kept'])

    if 'used_in_section' in data:
        msg.used_in_section = (data['used_in_section'] or '').strip() or None

    if 'sort_order' in data:
        msg.sort_order = int(data['sort_order'])

    campaign.updated_at = datetime.utcnow()
    db.session.commit()
    return jsonify(_serialize_message(msg))


@campaign_bp.route('/api/campaigns/<campaign_id>/messages/<message_id>', methods=['DELETE'])
@require_role('editor')
def delete_message(campaign_id, message_id):
    """Delete a single message."""
    campaign = _get_campaign_or_404(campaign_id)
    msg = CampaignMessage.query.filter_by(id=message_id, campaign_id=campaign.id).first()
    if not msg:
        from flask import abort
        abort(404)

    db.session.delete(msg)
    campaign.updated_at = datetime.utcnow()
    db.session.commit()
    return jsonify({'ok': True})


# =============================================================================
# Compile (Campaign → Builder Input)
# =============================================================================

@campaign_bp.route('/api/campaigns/<campaign_id>/compile', methods=['POST'])
@require_role('editor')
def compile_campaign(campaign_id):
    """Compile campaign data into builder-agent-compatible section outline.

    Returns the structured business_content dict per section that the builder
    agent uses to generate YAML.
    """
    campaign = _get_campaign_or_404(campaign_id)

    from campaign.compiler import compile_campaign_to_sections
    try:
        result = compile_campaign_to_sections(campaign)
    except ValueError as e:
        return jsonify({'error': str(e)}), 400

    return jsonify(result)


# =============================================================================
# Generate Landing Page
# =============================================================================

@campaign_bp.route('/api/campaigns/<campaign_id>/generate-page', methods=['POST'])
@require_role('editor')
def generate_page(campaign_id):
    """Generate a landing page from campaign data via the RAG pipeline.

    Creates a Site + SitePage if the campaign doesn't have one yet, or
    regenerates the existing page.

    Response: { ok, site_id, page_id, yaml, html }
    """
    import os
    import traceback
    from flask import current_app
    from models import Site, SitePage
    from campaign.compiler import compile_to_business_context

    campaign = _get_campaign_or_404(campaign_id)

    brand_context_source = campaign.brand
    if not brand_context_source:
        brand_context_source = Brand.query.filter_by(org_id=g.current_org_id, is_default=True).first()
    selected_products = [
        cp.product for cp in (campaign.campaign_products or [])
        if cp.product
    ]
    selected_product_ids = [p.id for p in selected_products]
    content_query = ContentItem.query.filter(
        ContentItem.org_id == g.current_org_id,
        ContentItem.status.in_(['approved', 'active']),
        db.or_(ContentItem.expires_at.is_(None), ContentItem.expires_at > datetime.utcnow()),
    )
    if campaign.brand_id:
        content_query = content_query.filter(db.or_(
            ContentItem.brand_id.is_(None),
            ContentItem.brand_id == campaign.brand_id,
        ))
    else:
        content_query = content_query.filter(ContentItem.brand_id.is_(None))
    if selected_product_ids:
        content_query = content_query.filter(db.or_(
            ContentItem.product_id.is_(None),
            ContentItem.product_id.in_(selected_product_ids),
        ))
    else:
        content_query = content_query.filter(ContentItem.product_id.is_(None))
    reusable_content = content_query.order_by(
        ContentItem.is_pinned.desc(),
        ContentItem.updated_at.desc(),
    ).limit(30).all()

    try:
        business_context = compile_to_business_context(
            campaign,
            brand_kit=brand_context_source,
            products=selected_products,
            content_items=reusable_content,
        )
    except ValueError as e:
        return jsonify({'error': str(e)}), 400

    # Pull images from the org media library.
    db_images = MediaAsset.query.filter_by(org_id=g.current_org_id) \
        .order_by(MediaAsset.created_at.desc()) \
        .limit(40) \
        .all()
    selected_images = [
        {
            'id': img.id,
            'url': img.url or (f'/uploads/{img.storage_path}' if img.storage_path else ''),
            'altText': img.alt_text or img.original_name or img.filename,
            'orientation': img.orientation or 'unknown',
            'photographer': img.photographer or '',
            'source': img.source or '',
            'sourceUrl': img.source_url or '',
            'license': img.license_label or '',
            'tags': img.get_tags(),
            'width': img.width,
            'height': img.height,
        }
        for img in db_images
        if img.url or img.storage_path
    ]

    # Call the RAG pipeline
    try:
        from llm_service import get_llm_service
        llm_service = get_llm_service()

        result = llm_service.chat(
            f"[campaign] {campaign.name}",
            '',
            None,
            selected_images=selected_images,
            progress_fn=lambda msg: None,
            business_context=business_context,
        )
    except Exception as e:
        current_app.logger.error(f"Campaign page generation error: {e}\n{traceback.format_exc()}")
        return jsonify({'error': f'Page generation failed: {str(e)}'}), 500

    generated_yaml = result.get('yaml')
    if not generated_yaml:
        return jsonify({'error': 'Generation produced no YAML output. Try adding more details to your campaign.'}), 422

    # Create or update the linked site/page
    site, page = _ensure_campaign_site(campaign, generated_yaml)

    # Render to HTML for preview
    html = _render_page_html(site, page)

    campaign.updated_at = datetime.utcnow()
    db.session.commit()

    return jsonify({
        'ok': True,
        'site_id': site.id,
        'page_id': page.id,
        'yaml': generated_yaml,
        'html': html,
    })


@campaign_bp.route('/api/campaigns/<campaign_id>/preview', methods=['GET'])
def preview_page(campaign_id):
    """Render the campaign's landing page to HTML for iframe preview.

    Response: raw HTML (text/html)
    """
    from flask import current_app
    from models import Site, SitePage

    campaign = _get_campaign_or_404(campaign_id)

    if not campaign.site_id:
        return jsonify({'error': 'No landing page generated yet.'}), 404

    site = Site.query.get(campaign.site_id)
    if not site:
        return jsonify({'error': 'Linked site not found.'}), 404

    page = SitePage.query.filter_by(site_id=site.id, is_homepage=True).first()
    if not page:
        return jsonify({'error': 'No homepage found.'}), 404

    html = _render_page_html(site, page)
    if html is None:
        return jsonify({'error': 'Failed to render page.'}), 500

    return current_app.response_class(html, mimetype='text/html')


@campaign_bp.route('/api/campaigns/<campaign_id>/regenerate-section', methods=['POST'])
@require_role('editor')
def regenerate_section(campaign_id):
    """Regenerate a specific section within the campaign landing page.

    Request JSON: { section_index: int, instruction?: str }
    Response: { ok, yaml, html }
    """
    import yaml as yaml_lib
    from flask import current_app
    from models import Site, SitePage

    campaign = _get_campaign_or_404(campaign_id)
    data = request.get_json(silent=True) or {}
    section_index = data.get('section_index')

    if section_index is None:
        return jsonify({'error': 'section_index is required.'}), 400

    if not campaign.site_id:
        return jsonify({'error': 'No landing page generated yet.'}), 404

    site = Site.query.get(campaign.site_id)
    page = SitePage.query.filter_by(site_id=site.id, is_homepage=True).first()
    if not page or not page.yaml_content:
        return jsonify({'error': 'No page content found.'}), 404

    try:
        structure = yaml_lib.safe_load(page.yaml_content)
        if not structure or not isinstance(structure, list):
            return jsonify({'error': 'Invalid page structure.'}), 400

        site_node = structure[0]
        page_node = (site_node.get('components') or [{}])[0]
        components = page_node.get('components') or []

        if section_index < 0 or section_index >= len(components):
            return jsonify({'error': f'Section index {section_index} out of range (0-{len(components)-1}).'}), 400

        instruction = (data.get('instruction') or '').strip()
        section_component = components[section_index]
        section_name = section_component.get('name', 'section')

        # Use the chat endpoint to modify this specific section
        from llm_service import get_llm_service
        section_yaml = yaml_lib.dump([section_component], default_flow_style=False, allow_unicode=True, sort_keys=False)

        prompt = instruction or f'Regenerate this {section_name} section with fresh copy. Keep the same component structure but rewrite all text content.'

        llm_service = get_llm_service()
        result = llm_service.chat(
            prompt,
            section_yaml,
            None,
            selected_images=[],
            progress_fn=lambda msg: None,
        )

        new_yaml = result.get('yaml')
        if new_yaml:
            new_components = yaml_lib.safe_load(new_yaml)
            if isinstance(new_components, list) and new_components:
                components[section_index] = new_components[0]
            elif isinstance(new_components, dict):
                components[section_index] = new_components

        page_node['components'] = components
        page.yaml_content = yaml_lib.dump(structure, default_flow_style=False, allow_unicode=True, sort_keys=False)
        page.updated_at = datetime.utcnow()
        db.session.commit()

        html = _render_page_html(site, page)

        return jsonify({
            'ok': True,
            'yaml': page.yaml_content,
            'html': html,
        })

    except Exception as e:
        current_app.logger.error(f"Regenerate section error: {e}")
        return jsonify({'error': f'Regeneration failed: {str(e)}'}), 500


# =============================================================================
# Helpers — Site/Page Management
# =============================================================================

def _ensure_campaign_site(campaign, yaml_content):
    """Create or update the campaign's linked site and homepage."""
    from models import Site, SitePage
    import re

    if campaign.site_id:
        site = Site.query.get(campaign.site_id)
        if site:
            page = SitePage.query.filter_by(site_id=site.id, is_homepage=True).first()
            if page:
                page.yaml_content = yaml_content
                page.updated_at = datetime.utcnow()
                return site, page

    slug = re.sub(r'[^a-z0-9]+', '-', campaign.name.lower()).strip('-')[:60] or 'campaign'
    existing = Site.query.filter_by(org_id=g.current_org_id, slug=slug).first()
    if existing:
        slug = f"{slug}-{campaign.id[:8]}"

    site = Site(
        org_id=g.current_org_id,
        name=campaign.name,
        slug=slug,
        campaign_id=campaign.id,
    )
    db.session.add(site)
    db.session.flush()

    page = SitePage(
        site_id=site.id,
        slug='home',
        title=campaign.name,
        yaml_content=yaml_content,
        sort_order=0,
        is_homepage=True,
    )
    db.session.add(page)
    db.session.flush()

    campaign.site_id = site.id
    return site, page


def _brand_for_site(site):
    """Resolve the Brand linked to a site via site -> campaign -> brand.

    Returns a Brand or None. This is how brand edits propagate to sites:
    the theme is resolved at render time, not copied into stored YAML.
    """
    from models import Campaign, Brand
    campaign_id = getattr(site, 'campaign_id', None)
    if not campaign_id:
        return None
    campaign = Campaign.query.filter_by(id=campaign_id).first()
    if not campaign or not campaign.brand_id:
        return None
    return Brand.query.filter_by(id=campaign.brand_id).first()


def _apply_brand_theme(structure, brand):
    """Overlay the brand's colors/fonts onto the composed site theme in place."""
    from campaign.theme import merge_brand_theme
    if not brand or not structure:
        return structure
    site_node = structure[0]
    if site_node.get('name') != 'site':
        return structure
    props = site_node.setdefault('properties', {})
    props['theme'] = merge_brand_theme(props.get('theme'), brand)
    return structure


def _render_page_html(site, page):
    """Render a page to HTML, returning None on failure.

    The linked brand's theme (colors + fonts) is overlaid at render time so
    editing a brand propagates to its sites on the next render/preview/publish.
    """
    from flask import current_app
    from extensions import TOKENS, COMPONENT_DEFAULTS
    from renderer import render_yaml_structure
    from site_composer import compose_page_yaml, CompositionError

    try:
        structure = compose_page_yaml(site, page)
        _apply_brand_theme(structure, _brand_for_site(site))
        return render_yaml_structure(structure, tokens=TOKENS, defaults=COMPONENT_DEFAULTS)
    except (CompositionError, Exception) as e:
        current_app.logger.error(f"Render error for page {page.id}: {e}")
        return None
