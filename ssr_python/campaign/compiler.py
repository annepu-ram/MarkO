"""
Campaign Compiler — transforms structured campaign data into builder-agent input.

Produces a section outline where each section carries a `business_content` dict.
The builder agent's existing logic ("when business_content is present, use exact values")
applies without modification.
"""


def compile_campaign_to_sections(campaign):
    """Compile a Campaign model into a list of section specs for the builder agent.

    Args:
        campaign: Campaign model instance with loaded brief, offer, and messages.

    Returns:
        dict with keys:
            - sections: list of section dicts, each with type, description, business_content
            - theme_hint: goal-derived theme suggestion
            - metadata: campaign identifiers for traceability

    Raises:
        ValueError: if campaign is missing required data (brief or offer).
    """
    brief = campaign.brief
    offer = campaign.offer

    if not brief:
        raise ValueError('Campaign brief is required before compilation.')
    if not offer:
        raise ValueError('Campaign offer is required before compilation.')

    messages_by_category = _group_messages(campaign.messages)
    sections = _build_section_outline(brief, offer, messages_by_category)

    return {
        'sections': sections,
        'theme_hint': _goal_to_theme_hint(campaign.goal),
        'metadata': {
            'campaign_id': campaign.id,
            'campaign_name': campaign.name,
            'goal': campaign.goal,
        },
    }


def compile_to_business_context(campaign, brand_kit=None, products=None, content_items=None):
    """Compile campaign into the business_context format expected by the guided pipeline.

    This bridges the campaign model to the existing RAG pipeline without modifications
    to the planner/builder/stitcher chain.

    Args:
        campaign: Campaign model with loaded brief, offer, and messages.
        brand_kit: Optional Brand instance for brand-aware generation.
        products: Optional list of Product instances selected for the campaign.
        content_items: Optional list of approved ContentItem records selected for
            the campaign's brand/product context.

    Returns:
        dict matching the guided flow's businessContext shape:
        {business_name, industry, variant_id, variant_label, description,
         sections[], style_preference, color_preference, brand_context?}

    Raises:
        ValueError: if campaign lacks required brief or offer.
    """
    brief = campaign.brief
    offer = campaign.offer

    if not brief:
        raise ValueError('Campaign brief is required before page generation.')
    if not offer:
        raise ValueError('Campaign offer is required before page generation.')

    messages_by_category = _group_messages(campaign.messages)
    # Recipes select, RAG fills (strategy imp.md decision 2): a scored recipe
    # decides the section sequence + which content fills each; the RAG builder
    # still generates each section. Falls back to the legacy hardcoded outline
    # if recipe selection can't produce a usable sequence.
    sections, recipe_meta = _build_recipe_driven_sections(
        campaign, brief, offer, messages_by_category, brand_kit,
    )
    style = _goal_to_style_preference(campaign.goal)

    products = products or []
    content_items = content_items or []
    business_name = campaign.name
    industry = 'general'
    color_preference = ''
    style_preference = style

    if brand_kit:
        brand_name = getattr(brand_kit, 'business_name', None) or getattr(brand_kit, 'name', None)
        if brand_name:
            business_name = brand_name
        brand_industry = getattr(brand_kit, 'industry', None)
        if brand_industry:
            industry = brand_industry
        brand_color = getattr(brand_kit, 'color_primary', None)
        if brand_color:
            color_preference = brand_color
        brand_style = getattr(brand_kit, 'default_style', None)
        if brand_style:
            style_preference = brand_style

    product_context = [_product_to_context(p) for p in products]
    content_context = [_content_item_to_context(item) for item in content_items]
    description = brief.description or brief.product_or_service or ''
    if product_context:
        product_lines = []
        for p in product_context:
            line = p.get('name', '')
            if p.get('short_description'):
                line = f"{line}: {p['short_description']}"
            elif p.get('description'):
                line = f"{line}: {p['description']}"
            if p.get('price') is not None:
                line = f"{line} Price: {p.get('currency', 'USD')} {p['price']}"
            if p.get('availability'):
                line = f"{line} Availability: {p['availability']}"
            product_lines.append(line)
        description = "\n".join([description, "Selected products:", *product_lines]).strip()
    if content_context:
        content_lines = []
        for item in content_context[:20]:
            category = item.get('category', 'content')
            title = item.get('title')
            prefix = f"[{category}]"
            if title:
                prefix = f"{prefix} {title}:"
            content_lines.append(f"{prefix} {item.get('content', '')}")
        description = "\n".join([description, "Approved reusable content:", *content_lines]).strip()

    gen_ctx = brand_kit.to_generation_context() if brand_kit else {}
    brand_guidance = _build_brand_guidance(gen_ctx)
    if brand_guidance:
        description = "\n".join([description, brand_guidance]).strip()

    result = {
        'business_name': business_name,
        'industry': industry,
        'variant_id': f'campaign_{campaign.id}',
        'variant_label': campaign.name,
        'description': description,
        'sections': sections,
        'style_preference': style_preference,
        'color_preference': color_preference,
    }

    if gen_ctx:
        result['brand_context'] = gen_ctx
    if product_context:
        result['product_context'] = product_context
    if content_context:
        result['content_library'] = content_context
    if recipe_meta:
        result['recipe'] = recipe_meta
        # Phase C2: bias RAG retrieval + copy toward the campaign's objective.
        if recipe_meta.get('conversion_intent'):
            result['conversion_intent'] = recipe_meta['conversion_intent']

    return result


