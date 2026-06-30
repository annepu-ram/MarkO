"""
Campaign semantic vocabulary — the single source of truth for V1 enums.

Mirrors `docs/plans_to_implement/SEMANTIC_LAYER_ONTOLOGY.md` §10. Recipe files,
validators, the scorer, content normalization, and section builders all read
from here. Do not fork or re-list these values elsewhere in code.

All values are snake_case.
"""

# --- Recipe / campaign dimensions ---------------------------------------------

INDUSTRY = {
    'saas', 'ecommerce', 'fashion', 'healthcare', 'education', 'finance',
    'legal', 'real_estate', 'hospitality', 'fitness', 'local_services',
    'agency', 'creator', 'nonprofit', 'marketplace', 'other',
}

# Refined, internal goal vocabulary. The user-facing Campaign.goal (6 values)
# is derived into this per ontology §4.
CONVERSION_GOAL = {
    'purchase', 'lead_generation', 'demo_booking', 'consultation_booking',
    'appointment_booking', 'trial_signup', 'webinar_registration',
    'newsletter_signup', 'app_install', 'donation', 'community_join',
    'repeat_purchase', 'retention', 'upsell',
}

AWARENESS_STAGE = {
    'unaware', 'problem_aware', 'solution_aware', 'product_aware', 'most_aware',
    'onboarding', 'retention', 'reactivation', 'expansion',
}

TRAFFIC_SOURCE = {
    'organic_search', 'paid_search', 'meta_ads', 'instagram', 'linkedin',
    'youtube', 'tiktok', 'x_twitter', 'email', 'referral', 'influencer',
    'affiliate', 'direct', 'retargeting', 'outbound', 'community', 'webinar',
}

SALES_CYCLE = {
    'impulse', 'transactional', 'consultative', 'high_consideration',
    'enterprise', 'recurring', 'seasonal',
}

BUYING_MOTIVATION = {
    'rational_evaluation', 'identity_expression', 'aspiration', 'transformation',
    'convenience', 'productivity', 'trust_safety', 'social_status',
    'trend_following', 'belonging', 'fear_avoidance', 'curiosity',
    'entertainment', 'luxury_desire',
}

DECISION_DRIVER = {
    'price', 'roi', 'convenience', 'speed', 'trust', 'aesthetics', 'novelty',
    'exclusivity', 'social_proof', 'authority', 'emotional_relief',
    'risk_reduction', 'quality', 'personalization',
}

AUDIENCE_SOPHISTICATION = {'beginner', 'aware', 'informed', 'expert'}

TRUST_REQUIREMENT = {'low', 'medium', 'high', 'critical'}

EMOTIONAL_INTENSITY = {'low', 'medium', 'high'}

PERSUASION_STYLE = {
    'authority_led', 'emotion_led', 'logic_led', 'aspiration_led',
    'transformation_led', 'urgency_led', 'education_led', 'community_led',
    'curiosity_led', 'fear_reduction',
}

CTA_STYLE = {'passive', 'soft', 'consultative', 'direct', 'urgent'}

PROOF_DEPTH = {'minimal', 'moderate', 'strong', 'extensive'}

OBJECTION_DEPTH = {'low', 'medium', 'high', 'complex'}

BRAND_STYLE = {
    'modern', 'minimalist', 'premium', 'luxury', 'playful', 'bold', 'warm',
    'trustworthy', 'technical', 'editorial', 'corporate', 'futuristic',
    'community_driven',
}

# --- Content (Content Library) dimensions -------------------------------------
# CONTENT_TYPE, COMPOSITE_TYPES, and GROUP_KEY_TO_TYPE are DERIVED from the
# canonical registry (campaign/content_registry.py) so the ontology and the
# Content Library catalog cannot drift apart. Add a content type in the registry
# once; both views update. These names are re-exported here unchanged so every
# existing `from campaign import vocabulary as V` consumer keeps working.
from campaign.content_registry import (
    ontology_keys as _ontology_keys,
    composite_ontology_keys as _composite_ontology_keys,
    group_key_to_ontology_type as _group_key_to_ontology_type,
)

CONTENT_TYPE = _ontology_keys()

# Composite types store their extra fields in slots.
COMPOSITE_TYPES = _composite_ontology_keys()

