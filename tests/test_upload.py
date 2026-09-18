from app import create_app, db
from app.models.user import User


def create_test_app():

    app = create_app()

    app.config["TESTING"] = True

    # Test-only home route
    if "home" not in app.view_functions:

        @app.route("/test-home", endpoint="home")
        def test_home():
            return "Home"

    return app


def create_test_user(app):

    with app.app_context():

        user = User(
            username="testuser",
            email="test@example.com"
        )

        user.set_password("Test@123")

        db.session.add(user)
        db.session.commit()


def test_login_page():

    app = create_test_app()

    with app.test_client() as client:

        response = client.get("/login")

        assert response.status_code == 200


def test_register_page():

    app = create_test_app()

    with app.test_client() as client:

        response = client.get("/register")

        assert response.status_code == 200