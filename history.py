# history.py - simple timeline store (events)
import os, json, datetime
from config import DATA_DIR, HISTORY_FILE

def _utc_now():
    return datetime.datetime.now(datetime.timezone.utc).isoformat()

def ensure_history_file():
    os.makedirs(DATA_DIR, exist_ok=True)
    if not os.path.exists(HISTORY_FILE):
        with open(HISTORY_FILE, "w", encoding="utf-8") as f:
            json.dump({"events": []}, f, indent=2)

def _load():
    ensure_history_file()
    with open(HISTORY_FILE, "r", encoding="utf-8") as f:
        return json.load(f)

def _save(data):
    with open(HISTORY_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)

def add_history(ev_type: str, detail: str):
    data = _load()
    data["events"].append({"time": _utc_now(), "type": ev_type, "detail": detail})
    data["events"] = data["events"][-500:]
    _save(data)

def get_history(n: int = 30):
    data = _load()
    return data.get("events", [])[-n:]
