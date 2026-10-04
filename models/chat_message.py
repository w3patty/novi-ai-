from datetime import datetime

from . import db


class ChatMessage(db.Model):
    __tablename__ = "chat_messages"

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    user_id = db.Column(
        db.Integer,
        db.ForeignKey("users.id"),
        nullable=False
    )

    role = db.Column(
        db.String(20),
        nullable=False
    )

    content = db.Column(
        db.Text,
        nullable=True
    )

    filename = db.Column(
        db.String(255),
        nullable=True
    )

    conversation_id = db.Column(
        db.String(255),
        nullable=True
    )

    created_at = db.Column(
        db.DateTime,
        default=datetime.utcnow
    )

    user = db.relationship(
        "User",
        backref=db.backref(
            "chat_messages",
            lazy=True
        )
    )

    def __repr__(self):
        return (
            f"<ChatMessage "
            f"{self.id}: "
            f"{self.role}>"
        )