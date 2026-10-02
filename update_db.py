from sqlalchemy import text

from app import app
from models import db


with app.app_context():

    result = db.session.execute(
        text("PRAGMA table_info(documents)")
    )

    columns = [
        row[1]
        for row in result
    ]

    if "ai_analysis" not in columns:

        db.session.execute(
            text(
                "ALTER TABLE documents "
                "ADD COLUMN ai_analysis TEXT"
            )
        )

        db.session.commit()

        print(
            "Готово: столбец ai_analysis добавлен."
        )

    else:

        print(
            "Столбец ai_analysis уже существует."
        )