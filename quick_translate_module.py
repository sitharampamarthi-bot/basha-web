from flask import (
    Blueprint,
    jsonify,
    redirect,
    render_template,
    request,
    session
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