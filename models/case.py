from datetime import datetime

from . import db


class Case(db.Model):
    __tablename__ = "cases"

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    title = db.Column(
        db.String(200),
        nullable=False
    )

    client_name = db.Column(
        db.String(150),
        nullable=False
    )

    description = db.Column(
        db.Text,
        nullable=True
    )

    status = db.Column(
        db.String(50),
        nullable=False,
        default="Новое"
    )

    created_at = db.Column(
        db.DateTime,
        default=datetime.utcnow,
        nullable=False
    )

    user_id = db.Column(
        db.Integer,
        db.ForeignKey("users.id"),
        nullable=False
    )

    documents = db.relationship(
        "Document",
        foreign_keys="Document.case_id",
        primaryjoin="Case.id == Document.case_id",
        back_populates="case",
        lazy=True,
        cascade="all, delete-orphan"
    )

    def __repr__(self):
        return f"<Case {self.id}: {self.title}>"