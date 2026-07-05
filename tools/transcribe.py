import os
from pathlib import Path

from dotenv import load_dotenv
from groq import Groq


load_dotenv()


def _client():
    api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        return None
    return Groq(api_key=api_key)


def transcribe_user_response(filename):
    path = Path(filename).expanduser()
    if not path.exists():
        return {
            "ok": False,
            "error": f"Audio file not found: {path}",
            "translation": "",
            "transcription": "",
        }

    client = _client()
    if client is None:
        return {
            "ok": False,
            "error": "GROQ_API_KEY is not set",
            "translation": "",
            "transcription": "",
        }

    with path.open("rb") as f:
        translation = client.audio.translations.create(
            model="whisper-large-v3",
            file=(path.name, f.read()),
            prompt="Translate this Hindi learner response into English.",
            response_format="json",
        )

    with path.open("rb") as f:
        transcription = client.audio.transcriptions.create(
            model="whisper-large-v3",
            file=(path.name, f.read()),
            prompt="Transcribe this Hindi learner response.",
            response_format="json",
        )

    return {
        "ok": True,
        "translation": translation.text,
        "transcription": transcription.text,
        "file": str(path),
    }
