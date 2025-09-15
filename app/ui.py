"""Minimal Gradio user interface for Synthtax."""

from __future__ import annotations

import io
import os
import base64
from typing import Tuple
import random

import gradio as gr
import yaml

from .engine import generate_recipe_from_prompt, build_track


DEFAULT_PROMPT = "Ambient soundscape with soft pads and long reverb"

PRESETS = {
    "Ambient": DEFAULT_PROMPT,
    "Synth": "Synthwave arps, punchy kick, chorus pads",
    "Pop": "Bright pop beat, claps on 2/4, clean bass",
    "Dance": "Clubby 4/4 kick, driving hats, saw bass",
}


def _waveform_html(audio_b64: str) -> str:
    """Return HTML/JS for a waveform visualizer using WaveSurfer."""

    return f"""
    <div id='waveform'></div>
    <div class='controls'><button id='play' aria-label='Play or pause preview'>Play/Pause</button></div>
    <script src='https://unpkg.com/wavesurfer.js'></script>
    <script>
    const wavesurfer = WaveSurfer.create({{
        container: '#waveform',
        waveColor: '#d9dcff',
        progressColor: '#4353ff'
    }});
    wavesurfer.load('data:audio/wav;base64,{audio_b64}');
    document.getElementById('play').onclick = () => wavesurfer.playPause();
    </script>
    """


def _preview_from_prompt(prompt: str) -> Tuple[Tuple[int, bytes], str, str]:
    """Build track from prompt and return audio bytes, YAML recipe and visualizer."""

    recipe = generate_recipe_from_prompt(prompt)
    track = build_track(recipe)
    buf = io.BytesIO()
    track.export(buf, format="wav")
    audio_bytes = buf.getvalue()
    audio_b64 = base64.b64encode(audio_bytes).decode("ascii")
    return (track.frame_rate, audio_bytes), yaml.safe_dump(recipe), _waveform_html(audio_b64)


def _export_from_prompt(prompt: str) -> str:
    """Render and export the track to ``out/synthtax_demo.wav``."""

    recipe = generate_recipe_from_prompt(prompt)
    track = build_track(recipe)
    out_dir = "out"
    os.makedirs(out_dir, exist_ok=True)
    out_path = os.path.join(out_dir, "synthtax_demo.wav")
    track.export(out_path, format="wav")
    return out_path


def launch_app() -> gr.Blocks:
    """Return the Gradio Blocks app."""

    with gr.Blocks(theme=gr.themes.Soft()) as demo:
        gr.Markdown("# Synthtax\nDescribe a vibe and let the AI mix.")
        prompt = gr.Textbox(
            label="Prompt",
            value=DEFAULT_PROMPT,
            placeholder="Describe the vibe or mood",
        )

        with gr.Row():
            for label, text in PRESETS.items():
                def _set(t=text):
                    return t

                gr.Button(label).click(_set, outputs=prompt)
            gr.Button("Random").click(
                lambda: random.choice(list(PRESETS.values())), outputs=prompt
            )
            gr.Button("Clear").click(lambda: "", outputs=prompt)

        preview_btn = gr.Button("Preview")
        export_btn = gr.Button("Export")

        audio = gr.Audio(label="Preview")
        code = gr.Code(label="Recipe", language="yaml")
        visual = gr.HTML(label="Visualizer")
        file_out = gr.File(label="Download")

        preview_btn.click(
            _preview_from_prompt, inputs=prompt, outputs=[audio, code, visual]
        )
        export_btn.click(_export_from_prompt, inputs=prompt, outputs=file_out)

    return demo


if __name__ == "__main__":  # pragma: no cover
    launch_app().launch()

