import gradio as gr
import numpy as np
from core import parser, render

PRESETS = {
    "Ambient": """set(bpm=80, key=\"C\")\nload main from \"uploaded\"\nreverb(main, amount=0.7)\ngain(main, -3)\nexport(\"ambient_mix.wav\")""",
    "Synth": """set(bpm=100, key=\"Dm\")\nload main from \"uploaded\"\nloop(main, bars=2)\nreverb(main, amount=0.5)\nexport(\"synth_mix.wav\")""",
    "Pop": """set(bpm=120, key=\"G\")\nload main from \"uploaded\"\ngain(main, 5)\nexport(\"pop_mix.wav\")""",
    "Dance": """set(bpm=128, key=\"F#m\")\nload main from \"uploaded\"\nloop(main, bars=4)\ngain(main, 2)\nexport(\"dance_mix.wav\")""",
}


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
    with gr.Blocks() as demo:
        gr.Markdown("# Synthtax")
        audio_file = gr.File(label="Upload", file_types=["audio"])
        recipe_box = gr.Code(label="Recipe", language="python")
        with gr.Row():
            for name, preset in PRESETS.items():
                gr.Button(name).click(lambda p=preset: p, None, recipe_box)
        with gr.Row():
            preview_btn = gr.Button("Preview")
            export_btn = gr.Button("Export")
        with gr.Row():
            audio_out = gr.Audio(label="Preview")
            recipe_out = gr.Code(label="Recipe")
            download_out = gr.File(label="Download")
        preview_btn.click(preview_fn, inputs=[audio_file, recipe_box], outputs=[audio_out, recipe_out, download_out])
        export_btn.click(export_fn, inputs=[audio_file, recipe_box], outputs=[audio_out, recipe_out, download_out])
    return demo


if __name__ == "__main__":
    build_ui().launch()
