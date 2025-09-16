"""Gradio user interface for Synthtax."""

from __future__ import annotations

import base64
import io
import os
import random
import re
import uuid
from typing import Dict, List, Tuple

import gradio as gr
import yaml

from .engine import build_track, generate_recipe_from_prompt


DEFAULT_PROMPT = "Ambient soundscape with soft pads and long reverb"
DEFAULT_BPM = 120
DEFAULT_HAT = "Pocket groove"
DEFAULT_PAD = "Warm sine"
DEFAULT_BARS = 8
DEFAULT_REVERB = True
DEFAULT_GAIN = -1.0
DEFAULT_NORMALIZE = True

HAT_PATTERNS: Dict[str, str] = {
    "Minimal pulses": "x---------------",
    "Half-time sway": "x---x---x---x---",
    DEFAULT_HAT: "x-x---x-x---x-x-",
    "Steady driver": "x-x-x-x-x-x-x-x-",
    "Full shimmer": "xxxxxxxxxxxxxxxx",
}

PAD_WAVES: Dict[str, str] = {
    DEFAULT_PAD: "sine",
    "Airy triangle": "triangle",
    "Bright saw": "saw",
    "Retro square": "square",
}

PRESETS: List[Dict[str, object]] = [
    {
        "label": "Deep Space Drift",
        "prompt": "Floating pads, gentle pulses, stars shimmering in the distance",
        "bpm": 78,
        "hat": "Minimal pulses",
        "pad": DEFAULT_PAD,
        "bars": 8,
        "reverb": True,
        "gain": -2.0,
        "normalize": True,
    },
    {
        "label": "Neon Arcade",
        "prompt": "Retro synthwave lead, punchy kick, arcade shimmer",
        "bpm": 118,
        "hat": "Steady driver",
        "pad": "Retro square",
        "bars": 8,
        "reverb": False,
        "gain": -1.5,
        "normalize": True,
    },
    {
        "label": "Sunset Pop",
        "prompt": "Feel-good pop groove, palm-muted guitars, bright claps",
        "bpm": 104,
        "hat": "Half-time sway",
        "pad": "Airy triangle",
        "bars": 8,
        "reverb": True,
        "gain": -1.0,
        "normalize": True,
    },
    {
        "label": "Club Accelerator",
        "prompt": "High energy dance floor, relentless hats, bold bass swells",
        "bpm": 128,
        "hat": "Full shimmer",
        "pad": "Bright saw",
        "bars": 8,
        "reverb": False,
        "gain": -0.5,
        "normalize": True,
    },
    {
        "label": "Lo-fi Glow",
        "prompt": "Lo-fi chillhop beat, vinyl crackle, shimmering keys",
        "bpm": 92,
        "hat": "Half-time sway",
        "pad": DEFAULT_PAD,
        "bars": 8,
        "reverb": True,
        "gain": -2.5,
        "normalize": True,
    },
]

RANDOM_POOL: List[Dict[str, object]] = PRESETS + [
    {
        "label": "Aurora Voices",
        "prompt": "Celestial choir, glittering textures, slow-motion crescendo",
        "bpm": 84,
        "hat": "Minimal pulses",
        "pad": "Airy triangle",
        "bars": 12,
        "reverb": True,
        "gain": -2.0,
        "normalize": True,
    },
    {
        "label": "Future Bounce",
        "prompt": "Playful future bass chords, chopped vox, sidechain energy",
        "bpm": 136,
        "hat": "Full shimmer",
        "pad": "Bright saw",
        "bars": 8,
        "reverb": False,
        "gain": -1.0,
        "normalize": True,
    },
    {
        "label": "Rainy Window",
        "prompt": "Soft piano droplets, mellow kick, hazy evening vibes",
        "bpm": 90,
        "hat": "Minimal pulses",
        "pad": DEFAULT_PAD,
        "bars": 8,
        "reverb": True,
        "gain": -2.2,
        "normalize": True,
    },
]

MAX_HISTORY = 6
NO_HISTORY_MESSAGE = "_No mixes yet. Tap **Preview mix** to kick off your creative timeline._"

