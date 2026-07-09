import os, uuid, tempfile, json, re, time
from urllib.parse import quote
from flask import request, session, jsonify
import google.generativeai as genai
from gtts import gTTS

AUDIO_ALLOWED = {"webm", "mp3", "wav", "m4a", "ogg", "aac"}

GTTS_LANG = {
    "te": "te", "hi": "hi", "en": "en", "ta": "ta",
    "kn": "kn", "ml": "ml", "mr": "mr", "gu": "gu",
    "bn": "bn", "pa": "pa", "ur": "ur"
}

MIME_MAP = {
    "webm": "audio/webm",
    "mp3": "audio/mpeg",
    "wav": "audio/wav",
    "m4a": "audio/mp4",
    "ogg": "audio/ogg",
    "aac": "audio/aac"
}


def audio_ext(filename):
    return filename.rsplit(".", 1)[1].lower() if "." in filename else "webm"


def upload_bytes_to_firebase(storage, data, path, content_type):
    bucket = storage.bucket()
    blob = bucket.blob(path)
    
    token = str(uuid.uuid4())
    blob.metadata = {"firebaseStorageDownloadTokens": token}
    blob.upload_from_string(data, content_type=content_type)

    encoded_path = quote(path, safe="")
    return f"https://firebasestorage.googleapis.com/v0/b/{bucket.name}/o/{encoded_path}?alt=media&token={token}"


def clean_json(text):
    text = (text or "").strip()
    if text.startswith("```"):
        text = text.replace("```json", "").replace("```", "").strip()

    match = re.search(r"\{.*\}", text, re.DOTALL)
    if match:
        text = match.group(0)

    return json.loads(text)


def wait_for_file(uploaded_file):
    for _ in range(20):
        f = genai.get_file(uploaded_file.name)
        if getattr(f, "state", None) and f.state.name == "ACTIVE":
            return f
        if getattr(f, "state", None) and f.state.name == "FAILED":
            raise Exception("Gemini file processing failed")
        time.sleep(1)
    raise Exception("Gemini file processing timeout")


def speech_translate(audio_path, ext, target_language_name):
    mime_type = MIME_MAP.get(ext, "audio/webm")

    uploaded = genai.upload_file(
        path=audio_path,
        mime_type=mime_type
    )

    uploaded = wait_for_file(uploaded)

    model = genai.GenerativeModel("gemini-1.5-flash")

    response = model.generate_content([
        uploaded,
        f"""
        
Detect spoken language automatically.
Transcribe the voice message exactly.
Translate it into receiver language: {target_language_name}.

Return ONLY valid JSON:
{{
  "original_text": "spoken text",
  "translated_text": "translated text in {target_language_name}"
}}
"""
    ])

    data = clean_json(response.text)
    return data.get("original_text", "").strip(), data.get("translated_text", "").strip()


def register_audio_translator_routes(app, db, storage, firestore, clean_mobile, translate_text, save_chat_message):

    @app.route("/audio/translate-send", methods=["POST"])
    def audio_translate_send():
        temp_audio_path = None
        temp_mp3_path = None

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
                return jsonify({"success": False, "error": f"Invalid audio format: {ext}"}), 400

            temp_audio = tempfile.NamedTemporaryFile(delete=False, suffix=f".{ext}")
            audio.save(temp_audio.name)
            temp_audio.close()
            temp_audio_path = temp_audio.name

            with open(temp_audio_path, "rb") as f:
                raw_audio = f.read()

            original_audio_url = upload_bytes_to_firebase(
                storage,
                raw_audio,
                f"voice_messages/{session['user_id']}_{uuid.uuid4().hex}.{ext}",
                MIME_MAP.get(ext, "audio/webm")
            )

            receiver_lang = "en"
            receiver_language_name = "English"

            receiver_docs = db.collection("users").where("mobile", "==", receiver_mobile).limit(1).get()
            
            if receiver_docs:
                receiver_data = receiver_docs[0].to_dict()
                receiver_lang = receiver_data.get("languageCode") or "en"
                receiver_language_name = receiver_data.get("languageName") or receiver_lang

            print("AUDIO TARGET:", receiver_mobile, receiver_lang, receiver_language_name)

            original_text, translated_text = speech_translate(
                temp_audio_path,
                ext,
                receiver_language_name
            )

            print("AUDIO ORIGINAL:", original_text)
            print("AUDIO TRANSLATED:", translated_text)

            if not translated_text:
                raise Exception("Translation text empty")

            temp_mp3 = tempfile.NamedTemporaryFile(delete=False, suffix=".mp3")
            temp_mp3.close()
            temp_mp3_path = temp_mp3.name

            tts_lang = GTTS_LANG.get(receiver_lang, "en")
            gTTS(text=translated_text, lang=tts_lang).save(temp_mp3_path)

            with open(temp_mp3_path, "rb") as f:
                mp3_bytes = f.read()

            translated_audio_url = upload_bytes_to_firebase(
                storage,
                mp3_bytes,
                f"audio_translations/{session['user_id']}_{uuid.uuid4().hex}.mp3",
                "audio/mpeg"
            )

            chat_text = (
                "🎙 Voice Translation\n\n"
                f"Original:\n{original_text}\n\n"
                f"Translated:\n{translated_text}"
            )

            save_chat_message(
                session["user_id"],
                receiver_mobile,
                chat_text,
                translated_audio_url,
                "basha-translated-audio.mp3",
                "audio"
            )

            return jsonify({
                "success": True,
                "audio_url": translated_audio_url,
                "original_text": original_text,
                "translated_text": translated_text
            })

        except Exception as e:
            print("AUDIO TRANSLATION ERROR:", repr(e))

            return jsonify({
                "success": False,
                "error": str(e)
            }), 500

        finally:
            for p in [temp_audio_path, temp_mp3_path]:
                try:
                    if p and os.path.exists(p):
                        os.remove(p)
                except:
                    pass