def _build_brand_guidance(gen_ctx):
    """Render brand strategy context into a compact, marketer-free guidance block
    that the styler and builder agents consume via `business_description`.

    Internal database labels are translated into plain instructions for the LLM.
    """
    if not gen_ctx:
        return ''

    lines = []

    def _join(value):
        if isinstance(value, list):
            return '; '.join(str(v) for v in value if v)
        return str(value)

    simple = [
        ('tone', 'Voice/tone'),
        ('target_audience', 'Audience'),
        ('brand_promise', 'Brand promise'),
        ('positioning_statement', 'Positioning'),
        ('differentiators', 'Differentiators'),
        ('voice_guidelines', 'Voice guidelines'),
        ('image_style', 'Image style'),
        ('cta_style', 'CTA style'),
        ('primary_market', 'Primary market'),
        ('locale', 'Locale'),
    ]
    for key, label in simple:
        if gen_ctx.get(key):
            lines.append(f"{label}: {_join(gen_ctx[key])}")

    if gen_ctx.get('voice_examples'):
        lines.append(f"Write in this voice (good examples): {_join(gen_ctx['voice_examples'])}")
    if gen_ctx.get('voice_anti_examples'):
        lines.append(f"Avoid this voice (bad examples): {_join(gen_ctx['voice_anti_examples'])}")
    if gen_ctx.get('required_claims'):
        lines.append(f"Prefer these claims when relevant: {_join(gen_ctx['required_claims'])}")
    if gen_ctx.get('forbidden_words'):
        lines.append(f"Never use these words: {_join(gen_ctx['forbidden_words'])}")
    if gen_ctx.get('forbidden_claims'):
        lines.append(f"Never make these claims: {_join(gen_ctx['forbidden_claims'])}")
    if gen_ctx.get('compliance_notes'):
        lines.append(f"Hard compliance rules (must follow): {gen_ctx['compliance_notes']}")

    if not lines:
        return ''
    return "Brand guidelines (follow strictly):\n" + "\n".join(f"- {line}" for line in lines)


def _content_item_to_context(item):
    if hasattr(item, 'to_generation_context'):
        return item.to_generation_context()
    return {
        'id': getattr(item, 'id', ''),
        'category': getattr(item, 'category', ''),
        'title': getattr(item, 'title', ''),
        'content': getattr(item, 'content', ''),
        'status': getattr(item, 'status', ''),
        'source': getattr(item, 'source', ''),
        'channel': getattr(item, 'channel', ''),
        'brand_id': getattr(item, 'brand_id', None),
        'product_id': getattr(item, 'product_id', None),
    }


def _product_to_context(product):
    if hasattr(product, 'to_generation_context'):
        return product.to_generation_context()
    return {
        'name': getattr(product, 'name', ''),
        'short_description': getattr(product, 'short_description', ''),
        'description': getattr(product, 'description', ''),
        'price': float(product.price) if getattr(product, 'price', None) is not None else None,
        'currency': getattr(product, 'currency', 'USD'),
        'availability': getattr(product, 'availability', ''),
    }


