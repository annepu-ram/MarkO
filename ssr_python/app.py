from flask import Flask, session
from dotenv import load_dotenv
from config import DevelopmentConfig, ProductionConfig
from renderer import opacity_to_hex, hex_to_rgb
import os
import secrets
import json

load_dotenv()


def create_app(config_name=None):
    app = Flask(__name__)

    config_name = config_name or os.environ.get('FLASK_ENV', 'development')
    configs = {
        'development': DevelopmentConfig,
        'production': ProductionConfig,
    }
    app.config.from_object(configs.get(config_name, DevelopmentConfig))

    # Register custom Jinja2 filters (defined in renderer.py)
    app.template_filter('opacity_to_hex')(opacity_to_hex)
    app.template_filter('hex_to_rgb')(hex_to_rgb)

    # Initialize database
    from extensions import db
    db.init_app(app)

    # Create instance and uploads directories
    os.makedirs(app.config.get('INSTANCE_DIR', ''), exist_ok=True)
    os.makedirs(app.config.get('UPLOAD_FOLDER', ''), exist_ok=True)

    # Create tables, run migrations, bootstrap default org/user
    with app.app_context():
        import models  # noqa: F401 — registers models with SQLAlchemy
        db.create_all()
        _run_migrations(app)
        _bootstrap_default_org(app)
        _bootstrap_industry_config(app)

    # Initialize storage backend
    from storage import create_storage
    import extensions
    extensions.storage = create_storage(app.config)

    # Load shared data (tokens, defaults)
    from extensions import load_shared_data
    load_shared_data(app)

    # Register route blueprints
    from routes import register_blueprints
    register_blueprints(app)

    # Register security headers
    _register_template_context(app)
    _register_security_headers(app)

    return app


def _get_or_create_ai_request_token():
    token = session.get('ai_request_token')
    if not token:
        token = secrets.token_urlsafe(32)
        session['ai_request_token'] = token
    return token


def _register_template_context(app):
    @app.context_processor
    def inject_app_request_tokens():
        return {'ai_request_token': _get_or_create_ai_request_token()}


