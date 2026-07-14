import os, uuid, tempfile, json, re
from urllib.parse import quote
from flask import request, session, jsonify
from gtts import gTTS
from google import genai


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


def speech_translate(
    audio_bytes,
    mime_type,
    target_language_name
):
    api_key = os.getenv(
        "GEMINI_API_KEY",
        ""
    ).strip()

    if not api_key:
        raise RuntimeError(
            "GEMINI_API_KEY missing."
        )

    client = genai.Client(
        api_key=api_key
    )

    suffix_map = {
        "audio/webm": ".webm",
        "audio/mpeg": ".mp3",
        "audio/wav": ".wav",
        "audio/mp4": ".m4a",
        "audio/ogg": ".ogg",
        "audio/aac": ".aac",
    }

    suffix = suffix_map.get(
        mime_type,
        ".webm"
    )

    temp_audio_path = None

    try:
        temp_audio = tempfile.NamedTemporaryFile(
            delete=False,
            suffix=suffix
        )

        temp_audio.write(
            audio_bytes
        )

        temp_audio.close()

        temp_audio_path = temp_audio.name

        uploaded_file = client.files.upload(
            file=temp_audio_path,
            config={
                "mime_type": mime_type
            }
        )

        prompt = f"""
You are Basha Messenger Audio Translator.

Detect the spoken language automatically.
Transcribe the voice message accurately.
Translate the transcription into {target_language_name}.

Return only valid JSON with this format:

{{
  "original_text": "exact spoken text",
  "translated_text": "translation in {target_language_name}"
}}

Rules:
- Do not return markdown.
- Do not return explanations.
- Preserve names and numbers correctly.
"""

        response_schema = {
            "type": "object",
            "properties": {
                "original_text": {
                    "type": "string"
                },
                "translated_text": {
                    "type": "string"
                }
            },
            "required": [
                "original_text",
                "translated_text"
            ]
        }

        interaction = client.interactions.create(
            model="gemini-3.1-flash-lite",

            input=[
                {
                    "type": "audio",
                    "uri": uploaded_file.uri,
                    "mime_type": uploaded_file.mime_type
                },
                {
                    "type": "text",
                    "text": prompt
                }
            ],

            response_format=[
                {
                    "type": "text",
                    "mime_type": "application/json",
                    "schema": response_schema
                }
            ],

            store=False
        )

        response_text = str(
            interaction.output_text or ""
        ).strip()

        if not response_text:
            raise RuntimeError(
                "Gemini returned empty audio translation."
            )

        data = clean_json(
            response_text
        )

        original_text = str(
            data.get("original_text", "")
        ).strip()

        translated_text = str(
            data.get("translated_text", "")
        ).strip()

        return (
            original_text,
            translated_text
        )

    finally:
        try:
            if (
                temp_audio_path
                and os.path.exists(temp_audio_path)
            ):
                os.remove(
                    temp_audio_path
                )
        except Exception:
            pass

def register_audio_translator_routes(app, db, storage, firestore, clean_mobile, translate_text, save_chat_message):

    @app.route("/audio/translate-send", methods=["POST"])
    def audio_translate_send():
        
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

            audio_bytes = audio.read()
            mime_type = MIME_MAP.get(ext, "audio/webm")

            original_audio_url = upload_bytes_to_firebase(
                storage,
                audio_bytes,
                f"voice_messages/{session['user_id']}_{uuid.uuid4().hex}.{ext}",
                mime_type
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
                audio_bytes,
                mime_type,
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

            sender_doc = db.collection("users").document(session["user_id"]).get()
            sender = sender_doc.to_dict() if sender_doc.exists else {}

            sender_mobile = clean_mobile(sender.get("mobile", ""))
            sender_lang = sender.get("languageCode") or "en"

            receiver_mobile = clean_mobile(receiver_mobile)

            chat_id = "_".join(sorted([sender_mobile, receiver_mobile]))
            chat_ref = db.collection("chats").document(chat_id)

            chat_ref.set({
                "participants": [sender_mobile, receiver_mobile],
                "lastMessage": "🎙 Voice Message",
                "lastMessageTime": firestore.SERVER_TIMESTAMP
            }, merge=True)

            chat_ref.collection("messages").add({
                "senderMobile": sender_mobile,
                "receiverMobile": receiver_mobile,

                # sender ki original text
                "message": original_text,

                # receiver ki translated text
                "translatedMessage": translated_text,

                "senderLanguage": sender_lang,
                "receiverLanguage": receiver_lang,

                # sender ki original audio
                "originalAudioUrl": original_audio_url,

                # receiver ki translated audio
                "translatedAudioUrl": translated_audio_url,

                "fileUrl": original_audio_url,
                "fileName": f"voice-message.{ext}",
                "fileType": "audio",

                "readBy": [sender_mobile],
                "delivered": False,
                "timestamp": firestore.SERVER_TIMESTAMP
            })

            return jsonify({
                "success": True,
                "audio_url": translated_audio_url,
                "original_audio_url": original_audio_url,
                "original_text": original_text,
                "translated_text": translated_text
            })

        except Exception as e:
            print("AUDIO TRANSLATION ERROR:", repr(e))
            return jsonify({"success": False, "error": str(e)}), 500

        finally:
            try:
                if temp_mp3_path and os.path.exists(temp_mp3_path):
                    os.remove(temp_mp3_path)
            except:
                pass