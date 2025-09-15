import re
import yaml
from typing import List, Dict


def prompt_to_synthtax(prompt: str) -> str:
    """Convert a simple natural language prompt to Synthtax DSL.

    This implementation is intentionally lightweight and only recognises a
    subset of the language.  It is *not* meant to be a perfect natural
    language parser but rather a convenience for the most common cases while
    a full model-backed solution is developed.

    Supported phrases:

    - ``set bpm to X`` and optional ``key to Y``
    - ``load TRACK from "file"``
    - ``loop TRACK for N bars``
    - ``gain TRACK by N dB``
    - ``export to "file"``

    Multiple commands can be included in a single prompt and will be emitted
    as separate Synthtax lines.  If no patterns are recognised a placeholder
    comment is returned, mirroring the previous behaviour.
    """

    lines: List[str] = []

    # ``set`` command (bpm and/or key)
    bpm_match = re.search(r"set\s+bpm\s+to\s+(\d+)", prompt, re.IGNORECASE)
    key_match = re.search(r"key\s+to\s+([^,\.]+)", prompt, re.IGNORECASE)
    if bpm_match or key_match:
        parts = []
        if bpm_match:
            parts.append(f"bpm={bpm_match.group(1)}")
        if key_match:
            key_val = key_match.group(1).strip()
            parts.append(f"key=\"{key_val}\"")
        lines.append(f"set({', '.join(parts)})")

    # ``load`` command
    for m in re.finditer(r"load\s+(\w+)\s+from\s+['\"]([^'\"]+)['\"]", prompt, re.IGNORECASE):
        track, file = m.groups()
        lines.append(f"load {track} from \"{file}\"")

    # ``loop`` command
    for m in re.finditer(r"loop\s+(\w+)\s+for\s+(\d+)\s+bars", prompt, re.IGNORECASE):
        track, bars = m.groups()
        lines.append(f"loop({track}, bars={bars})")

    # ``gain`` command
    for m in re.finditer(r"gain\s+(\w+)\s+by\s+(-?\d+)\s*dB", prompt, re.IGNORECASE):
        track, db = m.groups()
        lines.append(f"gain({track}, {db})")

    # ``export`` command
    for m in re.finditer(r"export\s+to\s+['\"]([^'\"]+)['\"]", prompt, re.IGNORECASE):
        filename = m.group(1)
        lines.append(f"export(\"{filename}\")")

    if not lines:
        return f"# TODO: implement OpenAI prompt -> Synthtax\n# prompt: {prompt}"

    return "\n".join(lines)

