import os
import sys
from pydub.generators import Sine

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from core import parser, fx


def test_parse_lowpass_roundtrip():
    text = "lowPass(DRUM, cutoff=1000)"
    cmds = parser.parse(text)
    assert cmds == [{'action': 'lowPass', 'track': 'DRUM', 'cutoff': 1000}]
    yaml_text = parser.to_yaml(text)
    assert parser.from_yaml(yaml_text).strip() == text


def test_fx_lowpass_reduces_high_freq():
    seg = Sine(5000).to_audio_segment(duration=1000)
    filtered = fx.low_pass(seg, 1000)
    assert filtered.dBFS < seg.dBFS - 10

