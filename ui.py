# ui.py - light-themed modern Tkinter UI with rounded buttons & text/speech toggle
import os
import tkinter as tk
from tkinter import ttk
import threading

from config import UI_THEME, MAX_CHAT_WIDTH, CAPTURES_DIR
from agents import handle_command
from tts_handler import speak
from history import add_history, get_history
from ocr_tools import capture_image

# Light theme palette (UI_THEME set to "light")
BG = "#F3F6FB"
PANEL = "#FFFFFF"
TXT = "#0B1220"
SUB = "#475569"
ACCENT = "#2563EB"  # blue
USER_BUBBLE = "#DCFCE7"
AI_BUBBLE = "#F1F5F9"

# Ensure folders
os.makedirs(CAPTURES_DIR, exist_ok=True)
os.makedirs(os.path.join(os.path.dirname(__file__), "data"), exist_ok=True)

# Rounded canvas button
class RoundButton(tk.Canvas):
    def __init__(self, master, text, command=None, bg=ACCENT, fg="#ffffff",
                 radius=14, padding=(14,8), font=("Segoe UI", 10, "bold")):
        super().__init__(master, bd=0, highlightthickness=0, bg=master["bg"])
        self.command = command
        self._bg = bg
        self._fg = fg
        self._radius = radius
        self._font = font
        self._padding = padding
        self._text = text
        self._draw()
        self.bind("<Button-1>", lambda e: self._on_click())
        self.bind("<Enter>", lambda e: self._hover(True))
        self.bind("<Leave>", lambda e: self._hover(False))

    def _draw(self):
        self.delete("all")
        txt_id = self.create_text(0,0, text=self._text, fill=self._fg, font=self._font, anchor="nw")
        bbox = self.bbox(txt_id)
        w = (bbox[2] - bbox[0]) + self._padding[0]*2
        h = (bbox[3] - bbox[1]) + self._padding[1]*2
        self.configure(width=w, height=h)
        # rounded rect using create_oval for corners
        r = self._radius
        self.create_rectangle(r, 0, w-r, h, fill=self._bg, outline=self._bg)
        self.create_rectangle(0, r, w, h-r, fill=self._bg, outline=self._bg)
        self.create_oval(0, 0, r*2, r*2, fill=self._bg, outline=self._bg)
        self.create_oval(w-2*r, 0, w, r*2, fill=self._bg, outline=self._bg)
        self.create_oval(0, h-2*r, r*2, h, fill=self._bg, outline=self._bg)
        self.create_oval(w-2*r, h-2*r, w, h, fill=self._bg, outline=self._bg)
        self.create_text(w/2, h/2, text=self._text, fill=self._fg, font=self._font, anchor="c")

    def _on_click(self):
        if callable(self.command):
            self.command()

    def _hover(self, on):
        self._bg = "#1D4ED8" if on else ACCENT
        self._draw()

