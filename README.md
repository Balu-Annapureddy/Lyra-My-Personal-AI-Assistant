# Lyra Mark 1 — Archived Predecessor

> 🗄️ Historical predecessor of [Lyra](https://github.com/Balu-Annapureddy/Lyra).

Lyra Mark 1 was the first major implementation of my personal AI assistant concept.

It explored:
- desktop UI interaction (Tkinter)
- natural-language commands
- voice interaction (ElevenLabs API)
- AI API integration
- task automation & web search
- optical character recognition (Tesseract OCR)

---

## Status

Archived.

This repository is preserved as the first stage of Lyra's development. Active development moved through Mark 2 and now continues in **[Lyra](https://github.com/Balu-Annapureddy/Lyra)**.

---

## Overview & Architectural Evolution

```
Lyra Architectural Evolution:
├── Lyra Mark 1 (This Repository - Original Prototype)
│   └── Single-file Python modules (main.py, tts_handler.py, ocr_tools.py, agents.py)
├── Lyra Mark 2 (Lyra-Ai-Mark2-)
│   └── Client-server architecture with Flask REST API & React frontend
└── Lyra (Lyra - Active Flagship)
    └── Local-first Personal AI Operating System with intent routing & policy guardrails
```

Development on this original prototype concluded when the architecture evolved into the client-server model in **Lyra Mark 2**, and subsequently into the local-first AI operating system engine in **[Lyra](https://github.com/Balu-Annapureddy/Lyra)**.

---

## Technical Stack (Mark 1)

- **Language**: Python 3.8+
- **Graphical UI**: Tkinter (custom light-themed desktop layout)
- **Voice & Speech**: ElevenLabs API integration (`tts_handler.py`)
- **Utilities**: Tesseract OCR (`ocr_tools.py`), Web search parsing (`web_search.py`)

---

## License

This project is licensed under the MIT License — see the [`LICENSE`](LICENSE) file for details.
