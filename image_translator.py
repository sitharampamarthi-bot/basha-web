import json
import re

import google.generativeai as genai
from PIL import Image


def clean_json_text(text):
    text = str(text).strip()

    if text.startswith("```"):
        text = text.replace("```json", "")
        text = text.replace("```", "").strip()

    match = re.search(r"\{.*\}", text, re.DOTALL)
    if match:
        text = match.group(0)

    return text


def make_advanced_translated_image(image_path, target_language):
    img = Image.open(image_path)

    model = genai.GenerativeModel("gemini-3.1-flash-lite")

    prompt = f"""
You are an OCR and Translator.

Read EVERY visible text from this image.
Translate all extracted text into {target_language}.

Return ONLY valid JSON object.

Format exactly:
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
- Do not return explanation.
- Keep phone numbers and emails unchanged.
- Keep brand names unchanged if needed.
- Each translated_text item should be a clean readable line.
"""

    response = model.generate_content([prompt, img])

    raw_text = clean_json_text(response.text)

    try:
        data = json.loads(raw_text)
    except Exception:
        data = {
            "title": "Translated Content",
            "translated_text": [str(response.text)]
        }

    if "translated_text" not in data:
        data["translated_text"] = []

    if isinstance(data["translated_text"], str):
        data["translated_text"] = [data["translated_text"]]

    if "title" not in data:
        data["title"] = "Translated Content"

        return data