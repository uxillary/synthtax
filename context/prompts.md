# Synthtax — Codex Prompt Library

This file contains **ready-to-use, copy-paste Codex prompts** for building Synthtax features.  
Each prompt assumes Codex already has the `context.md` loaded or understands Synthtax’s vision.

---

## 1. UI Components

### Prompt: Build Gradio Dashboard

You are adding a Gradio interface for Synthtax.  
Requirements:

- Dark theme dashboard with accent colors from Synthtax branding.
- Sections: Prompt Input, Style Presets (buttons), Prompt Influencers (sliders), Playback Controls, Track Layers, Export Buttons.
- Real-time playback preview after changes.
- Keep the layout clean and fun, with a creative/dev aesthetic.

---

### Prompt: Add Style Preset Buttons

You are updating the Gradio UI to include style preset buttons for:

- Ambient
- Synth
- Pop
- Dance
When clicked, they should populate the prompt input field with a starter genre description and set internal variables for AI generation.

---

### Prompt: Prompt Influencer Sliders

Add sliders to adjust prompt "influencers":

- Energy (0–100)
- Percussion Density (0–100)
- FX Intensity (0–100)
These sliders should modify the YAML recipe before track generation.

---

## 2. Audio Engine Features

### Prompt: Build Recipe-to-Audio Pipeline

Implement a function `build_track(recipe: dict)` that:

- Reads a YAML recipe file.
- Loads samples from built-in packs or user-uploaded files.
- Applies gain, panning, and basic FX from recipe.
- Overlays samples according to timing.
- Returns a pydub AudioSegment.

---

### Prompt: Real-Time Playback

Implement real-time audio playback for Synthtax using Python.  
Requirements:

- Low-latency streaming from buffer.
- Allow playback pause/resume.
- Reflect changes immediately when recipe is updated.

---

### Prompt: Sample Import System

Implement a drag-and-drop sample import in Gradio.  
Requirements:

- Accept WAV, MP3, FLAC.
- Auto-convert to WAV internally via FFmpeg.
- Store in `/samples/user/` with metadata.

---

### Prompt: Built-in Sample Packs

Add a system to load built-in sample packs from `/samples/builtin/`.  
Include metadata (BPM, key, genre tags) for AI to use during arrangement.

---

## 3. AI Integration

### Prompt: Prompt-to-Recipe Translator

Implement `generate_recipe_from_prompt(prompt: str, style: str, influencers: dict)`:

- Sends the prompt + style + influencer values to AI model.
- Returns a structured YAML recipe with layers, samples, FX, and arrangement.
- Include tempo, key, and duration.

---

### Prompt: Multi-Model AI Setup

Set up two AI models:

- Model A (text) for recipe generation.
- Model B (audio) for generating synthetic samples when needed.
Provide a way to toggle synthetic vs sample-based output.

---

### Prompt: AI Explanation of Track

After track generation, produce a plain-language description of what the user just made:

- Instruments used
- Mood/style
- Key production elements

---

## 4. Export & Output

### Prompt: Export Stems and Full Track

Implement `export_track_and_stems(track: AudioSegment, recipe: dict, out_dir: str)`:

- Export full track to `full_track.wav` and `full_track.mp3`.
- Export each layer to separate stem files.
- Include YAML recipe in the output folder.

---

## 5. Testing & Validation

### Prompt: Build Demo Recipe

Create a demo YAML recipe that:

- Has 3 layers (drums, bass, melody).
- Uses built-in samples.
- Lasts 8 bars.
- Demonstrates panning and gain changes.

---

### Prompt: Audio Validation

Implement a validation step after export:

- Check that all files are playable.
- Warn user if any track is silent or corrupted.

---

## 6. Fun Extras

### Prompt: Add Easter Egg Sound

Add a hidden Easter egg in Synthtax:

- If the prompt contains "Rick Astley" it overlays a short clip of "Never Gonna Give You Up" in the track intro.
- Make it subtle and funny.

---

### Prompt: Synthtax Startup Sound

On app launch, play a short Synthtax-branded synth arpeggio (use pydub to generate it).

---

**End of prompts.md**
