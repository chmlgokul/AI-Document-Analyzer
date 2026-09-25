import os
import json

from flask import Flask, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_swagger_ui import get_swaggerui_blueprint

from config import Config


db = SQLAlchemy()

login_manager = LoginManager()


def create_app():

    if os.environ.get("VERCEL"):
        instance_path = "/tmp/ai_document_analyzer"
    else:
        instance_path = None

    app = Flask(
    __name__,
    instance_relative_config=True,
    instance_path=instance_path,
    template_folder=os.path.join(
        os.path.dirname(__file__),
        "templates"
    ),
    static_folder=os.path.join(
        os.path.dirname(__file__),
        "static"
    )
    )

    app.config.from_object(Config)

    os.makedirs(
        app.instance_path,
        exist_ok=True
    )

    app.config["SQLALCHEMY_DATABASE_URI"] = (
        "sqlite:///"
        + os.path.join(
            app.instance_path,
            "documents_analyzer.db"
        )
    )

    db.init_app(app)

    login_manager.init_app(app)

    login_manager.login_view = "auth.login"


    # =========================
    # USER MODEL
    # =========================

    from app.models.user import User

    @login_manager.user_loader
    def load_user(user_id):

        return db.session.get(
            User,
            int(user_id)
        )


    # =========================
    # BLUEPRINTS
    # =========================

    from app.routes.auth import auth
    from app.routes.documents import documents
    from app.routes.api import api
    from app.routes.api_v1 import api_v1
    from app.routes.profile import profile


    # Register each blueprint ONLY ONCE

    app.register_blueprint(auth)

    app.register_blueprint(documents)

    app.register_blueprint(api)

    app.register_blueprint(api_v1)

    app.register_blueprint(profile)


    # =========================
    # SWAGGER UI
    # =========================

    swagger_url = "/api/docs"

    api_url = "/api/swagger.json"


    swaggerui_blueprint = get_swaggerui_blueprint(
        swagger_url,
        api_url,
        config={
            "app_name": "AI Document Analyzer API"
        }
    )


    app.register_blueprint(
        swaggerui_blueprint
    )


    # =========================
    # SWAGGER JSON
    # =========================

    @app.route("/api/swagger.json")
    def swagger_spec():

        swagger_file = os.path.join(
            os.path.dirname(__file__),
            "swagger",
            "swagger.json"
        )


        with open(
            swagger_file,
            "r",
            encoding="utf-8"
        ) as file:

            swagger_data = json.load(file)


        return jsonify(swagger_data)


    return app