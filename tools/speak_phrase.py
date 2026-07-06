import os
import re
import sys
from pathlib import Path

import httpx
from dotenv import load_dotenv


load_dotenv()

ROOT_DIR = Path(__file__).resolve().parent.parent
AUDIO_DIR = ROOT_DIR / "audiofiles"
ELEVENLABS_BASE_URL = "https://api.elevenlabs.io/v1"


def _safe_filename(phrase):
    cleaned = re.sub(r"[^a-zA-Z0-9_-]+", "_", phrase.strip()).strip("_")
    return (cleaned or "phrase")[:80]


def _play_audio(path):
    if os.getenv("LANGLEARN_PLAY_AUDIO", "1").lower() in {"0", "false", "no"}:
        return "Playback skipped because LANGLEARN_PLAY_AUDIO is disabled."

    if sys.platform == "win32":
        os.startfile(path)
        return "Playback started with the default Windows audio app."

    return "Audio generated, but automatic playback is only wired for Windows right now."


def _voice_category(voice):
    labels = voice.get("labels") or {}
    return str(
        voice.get("category")
        or labels.get("category")
        or labels.get("use_case")
        or ""
    ).lower()


def _choose_voice(client, api_key):
    configured_voice = os.getenv("ELEVENLABS_VOICE_ID")
    if configured_voice:
        return configured_voice, "env"

    response = client.get(
        f"{ELEVENLABS_BASE_URL}/voices",
        headers={"xi-api-key": api_key},
    )
    if response.is_error:
        raise RuntimeError(
            f"Could not list ElevenLabs voices: HTTP {response.status_code} {response.text}"
        )

    voices = response.json().get("voices", [])
    usable_voices = [
        voice
        for voice in voices
        if _voice_category(voice) not in {"library", "professional", "cloned"}
    ]
    if not usable_voices:
        usable_voices = voices
    if not usable_voices:
        raise RuntimeError(
            "No ElevenLabs voices are available for this API key. Create or add a voice in your ElevenLabs workspace, then set ELEVENLABS_VOICE_ID."
        )

    voice = usable_voices[0]
    return voice["voice_id"], f"auto:{voice.get('name', voice['voice_id'])}"


def speak_phrase(phrase, play_audio=True):
    api_key = os.getenv("ELEVENLABS_API_KEY")
    AUDIO_DIR.mkdir(exist_ok=True)
    output_path = AUDIO_DIR / f"{_safe_filename(phrase)}.mp3"

    if not api_key:
        return {
            "message": "ELEVENLABS_API_KEY is not set; returning text-only playback.",
            "phrase": phrase,
            "audio_file": None,
            "audio_generated": False,
            "playback_started": False,
        }

    payload = {
        "text": phrase,
        "model_id": os.getenv("ELEVENLABS_MODEL_ID", "eleven_multilingual_v2"),
        "voice_settings": {
            "stability": 0.45,
            "similarity_boost": 0.75,
        },
    }
    headers = {
        "xi-api-key": api_key,
        "accept": "audio/mpeg",
        "content-type": "application/json",
    }

    try:
        with httpx.Client(timeout=30.0) as client:
            voice_id, voice_source = _choose_voice(client, api_key)
            url = f"{ELEVENLABS_BASE_URL}/text-to-speech/{voice_id}"
            response = client.post(url, json=payload, headers=headers)
            if response.is_error:
                return {
                    "message": (
                        f"Could not generate speech audio: HTTP {response.status_code}"
                    ),
                    "phrase": phrase,
                    "audio_file": None,
                    "audio_generated": False,
                    "playback_started": False,
                    "voice_id": voice_id,
                    "voice_source": voice_source,
                    "elevenlabs_error": response.text,
                }
        output_path.write_bytes(response.content)
    except Exception as exc:
        return {
            "message": f"Could not generate speech audio: {exc}",
            "phrase": phrase,
            "audio_file": None,
            "audio_generated": False,
            "playback_started": False,
        }

    playback_message = None
    playback_started = False
    if play_audio:
        try:
            playback_message = _play_audio(str(output_path))
            playback_started = playback_message.startswith("Playback started")
        except Exception as exc:
            playback_message = f"Audio generated, but playback failed: {exc}"

    return {
        "message": "Speech audio generated successfully",
        "phrase": phrase,
        "audio_file": str(output_path),
        "audio_generated": True,
        "playback_started": playback_started,
        "playback_message": playback_message,
        "voice_id": voice_id,
        "voice_source": voice_source,
    }

