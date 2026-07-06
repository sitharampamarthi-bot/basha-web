import datetime
import uuid, os
from flask import Flask, render_template, request, redirect, session, jsonify, send_file
import firebase_admin
from firebase_admin import credentials, firestore, storage
from werkzeug.utils import secure_filename
from urllib.parse import quote, urljoin
import json
from deep_translator import GoogleTranslator
import requests
import google.generativeai as genai
from PIL import Image, ImageDraw, ImageFont
import textwrap
from dotenv import load_dotenv
from image_translator import make_advanced_translated_image
import tempfile
from io import BytesIO
load_dotenv()

genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

app = Flask(__name__)
app.secret_key = "basha_secret_key"

firebase_json = os.getenv("FIREBASE_SERVICE_ACCOUNT")

if firebase_json:
    cred_dict = json.loads(firebase_json)
    cred = credentials.Certificate(cred_dict)
else:
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    cred = credentials.Certificate(
        os.path.join(BASE_DIR, "serviceAccountKey.json")
    )
    
firebase_admin.initialize_app(cred, {
    "storageBucket": "basha-web.firebasestorage.app"
})

db = firestore.client()

ALLOWED_EXTENSIONS = {
    "png", "jpg", "jpeg", "gif", "webp",
    "pdf", "doc", "docx", "xls", "xlsx",
    "mp4", "mov", "avi", "mkv", "webm"
}

def upload_chat_file_to_firebase(file, sender_uid):
    original_name = secure_filename(file.filename)
    ext = os.path.splitext(original_name)[1].lower()

    unique_name = f"chat_uploads/{sender_uid}_{uuid.uuid4().hex}_{original_name}"

    bucket = storage.bucket()
    blob = bucket.blob(unique_name)

    token = str(uuid.uuid4())

    blob.metadata = {
        "firebaseStorageDownloadTokens": token
    }

    blob.upload_from_file(
        file,
        content_type=file.content_type
    )

    encoded_path = quote(unique_name, safe="")
    file_url = f"https://firebasestorage.googleapis.com/v0/b/{bucket.name}/o/{encoded_path}?alt=media&token={token}"

    if ext in [".png", ".jpg", ".jpeg", ".gif", ".webp"]:
        file_type = "image"
    elif ext in [".mp4", ".mov", ".avi", ".mkv", ".webm"]:
        file_type = "video"
    else:
        file_type = "document"

    return file_url, file_type, original_name

def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS

def clean_mobile(mobile):
    mobile = str(mobile).strip()
    mobile = "".join(ch for ch in mobile if ch.isdigit())

    if mobile.startswith("91") and len(mobile) == 12:
        mobile = mobile[2:]

    return mobile

def translate_text(text, target_lang):
    try:
        return GoogleTranslator(
            source="auto",
            target=target_lang
        ).translate(text)
    except Exception as e:
        print("TRANSLATION ERROR:", e)
        return text
    
def get_best_font(text, size=34):
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    font_dir = os.path.join(BASE_DIR, "static", "fonts")

    fonts = [
        "NotoSansTelugu-Regular.ttf",
        "NotoSansDevanagari-Regular.ttf",
        "NotoSansTamil-Regular.ttf",
        "NotoSansKannada-Regular.ttf",
        "NotoSansMalayalam-Regular.ttf",
        "NotoSansGujarati-Regular.ttf",
        "NotoSansBengali-Regular.ttf",
        "NotoSansGurmukhi-Regular.ttf",
        "NotoSansOriya-Regular.ttf",
        "NotoSansArabic-Regular.ttf",
        "NotoSansSinhala-Regular.ttf",
        "NotoSansMyanmar-Regular.ttf",
        "NotoSansThai-Regular.ttf",
        "NotoSansKhmer-Regular.ttf",
        "NotoSansLao-Regular.ttf",
        "NotoSansHebrew-Regular.ttf",
        "NotoSansSC-Regular.otf",
        "NotoSansJP-Regular.otf",
        "NotoSansKR-Regular.otf",
        "NotoSans-Regular.ttf",
    ]

    for font_name in fonts:
        font_path = os.path.join(font_dir, font_name)
        if os.path.exists(font_path):
            try:
                return ImageFont.truetype(font_path, size)
            except:
                pass

    windows_fonts = [
        r"C:\Windows\Fonts\Nirmala.ttf",
        r"C:\Windows\Fonts\arialuni.ttf",
        r"C:\Windows\Fonts\arial.ttf",
    ]

    for path in windows_fonts:
        if os.path.exists(path):
            return ImageFont.truetype(path, size)

    return ImageFont.load_default()


