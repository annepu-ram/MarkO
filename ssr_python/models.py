import json
import uuid
from datetime import datetime
from extensions import db


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
    versions = db.relationship('SiteVersion', backref='site', cascade='all, delete-orphan',
                               order_by='SiteVersion.version_number.desc()')
    images = db.relationship('SiteImage', backref='site', cascade='all, delete-orphan')
    submissions = db.relationship('FormSubmission', backref='site', cascade='all, delete-orphan')

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
    sort_order = db.Column(db.Integer, nullable=False, default=0)
    is_homepage = db.Column(db.Boolean, nullable=False, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    __table_args__ = (
        db.UniqueConstraint('site_id', 'slug', name='uq_site_source_page_slug'),
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


class SiteImage(db.Model):
    __tablename__ = 'site_images'

    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    site_id = db.Column(db.String(36), db.ForeignKey('sites.id'), nullable=True, index=True)
    page_id = db.Column(db.String(36), db.ForeignKey('site_pages.id'), nullable=True, index=True)
    filename = db.Column(db.String(255), nullable=False)
    original_name = db.Column(db.String(255))
    mime_type = db.Column(db.String(100))
    file_size = db.Column(db.Integer)
    width = db.Column(db.Integer, nullable=True)
    height = db.Column(db.Integer, nullable=True)
    source = db.Column(db.String(20))
    source_url = db.Column(db.Text, nullable=True)
    photographer = db.Column(db.String(255), nullable=True)
    alt_text = db.Column(db.String(500), nullable=True)
    storage_path = db.Column(db.String(500), nullable=True)    # "org_id/site_id/uuid.webp"
    orientation = db.Column(db.String(20), nullable=True)       # "landscape" | "portrait" | "square"
    created_at = db.Column(db.DateTime, default=datetime.utcnow)


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
    sort_order = db.Column(db.Integer, nullable=False, default=0)
    is_homepage = db.Column(db.Boolean, nullable=False, default=False)


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
