from flask import render_template
from flask_login import login_required

from app import create_app, db


app = create_app()


@app.route("/")
def home():
    return render_template("home.html")


@app.route("/dashboard")
@login_required
def dashboard():
    return render_template("dashboard.html")


with app.app_context():
    db.create_all()


if __name__ == "__main__":
    app.run(debug=True)