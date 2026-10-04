"""Limit BlueMap to the world border: x/z bounds in the first render-mask entry of each map.

BlueMap deletes tiles outside a new mask by itself. The Nether gets 1/8 of the border (coordinate scale) and keeps its
ceiling cut. Run as root with the server stopped or running: `python3 set-render-bounds.py BORDER [CONFIG_DIR]`.
"""
import re, sys
from pathlib import Path

BOUNDS = re.compile(r'^(\s*)#?\s*(min|max)-(x|z):\s*-?\d+\s*$', re.M)


def bounded(text, half):
    start = text.index('render-mask: [')
    first = text.index('{', start)
    end = text.index('}', first)
    block = text[first:end]
    if len(BOUNDS.findall(block)) != 4:
        raise ValueError('expected min/max x/z lines in the first render-mask entry')
    block = BOUNDS.sub(lambda m: f'{m.group(1)}{m.group(2)}-{m.group(3)}: {-half if m.group(2) == "min" else half}', block)
    return text[:first] + block + text[end:]


def main():
    border = int(sys.argv[1])
    folder = Path(sys.argv[2] if len(sys.argv) > 2 else '/opt/minecraft/config/bluemap/maps')
    if not 2000 <= border <= 60000:
        raise SystemExit('border must be between 2000 and 60000')
    for name, half in (('world.conf', border // 2), ('world_the_end.conf', border // 2), ('world_the_nether.conf', border // 16)):
        path = folder / name
        text = path.read_text(encoding='utf-8')
        new = bounded(text, half)
        if new != text:
            path.write_text(new, encoding='utf-8', newline='\n')
        print(f'{name}: +-{half}')


if __name__ == '__main__':
    main()
