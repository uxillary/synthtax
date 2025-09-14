import os
import sys
import pytest
from pydub.generators import Sine

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from core import parser, fx


def test_parse_normalize_roundtrip():
    text = "normalize(DRUM, headroom=0.5)"
    cmds = parser.parse(text)
    assert cmds == [{'action': 'normalize', 'track': 'DRUM', 'headroom': 0.5}]
    yaml_text = parser.to_yaml(text)
    assert parser.from_yaml(yaml_text).strip() == text


def test_fx_normalize_increases_level():
    seg = Sine(440).to_audio_segment(duration=1000) - 10
    assert seg.max_dBFS < -9  # ensure reduction
    normed = fx.normalize(seg, headroom=0.0)
    assert normed.max_dBFS == pytest.approx(0, abs=0.1)

