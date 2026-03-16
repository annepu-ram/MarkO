from routes.views import views_bp
from routes.render import render_bp
from routes.metadata import metadata_bp
from routes.images import images_bp
from routes.chat import chat_bp
from routes.site import site_bp
from routes.published import published_bp
from routes.uploads import uploads_bp
from routes.submissions import submissions_bp
from routes.rag import rag_bp
from routes.media import media_bp


def register_blueprints(app):
    app.register_blueprint(views_bp)
    app.register_blueprint(render_bp)
    app.register_blueprint(metadata_bp)
    app.register_blueprint(images_bp)
    app.register_blueprint(chat_bp)
    app.register_blueprint(site_bp)
    app.register_blueprint(published_bp)
    app.register_blueprint(uploads_bp)
    app.register_blueprint(submissions_bp)
    app.register_blueprint(rag_bp)
    app.register_blueprint(media_bp)
