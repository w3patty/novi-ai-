import json
import mimetypes
import os

import requests
from dotenv import load_dotenv


load_dotenv()


DIFY_API_KEY = os.getenv("DIFY_API_KEY")
DIFY_API_URL = os.getenv(
    "DIFY_API_URL",
    "https://api.dify.ai/v1"
)


def parse_ai_response(answer):
    """
    Преобразует ответ Dify в словарь.
    Если Dify вернул JSON — возвращает его.
    Если пришёл обычный текст — сохраняет его в answer.
    """

    if not answer:
        return {
            "answer": "",
            "risks": []
        }

    answer = answer.strip()

    # Убираем Markdown-обёртку, если модель случайно
    # вернула JSON внутри ```json ... ```
    if answer.startswith("```json"):
        answer = answer[7:]

    elif answer.startswith("```"):
        answer = answer[3:]

    if answer.endswith("```"):
        answer = answer[:-3]

    answer = answer.strip()

    try:
        data = json.loads(answer)

        if isinstance(data, dict):

            if "answer" not in data:
                data["answer"] = ""

            if "risks" not in data:
                data["risks"] = []

            return data

    except json.JSONDecodeError as error:
        print("JSON ERROR:", error)

    return {
        "answer": answer,
        "risks": []
    }


def upload_file_to_dify(file_path):
    """
    Загружает файл в Dify через /files/upload
    и возвращает ID загруженного файла.
    """

    if not DIFY_API_KEY:
        raise Exception(
            "DIFY_API_KEY не найден в .env"
        )

    if not file_path:
        raise Exception(
            "Путь к файлу не указан."
        )

    if not os.path.exists(file_path):
        raise Exception(
            f"Файл не найден: {file_path}"
        )

    url = (
        f"{DIFY_API_URL}"
        "/files/upload"
    )

    headers = {
        "Authorization":
            f"Bearer {DIFY_API_KEY}"
    }

    filename = os.path.basename(
        file_path
    )

    mime_type, _ = mimetypes.guess_type(
        filename
    )

    if not mime_type:
        mime_type = (
            "application/octet-stream"
        )

    print()
    print("========== DIFY FILE UPLOAD ==========")
    print("FILE:", file_path)
    print("FILENAME:", filename)
    print("MIME TYPE:", mime_type)

    try:

        with open(
            file_path,
            "rb"
        ) as file:

            files = {
                "file": (
                    filename,
                    file,
                    mime_type
                )
            }

            data = {
                "user": "legalai-user"
            }

            response = requests.post(
                url,
                headers=headers,
                files=files,
                data=data,
                timeout=120
            )

    except Exception as error:

        print(
            "ОШИБКА ПРИ ЗАГРУЗКЕ ФАЙЛА:",
            repr(error)
        )

        raise

    print(
        "DIFY FILE UPLOAD STATUS:",
        response.status_code
    )

    print(
        "DIFY FILE UPLOAD RESPONSE:"
    )

    print(
        response.text
    )

    if response.status_code != 201:

        raise Exception(
            "Ошибка загрузки файла в Dify: "
            f"{response.status_code} "
            f"{response.text}"
        )

    try:

        data = response.json()

    except Exception:

        raise Exception(
            "Dify вернул некорректный JSON "
            "при загрузке файла."
        )

    upload_file_id = data.get("id")

    if not upload_file_id:

        raise Exception(
            "Dify не вернул ID загруженного файла."
        )

    print(
        "DIFY UPLOAD FILE ID:",
        upload_file_id
    )

    print(
        "======================================"
    )

    return upload_file_id


def send_message_to_dify(
    query,
    file_id=None,
    conversation_id="",
    user="legalai-user"
):
    """
    Отправляет сообщение в Dify Chatflow.

    Если file_id указан, файл передаётся
    в поле files, чтобы Dify запустил
    файловую ветку Chatflow.
    """

    if not DIFY_API_KEY:
        raise Exception(
            "DIFY_API_KEY не найден в .env"
        )

    url = (
        f"{DIFY_API_URL}"
        "/chat-messages"
    )

    headers = {
        "Authorization":
            f"Bearer {DIFY_API_KEY}",
        "Content-Type":
            "application/json"
    }

    files = []

    if file_id:

        files = [
            {
                "type": "document",
                "transfer_method": "local_file",
                "upload_file_id": file_id
            }
        ]

    payload = {
        "inputs": {},
        "query": query or "Проанализируй документ.",
        "response_mode": "blocking",
        "conversation_id": conversation_id,
        "user": user,
        "files": files
    }

    print()
    print("========== DIFY CHAT REQUEST ==========")

    print(
        json.dumps(
            payload,
            ensure_ascii=False,
            indent=2
        )
    )

    print(
        "========================================"
    )

    response = requests.post(
        url,
        headers=headers,
        json=payload,
        timeout=180
    )

    print(
        "DIFY CHAT STATUS:",
        response.status_code
    )

    print(
        "DIFY CHAT RESPONSE:"
    )

    print(
        response.text
    )

    if response.status_code != 200:

        raise Exception(
            "Ошибка Dify Chatflow: "
            f"{response.status_code} "
            f"{response.text}"
        )

    try:

        data = response.json()

    except Exception:

        raise Exception(
            "Dify вернул некорректный JSON."
        )

    answer = data.get(
        "answer",
        ""
    )

    print()
    print("========== DIFY ANSWER ==========")
    print(answer)
    print(
        "================================="
    )

    return parse_ai_response(
        answer
    )


def analyze_document(
    text="",
    file_path=None
):
    """
    Основная функция анализа.

    Если передан file_path:
        1. Загружает настоящий файл в Dify.
        2. Получает ID файла.
        3. Передаёт ID в Chatflow.
        4. Dify самостоятельно извлекает текст
           через Экстрактор документов.
        5. LLM 2 анализирует документ.

    Если файл не передан:
        отправляет обычный вопрос в Chatflow.
    """

    if not DIFY_API_KEY:

        raise Exception(
            "DIFY_API_KEY не найден в .env"
        )

    # =====================================
    # ВАРИАНТ 1 — ЕСТЬ ДОКУМЕНТ
    # =====================================

    if file_path:

        print()
        print(
            "========================================"
        )
        print(
            "НАЧИНАЕМ АНАЛИЗ ДОКУМЕНТА ЧЕРЕЗ DIFY"
        )
        print(
            "========================================"
        )

        # Загружаем настоящий файл в Dify
        file_id = upload_file_to_dify(
            file_path
        )

        # Запрос для Chatflow
        query = (
            "Проанализируй загруженный "
            "юридический документ. "
            "Используй Экстрактор документов "
            "и инструкцию LegalAI."
        )

        # Передаём файл в Chatflow
        return send_message_to_dify(
            query=query,
            file_id=file_id
        )

    # =====================================
    # ВАРИАНТ 2 — ОБЫЧНЫЙ ВОПРОС
    # =====================================

    query = (
        text.strip()
        if text
        else "Ответь на вопрос пользователя."
    )

    print()
    print(
        "========================================"
    )
    print(
        "ОБЫЧНЫЙ ВОПРОС БЕЗ ФАЙЛА"
    )
    print(
        "========================================"
    )

    return send_message_to_dify(
        query=query,
        file_id=None
    )