def _run_migrations(app):
    """Run any pending schema migrations (SQLite ALTER TABLE)."""
    from extensions import db
    with db.engine.connect() as conn:
        # Sites table migrations
        result = conn.execute(db.text("PRAGMA table_info(sites)"))
        columns = [row[1] for row in result]
        if 'settings' not in columns:
            conn.execute(db.text("ALTER TABLE sites ADD COLUMN settings TEXT"))
            conn.commit()
            app.logger.info("Migration: Added 'settings' column to sites table")
        for col, col_type in [
            ('theme', 'TEXT'),
            ('brand_id', 'VARCHAR(36)'),
            ('campaign_id', 'VARCHAR(36)'),
            ('source_schema_version', 'INTEGER DEFAULT 2 NOT NULL'),
        ]:
            if col not in columns:
                conn.execute(db.text(f"ALTER TABLE sites ADD COLUMN {col} {col_type}"))
                conn.commit()
                app.logger.info(f"Migration: Added '{col}' column to sites table")

        # SitePage table migrations — body-only YAML source for composition model
        result = conn.execute(db.text("PRAGMA table_info(site_pages)"))
        page_columns = [row[1] for row in result]
        if 'body_yaml_content' not in page_columns:
            conn.execute(db.text("ALTER TABLE site_pages ADD COLUMN body_yaml_content TEXT"))
            conn.commit()
            app.logger.info("Migration: Added 'body_yaml_content' column to site_pages table")

        # SiteVersionPage table migrations — snapshot body-only YAML too
        result = conn.execute(db.text("PRAGMA table_info(site_version_pages)"))
        version_page_columns = [row[1] for row in result]
        if 'body_yaml_content' not in version_page_columns:
            conn.execute(db.text("ALTER TABLE site_version_pages ADD COLUMN body_yaml_content TEXT"))
            conn.commit()
            app.logger.info("Migration: Added 'body_yaml_content' column to site_version_pages table")

        # Drop legacy site-scoped media. Media is now org/CMS-scoped through media_assets.
        conn.execute(db.text("DROP TABLE IF EXISTS site_images"))
        conn.commit()

        # Drop legacy org-level brand kit. Multi-brand records live in brands.
        conn.execute(db.text("DROP TABLE IF EXISTS org_brand_kits"))
        conn.commit()

        # MediaAsset table migrations — metadata powers AI image selection
        result = conn.execute(db.text("PRAGMA table_info(media_assets)"))
        media_columns = [row[1] for row in result]
        for col, col_type in [
            ('original_name', 'VARCHAR(255)'),
            ('storage_path', 'VARCHAR(500)'),
            ('url', 'VARCHAR(500)'),
            ('mime_type', 'VARCHAR(100)'),
            ('file_size', 'INTEGER'),
            ('width', 'INTEGER'),
            ('height', 'INTEGER'),
            ('orientation', 'VARCHAR(20)'),
            ('alt_text', 'VARCHAR(500)'),
            ('source', 'VARCHAR(30)'),
            ('source_url', 'TEXT'),
            ('license_label', 'VARCHAR(120)'),
            ('photographer', 'VARCHAR(255)'),
            ('focal_point_x', 'FLOAT'),
            ('focal_point_y', 'FLOAT'),
            ('tags', 'TEXT'),
        ]:
            if media_columns and col not in media_columns:
                conn.execute(db.text(f"ALTER TABLE media_assets ADD COLUMN {col} {col_type}"))
                conn.commit()
                app.logger.info(f"Migration: Added '{col}' column to media_assets table")

        # Campaign table migrations
        result = conn.execute(db.text("PRAGMA table_info(campaigns)"))
        campaign_columns = [row[1] for row in result]
        if campaign_columns and 'brand_id' not in campaign_columns:
            conn.execute(db.text("ALTER TABLE campaigns ADD COLUMN brand_id VARCHAR(36)"))
            conn.commit()
            app.logger.info("Migration: Added 'brand_id' column to campaigns table")

        # ContentItem table migrations
        result = conn.execute(db.text("PRAGMA table_info(content_items)"))
        content_columns = [row[1] for row in result]
        if content_columns and 'structured_payload' in content_columns and 'slots' not in content_columns:
            try:
                conn.execute(db.text("ALTER TABLE content_items RENAME COLUMN structured_payload TO slots"))
                conn.commit()
                app.logger.info("Migration: Renamed 'structured_payload' column to 'slots' on content_items table")
            except Exception as e:
                app.logger.warning(f"Migration: Could not rename structured_payload to slots: {e}")
                conn.execute(db.text("ALTER TABLE content_items ADD COLUMN slots TEXT"))
                conn.execute(db.text(
                    "UPDATE content_items SET slots = structured_payload "
                    "WHERE (slots IS NULL OR slots = '') AND structured_payload IS NOT NULL AND structured_payload != ''"
                ))
                conn.commit()
                app.logger.info("Migration: Added 'slots' column and copied structured_payload values")
            result = conn.execute(db.text("PRAGMA table_info(content_items)"))
            content_columns = [row[1] for row in result]
        for col, col_type in [
            ('brand_id', 'VARCHAR(36)'),
            ('product_id', 'VARCHAR(36)'),
            ('folder_id', 'VARCHAR(36)'),
            ('status', "VARCHAR(20) DEFAULT 'approved' NOT NULL"),
            ('source', "VARCHAR(30) DEFAULT 'manual' NOT NULL"),
            ('channel', "VARCHAR(30) DEFAULT 'general' NOT NULL"),
            ('slots', 'TEXT'),
            ('tags', 'TEXT'),
            ('source_message_id', 'VARCHAR(36)'),
            ('tone', 'VARCHAR(30)'),
            ('proof_source', 'VARCHAR(500)'),
            ('proof_permission_status', 'VARCHAR(30)'),
            ('expires_at', 'DATETIME'),
            ('quality_score', 'INTEGER'),
            ('ai_notes', 'TEXT'),
        ]:
            if content_columns and col not in content_columns:
                conn.execute(db.text(f"ALTER TABLE content_items ADD COLUMN {col} {col_type}"))
                conn.commit()
                app.logger.info(f"Migration: Added '{col}' column to content_items table")
        result = conn.execute(db.text("PRAGMA table_info(content_items)"))
        content_columns = [row[1] for row in result]
        if content_columns and 'structured_payload' in content_columns and 'slots' in content_columns:
            conn.execute(db.text(
                "UPDATE content_items SET slots = structured_payload "
                "WHERE (slots IS NULL OR slots = '') AND structured_payload IS NOT NULL AND structured_payload != ''"
            ))
            conn.commit()
            try:
                conn.execute(db.text("ALTER TABLE content_items DROP COLUMN structured_payload"))
                conn.commit()
                app.logger.info("Migration: Dropped legacy 'structured_payload' column from content_items table")
            except Exception as e:
                app.logger.warning(f"Migration: Could not drop legacy structured_payload column: {e}")
        if content_columns and 'slots' in content_columns:
            from campaign.content_type_catalog import primary_slot_key

            rows = conn.execute(db.text(
                "SELECT id, category, content, slots FROM content_items "
                "WHERE (slots IS NULL OR slots = '') AND content IS NOT NULL AND content != ''"
            )).fetchall()
            for row in rows:
                conn.execute(
                    db.text("UPDATE content_items SET slots = :slots WHERE id = :id"),
                    {"slots": json.dumps({primary_slot_key(row.category): row.content}), "id": row.id},
                )
            if rows:
                conn.commit()
                app.logger.info(f"Migration: Backfilled slots for {len(rows)} content item(s)")

        # Brand table migrations — Phase 2 strategy fields
        # SectionItem table migrations
        result = conn.execute(db.text("PRAGMA table_info(section_items)"))
        section_columns = [row[1] for row in result]
        for col, col_type in [
            ('section_type', "VARCHAR(40) DEFAULT 'custom' NOT NULL"),
            ('yaml_content', 'TEXT'),
            ('generation_metadata', 'TEXT'),
        ]:
            if section_columns and col not in section_columns:
                conn.execute(db.text(f"ALTER TABLE section_items ADD COLUMN {col} {col_type}"))
                conn.commit()
                app.logger.info(f"Migration: Added '{col}' column to section_items table")

        result = conn.execute(db.text("PRAGMA table_info(brands)"))
        brand_columns = [row[1] for row in result]
        for col, col_type in [
            ('color_text', 'VARCHAR(20)'),
            ('target_audience', 'TEXT'),
            ('brand_promise', 'TEXT'),
            ('positioning_statement', 'TEXT'),
            ('compliance_notes', 'TEXT'),
            ('image_style', 'TEXT'),
            ('cta_style', 'TEXT'),
            ('primary_market', 'VARCHAR(120)'),
            ('locale', 'VARCHAR(40)'),
            ('differentiators', 'TEXT'),
            ('competitors', 'TEXT'),
            ('forbidden_words', 'TEXT'),
            ('forbidden_claims', 'TEXT'),
            ('required_claims', 'TEXT'),
            ('voice_examples', 'TEXT'),
            ('voice_anti_examples', 'TEXT'),
            ('social_links', 'TEXT'),
            ('content_wording_prompt', 'TEXT'),
            ('content_wording_prompt_metadata', 'TEXT'),
            ('content_wording_prompt_updated_at', 'DATETIME'),
            ('section_style_prompt', 'TEXT'),
            ('section_style_prompt_metadata', 'TEXT'),
            ('section_style_prompt_updated_at', 'DATETIME'),
        ]:
            if brand_columns and col not in brand_columns:
                conn.execute(db.text(f"ALTER TABLE brands ADD COLUMN {col} {col_type}"))
                conn.commit()
                app.logger.info(f"Migration: Added '{col}' column to brands table")


