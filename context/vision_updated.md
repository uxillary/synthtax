# SYNTHTAX — Vision & Context

**Goal:** make remixing feel like coding. *Synthtax* is a code-first, live-coding friendly sampler/mixer where lines of code shape stems, loops, and effects in real time—while remaining accessible to non-coders.

---

## Product pillars

- **Code is the DAW:** a tiny DSL (“Synthtax”) controls playback, stems, loops, FX, and exports.
- **Live-coding performance:** code updates recompile instantly; the UI pulses on-beat; audience mode shows code + reactive visuals.
- **Accessible on-ramp:** buttons and presets insert code snippets; you can click to add common actions, then learn by reading the generated code.
- **AI-assisted workflow:** optional prompts generate “recipes” (code + YAML) that structure a mix; future: stem classification and groove suggestions.

---

## Current UI (baseline)

- **Prompt** input (e.g., *“Ambient soundscape with soft pads and long reverb”*)
- **Style Presets:** Ambient / Synth / Pop / Dance (to insert recipe snippets)
- **Preview** button → renders a quick mixdown for audition
- **Export** button → renders full-quality wav
- Panels: **Preview (audio)**, **Recipe (code)**, **Download (link)**

---

## High-level flow

1. **Input**
   - Upload audio (track or samples) → optional stem separation.
   - Or start empty and load one-shots/loops.
2. **Recipe**
   - User types Synthtax code or clicks a preset → code appears in the Recipe panel.
3. **Render (Preview)**
   - The code compiles to a processing graph (segments, operations, effects).
   - Fast render for preview (low-latency, reduced quality if needed).
4. **Export**
   - Full-quality render (WAV) and downloadable file.
5. **Iterate / Perform**
   - Editing code re-renders on the next bar (quantized) for smooth live updates.

---

## Minimum Viable Feature Set (v0.1)

- Load WAV/MP3.
- Basic **operations**: `play`, `mute`, `solo`, `gain`, `pan`, `fadeIn`, `fadeOut`, `loop`, `trim(bars=..)`.
- Basic **FX**: `reverb(amount)`, `delay(time, feedback)`, `lowpass(freq)`, `highpass(freq)`, `pitch(semis)`.
- **Time model**: tempo (BPM), bars/beats timeline; bar-quantized live updates.
- **Preview** (fast) and **Export** (quality) paths.
- **Preset buttons** insert working code snippets into Recipe.

---

## Nice-to-have (v0.2–v0.3)

- **Stem separation** (vocals/drums/bass/other) via Spleeter or MDX (offline optional).
- **Groove tools**: `quantize`, `humanize`, `swing`.
- **Takes & scenes** for performance (A/B sections).
- **Audience mode**: large code + audio-reactive visuals (ASCII/waveforms).
- **MIDI/keystroke triggers** to run code blocks live.

---

## The Synthtax DSL (draft)

### Concepts

- **Track**: a named audio source (uploaded file or separated stem).
- **Region**: a time slice of a track.
- **FX chain**: ordered effects applied to a track/region.
- **Global**: tempo, key, length.

### Grammar (informal)

```synthtax
set(bpm=90, key="Dm")

load drums from "drums.wav"
load vox   from "song.wav#vocals"   # stem selector syntax (future)
load pad   from "pad.wav"

# timeline ops
loop(drums, bars=8)
gain(drums, -3dB)
lowpass(drums, 900)

play(vox, at=bar(5))
fadeIn(vox, 4s)
reverb(vox, 0.35)

# regions
region r1 = slice(pad, start=bar(1), end=bar(9))
pitch(r1, -3)
delay(r1, 1/4, feedback=0.35, mix=0.25)

export("mixdown.wav")
```

### Ergonomics

- Units: `s`, `ms`, `bar()`, `beat()`, dB (`-6dB`), semitones.
- Autocomplete for function names and track identifiers.
- Errors return **inline hints** and offer **auto-fixes** (e.g., suggest nearest track name).

---

## Preset “styles” (insertable code)

**Ambient**

```synthtax
set(bpm=70, key="Cmaj")
gain(master, -3dB)
reverb(master, 0.45)
lowpass(master, 6000)

fadeIn(pad, 6s)
loop(pad, bars=16)
delay(pad, 1/8, feedback=0.25, mix=0.2)

sidechain(pad, to=drums, depth=0.2)   # future
```

**Synth**

```synthtax
set(bpm=100, key="Am")
loop(drums, bars=8)
gain(drums, -2dB)
highpass(drums, 120)

arpeggiate(synth, rate=1/8, span=7)   # future helper
reverb(synth, 0.25)
```

