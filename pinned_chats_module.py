from flask import (
    Blueprint,
    jsonify,
    redirect,
    request,
    session
)

from firebase_admin import firestore


pinned_chats_bp = Blueprint(
    "pinned_chats",
    __name__
)


_db = None
_clean_mobile = None
_get_chat_id = None


def init_pinned_chats_module(
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


def get_contact_name(
    current_user_id,
    contact_user_id,
    fallback_name=""
):
    contact_doc = (
        _db.collection("users")
        .document(current_user_id)
        .collection("contacts")
        .document(contact_user_id)
        .get()
    )

    if contact_doc.exists:
        contact_data = contact_doc.to_dict() or {}

        saved_name = clean_text(
            contact_data.get("savedName")
        )

        if saved_name:
            return saved_name

    return clean_text(
        fallback_name
    ) or "User"


def get_individual_chat_data(
    current_user,
    receiver_mobile
):
    current_user_id = current_user["id"]

    current_mobile = _clean_mobile(
        current_user.get("mobile", "")
        or session.get("mobile", "")
    )

    receiver_mobile = _clean_mobile(
        receiver_mobile
    )

    if not receiver_mobile:
        return None

    receiver_docs = (
        _db.collection("users")
        .where("mobile", "==", receiver_mobile)
        .limit(1)
        .get()
    )

    if not receiver_docs:
        return None

    receiver_doc = receiver_docs[0]
    receiver = receiver_doc.to_dict() or {}

    receiver_name = get_contact_name(
        current_user_id,
        receiver_doc.id,
        receiver.get("name", "")
    )

    chat_id = _get_chat_id(
        current_mobile,
        receiver_mobile
    )

    chat_doc = (
        _db.collection("chats")
        .document(chat_id)
        .get()
    )

    chat_data = (
        chat_doc.to_dict()
        if chat_doc.exists
        else {}
    ) or {}

    return {
        "pinId": f"individual_{receiver_mobile}",
        "chatId": chat_id,
        "chatType": "individual",
        "title": receiver_name,
        "mobile": receiver_mobile,
        "groupId": "",
        "profilePic": clean_text(
            receiver.get("profilePic", "")
        ),
        "lastMessage": clean_text(
            chat_data.get("lastMessage", "")
        ),
        "lastMessageTime": chat_data.get(
            "lastMessageTime"
        ),
        "chatUrl": f"/chat/{receiver_mobile}"
    }


def get_group_chat_data(
    current_user,
    group_id
):
    current_user_id = current_user["id"]

    current_mobile = _clean_mobile(
        current_user.get("mobile", "")
        or session.get("mobile", "")
    )

    group_id = clean_text(group_id)

    if not group_id:
        return None

    group_doc = (
        _db.collection("groups")
        .document(group_id)
        .get()
    )

    if not group_doc.exists:
        return None

    group = group_doc.to_dict() or {}

    members_raw = group.get("members", [])

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
        return None

    return {
        "pinId": f"group_{group_id}",
        "chatId": group_id,
        "chatType": "group",
        "title": clean_text(
            group.get("groupName")
        ) or "Group",
        "mobile": "",
        "groupId": group_id,
        "profilePic": clean_text(
            group.get("groupPic", "")
        ),
        "lastMessage": clean_text(
            group.get("lastMessage", "")
        ),
        "lastMessageTime": group.get(
            "lastMessageTime"
        ),
        "chatUrl": f"/group-chat/{group_id}"
    }


def build_pinned_item(
    current_user,
    pin_doc
):
    pin_data = pin_doc.to_dict() or {}

    chat_type = clean_lower(
        pin_data.get("chatType")
    )

    if chat_type == "group":
        chat_data = get_group_chat_data(
            current_user,
            pin_data.get("groupId")
        )
    else:
        chat_data = get_individual_chat_data(
            current_user,
            pin_data.get("mobile")
        )

    if not chat_data:
        return None

    pinned_at = pin_data.get(
        "pinnedAt"
    )

    chat_data.update({
        "pinnedAt": pinned_at,
        "pinnedAtText": format_timestamp(
            pinned_at
        ),
        "sortTime": timestamp_value(
            pinned_at
        )
    })

    return chat_data


def get_pinned_chats(
    limit_value=5
):
    current_user = get_current_user()

    if not current_user:
        return None

    pin_docs = (
        _db.collection("users")
        .document(current_user["id"])
        .collection("pinnedChats")
        .stream()
    )

    items = []

    for pin_doc in pin_docs:
        item = build_pinned_item(
            current_user,
            pin_doc
        )

        if item:
            items.append(item)

    items.sort(
        key=lambda item: item.get(
            "sortTime",
            0
        ),
        reverse=True
    )

    return items[:limit_value]


@pinned_chats_bp.route(
    "/api/pinned-chats"
)
def pinned_chats_api():
    if "user_id" not in session:
        return jsonify({
            "success": False,
            "error": "Login required"
        }), 401

    try:
        limit_text = clean_text(
            request.args.get(
                "limit",
                "5"
            )
        )

        try:
            limit_value = int(
                limit_text
            )
        except ValueError:
            limit_value = 5

        limit_value = max(
            1,
            min(limit_value, 20)
        )

        items = get_pinned_chats(
            limit_value
        )

        if items is None:
            return jsonify({
                "success": False,
                "error": "User not found"
            }), 404

        return jsonify({
            "success": True,
            "total": len(items),
            "items": items
        })

    except Exception as error:
        print(
            "PINNED CHATS API ERROR:",
            str(error)
        )

        return jsonify({
            "success": False,
            "error": str(error),
            "total": 0,
            "items": []
        }), 500


@pinned_chats_bp.route(
    "/api/pin-chat",
    methods=["POST"]
)
def pin_chat_api():
    if "user_id" not in session:
        return jsonify({
            "success": False,
            "error": "Login required"
        }), 401

    try:
        data = request.get_json(
            silent=True
        ) or {}

        chat_type = clean_lower(
            data.get("chatType")
        )

        current_user = get_current_user()

        if not current_user:
            return jsonify({
                "success": False,
                "error": "User not found"
            }), 404

        if chat_type == "group":
            chat_data = get_group_chat_data(
                current_user,
                data.get("groupId")
            )
        else:
            chat_data = get_individual_chat_data(
                current_user,
                data.get("mobile")
            )

        if not chat_data:
            return jsonify({
                "success": False,
                "error": "Chat not found"
            }), 404

        pin_ref = (
            _db.collection("users")
            .document(current_user["id"])
            .collection("pinnedChats")
            .document(chat_data["pinId"])
        )

        pin_ref.set({
            "chatType": chat_data["chatType"],
            "mobile": chat_data["mobile"],
            "groupId": chat_data["groupId"],
            "pinnedAt": firestore.SERVER_TIMESTAMP
        }, merge=True)

        return jsonify({
            "success": True,
            "message": "Chat pinned",
            "pinId": chat_data["pinId"]
        })

    except Exception as error:
        print(
            "PIN CHAT ERROR:",
            str(error)
        )

        return jsonify({
            "success": False,
            "error": str(error)
        }), 500


@pinned_chats_bp.route(
    "/api/unpin-chat",
    methods=["POST"]
)
def unpin_chat_api():
    if "user_id" not in session:
        return jsonify({
            "success": False,
            "error": "Login required"
        }), 401

    try:
        data = request.get_json(
            silent=True
        ) or {}

        chat_type = clean_lower(
            data.get("chatType")
        )

        current_user = get_current_user()

        if not current_user:
            return jsonify({
                "success": False,
                "error": "User not found"
            }), 404

        if chat_type == "group":
            group_id = clean_text(
                data.get("groupId")
            )

            pin_id = f"group_{group_id}"

        else:
            mobile = _clean_mobile(
                data.get("mobile")
            )

            pin_id = f"individual_{mobile}"

        if not pin_id:
            return jsonify({
                "success": False,
                "error": "Invalid chat"
            }), 400

        (
            _db.collection("users")
            .document(current_user["id"])
            .collection("pinnedChats")
            .document(pin_id)
            .delete()
        )

        return jsonify({
            "success": True,
            "message": "Chat unpinned"
        })

    except Exception as error:
        print(
            "UNPIN CHAT ERROR:",
            str(error)
        )

        return jsonify({
            "success": False,
            "error": str(error)
        }), 500


@pinned_chats_bp.route(
    "/pinned-chats"
)
def pinned_chats_page():
    if "user_id" not in session:
        return redirect("/")

    return redirect("/home")