def wrap_text_by_width(text, font, max_width):
    lines = []

    for paragraph in text.split("\n"):
        words = paragraph.split(" ")

        current = ""

        for word in words:
            test_line = word if current == "" else current + " " + word
            bbox = font.getbbox(test_line)
            width = bbox[2] - bbox[0]

            if width <= max_width:
                current = test_line
            else:
                if current:
                    lines.append(current)
                current = word

        if current:
            lines.append(current)

    return lines    


def get_chat_id(mobile1, mobile2):
    nums = sorted([clean_mobile(mobile1), clean_mobile(mobile2)])
    return nums[0] + "_" + nums[1]

@app.route("/", methods=["GET", "POST"])
def login():
    error = ""

    if request.method == "POST":
        login_id = request.form.get("login_id", "").strip().lower()
        login_mobile = clean_mobile(login_id)
        password = request.form.get("password", "").strip()

        matched_user = None
        matched_doc_id = None

        docs = db.collection("users").stream()

        for doc in docs:
            data = doc.to_dict()

            db_mobile = clean_mobile(data.get("mobile", ""))
            db_phone = clean_mobile(data.get("phone", ""))
            db_email = str(data.get("email", "")).strip().lower()
            db_password = str(data.get("password", "")).strip()

            if login_id == db_email or login_mobile == db_mobile or login_mobile == db_phone:
                matched_user = data
                matched_doc_id = doc.id

                if password == db_password:
                    session["user_id"] = matched_doc_id
                    session["user_name"] = data.get("name", "")
                    session["mobile"] = clean_mobile(data.get("mobile", ""))
                    return redirect("/home")
                else:
                    error = "Password wrong. Please use Forgot Password."
                    break

        if not matched_user:
            error = "Mobile/email not registered"

    return render_template("login.html", error=error)

@app.route("/signup", methods=["GET", "POST"])
def signup():

    error = ""

    if request.method == "POST":

        name = request.form["name"]
        mobile = clean_mobile(request.form.get("mobile", ""))
        email = request.form["email"].strip().lower()
        password = request.form["password"]
        language_code = request.form["language_code"]
        language_name = request.form["language_name"]
        
        user = db.collection("users") \
                 .where("mobile", "==", mobile) \
                 .limit(1) \
                 .get()

        if len(user) > 0:
            error = "Mobile number already registered"

        else:
            db.collection("users").add({
                "name": name,
                "mobile": mobile,
                "email": email,
                "password": password,
                "languageCode": language_code,
                "languageName": language_name
            })

            return redirect("/")

    return render_template(
        "signup.html",
        error=error
    )

@app.route("/forgot-password", methods=["GET", "POST"])
def forgot_password():
    message = ""

    if request.method == "POST":
        mobile = clean_mobile(request.form.get("mobile", ""))
        email = request.form.get("email", "").strip().lower()

        found_id = None

        docs = db.collection("users").stream()

        for doc in docs:
            data = doc.to_dict()

            db_mobile = clean_mobile(data.get("mobile", ""))
            db_phone = clean_mobile(data.get("phone", ""))
            db_email = str(data.get("email", "")).strip().lower()

            if mobile and (db_mobile == mobile or db_phone == mobile):
                found_id = doc.id
                break

            if email and db_email == email:
                found_id = doc.id
                break

        if found_id:
            return redirect(f"/reset-password/{found_id}")
        else:
            message = "Mobile number or email not found"

    return render_template("forgot_password.html", message=message)

@app.route("/reset-password/<user_id>", methods=["GET", "POST"])
def reset_password(user_id):
    message = ""

    if request.method == "POST":
        new_password = request.form.get("new_password", "")
        confirm_password = request.form.get("confirm_password", "")

        if new_password != confirm_password:
            message = "Passwords do not match"
        elif len(new_password) < 4:
            message = "Password must be at least 4 characters"
        else:
            db.collection("users").document(user_id).update({
                "password": new_password
            })
            return redirect("/")

    return render_template("reset_password.html", message=message)    

