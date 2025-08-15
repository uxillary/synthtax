import gradio as gr
from pydub import AudioSegment

from .engine import (
    generate_recipe_from_prompt,
    build_track,
    play_preview,
    export_track,
)


STYLE_TEMPLATES = {
    "Ambient": "Ambient soundscape with soft pads and long reverb",
    "Synth": "Retro synthwave with arpeggios",
    "Pop": "Modern pop with catchy melodies",
    "Dance": "Upbeat dance track with heavy bass and bright leads",
}


def launch_app() -> gr.Blocks:
    with gr.Blocks(theme=gr.themes.Soft(primary_hue="slate"), css="body {background-color: #111; color: #eee}") as demo:
        gr.Markdown("## Synthtax Demo", elem_id="title")

        prompt = gr.Textbox(label="Prompt", lines=2)
        style_state = gr.State("")
        track_state = gr.State()

        with gr.Row():
            for name, template in STYLE_TEMPLATES.items():
                def _preset(template=template, name=name):
                    return template, name
                gr.Button(name).click(_preset, outputs=[prompt, style_state])

        audio_out = gr.Audio(label="Preview", interactive=False)

        def _preview(p, style):
            recipe = generate_recipe_from_prompt(p, style)
            track = build_track(recipe)
            data = play_preview(track)
            return data, track

        preview_btn = gr.Button("Preview")
        preview_btn.click(_preview, inputs=[prompt, style_state], outputs=[audio_out, track_state])

        def _export(track: AudioSegment):
            if track is None:
                raise gr.Error("Generate a preview first")
            return export_track(track, "out/demo.wav")

        export_btn = gr.Button("Export")
        file_out = gr.File(label="Download")
        export_btn.click(_export, inputs=track_state, outputs=file_out)

    return demo


if __name__ == "__main__":
    launch_app().launch()
