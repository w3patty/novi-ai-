from datetime import datetime

from . import db


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

    file_type = db.Column(
        db.String(50),
        nullable=False
    )

    extracted_text = db.Column(
        db.Text,
        nullable=True
    )

    ai_analysis = db.Column(
        db.Text,
        nullable=True
    )

    created_at = db.Column(
        db.DateTime,
        default=datetime.utcnow
    )

    case_id = db.Column(
        db.Integer,
        db.ForeignKey("cases.id"),
        nullable=False
    )

    case = db.relationship(
        "Case",
        foreign_keys=[case_id],
        primaryjoin="Case.id == Document.case_id",
        back_populates="documents"
    )

    def __repr__(self):
        return f"<Document {self.id}: {self.filename}>"