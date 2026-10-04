import os
import uuid

from flask import (
    Blueprint,
    render_template,
    request,
    redirect,
    url_for,
    flash,
    current_app
)

from flask_login import (
    login_required,
    current_user
)

from werkzeug.utils import secure_filename

from models import db
from models.case import Case
from models.document import Document
from models.user import User
from services.ai_analyzer import analyze_document


main = Blueprint(
    "main",
    __name__
)


ALLOWED_EXTENSIONS = {
    "pdf",
    "docx",
    "txt"
}


def allowed_file(filename):

    if not filename:
        return False

    if "." not in filename:
        return False

    extension = filename.rsplit(
        ".",
        1
    )[1].lower()

    return extension in ALLOWED_EXTENSIONS


@main.route("/")
def index():

    return render_template(
        "index.html"
    )


@main.route("/dashboard")
@login_required
def dashboard():

    cases_count = Case.query.filter_by(
        user_id=current_user.id
    ).count()

    documents_count = (
        Document.query
        .join(
            Case,
            Document.case_id == Case.id
        )
        .filter(
            Case.user_id == current_user.id
        )
        .count()
    )

    analyses_count = (
        Document.query
        .join(
            Case,
            Document.case_id == Case.id
        )
        .filter(
            Case.user_id == current_user.id
        )
        .filter(
            Document.ai_analysis.isnot(None)
        )
        .filter(
            Document.ai_analysis != ""
        )
        .count()
    )

    return render_template(
        "dashboard.html",
        user=current_user,
        cases_count=cases_count,
        documents_count=documents_count,
        analyses_count=analyses_count
    )


@main.route(
    "/ai-assistant",
    methods=["GET", "POST"]
)
@login_required
def ai_assistant():

    result = None
    filename = None

    if request.method == "POST":

        query = request.form.get(
            "question",
            ""
        ).strip()

        file = request.files.get(
            "document"
        )

        file_path = None

        print(
            "========== AI ASSISTANT DEBUG =========="
        )

        print(
            "QUERY:",
            query
        )

        print(
            "FILE OBJECT:",
            file
        )

        print(
            "FILE FILENAME:",
            file.filename if file else None
        )

        print(
            "FILE CONTENT TYPE:",
            file.content_type if file else None
        )

        print(
            "========================================"
        )

        try:

            if file and file.filename:

                original_filename = file.filename.strip()

                print(
                    "ORIGINAL FILENAME:",
                    original_filename
                )

                if "." not in original_filename:

                    print(
                        "ОШИБКА: в имени файла нет точки"
                    )

                    flash(
                        "Не удалось определить тип файла.",
                        "error"
                    )

                    return redirect(
                        url_for(
                            "main.ai_assistant"
                        )
                    )

                extension = original_filename.rsplit(
                    ".",
                    1
                )[1].lower()

                print(
                    "РАСШИРЕНИЕ:",
                    extension
                )

                if extension not in ALLOWED_EXTENSIONS:

                    print(
                        "ОШИБКА: неподдерживаемое расширение"
                    )

                    flash(
                        "Поддерживаются только PDF, DOCX и TXT.",
                        "error"
                    )

                    return redirect(
                        url_for(
                            "main.ai_assistant"
                        )
                    )

                filename = secure_filename(
                    original_filename
                )

                print(
                    "SECURE FILENAME:",
                    filename
                )

                if not filename:

                    print(
                        "ОШИБКА: secure_filename вернул пустое имя"
                    )

                    flash(
                        "Некорректное имя файла.",
                        "error"
                    )

                    return redirect(
                        url_for(
                            "main.ai_assistant"
                        )
                    )

                unique_filename = (
                    str(uuid.uuid4())
                    + "."
                    + extension
                )

                upload_folder = os.path.join(
                    current_app.root_path,
                    "uploads",
                    str(current_user.id),
                    "assistant"
                )

                os.makedirs(
                    upload_folder,
                    exist_ok=True
                )

                file_path = os.path.join(
                    upload_folder,
                    unique_filename
                )

                print(
                    "FILE PATH:",
                    file_path
                )

                file.save(
                    file_path
                )

                print(
                    "Файл сохранён:",
                    file_path
                )

            if not query and not file_path:

                print(
                    "ОШИБКА: нет вопроса и файла"
                )

                flash(
                    "Введите вопрос или загрузите документ.",
                    "error"
                )

                return redirect(
                    url_for(
                        "main.ai_assistant"
                    )
                )

            print(
                "ПЕРЕД ОТПРАВКОЙ В DIFY"
            )

            result = analyze_document(
                text=query,
                file_path=file_path
            )

            print(
                "Результат AI:",
                result
            )

        except Exception as error:

            print(
                "ОШИБКА AI ASSISTANT:",
                repr(error)
            )

            flash(
                "Не удалось выполнить AI-анализ. "
                "Проверьте подключение Dify.",
                "error"
            )

    return render_template(
        "ai_assistant.html",
        user=current_user,
        result=result,
        filename=filename
    )


