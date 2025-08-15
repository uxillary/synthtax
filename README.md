# Synthtax

**Code-first music mix engine** — write your mix in YAML, render with Python (`pydub`), prompt with AI.

![Synthtax](assets/synthtax-wordmark.png)

## Quickstart

```bash
python -m venv .venv
.venv\Scripts\activate   # Windows
# source .venv/bin/activate  # macOS/Linux

pip install -r requirements.txt
python app.py
```

Open the local URL shown to use the UI. Drop some samples in `samples/` and start prompting.

## FFmpeg
Install FFmpeg and make sure it's on your PATH. Or set `FFMPEG_PATH` in `app.py`.

## Repo Layout
```
assets/     # logos etc.
context/    # product vision, prompts for Agent
samples/    # put your audio samples here (drums/textures/fx)
out/        # rendered audio (gitignored)
app.py      # Synthtax UI
recipe.yaml # example
```

## License
MIT © 2025 Adam Johnston
