import io
import os
from typing import Dict, Any

from pydub import AudioSegment
from pydub.generators import Sine, WhiteNoise

# --- Helpers ---


def _builtin_sample(name: str) -> AudioSegment:
    """Return a simple synthesized AudioSegment for a builtin name."""
    if name == "drum":
        noise = WhiteNoise().to_audio_segment(duration=250)
        return noise.low_pass_filter(120)
    if name == "bass":
        return Sine(55).to_audio_segment(duration=1000)
    if name == "melody":
        return Sine(440).to_audio_segment(duration=1000)
    return AudioSegment.silent(duration=500)


# --- Core functions ---


def generate_recipe_from_prompt(prompt: str, style: str) -> Dict[str, Any]:
    """Return a simple hardcoded recipe based on prompt and style.

    This is a placeholder for future AI generation. For now the recipe does not
    actually depend on the prompt or style, but the parameters are accepted so
    the function signature stays stable.
    """
    return {
        "bpm": 90,
        "duration": 5000,  # milliseconds
        "layers": [
            {
                "source": "builtin:drum",
                "start_ms": 0,
                "fx": {"gain_db": -3},
            },
            {
                "source": "builtin:bass",
                "start_ms": 0,
                "fx": {"gain_db": -3},
            },
            {
                "source": "builtin:melody",
                "start_ms": 0,
                "fx": {"gain_db": -3},
            },
        ],
    }


def build_track(recipe: Dict[str, Any]) -> AudioSegment:
    """Build an AudioSegment from a recipe dictionary."""
    duration = recipe.get("duration", 0)
    track = AudioSegment.silent(duration=duration)

    for layer in recipe.get("layers", []):
        src = layer.get("source")
        seg = None
        if isinstance(src, str) and src.startswith("builtin:"):
            seg = _builtin_sample(src.split(":", 1)[1])
        elif src and os.path.exists(src):
            seg = AudioSegment.from_file(src)
        if seg is None:
            continue
        fx = layer.get("fx", {})
        gain = fx.get("gain_db")
        if gain is not None:
            seg = seg + gain
        start = int(layer.get("start_ms", 0))
        track = track.overlay(seg, position=start)

    return track


def play_preview(track: AudioSegment):
    """Return audio data suitable for Gradio preview."""
    import numpy as np

    buf = io.BytesIO()
    track.export(buf, format="wav")
    buf.seek(0)
    array = np.array(track.get_array_of_samples())
    if track.channels > 1:
        array = array.reshape((-1, track.channels))
    return track.frame_rate, array


def export_track(track: AudioSegment, out_path: str) -> str:
    """Export track to ``out_path`` as WAV. Returns the path."""
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    track.export(out_path, format="wav")
    return out_path
