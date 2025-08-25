from typing import List, Dict, Optional
from pydub import AudioSegment
from . import fx


def apply_commands(commands: List[Dict], uploaded_path: Optional[str] = None, preview: bool = False):
    """Apply parsed commands and return AudioSegment or output path."""
    context: Dict = {'bpm': 120, 'key': 'C'}
    tracks: Dict[str, AudioSegment] = {}
    export_file: Optional[str] = None

    for cmd in commands:
        action = cmd['action']
        if action == 'set':
            context.update({k: v for k, v in cmd.items() if k != 'action'})
        elif action == 'load':
            path = uploaded_path if cmd['file'] == 'uploaded' and uploaded_path else cmd['file']
            tracks[cmd['track']] = AudioSegment.from_file(path)
        elif action == 'loop':
            seg = tracks.get(cmd['track'])
            if seg is not None:
                tracks[cmd['track']] = fx.loop(seg, cmd['bars'], context.get('bpm', 120))
        elif action == 'gain':
            seg = tracks.get(cmd['track'])
            if seg is not None:
                tracks[cmd['track']] = fx.gain(seg, cmd['db'])
        elif action == 'fadeIn':
            seg = tracks.get(cmd['track'])
            if seg is not None:
                tracks[cmd['track']] = fx.fade_in(seg, cmd['seconds'])
        elif action == 'reverb':
            seg = tracks.get(cmd['track'])
            if seg is not None:
                tracks[cmd['track']] = fx.reverb(seg, cmd['amount'])
        elif action == 'export':
            export_file = cmd['file']

    # Mix tracks together
    if tracks:
        mix: Optional[AudioSegment] = None
        for seg in tracks.values():
            mix = seg if mix is None else mix.overlay(seg)
    else:
        mix = AudioSegment.silent(duration=1000)

    if preview:
        mix = mix.set_frame_rate(22050).set_channels(1)
        return mix

    if export_file:
        mix.export(export_file, format='wav')
        return export_file

    return mix
