"""Holy Lois server release for pack 1.8.0 "Fisch on Holy Lois". Run as root on the server from ~/hl-180.

- Fish of Thieves and Fishing Loot Crates (both sides), plus any required library the server does not run yet. The jars and their
  SHA-512 come from new-mods.json (make-pack-180.py on the owner's PC, straight from Modrinth).
- Holy Lois Extras 1.6.0 (both sides): legend items in structure chests and fishing treasure, messages in bottles, buried treasure
  maps, a weight and rarity for every fish caught, and the mod check always allows Fabric Loader's own built-ins.
  config/holylois-legends.json and config/holylois-fish.json hold the lore, chances and fish sizes (/legends reload).
- Advancements: Touched by Legend, one per legend set, Message in a Bottle, Fish Story, The One That Didn't Get Away.
- config/holylois-mods.json gets the new mods' ids (nested jars included); the pack minimum becomes 1.8.0, so a client without the
  new mods gets "update in the launcher" instead of a registry error.
Online players get a one-minute countdown, then a kick with a Holy Lois message. A complete verified backup comes first and everything
returns automatically if the server does not start.
  sudo python3 deploy-release-180.py --check   (all pre-checks, changes nothing)
  sudo python3 deploy-release-180.py
"""
import datetime, hashlib, io, json, os, re, shutil, subprocess, sys, time, zipfile
from pathlib import Path

from importlib import util
spec = util.spec_from_file_location('previous', '/home/ubuntu/hl-174/deploy-release-174.py'); previous = util.module_from_spec(spec); spec.loader.exec_module(previous)
online_players, wait_for_start, run, console, say = previous.online_players, previous.wait_for_start, previous.run, previous.console, previous.say

HOME = Path('/home/ubuntu/hl-180')
ROOT = Path('/opt/minecraft')
MODS = ROOT / 'mods'
EXTRAS_NEW = Path('/home/ubuntu/holylois-extras-160/holylois-extras-1.6.0+26.3.jar')
ADVANCEMENTS_NEW, ADVANCEMENTS = HOME / 'holylois-advancements', ROOT / 'world/datapacks/holylois-advancements'
CONFIGS = {HOME / 'holylois-legends.json': ROOT / 'config/holylois-legends.json', HOME / 'holylois-fish.json': ROOT / 'config/holylois-fish.json'}
MODLIST = ROOT / 'config/holylois-mods.json'
PACK_MINIMUM = ROOT / 'config/holylois-pack.json'
MOTD = ROOT / 'config/MiniMOTD/main.conf'
MAINTENANCE = Path('/run/holylois-maintenance')
ALERT = Path('/usr/local/lib/holylois/discord-alert.py')
# Server list line under the name: always the newest exciting change, capital letter after "New:".
HEADLINE = '<#FFAD42>✦ New:</#FFAD42> <white>Fish of Thieves, legends and trophy fish!</white>'
BAR = 'holylois:restart'


def jar_ids(data):
    """Mod ids (and provides) of a jar and of every jar nested inside it."""
    ids = set()
    with zipfile.ZipFile(io.BytesIO(data)) as jar:
        names = jar.namelist()
        if 'fabric.mod.json' in names:
            meta = json.loads(jar.read('fabric.mod.json').decode('utf-8-sig'), strict=False)
            ids.add(meta['id']); ids.update(meta.get('provides', []))
        for name in names:
            if name.startswith('META-INF/jars/') and name.endswith('.jar'): ids |= jar_ids(jar.read(name))
    return ids


def planned(home=HOME, mods=MODS):
    """new-mods.json and the server jars to add: every server-side new mod, checked by SHA-512, minus libraries already running."""
    manifest = json.loads((home / 'new-mods.json').read_text(encoding='utf-8'))
    present = set()
    for jar in mods.glob('*.jar'): present |= jar_ids(jar.read_bytes())
    jars = []
    for slug in manifest['sides']['server']:
        mod = manifest['mods'][slug]; jar = home / 'server-mods' / mod['filename']
        assert hashlib.sha512(jar.read_bytes()).hexdigest() == mod['sha512'], 'Checksum mismatch: ' + slug
        if mod['id'] in present: continue
        jars.append((mod['id'], jar))
    return manifest, jars


