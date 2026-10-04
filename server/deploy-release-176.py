"""Holy Lois server release for pack 1.7.6 (hotfix). Run as root on the server from ~/hl-176.

- Onboarding 1.7.2: every Epic Dungeon (small, medium, large, obelisks) and the small crypts are announced when first found.
- New achievements: Dungeon Delver, Deeper Still, Dungeon Master (hidden) and Odd Pillar (datapack holylois-advancements).
- Holy Lois Extras 1.3.1 (both sides): boombox range 16 to 48 blocks by volume, tool swap that never uses enchanted spares,
  REI no longer opens a recipe on the key press that sorted, first-person body pulled forward in front of walls and hidden in
  bed, dynamic lights step aside while a shader pack is on.
- Runeforged: Epic Dungeon chests join the rune tiers (treasure rooms are tier 1, the rest follow their contents).
- Server list line shortened so it fits.
The pack minimum stays 1.7.5: nothing new is registered, so players on 1.7.5 can still join until they update.
Online players get a one-minute countdown, then a kick with a Holy Lois message. A complete verified backup comes first
and everything returns automatically if the server does not start.
"""
import datetime, json, os, re, shutil, subprocess, time
from pathlib import Path

from importlib import util
spec = util.spec_from_file_location('previous', '/home/ubuntu/hl-174/deploy-release-174.py'); previous = util.module_from_spec(spec); spec.loader.exec_module(previous)
online_players, wait_for_start, run, console, say = previous.online_players, previous.wait_for_start, previous.run, previous.console, previous.say

HOME = Path('/home/ubuntu/hl-176')
ROOT = Path('/opt/minecraft')
MODS = ROOT / 'mods'
ONBOARDING_NEW = Path('/home/ubuntu/holylois-build-172/holylois-onboarding-1.7.2+26.3.jar')
EXTRAS_NEW = Path('/home/ubuntu/holylois-extras-131/holylois-extras-1.3.1+26.3.jar')
ADVANCEMENTS_NEW, ADVANCEMENTS = HOME / 'holylois-advancements', ROOT / 'world/datapacks/holylois-advancements'
MONSTERS = ROOT / 'config/runeforged-monsters.json'
PACK_MINIMUM = ROOT / 'config/holylois-pack.json'
MOTD = ROOT / 'config/MiniMOTD/main.conf'
MAINTENANCE = Path('/run/holylois-maintenance')
ALERT = Path('/usr/local/lib/holylois/discord-alert.py')
# Server list line under the name: always the newest exciting change, capital letter after "New:". Short enough to fit.
HEADLINE = '<#FFAD42>✦ New:</#FFAD42> <white>Dungeon achievements + louder boombox!</white>'
COUNTDOWN = 60
BAR = 'holylois:restart'


def countdown():
    """Same countdown as 1.7.4 (boss bar, big numbers, goodbye title, kick); only the chat line differs."""
    original = previous.say
    previous.say = lambda text: original(text.replace('land claims on the map, zone titles, /support',
                                                      'dungeon achievements, a louder boombox and small fixes'))
    try: previous.countdown()
    finally: previous.say = original


