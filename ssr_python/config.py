import os


class Config:
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    PROJECT_ROOT = os.path.dirname(BASE_DIR)
    CONFIG_DIR = os.path.join(BASE_DIR, 'config')

    TOKENS_PATH = os.path.join(BASE_DIR, 'tokens.yaml')
    DEFAULTS_PATH = os.path.join(CONFIG_DIR, 'component_defaults.yaml')
    SCHEMAS_PATH = os.path.join(CONFIG_DIR, 'component_schemas.yaml')
    SCHEMA_TOKENS_PATH = os.path.join(CONFIG_DIR, 'schema_tokens.yaml')
    LLM_GUIDE_PATH = os.path.join(PROJECT_ROOT, 'LLM_COMPONENT_GUIDE.md')


class DevelopmentConfig(Config):
    DEBUG = True
    HOST = '127.0.0.1'
    PORT = 5000


class ProductionConfig(Config):
    DEBUG = False
    HOST = '127.0.0.1'
    PORT = 5000
