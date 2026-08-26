from flask import (
    Blueprint,
    jsonify,
    redirect,
    render_template,
    request,
    session
)
import os
import tempfile

from werkzeug.utils import secure_filename

from quick_file_translator import (
    ALLOWED_EXTENSIONS,
    IMAGE_EXTENSIONS,
    translate_uploaded_file,
    translate_image_spatial,
    translate_live_camera_fast
)


quick_translate_bp = Blueprint(
    "quick_translate",
    __name__
)


_db = None
_translate_text = None


LANGUAGES = [
    {"code": "auto", "name": "Auto Detect"},
    {"code": "en", "name": "English"},
    {"code": "te", "name": "Telugu"},
    {"code": "hi", "name": "Hindi"},
    {"code": "ta", "name": "Tamil"},
    {"code": "kn", "name": "Kannada"},
    {"code": "ml", "name": "Malayalam"},
    {"code": "mr", "name": "Marathi"},
    {"code": "gu", "name": "Gujarati"},
    {"code": "bn", "name": "Bengali"},
    {"code": "pa", "name": "Punjabi"},
    {"code": "ur", "name": "Urdu"},
    {"code": "or", "name": "Odia"},
    {"code": "as", "name": "Assamese"},
    {"code": "ne", "name": "Nepali"},
]


def init_quick_translate_module(
    db,
    translate_text
):
    global _db
    global _translate_text

    _db = db
    _translate_text = translate_text


def clean_text(value):
    return str(value or "").strip()


def clean_lower(value):
    return clean_text(value).lower()


def get_language_by_code(code):
    code = clean_lower(code)

    for language in LANGUAGES:
        if language["code"] == code:
            return language

    return None

def get_uploaded_extension(filename):
    safe_name = secure_filename(
        filename or ""
    )

    return os.path.splitext(
        safe_name
    )[1].lower()


def get_current_user():
    if "user_id" not in session:
        return None

    user_doc = (
        _db.collection("users")
        .document(session["user_id"])
        .get()
    )

    if not user_doc.exists:
        return None

    user = user_doc.to_dict() or {}
    user["id"] = user_doc.id

    return user

def get_user_preferred_language():
    user = get_current_user() or {}

    language_code = clean_lower(
        user.get("languageCode")
        or user.get("preferredLanguageCode")
        or "en"
    )

    language_info = get_language_by_code(
        language_code
    )

    if (
        not language_info
        or language_code == "auto"
    ):
        language_code = "en"

        language_info = get_language_by_code(
            "en"
        )

    return (
        language_code,
        language_info
    )

def translate_value(
    text,
    source_language,
    target_language
):
    text = clean_text(text)

    if not text:
        return ""

    source_language = clean_lower(
        source_language
    )

    target_language = clean_lower(
        target_language
    )

    if not target_language:
        target_language = "en"

    if (
        source_language
        and source_language != "auto"
        and source_language == target_language
    ):
        return text

    return _translate_text(
        text,
        target_language
    )
    
@quick_translate_bp.route(
    "/api/quick-translate/live",
    methods=["POST"]
)
def quick_translate_live_api():

    if "user_id" not in session:
        return jsonify({
            "success": False,
            "error": "Login required"
        }), 401

    try:

        uploaded_file = request.files.get(
            "file"
        )

        if not uploaded_file:
            return jsonify({
                "success": False,
                "error": "Camera frame missing"
            }), 400

        image_bytes = uploaded_file.read()

        if not image_bytes:
            return jsonify({
                "success": False,
                "error": "Empty camera frame"
            }), 400

        # Live Camera always uses
        # logged-in user's preferred language.
        
        target_language_code = clean_lower(
            request.form.get(
                "targetLanguage",
                ""
            )
        )

        target_info = get_language_by_code(
            target_language_code
        )

        if (
            not target_info
            or target_language_code == "auto"
        ):
            (
                target_language_code,
                target_info
            ) = get_user_preferred_language()

        mime_type = (
            uploaded_file.mimetype
            or "image/jpeg"
        )

        result = translate_live_camera_fast(
            image_bytes=image_bytes,
            mime_type=mime_type,
            target_language=target_info["name"]
        )

        detected_language = clean_text(
            result.get("detected_language")
            or "Auto Detected"
        )

        original_text = clean_text(
            result.get("original_text")
        )

        translated_text = clean_text(
            result.get("translated_text")
        )

        return jsonify({
            "success": True,

            "inputType": "image",

            "original":
                original_text,

            "translated":
                translated_text,

            "sourceLanguage":
                "auto",

            "sourceLanguageName":
                detected_language,

            "detectedLanguage":
                detected_language,

            "targetLanguage":
                target_language_code,

            "targetLanguageName":
                target_info["name"],

            "lensMode":
                True,

            "regions":
                result.get(
                    "regions",
                    []
                )
        })

    except ValueError as error:

        # Live camera lo unreadable frame normal.
        # 500 error ga treat cheyyakudadhu.
        return jsonify({
            "success": False,
            "noText": True,
            "error": str(error)
        }), 200

    except Exception as error:

        print(
            "QUICK LIVE TRANSLATE ERROR:",
            str(error)
        )

        return jsonify({
            "success": False,
            "error": str(error)
        }), 500    