def countdown():
    """Same countdown as 1.7.4 (boss bar, big numbers, goodbye title, kick); only the chat line differs."""
    original = previous.say
    previous.say = lambda text: original(text.replace('land claims on the map, zone titles, /support',
                                                      'Fish of Thieves, loot crates, legends and trophy fish'))
    try: previous.countdown()
    finally: previous.say = original


def main():
    assert os.geteuid() == 0, 'Run as root'
    old_extras = sorted(MODS.glob('holylois-extras-*.jar'))
    assert len(old_extras) == 1, old_extras
    assert old_extras[0].name != EXTRAS_NEW.name, 'Already deployed'
    for path in [EXTRAS_NEW, ADVANCEMENTS_NEW / 'pack.mcmeta', ADVANCEMENTS, MODLIST, PACK_MINIMUM, MOTD, *CONFIGS]:
        assert path.exists(), path
    assert 'Touched by Legend' in (ADVANCEMENTS_NEW / 'data/holylois/advancement/legends/touched_by_legend.json').read_text(encoding='utf-8'), 'Advancements are not the 1.8.0 set'
    for source in CONFIGS: json.loads(source.read_text(encoding='utf-8'))
    manifest, jars = planned()
    assert any(mod_id == 'fishofthieves' for mod_id, _ in jars), 'Fish of Thieves is not in the server set'
    allowed = json.loads(MODLIST.read_text())
    assert allowed.get('mode') in ('enforce', 'warn', 'off') and len(allowed.get('allowed', [])) > 150, 'Mod list looks wrong'
    new_ids = sorted(set(manifest['allow']) - set(allowed['allowed']))
    assert shutil.disk_usage(ROOT).free > 8 * 1024**3, 'Less than 8 GB free'
    print('server jars to add:', ', '.join(jar.name for _, jar in jars))
    print('mod ids to allow:', ', '.join(new_ids) or 'none')
    if sys.argv[1:] == ['--check']:
        print('All pre-checks passed; nothing was changed.')
        return
    countdown()

    stamp = datetime.datetime.now(datetime.timezone.utc).strftime('%Y%m%dT%H%M%SZ')
    backup = Path('/opt/minecraft-backups/maintenance') / ('release180-' + stamp)
    backup.mkdir(mode=0o700)
    MAINTENANCE.touch()
    run('systemctl', 'stop', 'minecraft-console.socket', 'minecraft.service')
    installed = []
    saved = [*old_extras, MOTD, MODLIST, PACK_MINIMUM, *(target for target in CONFIGS.values() if target.exists())]
    try:
        archive = backup / 'complete-server.tar.gz'
        run('tar', '--exclude=minecraft/backups', '-czf', str(archive), '-C', '/opt', 'minecraft')
        archive.chmod(0o600)
        run('tar', '-tzf', str(archive), stdout=subprocess.DEVNULL)
        for path in saved: shutil.copy2(path, backup / path.name)
        shutil.copytree(ADVANCEMENTS, backup / 'holylois-advancements')

        for jar in [EXTRAS_NEW, *(jar for _, jar in jars)]:
            target = MODS / jar.name
            assert not target.exists() or target == MODS / EXTRAS_NEW.name, 'Already in mods: ' + jar.name
            run('install', '-o', 'minecraft', '-g', 'minecraft', '-m', '644', str(jar), str(target))
            installed.append(target)
        for old in old_extras: old.unlink()
        for source, target in CONFIGS.items():
            run('install', '-o', 'minecraft', '-g', 'minecraft', '-m', '644', str(source), str(target)); installed.append(target)
        shutil.rmtree(ADVANCEMENTS); shutil.copytree(ADVANCEMENTS_NEW, ADVANCEMENTS)
        allowed['allowed'] = sorted(set(allowed['allowed']) | set(manifest['allow']))
        MODLIST.write_text(json.dumps(allowed, indent=2) + '\n')
        PACK_MINIMUM.write_text(json.dumps({'minimum': '1.8.0'}) + '\n')
        motd, count = re.subn(r'(?m)^(\s*line2=).*$', lambda m: m.group(1) + json.dumps(HEADLINE, ensure_ascii=False), MOTD.read_text(encoding='utf-8'), count=1)
        assert count == 1, 'MOTD line2 not found'
        MOTD.write_text(motd, encoding='utf-8')
        run('chown', '-R', 'minecraft:minecraft', str(ADVANCEMENTS), str(MODLIST), str(PACK_MINIMUM), str(MOTD))

        since = time.strftime('%Y-%m-%d %H:%M:%S')
        run('systemctl', 'start', 'minecraft-console.socket', 'minecraft.service')
        log = wait_for_start(since)
        needles = ['holylois-extras 1.6.0', 'Holy Lois legends: 3 legends', 'fish weights: 14 species', 'holylois_boombox', 'Holy Lois discoveries']
        needles += [f'- {mod_id} ' for mod_id, _ in jars]
        for needle in needles:
            assert needle in log, 'Not loaded: ' + needle
        assert 'Registry loading errors' not in log, 'A datapack failed to load'
        assert not re.search(r'(?i)(error|couldn.t|failed)[^\n]{0,120}holylois:(legends|fishing)/', log), 'An advancement failed to load'
    except Exception:
        subprocess.run(['systemctl', 'stop', 'minecraft-console.socket', 'minecraft.service'])
        for target in installed: target.unlink(missing_ok=True)
        for path in saved:
            source = backup / path.name
            if source.exists(): shutil.copy2(source, path); subprocess.run(['chown', 'minecraft:minecraft', str(path)])
        if (backup / 'holylois-advancements').exists():
            shutil.rmtree(ADVANCEMENTS, ignore_errors=True); shutil.copytree(backup / 'holylois-advancements', ADVANCEMENTS)
            subprocess.run(['chown', '-R', 'minecraft:minecraft', str(ADVANCEMENTS)])
        subprocess.run(['systemctl', 'start', 'minecraft-console.socket', 'minecraft.service'])
        MAINTENANCE.unlink(missing_ok=True)
        print('Rolled back to the previous mods and settings. Backup kept at', backup)
        raise

    console(f'bossbar remove {BAR}', 'gamerule send_command_feedback true')
    MAINTENANCE.unlink(missing_ok=True)
    message = ("**Holy Lois 1.8.0 is live: Fisch on Holy Lois!** Close Minecraft, open the launcher and click Update.\n"
               "- Fish of Thieves: ten new kinds of fish with colour variants, each with its own waters (biomes, night, storms)\n"
               "- Fishing Loot Crates: now and then a crate comes up on the hook\n"
               "- Every fish has a size now. Rare, Epic and Legendary catches keep their weight in kg and your name: trophies. "
               "A Legendary catch is announced to everyone\n"
               "- Legends: rare named items hide in dungeon, tavern and town chests, each with a strange inscription. "
               "Who did they belong to? Find a whole set for an achievement\n"
               "- Fishing treasure can be a message in a bottle or a map to buried treasure")
    result = subprocess.run(['python3', str(ALERT), 'message', message], capture_output=True, text=True)
    receipt = {'release': 'pack 1.8.0 server', 'backup': str(archive), 'extras': '1.6.0', 'added_jars': [jar.name for _, jar in jars],
               'allowed_ids_added': new_ids, 'pack_minimum': '1.8.0', 'motd': HEADLINE,
               'discord': 'ok' if result.returncode == 0 else result.stderr.strip()[:200], 'result': 'Done'}
    (backup / 'receipt.json').write_text(json.dumps(receipt, indent=2, ensure_ascii=False) + '\n')
    print(json.dumps(receipt, indent=2, ensure_ascii=False))
    subprocess.run(['systemd-run', '--on-active=900', '--unit=holylois-offload-release180', 'systemctl', 'start', 'holylois-offsite-backup.service'])


if __name__ == '__main__':
    main()
