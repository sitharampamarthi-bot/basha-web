import json
import mimetypes
import os
import re
import zipfile
from xml.etree import ElementTree

from google import genai
from google.genai import types


MODEL_NAME = os.getenv(
    "GEMINI_MODEL",
    "gemini-3.1-flash-lite"
).strip()


IMAGE_EXTENSIONS = {
    ".png",
    ".jpg",
    ".jpeg",
    ".webp",
    ".gif"
}

DOCUMENT_EXTENSIONS = {
    ".pdf",
    ".docx",
    ".txt"
}

ALLOWED_EXTENSIONS = (
    IMAGE_EXTENSIONS |
    DOCUMENT_EXTENSIONS
)


def clean_json_text(value):
    text = str(value or "").strip()

    if text.startswith("```"):
        text = text.replace("```json", "")
        text = text.replace("```", "").strip()

    match = re.search(
        r"\{.*\}",
        text,
        re.DOTALL
    )

    if match:
        return match.group(0)

    return text


def get_extension(file_path):
    return os.path.splitext(
        str(file_path or "")
    )[1].lower()


def get_mime_type(file_path):
    extension = get_extension(file_path)

    custom_types = {
        ".png": "image/png",
        ".jpg": "image/jpeg",
        ".jpeg": "image/jpeg",
        ".webp": "image/webp",
        ".gif": "image/gif",
        ".pdf": "application/pdf",
        ".txt": "text/plain",
        ".docx": (
            "application/vnd.openxmlformats-officedocument."
            "wordprocessingml.document"
        )
    }

    if extension in custom_types:
        return custom_types[extension]

    guessed_type, _ = mimetypes.guess_type(
        file_path
    )

    return guessed_type or "application/octet-stream"


def extract_txt_text(file_path):
    with open(
        file_path,
        "rb"
    ) as file_object:
        file_bytes = file_object.read()

    encodings = [
        "utf-8",
        "utf-8-sig",
        "utf-16",
        "latin-1"
    ]

    for encoding in encodings:
        try:
            return file_bytes.decode(
                encoding
            ).strip()
        except UnicodeDecodeError:
            continue

    return file_bytes.decode(
        "utf-8",
        errors="ignore"
    ).strip()


def extract_docx_text(file_path):
    namespace = {
        "w": (
            "http://schemas.openxmlformats.org/"
            "wordprocessingml/2006/main"
        )
    }

    with zipfile.ZipFile(
        file_path
    ) as archive:
        xml_content = archive.read(
            "word/document.xml"
        )

    root = ElementTree.fromstring(
        xml_content
    )

    paragraphs = []

    for paragraph in root.findall(
        ".//w:p",
        namespace
    ):
        pieces = []

        for text_node in paragraph.findall(
            ".//w:t",
            namespace
        ):
            if text_node.text:
                pieces.append(
                    text_node.text
                )

        paragraph_text = "".join(
            pieces
        ).strip()

        if paragraph_text:
            paragraphs.append(
                paragraph_text
            )

    return "\n".join(
        paragraphs
    ).strip()


def build_prompt(target_language):
    return f"""
You are the file OCR, language detection and translation engine
for Basha Messenger.

Read all clearly available text from the supplied input.

The supplied input may be:
- a camera photo
- an uploaded image
- a PDF document
- extracted DOCX text
- extracted TXT text

Tasks:
1. Extract all readable text.
2. Detect the main source language.
3. Translate the extracted text into {target_language}.
4. Preserve the original paragraph and line order.

Return ONLY valid JSON in this exact format:

{{
  "detected_language": "English",
  "original_text": "All extracted original text",
  "translated_text": "All translated text"
}}

Rules:
- Do not include markdown.
- Do not include explanations.
- Preserve phone numbers exactly.
- Preserve email addresses exactly.
- Preserve URLs exactly.
- Preserve dates, prices and reference numbers.
- Keep brand names unchanged when appropriate.
- Do not invent unreadable text.
- If no readable text exists, return empty original_text and translated_text.
""".strip()


def parse_translation_response(
    response_text
):
    cleaned_response = clean_json_text(
        response_text
    )

    try:
        data = json.loads(
            cleaned_response
        )
    except json.JSONDecodeError as error:
        raise RuntimeError(
            "Gemini returned invalid file translation JSON."
        ) from error

    detected_language = str(
        data.get("detected_language")
        or "Auto Detected"
    ).strip()

    original_text = str(
        data.get("original_text")
        or ""
    ).strip()

    translated_text = str(
        data.get("translated_text")
        or ""
    ).strip()

    return {
        "detected_language":
            detected_language,

        "original_text":
            original_text,

        "translated_text":
            translated_text
    }


def translate_uploaded_file(
    file_path,
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

    if not os.path.exists(
        file_path
    ):
        raise FileNotFoundError(
            "Uploaded file was not found."
        )

    extension = get_extension(
        file_path
    )

    if extension not in ALLOWED_EXTENSIONS:
        raise ValueError(
            "Unsupported file type."
        )

    target_language = str(
        target_language or "English"
    ).strip()

    client = genai.Client(
        api_key=api_key
    )

    prompt = build_prompt(
        target_language
    )

    if extension == ".txt":
        original_content = extract_txt_text(
            file_path
        )

        if not original_content:
            raise ValueError(
                "The text file is empty."
            )

        contents = [
            f"{prompt}\n\nSUPPLIED TEXT:\n{original_content}"
        ]

    elif extension == ".docx":
        original_content = extract_docx_text(
            file_path
        )

        if not original_content:
            raise ValueError(
                "No readable text found in the DOCX file."
            )

        contents = [
            f"{prompt}\n\nSUPPLIED TEXT:\n{original_content}"
        ]

    else:
        with open(
            file_path,
            "rb"
        ) as file_object:
            file_bytes = file_object.read()

        contents = [
            prompt,
            types.Part.from_bytes(
                data=file_bytes,
                mime_type=get_mime_type(
                    file_path
                )
            )
        ]

    response = client.models.generate_content(
        model=MODEL_NAME,
        contents=contents,
        config=types.GenerateContentConfig(
            temperature=0.1,
            response_mime_type=(
                "application/json"
            )
        )
    )

    response_text = str(
        response.text or ""
    ).strip()

    if not response_text:
        raise RuntimeError(
            "Gemini returned an empty response."
        )

    result = parse_translation_response(
        response_text
    )

    if not result["original_text"]:
        raise ValueError(
            "No readable text found in the selected file."
        )

    if not result["translated_text"]:
        raise ValueError(
            "Unable to translate the extracted text."
        )

    result["input_type"] = (
        "image"
        if extension in IMAGE_EXTENSIONS
        else "document"
    )

    result["extension"] = extension

    return result