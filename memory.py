# memory.py - persistent key/value facts + last capture pointer
import os, json, datetime
from config import DATA_DIR, MEMORY_FILE
from history import add_history

def _utc_now():
    return datetime.datetime.now(datetime.timezone.utc).isoformat()

def ensure_memory_file():
    os.makedirs(DATA_DIR, exist_ok=True)
    if not os.path.exists(MEMORY_FILE):
        with open(MEMORY_FILE, "w", encoding="utf-8") as f:
            json.dump({"facts": {}, "last_capture": None}, f, indent=2)

def _load():
    ensure_memory_file()
    with open(MEMORY_FILE, "r", encoding="utf-8") as f:
        return json.load(f)

def _save(obj):
    with open(MEMORY_FILE, "w", encoding="utf-8") as f:
        json.dump(obj, f, indent=2)

def remember(key: str, value: str) -> str:
    obj = _load()
    obj["facts"][key.lower().strip()] = {"value": value.strip(), "time": _utc_now()}
    _save(obj)
    add_history("remember", f"{key} = {value}")
    return f"Okay, remembered {key} = {value}."

def recall(key: str) -> str:
    obj = _load()
    entry = obj["facts"].get(key.lower().strip())
    if not entry:
        return f"I don't have anything saved for '{key}'."
    return f"You told me: {key} = {entry['value']} (saved {entry['time']})."

def set_last_capture(path: str):
    obj = _load()
    obj["last_capture"] = {"path": path, "time": _utc_now()}
    _save(obj)
    add_history("capture_set", path)

def get_last_capture():
    obj = _load()
    return obj.get("last_capture")