def main():
    assert os.geteuid() == 0, 'Run as root'
    old_onboarding = sorted(MODS.glob('holylois-onboarding-*.jar')); old_extras = sorted(MODS.glob('holylois-extras-*.jar'))
    assert len(old_onboarding) == 1 and len(old_extras) == 1, (old_onboarding, old_extras)
    assert old_onboarding[0].name != ONBOARDING_NEW.name and old_extras[0].name != EXTRAS_NEW.name, 'Already deployed'
    for path in [ONBOARDING_NEW, EXTRAS_NEW, ADVANCEMENTS_NEW / 'pack.mcmeta', HOME / 'runeforged-epic-additions.json', ADVANCEMENTS,
                 MONSTERS, MOTD, PACK_MINIMUM]:
        assert path.exists(), path
    assert 'explore/dungeon_delver.json' in {p.relative_to(ADVANCEMENTS_NEW / 'data/holylois/advancement').as_posix()
                                             for p in (ADVANCEMENTS_NEW / 'data/holylois/advancement').rglob('*.json')}, 'Advancements are not the 1.7.6 set'
    assert shutil.disk_usage(ROOT).free > 8 * 1024**3, 'Less than 8 GB free'
    countdown()

    stamp = datetime.datetime.now(datetime.timezone.utc).strftime('%Y%m%dT%H%M%SZ')
    backup = Path('/opt/minecraft-backups/maintenance') / ('release176-' + stamp)
    backup.mkdir(mode=0o700)
    MAINTENANCE.touch()
    run('systemctl', 'stop', 'minecraft-console.socket', 'minecraft.service')
    installed = []
    saved = [*old_onboarding, *old_extras, MOTD, MONSTERS]
    try:
        archive = backup / 'complete-server.tar.gz'
        run('tar', '--exclude=minecraft/backups', '-czf', str(archive), '-C', '/opt', 'minecraft')
        archive.chmod(0o600)
        run('tar', '-tzf', str(archive), stdout=subprocess.DEVNULL)
        for path in saved: shutil.copy2(path, backup / path.name)
        shutil.copytree(ADVANCEMENTS, backup / 'holylois-advancements')

        for jar in [ONBOARDING_NEW, EXTRAS_NEW]:
            target = MODS / jar.name
            run('install', '-o', 'minecraft', '-g', 'minecraft', '-m', '644', str(jar), str(target))
            installed.append(target)
        for old in old_onboarding + old_extras: old.unlink()
        shutil.rmtree(ADVANCEMENTS); shutil.copytree(ADVANCEMENTS_NEW, ADVANCEMENTS)
        monsters = json.loads(MONSTERS.read_text())
        known = {e['loot_table'] for e in monsters['chest_loot_tables']}
        added = [e for e in json.loads((HOME / 'runeforged-epic-additions.json').read_text()) if e['loot_table'] not in known]
        monsters['chest_loot_tables'] += added
        MONSTERS.write_text(json.dumps(monsters, indent=1) + '\n')
        motd, count = re.subn(r'(?m)^(\s*line2=).*$', lambda m: m.group(1) + json.dumps(HEADLINE, ensure_ascii=False), MOTD.read_text(encoding='utf-8'), count=1)
        assert count == 1, 'MOTD line2 not found'
        MOTD.write_text(motd, encoding='utf-8')
        run('chown', '-R', 'minecraft:minecraft', str(ADVANCEMENTS), str(MONSTERS), str(MOTD))

        since = time.strftime('%Y-%m-%d %H:%M:%S')
        run('systemctl', 'start', 'minecraft-console.socket', 'minecraft.service')
        log = wait_for_start(since)
        for needle in ['holylois-onboarding 1.7.2', 'holylois-extras 1.3.1', 'holylois_boombox', 'Holy Lois discoveries']:
            assert needle in log, 'Not loaded: ' + needle
        assert 'Registry loading errors' not in log, 'A datapack failed to load'
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
    message = ("**Holy Lois 1.7.6 is live: dungeons and fixes!** Close Minecraft, open the launcher and click Update.\n"
               "- Dungeons: every dungeon is announced when you first find it, with new achievements (Dungeon Delver, Deeper Still, Dungeon Master)\n"
               "- Boombox: much longer range, from 16 blocks on volume 1 to 48 on volume 10\n"
               "- Tools: a broken tool swaps in the cheapest unenchanted spare. Your enchanted ones stay safe\n"
               "- R no longer opens a recipe on the press that sorts. Body no longer sits inside walls, no body in bed\n"
               "- Torches light yellow with shaders (dynamic lights step aside while a shader pack is on)")
    result = subprocess.run(['python3', str(ALERT), 'message', message], capture_output=True, text=True)
    receipt = {'release': 'pack 1.7.6 server', 'backup': str(archive), 'onboarding': '1.7.2', 'extras': '1.3.1', 'epic_loot_tables_added': len(added),
               'motd': HEADLINE, 'discord': 'ok' if result.returncode == 0 else result.stderr.strip()[:200], 'result': 'Done'}
    (backup / 'receipt.json').write_text(json.dumps(receipt, indent=2, ensure_ascii=False) + '\n')
    print(json.dumps(receipt, indent=2, ensure_ascii=False))
    subprocess.run(['systemd-run', '--on-active=900', '--unit=holylois-offload-release176', 'systemctl', 'start', 'holylois-offsite-backup.service'])


if __name__ == '__main__':
    main()