@app.route("/home")
def home():
    if "user_id" not in session:
        return redirect("/")

    current_user_id = session["user_id"]

    user_doc = db.collection("users").document(current_user_id).get()
    user_data = user_doc.to_dict()

    current_mobile = clean_mobile(user_data.get("mobile", "") or session.get("mobile", ""))
    user_name = user_data.get("name", "User")
    profile_pic = user_data.get("profilePic", "")

    contacts = []
    groups = []
    total_unread = 0
    

    contact_docs = db.collection("users").document(current_user_id)\
        .collection("contacts").stream()

    for c in contact_docs:
        cdata = c.to_dict()
        contact_user_id = cdata.get("contactUserId")

        udoc = db.collection("users").document(contact_user_id).get()

        if udoc.exists:
            u = udoc.to_dict()
            contact_mobile = clean_mobile(u.get("mobile", ""))

            chat_id = get_chat_id(current_mobile, contact_mobile)
            chat_doc = db.collection("chats").document(chat_id).get()

            unread_count = 0
            last_time = None
            last_message = ""

            if chat_doc.exists:
                chat_data = chat_doc.to_dict()
                last_time = chat_data.get("lastMessageTime")
                last_message = chat_data.get("lastMessage", "")

                msg_docs = db.collection("chats").document(chat_id)\
                    .collection("messages")\
                    .where("receiverMobile", "==", current_mobile)\
                    .stream()

                for msg in msg_docs:
                    m = msg.to_dict()
                    read_by = m.get("readBy", [])
                    if current_mobile not in read_by:
                        unread_count += 1

            total_unread += unread_count

            contacts.append({
                "isOnline": u.get("isOnline", False),
                "profilePic": u.get("profilePic", ""),
                "savedName": cdata.get("savedName", u.get("name", "")),
                "mobile": contact_mobile,
                "languageName": u.get("languageName", "English"),
                "unreadCount": unread_count,
                "lastMessage": last_message,
                "lastTime": last_time
            })
            
    def sort_time(contact):
        t = contact.get("lastTime")

        if t is None:
            return 0

        try:
            return t.timestamp()
        except:
            return 0
    groups_dict = {}

    group_docs = db.collection("groups").stream()

    for g in group_docs:
        gdata = g.to_dict()

        members_raw = gdata.get("members", [])
        members_mobile = [clean_mobile(m) for m in members_raw]

        created_by = clean_mobile(gdata.get("createdBy", ""))

        if (
            current_mobile in members_mobile
            or current_mobile == created_by
            or current_user_id in members_raw
        ):
            gdata["id"] = g.id
            groups_dict[g.id] = gdata

    groups = list(groups_dict.values())

    groups.sort(
        key=lambda x: x.get("lastMessageTime").timestamp() if x.get("lastMessageTime") else 0,
        reverse=True
    )
    contacts.sort(
        key=sort_time,
        reverse=True
    )
    print("CURRENT MOBILE:", current_mobile)
    print("GROUPS COUNT:", len(groups))

    return render_template(
        "home.html",
        user_name=user_name,
        profile_pic=profile_pic,
        contacts=contacts,
        groups=groups,
        total_unread=total_unread
        
    )

@app.route("/users")
def users():
    if "user_id" not in session:
        return redirect("/")

    current_user_id = session["user_id"]

    users_list = []

    docs = db.collection("users").stream()

    for doc in docs:
        if doc.id != current_user_id:
            data = doc.to_dict()
            data["id"] = doc.id
            users_list.append(data)

    return render_template(
        "users.html",
        users=users_list
    )

    
