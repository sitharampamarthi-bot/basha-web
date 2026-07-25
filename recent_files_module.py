from flask import (
    Blueprint,
    jsonify,
    redirect,
    render_template,
    request,
    session
)

from google.cloud.firestore_v1 import Query


recent_files_bp = Blueprint(
    "recent_files",
    __name__
)


_db = None
_clean_mobile = None
_get_chat_id = None


def init_recent_files_module(
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


def clean_text(value):
    return str(value or "").strip()


def clean_lower(value):
    return clean_text(value).lower()


def timestamp_value(timestamp):
    if not timestamp:
        return 0

    try:
        return timestamp.timestamp()
    except Exception:
        return 0


def format_timestamp(timestamp):
    if not timestamp:
        return ""

    try:
        return timestamp.strftime(
            "%d-%m-%Y %I:%M %p"
        )
    except Exception:
        return ""


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


def get_user_contacts(current_user_id):
    contacts = []

    contact_docs = (
        _db.collection("users")
        .document(current_user_id)
        .collection("contacts")
        .stream()
    )

    for contact_doc in contact_docs:
        contact_data = contact_doc.to_dict() or {}

        contact_user_id = contact_data.get(
            "contactUserId"
        )

        if not contact_user_id:
            continue

        user_doc = (
            _db.collection("users")
            .document(contact_user_id)
            .get()
        )

        if not user_doc.exists:
            continue

        user_data = user_doc.to_dict() or {}

        mobile = _clean_mobile(
            user_data.get("mobile", "")
            or contact_data.get("mobile", "")
        )

        if not mobile:
            continue

        contacts.append({
            "id": contact_user_id,
            "name": (
                contact_data.get("savedName")
                or user_data.get("name")
                or "User"
            ),
            "mobile": mobile,
            "profilePic": user_data.get(
                "profilePic",
                ""
            )
        })

    return contacts


def get_user_groups(
    current_user_id,
    current_mobile
):
    groups = []

    group_docs = (
        _db.collection("groups")
        .stream()
    )

    for group_doc in group_docs:
        group = group_doc.to_dict() or {}

        members_raw = group.get(
            "members",
            []
        )

        members_mobile = [
            _clean_mobile(member)
            for member in members_raw
        ]

        created_by = _clean_mobile(
            group.get("createdBy", "")
        )

        is_member = (
            current_mobile in members_mobile
            or current_mobile == created_by
            or current_user_id in members_raw
        )

        if not is_member:
            continue

        groups.append({
            "id": group_doc.id,
            "name": (
                group.get("groupName")
                or "Group"
            )
        })

    return groups


def infer_file_type(message):
    file_type = clean_lower(
        message.get("fileType", "")
    )

    file_name = clean_lower(
        message.get("fileName", "")
    )

    file_url = clean_lower(
        message.get("fileUrl", "")
    )

    original_audio_url = clean_lower(
        message.get("originalAudioUrl", "")
    )

    translated_audio_url = clean_lower(
        message.get("translatedAudioUrl", "")
    )

    check_value = file_name or file_url

    if (
        file_type == "audio"
        or original_audio_url
        or translated_audio_url
    ):
        return "audio"

    if file_type in {
        "image",
        "photo"
    }:
        return "image"

    if file_type == "video":
        return "video"

    if file_type in {
        "document",
        "file"
    }:
        return "document"

    if check_value.endswith((
        ".png",
        ".jpg",
        ".jpeg",
        ".gif",
        ".webp",
        ".bmp"
    )):
        return "image"

    if check_value.endswith((
        ".mp4",
        ".mov",
        ".avi",
        ".mkv",
        ".webm",
        ".m4v"
    )):
        return "video"

    if check_value.endswith((
        ".mp3",
        ".wav",
        ".m4a",
        ".ogg",
        ".aac",
        ".webm"
    )):
        return "audio"

    if (
        message.get("fileUrl")
        or message.get("fileName")
    ):
        return "document"

    return ""


def get_display_file_url(
    message,
    current_mobile
):
    file_type = infer_file_type(
        message
    )

    if file_type != "audio":
        return clean_text(
            message.get("fileUrl", "")
        )

    sender_mobile = _clean_mobile(
        message.get("senderMobile", "")
    )

    if sender_mobile == current_mobile:
        return clean_text(
            message.get("originalAudioUrl")
            or message.get("fileUrl")
            or message.get("translatedAudioUrl")
        )

    return clean_text(
        message.get("translatedAudioUrl")
        or message.get("fileUrl")
        or message.get("originalAudioUrl")
    )


def get_file_title(
    message,
    file_type
):
    file_name = clean_text(
        message.get("fileName", "")
    )

    if file_name:
        return file_name

    if file_type == "image":
        return "Shared photo"

    if file_type == "video":
        return "Shared video"

    if file_type == "audio":
        return "Voice message"

    return "Shared document"


def build_file_item(
    message_id,
    message,
    chat_name,
    chat_url,
    source_type,
    current_mobile
):
    file_type = infer_file_type(
        message
    )

    if not file_type:
        return None

    file_url = get_display_file_url(
        message,
        current_mobile
    )

    if not file_url:
        return None

    timestamp = message.get(
        "timestamp"
    )

    return {
        "id": message_id,
        "type": file_type,
        "title": get_file_title(
            message,
            file_type
        ),
        "fileName": clean_text(
            message.get("fileName", "")
        ),
        "fileUrl": file_url,
        "chatName": chat_name,
        "chatUrl": chat_url,
        "sourceType": source_type,
        "senderMobile": _clean_mobile(
            message.get("senderMobile", "")
        ),
        "timestampText": format_timestamp(
            timestamp
        ),
        "sortTime": timestamp_value(
            timestamp
        )
    }


def collect_recent_files():
    current_user = get_current_user()

    if not current_user:
        return None

    current_user_id = current_user["id"]

    current_mobile = _clean_mobile(
        current_user.get("mobile", "")
        or session.get("mobile", "")
    )

    contacts = get_user_contacts(
        current_user_id
    )

    groups = get_user_groups(
        current_user_id,
        current_mobile
    )

    files = []

    # Individual chats
    for contact in contacts:
        chat_id = _get_chat_id(
            current_mobile,
            contact["mobile"]
        )

        try:
            message_docs = (
                _db.collection("chats")
                .document(chat_id)
                .collection("messages")
                .order_by(
                    "timestamp",
                    direction=Query.DESCENDING
                )
                .limit(300)
                .stream()
            )

            for message_doc in message_docs:
                message = (
                    message_doc.to_dict()
                    or {}
                )

                item = build_file_item(
                    message_doc.id,
                    message,
                    contact["name"],
                    f"/chat/{contact['mobile']}",
                    "individual",
                    current_mobile
                )

                if item:
                    files.append(item)

        except Exception as error:
            print(
                "RECENT INDIVIDUAL FILE ERROR:",
                contact["mobile"],
                str(error)
            )

    # Group chats
    for group in groups:
        try:
            message_docs = (
                _db.collection("groups")
                .document(group["id"])
                .collection("messages")
                .order_by(
                    "timestamp",
                    direction=Query.DESCENDING
                )
                .limit(300)
                .stream()
            )

            for message_doc in message_docs:
                message = (
                    message_doc.to_dict()
                    or {}
                )

                item = build_file_item(
                    message_doc.id,
                    message,
                    group["name"],
                    f"/group-chat/{group['id']}",
                    "group",
                    current_mobile
                )

                if item:
                    files.append(item)

        except Exception as error:
            print(
                "RECENT GROUP FILE ERROR:",
                group["id"],
                str(error)
            )

    files.sort(
        key=lambda item: item.get(
            "sortTime",
            0
        ),
        reverse=True
    )

    return files


def filter_files(
    files,
    file_type
):
    valid_types = {
        "all",
        "image",
        "video",
        "audio",
        "document"
    }

    if file_type not in valid_types:
        file_type = "all"

    if file_type == "all":
        return files

    return [
        item
        for item in files
        if item.get("type") == file_type
    ]


def build_counts(files):
    counts = {
        "all": len(files),
        "images": 0,
        "videos": 0,
        "audio": 0,
        "documents": 0
    }

    for item in files:
        file_type = item.get("type")

        if file_type == "image":
            counts["images"] += 1

        elif file_type == "video":
            counts["videos"] += 1

        elif file_type == "audio":
            counts["audio"] += 1

        elif file_type == "document":
            counts["documents"] += 1

    return counts


@recent_files_bp.route(
    "/recent-files"
)
def recent_files_page():
    if "user_id" not in session:
        return redirect("/")

    file_type = clean_lower(
        request.args.get(
            "type",
            "all"
        )
    )

    files = collect_recent_files() or []

    filtered_files = filter_files(
        files,
        file_type
    )

    return render_template(
        "recent_files/recent_files.html",
        recent_files=filtered_files,
        recent_counts=build_counts(files),
        active_type=file_type
    )


@recent_files_bp.route(
    "/api/recent-files"
)
def recent_files_api():
    if "user_id" not in session:
        return jsonify({
            "success": False,
            "error": "Login required"
        }), 401

    try:
        file_type = clean_lower(
            request.args.get(
                "type",
                "all"
            )
        )

        limit_text = clean_text(
            request.args.get(
                "limit",
                "10"
            )
        )

        try:
            limit_value = int(
                limit_text
            )
        except ValueError:
            limit_value = 10

        limit_value = max(
            1,
            min(limit_value, 100)
        )

        files = collect_recent_files()

        if files is None:
            return jsonify({
                "success": False,
                "error": "User not found"
            }), 404

        filtered_files = filter_files(
            files,
            file_type
        )

        return jsonify({
            "success": True,
            "type": file_type,
            "counts": build_counts(files),
            "total": len(filtered_files),
            "items": filtered_files[
                :limit_value
            ]
        })

    except Exception as error:
        print(
            "RECENT FILES API ERROR:",
            str(error)
        )

        return jsonify({
            "success": False,
            "error": str(error),
            "counts": {
                "all": 0,
                "images": 0,
                "videos": 0,
                "audio": 0,
                "documents": 0
            },
            "total": 0,
            "items": []
        }), 500