CUSTOM_CSS = """
.gradio-container {
    font-family: "Inter", "Segoe UI", system-ui, -apple-system, BlinkMacSystemFont, sans-serif;
    background: radial-gradient(circle at 0% 0%, #f5f7ff 0%, #eef2ff 40%, #e0ecff 100%);
    color: #0f172a;
}

.hero-card {
    background: linear-gradient(135deg, rgba(67, 83, 255, 0.12), rgba(17, 25, 84, 0.16));
    border-radius: 1rem;
    padding: 1.25rem 1.5rem;
    box-shadow: 0 20px 45px rgba(15, 23, 42, 0.08);
}

.hero-card h1 {
    font-size: 1.85rem;
    margin-bottom: 0.35rem;
}

.hero-card p {
    margin: 0;
    font-size: 1rem;
    line-height: 1.5;
}

.layout-row {
    gap: 1.5rem !important;
    align-items: stretch;
}

.control-panel,
.output-panel {
    background: rgba(255, 255, 255, 0.82);
    border-radius: 1.1rem;
    padding: 1.5rem;
    box-shadow: 0 15px 35px rgba(15, 23, 42, 0.08);
}

.control-panel .gradio-row {
    gap: 0.75rem !important;
}

.preset-row .gr-button {
    border-radius: 999px !important;
    border: none;
    background: rgba(67, 83, 255, 0.1);
    color: #0f172a;
}

.preset-row .gr-button:hover {
    background: rgba(67, 83, 255, 0.18);
}

.waveform-card {
    background: rgba(15, 23, 42, 0.04);
    border-radius: 0.9rem;
    padding: 1rem;
    border: 1px solid rgba(67, 83, 255, 0.12);
}

.waveform-card button {
    margin-top: 0.75rem;
    background: #4353ff;
    color: white;
    border: none;
    padding: 0.55rem 1.25rem;
    border-radius: 999px;
    font-weight: 600;
    cursor: pointer;
}

.waveform-card button:hover,
.waveform-card button:focus {
    background: #2f3ecf;
}

#history-log {
    max-height: 260px;
    overflow-y: auto;
    padding-right: 0.75rem;
}

#history-log::-webkit-scrollbar {
    width: 8px;
}

#history-log::-webkit-scrollbar-thumb {
    background: rgba(67, 83, 255, 0.35);
    border-radius: 999px;
}

.history-list {
    list-style: none;
    margin: 0;
    padding-left: 0;
}

.history-list li {
    margin-bottom: 0.5rem;
    padding: 0.6rem 0.75rem;
    background: rgba(67, 83, 255, 0.08);
    border-radius: 0.75rem;
    line-height: 1.4;
}

@media (max-width: 980px) {
    .layout-row {
        flex-direction: column;
    }
}
"""


def _waveform_html(audio_b64: str) -> str:
    """Return accessible HTML/JS for a waveform visualizer using WaveSurfer."""

    uid = uuid.uuid4().hex
    waveform_id = f"waveform-{uid}"
    button_id = f"play-{uid}"
    script_flag = "data-synthtax-wavesurfer"

    return f"""
    <div class='waveform-card' role='group' aria-label='Preview waveform and transport controls'>
        <div id='{waveform_id}' class='waveform' aria-hidden='true'></div>
        <button id='{button_id}' type='button' aria-label='Play preview audio' aria-pressed='false'>Play</button>
    </div>
    <script>
    (function() {{
        const init = () => {{
            const wavesurfer = window.WaveSurfer.create({{
                container: '#{waveform_id}',
                waveColor: '#9db4ff',
                progressColor: '#4353ff',
                cursorColor: '#1d2cff',
                height: 96,
                responsive: true,
            }});
            wavesurfer.load('data:audio/wav;base64,{audio_b64}');
            const control = document.getElementById('{button_id}');
            const updateState = () => {{
                const playing = wavesurfer.isPlaying();
                control.setAttribute('aria-pressed', playing ? 'true' : 'false');
                control.textContent = playing ? 'Pause' : 'Play';
            }};
            control.addEventListener('click', () => {{
                wavesurfer.playPause();
                updateState();
            }});
            wavesurfer.on('finish', () => {{
                control.setAttribute('aria-pressed', 'false');
                control.textContent = 'Play';
            }});
        }};

        if (window.WaveSurfer) {{
            init();
            return;
        }}

        let script = document.querySelector('script[{script_flag}]');
        if (script) {{
            script.addEventListener('load', () => init(), {{ once: true }});
            return;
        }}
        script = document.createElement('script');
        script.src = 'https://unpkg.com/wavesurfer.js';
        script.async = true;
        script.setAttribute('{script_flag}', 'true');
        script.addEventListener('load', () => init(), {{ once: true }});
        document.body.appendChild(script);
    }})();
    </script>
    """