def _bootstrap_default_org(app):
    """Create a default organization and user on first run (before auth exists)."""
    from models import User, Organization, OrgMember

    default_org = Organization.query.filter_by(slug='default').first()
    if default_org:
        return  # Already bootstrapped

    from extensions import db

    default_user = User(
        email='admin@swiftsites.local',
        name='Default Admin',
        password_hash='not-set',  # Auth not implemented yet
    )
    db.session.add(default_user)

    default_org = Organization(
        name='Default Organization',
        slug='default',
    )
    db.session.add(default_org)
    db.session.flush()  # Get IDs before creating membership

    membership = OrgMember(
        org_id=default_org.id,
        user_id=default_user.id,
        role='owner',
    )
    db.session.add(membership)
    db.session.commit()

    app.logger.info(f"Bootstrapped default org '{default_org.slug}' with user '{default_user.email}'")


def _bootstrap_industry_config(app):
    """Seed `industry_configs` table from rag/industry_defaults.py if empty."""
    from models import IndustryConfig
    if IndustryConfig.query.first() is not None:
        return  # Already seeded

    try:
        from rag.scripts.seed_industry_config import seed_industry_config
        result = seed_industry_config(force=False)
        app.logger.info(f"Seeded industry_configs table: {result}")
    except Exception as e:
        app.logger.warning(f"Failed to seed industry_configs: {e}")


def _register_security_headers(app):
    @app.after_request
    def add_security_headers(response):
        """Add security headers to all responses"""
        # Restrict iframe embedding to same origin only (prevents clickjacking)
        response.headers['X-Frame-Options'] = 'SAMEORIGIN'

        # Content Security Policy
        response.headers['Content-Security-Policy'] = (
            "default-src 'self'; "
            "script-src 'self' 'unsafe-inline' 'unsafe-eval'; "
            "style-src 'self' 'unsafe-inline' https://fonts.googleapis.com; "
            "font-src 'self' https://fonts.gstatic.com; "
            "img-src 'self' data: blob: https:; "
            "frame-src 'self'; "
            "frame-ancestors 'self'; "
            "connect-src 'self';"
        )

        # Prevent MIME type sniffing
        response.headers['X-Content-Type-Options'] = 'nosniff'

        return response


if __name__ == '__main__':
    app = create_app()
    app.run(host='0.0.0.0')