@app.route("/chat/<mobile>")
def chat(mobile):
    if "user_id" not in session:
        return redirect("/")

    current_user_id = session["user_id"]

    current_doc = db.collection("users").document(current_user_id).get()
    current_user = current_doc.to_dict()

    current_mobile = clean_mobile(current_user.get("mobile", ""))
    receiver_mobile = clean_mobile(mobile)

    docs = db.collection("users").where("mobile", "==", receiver_mobile).limit(1).get()

    if not docs:
        return redirect("/contacts")

    receiver = docs[0].to_dict()
    receiver["id"] = docs[0].id

    chat_id = get_chat_id(current_mobile, receiver_mobile)

    messages = []

    msg_docs = db.collection("chats").document(chat_id)\
        .collection("messages")\
        .order_by("timestamp")\
        .stream()

    for m in msg_docs:

        data = m.to_dict()

        # message current user ki vachindi ante read mark cheyyi
        if data.get("receiverMobile") == current_mobile:
            
            m.reference.update({
                "delivered": True,
                "readBy": firestore.ArrayUnion([current_mobile])
            })
            data["delivered"] = True
            read_by = data.get("readBy", [])
            if current_mobile not in read_by:
                read_by.append(current_mobile)
            data["readBy"] = read_by

        messages.append(data)

    return render_template(
        "chat.html",
        receiver=receiver,
        messages=messages,
        current_mobile=current_mobile,
        back_url=request.args.get("from", "/home")
    )
    
def save_chat_message(sender_id, receiver_mobile, message, file_url="", file_name="", file_type=""):
    sender_doc = db.collection("users").document(sender_id).get()
    sender = sender_doc.to_dict()

    sender_mobile = clean_mobile(sender.get("mobile", ""))
    receiver_mobile = clean_mobile(receiver_mobile)

    receiver_docs = db.collection("users") \
        .where("mobile", "==", receiver_mobile) \
        .limit(1) \
        .get()

    receiver_language = "en"

    if receiver_docs:
        receiver_data = receiver_docs[0].to_dict()
        receiver_language = receiver_data.get("languageCode") or "en"

    translated_message = translate_text(message, receiver_language) if message else ""

    chat_id = get_chat_id(sender_mobile, receiver_mobile)
    chat_ref = db.collection("chats").document(chat_id)

    chat_ref.set({
        "participants": [sender_mobile, receiver_mobile],
        "lastMessage": translated_message if translated_message else (
            "📷 Photo" if file_type == "image" else
            "🎥 Video" if file_type == "video" else
            "📄 Document"
        ),
        "lastMessageTime": firestore.SERVER_TIMESTAMP
    }, merge=True)

    chat_ref.collection("messages").add({
        "senderMobile": sender_mobile,
        "receiverMobile": receiver_mobile,
        "message": message,
        "translatedMessage": translated_message,
        "receiverLanguage": receiver_language,
        "readBy": [sender_mobile],
        "delivered": False,
        "fileUrl": file_url,
        "fileName": file_name,
        "fileType": file_type,
        "timestamp": firestore.SERVER_TIMESTAMP
    })

    return chat_id    
    
@app.route("/send-message", methods=["POST"])
def send_message():
    try:
        if "user_id" not in session:
            return jsonify({"success": False, "error": "Login required"}), 401

        receiver_mobile = request.form.get("receiver_mobile", "").strip()
        message = request.form.get("message", "").strip()
        files = request.files.getlist("chat_files")

        sent_any = False

        if message:
            save_chat_message(
                session["user_id"],
                receiver_mobile,
                message,
                "",
                "",
                ""
            )
            sent_any = True

        for file in files:
            if file and file.filename and allowed_file(file.filename):

                file_url, file_type, original_name = upload_chat_file_to_firebase(
                    file,
                    session["user_id"]
                )

                save_chat_message(
                    session["user_id"],
                    receiver_mobile,
                    "",
                    file_url,
                    original_name,
                    file_type
                )

                sent_any = True

        if not sent_any:
            return jsonify({"success": False, "error": "Empty message"}), 400

        return jsonify({"success": True})

    except Exception as e:
        print("SEND MESSAGE ERROR:", str(e))
        return jsonify({"success": False, "error": str(e)}), 500

@app.route("/send-message-ajax", methods=["POST"])
def send_message_ajax():
    if "user_id" not in session:
        return jsonify({"success": False})

    data = request.get_json()
    receiver_mobile = data.get("receiver_mobile", "")
    message = data.get("message", "").strip()

    if not message:
        return jsonify({"success": False})

    save_chat_message(session["user_id"], receiver_mobile, message)

    return jsonify({"success": True})

