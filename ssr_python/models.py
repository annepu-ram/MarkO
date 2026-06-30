import json
import uuid
from datetime import datetime
from extensions import db
from campaign.content_type_catalog import content_type_keys


class User(db.Model):
    __tablename__ = 'users'

    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    email = db.Column(db.String(255), nullable=False, unique=True)
    name = db.Column(db.String(255), nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    is_active = db.Column(db.Boolean, nullable=False, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    memberships = db.relationship('OrgMember', backref='user', cascade='all, delete-orphan')


class Organization(db.Model):
    __tablename__ = 'organizations'

    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    name = db.Column(db.String(255), nullable=False)
    slug = db.Column(db.String(100), nullable=False, unique=True)
    plan = db.Column(db.String(20), nullable=False, default='free')
    is_active = db.Column(db.Boolean, nullable=False, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    members = db.relationship('OrgMember', backref='organization', cascade='all, delete-orphan')
    sites = db.relationship('Site', backref='organization', cascade='all, delete-orphan')
    brands = db.relationship('Brand', backref='organization', cascade='all, delete-orphan')
    products = db.relationship('Product', backref='organization', cascade='all, delete-orphan')


class OrgMember(db.Model):
    __tablename__ = 'org_members'

    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    org_id = db.Column(db.String(36), db.ForeignKey('organizations.id'), nullable=False, index=True)
    user_id = db.Column(db.String(36), db.ForeignKey('users.id'), nullable=False, index=True)
    role = db.Column(db.String(20), nullable=False, default='editor')
    joined_at = db.Column(db.DateTime, default=datetime.utcnow)

    __table_args__ = (
        db.UniqueConstraint('org_id', 'user_id', name='uq_org_user'),
    )


class Site(db.Model):
    __tablename__ = 'sites'

    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    org_id = db.Column(db.String(36), db.ForeignKey('organizations.id'), nullable=False, index=True)
    created_by = db.Column(db.String(36), db.ForeignKey('users.id'), nullable=True)
    name = db.Column(db.String(255), nullable=False, default='Untitled Site')
    slug = db.Column(db.String(255), nullable=False)
    status = db.Column(db.String(20), nullable=False, default='draft')
    current_version = db.Column(db.Integer, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    published_at = db.Column(db.DateTime, nullable=True)
    form_secret = db.Column(db.String(64), nullable=True)
    settings = db.Column(db.Text, nullable=True)
    theme = db.Column(db.Text, nullable=True)
    brand_id = db.Column(db.String(36), db.ForeignKey('brands.id'), nullable=True, index=True)
    campaign_id = db.Column(db.String(36), nullable=True, index=True)
    source_schema_version = db.Column(db.Integer, nullable=False, default=2)

    def get_settings(self):
        """Parse settings JSON, merge with defaults for missing keys."""
        from guards import DEFAULT_SITE_SETTINGS
        stored = {}
        if self.settings:
            try:
                stored = json.loads(self.settings)
            except (json.JSONDecodeError, TypeError):
                stored = {}
        result = {}
        for category, defaults in DEFAULT_SITE_SETTINGS.items():
            result[category] = {**defaults, **(stored.get(category, {}))}
        return result

    def set_settings(self, settings_dict):
        """Serialize settings dict to JSON and store."""
        self.settings = json.dumps(settings_dict)

    source_pages = db.relationship('SitePage', backref='site', cascade='all, delete-orphan',
                                   order_by='SitePage.sort_order')
    published_pages = db.relationship('PublishedPage', backref='site', cascade='all, delete-orphan')
    shared_blocks = db.relationship('SiteSharedBlock', backref='site', cascade='all, delete-orphan',
                                    order_by='SiteSharedBlock.sort_order')
    versions = db.relationship('SiteVersion', backref='site', cascade='all, delete-orphan',
                               order_by='SiteVersion.version_number.desc()')
    submissions = db.relationship('FormSubmission', backref='site', cascade='all, delete-orphan')
    brand = db.relationship('Brand', back_populates='site', foreign_keys=[brand_id])

    __table_args__ = (
        db.UniqueConstraint('org_id', 'slug', name='uq_org_site_slug'),
    )


class SitePage(db.Model):
    __tablename__ = 'site_pages'

    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    site_id = db.Column(db.String(36), db.ForeignKey('sites.id'), nullable=False, index=True)
    slug = db.Column(db.String(255), nullable=False)
    title = db.Column(db.String(255), nullable=False, default='Untitled Page')
    yaml_content = db.Column(db.Text, nullable=False, default='')
    body_yaml_content = db.Column(db.Text, nullable=True)
    sort_order = db.Column(db.Integer, nullable=False, default=0)
    is_homepage = db.Column(db.Boolean, nullable=False, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    __table_args__ = (
        db.UniqueConstraint('site_id', 'slug', name='uq_site_source_page_slug'),
    )


class SiteSharedBlock(db.Model):
    __tablename__ = 'site_shared_blocks'

    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    site_id = db.Column(db.String(36), db.ForeignKey('sites.id'), nullable=False, index=True)
    key = db.Column(db.String(50), nullable=False)
    label = db.Column(db.String(255), nullable=False)
    yaml_content = db.Column(db.Text, nullable=False, default='[]')
    enabled = db.Column(db.Boolean, nullable=False, default=True)
    sort_order = db.Column(db.Integer, nullable=False, default=0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    __table_args__ = (
        db.UniqueConstraint('site_id', 'key', name='uq_site_shared_block_key'),
    )


class PageSharedBlockOverride(db.Model):
    __tablename__ = 'page_shared_block_overrides'

    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    page_id = db.Column(db.String(36), db.ForeignKey('site_pages.id'), nullable=False, index=True)
    block_key = db.Column(db.String(50), nullable=False)
    mode = db.Column(db.String(20), nullable=False, default='inherit')
    custom_yaml_content = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    page = db.relationship('SitePage', backref=db.backref('shared_block_overrides', cascade='all, delete-orphan'))

    __table_args__ = (
        db.UniqueConstraint('page_id', 'block_key', name='uq_page_shared_block_override'),
    )


class PublishedPage(db.Model):
    __tablename__ = 'published_pages'

    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    site_id = db.Column(db.String(36), db.ForeignKey('sites.id'), nullable=False, index=True)
    slug = db.Column(db.String(255), nullable=False)
    title = db.Column(db.String(255), nullable=False)
    rendered_html = db.Column(db.Text, nullable=False)
    sort_order = db.Column(db.Integer, default=0)
    rendered_at = db.Column(db.DateTime, default=datetime.utcnow)

    __table_args__ = (
        db.UniqueConstraint('site_id', 'slug', name='uq_site_page_slug'),
    )


# =============================================================================
# Multi-Brand CMS Models
# =============================================================================

class Brand(db.Model):
    __tablename__ = 'brands'

    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    org_id = db.Column(db.String(36), db.ForeignKey('organizations.id'), nullable=False, index=True)
    name = db.Column(db.String(255), nullable=False)
    slug = db.Column(db.String(255), nullable=False)
    status = db.Column(db.String(20), nullable=False, default='active')
    tagline = db.Column(db.String(500), nullable=True)
    description = db.Column(db.Text, nullable=True)
    industry = db.Column(db.String(80), nullable=True)
    website_url = db.Column(db.String(500), nullable=True)
    logo_url = db.Column(db.String(500), nullable=True)
    logo_media_id = db.Column(db.String(36), nullable=True, index=True)
    favicon_media_id = db.Column(db.String(36), nullable=True, index=True)
    tone = db.Column(db.String(30), nullable=True)
    voice_guidelines = db.Column(db.Text, nullable=True)
    color_primary = db.Column(db.String(20), nullable=True)
    color_secondary = db.Column(db.String(20), nullable=True)
    color_text = db.Column(db.String(20), nullable=True)
    color_accent = db.Column(db.String(20), nullable=True)
    color_background = db.Column(db.String(20), nullable=True)
    font_heading = db.Column(db.String(100), nullable=True)
    font_body = db.Column(db.String(100), nullable=True)
    default_style = db.Column(db.String(80), nullable=True)
    is_default = db.Column(db.Boolean, nullable=False, default=False)
    # --- Brand strategy fields (Phase 2) ---
    target_audience = db.Column(db.Text, nullable=True)
    brand_promise = db.Column(db.Text, nullable=True)
    positioning_statement = db.Column(db.Text, nullable=True)
    compliance_notes = db.Column(db.Text, nullable=True)
    image_style = db.Column(db.Text, nullable=True)
    cta_style = db.Column(db.Text, nullable=True)
    primary_market = db.Column(db.String(120), nullable=True)
    locale = db.Column(db.String(40), nullable=True)
    # List-like strategy fields stored as JSON text
    differentiators = db.Column(db.Text, nullable=True)
    competitors = db.Column(db.Text, nullable=True)
    forbidden_words = db.Column(db.Text, nullable=True)
    forbidden_claims = db.Column(db.Text, nullable=True)
    required_claims = db.Column(db.Text, nullable=True)
    voice_examples = db.Column(db.Text, nullable=True)
    voice_anti_examples = db.Column(db.Text, nullable=True)
    social_links = db.Column(db.Text, nullable=True)
    content_wording_prompt = db.Column(db.Text, nullable=True)
    content_wording_prompt_metadata = db.Column(db.Text, nullable=True)
    content_wording_prompt_updated_at = db.Column(db.DateTime, nullable=True)
    section_style_prompt = db.Column(db.Text, nullable=True)
    section_style_prompt_metadata = db.Column(db.Text, nullable=True)
    section_style_prompt_updated_at = db.Column(db.DateTime, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    products = db.relationship('ProductBrand', back_populates='brand', cascade='all, delete-orphan')
    campaigns = db.relationship('Campaign', back_populates='brand')
    site = db.relationship('Site', back_populates='brand', uselist=False, foreign_keys='Site.brand_id')

    # Strategy list fields exposed as JSON arrays
    STRATEGY_LIST_FIELDS = (
        'differentiators', 'competitors', 'forbidden_words', 'forbidden_claims',
        'required_claims', 'voice_examples', 'voice_anti_examples',
    )
    STRATEGY_TEXT_FIELDS = (
        'target_audience', 'brand_promise', 'positioning_statement',
        'compliance_notes', 'image_style', 'cta_style', 'primary_market', 'locale',
    )

    def get_strategy_list(self, field):
        raw = getattr(self, field, None)
        try:
            return json.loads(raw) if raw else []
        except (json.JSONDecodeError, TypeError):
            return []

    def set_strategy_list(self, field, items):
        cleaned = [str(i).strip() for i in (items or []) if str(i).strip()]
        setattr(self, field, json.dumps(cleaned))

    def get_section_style_prompt_metadata(self):
        try:
            return json.loads(self.section_style_prompt_metadata) if self.section_style_prompt_metadata else {}
        except (json.JSONDecodeError, TypeError):
            return {}

    def set_section_style_prompt_metadata(self, data):
        self.section_style_prompt_metadata = json.dumps(data or {})

    def get_content_wording_prompt_metadata(self):
        try:
            return json.loads(self.content_wording_prompt_metadata) if self.content_wording_prompt_metadata else {}
        except (json.JSONDecodeError, TypeError):
            return {}

    def set_content_wording_prompt_metadata(self, data):
        self.content_wording_prompt_metadata = json.dumps(data or {})

    def get_social_links(self):
        try:
            links = json.loads(self.social_links) if self.social_links else {}
        except (json.JSONDecodeError, TypeError):
            return {}
        return links if isinstance(links, dict) else {}

    def set_social_links(self, data):
        allowed = {'instagram', 'facebook', 'linkedin', 'x', 'youtube', 'tiktok', 'website'}
        cleaned = {}
        for key, value in (data or {}).items():
            if key in allowed and str(value or '').strip():
                cleaned[key] = str(value).strip()[:500]
        self.social_links = json.dumps(cleaned)

    __table_args__ = (
        db.UniqueConstraint('org_id', 'slug', name='uq_org_brand_slug'),
    )

    VALID_STATUSES = {'active', 'archived'}
    VALID_TONES = {
        'professional', 'friendly', 'bold', 'playful', 'authoritative', 'minimal', 'warm',
        'confident', 'premium', 'empathetic', 'educational', 'energetic', 'trustworthy',
        'aspirational', 'technical', 'witty', 'calm',
    }

    def to_dict(self, include_counts=False):
        data = {
            'id': self.id,
            'org_id': self.org_id,
            'name': self.name,
            'slug': self.slug,
            'status': self.status,
            'tagline': self.tagline,
            'description': self.description,
            'industry': self.industry,
            'website_url': self.website_url,
            'logo_url': self.logo_url,
            'logo_media_id': self.logo_media_id,
            'favicon_media_id': self.favicon_media_id,
            'tone': self.tone,
            'voice_guidelines': self.voice_guidelines,
            'colors': {
                'primary': self.color_primary,
                'secondary': self.color_secondary,
                'text': self.color_text,
                'accent': self.color_accent,
                'background': self.color_background,
            },
            'fonts': {
                'heading': self.font_heading,
                'body': self.font_body,
            },
            'default_style': self.default_style,
            'is_default': self.is_default,
            'site_id': self.site.id if self.site else None,
            'social_links': self.get_social_links(),
            'content_wording_prompt': {
                'exists': bool(self.content_wording_prompt),
                'updated_at': self.content_wording_prompt_updated_at.isoformat() if self.content_wording_prompt_updated_at else None,
                'metadata': self.get_content_wording_prompt_metadata(),
            },
            'section_style_prompt': {
                'exists': bool(self.section_style_prompt),
                'updated_at': self.section_style_prompt_updated_at.isoformat() if self.section_style_prompt_updated_at else None,
                'metadata': self.get_section_style_prompt_metadata(),
            },
            'strategy': {
                'target_audience': self.target_audience,
                'brand_promise': self.brand_promise,
                'positioning_statement': self.positioning_statement,
                'compliance_notes': self.compliance_notes,
                'image_style': self.image_style,
                'cta_style': self.cta_style,
                'primary_market': self.primary_market,
                'locale': self.locale,
                'differentiators': self.get_strategy_list('differentiators'),
                'competitors': self.get_strategy_list('competitors'),
                'forbidden_words': self.get_strategy_list('forbidden_words'),
                'forbidden_claims': self.get_strategy_list('forbidden_claims'),
                'required_claims': self.get_strategy_list('required_claims'),
                'voice_examples': self.get_strategy_list('voice_examples'),
                'voice_anti_examples': self.get_strategy_list('voice_anti_examples'),
            },
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
        }
        if include_counts:
            data['product_count'] = len(self.products or [])
            data['campaign_count'] = len(self.campaigns or [])
        return data

    def to_generation_context(self):
        ctx = {}
        if self.name:
            ctx['business_name'] = self.name
        if self.tagline:
            ctx['tagline'] = self.tagline
        if self.description:
            ctx['brand_description'] = self.description
        if self.industry:
            ctx['industry'] = self.industry
        colors = {k: v for k, v in {
            'primary': self.color_primary,
            'secondary': self.color_secondary,
            'text': self.color_text,
            'accent': self.color_accent,
            'background': self.color_background,
        }.items() if v}
        if colors:
            ctx['brand_colors'] = colors
        fonts = {k: v for k, v in {
            'heading': self.font_heading,
            'body': self.font_body,
        }.items() if v}
        if fonts:
            ctx['brand_fonts'] = fonts
        if self.tone:
            ctx['tone'] = self.tone
        if self.voice_guidelines:
            ctx['voice_guidelines'] = self.voice_guidelines
        if self.logo_url:
            ctx['logo_url'] = self.logo_url
        if self.default_style:
            ctx['style'] = self.default_style
        if self.section_style_prompt:
            ctx['section_style_prompt_updated_at'] = self.section_style_prompt_updated_at.isoformat() if self.section_style_prompt_updated_at else None
        if self.content_wording_prompt:
            ctx['content_wording_prompt_updated_at'] = self.content_wording_prompt_updated_at.isoformat() if self.content_wording_prompt_updated_at else None
        social_links = self.get_social_links()
        if social_links:
            ctx['social_links'] = social_links

        # --- Brand strategy context (Phase 2) ---
        if self.target_audience:
            ctx['target_audience'] = self.target_audience
        if self.brand_promise:
            ctx['brand_promise'] = self.brand_promise
        if self.positioning_statement:
            ctx['positioning_statement'] = self.positioning_statement
        if self.image_style:
            ctx['image_style'] = self.image_style
        if self.cta_style:
            ctx['cta_style'] = self.cta_style
        if self.primary_market:
            ctx['primary_market'] = self.primary_market
        if self.locale:
            ctx['locale'] = self.locale
        differentiators = self.get_strategy_list('differentiators')
        if differentiators:
            ctx['differentiators'] = differentiators
        competitors = self.get_strategy_list('competitors')
        if competitors:
            ctx['competitors'] = competitors
        forbidden_words = self.get_strategy_list('forbidden_words')
        if forbidden_words:
            ctx['forbidden_words'] = forbidden_words
        forbidden_claims = self.get_strategy_list('forbidden_claims')
        if forbidden_claims:
            ctx['forbidden_claims'] = forbidden_claims
        required_claims = self.get_strategy_list('required_claims')
        if required_claims:
            ctx['required_claims'] = required_claims
        voice_examples = self.get_strategy_list('voice_examples')
        if voice_examples:
            ctx['voice_examples'] = voice_examples
        voice_anti_examples = self.get_strategy_list('voice_anti_examples')
        if voice_anti_examples:
            ctx['voice_anti_examples'] = voice_anti_examples
        # Compliance notes treated as hard constraints downstream
        if self.compliance_notes:
            ctx['compliance_notes'] = self.compliance_notes
        return ctx


class Product(db.Model):
    __tablename__ = 'products'

    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    org_id = db.Column(db.String(36), db.ForeignKey('organizations.id'), nullable=False, index=True)
    name = db.Column(db.String(255), nullable=False)
    slug = db.Column(db.String(255), nullable=False)
    status = db.Column(db.String(20), nullable=False, default='draft')
    product_type = db.Column(db.String(30), nullable=False, default='service')
    short_description = db.Column(db.Text, nullable=True)
    description = db.Column(db.Text, nullable=True)
    sku = db.Column(db.String(100), nullable=True)
    price = db.Column(db.Numeric(10, 2), nullable=True)
    compare_at_price = db.Column(db.Numeric(10, 2), nullable=True)
    currency = db.Column(db.String(10), nullable=False, default='USD')
    availability = db.Column(db.String(30), nullable=False, default='service_only')
    default_media_id = db.Column(db.String(36), nullable=True, index=True)
    default_image_url = db.Column(db.String(500), nullable=True)
    attributes = db.Column(db.Text, nullable=True)
    tags = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    brands = db.relationship('ProductBrand', back_populates='product', cascade='all, delete-orphan')
    campaigns = db.relationship('CampaignProduct', back_populates='product', cascade='all, delete-orphan')

    __table_args__ = (
        db.UniqueConstraint('org_id', 'slug', name='uq_org_product_slug'),
    )

    VALID_STATUSES = {'draft', 'active', 'archived'}
    VALID_TYPES = {'physical', 'digital', 'service', 'subscription'}
    VALID_AVAILABILITY = {'in_stock', 'out_of_stock', 'preorder', 'service_only'}

    def get_tags(self):
        try:
            return json.loads(self.tags) if self.tags else []
        except (json.JSONDecodeError, TypeError):
            return []

    def set_tags(self, items):
        self.tags = json.dumps(items or [])

    def get_attributes(self):
        try:
            return json.loads(self.attributes) if self.attributes else {}
        except (json.JSONDecodeError, TypeError):
            return {}

    def set_attributes(self, data):
        self.attributes = json.dumps(data or {})

    def to_dict(self):
        return {
            'id': self.id,
            'org_id': self.org_id,
            'name': self.name,
            'slug': self.slug,
            'status': self.status,
            'product_type': self.product_type,
            'short_description': self.short_description,
            'description': self.description,
            'sku': self.sku,
            'price': float(self.price) if self.price is not None else None,
            'compare_at_price': float(self.compare_at_price) if self.compare_at_price is not None else None,
            'currency': self.currency,
            'availability': self.availability,
            'default_media_id': self.default_media_id,
            'default_image_url': self.default_image_url,
            'attributes': self.get_attributes(),
            'tags': self.get_tags(),
            'brands': [pb.brand.to_dict() for pb in (self.brands or []) if pb.brand],
            'brand_ids': [pb.brand_id for pb in (self.brands or [])],
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
        }

    def to_generation_context(self):
        ctx = {
            'name': self.name,
            'type': self.product_type,
            'short_description': self.short_description,
            'description': self.description,
            'availability': self.availability,
            'tags': self.get_tags(),
        }
        if self.price is not None:
            ctx['price'] = float(self.price)
            ctx['currency'] = self.currency
        if self.compare_at_price is not None:
            ctx['compare_at_price'] = float(self.compare_at_price)
        if self.default_image_url:
            ctx['image_url'] = self.default_image_url
        return {k: v for k, v in ctx.items() if v not in (None, '', [])}


class ProductBrand(db.Model):
    __tablename__ = 'product_brands'

    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    product_id = db.Column(db.String(36), db.ForeignKey('products.id'), nullable=False, index=True)
    brand_id = db.Column(db.String(36), db.ForeignKey('brands.id'), nullable=False, index=True)
    role = db.Column(db.String(30), nullable=False, default='associated')
    sort_order = db.Column(db.Integer, nullable=False, default=0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    product = db.relationship('Product', back_populates='brands')
    brand = db.relationship('Brand', back_populates='products')

    __table_args__ = (
        db.UniqueConstraint('product_id', 'brand_id', name='uq_product_brand'),
    )


class ProductCollection(db.Model):
    __tablename__ = 'product_collections'

    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    org_id = db.Column(db.String(36), db.ForeignKey('organizations.id'), nullable=False, index=True)
    brand_id = db.Column(db.String(36), db.ForeignKey('brands.id'), nullable=True, index=True)
    name = db.Column(db.String(255), nullable=False)
    slug = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text, nullable=True)
    status = db.Column(db.String(20), nullable=False, default='draft')
    filter_config = db.Column(db.Text, nullable=True)
    sort_order = db.Column(db.Integer, nullable=False, default=0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    items = db.relationship('ProductCollectionItem', back_populates='collection', cascade='all, delete-orphan')
    brand = db.relationship('Brand')

    __table_args__ = (
        db.UniqueConstraint('org_id', 'slug', name='uq_org_product_collection_slug'),
    )


class ProductCollectionItem(db.Model):
    __tablename__ = 'product_collection_items'

    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    collection_id = db.Column(db.String(36), db.ForeignKey('product_collections.id'), nullable=False, index=True)
    product_id = db.Column(db.String(36), db.ForeignKey('products.id'), nullable=False, index=True)
    sort_order = db.Column(db.Integer, nullable=False, default=0)

    collection = db.relationship('ProductCollection', back_populates='items')
    product = db.relationship('Product')

    __table_args__ = (
        db.UniqueConstraint('collection_id', 'product_id', name='uq_collection_product'),
    )


class MediaAsset(db.Model):
    __tablename__ = 'media_assets'

    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    org_id = db.Column(db.String(36), db.ForeignKey('organizations.id'), nullable=False, index=True)
    filename = db.Column(db.String(255), nullable=False)
    original_name = db.Column(db.String(255), nullable=True)
    storage_path = db.Column(db.String(500), nullable=True)
    url = db.Column(db.String(500), nullable=True)
    mime_type = db.Column(db.String(100), nullable=True)
    file_size = db.Column(db.Integer, nullable=True)
    width = db.Column(db.Integer, nullable=True)
    height = db.Column(db.Integer, nullable=True)
    orientation = db.Column(db.String(20), nullable=True)
    alt_text = db.Column(db.String(500), nullable=True)
    source = db.Column(db.String(30), nullable=True)
    source_url = db.Column(db.Text, nullable=True)
    license_label = db.Column(db.String(120), nullable=True)
    photographer = db.Column(db.String(255), nullable=True)
    focal_point_x = db.Column(db.Float, nullable=True)
    focal_point_y = db.Column(db.Float, nullable=True)
    tags = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def get_tags(self):
        try:
            tags = json.loads(self.tags) if self.tags else []
        except (json.JSONDecodeError, TypeError):
            return []
        return tags if isinstance(tags, list) else []

    def set_tags(self, items):
        cleaned = [str(item).strip() for item in (items or []) if str(item).strip()]
        self.tags = json.dumps(list(dict.fromkeys(cleaned[:30])))


def compute_orientation(width, height):
    """Determine image orientation from dimensions."""
    if width is None or height is None:
        return None
    ratio = width / height
    if ratio > 1.2:
        return 'landscape'
    elif ratio < 0.8:
        return 'portrait'
    else:
        return 'square'


class FormSubmission(db.Model):
    __tablename__ = 'form_submissions'

    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    site_id = db.Column(db.String(36), db.ForeignKey('sites.id'), nullable=False, index=True)
    page_slug = db.Column(db.String(255), nullable=False)
    form_name = db.Column(db.String(255), nullable=False)
    data = db.Column(db.Text, nullable=False)
    submitted_at = db.Column(db.DateTime, default=datetime.utcnow)
    ip_address = db.Column(db.String(45), nullable=True)
    user_agent = db.Column(db.String(500), nullable=True)
    is_spam = db.Column(db.Boolean, nullable=False, default=False)
    is_read = db.Column(db.Boolean, nullable=False, default=False)


class SiteVersion(db.Model):
    __tablename__ = 'site_versions'

    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    site_id = db.Column(db.String(36), db.ForeignKey('sites.id'), nullable=False, index=True)
    version_number = db.Column(db.Integer, nullable=False)
    label = db.Column(db.String(255), nullable=True)
    published_at = db.Column(db.DateTime, default=datetime.utcnow)
    published_by = db.Column(db.String(36), db.ForeignKey('users.id'), nullable=True)

    pages = db.relationship('SiteVersionPage', backref='version', cascade='all, delete-orphan',
                            order_by='SiteVersionPage.sort_order')
    shared_blocks = db.relationship('SiteVersionSharedBlock', backref='version', cascade='all, delete-orphan',
                                    order_by='SiteVersionSharedBlock.sort_order')

    __table_args__ = (
        db.UniqueConstraint('site_id', 'version_number', name='uq_site_version_number'),
    )


class SiteVersionPage(db.Model):
    __tablename__ = 'site_version_pages'

    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    version_id = db.Column(db.String(36), db.ForeignKey('site_versions.id'), nullable=False, index=True)
    slug = db.Column(db.String(255), nullable=False)
    title = db.Column(db.String(255), nullable=False)
    yaml_content = db.Column(db.Text, nullable=False)
    body_yaml_content = db.Column(db.Text, nullable=True)
    sort_order = db.Column(db.Integer, nullable=False, default=0)
    is_homepage = db.Column(db.Boolean, nullable=False, default=False)


class SiteVersionSharedBlock(db.Model):
    __tablename__ = 'site_version_shared_blocks'

    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    version_id = db.Column(db.String(36), db.ForeignKey('site_versions.id'), nullable=False, index=True)
    key = db.Column(db.String(50), nullable=False)
    label = db.Column(db.String(255), nullable=False)
    yaml_content = db.Column(db.Text, nullable=False)
    enabled = db.Column(db.Boolean, nullable=False, default=True)
    sort_order = db.Column(db.Integer, nullable=False, default=0)


class IndustryConfig(db.Model):
    """
    Stores JSON-encoded configuration data used by the guided chat flow.

    Rows are keyed by config_key:
      - 'industries'         → INDUSTRY_REGISTRY  (industry → variants → sections)
      - 'section_questions'  → SECTION_QUESTIONS  (content questions per section type)
      - 'recommendations'    → {section_pairs, category_flows}  (co-occurrence upsells)
      - 'page_purposes'      → PAGE_PURPOSES       (cross-industry page intents)

    Seed data lives in rag/industry_defaults.py (git-tracked).
    """
    __tablename__ = 'industry_configs'

    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    config_key = db.Column(db.String(50), unique=True, nullable=False)
    data = db.Column(db.Text, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def get_data(self):
        try:
            return json.loads(self.data) if self.data else {}
        except (json.JSONDecodeError, TypeError):
            return {}

    def set_data(self, data_dict):
        self.data = json.dumps(data_dict)


# =============================================================================
# Campaign Models
# =============================================================================

class Campaign(db.Model):
    __tablename__ = 'campaigns'

    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    org_id = db.Column(db.String(36), db.ForeignKey('organizations.id'), nullable=False, index=True)
    brand_id = db.Column(db.String(36), db.ForeignKey('brands.id'), nullable=True, index=True)
    name = db.Column(db.String(200), nullable=False, default='Untitled Campaign')
    status = db.Column(db.String(20), nullable=False, default='draft')
    goal = db.Column(db.String(30), nullable=True)
    site_id = db.Column(db.String(36), db.ForeignKey('sites.id'), nullable=True, index=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    brief = db.relationship('CampaignBrief', backref='campaign', uselist=False, cascade='all, delete-orphan')
    offer = db.relationship('CampaignOffer', backref='campaign', uselist=False, cascade='all, delete-orphan')
    messages = db.relationship('CampaignMessage', backref='campaign', cascade='all, delete-orphan',
                               order_by='CampaignMessage.sort_order')
    site = db.relationship('Site', foreign_keys=[site_id])
    brand = db.relationship('Brand', back_populates='campaigns')
    campaign_products = db.relationship('CampaignProduct', back_populates='campaign', cascade='all, delete-orphan')
    campaign_collections = db.relationship('CampaignCollection', back_populates='campaign', cascade='all, delete-orphan')

    VALID_STATUSES = {'draft', 'active', 'paused', 'completed'}
    VALID_GOALS = {'leads', 'calls', 'sales', 'signups', 'traffic', 'inform'}


class CampaignBrief(db.Model):
    __tablename__ = 'campaign_briefs'

    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    campaign_id = db.Column(db.String(36), db.ForeignKey('campaigns.id'), nullable=False, unique=True)
    product_or_service = db.Column(db.Text, nullable=True)
    description = db.Column(db.Text, nullable=True)
    target_audience = db.Column(db.Text, nullable=True)
    problem_or_desire = db.Column(db.Text, nullable=True)
    awareness_level = db.Column(db.String(30), nullable=True)
    buying_stage = db.Column(db.String(30), nullable=True)
    location_or_segment = db.Column(db.String(200), nullable=True)

    VALID_AWARENESS_LEVELS = {'unaware', 'problem_aware', 'solution_aware', 'product_aware', 'most_aware'}
    VALID_BUYING_STAGES = {'research', 'consideration', 'decision', 'retention'}


class CampaignOffer(db.Model):
    __tablename__ = 'campaign_offers'

    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    campaign_id = db.Column(db.String(36), db.ForeignKey('campaigns.id'), nullable=False, unique=True)
    offer = db.Column(db.Text, nullable=True)
    primary_cta = db.Column(db.String(200), nullable=True)
    secondary_cta = db.Column(db.String(200), nullable=True)
    benefits = db.Column(db.Text, nullable=True)
    proof_points = db.Column(db.Text, nullable=True)
    objections = db.Column(db.Text, nullable=True)
    faqs = db.Column(db.Text, nullable=True)

    def get_benefits(self):
        try:
            return json.loads(self.benefits) if self.benefits else []
        except (json.JSONDecodeError, TypeError):
            return []

    def set_benefits(self, items):
        self.benefits = json.dumps(items)

    def get_proof_points(self):
        try:
            return json.loads(self.proof_points) if self.proof_points else []
        except (json.JSONDecodeError, TypeError):
            return []

    def set_proof_points(self, items):
        self.proof_points = json.dumps(items)

    def get_objections(self):
        try:
            return json.loads(self.objections) if self.objections else []
        except (json.JSONDecodeError, TypeError):
            return []

    def set_objections(self, items):
        self.objections = json.dumps(items)

    def get_faqs(self):
        try:
            return json.loads(self.faqs) if self.faqs else []
        except (json.JSONDecodeError, TypeError):
            return []

    def set_faqs(self, items):
        self.faqs = json.dumps(items)


class CampaignMessage(db.Model):
    __tablename__ = 'campaign_messages'

    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    campaign_id = db.Column(db.String(36), db.ForeignKey('campaigns.id'), nullable=False, index=True)
    category = db.Column(db.String(30), nullable=False)
    content = db.Column(db.Text, nullable=False)
    is_kept = db.Column(db.Boolean, nullable=False, default=False)
    used_in_section = db.Column(db.String(100), nullable=True)
    sort_order = db.Column(db.Integer, nullable=False, default=0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    VALID_CATEGORIES = {
        'headline', 'subheadline', 'benefit', 'proof',
        'objection', 'faq', 'cta', 'testimonial',
    }


class CampaignProduct(db.Model):
    __tablename__ = 'campaign_products'

    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    campaign_id = db.Column(db.String(36), db.ForeignKey('campaigns.id'), nullable=False, index=True)
    product_id = db.Column(db.String(36), db.ForeignKey('products.id'), nullable=False, index=True)
    role = db.Column(db.String(30), nullable=False, default='promoted')
    sort_order = db.Column(db.Integer, nullable=False, default=0)

    campaign = db.relationship('Campaign', back_populates='campaign_products')
    product = db.relationship('Product', back_populates='campaigns')

    __table_args__ = (
        db.UniqueConstraint('campaign_id', 'product_id', name='uq_campaign_product'),
    )


class CampaignCollection(db.Model):
    __tablename__ = 'campaign_collections'

    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    campaign_id = db.Column(db.String(36), db.ForeignKey('campaigns.id'), nullable=False, index=True)
    collection_id = db.Column(db.String(36), db.ForeignKey('product_collections.id'), nullable=False, index=True)
    role = db.Column(db.String(30), nullable=False, default='promoted')
    sort_order = db.Column(db.Integer, nullable=False, default=0)

    campaign = db.relationship('Campaign', back_populates='campaign_collections')
    collection = db.relationship('ProductCollection')

    __table_args__ = (
        db.UniqueConstraint('campaign_id', 'collection_id', name='uq_campaign_collection'),
    )


# =============================================================================
# Brand Kit & Content Library (Org-Level CMS)
# =============================================================================

class ContentFolder(db.Model):
    """Flat optional folder for organizing content library items."""
    __tablename__ = 'content_folders'

    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    org_id = db.Column(db.String(36), db.ForeignKey('organizations.id'), nullable=False, index=True)
    name = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text, nullable=True)
    sort_order = db.Column(db.Integer, nullable=False, default=0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def to_dict(self):
        return {
            'id': self.id,
            'org_id': self.org_id,
            'name': self.name,
            'description': self.description,
            'sort_order': self.sort_order,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
        }


class ContentItem(db.Model):
    """Reusable marketing CMS content asset.

    ContentItem is the current durable asset record. It stores approved copy,
    campaign-generated winners, proof, offers, FAQs, product content, and other
    reusable marketing material with enough metadata for AI and marketers to
    select it safely.
    """
    __tablename__ = 'content_items'

    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    org_id = db.Column(db.String(36), db.ForeignKey('organizations.id'), nullable=False, index=True)
    brand_id = db.Column(db.String(36), db.ForeignKey('brands.id'), nullable=True, index=True)
    product_id = db.Column(db.String(36), db.ForeignKey('products.id'), nullable=True, index=True)
    folder_id = db.Column(db.String(36), db.ForeignKey('content_folders.id'), nullable=True, index=True)
    category = db.Column(db.String(30), nullable=False)
    status = db.Column(db.String(20), nullable=False, default='approved')
    source = db.Column(db.String(30), nullable=False, default='manual')
    channel = db.Column(db.String(30), nullable=False, default='general')
    title = db.Column(db.String(255), nullable=True)
    content = db.Column(db.Text, nullable=False)
    slots = db.Column(db.Text, nullable=True)
    tags = db.Column(db.Text, nullable=True)
    source_campaign_id = db.Column(db.String(36), nullable=True, index=True)
    source_message_id = db.Column(db.String(36), nullable=True, index=True)
    tone = db.Column(db.String(30), nullable=True)
    proof_source = db.Column(db.String(500), nullable=True)
    proof_permission_status = db.Column(db.String(30), nullable=True)
    expires_at = db.Column(db.DateTime, nullable=True)
    quality_score = db.Column(db.Integer, nullable=True)
    ai_notes = db.Column(db.Text, nullable=True)
    is_pinned = db.Column(db.Boolean, nullable=False, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    brand = db.relationship('Brand')
    product = db.relationship('Product')
    folder = db.relationship('ContentFolder')

    VALID_CATEGORIES = content_type_keys()
    VALID_STATUSES = {'draft', 'approved', 'active', 'archived', 'expired'}
    VALID_SOURCES = {'manual', 'ai', 'campaign', 'import', 'performance_winner'}
    VALID_CHANNELS = {'general', 'landing_page', 'email', 'ad', 'social', 'ecommerce'}
    VALID_PERMISSION_STATUSES = {'unknown', 'approved', 'needs_review', 'restricted'}

    def get_slots(self):
        try:
            return json.loads(self.slots) if self.slots else {}
        except (json.JSONDecodeError, TypeError):
            return {}

    def set_slots(self, data):
        self.slots = json.dumps(data or {})

    def get_tags(self):
        try:
            return json.loads(self.tags) if self.tags else []
        except (json.JSONDecodeError, TypeError):
            return []

    def set_tags(self, items):
        self.tags = json.dumps(items or [])

    def to_generation_context(self):
        ctx = {
            'id': self.id,
            'category': self.category,
            'title': self.title,
            'content': self.content,
            'status': self.status,
            'source': self.source,
            'channel': self.channel,
            'tags': self.get_tags(),
            'brand_id': self.brand_id,
            'product_id': self.product_id,
        }
        slots = self.get_slots()
        if slots:
            ctx['slots'] = slots
        if self.proof_source:
            ctx['proof_source'] = self.proof_source
        if self.proof_permission_status:
            ctx['proof_permission_status'] = self.proof_permission_status
        if self.expires_at:
            ctx['expires_at'] = self.expires_at.isoformat()
        if self.quality_score is not None:
            ctx['quality_score'] = self.quality_score
        return {k: v for k, v in ctx.items() if v not in (None, '', [], {})}


class SectionItem(db.Model):
    """Reusable, live-binding page section composed from ContentItems.

    A SectionItem is an ordered composition of existing content items (by id).
    It stores references, never frozen copies, so it re-renders on demand from
    the current content values + the owning brand's theme — editing an item or
    the brand propagates to every section that uses it.
    """
    __tablename__ = 'section_items'

    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    org_id = db.Column(db.String(36), db.ForeignKey('organizations.id'), nullable=False, index=True)
    brand_id = db.Column(db.String(36), db.ForeignKey('brands.id'), nullable=True, index=True)
    name = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text, nullable=True)
    section_type = db.Column(db.String(40), nullable=False, default='custom')
    status = db.Column(db.String(20), nullable=False, default='draft')
    content_refs = db.Column(db.Text, nullable=True)   # JSON: ordered list of content_item ids
    yaml_content = db.Column(db.Text, nullable=True)   # YAML: renderer-compatible component list
    generation_metadata = db.Column(db.Text, nullable=True)  # JSON: compiler/source metadata
    tags = db.Column(db.Text, nullable=True)           # JSON: list of strings
    is_pinned = db.Column(db.Boolean, nullable=False, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    brand = db.relationship('Brand')

    VALID_STATUSES = {'draft', 'active', 'archived'}
    VALID_SECTION_TYPES = {
        'hero', 'features', 'pricing', 'testimonials', 'faq', 'cta', 'about',
        'offer', 'products', 'value_prop', 'stats', 'footer', 'custom'
    }

    def get_content_refs(self):
        """Return the ordered list of content_item ids (strings)."""
        try:
            refs = json.loads(self.content_refs) if self.content_refs else []
        except (json.JSONDecodeError, TypeError):
            return []
        # Tolerate either bare id strings or {'content_item_id': id} dicts.
        out = []
        for ref in refs if isinstance(refs, list) else []:
            if isinstance(ref, str):
                out.append(ref)
            elif isinstance(ref, dict):
                rid = ref.get('content_item_id') or ref.get('id')
                if rid:
                    out.append(str(rid))
        return out

    def set_content_refs(self, ids):
        """Store an ordered list of content_item ids as JSON (bare strings)."""
        clean = [str(i) for i in (ids or []) if str(i).strip()]
        self.content_refs = json.dumps(clean)

    def get_generation_metadata(self):
        try:
            return json.loads(self.generation_metadata) if self.generation_metadata else {}
        except (json.JSONDecodeError, TypeError):
            return {}

    def set_generation_metadata(self, data):
        self.generation_metadata = json.dumps(data or {})

    def get_tags(self):
        try:
            return json.loads(self.tags) if self.tags else []
        except (json.JSONDecodeError, TypeError):
            return []

    def set_tags(self, items):
        self.tags = json.dumps(items or [])
