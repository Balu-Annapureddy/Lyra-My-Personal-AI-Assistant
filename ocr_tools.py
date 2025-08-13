# ocr_tools.py - camera capture + OCR (Tesseract optional)
import os, cv2, datetime
from PIL import Image
import pytesseract
from config import CAPTURES_DIR, TESSERACT_PATH
from memory import set_last_capture
from history import add_history

# configure tesseract if path exists
if TESSERACT_PATH and os.path.exists(TESSERACT_PATH):
    pytesseract.pytesseract.tesseract_cmd = TESSERACT_PATH

os.makedirs(CAPTURES_DIR, exist_ok=True)

def capture_image() -> str:
    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        return ""
    ok, frame = cap.read()
    cap.release()
    if not ok:
        return ""
    ts = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    path = os.path.join(CAPTURES_DIR, f"capture_{ts}.png")
    cv2.imwrite(path, frame)
    set_last_capture(path)
    add_history("capture", path)
    return path

def ocr_image(path: str) -> str:
    if not os.path.exists(path):
        return "(ocr) file not found"
    try:
        img = Image.open(path)
        text = pytesseract.image_to_string(img)
        return (text or "").strip()
    except Exception as e:
        return f"(ocr error) {e}"