# Brief awareness_level uses the same tokens as the ontology AWARENESS_STAGE
# subset; buying_stage maps loosely. Only the awareness_stage scoring dimension
# is needed for recipe selection.
def _build_campaign_block(campaign, brief, brand_kit):
    """Assemble the recipe-scoring + ref-resolution campaign block.

    Derives conversion_goal from the user goal (Phase A) and pulls the optional
    scoring dimensions (awareness_stage, industry, brand_style, sales_cycle,
    traffic_source) from the brief + brand where available. Also exposes a few
    ``campaign.<field>`` values (product, audience) for content_ref resolution.
    """
    from campaign import vocabulary as V

    awareness = (brief.awareness_level or '').strip().lower() or None
    if awareness and awareness not in V.AWARENESS_STAGE:
        awareness = None

    industry = None
    brand_style = None
    if brand_kit:
        bi = (getattr(brand_kit, 'industry', None) or '').strip().lower()
        if bi in V.INDUSTRY:
            industry = bi
        bs = (getattr(brand_kit, 'default_style', None) or '').strip().lower()
        if bs in V.BRAND_STYLE:
            brand_style = bs

    conversion_goal = V.derive_conversion_goal(
        campaign.goal, awareness_stage=awareness,
    )

    block = {
        'id': campaign.id,
        'name': campaign.name,
        'goal': campaign.goal,
        'conversion_goal': conversion_goal,
        'awareness_stage': awareness,
        'industry': industry,
        'brand_style': brand_style,
        # campaign.<field> refs used by recipe content_refs
        'product': brief.product_or_service or campaign.name,
        'audience': brief.target_audience or '',
    }
    return {k: v for k, v in block.items() if v not in (None, '')}


def _campaign_content_items(offer, messages, reusable_content):
    """Normalize all campaign content into the recipe engine's typed-item shape.

    Combines, in priority order: the campaign offer fields, kept campaign
    messages, and approved reusable ContentItems — all mapped through the
    canonical registry so content_refs (content.<group>[i]) resolve uniformly.
    """
    from campaign.content_registry import normalize_content_items

    grouped = {
        'promises': _pick_messages(messages, 'headline'),
        'pain_points': [],
        'benefits': list(offer.get_benefits()),
        'proof': list(offer.get_proof_points()),
        'offers': [offer.offer] if (offer.offer or '').strip() else [],
        'objections': offer.get_objections(),
        'faqs': offer.get_faqs(),
        'testimonials': _pick_messages(messages, 'testimonial'),
    }
    # Subheadlines/benefits from messages augment the offer's.
    grouped['benefits'].extend(_pick_messages(messages, 'benefit'))
    ctas = {}
    if (offer.primary_cta or '').strip():
        ctas['primary'] = offer.primary_cta
    if (offer.secondary_cta or '').strip():
        ctas['secondary'] = offer.secondary_cta
    if ctas:
        grouped['calls_to_action'] = ctas

    # Drop empty groups so normalization doesn't create blank items.
    grouped = {k: v for k, v in grouped.items() if v}

    from campaign.content import normalize_campaign_content
    items = normalize_campaign_content(grouped) if grouped else []

    # Append durable reusable library items (already typed ORM rows).
    if reusable_content:
        items = items + normalize_content_items(reusable_content)
    return items


def _build_recipe_driven_sections(campaign, brief, offer, messages, brand_kit,
                                  reusable_content=None):
    """Select a recipe and map it to guided sections; fall back on failure.

    Returns (sections, recipe_meta). recipe_meta is None when the legacy
    hardcoded outline was used (no usable recipe sequence).
    """
    import logging
    logger = logging.getLogger(__name__)

    try:
        from campaign.section_mapper import build_recipe_sections

        campaign_block = _build_campaign_block(campaign, brief, brand_kit)
        content_items = _campaign_content_items(offer, messages, reusable_content)
        explicit = _explicit_recipe_id(campaign)

        result = build_recipe_sections(
            campaign_block, content_items, explicit_recipe_id=explicit,
        )
        sections = result.get('sections') or []
        # Only adopt the recipe outline if it produced sections with content;
        # otherwise the hardcoded outline is a safer default.
        if sections and any(s.get('content') for s in sections):
            meta = dict(result.get('recipe') or {})
            meta['conversion_intent'] = result.get('conversion_intent')
            return sections, meta
        logger.info(
            'Recipe outline empty/contentless for campaign %s; using legacy sections.',
            campaign.id,
        )
    except Exception as e:  # selection/resolution must never break generation
        logger.warning(
            'Recipe-driven sections failed for campaign %s (%s); using legacy sections.',
            campaign.id, e,
        )

    return _build_guided_sections(brief, offer, messages), None


