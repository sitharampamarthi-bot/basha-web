import os
import uuid
from urllib.parse import quote

from flask import Blueprint, render_template, request, redirect, session, flash
from firebase_admin import firestore, storage
from werkzeug.utils import secure_filename


settings_bp = Blueprint("settings_bp", __name__)

ALLOWED_PROFILE_EXTENSIONS = {"png", "jpg", "jpeg", "webp"}
MAX_PROFILE_IMAGE_BYTES = 5 * 1024 * 1024

LANGUAGES = [
    ("en", "English"),
    ("te", "Telugu"),
    ("hi", "Hindi"),
    ("ta", "Tamil"),
    ("kn", "Kannada"),
    ("ml", "Malayalam"),
    ("mr", "Marathi"),
    ("gu", "Gujarati"),
    ("bn", "Bengali"),
    ("pa", "Punjabi"),
    ("or", "Odia"),
    ("as", "Assamese"),
    ("ur", "Urdu"),
    ("sa", "Sanskrit"),
    ("kok", "Konkani"),
    ("mai", "Maithili"),
    ("ne", "Nepali"),
    ("sd", "Sindhi"),
    ("mni", "Manipuri"),
    ("doi", "Dogri"),
    ("ks", "Kashmiri"),
    ("bo", "Bodo"),
    ("sat", "Santali"),
    ("si", "Sinhala"),
    ("my", "Burmese"),
    ("th", "Thai"),
    ("ar", "Arabic"),
    ("fr", "French"),
    ("es", "Spanish"),
    ("de", "German"),
    ("zh-CN", "Chinese"),
    ("ja", "Japanese"),
    ("ko", "Korean"),
    ("it", "Italian"),
    ("dv", "Dhivehi"),
    ("dz", "Dzongkha"),
    ("ps", "Pashto"),
    ("fa", "Persian"),
    ("vi", "Vietnamese"),
    ("id", "Indonesian"),
    ("ms", "Malay"),
    ("tl", "Filipino"),
    ("km", "Khmer"),
    ("lo", "Lao"),
    ("he", "Hebrew"),
    ("tr", "Turkish"),
]

DEFAULT_SETTINGS = {
    "privacy": {
        "lastSeen": "everyone",
        "profilePhoto": "everyone",
        "readReceipts": True,
        "onlineStatus": True,
    },
    "chats": {
        "theme": "system",
        "fontSize": "medium",
        "enterToSend": False,
        "autoTranslate": True,
        "showOriginalText": True,
        "wallpaper": "default",
    },
    "notifications": {
        "enabled": True,
        "messagePreview": True,
        "sound": True,
        "vibration": True,
        "groupNotifications": True,
    },
    "storage": {
        "photoQuality": "standard",
        "autoDownloadPhotos": True,
        "autoDownloadVideos": False,
        "autoDownloadDocuments": False,
        "dataSaver": False,
    },
}


def init_settings_module(db, clean_mobile):
    settings_bp.db = db
    settings_bp.clean_mobile = clean_mobile


def get_current_user():
    if "user_id" not in session:
        return None, None

    user_ref = settings_bp.db.collection("users").document(
        session["user_id"]
    )

    user_doc = user_ref.get()

    if not user_doc.exists:
        return None, None

    user = user_doc.to_dict() or {}
    user["id"] = user_doc.id

    return user_ref, user


def merged_settings(user):
    saved = user.get("settings", {}) or {}
    result = {}

    for section, defaults in DEFAULT_SETTINGS.items():
        section_saved = saved.get(section, {}) or {}

        result[section] = {
            **defaults,
            **section_saved
        }

    return result


def upload_profile_image(file, user_id):
    if not file or not file.filename:
        return None

    original_name = secure_filename(file.filename)

    extension = (
        original_name.rsplit(".", 1)[-1].lower()
        if "." in original_name
        else ""
    )

    if extension not in ALLOWED_PROFILE_EXTENSIONS:
        raise ValueError(
            "Only PNG, JPG, JPEG or WEBP profile images are allowed."
        )

    file.stream.seek(0, os.SEEK_END)
    size = file.stream.tell()
    file.stream.seek(0)

    if size > MAX_PROFILE_IMAGE_BYTES:
        raise ValueError(
            "Profile image must be below 5 MB."
        )

    bucket = storage.bucket()

    firebase_path = (
        f"profile_pics/{user_id}/"
        f"{uuid.uuid4().hex}.{extension}"
    )

    blob = bucket.blob(firebase_path)

    token = str(uuid.uuid4())

    blob.metadata = {
        "firebaseStorageDownloadTokens": token
    }

    blob.upload_from_file(
        file,
        content_type=file.content_type
    )

    encoded_path = quote(
        firebase_path,
        safe=""
    )

    return (
        f"https://firebasestorage.googleapis.com/v0/b/"
        f"{bucket.name}/o/{encoded_path}"
        f"?alt=media&token={token}"
    )


