from datetime import datetime, timezone

from app import db


class Document(db.Model):
    __tablename__ = "documents"

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    filename = db.Column(
        db.String(255),
        nullable=False
    )

    filepath = db.Column(
        db.String(500),
        nullable=False
    )
    extracted_text = db.Column(
    db.Text,
    nullable=True
    )

    uploaded_at = db.Column(
        db.DateTime,
        default=lambda: datetime.now(timezone.utc),
        nullable=False
    )

    user_id = db.Column(
        db.Integer,
        db.ForeignKey("users.id"),
        nullable=False
    )

    user = db.relationship(
        "User",
        backref=db.backref(
            "documents",
            lazy=True
        )
    )

    def __repr__(self):
        return f"<Document {self.filename}>"