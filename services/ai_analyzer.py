import re


def analyze_document(text):
    """
    Временный локальный анализатор LegalAI.

    Позже здесь подключим настоящую AI-модель.
    """

    if not text:
        return (
            "Не удалось выполнить анализ.\n\n"
            "В документе не найден извлечённый текст."
        )

    clean_text = re.sub(
        r"\s+",
        " ",
        text
    ).strip()

    words = clean_text.split()

    sentences = re.split(
        r"(?<=[.!?])\s+",
        clean_text
    )

    sentences = [
        sentence.strip()
        for sentence in sentences
        if sentence.strip()
    ]

    summary = clean_text[:1000]

    if len(clean_text) > 1000:
        summary += "..."

    important_keywords = [
        "договор",
        "срок",
        "оплата",
        "штраф",
        "ответственность",
        "обязан",
        "право",
        "расторжение",
        "суд",
        "стороны",
        "клиент"
    ]

    found_keywords = []

    lower_text = clean_text.lower()

    for keyword in important_keywords:

        if keyword in lower_text:
            found_keywords.append(keyword)

    result = []

    result.append("AI-АНАЛИЗ ДОКУМЕНТА")
    result.append("")
    result.append("Краткое содержание:")
    result.append(summary)
    result.append("")

    result.append("Основные показатели:")
    result.append(
        f"• Символов: {len(clean_text)}"
    )
    result.append(
        f"• Слов: {len(words)}"
    )
    result.append(
        f"• Предложений: {len(sentences)}"
    )
    result.append("")

    result.append("Обнаруженные юридические темы:")

    if found_keywords:

        for keyword in found_keywords:
            result.append(
                f"• {keyword.capitalize()}"
            )

    else:

        result.append(
            "• Явные юридические ключевые слова не обнаружены."
        )

    result.append("")
    result.append(
        "Важно: данный результат является "
        "предварительным техническим анализом. "
        "Для юридически значимых выводов необходим "
        "анализ специалистом."
    )

    return "\n".join(result)