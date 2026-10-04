import os
import uuid
import json

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

from services.document_parser import extract_text
from services.ai_analyzer import analyze_document


cases = Blueprint(
    "cases",
    __name__
)


ALLOWED_EXTENSIONS = {
    "pdf",
    "docx",
    "txt"
}


def allowed_file(filename):

    if "." not in filename:
        return False

    extension = filename.rsplit(
        ".",
        1
    )[1].lower()

    return extension in ALLOWED_EXTENSIONS


@cases.route(
    "/case",
    methods=["GET", "POST"]
)
@login_required
def case_list():

    if request.method == "POST":

        title = request.form.get(
            "title",
            ""
        ).strip()

        client_name = request.form.get(
            "client_name",
            ""
        ).strip()

        description = request.form.get(
            "description",
            ""
        ).strip()

        if not title or not client_name:

            flash(
                "Название дела и клиент обязательны.",
                "error"
            )

            return redirect(
                url_for("cases.case_list")
            )

        new_case = Case(
            title=title,
            client_name=client_name,
            description=description,
            status="Новое",
            user_id=current_user.id
        )

        db.session.add(new_case)
        db.session.commit()

        flash(
            "Дело успешно создано.",
            "success"
        )

        return redirect(
            url_for("cases.case_list")
        )

    user_cases = (
        Case.query
        .filter_by(
            user_id=current_user.id
        )
        .order_by(
            Case.created_at.desc()
        )
        .all()
    )

    return render_template(
        "cases.html",
        cases=user_cases
    )


@cases.route(
    "/case/<int:case_id>",
    methods=["GET"]
)
@login_required
def case_detail(case_id):

    case = (
        Case.query
        .filter_by(
            id=case_id,
            user_id=current_user.id
        )
        .first_or_404()
    )

    return render_template(
        "case.html",
        case=case
    )
@cases.route(
    "/case/<int:case_id>/delete",
    methods=["POST"]
)
@login_required
def delete_case(case_id):

    case = (
        Case.query
        .filter_by(
            id=case_id,
            user_id=current_user.id
        )
        .first_or_404()
    )

    documents = Document.query.filter_by(
        case_id=case.id
    ).all()

    for document in documents:

        if document.filepath and os.path.exists(
            document.filepath
        ):

            try:

                os.remove(
                    document.filepath
                )

            except Exception as error:

                print(
                    "Ошибка удаления файла:",
                    error
                )

        db.session.delete(
            document
        )

    db.session.delete(
        case
    )

    db.session.commit()

    flash(
        "Дело и связанные документы удалены.",
        "success"
    )

    return redirect(
        url_for(
            "cases.case_list"
        )
    )

@cases.route(
    "/documents",
    methods=["GET"]
)
@login_required
def documents():

    user_cases = (
        Case.query
        .filter_by(
            user_id=current_user.id
        )
        .all()
    )

    documents = (
        Document.query
        .join(
            Case,
            Document.case_id == Case.id
        )
        .filter(
            Case.user_id == current_user.id
        )
        .order_by(
            Document.created_at.desc()
        )
        .all()
    )

    print("========== DOCUMENTS DEBUG ==========")
    print("CURRENT USER ID:", current_user.id)
    print("DOCUMENTS COUNT:", len(documents))

    for document in documents:

        print(
            "DOCUMENT:",
            document.id,
            document.filename,
            "CASE:",
            document.case_id
        )

    print("======================================")

    return render_template(
        "documents.html",
        documents=documents,
        cases=user_cases,
        user=current_user
    )


