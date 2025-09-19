import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from core import parser


def test_prompt_to_synthtax_basic():
    prompt = (
        'Set bpm to 100 and key to C minor, load DRUM from "drum.wav" '
        'and loop DRUM for 4 bars and gain DRUM by -3 dB and export to "out.wav"'
    )
    expected = '\n'.join([
        'set(bpm=100, key="C minor")',
        'load DRUM from "drum.wav"',
        'loop(DRUM, bars=4)',
        'gain(DRUM, -3)',
        'export("out.wav")',
    ])
    synth = parser.prompt_to_synthtax(prompt)
    assert synth == expected
    cmds = parser.parse(synth)
    assert cmds == [
        {'action': 'set', 'bpm': 100, 'key': 'C minor'},
        {'action': 'load', 'track': 'DRUM', 'file': 'drum.wav'},
        {'action': 'loop', 'track': 'DRUM', 'bars': 4},
        {'action': 'gain', 'track': 'DRUM', 'db': -3},
        {'action': 'export', 'file': 'out.wav'},
    ]


def test_prompt_to_synthtax_with_beat():
    prompt = "layer a hip hop beat and export to \"flip.wav\""
    synth = parser.prompt_to_synthtax(prompt)
    expected = '\n'.join([
        'beat(drums, style="hiphop", bars=4)',
        'export("flip.wav")',
    ])
    assert synth == expected
