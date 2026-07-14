import base64
import json
import mimetypes
import os
import re

from google import genai
from PIL import Image


MODEL_NAME = "gemini-3.1-flash-lite"


OCR_RESPONSE_SCHEMA = {
    "type": "object",
    "properties": {
        "title": {
            "type": "string"
        },
        "translated_text": {
            "type": "array",
            "items": {
                "type": "string"
            }
        }
    },
    "required": [
        "title",
        "translated_text"
    ]
}


def clean_json_text(text):
    text = str(text or "").strip()

    if text.startswith("```"):
        text = text.replace("```json", "")
        text = text.replace("```", "").strip()

    match = re.search(
        r"\{.*\}",
        text,
        re.DOTALL
    )

    if match:
        text = match.group(0)

    return text


def get_image_mime_type(image_path):
    mime_type, _ = mimetypes.guess_type(
        image_path
    )

    if mime_type and mime_type.startswith("image/"):
        return mime_type

    try:
        with Image.open(image_path) as image:
            image_format = str(
                image.format or ""
            ).lower()

        return {
            "jpeg": "image/jpeg",
            "jpg": "image/jpeg",
            "png": "image/png",
            "webp": "image/webp",
            "gif": "image/gif",
        }.get(
            image_format,
            "image/jpeg"
        )

    except Exception:
        return "image/jpeg"


def make_advanced_translated_image(
    image_path,
    target_language
):
    api_key = os.getenv(
        "GEMINI_API_KEY",
        ""
    ).strip()

    if not api_key:
        raise RuntimeError(
            "GEMINI_API_KEY is missing."
        )

    if not os.path.exists(image_path):
        raise FileNotFoundError(
            f"Image file not found: {image_path}"
        )

    client = genai.Client(
        api_key=api_key
    )

    mime_type = get_image_mime_type(
        image_path
    )

    with open(image_path, "rb") as image_file:
        image_base64 = base64.b64encode(
            image_file.read()
        ).decode("utf-8")

    prompt = f"""
You are the OCR and translation engine for Basha Messenger.

Read every clearly visible text from the supplied image.
Translate all extracted text into {target_language}.

Rules:
- Do not omit readable text.
- Preserve phone numbers exactly.
- Preserve email addresses exactly.
- Preserve URLs exactly.
- Preserve product codes and reference numbers.
- Keep brand names unchanged when translation is inappropriate.
- Return every readable sentence or line separately.
- If no readable text exists, return an empty translated_text list.
"""

    interaction = client.interactions.create(
        model=MODEL_NAME,

        input=[
            {
                "type": "image",
                "mime_type": mime_type,
                "data": image_base64
            },
            {
                "type": "text",
                "text": prompt
            }
        ],

        response_format=[
            {
                "type": "text",
                "mime_type": "application/json",
                "schema": OCR_RESPONSE_SCHEMA
            }
        ],

        store=False
    )

    response_text = str(
        interaction.output_text or ""
    ).strip()

    if not response_text:
        raise RuntimeError(
            "Gemini returned an empty OCR response."
        )

    raw_text = clean_json_text(
        response_text
    )

    try:
        data = json.loads(raw_text)

    except json.JSONDecodeError:
        data = {
            "title": "Translated Content",
            "translated_text": [
                response_text
            ]
        }

    translated_text = data.get(
        "translated_text",
        []
    )

    if isinstance(translated_text, str):
        translated_text = [
            translated_text
        ]

    if not isinstance(translated_text, list):
        translated_text = []

    cleaned_lines = []

    for line in translated_text:
        clean_line = str(
            line or ""
        ).strip()

        if clean_line:
            cleaned_lines.append(
                clean_line
            )

    return {
        "title": str(
            data.get("title")
            or "Translated Content"
        ).strip(),

        "translated_text": cleaned_lines
    }