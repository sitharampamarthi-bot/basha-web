from flask import (
    Blueprint,
    jsonify,
    redirect,
    render_template,
    request,
    session
)

from google.cloud.firestore_v1 import Query


universal_search_bp = Blueprint(
    "universal_search",
    __name__
)


_db = None
_clean_mobile = None
_get_chat_id = None


def init_universal_search_module(
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


def clean_search_text(value):
    return str(value or "").strip().lower()


def contains_query(value, query):
    return query in clean_search_text(value)


def format_timestamp(timestamp):
    if not timestamp:
        return ""

    try:
        return timestamp.strftime(
            "%d-%m-%Y %I:%M %p"
        )
    except Exception:
        return ""


def timestamp_value(timestamp):
    if not timestamp:
        return 0

    try:
        return timestamp.timestamp()
    except Exception:
        return 0


def normalize_file_type(message):
    file_type = clean_search_text(
        message.get("fileType", "")
    )

    file_url = str(
        message.get("fileUrl", "")
        or ""
    ).strip()

    file_name = clean_search_text(
        message.get("fileName", "")
    )

    check_value = (
        file_name
        or file_url.split("?")[0].lower()
    )

    if file_type:
        return file_type

    if check_value.endswith(
        (
            ".png",
            ".jpg",
            ".jpeg",
            ".gif",
            ".webp"
        )
    ):
        return "image"

    if check_value.endswith(
        (
            ".mp4",
            ".mov",
            ".avi",
            ".mkv",
            ".webm"
        )
    ):
        return "video"

    if check_value.endswith(
        (
            ".mp3",
            ".wav",
            ".m4a",
            ".ogg",
            ".aac"
        )
    ):
        return "audio"

    if file_url:
        return "document"

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
            "contactUserId",
            ""
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

        user = user_doc.to_dict() or {}

        mobile = _clean_mobile(
            user.get("mobile", "")
            or contact_data.get("mobile", "")
        )

        if not mobile:
            continue

        contacts.append({
            "id": contact_user_id,
            "name": (
                contact_data.get("savedName")
                or user.get("name")
                or "User"
            ),
            "mobile": mobile,
            "email": user.get("email", ""),
            "languageName": user.get(
                "languageName",
                "English"
            ),
            "profilePic": user.get(
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

    group_docs = _db.collection(
        "groups"
    ).stream()

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

        group["id"] = group_doc.id
        groups.append(group)

    return groups


def message_matches_query(
    message,
    query
):
    searchable_values = [
        message.get("message", ""),
        message.get("translatedMessage", ""),
        message.get("fileName", ""),
        message.get("senderName", "")
    ]

    return any(
        contains_query(value, query)
        for value in searchable_values
    )


def build_message_result(
    message_id,
    message,
    chat_url,
    chat_name,
    source_type
):
    file_type = normalize_file_type(
        message
    )

    message_text = str(
        message.get("translatedMessage")
        or message.get("message")
        or ""
    ).strip()

    file_name = str(
        message.get("fileName", "")
        or ""
    ).strip()

    if file_type == "image":
        result_type = "image"
        title = file_name or "Shared photo"

    elif file_type == "video":
        result_type = "video"
        title = file_name or "Shared video"

    elif file_type == "audio":
        result_type = "audio"
        title = file_name or "Voice message"

    elif file_type == "document":
        result_type = "document"
        title = file_name or "Shared document"

    else:
        result_type = "message"
        title = (
            message_text[:80]
            if message_text
            else "Message"
        )

    subtitle_parts = [chat_name]

    timestamp_text = format_timestamp(
        message.get("timestamp")
    )

    if timestamp_text:
        subtitle_parts.append(
            timestamp_text
        )

    return {
        "id": message_id,
        "type": result_type,
        "sourceType": source_type,
        "title": title,
        "subtitle": " • ".join(
            subtitle_parts
        ),
        "messageText": message_text,
        "fileUrl": message.get(
            "fileUrl",
            ""
        ),
        "fileName": file_name,
        "chatUrl": chat_url,
        "sortTime": timestamp_value(
            message.get("timestamp")
        )
    }
    
def get_result_category(result_type):
    category_map = {
        "image": "images",
        "video": "videos",
        "audio": "audio",
        "document": "documents",
        "message": "messages"
    }

    return category_map.get(
        str(result_type or "").strip().lower(),
        "messages"
    )    


def perform_search(query):
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

    results = {
        "contacts": [],
        "groups": [],
        "messages": [],
        "images": [],
        "videos": [],
        "audio": [],
        "documents": []
    }

    # CONTACT SEARCH
    for contact in contacts:
        if any(
            contains_query(value, query)
            for value in [
                contact.get("name", ""),
                contact.get("mobile", ""),
                contact.get("email", ""),
                contact.get(
                    "languageName",
                    ""
                )
            ]
        ):
            results["contacts"].append({
                "id": contact["id"],
                "type": "contact",
                "title": contact["name"],
                "subtitle": contact["mobile"],
                "profilePic": contact[
                    "profilePic"
                ],
                "chatUrl": (
                    f"/chat/{contact['mobile']}"
                )
            })

    # GROUP SEARCH
    for group in groups:
        group_name = str(
            group.get("groupName", "")
            or "Group"
        )

        if contains_query(
            group_name,
            query
        ):
            results["groups"].append({
                "id": group["id"],
                "type": "group",
                "title": group_name,
                "subtitle": "Group chat",
                "chatUrl": (
                    f"/group-chat/{group['id']}"
                )
            })

    # INDIVIDUAL CHAT MESSAGE SEARCH
    for contact in contacts:
        chat_id = _get_chat_id(
            current_mobile,
            contact["mobile"]
        )

        message_docs = (
            _db.collection("chats")
            .document(chat_id)
            .collection("messages")
            .order_by(
                "timestamp",
                direction=Query.DESCENDING
            )
            .limit(250)
            .stream()
        )

        for message_doc in message_docs:
            message = (
                message_doc.to_dict()
                or {}
            )

            if not message_matches_query(
                message,
                query
            ):
                continue

            result = build_message_result(
                message_doc.id,
                message,
                f"/chat/{contact['mobile']}",
                contact["name"],
                "individual"
            )

            category = get_result_category(
                result.get("type")
            )

            results[category].append(
                result
            )

    # GROUP MESSAGE SEARCH
    for group in groups:
        group_name = str(
            group.get("groupName", "")
            or "Group"
        )

        message_docs = (
            _db.collection("groups")
            .document(group["id"])
            .collection("messages")
            .order_by(
                "timestamp",
                direction=Query.DESCENDING
            )
            .limit(250)
            .stream()
        )

        for message_doc in message_docs:
            message = (
                message_doc.to_dict()
                or {}
            )

            if not message_matches_query(
                message,
                query
            ):
                continue

            result = build_message_result(
                message_doc.id,
                message,
                f"/group-chat/{group['id']}",
                group_name,
                "group"
            )
            
            print("TYPE =", result.get("type"))
            print("FILE =", message.get("fileName"))

            category = get_result_category(
                result.get("type")
            )
            
            print("CATEGORY =", category)

            results[category].append(
                result
            )

    for category in [
        "messages",
        "images",
        "videos",
        "audio",
        "documents"
    ]:
        results[category].sort(
            key=lambda item: item.get(
                "sortTime",
                0
            ),
            reverse=True
        )

        results[category] = (
            results[category][:50]
        )

    return {
        "query": query,
        "results": results,
        "total": sum(
            len(items)
            for items in results.values()
        )
    }


@universal_search_bp.route(
    "/search"
)
def search_page():
    if "user_id" not in session:
        return redirect("/")

    query = clean_search_text(
        request.args.get("q", "")
    )

    search_data = None

    if query:
        search_data = perform_search(
            query
        )

    return render_template(
        "search/search_results.html",
        query=query,
        search_data=search_data
    )


@universal_search_bp.route("/api/search")
def search_api():
    if "user_id" not in session:
        return jsonify({
            "success": False,
            "error": "Login required"
        }), 401

    query = clean_search_text(
        request.args.get("q", "")
    )

    empty_results = {
        "contacts": [],
        "groups": [],
        "messages": [],
        "images": [],
        "videos": [],
        "audio": [],
        "documents": []
    }

    if len(query) < 2:
        return jsonify({
            "success": True,
            "query": query,
            "total": 0,
            "results": empty_results
        })

    try:
        search_data = perform_search(query)

        if not search_data:
            return jsonify({
                "success": False,
                "error": "User not found"
            }), 404

        return jsonify({
            "success": True,
            **search_data
        })

    except Exception as error:
        print("UNIVERSAL SEARCH API ERROR:", str(error))

        return jsonify({
            "success": False,
            "error": str(error),
            "query": query,
            "total": 0,
            "results": empty_results
        }), 500