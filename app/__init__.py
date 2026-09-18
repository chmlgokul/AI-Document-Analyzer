import os

from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager

from config import Config


db = SQLAlchemy()

login_manager = LoginManager()


def create_app():

    app = Flask(
        __name__,
        instance_relative_config=True,
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


    # User model

    from app.models.user import User


    @login_manager.user_loader
    def load_user(user_id):

        return db.session.get(
            User,
            int(user_id)
        )


    # Authentication blueprint

    from app.routes.auth import auth

    app.register_blueprint(auth)


    # Documents blueprint

    from app.routes.documents import documents

    app.register_blueprint(documents)


    # Profile blueprint

    from app.routes.profile import profile

    app.register_blueprint(profile)


    return app