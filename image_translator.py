import json
import mimetypes
import os
import re
from google import genai
from google.genai import types
from PIL import Image


MODEL_NAME = "gemini-3.1-flash-lite"


def clean_json_text(text):
    text = str(text or "").strip()

    if text.startswith("```"):
        text = text.replace("```json", "")
        text = text.replace("```", "").strip()

    match = re.search(r"\{.*\}", text, re.DOTALL)

    if match:
        text = match.group(0)

    return text


def get_image_mime_type(image_path):
    mime_type, _ = mimetypes.guess_type(image_path)

    if mime_type and mime_type.startswith("image/"):
        return mime_type

    try:
        with Image.open(image_path) as image:
            image_format = str(image.format or "").lower()

        format_map = {
            "jpeg": "image/jpeg",
            "jpg": "image/jpeg",
            "png": "image/png",
            "webp": "image/webp",
            "gif": "image/gif",
        }

        return format_map.get(image_format, "image/jpeg")

    except Exception:
        return "image/jpeg"


def make_advanced_translated_image(image_path, target_language):
    api_key = os.getenv("GEMINI_API_KEY", "").strip()

    if not api_key:
        raise RuntimeError(
            "GEMINI_API_KEY is missing. Add it to the .env file."
        )

    if not os.path.exists(image_path):
        raise FileNotFoundError(
            f"Image file not found: {image_path}"
        )

    client = genai.Client(api_key=api_key)

    mime_type = get_image_mime_type(image_path)

    with open(image_path, "rb") as image_file:
        image_bytes = image_file.read()

    prompt = f"""
You are an OCR and Translator.

Read EVERY visible text from the provided image.
Translate all extracted text into {target_language}.

Return only one valid JSON object in this exact structure:


{{
  "title": "Translated Content",
  "translated_text": [
    "line 1",
    "line 2",
    "line 3"
  ]
}}

Rules:
- Do not return markdown.
- Do not return explanations.
- Do not omit visible text.
- Preserve phone numbers exactly.
- Preserve email addresses exactly.
- Preserve URLs exactly.
- Keep brand names unchanged when translation is inappropriate.
- Return each readable translated sentence or line as a separate list item.
- If no readable text exists, return an empty translated_text list.
"""

    response = client.models.generate_content(
        model=MODEL_NAME,
        contents=[
            prompt,
            types.Part.from_bytes(
                data=image_bytes,
                mime_type=mime_type
            )
        ],
        config=types.GenerateContentConfig(
            temperature=0.1,
            response_mime_type="application/json"
        )
    )

    response_text = response.text or ""

    if not response_text.strip():
        raise RuntimeError(
            "Gemini returned an empty OCR response."
        )

    raw_text = clean_json_text(response_text)

    try:
        data = json.loads(raw_text)

    except json.JSONDecodeError:
        data = {
            "title": "Translated Content",
            "translated_text": [response_text.strip()]
        }

    translated_text = data.get("translated_text", [])

    if isinstance(translated_text, str):
        translated_text = [translated_text]

    if not isinstance(translated_text, list):
        translated_text = []

    cleaned_lines = []

    for line in translated_text:
        line = str(line or "").strip()

        if line:
            cleaned_lines.append(line)

    return {
        "title": str(
            data.get("title") or "Translated Content"
        ).strip(),

        "translated_text": cleaned_lines
    }