def _explicit_recipe_id(campaign):
    """An operator-pinned recipe id, if the campaign stores one. None today."""
    return getattr(campaign, 'recipe_id', None) or None


def _build_guided_sections(brief, offer, messages):
    """Build the sections array matching the guided flow format.

    Each section has: {type, content} where content maps field keys to values.
    """
    headlines = _pick_messages(messages, 'headline', limit=2)
    subheadlines = _pick_messages(messages, 'subheadline', limit=1)
    benefits_msgs = _pick_messages(messages, 'benefit', limit=5)
    testimonials = _pick_messages(messages, 'testimonial', limit=3)
    proof_msgs = _pick_messages(messages, 'proof', limit=3)

    benefits = offer.get_benefits()
    proof_points = offer.get_proof_points()
    faqs = offer.get_faqs()

    sections = []

    sections.append({
        'type': 'hero',
        'content': {
            'tagline': headlines[0] if headlines else (brief.product_or_service or ''),
            'subtagline': subheadlines[0] if subheadlines else (offer.offer or ''),
            'cta_text': offer.primary_cta or 'Get Started',
            'description': brief.description or '',
        },
    })

    if proof_points or proof_msgs:
        sections.append({
            'type': 'stats',
            'content': {
                'stats': '; '.join(proof_points[:4]) if proof_points else '; '.join(proof_msgs[:4]),
            },
        })

    if benefits or benefits_msgs:
        items = benefits if benefits else benefits_msgs
        sections.append({
            'type': 'features',
            'content': {
                'features': '; '.join(items[:6]),
                'description': f'Why choose {brief.product_or_service or "us"}',
            },
        })

    sections.append({
        'type': 'about',
        'content': {
            'description': brief.description or '',
            'audience': brief.target_audience or '',
        },
    })

    if testimonials:
        sections.append({
            'type': 'testimonials',
            'content': {
                'testimonials': '; '.join(testimonials[:3]),
            },
        })

    if faqs:
        faq_text = '; '.join(f"Q: {f['question']} A: {f['answer']}" for f in faqs[:5])
        sections.append({
            'type': 'faq',
            'content': {
                'faqs': faq_text,
            },
        })

    sections.append({
        'type': 'cta',
        'content': {
            'tagline': headlines[-1] if len(headlines) > 1 else (offer.offer or 'Get started today'),
            'cta_text': offer.primary_cta or 'Get Started',
            'secondary_cta': offer.secondary_cta or '',
        },
    })

    return sections


def _goal_to_style_preference(goal):
    """Map campaign goal to a visual style preference for the RAG pipeline."""
    styles = {
        'leads': 'modern_minimalist',
        'calls': 'organic_natural',
        'sales': 'bold_editorial',
        'signups': 'scandinavian_clean',
        'traffic': 'memphis_design',
        'inform': 'corporate_professional',
    }
    return styles.get(goal, 'modern_minimalist')


def _group_messages(messages):
    """Group messages by category, preferring kept messages first."""
    groups = {}
    for msg in messages:
        if msg.category not in groups:
            groups[msg.category] = []
        groups[msg.category].append({
            'content': msg.content,
            'is_kept': msg.is_kept,
            'used_in_section': msg.used_in_section,
        })
    for category in groups:
        groups[category].sort(key=lambda m: (not m['is_kept'], 0))
    return groups


def _build_section_outline(brief, offer, messages):
    """Build the canonical section outline from campaign data."""
    sections = []

    sections.append(_build_hero_section(brief, offer, messages))
    sections.append(_build_trust_section(offer, messages))
    sections.append(_build_benefits_section(offer, messages))
    sections.append(_build_how_it_works_section(brief))
    sections.append(_build_offer_details_section(offer, messages))
    sections.append(_build_testimonials_section(messages))
    sections.append(_build_faq_section(offer, messages))
    sections.append(_build_final_cta_section(offer, messages))

    return sections


