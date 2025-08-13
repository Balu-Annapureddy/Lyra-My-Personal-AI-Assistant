# tts_handler.py - ElevenLabs TTS (optional) with offline pyttsx3 fallback
import os, threading, traceback
from config import TTS_MODE, ELEVEN_API_KEY, ELEVEN_VOICE_ID

# Load .env if present (so ELEVEN_API_KEY set via .env works)
try:
    from dotenv import load_dotenv
    load_dotenv()
except Exception:
    pass

def _init_engine():
    try:
        import pyttsx3
        engine = pyttsx3.init()
        # try to pick a female voice
        try:
            for v in engine.getProperty("voices"):
                nm = (v.name or "").lower()
                if "female" in nm or "zira" in nm or "susan" in nm:
                    engine.setProperty("voice", v.id)
                    break
        except Exception:
            pass
        engine.setProperty("rate", 180)
        return engine
    except Exception:
        return None

_engine = _init_engine()

def _speak_offline(text: str):
    global _engine
    if _engine is None:
        _engine = _init_engine()
    if not _engine:
        return
    try:
        _engine.say(text)
        _engine.runAndWait()
    except Exception:
        traceback.print_exc()

def _speak_eleven(text: str):
    key = ELEVEN_API_KEY or os.environ.get("ELEVEN_API_KEY", "")
    if not key:
        _speak_offline(text)
        return
    try:
        import requests, tempfile
        from pydub import AudioSegment
        from pydub.playback import play
        url = f"https://api.elevenlabs.io/v1/text-to-speech/{ELEVEN_VOICE_ID}"
        headers = {
            "xi-api-key": key,
            "accept": "audio/mpeg",
            "content-type": "application/json"
        }
        payload = {"text": text, "model_id": "eleven_multilingual_v2",
                   "voice_settings": {"stability": 0.4, "similarity_boost": 0.7}}
        r = requests.post(url, headers=headers, json=payload, timeout=60)
        r.raise_for_status()
        with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as tmp:
            tmp.write(r.content)
            path = tmp.name
        # play via pydub
        try:
            audio = AudioSegment.from_mp3(path)
            play(audio)
        except Exception:
            # fallback to system player
            try:
                if os.name == "nt":
                    os.startfile(path)
                else:
                    opener = "xdg-open" if os.system("which xdg-open >/dev/null 2>&1") == 0 else "open"
                    os.system(f'{opener} "{path}" &')
            except Exception:
                pass
    except Exception:
        _speak_offline(text)

def speak(text: str):
    if not text:
        return
    if TTS_MODE.lower() == "elevenlabs":
        threading.Thread(target=_speak_eleven, args=(text,), daemon=True).start()
    else:
        threading.Thread(target=_speak_offline, args=(text,), daemon=True).start()
