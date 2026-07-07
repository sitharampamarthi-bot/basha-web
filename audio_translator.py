import os, uuid, tempfile
from urllib.parse import quote
from flask import request, session, jsonify
import google.generativeai as genai
from gtts import gTTS


AUDIO_ALLOWED = {"webm", "mp3", "wav", "m4a", "ogg"}


def audio_ext(filename):
    return filename.rsplit(".", 1)[1].lower() if "." in filename else ""


def upload_bytes_to_firebase(storage, data, path, content_type):
    bucket = storage.bucket()
    blob = bucket.blob(path)

    token = str(uuid.uuid4())
    blob.metadata = {"firebaseStorageDownloadTokens": token}
    blob.upload_from_string(data, content_type=content_type)

    encoded_path = quote(path, safe="")
    return f"https://firebasestorage.googleapis.com/v0/b/{bucket.name}/o/{encoded_path}?alt=media&token={token}"


def speech_to_text(audio_path):
    uploaded = genai.upload_file(audio_path)

    model = genai.GenerativeModel("gemini-1.5-flash")
    response = model.generate_content([
        uploaded,
        """
        Convert this voice message to text.
        Return only the spoken text.
        Keep punctuation clear.
        """
    ])

    return (response.text or "").strip()


def register_audio_translator_routes(app, db, storage, firestore, clean_mobile, translate_text, save_chat_message):
    
    @app.route("/audio/translate-send", methods=["POST"])
    def audio_translate_send():
        try:
            if "user_id" not in session:
                return jsonify({"success": False, "error": "Login required"}), 401

            receiver_mobile = clean_mobile(request.form.get("receiver_mobile", ""))
            audio = request.files.get("audio")

            if not receiver_mobile:
                return jsonify({"success": False, "error": "Receiver missing"}), 400

            if not audio or audio.filename == "":
                return jsonify({"success": False, "error": "Audio missing"}), 400

            ext = audio_ext(audio.filename)
            if ext not in AUDIO_ALLOWED:
                return jsonify({"success": False, "error": "Invalid audio format"}), 400

            temp_audio = tempfile.NamedTemporaryFile(delete=False, suffix=f".{ext}")
            audio.save(temp_audio.name)
            temp_audio.close()

            # Receiver language
            receiver_docs = db.collection("users").where("mobile", "==", receiver_mobile).limit(1).get()
            receiver_lang = "en"

            if receiver_docs:
                receiver_lang = receiver_docs[0].to_dict().get("languageCode") or "en"

            original_text = speech_to_text(temp_audio.name)

            if not original_text:
                return jsonify({"success": False, "error": "Speech not detected"}), 400

            translated_text = translate_text(original_text, receiver_lang)

            # Text to Speech
            tts = gTTS(text=translated_text, lang=receiver_lang)
            temp_mp3 = tempfile.NamedTemporaryFile(delete=False, suffix=".mp3")
            tts.save(temp_mp3.name)
            temp_mp3.close()

            with open(temp_mp3.name, "rb") as f:
                mp3_bytes = f.read()

            audio_url = upload_bytes_to_firebase(
                storage,
                mp3_bytes,
                f"audio_translations/{session['user_id']}_{uuid.uuid4().hex}.mp3",
                "audio/mpeg"
            )

            save_chat_message(
                session["user_id"],
                receiver_mobile,
                f"🎙 Voice Translation\n\nOriginal:\n{original_text}\n\nTranslated:\n{translated_text}",
                audio_url,
                "basha-translated-audio.mp3",
                "audio"
            )

            try:
                os.remove(temp_audio.name)
                os.remove(temp_mp3.name)
            except:
                pass

            return jsonify({
                "success": True,
                "original_text": original_text,
                "translated_text": translated_text,
                "audio_url": audio_url
            })

        except Exception as e:
            print("AUDIO TRANSLATOR ERROR:", str(e))
            return jsonify({"success": False, "error": str(e)}), 500