@cases.route(
    "/case/<int:case_id>/upload",
    methods=["POST"]
)
@login_required
def upload_document(case_id):

    case = (
        Case.query
        .filter_by(
            id=case_id,
            user_id=current_user.id
        )
        .first_or_404()
    )

    file = request.files.get(
        "document"
    )

    if not file or not file.filename:

        flash(
            "Выберите документ.",
            "error"
        )

        return redirect(
            url_for(
                "cases.case_detail",
                case_id=case.id
            )
        )

    original_filename = file.filename.strip()

    if "." not in original_filename:

        flash(
            "У файла отсутствует расширение.",
            "error"
        )

        return redirect(
            url_for(
                "cases.case_detail",
                case_id=case.id
            )
        )

    extension = original_filename.rsplit(
        ".",
        1
    )[1].lower()

    if extension not in ALLOWED_EXTENSIONS:

        flash(
            "Поддерживаются только PDF, DOCX и TXT.",
            "error"
        )

        return redirect(
            url_for(
                "cases.case_detail",
                case_id=case.id
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
        str(case.id)
    )

    os.makedirs(
        upload_folder,
        exist_ok=True
    )

    filepath = os.path.join(
        upload_folder,
        unique_filename
    )

    file.save(
        filepath
    )

    try:

        extracted_text = extract_text(
            filepath,
            extension
        )

    except Exception as error:

        print(
            "Ошибка извлечения текста:",
            error
        )

        extracted_text = ""

    document = Document(
        filename=original_filename,
        filepath=filepath,
        file_type=extension,
        extracted_text=extracted_text,
        case_id=case.id
    )

    db.session.add(
        document
    )

    db.session.commit()

    print("========== DOCUMENT UPLOAD ==========")
    print("DOCUMENT ID:", document.id)
    print("FILENAME:", document.filename)
    print("CASE ID:", document.case_id)
    print("USER ID:", current_user.id)
    print("======================================")

    flash(
        "Документ успешно загружен.",
        "success"
    )

    return redirect(
        url_for(
            "cases.documents"
        )
    )


@cases.route(
    "/document/<int:document_id>/delete",
    methods=["POST"]
)
@login_required
def delete_document(document_id):

    document = (
        Document.query
        .filter_by(
            id=document_id
        )
        .first_or_404()
    )

    case = (
        Case.query
        .filter_by(
            id=document.case_id,
            user_id=current_user.id
        )
        .first_or_404()
    )

    if document.filepath and os.path.exists(
        document.filepath
    ):

        try:

            os.remove(
                document.filepath
            )

        except Exception as error:

            print(
                "Ошибка удаления файла:",
                error
            )

    db.session.delete(
        document
    )

    db.session.commit()

    flash(
        "Документ удалён.",
        "success"
    )

    return redirect(
        url_for(
            "cases.documents"
        )
    )


@cases.route(
    "/document/<int:document_id>/rename",
    methods=["POST"]
)
@login_required
def rename_document(document_id):

    document = (
        Document.query
        .filter_by(
            id=document_id
        )
        .first_or_404()
    )

    case = (
        Case.query
        .filter_by(
            id=document.case_id,
            user_id=current_user.id
        )
        .first_or_404()
    )

    new_filename = request.form.get(
        "filename",
        ""
    ).strip()

    if not new_filename:

        flash(
            "Введите новое название документа.",
            "error"
        )

        return redirect(
            url_for(
                "cases.documents"
            )
        )

    extension = document.file_type

    if not new_filename.lower().endswith(
        "." + extension
    ):

        new_filename += "." + extension

    document.filename = secure_filename(
        new_filename
    )

    db.session.commit()

    flash(
        "Название документа изменено.",
        "success"
    )

    return redirect(
        url_for(
            "cases.documents"
        )
    )

@cases.route(
    "/document/<int:document_id>/file",
    methods=["GET"]
)
@login_required
def document_file(document_id):

    document = (
        Document.query
        .filter_by(
            id=document_id
        )
        .first_or_404()
    )

    Case.query.filter_by(
        id=document.case_id,
        user_id=current_user.id
    ).first_or_404()

    if not document.filepath or not os.path.exists(
        document.filepath
    ):
        flash(
            "Файл документа не найден.",
            "error"
        )

        return redirect(
            url_for(
                "cases.document_detail",
                document_id=document.id
            )
        )

    from flask import send_file

    return send_file(
        document.filepath,
        as_attachment=False,
        download_name=document.filename
    )
@cases.route(
    "/document/<int:document_id>",
    methods=["GET"]
)
@login_required
def document_detail(document_id):

    document = (
        Document.query
        .filter_by(
            id=document_id
        )
        .first_or_404()
    )

    case = (
        Case.query
        .filter_by(
            id=document.case_id,
            user_id=current_user.id
        )
        .first_or_404()
    )

    analysis = None

    if document.ai_analysis:

        try:

            analysis = json.loads(
                document.ai_analysis
            )

            if isinstance(
                analysis,
                str
            ):

                analysis = {
                    "answer": analysis,
                    "risks": []
                }

            elif not isinstance(
                analysis,
                dict
            ):

                analysis = {
                    "answer": str(analysis),
                    "risks": []
                }

        except Exception as error:

            print(
                "Ошибка чтения AI-анализа:",
                error
            )

            analysis = {
                "answer": document.ai_analysis,
                "risks": []
            }

    return render_template(
        "document.html",
        document=document,
        case=case,
        analysis=analysis
    )


@cases.route(
    "/document/<int:document_id>/analyze",
    methods=["POST"]
)
@login_required
def analyze_document_route(document_id):

    document = (
        Document.query
        .filter_by(
            id=document_id
        )
        .first_or_404()
    )

    case = (
        Case.query
        .filter_by(
            id=document.case_id,
            user_id=current_user.id
        )
        .first_or_404()
    )

    if not document.filepath or not os.path.exists(
        document.filepath
    ):

        flash(
            "Файл документа не найден.",
            "error"
        )

        return redirect(
            url_for(
                "cases.document_detail",
                document_id=document.id
            )
        )

    try:

        analysis = analyze_document(
            document.extracted_text,
            document.filepath
        )

        if isinstance(
            analysis,
            str
        ):

            try:

                analysis = json.loads(
                    analysis
                )

            except Exception:

                analysis = {
                    "answer": analysis,
                    "risks": []
                }

        if not isinstance(
            analysis,
            dict
        ):

            analysis = {
                "answer": str(analysis),
                "risks": []
            }

        if "answer" not in analysis:

            analysis["answer"] = (
                "Анализ документа выполнен."
            )

        if "risks" not in analysis:

            analysis["risks"] = []

        document.ai_analysis = json.dumps(
            analysis,
            ensure_ascii=False
        )

        db.session.commit()

        flash(
            "Анализ документа выполнен.",
            "success"
        )

    except Exception as error:

        db.session.rollback()

        print(
            "Ошибка AI-анализа:",
            error
        )

        flash(
            "Не удалось выполнить анализ документа.",
            "error"
        )

    return redirect(
        url_for(
            "cases.document_detail",
            document_id=document.id
        )
    )