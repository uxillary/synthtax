from typing import Optional
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
