"""Regenerate the three voice prompts in public/audio/ with gTTS.

Run from repo root:
    python3 scripts/generate_tts.py
"""

from pathlib import Path
from gtts import gTTS

OUT = Path(__file__).resolve().parent.parent / "public" / "audio"

PROMPTS = {
    "welcome": "Hi! I'm Zorpie. Let's play a shape game together!",
    "how_to_play": "Two pictures are the same thing. One is different. Find the different one!",
    "reminder": "Remember! Two are the same thing. One is different. Tap the different one!",
}

OUT.mkdir(parents=True, exist_ok=True)
for name, text in PROMPTS.items():
    path = OUT / f"{name}.mp3"
    gTTS(text=text, lang="en", slow=False).save(str(path))
    print(f"wrote {path}: {text!r}")
