# Synthtax — Master Context for AI-Assisted Music Generation

## 1. Vision & Purpose

Synthtax is a **code-powered, AI-assisted music creation environment** designed for creatives who want to generate **tracks, loops, and soundscapes** with limited production knowledge — all through a mix of **natural language prompts** and **hands-on editing tools**.

The goal: let anyone — from DJs to coders to curious hobbyists — **write music like they write code**, with an AI that understands intent and turns it into structured, editable audio recipes.

---

## 2. Target Users

- **Creative musicians & DJs** who want fast track ideas without complex DAW workflows.
- **Coders** who want to experiment with generative audio.
- **Hobbyists** with limited music production knowledge but strong creative ideas.
- Anyone curious about **AI-assisted, code-driven music**.

**User Goals:**

- Quickly generate high-quality, unique tracks with minimal setup.
- Learn basic music structure through interactive editing.
- Balance AI creativity with personal control/tweaks.

---

## 3. Product Goals

### MVP Features

- **Prompt → Code → Track → Preview → Edit → Export** pipeline.
- Real-time playback while editing.
- Built-in style presets (ambient, synth, pop, dance, etc.).
- Pre-defined “prompt influencers” to guide generation.
- AI generates a plain-language description of the track.
- Simple editing tools: gain, panning, EQ, layering, trimming.
- Import personal samples + use built-in sample packs.
- Export: Full track + individual stems.

### Future Features

- MIDI input/output support.
- More advanced FX: convolution reverb, sidechain compression, tempo automation.
- AI-assisted mix mastering.
- Collaboration features (Discord/Twitch integrations).
- Web app version with no local dependencies.

---

## 4. Core Features in Detail

1. **Prompt Interpreter**
   - Multi-model AI processes user prompt + style preset.
   - Outputs YAML-based “recipe” defining samples, timing, FX, and automation.

2. **Pre-Defined Prompt Influencers**
   - Quick selection buttons that alter the “feel” of AI output.
   - Example: “Make it dreamy”, “Add more percussion”, “Go minimal”.

3. **Sample Handling**
   - Built-in curated sample packs.
   - User-imported samples via drag-and-drop.

4. **Editing Tools**
   - Track layer controls (volume, panning, mute/solo).
   - FX toggles and sliders.
   - Timeline trimming and rearranging.

5. **Real-Time Playback**
   - Immediate audio preview of changes.
   - Low-latency streaming with caching.

6. **Export**
   - High-quality WAV/MP3.
   - Stems for each track.
   - YAML recipe for reproducibility.

---

## 5. AI Integration Plan

### AI Roles

- **Prompt-to-recipe translation** (turn user input into structured YAML).
- **Sample selection** (choose from packs or user uploads).
- **Track arrangement** (tempo, structure, FX).
- **Plain-language explanation** of generated music:
  - *“You’ve got a smooth ambient pad with a low-pass filter, subtle hi-hat, and a 4/4 kick driving at 110bpm.”*

### Multiple Model Use

- **Text model** for parsing prompts.
- **Optional audio generation model** for synthetic samples.
- **Style presets** for AI to understand genres.

**Example Prompt:**
> “Create an 80s-style synthwave loop with a heavy bassline, gated reverb snare, and spacey pads.”

---

## 6. Technical Architecture

### Initial Stack

- **Python** for backend logic.
- **pydub** for audio assembly and FX.
- **Gradio** for interactive UI.
- **FFmpeg** for file format support.
- YAML for recipe structure.

### Future Stack

- **Web app** version using Web Audio API + Python backend (FastAPI).
- **Node.js/React** possible for high-performance UI.

### File Structure

/context/ — Master context & AI prompt files
/assets/ — Logos, branding, UI elements
/samples/ — Built-in and user-uploaded samples
/app/ — Core Python code (UI + audio engine)
/out/ — Generated tracks & stems

markdown
Copy code

### Coding Conventions

- Use **clear, commented functions**.
- Keep **AI logic** separate from **audio processing**.
- Use **config files** for adjustable parameters.

---

## 7. UX & Branding Guidelines

- **Tone:** Cool, edgy, light humour. Playful without being distracting.
- **Aesthetic:** Sleek creative dashboard with music + dev culture blend.
- **Color palette:** Dark theme with accent colors for genres/tools.
- **Metaphors in UI:**
  - “Mixing pot” for combining tracks.
  - “Recipe” for YAML instructions.
  - “Prompt influencers” as “seasoning” sliders.
- **Feedback style:** Friendly, metaphor-rich guidance.
  - Example: “We just sprinkled some extra reverb dust on that snare!”

---

## 8. Development Guidelines for AI Agents

- **Always respect real-time playback** as a core user expectation.
- **Never break** backward compatibility for YAML recipe format.
- **When adding features**, include a demo recipe for testing.
- **Ask for missing info** if user prompt is too vague.
- Include **unit tests** for audio functions.
- Validate that exported files are playable before finalizing.

---

## 9. Roadmap

### Phase 1 — MVP

- Prompt → recipe → track pipeline.
- Style presets & prompt influencers.
- Sample import + built-in packs.
- Real-time playback.

### Phase 2 — Advanced Editing

- FX automation, reverb, tempo changes.
- AI-assisted mastering.

### Phase 3 — Platform Expansion

- Web app version.
- Discord/Twitch integration.
- Marketplace for plugins/sample packs.

### Phase 4 — Monetization

- Paid pro tier (exclusive sample packs, more AI models).
- Plugin marketplace.
- Branded content packs.

---

## 10. Example Code Pattern (Prompt → Recipe → Audio)

```python
from pydub import AudioSegment

def apply_fx(segment, fx):
    if 'gain_db' in fx:
        segment = segment + fx['gain_db']
    if 'pan' in fx:
        segment = segment.pan(fx['pan'])
    return segment

def build_track(recipe):
    track = AudioSegment.silent(duration=recipe['duration'] * 1000)
    for layer in recipe['layers']:
        sample = AudioSegment.from_file(layer['source'])
        sample = apply_fx(sample, layer.get('fx', {}))
        track = track.overlay(sample, position=layer['start_ms'])
    return track
```

## 11. Prompt Examples for Users

“Lo-fi hip hop loop with vinyl crackle and soft piano chords.”

“Fast techno beat with glitchy vocal chops and sub bass.”

“Ambient drone with slow build and deep reverb.”