@quick_translate_bp.route(
    "/api/quick-translate",
    methods=["POST"]
)
def quick_translate_api():
    if "user_id" not in session:
        return jsonify({
            "success": False,
            "error": "Login required"
        }), 401

    try:
        data = request.get_json(
            silent=True
        ) or {}

        text = clean_text(
            data.get("text")
        )

        source_language = clean_lower(
            data.get("sourceLanguage")
            or data.get("from")
            or "auto"
        )

        target_language = clean_lower(
            data.get("targetLanguage")
            or data.get("to")
            or "en"
        )

        if not text:
            return jsonify({
                "success": False,
                "error": "Please enter text"
            }), 400

        if len(text) > 5000:
            return jsonify({
                "success": False,
                "error": "Text is too long"
            }), 400

        source_info = get_language_by_code(
            source_language
        )

        target_info = get_language_by_code(
            target_language
        )

        if not source_info:
            return jsonify({
                "success": False,
                "error": "Invalid source language"
            }), 400

        if not target_info or target_language == "auto":
            return jsonify({
                "success": False,
                "error": "Invalid target language"
            }), 400

        translated_text = translate_value(
            text,
            source_language,
            target_language
        )

        return jsonify({
            "success": True,
            "original": text,
            "translated": translated_text,
            "sourceLanguage": source_language,
            "sourceLanguageName": source_info["name"],
            "targetLanguage": target_language,
            "targetLanguageName": target_info["name"]
        })

    except Exception as error:
        print(
            "QUICK TRANSLATE API ERROR:",
            str(error)
        )

        return jsonify({
            "success": False,
            "error": str(error)
        }), 500
        
@quick_translate_bp.route(
    "/api/quick-translate/file",
    methods=["POST"]
)
def quick_translate_file_api():
    if "user_id" not in session:
        return jsonify({
            "success": False,
            "error": "Login required"
        }), 401

    temp_path = None

    try:
        uploaded_file = request.files.get(
            "file"
        )

        if not uploaded_file:
            return jsonify({
                "success": False,
                "error": "Please select a file"
            }), 400

        if not uploaded_file.filename:
            return jsonify({
                "success": False,
                "error": "Invalid file name"
            }), 400


        lens_mode = clean_lower(
            request.form.get(
                "lensMode",
                ""
            )
        ) in {
            "1",
            "true",
            "yes",
            "lens"
        }
        
        if lens_mode:

            (
                target_language_code,
                target_info
            ) = get_user_preferred_language()

        else:

            target_language_code = clean_lower(
                request.form.get(
                    "targetLanguage",
                    "en"
                )
            )

            target_info = get_language_by_code(
                target_language_code
            )


        if (
            not target_info
            or target_language_code == "auto"
        ):
            return jsonify({
                "success": False,
                "error": "Invalid target language"
            }), 400


        extension = get_uploaded_extension(
            uploaded_file.filename
        )


        if extension not in ALLOWED_EXTENSIONS:
            return jsonify({
                "success": False,
                "error": (
                    "Supported files: JPG, PNG, WEBP, "
                    "GIF, PDF, DOCX and TXT"
                )
            }), 400


        uploaded_file.stream.seek(
            0,
            os.SEEK_END
        )

        file_size = uploaded_file.stream.tell()

        uploaded_file.stream.seek(
            0
        )


        maximum_size = (
            15 * 1024 * 1024
        )


        if file_size > maximum_size:
            return jsonify({
                "success": False,
                "error": (
                    "File size must be below 15 MB"
                )
            }), 400


        temp_file = tempfile.NamedTemporaryFile(
            delete=False,
            suffix=extension
        )

        temp_path = temp_file.name

        uploaded_file.save(
            temp_path
        )

        temp_file.close()


        if (
            lens_mode
            and extension in IMAGE_EXTENSIONS
        ):

            result = translate_image_spatial(
                file_path=temp_path,
                target_language=
                    target_info["name"]
            )

        else:

            result = translate_uploaded_file(
                file_path=temp_path,
                target_language=
                    target_info["name"]
            )


        detected_language = clean_text(
            result.get(
                "detected_language"
            )
            or "Auto Detected"
        )


        original_text = clean_text(
            result.get(
                "original_text"
            )
        )


        translated_text = clean_text(
            result.get(
                "translated_text"
            )
        )


        return jsonify({
            "success": True,

            "inputType":
                result.get(
                    "input_type",
                    "document"
                ),

            "fileName":
                secure_filename(
                    uploaded_file.filename
                ),

            "original":
                original_text,

            "translated":
                translated_text,

            "sourceLanguage":
                "auto",

            "sourceLanguageName":
                detected_language,

            "detectedLanguage":
                detected_language,

            "targetLanguage":
                target_language_code,

            "targetLanguageName":
                target_info["name"],

            "lensMode":
                lens_mode,

            "regions":
                result.get(
                    "regions",
                    []
                )
        })

    except Exception as error:

        print(
            "QUICK FILE TRANSLATE ERROR:",
            str(error)
        )

        return jsonify({
            "success": False,
            "error": str(error)
        }), 500

    finally:

        if (
            temp_path
            and os.path.exists(
                temp_path
            )
        ):
            try:
                os.remove(
                    temp_path
                )
            except OSError:
                pass