def _assemble_recipe(
    prompt: str,
    bpm: int,
    hat_label: str,
    pad_label: str,
    bars: int,
    reverb: bool,
    gain_db: float,
    normalize: bool,
) -> Dict:
    """Return a recipe that blends prompt-based defaults with UI overrides."""

    recipe = generate_recipe_from_prompt(prompt, override_bpm=bpm)
    recipe["bars"] = bars
    recipe["pad_reverb"] = bool(reverb)
    hat_pattern = HAT_PATTERNS.get(hat_label, HAT_PATTERNS[DEFAULT_HAT])
    pad_wave = PAD_WAVES.get(pad_label, PAD_WAVES[DEFAULT_PAD])

    for layer in recipe.get("layers", []):
        if layer.get("name") == "hat":
            layer["pattern"] = hat_pattern
        if layer.get("name") == "pad":
            layer["wave"] = pad_wave
            layer["bars"] = bars

    fx = recipe.setdefault("master_fx", {})
    fx["gain_db"] = gain_db
    fx["normalize"] = bool(normalize)

    return recipe


def _format_duration_ms(duration_ms: int) -> str:
    seconds = max(duration_ms / 1000.0, 0.0)
    return f"{seconds:.1f}s"


def _update_history(
    history: List[Dict[str, object]] | None,
    prompt: str,
    bpm: int,
    hat_label: str,
    pad_label: str,
    bars: int,
    reverb: bool,
    gain_db: float,
    normalize: bool,
    duration_ms: int,
    action: str,
) -> List[Dict[str, object]]:
    """Return history with a new entry prepended."""

    entries: List[Dict[str, object]] = list(history or [])
    title = prompt.strip() or "Untitled mix"
    entry = {
        "title": title,
        "action": action,
        "bpm": bpm,
        "hat": hat_label,
        "pad": pad_label,
        "bars": bars,
        "reverb": bool(reverb),
        "gain": float(gain_db),
        "normalize": bool(normalize),
        "duration": _format_duration_ms(duration_ms),
    }
    entries.insert(0, entry)
    return entries[:MAX_HISTORY]


def _history_markdown(history: List[Dict[str, object]] | None) -> str:
    if not history:
        return NO_HISTORY_MESSAGE

    lines = ["<ul class='history-list'>"]
    for item in history:
        reverb_text = "Reverb" if item.get("reverb") else "Dry mix"
        gain = item.get("gain", 0.0)
        gain_text = f" · {gain:+.1f} dB" if gain else ""
        normalize = " · Auto-level" if item.get("normalize") else " · Raw levels"
        lines.append(
            "<li>"
            f"<strong>{item.get('action', 'Previewed')}</strong> — "
            f"{item.get('title', 'Untitled mix')}<br />"
            f"{item.get('bpm')} BPM · {item.get('bars')} bars · {item.get('hat')} hats · "
            f"{item.get('pad')} pad · {reverb_text} · {item.get('duration')}{gain_text}{normalize}"
            "</li>"
        )
    lines.append("</ul>")
    return "\n".join(lines)


def _safe_filename(name: str) -> str:
    slug = re.sub(r"[^a-zA-Z0-9]+", "-", name.strip().lower()).strip("-")
    if not slug:
        slug = "synthtax-mix"
    return f"{slug}.wav"


def _unique_output_path(directory: str, filename: str) -> str:
    path = os.path.join(directory, filename)
    if not os.path.exists(path):
        return path
    stem, ext = os.path.splitext(filename)
    index = 1
    while True:
        candidate = os.path.join(directory, f"{stem}-{index}{ext}")
        if not os.path.exists(candidate):
            return candidate
        index += 1


