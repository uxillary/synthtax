from typing import Optional

import gradio as gr
import numpy as np

from core import parser, render

PRESETS = {
    "Ambient Drift": {
        "recipe": """set(bpm=80, key=\"C\")\nload main from \"uploaded\"\nreverb(main, amount=0.7)\ngain(main, -3)\nexport(\"ambient_mix.wav\")""",
        "description": "Float through airy pads with long echoes for calm and spacious textures.\n\n- Tempo: 80 BPM in C\n- Wide reverb wash\n- Gentle gain dip for smooth dynamics",
    },
    "Neon Pulse": {
        "recipe": """set(bpm=100, key=\"Dm\")\nload main from \"uploaded\"\nloop(main, bars=2)\nreverb(main, amount=0.5)\nexport(\"synth_mix.wav\")""",
        "description": "Layered synthwave bounce with a tight loop and shimmering tails.\n\n- Tempo: 100 BPM in D minor\n- Two-bar looping motif\n- Polished ambience for neon shimmer",
    },
    "Sunny Pop": {
        "recipe": """set(bpm=120, key=\"G\")\nload main from \"uploaded\"\ngain(main, 5)\nexport(\"pop_mix.wav\")""",
        "description": "Brighten your hooks with an upbeat tempo boost and polished gain stage.\n\n- Tempo: 120 BPM in G\n- Forward vocals and leads\n- Clean export with extra sparkle",
    },
    "Night Runner": {
        "recipe": """set(bpm=128, key=\"F#m\")\nload main from \"uploaded\"\nloop(main, bars=4)\ngain(main, 2)\nexport(\"dance_mix.wav\")""",
        "description": "High-energy club feel with extended loops and a confident lift in loudness.\n\n- Tempo: 128 BPM in F# minor\n- Four-bar repeating driver\n- Volume push to own the floor",
    },
    "Remix Spark": {
        "recipe": """set(bpm=100, key=\"Am\")\nload vox from \"uploaded\"\nslice(vox, start=0, duration=16000)\nloop(vox, bars=4)\nbeat(drums, style=\"hiphop\", bars=4)\ngain(drums, -2)\nexport(\"remix_flip.wav\")""",
        "description": "Jump-start a remix with a looped vocal slice riding over a ready-made hip-hop beat.\n\n- Tempo: 100 BPM in A minor\n- Auto-generated drums in hip-hop style\n- Quick stem loop for chopping inspiration",
    },
}

DEFAULT_PRESET = "Ambient Drift"
DEFAULT_RECIPE = PRESETS[DEFAULT_PRESET]["recipe"]

THEME = gr.themes.Soft(
    primary_hue="violet",
    secondary_hue="blue",
    neutral_hue="slate",
).set(
    body_background_fill="#0f172a",
    body_text_color="#e2e8f0",
    block_background_fill="#1e293b",
    block_border_color="#334155",
    shadow_drop="0 12px 40px rgba(15, 23, 42, 0.45)",
    button_primary_background_fill="#7c3aed",
    button_primary_background_fill_hover="#6d28d9",
    button_primary_text_color="#f8fafc",
    button_secondary_background_fill="#334155",
    button_secondary_background_fill_hover="#1e293b",
    button_secondary_text_color="#e2e8f0",
)

CSS = """
:root {color-scheme: dark;}
body {background-color: #0f172a; color: #e2e8f0;}
.gradio-container {max-width: 1100px !important; margin: 0 auto; color: #e2e8f0;}
.gradio-container .gr-block, .gradio-container .gr-panel {background-color: transparent;}
.gradio-container .gr-box, .gradio-container .gr-accordion, .gradio-container .gr-panel, .gradio-container .gr-form {background-color: #1e293b; border-color: #334155;}
.gradio-container label, .gradio-container .gr-markdown {color: #e2e8f0;}
.gradio-container .gr-markdown h1, .gradio-container .gr-markdown h2, .gradio-container .gr-markdown h3, .gradio-container .gr-markdown h4, .gradio-container .gr-markdown h5, .gradio-container .gr-markdown h6, .gradio-container .gr-markdown p, .gradio-container .gr-markdown li {color: #e2e8f0;}
.gradio-container input, .gradio-container textarea, .gradio-container select {background-color: #0b1120; color: #f8fafc; border-color: #334155;}
.gradio-container input::placeholder, .gradio-container textarea::placeholder {color: #94a3b8;}
.gradio-container .cm-editor, .gradio-container .cm-scroller {background-color: #0b1120 !important; color: #f8fafc !important;}
.gradio-container .cm-content {color: #f8fafc !important;}
.gradio-container .gr-button-primary {background-color: #7c3aed !important; border-color: #7c3aed !important; color: #f8fafc !important;}
.gradio-container .gr-button-primary:hover {background-color: #6d28d9 !important;}
.gradio-container .gr-button-secondary {background-color: #334155 !important; border-color: #475569 !important; color: #e2e8f0 !important;}
.gradio-container .gr-button-secondary:hover {background-color: #1e293b !important;}
.gradio-container .svelte-drum {color: #e2e8f0;}
.preset-description {min-height: 120px;}
.recipe-box textarea {font-size: 0.95rem;}
"""