PERSUASION_ROLE = {
    'authority', 'trust_building', 'pain_agitation', 'aspiration',
    'transformation', 'social_validation', 'urgency', 'fear_reduction',
    'objection_resolution', 'mechanism_explanation', 'identity_alignment',
    'emotional_connection', 'reassurance', 'curiosity', 'exclusivity',
    'simplicity',
}

EMOTION = {
    'trust', 'fear', 'aspiration', 'relief', 'excitement', 'curiosity',
    'confidence', 'urgency', 'belonging', 'exclusivity', 'pride',
    'frustration', 'anxiety', 'hope', 'empowerment',
}

PROOF_TYPE = {
    'testimonial', 'case_study', 'metric', 'customer_count', 'review',
    'rating', 'certification', 'credential', 'media_mention', 'integration',
    'founder_story', 'before_after', 'guarantee',
}

SPECIFICITY_LEVEL = {'generic', 'semi_specific', 'specific', 'quantified'}

TRUTH_LEVEL = {'verified', 'approved', 'inferred', 'generated', 'experimental'}

SOURCE = {
    'human_input', 'website_crawl', 'uploaded_document', 'crm', 'analytics',
    'ai_generated', 'imported_campaign', 'sales_call', 'support_conversation',
    'review_platform',
}

COMPLIANCE_SENSITIVITY = {'none', 'moderate', 'high', 'regulated'}

CHANNEL = {'landing_page', 'email', 'ad', 'social', 'sms', 'seo'}

# --- Goal derivation (ontology §4) --------------------------------------------
# Simple user-facing Campaign.goal (6 values) -> refined conversion_goal.
USER_GOALS = {'leads', 'sales', 'signups', 'calls', 'traffic', 'inform'}


# Awareness stages that signal an existing-customer lifecycle motion rather
# than first-purchase acquisition. Used to refine the `sales` goal into
# repeat_purchase / upsell instead of a generic purchase.
_LIFECYCLE_RETENTION_STAGES = {'retention', 'reactivation'}
_LIFECYCLE_EXPANSION_STAGES = {'expansion'}

# Sales cycles where "calls" means a quick local booking (a slot/appointment)
# rather than a consultative sales call.
_IMPULSE_BOOKING_CYCLES = {'impulse', 'transactional', 'seasonal'}


def derive_conversion_goal(goal, sales_cycle=None, awareness_stage=None,
                           traffic_source=None):
    """Derive the refined conversion_goal from the user-facing goal + context.

    The user-facing Campaign.goal stays a short list of 6 values; this mapping
    is where it gets refined into the internal CONVERSION_GOAL vocabulary using
    the additional campaign signals available at compile time (sales_cycle,
    awareness_stage, traffic_source). Expanding the engine = expanding this
    mapping, not the user goal list (strategy imp.md, decision 3).

    Pure function. Falls back to the closest sensible default for unmapped
    combinations. Always returns a value in CONVERSION_GOAL.
    """
    g = (goal or '').strip().lower()
    sc = (sales_cycle or '').strip().lower()
    aw = (awareness_stage or '').strip().lower()
    ts = (traffic_source or '').strip().lower()

    # Webinar traffic converts to a registration regardless of the headline goal.
    if ts == 'webinar' and g in ('leads', 'signups', 'inform'):
        return 'webinar_registration'

    if g == 'calls':
        if sc == 'enterprise':
            return 'demo_booking'
        if sc in _IMPULSE_BOOKING_CYCLES:
            return 'appointment_booking'
        return 'consultation_booking'
    if g == 'leads':
        return 'lead_generation'
    if g == 'sales':
        if aw in _LIFECYCLE_RETENTION_STAGES:
            return 'repeat_purchase'
        if aw in _LIFECYCLE_EXPANSION_STAGES:
            return 'upsell'
        if sc == 'recurring':
            return 'trial_signup'
        return 'purchase'
    if g == 'signups':
        if sc == 'recurring':
            return 'trial_signup'
        return 'newsletter_signup'
    if g == 'traffic':
        return 'community_join'
    if g == 'inform':
        return 'newsletter_signup'
    # Already a refined value? pass through.
    if g in CONVERSION_GOAL:
        return g
    return 'lead_generation'


# Group key (campaign shorthand) -> content type. Derived from the registry's
# `group_key` declarations (see campaign/content_registry.py).
GROUP_KEY_TO_TYPE = _group_key_to_ontology_type()
