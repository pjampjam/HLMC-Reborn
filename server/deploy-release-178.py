"""Holy Lois server release for pack 1.7.8. Run as root on the server from ~/hl-178.

- Holy Lois Extras 1.4.0 (both sides): the mod check. A joining client reports its mod ids and the server compares them with
  config/holylois-mods.json (the pack's mods). Extra mods are turned away with a message; old clients are let in; the owner is exempt.
  Switch it off without a restart: set "mode" to "off" in that file (it is read on every join).
- Crisp crown window icons (client) and a new server icon in the multiplayer list.
- Clearer texts for the Discoverer, Dungeon Delver, Deeper Still and Odd Pillar achievements (datapack holylois-advancements).
The pack minimum stays 1.7.5. Online players get a one-minute countdown, then a kick with a Holy Lois message. A complete verified
backup comes first and everything returns automatically if the server does not start.
"""
import datetime, json, os, re, shutil, subprocess, time
from pathlib import Path

from importlib import util
spec = util.spec_from_file_location('previous', '/home/ubuntu/hl-174/deploy-release-174.py'); previous = util.module_from_spec(spec); spec.loader.exec_module(previous)
online_players, wait_for_start, run, console, say = previous.online_players, previous.wait_for_start, previous.run, previous.console, previous.say

HOME = Path('/home/ubuntu/hl-178')
ROOT = Path('/opt/minecraft')
MODS = ROOT / 'mods'
EXTRAS_NEW = Path('/home/ubuntu/holylois-extras-131/holylois-extras-1.4.0+26.3.jar')
ADVANCEMENTS_NEW, ADVANCEMENTS = HOME / 'holylois-advancements', ROOT / 'world/datapacks/holylois-advancements'
MODLIST_NEW, MODLIST = HOME / 'holylois-mods.json', ROOT / 'config/holylois-mods.json'
ICON_NEW, ICON = HOME / 'server-icon.png', ROOT / 'server-icon.png'
PACK_MINIMUM = ROOT / 'config/holylois-pack.json'
MOTD = ROOT / 'config/MiniMOTD/main.conf'
MAINTENANCE = Path('/run/holylois-maintenance')
ALERT = Path('/usr/local/lib/holylois/discord-alert.py')
# Server list line under the name: always the newest exciting change, capital letter after "New:". Short enough to fit.
HEADLINE = '<#FFAD42>✦ New:</#FFAD42> <white>Crown icons + pack-only mod check!</white>'
COUNTDOWN = 60
BAR = 'holylois:restart'


def countdown():
    """Same countdown as 1.7.4 (boss bar, big numbers, goodbye title, kick); only the chat line differs."""
    original = previous.say
    previous.say = lambda text: original(text.replace('land claims on the map, zone titles, /support',
                                                      'a pack-only mod check, crown icons and clearer achievements'))
    try: previous.countdown()
    finally: previous.say = original