class LyraUI:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Lyra — Personal AI")
        self.root.geometry("940x680")
        self.root.configure(bg=BG)

        self.voice_enabled = tk.BooleanVar(value=False)

        # Header
        top = tk.Frame(self.root, bg=BG)
        top.pack(fill=tk.X, padx=16, pady=(12,8))
        title = tk.Label(top, text="Lyra", bg=BG, fg=ACCENT, font=("Segoe UI", 20, "bold"))
        title.pack(side=tk.LEFT)
        # Speak toggle
        voice_chk = ttk.Checkbutton(top, text="Speak replies", variable=self.voice_enabled)
        voice_chk.pack(side=tk.RIGHT)

        # Canvas chat area
        mid = tk.Frame(self.root, bg=BG)
        mid.pack(fill=tk.BOTH, expand=True, padx=12, pady=(0,12))

        self.canvas = tk.Canvas(mid, bg=BG, highlightthickness=0)
        self.scroll = ttk.Scrollbar(mid, orient="vertical", command=self.canvas.yview)
        self.canvas.configure(yscrollcommand=self.scroll.set)
        self.scroll.pack(side=tk.RIGHT, fill=tk.Y)
        self.canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        self.chat_frame = tk.Frame(self.canvas, bg=BG)
        self.canvas.create_window((0,0), window=self.chat_frame, anchor="nw")
        self.chat_frame.bind("<Configure>", lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all")))

        # Bottom entry / buttons
        bottom = tk.Frame(self.root, bg=BG)
        bottom.pack(fill=tk.X, padx=12, pady=(0,14))

        self.entry = tk.Entry(bottom, font=("Segoe UI", 12), bg=PANEL, fg=TXT, insertbackground=TXT, relief="flat")
        self.entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0,10), ipady=10)
        self.entry.bind("<Return>", lambda e: self.on_send())

        self.btn_send = RoundButton(bottom, "Send", command=self.on_send)
        self.btn_send.pack(side=tk.LEFT, padx=(0,8))

        self.btn_mic = RoundButton(bottom, "🎤 Mic", command=self.on_mic)
        self.btn_mic.pack(side=tk.LEFT, padx=(0,8))

        self.btn_capture = RoundButton(bottom, "📷 Capture", command=self.on_capture)
        self.btn_capture.pack(side=tk.LEFT)

        # initial greeting
        self._post_ai("Hello — I'm Lyra. Type or press 🎤. Try: 'remember X as Y', 'what did i say about X', 'capture', 'read text', 'describe', 'history'.")

    # ---------- bubbles ----------
    def _bubble(self, text, is_user=False):
        wrap = min(MAX_CHAT_WIDTH, int(self.root.winfo_width() * 0.6 or MAX_CHAT_WIDTH))
        outer = tk.Frame(self.chat_frame, bg=BG)
        outer.pack(fill=tk.X, padx=8, pady=6)
        holder = tk.Frame(outer, bg=BG)
        holder.pack(anchor="e" if is_user else "w")
        bubble = tk.Frame(holder, bg=USER_BUBBLE if is_user else AI_BUBBLE, bd=0)
        bubble.pack()
        lbl = tk.Label(bubble, text=text, bg=USER_BUBBLE if is_user else AI_BUBBLE,
                       fg=TXT, font=("Segoe UI", 11), wraplength=wrap, justify="right" if is_user else "left")
        lbl.pack(padx=12, pady=8)
        # scroll to bottom
        self.root.after(50, lambda: self.canvas.yview_moveto(1.0))

    def post_user(self, text: str):
        self._bubble(text, is_user=True)

    def _post_ai(self, text: str):
        self._bubble(text, is_user=False)

    # ---------- actions ----------
    def on_send(self):
        text = self.entry.get().strip()
        if not text:
            return
        self.entry.delete(0, tk.END)
        self.post_user(text)
        threading.Thread(target=self._process_and_reply, args=(text,), daemon=True).start()

    def on_mic(self):
        self._post_ai("Listening... (say something)")
        threading.Thread(target=self._mic_worker, daemon=True).start()

    def _mic_worker(self):
        try:
            import speech_recognition as sr
            r = sr.Recognizer()
            with sr.Microphone() as src:
                r.adjust_for_ambient_noise(src, duration=0.6)
                audio = r.listen(src, phrase_time_limit=8)
            try:
                txt = r.recognize_google(audio)
            except sr.UnknownValueError:
                self._post_ai("Sorry — I didn't catch that.")
                return
            except Exception as e:
                self._post_ai(f"Speech recognition error: {e}")
                return
            self.post_user(txt)
            resp = handle_command(txt)
            self._post_ai(resp)
            if self.voice_enabled.get() and resp:
                speak(resp)
        except Exception:
            self._post_ai("Mic not available (install PyAudio & SpeechRecognition).")

    def on_capture(self):
        self._post_ai("Capturing...")
        threading.Thread(target=self._capture_worker, daemon=True).start()

    def _capture_worker(self):
        p = capture_image()
        if not p:
            self._post_ai("Camera not available / capture failed.")
            return
        self._post_ai(f"Captured to {p}. You can say 'read text' or 'describe'.")

    def _process_and_reply(self, text: str):
        resp = handle_command(text)
        # ensure string
        if not isinstance(resp, str):
            resp = str(resp)
        self._post_ai(resp)
        if self.voice_enabled.get() and resp:
            speak(resp)

    def run(self):
        self.root.mainloop()
