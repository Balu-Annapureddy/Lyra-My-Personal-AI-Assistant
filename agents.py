# agents.py - command router connecting memory/vision/LLM/search
import re
from llm_adapter import chat
from history import add_history, get_history
from memory import remember, recall, get_last_capture
from ocr_tools import capture_image, ocr_image
from web_search import search_web_fallback
from spellfix import maybe_fix_query

SYSTEM_PROMPT = (
    "You are Lyra, a concise, helpful personal assistant. Answer in clear short sentences. "
    "If information may be outdated, mention briefly that it may be."
)

def handle_command(text: str) -> str:
    t = (text or "").strip()
    if not t:
        return ""

    # Light spell-fix for command-like phrases
    t = maybe_fix_query(t)

    # remember <k> as <v>
    m = re.match(r"^remember\s+(.+?)\s+as\s+(.+)$", t, flags=re.I)
    if m:
        k, v = m.group(1).strip(), m.group(2).strip()
        return remember(k, v)

    # recall
    m = re.match(r"^what did i say about\s+(.+)$", t, flags=re.I)
    if m:
        return recall(m.group(1).strip())

    # capture
    if t.lower() == "capture":
        p = capture_image()
        if not p:
            return "Camera not available or capture failed."
        return f"Captured to {p}. You can say 'read text' or 'describe'."

    # OCR last capture
    if t.lower() in ("read text", "ocr", "read"):
        last = get_last_capture()
        if not last:
            return "No recent capture found."
        return ocr_image(last["path"]) or "(No text detected.)"

    # describe image
    if t.lower() in ("describe", "analyze", "describe image", "what's in the image"):
        last = get_last_capture()
        if not last:
            return "No recent capture found."
        hint = ocr_image(last["path"])
        prompt = f"Describe the latest captured image briefly. OCR text (may be noisy):\n{hint}"
        ans = chat(prompt, system=SYSTEM_PROMPT)
        if ans.startswith("(LLM offline/error)"):
            return "Cannot analyze image (LLM offline)."
        return ans

    # history
    if t.lower() == "history":
        ev = get_history(30)
        if not ev:
            return "No history yet."
        return "\n".join(f"[{e['time']}] {e['type']}: {e['detail']}" for e in ev)

    # General Q&A: LLM first, fallback to web search if LLM fails or returns too short.
    ans = chat(t, system=SYSTEM_PROMPT)
    if ans.startswith("(LLM offline/error)") or len(ans.strip()) < 4:
        ans = search_web_fallback(t)
    add_history("chat", t)
    return ans