@app.route("/get-messages/<receiver_mobile>")
def get_messages(receiver_mobile):
    if "user_id" not in session:
        return ""

    current_user_id = session["user_id"]

    current_doc = db.collection("users").document(current_user_id).get()
    current_user = current_doc.to_dict()

    current_mobile = clean_mobile(current_user.get("mobile", ""))
    receiver_mobile = clean_mobile(receiver_mobile)

    chat_id = get_chat_id(current_mobile, receiver_mobile)

    msg_docs = db.collection("chats").document(chat_id) \
        .collection("messages") \
        .order_by("timestamp") \
        .stream()

    messages = []

    for m in msg_docs:
        data = m.to_dict()

        if data.get("receiverMobile") == current_mobile:
            read_by = data.get("readBy", [])
            already_read = current_mobile in read_by
            already_delivered = data.get("delivered", False)

            if not already_read or not already_delivered:
                m.reference.update({
                    "delivered": True,
                    "readBy": firestore.ArrayUnion([current_mobile])
                })

            data["delivered"] = True
            if current_mobile not in read_by:
                read_by.append(current_mobile)
            data["readBy"] = read_by            
        messages.append(data)

    return render_template(
        "message_bubbles.html",
        messages=messages,
        current_mobile=current_mobile
    )
    
@app.route("/update-presence", methods=["POST"])
def update_presence():
    if "user_id" not in session:
        return jsonify({"success": False})

    current_user_id = session["user_id"]

    db.collection("users").document(current_user_id).update({
        "isOnline": True,
        "lastSeen": firestore.SERVER_TIMESTAMP
    })

    return jsonify({"success": True})


@app.route("/set-typing", methods=["POST"])
def set_typing():
    if "user_id" not in session:
        return jsonify({"success": False})

    data = request.get_json()
    receiver_mobile = clean_mobile(data.get("receiver_mobile", ""))
    is_typing = data.get("is_typing", False)

    current_mobile = clean_mobile(session.get("mobile", ""))
    chat_id = get_chat_id(current_mobile, receiver_mobile)

    db.collection("chats").document(chat_id).set({
        f"typing_{current_mobile}": is_typing
    }, merge=True)

    return jsonify({"success": True})


@app.route("/chat-status/<receiver_mobile>")
def chat_status(receiver_mobile):
    if "user_id" not in session:
        return jsonify({"success": False})

    current_mobile = clean_mobile(session.get("mobile", ""))
    receiver_mobile = clean_mobile(receiver_mobile)

    chat_id = get_chat_id(current_mobile, receiver_mobile)

    receiver_docs = db.collection("users").where("mobile", "==", receiver_mobile).limit(1).get()

    is_online = False
    last_seen = ""

    if receiver_docs:
        receiver = receiver_docs[0].to_dict()
        is_online = receiver.get("isOnline", False)
        last_seen = str(receiver.get("lastSeen", ""))

    chat_doc = db.collection("chats").document(chat_id).get()
    is_typing = False

    if chat_doc.exists:
        chat_data = chat_doc.to_dict()
        is_typing = chat_data.get(f"typing_{receiver_mobile}", False)

    return jsonify({
        "success": True,
        "isOnline": is_online,
        "lastSeen": last_seen,
        "isTyping": is_typing
    })    
    
@app.route("/groups")
def groups():
    if "user_id" not in session:
        return redirect("/")

    current_mobile = clean_mobile(session.get("mobile", ""))

    groups = []

    docs = db.collection("groups").stream()

    for doc in docs:
        data = doc.to_dict()

        members = [clean_mobile(m) for m in data.get("members", [])]

        if current_mobile in members:
            data["id"] = doc.id
            groups.append(data)

    return render_template("groups.html", groups=groups)           
    
