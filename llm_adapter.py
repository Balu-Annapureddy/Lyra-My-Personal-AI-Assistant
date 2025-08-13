# llm_adapter.py - minimal Ollama client returning clean text
import requests
from config import OLLAMA_HOST, OLLAMA_MODEL

def chat(prompt: str, system: str | None = None, timeout: int = 60) -> str:
    """
    Uses Ollama /api/generate to get a plain-text response.
    Returns a short string or an error string starting with (LLM offline/error)
    """
    url = f"{OLLAMA_HOST}/api/generate"
    payload = {
        "model": OLLAMA_MODEL,
        "prompt": (system + "\n\n" + prompt) if system else prompt,
        "stream": False
    }
    try:
        r = requests.post(url, json=payload, timeout=timeout)
        r.raise_for_status()
        data = r.json()
        # Try common keys
        if isinstance(data, dict):
            if "response" in data and data["response"]:
                return str(data["response"]).strip()
            if "choices" in data and isinstance(data["choices"], list) and data["choices"]:
                # Ollama can sometimes return choices with message/content-like structure
                first = data["choices"][0]
                if isinstance(first, dict):
                    for k in ("message","text","content"):
                        v = first.get(k)
                        if v:
                            return str(v).strip()
        # fallback to stringification
        return str(data).strip()
    except Exception as e:
        return f"(LLM offline/error) {e}"