def _pick_messages(messages, category, limit=None):
    """Pick message content strings from a category, respecting limit."""
    items = messages.get(category, [])
    if limit:
        items = items[:limit]
    return [m['content'] for m in items]


def _build_hero_section(brief, offer, messages):
    headlines = _pick_messages(messages, 'headline', limit=2)
    subheadlines = _pick_messages(messages, 'subheadline', limit=1)

    return {
        'type': 'hero',
        'description': f'Hero section for {brief.product_or_service or "campaign"}',
        'business_content': {
            'headline': headlines[0] if headlines else None,
            'subheadline': subheadlines[0] if subheadlines else None,
            'cta_text': offer.primary_cta,
            'offer_text': offer.offer,
            'product_name': brief.product_or_service,
        },
        'components': ['layout-row', 'heading', 'paragraph', 'button', 'image', 'eyebrow'],
    }


def _build_trust_section(offer, messages):
    proof_points = offer.get_proof_points()[:5]
    testimonial_snippets = _pick_messages(messages, 'testimonial', limit=3)

    return {
        'type': 'stats',
        'description': 'Trust and proof strip with key metrics or endorsements',
        'business_content': {
            'proof_points': proof_points,
            'testimonial_snippets': testimonial_snippets,
        },
        'components': ['columnsgrid', 'heading', 'paragraph', 'icon', 'counter-up'],
    }


def _build_benefits_section(offer, messages):
    benefits = offer.get_benefits()
    benefit_messages = _pick_messages(messages, 'benefit')

    return {
        'type': 'features',
        'description': 'Benefits grid showing value proposition',
        'business_content': {
            'benefits': benefits,
            'benefit_messages': benefit_messages,
        },
        'components': ['columnsgrid', 'icon', 'heading', 'paragraph'],
    }


def _build_how_it_works_section(brief):
    return {
        'type': 'how_it_works',
        'description': f'How {brief.product_or_service or "it"} works — step-by-step process',
        'business_content': {
            'product_description': brief.description,
            'awareness_level': brief.awareness_level,
            'target_audience': brief.target_audience,
        },
        'components': ['columnsgrid', 'icon', 'heading', 'paragraph', 'badge'],
    }


def _build_offer_details_section(offer, messages):
    objection_messages = _pick_messages(messages, 'objection')

    return {
        'type': 'pricing',
        'description': 'Detailed offer with objection handling',
        'business_content': {
            'offer': offer.offer,
            'secondary_cta': offer.secondary_cta,
            'objections': offer.get_objections(),
            'objection_messages': objection_messages,
        },
        'components': ['layout-row', 'heading', 'paragraph', 'button', 'badge'],
    }


def _build_testimonials_section(messages):
    testimonials = _pick_messages(messages, 'testimonial')

    return {
        'type': 'testimonials',
        'description': 'Social proof from customers',
        'business_content': {
            'testimonials': testimonials,
        },
        'components': ['columnsgrid', 'heading', 'paragraph', 'image', 'rating'],
    }


def _build_faq_section(offer, messages):
    faqs_from_offer = offer.get_faqs()
    faq_messages = _pick_messages(messages, 'faq')

    return {
        'type': 'faq',
        'description': 'Frequently asked questions',
        'business_content': {
            'faqs': faqs_from_offer,
            'faq_messages': faq_messages,
        },
        'components': ['accordion', 'heading', 'paragraph'],
    }


def _build_final_cta_section(offer, messages):
    headlines = _pick_messages(messages, 'headline')
    cta_messages = _pick_messages(messages, 'cta')

    return {
        'type': 'cta',
        'description': 'Final call-to-action',
        'business_content': {
            'primary_cta': offer.primary_cta,
            'headline': headlines[-1] if headlines else None,
            'cta_messages': cta_messages,
            'offer_summary': offer.offer,
        },
        'components': ['layout-row', 'heading', 'paragraph', 'button'],
    }


def _goal_to_theme_hint(goal):
    """Suggest a theme direction based on campaign goal."""
    hints = {
        'leads': 'professional, trust-focused, clear CTAs',
        'calls': 'warm, personal, accessible',
        'sales': 'bold, urgent, value-focused',
        'signups': 'modern, clean, minimal friction',
        'traffic': 'engaging, visual, shareable',
        'inform': 'clean, readable, authoritative',
    }
    return hints.get(goal, 'modern, professional')
