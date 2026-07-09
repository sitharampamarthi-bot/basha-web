import os, uuid, tempfile, json, re
from urllib.parse import quote
from flask import request, session, jsonify
import google.generativeai as genai
from gtts import gTTS

AUDIO_ALLOWED = {"webm", "mp3", "wav", "m4a", "ogg", "aac"}


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


def speech_translate(audio_path, target_language_name):
    uploaded = genai.upload_file(audio_path)

    model = genai.GenerativeModel("gemini-1.5-flash")

    response = model.generate_content([
        uploaded,
        f"""
You are Basha Messenger Audio Translator.

Detect spoken language automatically.
Transcribe the voice message.
Translate the transcription into receiver language: {target_language_name}.

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
                raw_audio_bytes = f.read()

            original_audio_url = upload_bytes_to_firebase(
                storage,
                raw_audio_bytes,
                f"voice_messages/{session['user_id']}_{uuid.uuid4().hex}.{ext}",
                audio.content_type or "audio/webm"
            )

            receiver_lang = "en"
            receiver_language_name = "English"

            receiver_docs = db.collection("users").where("mobile", "==", receiver_mobile).limit(1).get()

            if receiver_docs:
                receiver_data = receiver_docs[0].to_dict()
                receiver_lang = receiver_data.get("languageCode") or "en"
                receiver_language_name = receiver_data.get("languageName") or receiver_lang

            print("AUDIO TARGET:", receiver_mobile, receiver_lang, receiver_language_name)

            original_text = ""
            translated_text = ""
            translated_audio_url = ""

            try:
                original_text, translated_text = speech_translate(
                    temp_audio_path,
                    receiver_language_name
                )

                print("AUDIO ORIGINAL:", original_text)
                print("AUDIO TRANSLATED:", translated_text)

                if translated_text:
                    temp_mp3 = tempfile.NamedTemporaryFile(delete=False, suffix=".mp3")
                    temp_mp3.close()
                    temp_mp3_path = temp_mp3.name

                    tts = gTTS(text=translated_text, lang=receiver_lang)
                    tts.save(temp_mp3_path)

                    with open(temp_mp3_path, "rb") as f:
                        mp3_bytes = f.read()

                    translated_audio_url = upload_bytes_to_firebase(
                        storage,
                        mp3_bytes,
                        f"audio_translations/{session['user_id']}_{uuid.uuid4().hex}.mp3",
                        "audio/mpeg"
                    )

            except Exception as e:
                print("AUDIO TRANSLATION FAILED:", repr(e))

            # If translation success, send translated audio.
            # If translation fail, send original audio.
            final_audio_url = translated_audio_url or original_audio_url
            final_file_name = "basha-translated-audio.mp3" if translated_audio_url else f"voice-message.{ext}"

            chat_text = "🎙 Voice Message"

            if original_text or translated_text:
                chat_text = (
                    "🎙 Voice Translation\n\n"
                    f"Original:\n{original_text}\n\n"
                    f"Translated:\n{translated_text or 'Translation failed'}"
                )

            save_chat_message(
                session["user_id"],
                receiver_mobile,
                chat_text,
                final_audio_url,
                final_file_name,
                "audio"
            )

            return jsonify({
                "success": True,
                "original_text": original_text,
                "translated_text": translated_text,
                "original_audio_url": original_audio_url,
                "translated_audio_url": translated_audio_url,
                "audio_url": final_audio_url,
                "translation_success": bool(translated_audio_url)
            })

        except Exception as e:
            print("AUDIO SEND ERROR:", repr(e))
            return jsonify({"success": False, "error": str(e)}), 500

        finally:
            for p in [temp_audio_path, temp_mp3_path]:
                try:
                    if p and os.path.exists(p):
                        os.remove(p)
                except:
                    pass