def _preview_from_prompt(
    prompt: str,
    bpm: int,
    hat_label: str,
    pad_label: str,
    bars: int,
    reverb: bool,
    gain_db: float,
    normalize: bool,
    history: List[Dict[str, object]] | None,
) -> Tuple[Tuple[int, bytes], str, str, str, List[Dict[str, object]]]:
    """Build track and return audio bytes, YAML recipe, visualizer, history text and state."""

    recipe = _assemble_recipe(prompt, bpm, hat_label, pad_label, bars, reverb, gain_db, normalize)
    track = build_track(recipe)
    buf = io.BytesIO()
    track.export(buf, format="wav")
    audio_bytes = buf.getvalue()
    audio_b64 = base64.b64encode(audio_bytes).decode("ascii")
    history_entries = _update_history(
        history,
        prompt,
        bpm,
        hat_label,
        pad_label,
        bars,
        reverb,
        gain_db,
        normalize,
        len(track),
        "Previewed",
    )
    return (
        (track.frame_rate, audio_bytes),
        yaml.safe_dump(recipe, sort_keys=False, indent=2),
        _waveform_html(audio_b64),
        _history_markdown(history_entries),
        history_entries,
    )


def _export_from_prompt(
    prompt: str,
    bpm: int,
    hat_label: str,
    pad_label: str,
    bars: int,
    reverb: bool,
    gain_db: float,
    normalize: bool,
    mix_name: str,
    history: List[Dict[str, object]] | None,
) -> Tuple[str, str, List[Dict[str, object]]]:
    """Render and export the track, returning the file path and updated history."""

    recipe = _assemble_recipe(prompt, bpm, hat_label, pad_label, bars, reverb, gain_db, normalize)
    track = build_track(recipe)
    out_dir = "out"
    os.makedirs(out_dir, exist_ok=True)
    filename = _safe_filename(mix_name or "synthtax-mix")
    out_path = _unique_output_path(out_dir, filename)
    track.export(out_path, format="wav")
    history_entries = _update_history(
        history,
        prompt,
        bpm,
        hat_label,
        pad_label,
        bars,
        reverb,
        gain_db,
        normalize,
        len(track),
        "Exported",
    )
    return out_path, _history_markdown(history_entries), history_entries


def _preset_outputs(preset: Dict[str, object]) -> Tuple[object, ...]:
    return (
        preset.get("prompt", DEFAULT_PROMPT),
        int(preset.get("bpm", DEFAULT_BPM)),
        preset.get("hat", DEFAULT_HAT),
        preset.get("pad", DEFAULT_PAD),
        int(preset.get("bars", DEFAULT_BARS)),
        bool(preset.get("reverb", DEFAULT_REVERB)),
        float(preset.get("gain", DEFAULT_GAIN)),
        bool(preset.get("normalize", DEFAULT_NORMALIZE)),
    )


def _randomize_controls() -> Tuple[object, ...]:
    return _preset_outputs(random.choice(RANDOM_POOL))