@quick_translate_bp.route(
    "/api/quick-translate/languages"
)
def quick_translate_languages_api():
    if "user_id" not in session:
        return jsonify({
            "success": False,
            "error": "Login required"
        }), 401

    return jsonify({
        "success": True,
        "languages": LANGUAGES
    })
    
def get_quick_translate_contacts():
    current_user = get_current_user()

    if not current_user:
        return []

    current_user_id = current_user["id"]

    contacts = []

    contact_docs = (
        _db.collection("users")
        .document(current_user_id)
        .collection("contacts")
        .stream()
    )

    for contact_doc in contact_docs:
        contact_data = contact_doc.to_dict() or {}

        contact_user_id = clean_text(
            contact_data.get("contactUserId")
        )

        user_data = {}

        if contact_user_id:
            user_doc = (
                _db.collection("users")
                .document(contact_user_id)
                .get()
            )

            if user_doc.exists:
                user_data = user_doc.to_dict() or {}

        mobile = clean_text(
            user_data.get("mobile")
            or contact_data.get("mobile")
            or contact_data.get("phone")
        )

        if not mobile:
            continue

        name = clean_text(
            contact_data.get("savedName")
            or user_data.get("name")
            or contact_data.get("name")
            or "User"
        )

        contacts.append({
            "id": contact_user_id or contact_doc.id,
            "name": name,
            "mobile": mobile,
            "profilePic": clean_text(
                user_data.get("profilePic")
                or contact_data.get("profilePic")
            ),
            "languageName": clean_text(
                user_data.get("languageName")
                or contact_data.get("languageName")
            )
        })

    contacts.sort(
        key=lambda item: item["name"].lower()
    )

    return contacts


@quick_translate_bp.route(
    "/api/quick-translate/contacts"
)
def quick_translate_contacts_api():
    if "user_id" not in session:
        return jsonify({
            "success": False,
            "error": "Login required",
            "items": []
        }), 401

    try:
        contacts = get_quick_translate_contacts()

        return jsonify({
            "success": True,
            "total": len(contacts),
            "items": contacts
        })

    except Exception as error:
        print(
            "QUICK TRANSLATE CONTACTS ERROR:",
            str(error)
        )

        return jsonify({
            "success": False,
            "error": str(error),
            "items": []
        }), 500    


@quick_translate_bp.route(
    "/quick-translate"
)
def quick_translate_page():
    if "user_id" not in session:
        return redirect("/")

    current_user = get_current_user() or {}

    default_target_language = clean_lower(
        current_user.get("languageCode")
        or "en"
    )

    if not get_language_by_code(
        default_target_language
    ):
        default_target_language = "en"

    return render_template(
        "quick_translate/quick_translate.html",
        languages=LANGUAGES,
        default_source_language="auto",
        default_target_language=default_target_language
    )