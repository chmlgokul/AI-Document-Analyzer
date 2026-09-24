from app import create_app, db
from app.models.user import User


def create_test_app():
    """
    Create a Flask application for testing.

    The production application normally provides the real
    dashboard endpoint. The fallback below ensures that
    base.html can render in the test environment even when
    the dashboard route is not registered.
    """

    app = create_app()

    app.config["TESTING"] = True

    # =====================================================
    # TEST-ONLY FALLBACK DASHBOARD ROUTE
    # =====================================================

    if "dashboard" not in app.view_functions:

        @app.route(
            "/test-dashboard",
            endpoint="dashboard"
        )
        def test_dashboard():

            return "Dashboard"


    # =====================================================
    # TEST-ONLY FALLBACK HOME ROUTE
    # =====================================================

    if "home" not in app.view_functions:

        @app.route(
            "/test-home",
            endpoint="home"
        )
        def test_home():

            return "Home"


    return app


def create_test_user(app):

    with app.app_context():

        user = User(
            username="testuser",
            email="test@example.com"
        )

        user.set_password(
            "Test@123"
        )

        db.session.add(user)

        db.session.commit()


def test_login_page():

    app = create_test_app()

    with app.test_client() as client:

        response = client.get(
            "/login"
        )

        assert response.status_code == 200


def test_register_page():

    app = create_test_app()

    with app.test_client() as client:

        response = client.get(
            "/register"
        )

        assert response.status_code == 200