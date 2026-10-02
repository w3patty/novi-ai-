import os

from flask import Flask

from config import Config
from models import db, login_manager
from models.user import User


def create_app():
    app = Flask(__name__)

    # ==========================================
    # CONFIG
    # ==========================================

    app.config.from_object(Config)

    # ==========================================
    # FOLDERS
    # ==========================================

    os.makedirs(
        os.path.join(app.root_path, "instance"),
        exist_ok=True
    )

    # ==========================================
    # DATABASE
    # ==========================================

    db.init_app(app)

    # ==========================================
    # LOGIN
    # ==========================================

    login_manager.init_app(app)
    login_manager.login_view = "auth.login"

    # ==========================================
    # MODELS
    # ==========================================

    from models.case import Case
    from models.document import Document

    # ==========================================
    # DATABASE CREATE
    # ==========================================

    with app.app_context():
        db.create_all()

    # ==========================================
    # BLUEPRINTS
    # ==========================================

    from routes.main import main
    from routes.auth import auth
    from routes.cases import cases

    app.register_blueprint(main)
    app.register_blueprint(auth)
    app.register_blueprint(cases)

    # ==========================================
    # HOME CHECK
    # ==========================================

    @app.context_processor
    def inject_app_name():
        return {
            "app_name": "LegalAI"
        }

    return app


# ==========================================
# USER LOADER
# ==========================================

@login_manager.user_loader
def load_user(user_id):

    try:
        return db.session.get(
            User,
            int(user_id)
        )
    except (ValueError, TypeError):
        return None


# ==========================================
# APPLICATION
# ==========================================

app = create_app()


# ==========================================
# RUN
# ==========================================

if __name__ == "__main__":

    app.run(
        debug=True,
        host="127.0.0.1",
        port=5000
    )