@main.route("/templates")
@login_required
def templates_page():

    return render_template(
        "templates_page.html",
        user=current_user
    )


@main.route("/templates/<template_id>")
@login_required
def template_detail(template_id):

    templates = {

        "service-contract": {
            "title": "Договор оказания услуг",

            "description": (
                "Шаблон договора между заказчиком "
                "и исполнителем на оказание услуг."
            ),

            "content": """
ДОГОВОР ОКАЗАНИЯ УСЛУГ

г. ____________                         «___» __________ 20___ г.


ЗАКАЗЧИК:

ФИО / Наименование: ________________________________

Адрес: ____________________________________________

Телефон: __________________________________________


ИСПОЛНИТЕЛЬ:

ФИО / Наименование: ________________________________

Адрес: ____________________________________________

Телефон: __________________________________________


1. ПРЕДМЕТ ДОГОВОРА

1.1. Исполнитель обязуется оказать Заказчику следующие услуги:

____________________________________________________

____________________________________________________


1.2. Заказчик обязуется принять оказанные услуги
и оплатить их в установленном порядке.


2. СТОИМОСТЬ УСЛУГ

2.1. Стоимость услуг составляет:

____________________________________________________


2.2. Порядок оплаты:

____________________________________________________


3. ПРАВА И ОБЯЗАННОСТИ СТОРОН

3.1. Исполнитель обязан качественно и своевременно оказать услуги.

3.2. Заказчик обязан предоставить необходимую информацию
для выполнения работ.


4. ОТВЕТСТВЕННОСТЬ СТОРОН

4.1. Стороны несут ответственность в соответствии
с действующим законодательством.


5. СРОК ДЕЙСТВИЯ ДОГОВОРА

5.1. Договор вступает в силу с момента его подписания.


6. РЕКВИЗИТЫ И ПОДПИСИ СТОРОН

ЗАКАЗЧИК:

ФИО: __________________________

Подпись: ______________________


ИСПОЛНИТЕЛЬ:

ФИО: __________________________

Подпись: ______________________
"""
        },

        "employment-contract": {
            "title": "Трудовой договор",

            "description": (
                "Основные условия трудовых отношений "
                "между работником и работодателем."
            ),

            "content": """
ТРУДОВОЙ ДОГОВОР

г. ____________                         «___» __________ 20___ г.


РАБОТОДАТЕЛЬ:

_______________________________________________


РАБОТНИК:

_______________________________________________


1. ОБЩИЕ ПОЛОЖЕНИЯ

1.1. Работник принимается на должность:

____________________________________________________


1.2. Место работы:

____________________________________________________


2. ТРУДОВЫЕ ОБЯЗАННОСТИ

2.1. Работник обязан добросовестно выполнять
свои трудовые обязанности.

2.2. Работник обязан соблюдать правила
внутреннего трудового распорядка.


3. ОПЛАТА ТРУДА

3.1. Размер заработной платы:

____________________________________________________


3.2. Порядок выплаты заработной платы:

____________________________________________________


4. РЕЖИМ РАБОТЫ

4.1. Рабочее время:

____________________________________________________


5. СРОК ДЕЙСТВИЯ

5.1. Настоящий договор действует с:

____________________________________________________


6. ПОДПИСИ СТОРОН

РАБОТОДАТЕЛЬ:

__________________________


РАБОТНИК:

__________________________
"""
        },

        "claim": {
            "title": "Претензия",

            "description": (
                "Шаблон досудебной претензии "
                "с основными требованиями."
            ),

            "content": """
ПРЕТЕНЗИЯ

Кому: ______________________________________________

От: _______________________________________________

Адрес: ____________________________________________

Телефон: __________________________________________

Электронная почта: _________________________________


ОБСТОЯТЕЛЬСТВА

«___» __________ 20___ года:

____________________________________________________

____________________________________________________


В результате:

____________________________________________________

____________________________________________________


ТРЕБОВАНИЯ

На основании изложенного прошу:

1. _________________________________________________

2. _________________________________________________

3. _________________________________________________


Срок исполнения требований:

____________________________________________________


В случае невыполнения требований в установленный срок
я оставляю за собой право обратиться за защитой своих
прав в установленном законом порядке.


Дата: «___» __________ 20___ г.

Подпись: ______________________
"""
        },

        "lawsuit": {
            "title": "Исковое заявление",

            "description": (
                "Основная структура заявления "
                "для обращения в суд."
            ),

            "content": """
ИСКОВОЕ ЗАЯВЛЕНИЕ

В _________________________________________________ суд


ИСТЕЦ:

ФИО: ______________________________________________

Адрес: ____________________________________________

Телефон: __________________________________________


ОТВЕТЧИК:

ФИО / Наименование: ________________________________

Адрес: ____________________________________________


ЦЕНА ИСКА:

____________________________________________________


ОБСТОЯТЕЛЬСТВА ДЕЛА

____________________________________________________

____________________________________________________

____________________________________________________


ПРАВОВОЕ ОБОСНОВАНИЕ

____________________________________________________

____________________________________________________


ТРЕБОВАНИЯ ИСТЦА

На основании изложенного прошу суд:

1. _________________________________________________

2. _________________________________________________

3. _________________________________________________


ПРИЛОЖЕНИЯ

1. _________________________________________________

2. _________________________________________________

3. _________________________________________________


Дата: «___» __________ 20___ г.

Подпись: ______________________
"""
        },

        "power-of-attorney": {
            "title": "Доверенность",

            "description": (
                "Шаблон доверенности для "
                "представления интересов."
            ),

            "content": """
ДОВЕРЕННОСТЬ

г. ____________                         «___» __________ 20___ г.


Я, __________________________________________________,

паспорт: ___________________________________________,

настоящей доверенностью уполномочиваю:

____________________________________________________,

паспорт: ___________________________________________,


ПРЕДСТАВЛЯТЬ МОИ ИНТЕРЕСЫ:

____________________________________________________


ПРЕДСТАВИТЕЛЮ ПРЕДОСТАВЛЯЮТСЯ ПОЛНОМОЧИЯ:

1. Представлять мои интересы перед организациями
и государственными органами.

2. Подавать и получать необходимые документы.

3. Подписывать документы, необходимые для выполнения
поручения.

4. Совершать иные действия в пределах предоставленных
полномочий.


СРОК ДЕЙСТВИЯ:

____________________________________________________


ПОДПИСЬ ДОВЕРИТЕЛЯ:

__________________________
"""
        },

        "nda": {
            "title": "Соглашение о конфиденциальности",

            "description": (
                "Шаблон NDA для защиты "
                "конфиденциальной информации."
            ),

            "content": """
СОГЛАШЕНИЕ О КОНФИДЕНЦИАЛЬНОСТИ

г. ____________                         «___» __________ 20___ г.


СТОРОНА 1:

____________________________________________________


СТОРОНА 2:

____________________________________________________


1. ПРЕДМЕТ СОГЛАШЕНИЯ

Стороны обязуются сохранять конфиденциальность
информации, полученной в рамках сотрудничества.


2. КОНФИДЕНЦИАЛЬНАЯ ИНФОРМАЦИЯ

К конфиденциальной информации относится:

____________________________________________________

____________________________________________________


3. ОБЯЗАННОСТИ СТОРОН

3.1. Не раскрывать конфиденциальную информацию
третьим лицам без предварительного согласия другой стороны.

3.2. Использовать информацию только для целей сотрудничества.


4. ОТВЕТСТВЕННОСТЬ

За нарушение условий настоящего соглашения стороны
несут ответственность в соответствии с применимым
законодательством.


5. СРОК ДЕЙСТВИЯ

____________________________________________________


ПОДПИСИ СТОРОН


СТОРОНА 1:

__________________________


СТОРОНА 2:

__________________________
"""
        }

    }

    template = templates.get(
        template_id
    )

    if template is None:

        flash(
            "Шаблон не найден.",
            "error"
        )

        return redirect(
            url_for(
                "main.templates_page"
            )
        )

    return render_template(
        "template_detail.html",
        template=template,
        user=current_user
    )



