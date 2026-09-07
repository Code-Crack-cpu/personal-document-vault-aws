from flask import Flask
from dotenv import load_dotenv

load_dotenv()

from app.config import Config


def create_app() -> Flask:
    load_dotenv()
    app = Flask(__name__, template_folder="../templates", static_folder="../static")
    app.config.from_object(Config)

    from app.routes.auth import auth_bp
    from app.routes.documents import documents_bp
    from app.routes.main import main_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(documents_bp)
    app.register_blueprint(main_bp)
    return app
