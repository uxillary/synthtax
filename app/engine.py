"""Core audio engine for Synthtax.

This module turns a free-form text prompt into a simple recipe dictionary and
renders the recipe to an :class:`pydub.AudioSegment` using only synthesized
tones and noises.  The goal is not to be a full blown DAW but to provide a
minimal, musical "prompt -> recipe -> audio" pipeline that works without any
external samples or dependencies beyond ``pydub``.

The functions here purposely keep the implementation compact and commented so
it is easy to understand and extend in later iterations of the project.
"""

from __future__ import annotations

from typing import Dict

from pydub import AudioSegment, effects
from pydub.generators import (
    Sine,
    Square,
    Sawtooth,
    Triangle,
    WhiteNoise,
)


# ---------------------------------------------------------------------------
# Helper synthesis utilities


def beats_to_ms(beats: float, bpm: float) -> float:
    """Convert ``beats`` at ``bpm`` to milliseconds."""

    return (60_000 / bpm) * beats


def env_fade(seg: AudioSegment, attack_ms: int = 2, release_ms: int = 10) -> AudioSegment:
    """Apply a simple attack/release envelope via fades."""

    return seg.fade_in(int(attack_ms)).fade_out(int(release_ms))


def make_kick(ms: int = 120, freq_start: float = 120, freq_end: float = 45, vol_db: float = 0) -> AudioSegment:
    """Very small synthesized kick drum: descending sine blip."""

    steps = 8
    part = ms / steps
    seg = AudioSegment.silent(duration=0)
    freq = freq_start
    delta = (freq_end - freq_start) / steps
    for _ in range(steps):
        seg += Sine(freq).to_audio_segment(duration=part)
        freq += delta
    seg = env_fade(seg, 2, ms)
    return (seg + vol_db).set_channels(2)


def make_snare(ms: int = 140, vol_db: float = -2) -> AudioSegment:
    """Short snare: sine "body" plus white noise burst."""

    body = Sine(200).to_audio_segment(duration=ms)
    noise = WhiteNoise().to_audio_segment(duration=ms).high_pass_filter(2000)
    seg = body.overlay(noise)
    seg = env_fade(seg, 5, ms)
    return (seg + vol_db).set_channels(2)


def make_hat(ms: int = 80, vol_db: float = -10) -> AudioSegment:
    """Tight hi‑hat: high‑passed white noise."""

    noise = WhiteNoise().to_audio_segment(duration=ms).high_pass_filter(6000)
    seg = env_fade(noise, 2, ms)
    return (seg + vol_db).set_channels(2)


def make_pad(
    duration_ms: int = 2000,
    waveform: str = "sine",
    freq: float = 220,
    vol_db: float = -10,
) -> AudioSegment:
    """Sustain pad tone using one of the basic waveforms."""

    gen_map = {
        "sine": Sine,
        "saw": Sawtooth,
        "square": Square,
        "triangle": Triangle,
    }
    gen_cls = gen_map.get(waveform, Sine)
    seg = gen_cls(freq).to_audio_segment(duration=duration_ms)
    seg = seg.low_pass_filter(3000)
    seg = env_fade(seg, 50, 200)
    return (seg + vol_db).set_channels(2)


# ---------------------------------------------------------------------------
# Prompt -> recipe


def generate_recipe_from_prompt(prompt: str, override_bpm: int | None = None) -> Dict:
    """Return a minimal recipe dict derived from ``prompt``.

    The prompt is scanned for simple style keywords.  Each style controls the
    BPM, hi‑hat density and pad waveform so that different prompts yield
    noticeably different audio.  If ``override_bpm`` is provided it will replace
    the style's default tempo so the user can fine tune the speed of the mix.
    """

    text = prompt.lower()

    if "ambient" in text:
        style = "ambient"
    elif "dance" in text or "techno" in text or "clubby" in text:
        style = "dance"
    elif "pop" in text:
        style = "pop"
    elif "synthwave" in text or "synth" in text:
        style = "synth"
    else:
        style = "synth"

    style_cfg = {
        "ambient": {"bpm": 75, "hat": "x---------------", "wave": "sine"},
        "synth": {"bpm": 95, "hat": "x-x-x-x-x-x-x-x-", "wave": "saw"},
        "dance": {"bpm": 125, "hat": "xxxxxxxxxxxxxxxx", "wave": "square"},
        "pop": {"bpm": 110, "hat": "x---x---x---x---", "wave": "triangle"},
    }[style]

    bars = 8
    recipe = {
        "bpm": style_cfg["bpm"],
        "bars": bars,
        "grid": 16,
        "layers": [
            {"name": "kick", "type": "drum", "pattern": "x---x---x---x---"},
            {"name": "snare", "type": "drum", "pattern": "----x-------x---"},
            {"name": "hat", "type": "drum", "pattern": style_cfg["hat"]},
            {"name": "pad", "type": "synth", "wave": style_cfg["wave"], "freq": 220, "bars": bars},
        ],
        "master_fx": {"normalize": True, "gain_db": -1.0},
    }

    if "reverb" in text or "space" in text:
        recipe["pad_reverb"] = True
    else:
        recipe["pad_reverb"] = False

    if override_bpm is not None:
        recipe["bpm"] = override_bpm

    return recipe


# ---------------------------------------------------------------------------
# Recipe -> AudioSegment


def build_track(recipe: Dict) -> AudioSegment:
    """Render ``recipe`` to an ``AudioSegment``."""

    bpm = recipe.get("bpm", 120)
    bars = recipe.get("bars", 8)
    grid = recipe.get("grid", 16)
    step_ms = 60_000 / bpm / (grid / 4)
    total_ms = int(step_ms * grid * bars)

    track = AudioSegment.silent(duration=total_ms, frame_rate=44100).set_channels(2)

    for layer in recipe.get("layers", []):
        name = layer.get("name")
        ltype = layer.get("type")
        if ltype == "drum":
            pattern = layer.get("pattern", "")
            for bar in range(bars):
                for i, ch in enumerate(pattern):
                    if ch != "x":
                        continue
                    pos = int((bar * grid + i) * step_ms)
                    if name == "kick":
                        sample = make_kick()
                    elif name == "snare":
                        sample = make_snare()
                    elif name == "hat":
                        sample = make_hat()
                    else:
                        continue
                    track = track.overlay(sample, position=pos)

        elif ltype == "synth" and name == "pad":
            dur = total_ms
            pad = make_pad(duration_ms=dur, waveform=layer.get("wave", "sine"), freq=layer.get("freq", 220))
            if recipe.get("pad_reverb"):
                for d in (60, 120, 240):
                    pad = pad.overlay(pad - 12, position=d)
                pad = pad[:dur]
            track = track.overlay(pad, position=0)

    fx = recipe.get("master_fx", {})
    if fx.get("normalize"):
        track = effects.normalize(track)
    gain = fx.get("gain_db")
    if gain is not None:
        track = track + gain

    return track


# End of file

