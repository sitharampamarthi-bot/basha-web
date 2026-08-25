import base64
import json
import os
import re
import tempfile
import uuid

from difflib import SequenceMatcher

try:
    from google.cloud import texttospeech
except ImportError:
    texttospeech = None

from urllib.parse import quote

from flask import jsonify, request, session

from gtts import gTTS

from google import genai
from google.genai import types


AUDIO_ALLOWED = {
    "webm",
    "mp3",
    "wav",
    "m4a",
    "ogg",
    "aac"
}


MIME_MAP = {
    "webm": "audio/webm",
    "mp3": "audio/mpeg",
    "wav": "audio/wav",
    "m4a": "audio/mp4",
    "ogg": "audio/ogg",
    "aac": "audio/aac"
}


LANGUAGE_NAMES = {
    "en": "English",
    "te": "Telugu",
    "hi": "Hindi",
    "ta": "Tamil",
    "kn": "Kannada",
    "ml": "Malayalam",
    "mr": "Marathi",
    "gu": "Gujarati",
    "bn": "Bengali",
    "pa": "Punjabi",
    "ur": "Urdu",
    "or": "Odia",
    "as": "Assamese",
    "ne": "Nepali"
}


GTTS_LANG = {
    "en": "en",
    "te": "te",
    "hi": "hi",
    "ta": "ta",
    "kn": "kn",
    "ml": "ml",
    "mr": "mr",
    "gu": "gu",
    "bn": "bn",
    "pa": "pa",
    "ur": "ur",
    "or": "or",
    "ne": "ne"
}


AUDIO_MODEL_NAME = os.getenv(
    "AUDIO_GEMINI_MODEL",
    "gemini-2.5-flash"
).strip()


MAX_AUDIO_SIZE = 15 * 1024 * 1024


def clean_text(value):
    return str(value or "").strip()


def audio_ext(filename):
    filename = clean_text(filename)

    if "." not in filename:
        return "webm"

    return filename.rsplit(
        ".",
        1
    )[1].lower()


def get_audio_mime_type(
    extension,
    browser_mime_type=""
):
    browser_mime_type = clean_text(
        browser_mime_type
    ).split(";")[0].lower()

    if browser_mime_type.startswith(
        "audio/"
    ):
        return browser_mime_type

    return MIME_MAP.get(
        extension,
        "audio/webm"
    )


def upload_bytes_to_firebase(
    storage,
    data,
    path,
    content_type
):
    bucket = storage.bucket()

    blob = bucket.blob(
        path
    )

    token = str(
        uuid.uuid4()
    )

    blob.metadata = {
        "firebaseStorageDownloadTokens":
            token
    }

    blob.upload_from_string(
        data,
        content_type=content_type
    )

    encoded_path = quote(
        path,
        safe=""
    )

    return (
        "https://firebasestorage.googleapis.com"
        f"/v0/b/{bucket.name}/o/{encoded_path}"
        f"?alt=media&token={token}"
    )


def clean_json(text):
    text = clean_text(
        text
    )

    if text.startswith("```"):
        text = (
            text.replace(
                "```json",
                ""
            )
            .replace(
                "```",
                ""
            )
            .strip()
        )

    match = re.search(
        r"\{.*\}",
        text,
        re.DOTALL
    )

    if match:
        text = match.group(0)

    return json.loads(
        text
    )
    
def normalize_repeated_sentence(text):
    text = clean_text(text)

    text = re.sub(
        r"\s+",
        " ",
        text
    )

    text = re.sub(
        r"[\u200b-\u200d\ufeff]",
        "",
        text
    )

    return text.strip().lower()


def sentence_similarity(
    first,
    second
):
    first = normalize_repeated_sentence(
        first
    )

    second = normalize_repeated_sentence(
        second
    )

    if not first or not second:
        return 0.0

    if first == second:
        return 1.0

    return SequenceMatcher(
        None,
        first,
        second
    ).ratio()


def split_voice_sentences(text):
    text = clean_text(
        text
    )

    if not text:
        return []

    sentences = [
        clean_text(piece)
        for piece in re.split(
            r"(?<=[.!?。！？।])\s*",
            text
        )
        if clean_text(piece)
    ]

    if len(sentences) <= 1:

        sentences = [
            clean_text(piece)
            for piece in re.split(
                r"(?<=[,，;；])\s*",
                text
            )
            if clean_text(piece)
        ]

    return sentences


