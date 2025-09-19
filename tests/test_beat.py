import os
import sys

import pytest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from core import fx, parser


def test_parse_beat_command():
    commands = parser.parse('beat(drums, style="hiphop", bars=3)')
    assert commands[0] == {
        'action': 'beat',
        'track': 'drums',
        'style': 'hiphop',
        'bars': 3,
    }


def test_parse_beat_defaults():
    commands = parser.parse('beat(groove, bars=2)')
    cmd = commands[0]
    assert cmd['style'] == 'house'
    assert cmd['bars'] == 2


def test_generate_beat_matches_bpm_and_bars():
    bpm = 96
    bars = 3
    seg = fx.generate_beat('breakbeat', bars=bars, bpm=bpm)
    expected_ms = int(60000 / bpm * 4 * bars)
    assert abs(len(seg) - expected_ms) <= 20


def test_generate_beat_requires_positive_bars():
    with pytest.raises(ValueError):
        fx.generate_beat('house', bars=0, bpm=120)
