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


def speech_to_text(audio_path, target_language_name):
    import json, re

    uploaded = genai.upload_file(audio_path)
    
    model = genai.GenerativeModel("gemini-1.5-flash")

    response = model.generate_content([
        uploaded,
        f"""
        You are an audio transcription and translation engine.

        Detect the spoken language automatically.
        Transcribe the audio exactly.
        Translate the transcribed text into this receiver language:
        {target_language_name}

        Return ONLY valid JSON:
        {{
            "original_text": "detected spoken text",
            "translated_text": "text translated into {target_language_name}"
        }}
        """
    ])

    text = (response.text or "").strip()

    if text.startswith("```"):
        text = text.replace("```json", "").replace("```", "").strip()

    match = re.search(r"\{.*\}", text, re.DOTALL)
    if match:
        text = match.group(0)

    data = json.loads(text)
    return data.get("original_text", ""), data.get("translated_text", "")


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

                with open(temp_audio.name, "rb") as f:
                    raw_audio_bytes = f.read()

                # First original audio upload
                original_audio_url = upload_bytes_to_firebase(
                    storage,
                    raw_audio_bytes,
                    f"voice_messages/{session['user_id']}_{uuid.uuid4().hex}.{ext}",
                    audio.content_type or "audio/webm"
                )

                original_text = ""
                translated_text = ""
                final_audio_url = original_audio_url
                final_file_name = f"voice-message.{ext}"

                try:
                    receiver_docs = db.collection("users").where("mobile", "==", receiver_mobile).limit(1).get()

                    receiver_lang = "en"
                    receiver_language_name = "English"

                    if receiver_docs:
                        receiver_data = receiver_docs[0].to_dict()
                        receiver_lang = receiver_data.get("languageCode") or "en"
                        receiver_language_name = receiver_data.get("languageName") or "English"

                    original_text, translated_text = speech_to_text(
                        temp_audio.name,
                        receiver_language_name
                    )

                    if original_text and translated_text:

                        tts = gTTS(text=translated_text, lang=receiver_lang)
                        temp_mp3 = tempfile.NamedTemporaryFile(delete=False, suffix=".mp3")
                        tts.save(temp_mp3.name)
                        temp_mp3.close()

                        with open(temp_mp3.name, "rb") as f:
                            mp3_bytes = f.read()

                        final_audio_url = upload_bytes_to_firebase(
                            storage,
                            mp3_bytes,
                            f"audio_translations/{session['user_id']}_{uuid.uuid4().hex}.mp3",
                            "audio/mpeg"
                        )

                        final_file_name = "basha-translated-audio.mp3"

                        try:
                            os.remove(temp_mp3.name)
                        except:
                            pass

                except Exception as e:
                    print("AUDIO TRANSLATION SKIPPED:", str(e))

                chat_text = "🎙 Voice Message"

                if original_text or translated_text:
                    chat_text = f"🎙 Voice Translation\n\nOriginal:\n{original_text}\n\nTranslated:\n{translated_text}"

                save_chat_message(
                    session["user_id"],
                    receiver_mobile,
                    chat_text,
                    final_audio_url,
                    final_file_name,
                    "audio"
                )

                try:
                    os.remove(temp_audio.name)
                except:
                    pass

                return jsonify({
                    "success": True,
                    "original_text": original_text,
                    "translated_text": translated_text,
                    "audio_url": final_audio_url
                })

            except Exception as e:
                print("AUDIO SEND ERROR:", str(e))
                return jsonify({"success": False, "error": str(e)}), 500