from datetime import datetime, timezone

from app import db


class Document(db.Model):
    __tablename__ = "documents"

    # =========================================================
    # PRIMARY KEY
    # =========================================================

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    # =========================================================
    # ORIGINAL FILE NAME
    # =========================================================

    filename = db.Column(
        db.String(255),
        nullable=False
    )

    # =========================================================
    # STORED FILE PATH
    # =========================================================

    filepath = db.Column(
        db.String(500),
        nullable=False
    )

    # =========================================================
    # EXTRACTED DOCUMENT TEXT
    # =========================================================

    extracted_text = db.Column(
        db.Text,
        nullable=True
    )

    # =========================================================
    # UPLOAD DATE / TIME
    # =========================================================

    uploaded_at = db.Column(
        db.DateTime,
        default=lambda: datetime.now(timezone.utc),
        nullable=False
    )

    # =========================================================
    # USER RELATIONSHIP
    # =========================================================

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

    # =========================================================
    # STRING REPRESENTATION
    # =========================================================

    def __repr__(self):
        return f"<Document {self.filename}>"