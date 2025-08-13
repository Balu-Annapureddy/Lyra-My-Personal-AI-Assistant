# config.py
import os

# ---- LLM / Ollama ----
OLLAMA_HOST = os.environ.get("OLLAMA_HOST", "http://localhost:11434")
OLLAMA_MODEL = os.environ.get("OLLAMA_MODEL", "gemma:2b")

# ---- Paths ----
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, "data")
CAPTURES_DIR = os.path.join(BASE_DIR, "captures")
MEMORY_FILE = os.path.join(DATA_DIR, "memory.json")
HISTORY_FILE = os.path.join(DATA_DIR, "history.json")

# ---- UI ----
UI_THEME = "light"                 # use "light" for preferred light UI
MAX_CHAT_WIDTH = 720

# ---- Voice / TTS ----
TTS_MODE = os.environ.get("TTS_MODE", "offline")  # "offline" or "elevenlabs"
ELEVEN_API_KEY = os.environ.get("ELEVEN_API_KEY", "")
ELEVEN_VOICE_ID = os.environ.get("ELEVEN_VOICE_ID", "Bella")

# ---- Speech Recognition ----
USE_SPEECH_RECOG = True

# ---- OCR / Tesseract ----
TESSERACT_PATH = os.environ.get("TESSERACT_PATH", r"C:\Program Files\Tesseract-OCR\tesseract.exe")

# ---- Web search ----
SEARCH_TIMEOUT = 10
USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) LyraAI/1.0"