@app.route("/check-phone-contact", methods=["POST"])
def check_phone_contact():
    if "user_id" not in session:
        return jsonify({"success": False, "message": "Not logged in"})

    data = request.get_json()
    name = data.get("name", "")
    mobile = data.get("mobile", "")

    mobile = mobile.replace(" ", "").replace("+91", "").replace("-", "")

    current_user_id = session["user_id"]

    docs = db.collection("users").where("mobile", "==", mobile).limit(1).get()

    if not docs:
        return jsonify({
            "success": False,
            "registered": False,
            "message": "Not registered",
            "mobile": mobile,
            "name": name
        })

    found_doc = docs[0]
    found_id = found_doc.id
    found_user = found_doc.to_dict()

    if found_id == current_user_id:
        return jsonify({
            "success": False,
            "registered": True,
            "message": "This is your own number"
        })

    db.collection("users").document(current_user_id)\
        .collection("contacts").document(found_id).set({
            "contactUserId": found_id,
            "savedName": name or found_user.get("name", ""),
            "mobile": mobile,
            "registered": True,
            "createdAt": firestore.SERVER_TIMESTAMP
        })

    return jsonify({
        "success": True,
        "registered": True,
        "message": "Contact added",
        "mobile": mobile,
        "name": name
    })
    
@app.route("/settings", methods=["GET", "POST"])
def settings():
    if "user_id" not in session:
        return redirect("/")

    current_user_id = session["user_id"]
    message = ""

    user_ref = db.collection("users").document(current_user_id)
    user_doc = user_ref.get()

    if not user_doc.exists:
        return redirect("/")

    user = user_doc.to_dict()

    if request.method == "POST":
        action = request.form.get("action", "")

        if action == "profile":
            name = request.form.get("name", "").strip()
            email = request.form.get("email", "").strip().lower()
            mobile = clean_mobile(request.form.get("mobile", ""))

            profile_pic = user.get("profilePic", "")

            file = request.files.get("profile_image")

            if file and file.filename:

                upload_folder = os.path.join(
                    os.path.dirname(os.path.abspath(__file__)),
                    "static",
                    "profile_pics"
                )

                os.makedirs(upload_folder, exist_ok=True)

                filename = secure_filename(
                    f"{current_user_id}_{file.filename}"
                )

                save_path = os.path.join(
                    upload_folder,
                    filename
                )

                file.save(save_path)
                

                profile_pic = f"/static/profile_pics/{filename}"

            user_ref.update({
                "name": name,
                "email": email,
                "mobile": mobile,
                "profilePic": profile_pic
            })

            session["user_name"] = name
            message = "Profile updated successfully"

        elif action == "password":
            old_password = request.form.get("old_password", "").strip()
            new_password = request.form.get("new_password", "").strip()
            confirm_password = request.form.get("confirm_password", "").strip()

            db_password = str(user.get("password", "")).strip()

            if old_password != db_password:
                message = "Old password is wrong"
            elif new_password != confirm_password:
                message = "New passwords do not match"
            elif len(new_password) < 4:
                message = "Password must be at least 4 characters"
            else:
                user_ref.update({
                    "password": new_password
                })
                message = "Password changed successfully"

        elif action == "language":
            language_code = request.form.get("language_code", "en")
            language_name = request.form.get("language_name", "English")

            user_ref.update({
                "languageCode": language_code,
                "languageName": language_name
            })

            message = "Language updated successfully"

        user_doc = user_ref.get()
        user = user_doc.to_dict()

    return render_template(
        "settings.html",
        user=user,
        message=message
    )            
    
@app.route("/contacts", methods=["GET", "POST"])
def contacts():
    if "user_id" not in session:
        return redirect("/")

    current_user_id = session["user_id"]
    message = ""
    contacts_list = []

    if request.method == "POST":
        saved_name = request.form.get("saved_name", "").strip()
        mobile = request.form.get("mobile", "").strip()

        found_user = None
        found_id = None

        docs = db.collection("users").where("mobile", "==", mobile).limit(1).get()

        if docs:
            found_id = docs[0].id
            found_user = docs[0].to_dict()

            if found_id == current_user_id:
                message = "You cannot add yourself"
            else:
                db.collection("users").document(current_user_id)\
                    .collection("contacts").document(found_id).set({
                        "contactUserId": found_id,
                        "savedName": saved_name or found_user.get("name", ""),
                        "mobile": mobile,
                        "registered": True,
                        "createdAt": firestore.SERVER_TIMESTAMP
                    })
                message = "Contact added successfully"
        else:
            message = "This mobile number is not registered. Send invite link."

    contact_docs = db.collection("users").document(current_user_id)\
        .collection("contacts").stream()

    for c in contact_docs:
        cdata = c.to_dict()
        contact_user_id = cdata.get("contactUserId")

        user_doc = db.collection("users").document(contact_user_id).get()

        if user_doc.exists:
            u = user_doc.to_dict()
            u["id"] = contact_user_id
            u["savedName"] = cdata.get("savedName", u.get("name", ""))
            contacts_list.append(u)

    return render_template(
        "contacts.html",
        contacts=contacts_list,
        message=message
    )
    
