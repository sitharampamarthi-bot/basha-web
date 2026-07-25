from flask import Blueprint

unread_bp = Blueprint(
    "unread",
    __name__
)

_db = None
_clean_mobile = None
_get_chat_id = None


def init_unread_module(
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