@settings_bp.route("/settings")
def settings_home():
    user_ref, user = get_current_user()

    if not user:
        return redirect("/")

    return render_template(
        "settings/settings_home.html",
        user=user,
        settings_data=merged_settings(user)
    )


@settings_bp.route(
    "/settings/profile",
    methods=["GET", "POST"]
)
def settings_profile():
    user_ref, user = get_current_user()

    if not user:
        return redirect("/")

    if request.method == "POST":
        name = request.form.get(
            "name",
            ""
        ).strip()

        email = request.form.get(
            "email",
            ""
        ).strip().lower()

        mobile = settings_bp.clean_mobile(
            request.form.get("mobile", "")
        )

        if not name:
            flash(
                "Full name is required.",
                "danger"
            )

            return redirect(
                "/settings/profile"
            )

        if len(mobile) != 10:
            flash(
                "Enter a valid 10-digit mobile number.",
                "danger"
            )

            return redirect(
                "/settings/profile"
            )

        duplicate_users = (
            settings_bp.db.collection("users")
            .where("mobile", "==", mobile)
            .limit(2)
            .get()
        )

        for doc in duplicate_users:
            if doc.id != session["user_id"]:
                flash(
                    "This mobile number is already registered.",
                    "danger"
                )

                return redirect(
                    "/settings/profile"
                )

        profile_pic = user.get(
            "profilePic",
            ""
        )

        profile_image = request.files.get(
            "profile_image"
        )

        try:
            uploaded_url = upload_profile_image(
                profile_image,
                session["user_id"]
            )

            if uploaded_url:
                profile_pic = uploaded_url

        except ValueError as exc:
            flash(
                str(exc),
                "danger"
            )

            return redirect(
                "/settings/profile"
            )

        except Exception as exc:
            print(
                "PROFILE IMAGE UPLOAD ERROR:",
                exc
            )

            flash(
                "Unable to upload profile picture.",
                "danger"
            )

            return redirect(
                "/settings/profile"
            )

        user_ref.update({
            "name": name,
            "email": email,
            "mobile": mobile,
            "profilePic": profile_pic,
            "updatedAt": firestore.SERVER_TIMESTAMP
        })

        session["user_name"] = name
        session["mobile"] = mobile

        flash(
            "Profile updated successfully.",
            "success"
        )

        return redirect(
            "/settings/profile"
        )

    return render_template(
        "settings/settings_profile.html",
        user=user
    )


@settings_bp.route(
    "/settings/language",
    methods=["GET", "POST"]
)
def settings_language():
    user_ref, user = get_current_user()

    if not user:
        return redirect("/")

    if request.method == "POST":
        language_code = request.form.get(
            "language_code",
            "en"
        ).strip()

        language_map = dict(LANGUAGES)

        if language_code not in language_map:
            flash(
                "Please select a valid language.",
                "danger"
            )

            return redirect(
                "/settings/language"
            )

        user_ref.update({
            "languageCode": language_code,
            "languageName": language_map[language_code],
            "updatedAt": firestore.SERVER_TIMESTAMP
        })

        flash(
            "Language updated successfully.",
            "success"
        )

        return redirect(
            "/settings/language"
        )

    return render_template(
        "settings/settings_language.html",
        user=user,
        languages=LANGUAGES
    )


@settings_bp.route(
    "/settings/password",
    methods=["GET", "POST"]
)
def settings_password():
    user_ref, user = get_current_user()

    if not user:
        return redirect("/")

    if request.method == "POST":
        old_password = request.form.get(
            "old_password",
            ""
        ).strip()

        new_password = request.form.get(
            "new_password",
            ""
        ).strip()

        confirm_password = request.form.get(
            "confirm_password",
            ""
        ).strip()

        db_password = str(
            user.get("password", "")
        ).strip()

        if old_password != db_password:
            flash(
                "Old password is wrong.",
                "danger"
            )

        elif len(new_password) < 6:
            flash(
                "New password must be at least 6 characters.",
                "danger"
            )

        elif new_password != confirm_password:
            flash(
                "New passwords do not match.",
                "danger"
            )

        elif new_password == old_password:
            flash(
                "New password must be different from old password.",
                "danger"
            )

        else:
            user_ref.update({
                "password": new_password,
                "passwordChangedAt":
                    firestore.SERVER_TIMESTAMP,
                "updatedAt":
                    firestore.SERVER_TIMESTAMP
            })

            flash(
                "Password changed successfully.",
                "success"
            )

            return redirect(
                "/settings/password"
            )

    return render_template(
        "settings/settings_password.html",
        user=user
    )


