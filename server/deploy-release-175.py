"""Holy Lois server release for pack 1.7.5 ("Polish and a bigger world"). Run as root on the server from ~/hl-175.

- Onboarding 1.7.1: /home picks the home named home when there are several, case-only duplicate names are refused,
  /Home alias, players return through the Nether portal pair they used, /structures, Tab slots placeholder.
- Holy Lois Extras 1.3.0 (both sides): boombox volume and 6 new stations, outdated-pack check before joining
  (config/holylois-pack.json minimum 1.7.5), safe clickable commands without the confirm screen.
- World border 20000. BlueMap renders only inside it. The terrain job pregenerates the whole square while the server
  is empty and raises /rtp to 5000 once every chunk is proven Status=full. The old radius-4000 job state is archived.
- Datapack holylois-recipes: the recovery compass recipe is gone (the death point is on the minimap).
- Rules (in game and Discord #rules) and the Tab list follow the 1.7.5 texts.
Online players get a one-minute countdown, then a kick with a Holy Lois message. A complete verified backup comes first
and everything returns automatically if the server does not start.
"""
import datetime, json, os, re, shutil, subprocess, time
from pathlib import Path

from importlib import util
spec = util.spec_from_file_location('previous', '/home/ubuntu/hl-174/deploy-release-174.py'); previous = util.module_from_spec(spec); spec.loader.exec_module(previous)
online_players, wait_for_start, run, console, say = previous.online_players, previous.wait_for_start, previous.run, previous.console, previous.say

HOME = Path('/home/ubuntu/hl-175')
ROOT = Path('/opt/minecraft')
MODS = ROOT / 'mods'
ONBOARDING_NEW = Path('/home/ubuntu/holylois-build-171/holylois-onboarding-1.7.1+26.3.jar')
EXTRAS_NEW = Path('/home/ubuntu/holylois-extras-130/holylois-extras-1.3.0+26.3.jar')
PACK_MINIMUM = ROOT / 'config/holylois-pack.json'
BOOMBOX = ROOT / 'config/holylois-boombox.json'
NEW_STATIONS = [('SomaFM Dub Step Beyond', 'https://ice2.somafm.com/dubstep-128-mp3'), ('Bassdrive (drum and bass)', 'http://ice.bassdrive.net/stream'),
                ('laut.fm Trap', 'https://stream.laut.fm/trap'), ('laut.fm Lo-fi', 'https://stream.laut.fm/lofi'),
                ('laut.fm Hardstyle', 'https://stream.laut.fm/hardstyle'), ('laut.fm Techno', 'https://stream.laut.fm/techno')]
RECIPES_NEW, RECIPES = HOME / 'holylois-recipes', ROOT / 'world/datapacks/holylois-recipes'
BLUEMAP_MAPS = ROOT / 'config/bluemap/maps'
STYLE = ROOT / 'config/styledplayerlist/styles/holylois.json'
RULES_TXT = ROOT / 'config/essentialcommands/rules.txt'
OLD_CLAIM_RULE, NEW_CLAIM_RULE = 'Claim your land on the map (M, right-click a chunk)', 'Claim your land on the map (J, right-click a chunk)'
RULES_MD_NEW, RULES_MD = HOME / 'RULES.md', Path('/opt/holylois-bot/RULES.md')
TERRAIN_NEW, TERRAIN = HOME / 'expand-terrain.py', Path('/usr/local/lib/holylois/expand-terrain.py')
CHUNKY_TASK = ROOT / 'config/chunky/tasks/minecraft/overworld.properties'
TERRAIN_STATE = Path('/opt/minecraft-backups/terrain-expansion/job.json')
MOTD = ROOT / 'config/MiniMOTD/main.conf'
MAINTENANCE = Path('/run/holylois-maintenance')
ALERT = Path('/usr/local/lib/holylois/discord-alert.py')
# Server list line under the name: always the newest exciting change, capital letter after "New:".
HEADLINE = '<#FFAD42>✦ New:</#FFAD42> <white>Boombox volume, 6 new stations and a bigger world!</white>'
COUNTDOWN = 60
BORDER = 20000
BAR = 'holylois:restart'


def countdown():
    """Same countdown as 1.7.4 (boss bar, big numbers, goodbye title, kick); only the chat line differs."""
    original = previous.say
    previous.say = lambda text: original(text.replace('land claims on the map, zone titles, /support',
                                                      'boombox volume, new stations, /home and portal fixes, a bigger world'))
    try: previous.countdown()
    finally: previous.say = original


