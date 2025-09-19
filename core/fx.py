from typing import Dict, List
import numpy as np
from pydub import AudioSegment


def loop(segment: AudioSegment, bars: int, bpm: int) -> AudioSegment:
    """Loop a segment for a given number of bars."""
    bar_ms = 60000 / bpm * 4  # assuming 4 beats per bar
    target_ms = int(bar_ms * bars)
    repetitions = int(target_ms / len(segment) + 1)
    out = segment * repetitions
    return out[:target_ms]

def gain(segment: AudioSegment, db: int) -> AudioSegment:
    """Apply gain in decibels."""
    return segment + db

def fade_in(segment: AudioSegment, seconds: int) -> AudioSegment:
    """Fade in the segment."""
    return segment.fade_in(seconds * 1000)

def fade_out(segment: AudioSegment, seconds: int) -> AudioSegment:
    """Fade out the segment."""
    return segment.fade_out(seconds * 1000)

def slice_segment(segment: AudioSegment, start_ms: int, duration_ms: int) -> AudioSegment:
    """Extract a portion of the segment."""
    end_ms = start_ms + duration_ms
    return segment[start_ms:end_ms]

def reverse(segment: AudioSegment) -> AudioSegment:
    """Reverse the audio segment."""
    return segment.reverse()

def pan(segment: AudioSegment, amount: float) -> AudioSegment:
    """Pan the audio segment left (-1.0) to right (1.0)."""
    return segment.pan(amount)

def normalize(segment: AudioSegment, headroom: float = 0.1) -> AudioSegment:
    """Normalize audio to a target headroom in dBFS."""
    change = -segment.max_dBFS - headroom
    return segment.apply_gain(change)

def reverb(segment: AudioSegment, amount: float = 0.5) -> AudioSegment:
    """Simple reverb using delayed attenuated copies with numpy."""
    samples = np.array(segment.get_array_of_samples()).astype(np.float32)
    delay = int(0.03 * segment.frame_rate)  # 30ms delay
    out = np.copy(samples)
    for i in range(1, 4):
        atten = amount / (i + 1)
        if len(samples) > delay * i:
            out[delay * i :] += samples[: len(samples) - delay * i] * atten
    # clip to int16 range
    out = np.clip(out, -32768, 32767).astype(np.int16)
    return segment._spawn(out.tobytes())


def _to_segment(samples: np.ndarray, frame_rate: int) -> AudioSegment:
    """Convert floating point samples (-1..1) to an AudioSegment."""
    clipped = np.clip(samples, -1.0, 1.0)
    int_samples = (clipped * 32767).astype(np.int16)
    return AudioSegment(
        data=int_samples.tobytes(), sample_width=2, frame_rate=frame_rate, channels=1
    )


def _kick(frame_rate: int) -> AudioSegment:
    duration_ms = 240
    t = np.linspace(0, duration_ms / 1000.0, int(frame_rate * duration_ms / 1000.0), False)
    freq_start, freq_end = 120.0, 50.0
    freq = freq_start * (freq_end / freq_start) ** (t / t.max())
    envelope = np.exp(-6 * t)
    wave = np.sin(2 * np.pi * freq * t) * envelope
    segment = _to_segment(wave, frame_rate)
    return segment.fade_out(80)


def _snare(frame_rate: int) -> AudioSegment:
    duration_ms = 180
    n_samples = int(frame_rate * duration_ms / 1000.0)
    rng = np.random.default_rng(42)
    noise = rng.uniform(-1.0, 1.0, n_samples)
    envelope = np.exp(-10 * np.linspace(0, 1, n_samples))
    wave = noise * envelope
    segment = _to_segment(wave, frame_rate)
    return segment.high_pass_filter(2000).fade_out(60)


def _hat(frame_rate: int) -> AudioSegment:
    duration_ms = 120
    n_samples = int(frame_rate * duration_ms / 1000.0)
    rng = np.random.default_rng(99)
    noise = rng.uniform(-1.0, 1.0, n_samples)
    envelope = np.exp(-12 * np.linspace(0, 1, n_samples))
    wave = noise * envelope
    segment = _to_segment(wave, frame_rate).high_pass_filter(6000)
    return segment.fade_out(40)


def _drum_kit(frame_rate: int) -> Dict[str, AudioSegment]:
    return {
        "kick": _kick(frame_rate),
        "snare": _snare(frame_rate),
        "hat": _hat(frame_rate),
    }


BEAT_PATTERNS: Dict[str, Dict[str, List[int]]] = {
    "house": {
        "kick": [1, 0, 0, 0, 1, 0, 0, 0, 1, 0, 0, 0, 1, 0, 0, 0],
        "snare": [0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0],
        "hat": [0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1],
    },
    "hiphop": {
        "kick": [1, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 1, 0, 0, 1, 0],
        "snare": [0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0],
        "hat": [0, 1, 0, 0, 1, 0, 0, 1, 0, 1, 0, 0, 1, 0, 0, 1],
    },
    "breakbeat": {
        "kick": [1, 0, 0, 1, 0, 0, 1, 0, 1, 0, 0, 1, 0, 1, 0, 0],
        "snare": [0, 0, 1, 0, 0, 1, 0, 0, 0, 0, 1, 0, 0, 1, 0, 0],
        "hat": [0, 1, 1, 1, 0, 1, 1, 1, 0, 1, 1, 1, 0, 1, 1, 1],
    },
}


def generate_beat(style: str, bars: int, bpm: int, frame_rate: int = 44100) -> AudioSegment:
    """Generate a simple beat pattern using synthesized drum sounds."""

    if bars <= 0:
        raise ValueError("bars must be positive for beat generation")

    pattern = BEAT_PATTERNS.get(style, BEAT_PATTERNS["house"])
    kit = _drum_kit(frame_rate)

    steps_per_bar = len(next(iter(pattern.values())))
    bar_ms = 60000 / bpm * 4
    step_ms = bar_ms / steps_per_bar
    total_ms = int(bar_ms * bars)

    beat = AudioSegment.silent(duration=total_ms + 5, frame_rate=frame_rate)

    for instrument, steps in pattern.items():
        sample = kit[instrument]
        for bar_index in range(bars):
            for step_index, active in enumerate(steps):
                if not active:
                    continue
                position = int((bar_index * steps_per_bar + step_index) * step_ms)
                beat = beat.overlay(sample, position=position)

    return normalize(beat, headroom=1.5)