---

## YAML “Recipe” (optional companion)

Users can store presets or longer arrangements in YAML; your UI can sync YAML ↔ code.

```yaml
version: 0.1
global:
  bpm: 90
  key: Dm
tracks:
  drums: {path: "drums.wav"}
  vox:   {path: "song.wav#vocals"}   # future stem selector
  pad:   {path: "pad.wav"}
ops:
  - loop: {track: drums, bars: 8}
  - gain: {track: drums, db: -3}
  - lowpass: {track: drums, freq: 900}
  - play: {track: vox, at: bar(5)}
  - fadeIn: {track: vox, seconds: 4}
  - reverb: {track: vox, amount: 0.35}
  - region:
      name: r1
      of: pad
      start: bar(1)
      end: bar(9)
  - pitch: {target: r1, semis: -3}
  - delay: {target: r1, time: 0.5, feedback: 0.35, mix: 0.25}
export:
  file: mixdown.wav
```

---

## Tech plan (matches current requirements)

**Runtime & UI**

- **Gradio** for rapid UI: file upload, code editor (textbox), preview player, download link.
- **Python core** for audio graph + rendering.
- **pydub + numpy** for slicing/concats/gain/pan; custom simple FX (1st-order filters, delay); later: `scipy` / `ffmpeg` for quality.
- **pyyaml** for recipe import/export.
- **openai** (optional) to turn text prompts into code/YAML recipes (“Ambient with long reverb” → Synthtax).

**Optional add-ons**

- **Spleeter/MDX** (separate install) wrapped behind a feature flag for stem splitting.
- **FFmpeg** on system for robust decode/encode.

---

## Module sketch

```
/synthtax
  /core
    time.py          # bars/beats <-> seconds
    parser.py        # parse Synthtax to ops
    graph.py         # build processing graph
    audio.py         # load/save, resample, mix (pydub/numpy)
    fx.py            # reverb/delay/filters/pitch (basic)
    render.py        # preview vs export renderers
  /io
    yaml_io.py       # YAML <-> ops
    stems.py         # optional stem separation
  /ui
    app.py           # gradio interface
    snippets.py      # preset code/YAML inserts
```

---

## Data flow

1. **UI input** → (files, prompt, preset)  
2. **Prompt → (OpenAI)** → suggested Synthtax/YAML (optional)  
3. **Parser** → ops list → **Graph**  
4. **Renderer** → preview buffer (fast) or export WAV (HQ)  
5. **UI** shows **Preview** audio and **Download** link.

---

## Rendering strategy

- **Preview:** downsample to 22.05/32 kHz, lighter reverb tails, fixed-latency delay.
- **Export:** source rate, higher-order filters, full tails, dithering.

---

## Live-coding behavior

- Buffer timeline in bars; apply code edits at next bar boundary.
- Visual beat indicator; highlight active lines (ops) while they run.
- Safe reload: validate new graph; if valid, swap at boundary; otherwise keep current graph and show error.

---

## Risks & constraints

- Pydub’s simplicity vs effect quality—acceptable for v0.1; plan a DSP upgrade path.
- Stem separation is heavy; keep it optional/offline.
- Browser autoplay policies (if Gradio runs in browser)—ensure user interaction unlocks audio.

---

## Roadmap (condensed)

**v0.1**: core ops/FX, preview/export, presets, error hints.  
**v0.2**: stem splitting, scenes (A/B), swing/quantize, audience mode.  
**v0.3**: MIDI/keystroke triggers, better DSP, effect automation (`automate(param, curve)`), clip launcher.  
**v0.4**: collaboration (share recipes), package as desktop app (PyInstaller) or web+backend hybrid.

---

## Requirements (current)

```
pydub
pyyaml
gradio
openai
numpy
```

*(Optional later: spleeter, scipy, ffmpeg on path)*

---

## Definition of Done (v0.1)

- Can upload at least one file, write a small recipe, preview changes, and export a WAV.
- Preset buttons insert valid, audible recipes.
- Errors are readable and point to fixes.
- Code edits are audible within one bar of playback.

---

## Example end-to-end (copy into Recipe and run)

```synthtax
set(bpm=84, key="Gm")
load drums from "kit.wav"
load pad   from "pad.wav"
loop(drums, bars=8)
gain(drums, -2dB)
lowpass(drums, 1000)

fadeIn(pad, 4s)
loop(pad, bars=16)
reverb(pad, 0.4)
delay(pad, 1/8, feedback=0.3, mix=0.2)

export("demo_mix.wav")
```