def parse(text: str) -> List[Dict]:
    """Parse Synthtax DSL into a list of command dictionaries."""
    commands: List[Dict] = []
    lines = text.strip().splitlines()
    for line in lines:
        line = line.strip()
        if not line or line.startswith('#'):
            continue
        if line.startswith('set('):
            bpm_match = re.search(r'bpm\s*=\s*(\d+)', line)
            key_match = re.search(r'key\s*=\s*"([^"]+)"', line)
            cmd = {'action': 'set'}
            if bpm_match:
                cmd['bpm'] = int(bpm_match.group(1))
            if key_match:
                cmd['key'] = key_match.group(1)
            commands.append(cmd)
        elif line.startswith('load'):
            m = re.match(r'load\s+(\w+)\s+from\s+"([^"]+)"', line)
            if not m:
                raise ValueError(f"Invalid load syntax: {line}")
            track, file = m.groups()
            commands.append({'action': 'load', 'track': track, 'file': file})
        elif line.startswith('loop'):
            m = re.match(r'loop\(\s*(\w+),\s*bars\s*=\s*(\d+)\s*\)', line)
            if not m:
                raise ValueError(f"Invalid loop syntax: {line}")
            track, bars = m.groups()
            commands.append({'action': 'loop', 'track': track, 'bars': int(bars)})
        elif line.startswith('gain'):
            m = re.match(r'gain\(\s*(\w+),\s*(-?\d+)\s*\)', line)
            if not m:
                raise ValueError(f"Invalid gain syntax: {line}")
            track, db = m.groups()
            commands.append({'action': 'gain', 'track': track, 'db': int(db)})
        elif line.startswith('fadeIn'):
            m = re.match(r'fadeIn\(\s*(\w+),\s*seconds\s*=\s*(\d+)\s*\)', line)
            if not m:
                raise ValueError(f"Invalid fadeIn syntax: {line}")
            track, secs = m.groups()
            commands.append({'action': 'fadeIn', 'track': track, 'seconds': int(secs)})
        elif line.startswith('fadeOut'):
            m = re.match(r'fadeOut\(\s*(\w+),\s*seconds\s*=\s*(\d+)\s*\)', line)
            if not m:
                raise ValueError(f"Invalid fadeOut syntax: {line}")
            track, secs = m.groups()
            commands.append({'action': 'fadeOut', 'track': track, 'seconds': int(secs)})
        elif line.startswith('slice'):
            m = re.match(r'slice\(\s*(\w+),\s*start\s*=\s*(\d+),\s*duration\s*=\s*(\d+)\s*\)', line)
            if not m:
                raise ValueError(f"Invalid slice syntax: {line}")
            track, start, dur = m.groups()
            commands.append({'action': 'slice', 'track': track, 'start': int(start), 'duration': int(dur)})
        elif line.startswith('reverse'):
            m = re.match(r'reverse\(\s*(\w+)\s*\)', line)
            if not m:
                raise ValueError(f"Invalid reverse syntax: {line}")
            track = m.group(1)
            commands.append({'action': 'reverse', 'track': track})
        elif line.startswith('pan'):
            m = re.match(r'pan\(\s*(\w+),\s*amount\s*=\s*(-?[0-9.]+)\s*\)', line)
            if not m:
                raise ValueError(f"Invalid pan syntax: {line}")
            track, amt = m.groups()
            commands.append({'action': 'pan', 'track': track, 'amount': float(amt)})
        elif line.startswith('normalize'):
            m = re.match(r'normalize\(\s*(\w+)(?:,\s*headroom\s*=\s*([0-9.]+))?\s*\)', line)
            if not m:
                raise ValueError(f"Invalid normalize syntax: {line}")
            track, headroom = m.groups()
            cmd = {'action': 'normalize', 'track': track}
            if headroom is not None:
                cmd['headroom'] = float(headroom)
            commands.append(cmd)
        elif line.startswith('reverb'):
            m = re.match(r'reverb\(\s*(\w+),\s*amount\s*=\s*([0-9.]+)\s*\)', line)
            if not m:
                raise ValueError(f"Invalid reverb syntax: {line}")
            track, amt = m.groups()
            commands.append({'action': 'reverb', 'track': track, 'amount': float(amt)})
        elif line.startswith('export'):
            m = re.match(r'export\(\s*"([^"]+)"\s*\)', line)
            if not m:
                raise ValueError(f"Invalid export syntax: {line}")
            filename = m.group(1)
            commands.append({'action': 'export', 'file': filename})
        else:
            raise ValueError(f"Unknown command: {line}")
    return commands

def to_yaml(text: str) -> str:
    """Convert Synthtax text to YAML representation."""
    cmds = parse(text)
    return yaml.safe_dump(cmds)

def from_yaml(yaml_text: str) -> str:
    """Convert YAML representation back to Synthtax text."""
    data = yaml.safe_load(yaml_text)
    lines = []
    for cmd in data:
        act = cmd.get('action')
        if act == 'set':
            lines.append(f"set(bpm={cmd.get('bpm')}, key=\"{cmd.get('key')}\")")
        elif act == 'load':
            lines.append(f"load {cmd['track']} from \"{cmd['file']}\"")
        elif act == 'loop':
            lines.append(f"loop({cmd['track']}, bars={cmd['bars']})")
        elif act == 'gain':
            lines.append(f"gain({cmd['track']}, {cmd['db']})")
        elif act == 'fadeIn':
            lines.append(f"fadeIn({cmd['track']}, seconds={cmd['seconds']})")
        elif act == 'fadeOut':
            lines.append(f"fadeOut({cmd['track']}, seconds={cmd['seconds']})")
        elif act == 'slice':
            lines.append(f"slice({cmd['track']}, start={cmd['start']}, duration={cmd['duration']})")
        elif act == 'reverse':
            lines.append(f"reverse({cmd['track']})")
        elif act == 'pan':
            lines.append(f"pan({cmd['track']}, amount={cmd['amount']})")
        elif act == 'normalize':
            if 'headroom' in cmd:
                lines.append(f"normalize({cmd['track']}, headroom={cmd['headroom']})")
            else:
                lines.append(f"normalize({cmd['track']})")
        elif act == 'reverb':
            lines.append(f"reverb({cmd['track']}, amount={cmd['amount']})")
        elif act == 'export':
            lines.append(f"export(\"{cmd['file']}\")")
    return "\n".join(lines)