def remove_accidental_repetitions(
    text
):
    text = clean_text(
        text
    )

    if not text:
        return ""

    # Remove accidental repeated spaces.
    text = re.sub(
        r"\s+",
        " ",
        text
    ).strip()

    sentences = split_voice_sentences(
        text
    )

    if len(sentences) > 1:

        cleaned = []

        previous_sentence = ""

        repeated_count = 0

        for sentence in sentences:

            if not previous_sentence:

                cleaned.append(
                    sentence
                )

                previous_sentence = (
                    sentence
                )

                repeated_count = 1

                continue

            similarity = sentence_similarity(
                previous_sentence,
                sentence
            )

            if similarity >= 0.93:

                repeated_count += 1

                # Preserve maximum two genuine repeats.
                if repeated_count <= 2:

                    cleaned.append(
                        sentence
                    )

                continue

            cleaned.append(
                sentence
            )

            previous_sentence = (
                sentence
            )

            repeated_count = 1

        text = " ".join(
            cleaned
        )


    # =====================================
    # PHRASE-LEVEL REPETITION PROTECTION
    # =====================================

    words = text.split()

    if len(words) >= 8:

        for phrase_length in range(
            min(12, len(words) // 2),
            2,
            -1
        ):

            index = 0

            output = []

            changed = False

            while index < len(words):

                current_phrase = words[
                    index:
                    index + phrase_length
                ]

                next_phrase = words[
                    index + phrase_length:
                    index + (
                        phrase_length * 2
                    )
                ]

                third_phrase = words[
                    index + (
                        phrase_length * 2
                    ):
                    index + (
                        phrase_length * 3
                    )
                ]

                if (
                    len(current_phrase)
                    == phrase_length
                    and
                    len(next_phrase)
                    == phrase_length
                ):

                    current_text = " ".join(
                        current_phrase
                    )

                    next_text = " ".join(
                        next_phrase
                    )

                    similarity = (
                        sentence_similarity(
                            current_text,
                            next_text
                        )
                    )

                    if similarity >= 0.96:

                        output.extend(
                            current_phrase
                        )

                        output.extend(
                            next_phrase
                        )

                        index += (
                            phrase_length * 2
                        )

                        # Remove third/fourth/etc
                        # model-created repetitions.
                        while (
                            index + phrase_length
                            <= len(words)
                        ):

                            candidate = " ".join(
                                words[
                                    index:
                                    index
                                    + phrase_length
                                ]
                            )

                            if (
                                sentence_similarity(
                                    current_text,
                                    candidate
                                )
                                >= 0.96
                            ):

                                index += (
                                    phrase_length
                                )

                                changed = True

                            else:

                                break

                        continue

                output.append(
                    words[index]
                )

                index += 1

            if changed:

                words = output

                text = " ".join(
                    words
                )

    return clean_text(
        text
    )
    
def speech_translate(
    audio_bytes,
    mime_type,
    target_language_name,
    target_language_code=""
):
    api_key = os.getenv(
        "GEMINI_API_KEY",
        ""
    ).strip()

    if not api_key:
        raise RuntimeError(
            "GEMINI_API_KEY missing."
        )

    if not audio_bytes:
        raise ValueError(
            "Recorded audio is empty."
        )

    client = genai.Client(
        api_key=api_key
    )

    target_language_name = (
        clean_text(
            target_language_name
        )
        or "English"
    )

    target_language_code = (
        clean_text(
            target_language_code
        ).lower()
        or "en"
    )

    prompt = f"""
You are Basha Messenger's production speech translator.

Listen to the supplied recording once as one continuous recording.

The audio may contain:
- normal human conversation
- television audio
- movie dialogue
- background music
- multiple speakers
- background noise

Tasks:

1. Detect the primary spoken language.
2. Transcribe only clearly audible speech.
3. Translate that speech into {target_language_name}.
4. Preserve the real spoken order.

IMPORTANT REPETITION RULE:

Sometimes audio models accidentally repeat the same sentence
many times even though the recording contains it only once.

Do NOT duplicate sentences because of decoding/transcription errors.

However, if the actual speaker intentionally repeats a phrase,
preserve the genuine repetition.

Ignore:
- background music
- non-speech noise
- echoes
- duplicated model decoding
- subtitles or imagined words not spoken

Return ONLY valid JSON:

{{
  "detected_language": "Chinese",
  "detected_language_code": "zh",
  "original_text": "accurate spoken text",
  "translated_text": "translation in {target_language_name}"
}}

Rules:

- No markdown.
- No explanation.
- No timestamps.
- Preserve names.
- Preserve numbers.
- Do not invent speech.
- Do not translate music lyrics unless they are clearly the main speech.
- If multiple people speak, keep their spoken sequence.
""".strip()

    response = client.models.generate_content(
        model=AUDIO_MODEL_NAME,

        contents=[
            types.Part.from_bytes(
                data=audio_bytes,
                mime_type=mime_type
            ),
            prompt
        ],

        config=types.GenerateContentConfig(
            temperature=0.0,
            response_mime_type=(
                "application/json"
            )
        )
    )

    response_text = clean_text(
        response.text
    )

    if not response_text:
        raise RuntimeError(
            "Audio translator returned an empty response."
        )

    data = clean_json(
        response_text
    )

    detected_language = (
        clean_text(
            data.get(
                "detected_language"
            )
        )
        or "Auto Detected"
    )

    detected_language_code = (
        clean_text(
            data.get(
                "detected_language_code"
            )
        ).lower()
    )

    original_text = (
        remove_accidental_repetitions(
            data.get(
                "original_text",
                ""
            )
        )
    )

    translated_text = (
        remove_accidental_repetitions(
            data.get(
                "translated_text",
                ""
            )
        )
    )

    if not original_text:
        raise ValueError(
            "No clear speech was detected."
        )

    if not translated_text:
        raise ValueError(
            "Unable to translate the recorded speech."
        )

    return {
        "detected_language":
            detected_language,

        "detected_language_code":
            detected_language_code,

        "original_text":
            original_text,

        "translated_text":
            translated_text
    }

def build_tts_mp3_bytes(
    translated_text,
    language_code
):
    translated_text = clean_text(
        translated_text
    )

    language_code = clean_text(
        language_code
    ).lower()

    if not translated_text:
        raise ValueError(
            "Translated text is empty."
        )

    tts_language = GTTS_LANG.get(
        language_code
    )

    if not tts_language:
        raise ValueError(
            "Translated audio is not "
            "available for this language."
        )


    # =====================================
    # FAST PATH - GOOGLE CLOUD TTS
    # =====================================

    if texttospeech is not None:

        try:

            client = (
                texttospeech
                .TextToSpeechClient()
            )

            language_map = {
                "en": "en-IN",
                "te": "te-IN",
                "hi": "hi-IN",
                "ta": "ta-IN",
                "kn": "kn-IN",
                "ml": "ml-IN",
                "mr": "mr-IN",
                "gu": "gu-IN",
                "bn": "bn-IN",
                "pa": "pa-IN",
                "ur": "ur-IN"
            }

            cloud_language_code = (
                language_map.get(
                    language_code
                )
            )

            if cloud_language_code:

                synthesis_input = (
                    texttospeech
                    .SynthesisInput(
                        text=translated_text
                    )
                )

                voice = (
                    texttospeech
                    .VoiceSelectionParams(
                        language_code=
                            cloud_language_code,

                        ssml_gender=
                            texttospeech
                            .SsmlVoiceGender
                            .FEMALE
                    )
                )

                audio_config = (
                    texttospeech
                    .AudioConfig(
                        audio_encoding=
                            texttospeech
                            .AudioEncoding
                            .MP3,

                        speaking_rate=1.05
                    )
                )

                response = (
                    client
                    .synthesize_speech(
                        input=
                            synthesis_input,

                        voice=
                            voice,

                        audio_config=
                            audio_config
                    )
                )

                if response.audio_content:

                    return (
                        response
                        .audio_content
                    )

        except Exception as cloud_error:

            print(
                "GOOGLE CLOUD TTS FALLBACK:",
                repr(cloud_error)
            )


    # =====================================
    # FALLBACK - GTTS
    # =====================================

    temp_mp3_path = None

    try:

        temp_mp3 = (
            tempfile.NamedTemporaryFile(
                delete=False,
                suffix=".mp3"
            )
        )

        temp_mp3.close()

        temp_mp3_path = (
            temp_mp3.name
        )

        gTTS(
            text=translated_text,
            lang=tts_language,
            slow=False
        ).save(
            temp_mp3_path
        )

        with open(
            temp_mp3_path,
            "rb"
        ) as audio_file:

            return audio_file.read()

    finally:

        if (
            temp_mp3_path
            and os.path.exists(
                temp_mp3_path
            )
        ):

            try:

                os.remove(
                    temp_mp3_path
                )

            except OSError:

                pass
            
def register_audio_translator_routes(
    app,
    db,
    storage,
    firestore,
    clean_mobile,
    translate_text,
    save_chat_message
):

    # ==========================================
    # HOME QUICK AUDIO TRANSLATOR
    # NO CHAT MESSAGE IS CREATED
    # ==========================================

    @app.route(
        "/audio/translate-preview",
        methods=["POST"]
    )
    def audio_translate_preview():

        try:
            if "user_id" not in session:
                return jsonify({
                    "success": False,
                    "error": "Login required"
                }), 401

            audio = request.files.get(
                "audio"
            )

            if (
                not audio
                or not audio.filename
            ):
                return jsonify({
                    "success": False,
                    "error": "Recorded audio missing"
                }), 400

            extension = audio_ext(
                audio.filename
            )

            if extension not in AUDIO_ALLOWED:
                return jsonify({
                    "success": False,
                    "error": (
                        "Unsupported audio format: "
                        f"{extension}"
                    )
                }), 400

            audio_bytes = audio.read()

            if not audio_bytes:
                return jsonify({
                    "success": False,
                    "error": "Recorded audio is empty"
                }), 400

            if len(audio_bytes) > MAX_AUDIO_SIZE:
                return jsonify({
                    "success": False,
                    "error": (
                        "Audio recording must be "
                        "below 15 MB."
                    )
                }), 400

            target_language_code = (
                clean_text(
                    request.form.get(
                        "target_language_code"
                    )
                ).lower()
                or "en"
            )

            target_language_name = (
                clean_text(
                    request.form.get(
                        "target_language_name"
                    )
                )
                or LANGUAGE_NAMES.get(
                    target_language_code,
                    "English"
                )
            )

            if (
                target_language_code
                not in LANGUAGE_NAMES
            ):
                return jsonify({
                    "success": False,
                    "error": (
                        "Invalid target language."
                    )
                }), 400

            mime_type = get_audio_mime_type(
                extension,
                audio.mimetype
            )

            result = speech_translate(
                audio_bytes=audio_bytes,

                mime_type=mime_type,

                target_language_name=
                    target_language_name,

                target_language_code=
                    target_language_code
            )

            translated_audio_available = (
                True
            )

            translated_audio_data = ""

            translated_audio_error = ""

            try:
                mp3_bytes = (
                    build_tts_mp3_bytes(
                        result[
                            "translated_text"
                        ],
                        target_language_code
                    )
                )

                translated_audio_data = (
                    "data:audio/mpeg;base64,"
                    + base64.b64encode(
                        mp3_bytes
                    ).decode(
                        "ascii"
                    )
                )

            except Exception as tts_error:
                translated_audio_available = (
                    False
                )

                translated_audio_error = (
                    str(tts_error)
                )

                print(
                    "QUICK AUDIO TTS ERROR:",
                    repr(tts_error)
                )

            return jsonify({
                "success": True,

                "inputType":
                    "audio",

                "original":
                    result[
                        "original_text"
                    ],

                "translated":
                    result[
                        "translated_text"
                    ],

                "sourceLanguage":
                    result[
                        "detected_language_code"
                    ] or "auto",

                "sourceLanguageName":
                    result[
                        "detected_language"
                    ],

                "detectedLanguage":
                    result[
                        "detected_language"
                    ],

                "detectedLanguageCode":
                    result[
                        "detected_language_code"
                    ],

                "targetLanguage":
                    target_language_code,

                "targetLanguageName":
                    target_language_name,

                "translatedAudioAvailable":
                    translated_audio_available,

                "translatedAudioData":
                    translated_audio_data,

                "translatedAudioError":
                    translated_audio_error
            })

        except Exception as error:

            print(
                "QUICK AUDIO TRANSLATION ERROR:",
                repr(error)
            )

            return jsonify({
                "success": False,
                "error": str(error)
            }), 500


    # ==========================================
    # EXISTING CHAT AUDIO TRANSLATOR
    # PRESERVED
    # ==========================================

    @app.route(
        "/audio/translate-send",
        methods=["POST"]
    )
    def audio_translate_send():

        try:
            if "user_id" not in session:
                return jsonify({
                    "success": False,
                    "error": "Login required"
                }), 401

            receiver_mobile = clean_mobile(
                request.form.get(
                    "receiver_mobile",
                    ""
                )
            )

            audio = request.files.get(
                "audio"
            )

            if not receiver_mobile:
                return jsonify({
                    "success": False,
                    "error": "Receiver missing"
                }), 400

            if (
                not audio
                or not audio.filename
            ):
                return jsonify({
                    "success": False,
                    "error": "Audio missing"
                }), 400

            extension = audio_ext(
                audio.filename
            )

            if extension not in AUDIO_ALLOWED:
                return jsonify({
                    "success": False,
                    "error": (
                        "Invalid audio format: "
                        f"{extension}"
                    )
                }), 400

            audio_bytes = audio.read()

            if not audio_bytes:
                return jsonify({
                    "success": False,
                    "error": "Audio is empty"
                }), 400

            if len(audio_bytes) > MAX_AUDIO_SIZE:
                return jsonify({
                    "success": False,
                    "error": (
                        "Audio must be below 15 MB."
                    )
                }), 400

            mime_type = get_audio_mime_type(
                extension,
                audio.mimetype
            )

            original_audio_url = (
                upload_bytes_to_firebase(
                    storage,

                    audio_bytes,

                    (
                        "voice_messages/"
                        f"{session['user_id']}_"
                        f"{uuid.uuid4().hex}."
                        f"{extension}"
                    ),

                    mime_type
                )
            )

            receiver_language_code = (
                "en"
            )

            receiver_language_name = (
                "English"
            )

            receiver_docs = (
                db.collection("users")
                .where(
                    "mobile",
                    "==",
                    receiver_mobile
                )
                .limit(1)
                .get()
            )

            if receiver_docs:
                receiver_data = (
                    receiver_docs[0]
                    .to_dict()
                    or {}
                )

                receiver_language_code = (
                    receiver_data.get(
                        "languageCode"
                    )
                    or "en"
                )

                receiver_language_name = (
                    receiver_data.get(
                        "languageName"
                    )
                    or LANGUAGE_NAMES.get(
                        receiver_language_code,
                        "English"
                    )
                )

            result = speech_translate(
                audio_bytes=audio_bytes,

                mime_type=mime_type,

                target_language_name=
                    receiver_language_name,

                target_language_code=
                    receiver_language_code
            )

            mp3_bytes = (
                build_tts_mp3_bytes(
                    result[
                        "translated_text"
                    ],
                    receiver_language_code
                )
            )

            translated_audio_url = (
                upload_bytes_to_firebase(
                    storage,

                    mp3_bytes,

                    (
                        "audio_translations/"
                        f"{session['user_id']}_"
                        f"{uuid.uuid4().hex}.mp3"
                    ),

                    "audio/mpeg"
                )
            )

            sender_doc = (
                db.collection("users")
                .document(
                    session["user_id"]
                )
                .get()
            )

            sender = (
                sender_doc.to_dict()
                if sender_doc.exists
                else {}
            )

            sender_mobile = clean_mobile(
                sender.get(
                    "mobile",
                    ""
                )
            )

            sender_language_code = (
                sender.get(
                    "languageCode"
                )
                or result[
                    "detected_language_code"
                ]
                or "en"
            )

            receiver_mobile = clean_mobile(
                receiver_mobile
            )

            chat_id = "_".join(
                sorted([
                    sender_mobile,
                    receiver_mobile
                ])
            )

            chat_ref = (
                db.collection("chats")
                .document(chat_id)
            )

            chat_ref.set({
                "participants": [
                    sender_mobile,
                    receiver_mobile
                ],

                "lastMessage":
                    "🎙 Voice Message",

                "lastMessageTime":
                    firestore.SERVER_TIMESTAMP

            }, merge=True)

            chat_ref.collection(
                "messages"
            ).add({

                "senderMobile":
                    sender_mobile,

                "receiverMobile":
                    receiver_mobile,

                "message":
                    result[
                        "original_text"
                    ],

                "translatedMessage":
                    result[
                        "translated_text"
                    ],

                "senderLanguage":
                    sender_language_code,

                "detectedLanguage":
                    result[
                        "detected_language"
                    ],

                "receiverLanguage":
                    receiver_language_code,

                "originalAudioUrl":
                    original_audio_url,

                "translatedAudioUrl":
                    translated_audio_url,

                "fileUrl":
                    original_audio_url,

                "fileName":
                    (
                        "voice-message."
                        f"{extension}"
                    ),

                "fileType":
                    "audio",

                "readBy":
                    [sender_mobile],

                "delivered":
                    False,

                "timestamp":
                    firestore.SERVER_TIMESTAMP
            })

            return jsonify({
                "success": True,

                "audio_url":
                    translated_audio_url,

                "original_audio_url":
                    original_audio_url,

                "original_text":
                    result[
                        "original_text"
                    ],

                "translated_text":
                    result[
                        "translated_text"
                    ],

                "detected_language":
                    result[
                        "detected_language"
                    ]
            })

        except Exception as error:

            print(
                "AUDIO TRANSLATION ERROR:",
                repr(error)
            )

            return jsonify({
                "success": False,
                "error": str(error)
            }), 500