from flask import Flask, jsonify, render_template, request, redirect, session
import firebase_admin
from firebase_admin import credentials, firestore
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

app = Flask(__name__)
app.secret_key = "basha_secret_key"

cred = credentials.Certificate(
    os.path.join(BASE_DIR, "serviceAccountKey.json")
)

firebase_admin.initialize_app(cred)

db = firestore.client()

def clean_mobile(mobile):
    mobile = str(mobile).strip()
    mobile = mobile.replace(" ", "").replace("-", "")
    mobile = mobile.replace("+91", "")
    if mobile.startswith("91") and len(mobile) == 12:
        mobile = mobile[2:]
    return mobile


def get_chat_id(mobile1, mobile2):
    nums = sorted([clean_mobile(mobile1), clean_mobile(mobile2)])
    return nums[0] + "_" + nums[1]

@app.route("/", methods=["GET", "POST"])
def login():
    error = ""

    if request.method == "POST":
        login_id = request.form.get("login_id", "").strip().lower()
        password = request.form.get("password", "").strip()

        docs = db.collection("users").stream()

        for doc in docs:
            data = doc.to_dict()

            db_mobile = str(data.get("mobile", "")).strip().lower()
            db_phone = str(data.get("phone", "")).strip().lower()
            db_email = str(data.get("email", "")).strip().lower()
            db_password = str(data.get("password", "")).strip()

            if (login_id == db_mobile or login_id == db_phone or login_id == db_email) and password == db_password:
                session["user_id"] = doc.id
                session["user_name"] = data.get("name", "")
                return redirect("/home")

        error = "Invalid mobile/email or password"

    return render_template("login.html", error=error)

@app.route("/signup", methods=["GET", "POST"])
def signup():

    error = ""

    if request.method == "POST":

        name = request.form["name"]
        mobile = request.form["mobile"]
        email = request.form["email"]
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
        mobile = request.form.get("mobile", "").strip()
        email = request.form.get("email", "").strip().lower()

        found_id = None

        docs = db.collection("users").stream()

        for doc in docs:
            data = doc.to_dict()

            db_mobile = str(data.get("mobile", "")).strip()
            db_phone = str(data.get("phone", "")).strip()
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
    return render_template("home.html")

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
        messages.append(data)

    return render_template(
        "chat.html",
        receiver=receiver,
        messages=messages,
        current_mobile=current_mobile
    )
    
@app.route("/send-message", methods=["POST"])
def send_message():
    if "user_id" not in session:
        return redirect("/")

    sender_id = session["user_id"]
    receiver_mobile = request.form.get("receiver_mobile", "").strip()
    message = request.form.get("message", "").strip()

    if not message:
        return redirect(f"/chat/{receiver_mobile}")

    sender_doc = db.collection("users").document(sender_id).get()
    sender = sender_doc.to_dict()

    sender_mobile = clean_mobile(sender.get("mobile", ""))
    receiver_mobile = clean_mobile(receiver_mobile)

    chat_id = get_chat_id(sender_mobile, receiver_mobile)

    chat_ref = db.collection("chats").document(chat_id)

    chat_ref.set({
        "participants": [sender_mobile, receiver_mobile],
        "lastMessage": message,
        "lastMessageTime": firestore.SERVER_TIMESTAMP
    }, merge=True)

    chat_ref.collection("messages").add({
        "senderMobile": sender_mobile,
        "receiverMobile": receiver_mobile,
        "message": message,
        "timestamp": firestore.SERVER_TIMESTAMP
    })

    return redirect(f"/chat/{receiver_mobile}")    
    
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
            "createdAt": firestore.SERVER_TIMESTAMP
        })

    return jsonify({
        "success": True,
        "registered": True,
        "message": "Contact added",
        "mobile": mobile,
        "name": name
    })        
    
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

if __name__ == "__main__":
    app.run(debug=True)