from datetime import datetime

from flask import (
    Blueprint,
    jsonify,
    redirect,
    render_template,
    request,
    session
)


media_gallery_bp = Blueprint(
    "media_gallery",
    __name__
)


_db = None
_clean_mobile = None
_get_chat_id = None


def init_media_gallery_module(
    db,
    clean_mobile,
    get_chat_id
):
    global _db
    global _clean_mobile
    global _get_chat_id

    _db = db
    _clean_mobile = clean_mobile
    _get_chat_id = get_chat_id


def normalize_file_type(message):
    file_type = str(
        message.get("fileType", "")
        or ""
    ).strip().lower()

    file_url = str(
        message.get("fileUrl", "")
        or ""
    ).strip()

    file_name = str(
        message.get("fileName", "")
        or ""
    ).strip()

    check_value = (
        file_name or file_url.split("?")[0]
    ).lower()

    if file_type in {
        "image",
        "video",
        "document"
    }:
        return file_type

    image_extensions = (
        ".png",
        ".jpg",
        ".jpeg",
        ".gif",
        ".webp"
    )

    video_extensions = (
        ".mp4",
        ".mov",
        ".avi",
        ".mkv",
        ".webm"
    )

    if check_value.endswith(image_extensions):
        return "image"

    if check_value.endswith(video_extensions):
        return "video"

    if file_url:
        return "document"

    return ""


def format_timestamp(timestamp):
    if not timestamp:
        return ""

    try:
        return timestamp.strftime(
            "%d-%m-%Y %I:%M %p"
        )
    except Exception:
        return str(timestamp)


def timestamp_sort_value(timestamp):
    if not timestamp:
        return 0

    try:
        return timestamp.timestamp()
    except Exception:
        return 0


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


def get_receiver(receiver_mobile):
    receiver_mobile = _clean_mobile(
        receiver_mobile
    )

    docs = (
        _db.collection("users")
        .where(
            "mobile",
            "==",
            receiver_mobile
        )
        .limit(1)
        .get()
    )

    if not docs:
        return None

    receiver = docs[0].to_dict() or {}
    receiver["id"] = docs[0].id
    receiver["mobile"] = receiver_mobile

    return receiver


def load_chat_media(
    current_mobile,
    receiver_mobile
):
    chat_id = _get_chat_id(
        current_mobile,
        receiver_mobile
    )

    media_items = []

    message_docs = (
        _db.collection("chats")
        .document(chat_id)
        .collection("messages")
        .order_by(
            "timestamp",
            direction="DESCENDING"
        )
        .stream()
    )

    for message_doc in message_docs:
        message = message_doc.to_dict() or {}

        file_url = str(
            message.get("fileUrl", "")
            or ""
        ).strip()

        if not file_url:
            continue

        file_type = normalize_file_type(
            message
        )

        if file_type not in {
            "image",
            "video",
            "document"
        }:
            continue

        timestamp = message.get("timestamp")

        media_items.append({
            "id": message_doc.id,
            "fileUrl": file_url,
            "fileName": (
                message.get("fileName")
                or (
                    "Photo"
                    if file_type == "image"
                    else "Video"
                    if file_type == "video"
                    else "Document"
                )
            ),
            "fileType": file_type,
            "senderMobile": _clean_mobile(
                message.get(
                    "senderMobile",
                    ""
                )
            ),
            "receiverMobile": _clean_mobile(
                message.get(
                    "receiverMobile",
                    ""
                )
            ),
            "timestamp": timestamp,
            "formattedTime": format_timestamp(
                timestamp
            ),
            "sortTime": timestamp_sort_value(
                timestamp
            )
        })

    return media_items


@media_gallery_bp.route(
    "/chat-media/<receiver_mobile>"
)
def chat_media(receiver_mobile):
    current_user = get_current_user()

    if not current_user:
        return redirect("/")

    current_mobile = _clean_mobile(
        current_user.get("mobile", "")
        or session.get("mobile", "")
    )

    receiver_mobile = _clean_mobile(
        receiver_mobile
    )

    receiver = get_receiver(
        receiver_mobile
    )

    if not receiver:
        return redirect("/home")

    media_items = load_chat_media(
        current_mobile,
        receiver_mobile
    )

    images = [
        item
        for item in media_items
        if item["fileType"] == "image"
    ]

    videos = [
        item
        for item in media_items
        if item["fileType"] == "video"
    ]

    documents = [
        item
        for item in media_items
        if item["fileType"] == "document"
    ]

    return render_template(
        "media_gallery/chat_media.html",

        receiver=receiver,
        current_mobile=current_mobile,

        images=images,
        videos=videos,
        documents=documents,

        image_count=len(images),
        video_count=len(videos),
        document_count=len(documents),

        back_url=(
            f"/chat/{receiver_mobile}"
        )
    )


@media_gallery_bp.route(
    "/api/chat-media/<receiver_mobile>"
)
def chat_media_api(receiver_mobile):
    current_user = get_current_user()

    if not current_user:
        return jsonify({
            "success": False,
            "error": "Login required"
        }), 401

    current_mobile = _clean_mobile(
        current_user.get("mobile", "")
        or session.get("mobile", "")
    )

    receiver_mobile = _clean_mobile(
        receiver_mobile
    )

    receiver = get_receiver(
        receiver_mobile
    )

    if not receiver:
        return jsonify({
            "success": False,
            "error": "User not found"
        }), 404

    media_items = load_chat_media(
        current_mobile,
        receiver_mobile
    )

    return jsonify({
        "success": True,
        "items": media_items
    })