def _preset_summary_text(name: Optional[str]) -> str:
    preset = PRESETS.get(name or "")
    if not preset:
        return "Select a preset to see what it does."
    return f"**{name}**\n\n{preset['description']}"


def _preset_summary(name: Optional[str]):
    return gr.Markdown.update(value=_preset_summary_text(name))


def _load_preset_recipe(name: Optional[str]):
    preset = PRESETS.get(name or "")
    if not preset:
        return gr.update()
    return preset["recipe"]


def _reset_workspace():
    return (
        None,
        DEFAULT_RECIPE,
        None,
        gr.update(value=""),
        None,
        gr.update(value=DEFAULT_PRESET),
        _preset_summary(DEFAULT_PRESET),
    )


def _segment_to_ndarray(seg):
    arr = np.array(seg.get_array_of_samples())
    if seg.channels == 2:
        arr = arr.reshape((-1, 2))
    return arr.astype(np.float32) / (1 << 15)


def preview_fn(file, recipe):
    try:
        cmds = parser.parse(recipe)
        seg = render.apply_commands(cmds, file.name if file else None, preview=True)
        return (seg.frame_rate, _segment_to_ndarray(seg)), recipe, None
    except Exception as e:
        return None, f"Error: {e}", None


def export_fn(file, recipe):
    try:
        cmds = parser.parse(recipe)
        output_path = render.apply_commands(cmds, file.name if file else None, preview=False)
        return None, recipe, output_path
    except Exception as e:
        return None, f"Error: {e}", None


def build_ui() -> gr.Blocks:
    with gr.Blocks(theme=THEME, css=CSS) as demo:
        gr.Markdown(
            """# 🎛️ Synthtax Studio\nDesign transformations for your tracks with readable audio recipes."""
        )
        with gr.Row(equal_height=True):
            with gr.Column(scale=1, min_width=320):
                gr.Markdown(
                    """### 1. Drop in audio\nUpload a stem or full mix to start reshaping your sound."""
                )
                audio_file = gr.File(label="Upload audio", file_types=["audio"])
                with gr.Accordion("Need a quick syntax tour?", open=False):
                    gr.Markdown(
                        """- `set(bpm=120, key=\"C\")` adjusts global tempo and key.\n- `load main from \"uploaded\"` grabs your uploaded file.\n- `beat(drums, style=\"house\", bars=4)` adds an auto-generated drum groove.\n- Effects like `reverb`, `gain`, and `loop` sculpt the vibe.\n- `export(\"mix.wav\")` saves the final bounce."""
                    )
                gr.Markdown(
                    """### 2. Choose a preset vibe\nExplore curated starting points before fine-tuning the recipe."""
                )
                preset_selector = gr.Radio(
                    choices=list(PRESETS.keys()),
                    value=DEFAULT_PRESET,
                    label="Preset",
                    info="Preview the description below, then load it into the editor when you're ready.",
                )
                preset_summary = gr.Markdown(
                    _preset_summary_text(DEFAULT_PRESET),
                    elem_classes=["preset-description"],
                )
                use_preset_btn = gr.Button("Use preset in editor", variant="secondary")
            with gr.Column(scale=2, min_width=480):
                gr.Markdown(
                    """### 3. Craft your recipe\nTweak the steps or write new ones to explore different sonic outcomes."""
                )
                recipe_box = gr.Code(
                    label="Recipe editor",
                    language="python",
                    value=DEFAULT_RECIPE,
                    elem_classes=["recipe-box"],
                    lines=12,
                )
                with gr.Row():
                    preview_btn = gr.Button("🎧 Preview mix", variant="secondary")
                    export_btn = gr.Button("💾 Export mix", variant="primary")
                    reset_btn = gr.Button("Reset workspace", variant="secondary")
                with gr.Row():
                    audio_out = gr.Audio(label="Preview audio", interactive=False)
                    recipe_out = gr.Code(label="Executed recipe", language="python", interactive=False)
                download_out = gr.File(label="Rendered file", interactive=False)
                gr.Markdown(
                    "Preview delivers a fast snippet for quick tweaks, while export renders the full track and unlocks the download link."
                )
        preset_selector.change(_preset_summary, preset_selector, preset_summary)
        use_preset_btn.click(_load_preset_recipe, preset_selector, recipe_box)
        preview_btn.click(
            preview_fn,
            inputs=[audio_file, recipe_box],
            outputs=[audio_out, recipe_out, download_out],
        )
        export_btn.click(
            export_fn,
            inputs=[audio_file, recipe_box],
            outputs=[audio_out, recipe_out, download_out],
        )
        reset_btn.click(
            _reset_workspace,
            inputs=None,
            outputs=[audio_file, recipe_box, audio_out, recipe_out, download_out, preset_selector, preset_summary],
        )
    return demo


if __name__ == "__main__":
    build_ui().launch()
