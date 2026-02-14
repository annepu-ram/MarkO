from flask import Flask
from dotenv import load_dotenv
from config import DevelopmentConfig, ProductionConfig
from renderer import transparency_to_hex, hex_to_rgb
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
    app.template_filter('transparency_to_hex')(transparency_to_hex)
    app.template_filter('hex_to_rgb')(hex_to_rgb)

    # Load shared data (tokens, defaults)
    from extensions import load_shared_data
    load_shared_data(app)

    # Register route blueprints
    from routes import register_blueprints
    register_blueprints(app)

    # Register security headers
    _register_security_headers(app)

    return app


def _register_security_headers(app):
    @app.after_request
    def add_security_headers(response):
        """Add security headers to all responses"""
        # Restrict iframe embedding to same origin only (prevents clickjacking)
        response.headers['X-Frame-Options'] = 'SAMEORIGIN'

        # Content Security Policy
        response.headers['Content-Security-Policy'] = (
            "default-src 'self'; "
            "script-src 'self' 'unsafe-inline'; "
            "style-src 'self' 'unsafe-inline'; "
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
    app.run(
        host=app.config.get('HOST', '127.0.0.1'),
        port=app.config.get('PORT', 5000),
        debug=app.config.get('DEBUG', False),
    )