def launch_app() -> gr.Blocks:
    """Return the Gradio Blocks app."""

    with gr.Blocks(theme=gr.themes.Soft(), css=CUSTOM_CSS, title="Synthtax Studio") as demo:
        history_state = gr.State([])

        gr.HTML(
            """
            <div class="hero-card">
                <h1>🎛️ Synthtax Studio</h1>
                <p>Craft expressive text-to-groove mixes. Describe the vibe, dial in the energy and export a ready-to-share loop.</p>
            </div>
            """
        )

        with gr.Row(elem_classes="layout-row"):
            with gr.Column(scale=1, elem_classes="control-panel"):
                gr.Markdown(
                    "### Tell Synthtax the vibe\nBlend styles, textures and moods. The controls help you fine-tune the mix."
                )
                prompt = gr.Textbox(
                    label="Describe your vibe",
                    value=DEFAULT_PROMPT,
                    placeholder="e.g. Dreamy pads with gentle percussion and sparkling delays",
                    lines=4,
                    info="Tips: mention instruments, dynamics or specific references to guide the recipe.",
                    autofocus=True,
                )
                with gr.Row():
                    bpm = gr.Slider(
                        minimum=60,
                        maximum=160,
                        value=DEFAULT_BPM,
                        step=1,
                        label="Tempo (BPM)",
                    )
                    bars = gr.Slider(
                        minimum=4,
                        maximum=16,
                        value=DEFAULT_BARS,
                        step=4,
                        label="Length (bars)",
                        info="Extend to explore longer evolving loops.",
                    )
                with gr.Row():
                    hat_style = gr.Dropdown(
                        choices=list(HAT_PATTERNS.keys()),
                        value=DEFAULT_HAT,
                        label="Hi-hat energy",
                    )
                    pad_wave = gr.Dropdown(
                        choices=list(PAD_WAVES.keys()),
                        value=DEFAULT_PAD,
                        label="Pad flavor",
                    )
                with gr.Row():
                    reverb_toggle = gr.Checkbox(
                        value=DEFAULT_REVERB,
                        label="Dream reverb",
                    )
                    normalize_toggle = gr.Checkbox(
                        value=DEFAULT_NORMALIZE,
                        label="Auto-level mix",
                    )
                gain = gr.Slider(
                    minimum=-6.0,
                    maximum=6.0,
                    value=DEFAULT_GAIN,
                    step=0.5,
                    label="Output gain (dB)",
                    info="Trim the loudness after normalization. Negative values keep headroom for mastering.",
                )
                mix_name = gr.Textbox(
                    label="Mix name for export",
                    value="synthtax_demo",
                    placeholder="Used as the WAV filename",
                )

                control_outputs = [
                    prompt,
                    bpm,
                    hat_style,
                    pad_wave,
                    bars,
                    reverb_toggle,
                    gain,
                    normalize_toggle,
                ]

                with gr.Row(elem_classes="preset-row"):
                    for preset in PRESETS:
                        gr.Button(preset["label"], variant="secondary").click(
                            lambda p=preset: _preset_outputs(p), outputs=control_outputs
                        )

                with gr.Row(elem_classes="preset-row"):
                    inspire_btn = gr.Button("Inspire me ✨", variant="secondary")
                    reset_btn = gr.Button("Reset controls", variant="secondary")
                    clear_btn = gr.Button("Clear prompt", variant="secondary")

                inspire_btn.click(_randomize_controls, outputs=control_outputs)
                reset_btn.click(
                    lambda: (
                        DEFAULT_PROMPT,
                        DEFAULT_BPM,
                        DEFAULT_HAT,
                        DEFAULT_PAD,
                        DEFAULT_BARS,
                        DEFAULT_REVERB,
                        DEFAULT_GAIN,
                        DEFAULT_NORMALIZE,
                    ),
                    outputs=control_outputs,
                )
                clear_btn.click(lambda: "", outputs=prompt)

                with gr.Row():
                    preview_btn = gr.Button("🎧 Preview mix", variant="primary")
                    export_btn = gr.Button("💾 Export WAV", variant="secondary")

                with gr.Accordion("Prompt playbook", open=False):
                    gr.Markdown(
                        """
                        * Combine genres: _"Ambient techno with glassy arps"_.
                        * Mention instruments: _"Lo-fi piano"_, _"analog bass"_, _"vocal chops"_.
                        * Describe transitions or mood shifts for evolving loops.
                        * Keep experimenting — every preview updates your creative history.
                        """
                    )

            with gr.Column(scale=1, elem_classes="output-panel"):
                gr.Markdown("### Listen & iterate")
                with gr.Tabs():
                    with gr.Tab("Preview"):
                        visual = gr.HTML(
                            value="<div class='waveform-card'>Preview to reveal the waveform visualizer.</div>",
                            elem_classes="visualizer",
                        )
                        audio = gr.Audio(label="Audio preview", interactive=False)
                    with gr.Tab("Recipe"):
                        code = gr.Code(
                            label="Recipe", language="yaml", value="# Preview to generate a recipe"
                        )
                    with gr.Tab("History"):
                        history_display = gr.Markdown(
                            value=NO_HISTORY_MESSAGE,
                            elem_id="history-log",
                        )
                file_out = gr.File(label="Download exported mix")
                gr.Markdown(
                    "_Exports are saved in the `out/` folder so you can layer them in your DAW or share with friends._"
                )

        preview_btn.click(
            _preview_from_prompt,
            inputs=[
                prompt,
                bpm,
                hat_style,
                pad_wave,
                bars,
                reverb_toggle,
                gain,
                normalize_toggle,
                history_state,
            ],
            outputs=[audio, code, visual, history_display, history_state],
        )
        export_btn.click(
            _export_from_prompt,
            inputs=[
                prompt,
                bpm,
                hat_style,
                pad_wave,
                bars,
                reverb_toggle,
                gain,
                normalize_toggle,
                mix_name,
                history_state,
            ],
            outputs=[file_out, history_display, history_state],
        )

    return demo


if __name__ == "__main__":  # pragma: no cover
    launch_app().launch()