def add_stations():
    config = json.loads(BOOMBOX.read_text(encoding='utf-8'))
    known = {station['url'] for station in config['stations']}
    config['stations'] += [{'name': name, 'url': url} for name, url in NEW_STATIONS if url not in known]
    assert len(config['stations']) <= 16, 'The boombox cycles through at most 16 stations'
    BOOMBOX.write_text(json.dumps(config, indent=2, ensure_ascii=False) + '\n', encoding='utf-8')
    return len(config['stations'])


def main():
    assert os.geteuid() == 0, 'Run as root'
    old_onboarding = sorted(MODS.glob('holylois-onboarding-*.jar')); old_extras = sorted(MODS.glob('holylois-extras-*.jar'))
    assert len(old_onboarding) == 1 and len(old_extras) == 1, (old_onboarding, old_extras)
    assert old_onboarding[0].name != ONBOARDING_NEW.name and old_extras[0].name != EXTRAS_NEW.name, 'Already deployed'
    assert STYLE.read_text(encoding='utf-8').count('%server:max_players%') == 1, 'Tab style not as expected'
    for path in [ONBOARDING_NEW, EXTRAS_NEW, RECIPES_NEW / 'pack.mcmeta', STYLE, RULES_MD_NEW, TERRAIN_NEW, HOME / 'set-render-bounds.py',
                 BOOMBOX, MOTD, RULES_TXT]:
        assert path.exists(), path
    assert not RECIPES.exists() and not PACK_MINIMUM.exists(), 'Partly deployed already'
    assert OLD_CLAIM_RULE in RULES_TXT.read_text(encoding='utf-8'), 'Rules text not as expected'
    assert 'BORDER = 20000' in TERRAIN_NEW.read_text(), 'Terrain job is not the 20000 version'
    assert subprocess.run(['systemctl', 'is-enabled', 'holylois-terrain-expansion.timer'], capture_output=True, text=True).stdout.strip() != 'enabled', \
        'Terrain timer is enabled; it must stay off until the new job is installed'
    assert shutil.disk_usage(ROOT).free > 8 * 1024**3, 'Less than 8 GB free'
    maps = sorted(BLUEMAP_MAPS.glob('*.conf')); assert len(maps) == 3, maps
    countdown()

    stamp = datetime.datetime.now(datetime.timezone.utc).strftime('%Y%m%dT%H%M%SZ')
    backup = Path('/opt/minecraft-backups/maintenance') / ('release175-' + stamp)
    backup.mkdir(mode=0o700)
    MAINTENANCE.touch()
    run('systemctl', 'stop', 'minecraft-console.socket', 'minecraft.service')
    installed = []
    saved = [*old_onboarding, *old_extras, MOTD, RULES_TXT, BOOMBOX, STYLE, *maps]
    moved = [path for path in (CHUNKY_TASK, TERRAIN_STATE) if path.exists()]
    try:
        archive = backup / 'complete-server.tar.gz'
        run('tar', '--exclude=minecraft/backups', '-czf', str(archive), '-C', '/opt', 'minecraft')
        archive.chmod(0o600)
        run('tar', '-tzf', str(archive), stdout=subprocess.DEVNULL)
        (backup / 'bluemap').mkdir()
        for path in saved: shutil.copy2(path, backup / ('bluemap' if path in maps else '') / path.name)
        # The radius-4000 job is superseded by the 20000 border; its task and state go into the backup, never deleted.
        for path in moved: shutil.move(str(path), str(backup / ('old-' + path.name)))

        for jar in [ONBOARDING_NEW, EXTRAS_NEW]:
            target = MODS / jar.name
            run('install', '-o', 'minecraft', '-g', 'minecraft', '-m', '644', str(jar), str(target))
            installed.append(target)
        for old in old_onboarding + old_extras: old.unlink()
        shutil.copytree(RECIPES_NEW, RECIPES); installed.append(RECIPES)
        PACK_MINIMUM.write_text(json.dumps({'minimum': '1.7.5'}) + '\n'); installed.append(PACK_MINIMUM)
        run('python3', str(HOME / 'set-render-bounds.py'), str(BORDER), str(BLUEMAP_MAPS))
        stations = add_stations()
        # Only the player count changes; the live style carries layout tweaks made on the server.
        STYLE.write_text(STYLE.read_text(encoding='utf-8').replace('%server:max_players%', '%holylois:slots%'), encoding='utf-8')
        RULES_TXT.write_text(RULES_TXT.read_text(encoding='utf-8').replace(OLD_CLAIM_RULE, NEW_CLAIM_RULE), encoding='utf-8')
        motd, count = re.subn(r'(?m)^(\s*line2=).*$', lambda m: m.group(1) + json.dumps(HEADLINE, ensure_ascii=False), MOTD.read_text(encoding='utf-8'), count=1)
        assert count == 1, 'MOTD line2 not found'
        MOTD.write_text(motd, encoding='utf-8')
        run('chown', '-R', 'minecraft:minecraft', str(RECIPES), str(PACK_MINIMUM), str(BOOMBOX), str(STYLE), str(RULES_TXT), str(MOTD), *map(str, maps))

        since = time.strftime('%Y-%m-%d %H:%M:%S')
        run('systemctl', 'start', 'minecraft-console.socket', 'minecraft.service')
        log = wait_for_start(since)
        for needle in ['holylois-onboarding 1.7.1', 'holylois-extras 1.3.0', 'holylois_boombox', 'Holy Lois discoveries']:
            assert needle in log, 'Not loaded: ' + needle
        assert 'Registry loading errors' not in log, 'A datapack failed to load'
    except Exception:
        subprocess.run(['systemctl', 'stop', 'minecraft-console.socket', 'minecraft.service'])
        for target in installed:
            if target.is_dir(): shutil.rmtree(target, ignore_errors=True)
            else: target.unlink(missing_ok=True)
        for path in saved:
            source = backup / ('bluemap' if path in maps else '') / path.name
            if source.exists(): shutil.copy2(source, path); subprocess.run(['chown', 'minecraft:minecraft', str(path)])
        for path in moved:
            if (backup / ('old-' + path.name)).exists(): shutil.move(str(backup / ('old-' + path.name)), str(path))
        subprocess.run(['systemctl', 'start', 'minecraft-console.socket', 'minecraft.service'])
        MAINTENANCE.unlink(missing_ok=True)
        print('Rolled back to the previous mods and settings. Backup kept at', backup)
        raise

    console(f'bossbar remove {BAR}', 'gamerule send_command_feedback true', 'worldborder center 0 0', f'worldborder set {BORDER}',
            'worldborder warning distance 64')
    MAINTENANCE.unlink(missing_ok=True)
    # The bot keeps Discord #rules in sync with RULES.md and only reads the log, so it can update after the server is up.
    run('install', '-m', '644', str(RULES_MD_NEW), str(RULES_MD))
    subprocess.run(['systemctl', 'restart', 'holylois-discord-bot'])
    # New terrain job: one short step per tick, only while nobody is online; /rtp changes only after the full proof.
    run('install', '-m', '755', str(TERRAIN_NEW), str(TERRAIN))
    run('systemctl', 'daemon-reload')
    run('systemctl', 'enable', '--now', 'holylois-terrain-expansion.timer')
    message = ("**Holy Lois 1.7.5 is live: polish and a bigger world!** Close Minecraft, open the launcher and click Update.\n"
               "- Boombox: sneak + scroll for volume, music notes, and 6 new stations (dubstep, drum and bass, trap, lo-fi, hardstyle, techno)\n"
               "- R on an item shows its recipe, R on an empty slot sorts. A broken tool swaps in the cheapest spare with a soft chime\n"
               "- /home goes to the home named home when you have several. Portals take you back to the one you came through\n"
               "- World border 20000, new land generates while the server is empty. /structures tells you where you are\n"
               "- Click commands in chat (tpa accept, homes) without the confirm screen. No more glass flicker with shaders\n"
               "- Fix: the world map opens with **J**, not M")
    result = subprocess.run(['python3', str(ALERT), 'message', message], capture_output=True, text=True)
    receipt = {'release': 'pack 1.7.5 server', 'backup': str(archive), 'onboarding': '1.7.1', 'extras': '1.3.0', 'pack_minimum': '1.7.5',
               'boombox_stations': stations, 'world_border': BORDER, 'archived_terrain_state': [p.name for p in moved], 'motd': HEADLINE,
               'discord': 'ok' if result.returncode == 0 else result.stderr.strip()[:200], 'result': 'Done'}
    (backup / 'receipt.json').write_text(json.dumps(receipt, indent=2, ensure_ascii=False) + '\n')
    print(json.dumps(receipt, indent=2, ensure_ascii=False))
    # Offload this backup to Google Drive once it has been quiet for 15 minutes (the job verifies before deleting).
    subprocess.run(['systemd-run', '--on-active=900', '--unit=holylois-offload-release175', 'systemctl', 'start', 'holylois-offsite-backup.service'])


if __name__ == '__main__':
    main()
