# spellfix.py - safe fuzzy command suggestion using rapidfuzz
try:
    from rapidfuzz import process as rf_process
except Exception:
    rf_process = None

COMMON_COMMANDS = [
    "remember", "what did i say about", "capture", "read text", "ocr", "describe",
    "describe image", "history", "help", "exit", "quit"
]

def suggest_command(user_text: str):
    """
    Returns a suggested command string if there's a high-confidence match,
    otherwise returns None. Handles the case where rapidfuzz isn't available.
    """
    if not rf_process or not user_text:
        return None
    result = rf_process.extractOne(user_text.lower(), COMMON_COMMANDS, score_cutoff=80)
    if not result:
        return None
    # result can be (choice, score, index)
    try:
        choice = result[0]
        return choice
    except Exception:
        return None

def maybe_fix_query(user_text: str) -> str:
    suggestion = suggest_command(user_text)
    return suggestion if suggestion else user_text
