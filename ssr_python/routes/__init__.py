from routes.views import views_bp
from routes.render import render_bp
from routes.metadata import metadata_bp
from routes.images import images_bp
from routes.chat import chat_bp


def register_blueprints(app):
    app.register_blueprint(views_bp)
    app.register_blueprint(render_bp)
    app.register_blueprint(metadata_bp)
    app.register_blueprint(images_bp)
    app.register_blueprint(chat_bp)