@main.route(
    "/settings",
    methods=["GET", "POST"]
)
@login_required
def settings():

    if request.method == "POST":

        action = request.form.get(
            "action",
            ""
        )

        # Изменение профиля

        if action == "profile":

            username = request.form.get(
                "username",
                ""
            ).strip()

            email = request.form.get(
                "email",
                ""
            ).strip()

            if not username or not email:

                flash(
                    "Заполните все поля профиля.",
                    "error"
                )

                return redirect(
                    url_for(
                        "main.settings"
                    )
                )

            existing_username = User.query.filter(
                User.username == username,
                User.id != current_user.id
            ).first()

            if existing_username:

                flash(
                    "Это имя пользователя уже занято.",
                    "error"
                )

                return redirect(
                    url_for(
                        "main.settings"
                    )
                )

            existing_email = User.query.filter(
                User.email == email,
                User.id != current_user.id
            ).first()

            if existing_email:

                flash(
                    "Этот email уже используется.",
                    "error"
                )

                return redirect(
                    url_for(
                        "main.settings"
                    )
                )

            current_user.username = username
            current_user.email = email

            db.session.commit()

            flash(
                "Профиль успешно обновлён.",
                "success"
            )

            return redirect(
                url_for(
                    "main.settings"
                )
            )

        # Изменение пароля

        if action == "password":

            current_password = request.form.get(
                "current_password",
                ""
            )

            new_password = request.form.get(
                "new_password",
                ""
            )

            confirm_password = request.form.get(
                "confirm_password",
                ""
            )

            if not current_password:

                flash(
                    "Введите текущий пароль.",
                    "error"
                )

                return redirect(
                    url_for(
                        "main.settings"
                    )
                )

            if not current_user.check_password(
                current_password
            ):

                flash(
                    "Текущий пароль введён неправильно.",
                    "error"
                )

                return redirect(
                    url_for(
                        "main.settings"
                    )
                )

            if len(new_password) < 6:

                flash(
                    "Новый пароль должен содержать минимум 6 символов.",
                    "error"
                )

                return redirect(
                    url_for(
                        "main.settings"
                    )
                )

            if new_password != confirm_password:

                flash(
                    "Новые пароли не совпадают.",
                    "error"
                )

                return redirect(
                    url_for(
                        "main.settings"
                    )
                )

            current_user.set_password(
                new_password
            )

            db.session.commit()

            flash(
                "Пароль успешно изменён.",
                "success"
            )

            return redirect(
                url_for(
                    "main.settings"
                )
            )

        flash(
            "Неизвестное действие.",
            "error"
        )

        return redirect(
            url_for(
                "main.settings"
            )
        )

    return render_template(
        "settings.html",
        user=current_user
    )