@settings_bp.route(
    "/settings/privacy",
    methods=["GET", "POST"]
)
def settings_privacy():
    user_ref, user = get_current_user()

    if not user:
        return redirect("/")

    privacy = merged_settings(
        user
    )["privacy"]

    if request.method == "POST":
        privacy = {
            "lastSeen":
                request.form.get(
                    "last_seen",
                    "everyone"
                ),

            "profilePhoto":
                request.form.get(
                    "profile_photo",
                    "everyone"
                ),

            "readReceipts":
                request.form.get(
                    "read_receipts"
                ) == "on",

            "onlineStatus":
                request.form.get(
                    "online_status"
                ) == "on"
        }

        user_ref.set({
            "settings": {
                "privacy": privacy
            },
            "updatedAt":
                firestore.SERVER_TIMESTAMP
        }, merge=True)

        flash(
            "Privacy settings saved.",
            "success"
        )

        return redirect(
            "/settings/privacy"
        )

    return render_template(
        "settings/settings_privacy.html",
        user=user,
        privacy=privacy
    )


@settings_bp.route(
    "/settings/chats",
    methods=["GET", "POST"]
)
def settings_chats():
    user_ref, user = get_current_user()

    if not user:
        return redirect("/")

    chats = merged_settings(
        user
    )["chats"]

    if request.method == "POST":
        chats = {
            "theme":
                request.form.get(
                    "theme",
                    "system"
                ),

            "fontSize":
                request.form.get(
                    "font_size",
                    "medium"
                ),

            "enterToSend":
                request.form.get(
                    "enter_to_send"
                ) == "on",

            "autoTranslate":
                request.form.get(
                    "auto_translate"
                ) == "on",

            "showOriginalText":
                request.form.get(
                    "show_original_text"
                ) == "on",

            "wallpaper":
                request.form.get(
                    "wallpaper",
                    "default"
                )
        }

        user_ref.set({
            "settings": {
                "chats": chats
            },
            "updatedAt":
                firestore.SERVER_TIMESTAMP
        }, merge=True)

        flash(
            "Chat settings saved.",
            "success"
        )

        return redirect(
            "/settings/chats"
        )

    return render_template(
        "settings/settings_chats.html",
        user=user,
        chats=chats
    )


@settings_bp.route(
    "/settings/notifications",
    methods=["GET", "POST"]
)
def settings_notifications():
    user_ref, user = get_current_user()

    if not user:
        return redirect("/")

    notifications = merged_settings(
        user
    )["notifications"]

    if request.method == "POST":
        notifications = {
            "enabled":
                request.form.get(
                    "notifications"
                ) == "on",

            "messagePreview":
                request.form.get(
                    "message_preview"
                ) == "on",

            "sound":
                request.form.get(
                    "sound"
                ) == "on",

            "vibration":
                request.form.get(
                    "vibration"
                ) == "on",

            "groupNotifications":
                request.form.get(
                    "group_notifications"
                ) == "on"
        }

        user_ref.set({
            "settings": {
                "notifications": notifications
            },
            "updatedAt":
                firestore.SERVER_TIMESTAMP
        }, merge=True)

        flash(
            "Notification settings saved.",
            "success"
        )

        return redirect(
            "/settings/notifications"
        )

    return render_template(
        "settings/settings_notifications.html",
        user=user,
        notifications=notifications
    )


@settings_bp.route(
    "/settings/storage",
    methods=["GET", "POST"]
)
def settings_storage():
    user_ref, user = get_current_user()

    if not user:
        return redirect("/")

    storage_settings = merged_settings(
        user
    )["storage"]

    if request.method == "POST":
        storage_settings = {
            "photoQuality":
                request.form.get(
                    "photo_quality",
                    "standard"
                ),

            "autoDownloadPhotos":
                request.form.get(
                    "auto_download_photos"
                ) == "on",

            "autoDownloadVideos":
                request.form.get(
                    "auto_download_videos"
                ) == "on",

            "autoDownloadDocuments":
                request.form.get(
                    "auto_download_documents"
                ) == "on",

            "dataSaver":
                request.form.get(
                    "data_saver"
                ) == "on"
        }

        user_ref.set({
            "settings": {
                "storage": storage_settings
            },
            "updatedAt":
                firestore.SERVER_TIMESTAMP
        }, merge=True)

        flash(
            "Storage and data settings saved.",
            "success"
        )

        return redirect(
            "/settings/storage"
        )

    return render_template(
        "settings/settings_storage.html",
        user=user,
        storage_settings=storage_settings
    )


@settings_bp.route("/settings/help")
def settings_help():
    user_ref, user = get_current_user()

    if not user:
        return redirect("/")

    return render_template(
        "settings/settings_help.html",
        user=user
    )


@settings_bp.route("/logout")
def settings_logout():
    session.clear()
    return redirect("/")