@app.route("/create-group", methods=["GET", "POST"])
def create_group():
    if "user_id" not in session:
        return redirect("/")

    current_mobile = clean_mobile(session.get("mobile", ""))

    contacts = []
    contact_docs = db.collection("users").document(session["user_id"]).collection("contacts").stream()

    for c in contact_docs:
        cdata = c.to_dict()
        user_doc = db.collection("users").document(cdata.get("contactUserId")).get()
        if user_doc.exists:
            u = user_doc.to_dict()
            u["mobile"] = clean_mobile(u.get("mobile", ""))
            u["savedName"] = cdata.get("savedName", u.get("name", ""))
            contacts.append(u)

    if request.method == "POST":
        group_name = request.form.get("group_name", "").strip()
        members = request.form.getlist("members")

        if current_mobile not in members:
            members.append(current_mobile)
            
        existing_groups = db.collection("groups") \
            .where("createdBy", "==", current_mobile) \
            .where("groupName", "==", group_name) \
            .limit(1) \
            .get()

        if len(existing_groups) > 0:
            return redirect("/home")                            

        db.collection("groups").add({
            "groupName": group_name,
            "createdBy": current_mobile,
            "members": members,
            "createdAt": firestore.SERVER_TIMESTAMP,
            "lastMessage": "",
            "lastMessageTime": firestore.SERVER_TIMESTAMP
        })

        return redirect("/home")

    return render_template("create_group.html", contacts=contacts)


@app.route("/group-chat/<group_id>")
def group_chat(group_id):
    if "user_id" not in session:
        return redirect("/")

    current_mobile = clean_mobile(session.get("mobile", ""))

    group_doc = db.collection("groups").document(group_id).get()
    if not group_doc.exists:
        return redirect("/home")

    group = group_doc.to_dict()
    group["id"] = group_id

    messages = []
    msg_docs = db.collection("groups").document(group_id).collection("messages").order_by("timestamp").stream()

    for m in msg_docs:
        messages.append(m.to_dict())

    return render_template(
        "group_chat.html",
        group=group,
        messages=messages,
        current_mobile=current_mobile
    )


@app.route("/send-group-message", methods=["POST"])
def send_group_message():

    if "user_id" not in session:
        return jsonify({"success": False})

    group_id = request.form.get("group_id")
    message = request.form.get("message", "").strip()

    files = request.files.getlist("chat_files")

    sender_mobile = clean_mobile(session.get("mobile", ""))
    sender_name = session.get("user_name", "")

    group_ref = db.collection("groups").document(group_id)

    sent_any = False

    # text message
    if message:

        group_ref.collection("messages").add({

            "senderMobile": sender_mobile,
            "senderName": sender_name,
            "message": message,

            "fileUrl": "",
            "fileName": "",
            "fileType": "",

            "timestamp": firestore.SERVER_TIMESTAMP

        })

        sent_any = True

    # multiple files
    for file in files:

        if not file:
            continue

        if file.filename == "":
            continue

        if not allowed_file(file.filename):
            continue

        file_url, file_type, file_name = upload_chat_file_to_firebase(
            file,
            session["user_id"]
        )

        group_ref.collection("messages").add({

            "senderMobile": sender_mobile,
            "senderName": sender_name,

            "message": "",

            "fileUrl": file_url,
            "fileName": file_name,
            "fileType": file_type,

            "timestamp": firestore.SERVER_TIMESTAMP

        })

        sent_any = True

    if not sent_any:
        return jsonify({
            "success": False,
            "error": "Empty message"
        })

    group_ref.update({

        "lastMessage":
            message if message else
            f"📎 {len(files)} file(s)",

        "lastMessageTime":
            firestore.SERVER_TIMESTAMP

    })

    return jsonify({
        "success": True
    })
        
