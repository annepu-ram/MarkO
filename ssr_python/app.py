from flask import Flask
from dotenv import load_dotenv
from config import DevelopmentConfig, ProductionConfig
from renderer import opacity_to_hex, hex_to_rgb
import os

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
    _register_security_headers(app)

    return app


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

        # SiteImage table migrations — storage_path, orientation, collection_id, page_id
        result = conn.execute(db.text("PRAGMA table_info(site_images)"))
        img_columns = [row[1] for row in result]
        for col, col_type in [('storage_path', 'VARCHAR(500)'), ('orientation', 'VARCHAR(20)'),
                               ('collection_id', 'VARCHAR(36)'), ('page_id', 'VARCHAR(36)')]:
            if col not in img_columns:
                conn.execute(db.text(f"ALTER TABLE site_images ADD COLUMN {col} {col_type}"))
                conn.commit()
                app.logger.info(f"Migration: Added '{col}' column to site_images table")


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
