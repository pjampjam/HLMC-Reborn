"""Holy Lois hotfix: let Fabric Loader's own built-in mods through the mod check. Run as root on the server from ~/hl-hotfix.

Every client reports the mods Fabric Loader itself provides (java, minecraft, fabricloader and mixinextras, the mixin library the
loader ships inside itself). The allowed list in config/holylois-mods.json was made from the pack's jars, so mixinextras was missing
and every non-exempt player was turned away with "Not part of it: mixinextras". The owner is exempt, so it only showed up when the
launcher 1.3.0 fast start test joined as a normal player.

The mod check reads the file on every join: no restart, nobody is kicked. A copy of the old file is kept next to it.
  sudo python3 allow-loader-mods.py --check   (only shows what would change and how many players were turned away)
  sudo python3 allow-loader-mods.py
"""
import gzip, json, os, re, sys
from pathlib import Path

ROOT = Path('/opt/minecraft')
MODLIST = ROOT / 'config/holylois-mods.json'
BACKUP = MODLIST.with_name('holylois-mods.json.before-loader-mods')
LOADER_MODS = ['fabricloader', 'java', 'minecraft', 'mixinextras']
TURNED_AWAY = re.compile(r'(\S+) has mods that are not part of the pack: \[([^\]]*)\]')


def turned_away():
    """Players the mod check sent away, from the current and archived logs (names and the mods it named)."""
    found = {}
    for log in sorted((ROOT / 'logs').glob('*.log*')):
        try:
            text = gzip.open(log, 'rt', errors='replace').read() if log.suffix == '.gz' else log.read_text(errors='replace')
        except OSError:
            continue
        for name, mods in TURNED_AWAY.findall(text):
            found.setdefault(name, set()).update(m.strip() for m in mods.split(','))
    return found


def main():
    check = '--check' in sys.argv
    config = json.loads(MODLIST.read_text())
    allowed = config.get('allowed', [])
    assert config.get('mode') in ('enforce', 'warn', 'off') and len(allowed) > 150 and 'holylois-extras' in allowed, 'Mod list looks wrong'
    missing = [mod for mod in LOADER_MODS if mod not in allowed]
    print('allowed mods now:', len(allowed), '| loader mods to add:', missing or 'none')
    for name, mods in sorted(turned_away().items()):
        print('turned away before:', name, 'for', ', '.join(sorted(mods)))
    if check or not missing:
        print('no change' if not missing else 'check only, nothing changed')
        return
    stat = MODLIST.stat()
    BACKUP.write_bytes(MODLIST.read_bytes())
    os.chown(BACKUP, stat.st_uid, stat.st_gid)
    config['allowed'] = sorted(set(allowed) | set(LOADER_MODS))
    temp = MODLIST.with_name(MODLIST.name + '.tmp')
    temp.write_text(json.dumps(config, indent=2) + '\n')
    os.chown(temp, stat.st_uid, stat.st_gid)
    os.chmod(temp, stat.st_mode & 0o777)
    os.replace(temp, MODLIST)
    print('added', ', '.join(missing), '| allowed mods now:', len(config['allowed']), '| old file kept as', BACKUP.name)
    print('undo: sudo cp', BACKUP, MODLIST)


if __name__ == '__main__':
    main()