@app.route("/convert-image-text", methods=["POST"])
def convert_image_text():
    try:
        if "user_id" not in session:
            return jsonify({"error": "Login required"}), 401

        data = request.get_json(silent=True) or {}
        image_url = data.get("image_url", "")
        if image_url.startswith("/"):
            image_url = urljoin(request.host_url, image_url)

        if not image_url:
            return jsonify({"error": "Image not found"}), 400

        user_doc = db.collection("users").document(session["user_id"]).get()
        user = user_doc.to_dict() if user_doc.exists else {}
        target_language = user.get("languageName", "English")

        response = requests.get(image_url, timeout=20)

        if response.status_code != 200:
            return jsonify({"error": "Unable to download image"}), 400

        temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".jpg")
        temp_file.write(response.content)
        temp_file.close()

        image_path = temp_file.name

        result = make_advanced_translated_image(
            image_path=image_path,
            target_language=target_language
        )
        if not result:
            return jsonify({"error": "Image translation failed. Please try again"}), 500

        lines = result.get("translated_text", [])
        if isinstance(lines, str):
            lines = [lines]

        img = Image.open(image_path).convert("RGB")
        w, h = img.size

        font = get_best_font("\n".join(lines), 34)
        title_font = get_best_font(target_language, 38)

        padding = 30
        wrapped_lines = []

        for line in lines:
            wrapped_lines.extend(wrap_text_by_width(line, font, w - 60))

        # Original image ni save chestham.
        output_path = tempfile.NamedTemporaryFile(delete=False, suffix=".jpg").name
        img.save(output_path, "JPEG", quality=95)

        bucket = storage.bucket()
        firebase_path = f"translated_images/{session['user_id']}_{uuid.uuid4().hex}.jpg"
        blob = bucket.blob(firebase_path)

        token = str(uuid.uuid4())
        blob.metadata = {"firebaseStorageDownloadTokens": token}
        blob.upload_from_filename(output_path, content_type="image/jpeg")

        encoded_path = quote(firebase_path, safe="")
        translated_image_url = f"https://firebasestorage.googleapis.com/v0/b/{bucket.name}/o/{encoded_path}?alt=media&token={token}"

        try:
            os.remove(image_path)
            os.remove(output_path)
        except:
            pass

        return jsonify({
            "success": True,
            "translated_image_url": translated_image_url,
            "translated_text": wrapped_lines,
            "language": target_language,
            "title": result.get("title", "")
        })

    except Exception as e:
        print("CONVERT IMAGE ERROR:", str(e))
        return jsonify({"error": str(e)}), 500
    
@app.route("/download-image")
def download_image():
    try:
        image_url = request.args.get("url", "")

        if not image_url:
            return "Image URL missing", 400

        response = requests.get(image_url, timeout=30)

        if response.status_code != 200:
            return "Unable to download image", 400

        return send_file(
            BytesIO(response.content),
            mimetype="image/jpeg",
            as_attachment=True,
            download_name="basha-image.jpg"
        )     

    except Exception as e:
        return str(e), 500 
    
               
@app.route("/download-file")
def download_file():
    try:
        from urllib.parse import unquote
        from flask import send_file
        import mimetypes

        url = request.args.get("url", "")
        if url.startswith("/"):
            url = urljoin(request.host_url, url)

        name = request.args.get("name", "basha-file")

        if not url:
            return "No URL", 400

        r = requests.get(url, timeout=30)

        if r.status_code != 200:
            return "Unable to download file", 400

        filename = secure_filename(unquote(name)) or "basha-file"

        content_type = (
            r.headers.get("Content-Type")
            or mimetypes.guess_type(filename)[0]
            or "application/octet-stream"
        )

        ext = os.path.splitext(filename)[1].lower()

        if not ext:
            if "jpeg" in content_type or "jpg" in content_type:
                filename += ".jpg"
            elif "png" in content_type:
                filename += ".png"
            elif "gif" in content_type:
                filename += ".gif"
            elif "webp" in content_type:
                filename += ".webp"
            elif "pdf" in content_type:
                filename += ".pdf"
            elif "mp4" in content_type:
                filename += ".mp4"

        return send_file(
            BytesIO(r.content),
            mimetype=content_type,
            as_attachment=True,
            download_name=filename
        )

    except Exception as e:
        return str(e), 500
            
if __name__ == "__main__":
    app.run(debug=True)