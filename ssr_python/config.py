import os


class Config:
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    PROJECT_ROOT = os.path.dirname(BASE_DIR)
    CONFIG_DIR = os.path.join(BASE_DIR, 'config')
    INSTANCE_DIR = os.path.join(BASE_DIR, 'instance')

    TOKENS_PATH = os.path.join(BASE_DIR, 'tokens.yaml')
    DEFAULTS_PATH = os.path.join(CONFIG_DIR, 'component_defaults.yaml')
    SCHEMAS_PATH = os.path.join(CONFIG_DIR, 'component_schemas.yaml')
    SCHEMA_TOKENS_PATH = os.path.join(CONFIG_DIR, 'schema_tokens.yaml')
    LLM_GUIDE_PATH = os.path.join(CONFIG_DIR, 'COMPONENT_SYNTAX_REFERENCE.md')

    SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(INSTANCE_DIR, 'swift_sites.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    UPLOAD_FOLDER = os.path.join(INSTANCE_DIR, 'uploads')
    MAX_CONTENT_LENGTH = 10 * 1024 * 1024  # 10MB max upload

    # Storage backend: 'local' | 'r2' | 'gcs'
    STORAGE_BACKEND = 'local'

    # Cloudflare R2 settings (only used when STORAGE_BACKEND='r2')
    R2_BUCKET = os.environ.get('R2_BUCKET', '')
    R2_ACCOUNT_ID = os.environ.get('R2_ACCOUNT_ID', '')
    R2_ACCESS_KEY = os.environ.get('R2_ACCESS_KEY', '')
    R2_SECRET_KEY = os.environ.get('R2_SECRET_KEY', '')
    R2_PUBLIC_DOMAIN = os.environ.get('R2_PUBLIC_DOMAIN', '')  # Custom domain or r2.dev

    # GCS settings (only used when STORAGE_BACKEND='gcs')
    GCS_BUCKET = os.environ.get('GCS_BUCKET', '')
    GCS_CREDENTIALS_PATH = os.environ.get('GCS_CREDENTIALS_PATH', '')
    GCS_CDN_DOMAIN = os.environ.get('GCS_CDN_DOMAIN', '')


class DevelopmentConfig(Config):
    DEBUG = True
    HOST = '127.0.0.1'
    PORT = 5000
    PLATFORM_DOMAIN = 'localhost'
    PUBLISHED_MODE = 'path'  # Force path-based in local dev (/s/:slug/:page)
    STORAGE_BACKEND = 'local'


class ProductionConfig(Config):
    DEBUG = False
    HOST = '127.0.0.1'
    PORT = 5000
    PLATFORM_DOMAIN = os.environ.get('PLATFORM_DOMAIN', 'swiftsites.com')
    PUBLISHED_MODE = 'auto'  # Subdomain if Host matches *.PLATFORM_DOMAIN, else path
    SERVER_NAME = os.environ.get('SERVER_NAME')  # Required for Flask subdomain routing
    STORAGE_BACKEND = os.environ.get('STORAGE_BACKEND', 'local')
