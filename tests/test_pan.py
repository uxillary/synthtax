import os
import sys
from pydub.generators import Sine

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from core import parser, fx


def test_parse_pan_roundtrip():
    text = "pan(DRUM, amount=-0.25)"
    cmds = parser.parse(text)
    assert cmds == [{'action': 'pan', 'track': 'DRUM', 'amount': -0.25}]
    yaml_text = parser.to_yaml(text)
    assert parser.from_yaml(yaml_text).strip() == text


def test_fx_pan_left_channel():
    seg = Sine(440).to_audio_segment(duration=1000).set_channels(2)
    panned = fx.pan(seg, -1.0)
    left, right = panned.split_to_mono()
    assert right.dBFS < -50
    assert left.dBFS > right.dBFS
