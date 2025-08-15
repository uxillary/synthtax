"""Minimal Gradio user interface for Synthtax."""

from __future__ import annotations

import io
import os
from typing import Tuple

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


def _preview_from_prompt(prompt: str) -> Tuple[Tuple[int, bytes], str]:
    """Build track from prompt and return audio bytes + YAML recipe."""

    recipe = generate_recipe_from_prompt(prompt)
    track = build_track(recipe)
    buf = io.BytesIO()
    track.export(buf, format="wav")
    audio_bytes = buf.getvalue()
    return (track.frame_rate, audio_bytes), yaml.safe_dump(recipe)


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

    with gr.Blocks() as demo:
        prompt = gr.Textbox(label="Prompt", value=DEFAULT_PROMPT)

        with gr.Row():
            for label, text in PRESETS.items():
                def _set(t=text):
                    return t

                gr.Button(label).click(_set, outputs=prompt)

        preview_btn = gr.Button("Preview")
        export_btn = gr.Button("Export")

        audio = gr.Audio(label="Preview")
        code = gr.Code(label="Recipe", language="yaml")
        file_out = gr.File(label="Download")

        preview_btn.click(_preview_from_prompt, inputs=prompt, outputs=[audio, code])
        export_btn.click(_export_from_prompt, inputs=prompt, outputs=file_out)

    return demo


if __name__ == "__main__":  # pragma: no cover
    launch_app().launch()