def main():
    assert os.geteuid() == 0, 'Run as root'
    old_extras = sorted(MODS.glob('holylois-extras-*.jar'))
    assert len(old_extras) == 1, old_extras
    assert old_extras[0].name != EXTRAS_NEW.name, 'Already deployed'
    for path in [EXTRAS_NEW, ADVANCEMENTS_NEW / 'pack.mcmeta', MODLIST_NEW, ICON_NEW, ADVANCEMENTS, MOTD, PACK_MINIMUM]:
        assert path.exists(), path
    allowed = json.loads(MODLIST_NEW.read_text())
    assert allowed['mode'] == 'enforce' and 'holylois-extras' in allowed['allowed'] and len(allowed['allowed']) > 150 and allowed['exempt'], 'Mod list looks wrong'
    assert 'Step inside an underground dungeon' in (ADVANCEMENTS_NEW / 'data/holylois/advancement/explore/dungeon_delver.json').read_text(), 'Advancements are not the 1.7.8 set'
    assert shutil.disk_usage(ROOT).free > 8 * 1024**3, 'Less than 8 GB free'
    countdown()

    stamp = datetime.datetime.now(datetime.timezone.utc).strftime('%Y%m%dT%H%M%SZ')
    backup = Path('/opt/minecraft-backups/maintenance') / ('release178-' + stamp)
    backup.mkdir(mode=0o700)
    MAINTENANCE.touch()
    run('systemctl', 'stop', 'minecraft-console.socket', 'minecraft.service')
    installed = []
    had_modlist = MODLIST.exists()
    saved = [*old_extras, MOTD, *([MODLIST] if had_modlist else []), *([ICON] if ICON.exists() else [])]
    try:
        archive = backup / 'complete-server.tar.gz'
        run('tar', '--exclude=minecraft/backups', '-czf', str(archive), '-C', '/opt', 'minecraft')
        archive.chmod(0o600)
        run('tar', '-tzf', str(archive), stdout=subprocess.DEVNULL)
        for path in saved: shutil.copy2(path, backup / path.name)
        shutil.copytree(ADVANCEMENTS, backup / 'holylois-advancements')

        target = MODS / EXTRAS_NEW.name
        run('install', '-o', 'minecraft', '-g', 'minecraft', '-m', '644', str(EXTRAS_NEW), str(target))
        installed.append(target)
        for old in old_extras: old.unlink()
        shutil.rmtree(ADVANCEMENTS); shutil.copytree(ADVANCEMENTS_NEW, ADVANCEMENTS)
        run('install', '-o', 'minecraft', '-g', 'minecraft', '-m', '644', str(MODLIST_NEW), str(MODLIST))
        run('install', '-o', 'minecraft', '-g', 'minecraft', '-m', '644', str(ICON_NEW), str(ICON))
        motd, count = re.subn(r'(?m)^(\s*line2=).*$', lambda m: m.group(1) + json.dumps(HEADLINE, ensure_ascii=False), MOTD.read_text(encoding='utf-8'), count=1)
        assert count == 1, 'MOTD line2 not found'
        MOTD.write_text(motd, encoding='utf-8')
        run('chown', '-R', 'minecraft:minecraft', str(ADVANCEMENTS), str(MOTD))

        since = time.strftime('%Y-%m-%d %H:%M:%S')
        run('systemctl', 'start', 'minecraft-console.socket', 'minecraft.service')
        log = wait_for_start(since)
        for needle in ['holylois-extras 1.4.0', 'holylois_boombox', 'Holy Lois discoveries']:
            assert needle in log, 'Not loaded: ' + needle
        assert 'Registry loading errors' not in log, 'A datapack failed to load'
    except Exception:
        subprocess.run(['systemctl', 'stop', 'minecraft-console.socket', 'minecraft.service'])
        for target in installed: target.unlink(missing_ok=True)
        for path in saved:
            source = backup / path.name
            if source.exists(): shutil.copy2(source, path); subprocess.run(['chown', 'minecraft:minecraft', str(path)])
        if not had_modlist: MODLIST.unlink(missing_ok=True)
        if (backup / 'holylois-advancements').exists():
            shutil.rmtree(ADVANCEMENTS, ignore_errors=True); shutil.copytree(backup / 'holylois-advancements', ADVANCEMENTS)
            subprocess.run(['chown', '-R', 'minecraft:minecraft', str(ADVANCEMENTS)])
        subprocess.run(['systemctl', 'start', 'minecraft-console.socket', 'minecraft.service'])
        MAINTENANCE.unlink(missing_ok=True)
        print('Rolled back to the previous mods and settings. Backup kept at', backup)
        raise

    console(f'bossbar remove {BAR}', 'gamerule send_command_feedback true')
    MAINTENANCE.unlink(missing_ok=True)
    message = ("**Holy Lois 1.7.8 is live: one pack for everyone!** Close Minecraft, open the launcher and click Update.\n"
               "- The server now only lets the Holy Lois pack in: extra mods are turned away with a message that says how to fix it, "
               "and the launcher's Play button tidies the folder for you. Shaders and resource packs stay yours\n"
               "- New crown icon on the game window, crisp at every size, and a new server icon\n"
               "- Clearer achievement texts: Discoverer, Dungeon Delver, Deeper Still, Odd Pillar")
    result = subprocess.run(['python3', str(ALERT), 'message', message], capture_output=True, text=True)
    receipt = {'release': 'pack 1.7.8 server', 'backup': str(archive), 'extras': '1.4.0', 'mod_list_ids': len(allowed['allowed']),
               'motd': HEADLINE, 'discord': 'ok' if result.returncode == 0 else result.stderr.strip()[:200], 'result': 'Done'}
    (backup / 'receipt.json').write_text(json.dumps(receipt, indent=2, ensure_ascii=False) + '\n')
    print(json.dumps(receipt, indent=2, ensure_ascii=False))
    subprocess.run(['systemd-run', '--on-active=900', '--unit=holylois-offload-release178', 'systemctl', 'start', 'holylois-offsite-backup.service'])


if __name__ == '__main__':
    main()
