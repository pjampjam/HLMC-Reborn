"""Holy Lois server hotfix for pack 1.7.3. Run as root on the server from ~/hl-173.

Onboarding 1.6.1 (/support lists TRON, labels Bitcoin SegWit, explains each network on hover) and Holy Lois Extras 1.1.1
(achievement tabs take a left click again, placed boombox texture; both sides). Also: removes the restart boss bar that
1.7.2 left saved in the world, capitalises the server list headline, installs the stats feed that masks offensive names
instead of hiding them, writes SkinsRestorer translations without em dashes, and moves the profiles the owner asked to delete (2026-10-04) into the backup folder.
Online players get a one-minute countdown (owner's choice). A complete verified backup comes first and everything returns
automatically if the server does not start.
"""
import datetime, json, os, re, shutil, subprocess, sys, time
from pathlib import Path

from importlib import util
spec = util.spec_from_file_location('previous', '/home/ubuntu/hl-170/deploy-release-170.py'); previous = util.module_from_spec(spec); spec.loader.exec_module(previous)
online_players, wait_for_start, run = previous.online_players, previous.wait_for_start, previous.run

HOME = Path('/home/ubuntu/hl-173')
ROOT = Path('/opt/minecraft')
WORLD = ROOT / 'world'
MODS = ROOT / 'mods'
ONBOARDING_NEW = Path('/home/ubuntu/holylois-build-161/holylois-onboarding-1.6.1+26.3.jar')
EXTRAS_NEW = Path('/home/ubuntu/holylois-extras-111/holylois-extras-1.1.1+26.3.jar')
STATS_NEW = HOME / 'make-stats.py'
STATS = Path('/usr/local/lib/holylois/make-stats.py')
FIFO = Path('/run/minecraft-console.fifo')
MOTD = ROOT / 'config/MiniMOTD/main.conf'
MAINTENANCE = Path('/run/holylois-maintenance')
ALERT = Path('/usr/local/lib/holylois/discord-alert.py')
# Server list line under the name: always the newest exciting change, capital letter after "New:".
HEADLINE = '<#FFAD42>✦ New:</#FFAD42> <white>Set your boombox down and party!</white>'
COUNTDOWN = 60
BAR = 'holylois:restart'
# Old test and duplicate accounts the owner asked to delete. pjampjam and the player who will rename stay.
REMOVE = {'6d9080bd-7e5d-3b46-a5ee-71c46f64afe4': 'normTesterHolyMa', '60706dd5-2f06-38bc-b252-cb08a5e9d6f6': 'MarekNahui',
          'e23aa66e-721b-3e6f-9f29-7b248454a16c': 'NormundsLilPidor'}


def console(*commands):
    with FIFO.open('w') as stream:
        for command in commands: stream.write(command + '\n')


def say(text):
    console('tellraw @a ' + json.dumps([{'text': '[Holy Lois] ', 'color': 'gold', 'bold': True}, {'text': text, 'color': 'yellow', 'bold': False}]))


def countdown():
    """Boss bar countdown with chat at 60/30/10 s and big numbers for the last 10 s. Command feedback is off meanwhile so
    ops do not see every bossbar command; the bar is removed at the end because custom boss bars are saved in the world."""
    console(f'bossbar remove {BAR}')
    if online_players() == 0: return
    console('gamerule send_command_feedback false', f'bossbar add {BAR} ' + json.dumps({'text': 'Server restart for an update'}),
            f'bossbar set {BAR} max {COUNTDOWN}', f'bossbar set {BAR} value {COUNTDOWN}', f'bossbar set {BAR} color yellow',
            f'bossbar set {BAR} style notched_10', f'bossbar set {BAR} players @a', 'title @a times 0 25 5')
    start = time.monotonic()
    for left in range(COUNTDOWN, 0, -1):
        time.sleep(max(0, COUNTDOWN - left - (time.monotonic() - start)))
        label = f'{left} second{"s" if left != 1 else ""}'
        commands = [f'bossbar set {BAR} value {left}', f'bossbar set {BAR} players @a',
                    f'bossbar set {BAR} name ' + json.dumps({'text': f'Server restarting in {label} - update after with the launcher', 'color': 'yellow' if left > 10 else 'red'})]
        if left == 10: commands.append(f'bossbar set {BAR} color red')
        if left <= 10:
            commands += ['title @a subtitle ' + json.dumps({'text': 'Then open the Holy Lois launcher and click Update', 'color': 'yellow'}),
                         'title @a title ' + json.dumps({'text': str(left), 'color': 'gold', 'bold': True}),
                         'execute as @a at @s run playsound minecraft:block.note_block.hat master @s ~ ~ ~ 1 ' + ('2' if left <= 3 else '1')]
        console(*commands)
        if left in (COUNTDOWN, 30, 10):
            say(f'Server restarts in {label} for a quick fix: achievement tabs and the placed boombox. '
                'Afterwards close Minecraft and open the Holy Lois launcher to update.')
    console(f'bossbar remove {BAR}', 'gamerule send_command_feedback true',
            'title @a title ' + json.dumps({'text': 'Maaarek nahhul!', 'color': 'gold', 'bold': True}),
            'title @a subtitle ' + json.dumps({'text': 'Back in a few minutes', 'color': 'yellow'}))
    time.sleep(2)


def profile_files(uuid):
    return [p for p in [WORLD / f'players/data/{uuid}.dat', WORLD / f'players/data/{uuid}.dat_old', WORLD / f'players/advancements/{uuid}.json',
                        WORLD / f'players/stats/{uuid}.json', WORLD / f'players/data/claimData/{uuid}.json',
                        WORLD / f'ec_player_profiles/{uuid}.dat', WORLD / f'modplayerdata/{uuid}.dat'] if p.exists()]


def remove_profiles(backup, moved):
    """Move the listed players' files into the backup (not deleted) and drop them from usercache and onboarding."""
    target = backup / 'removed-profiles'; target.mkdir()
    for uuid in REMOVE:
        for path in profile_files(uuid):
            dest = target / path.relative_to(WORLD); dest.parent.mkdir(parents=True, exist_ok=True)
            shutil.move(path, dest); moved.append((path, dest))
    cache = ROOT / 'usercache.json'
    entries = json.loads(cache.read_text(encoding='utf-8'))
    cache.write_text(json.dumps([e for e in entries if e.get('uuid') not in REMOVE]), encoding='utf-8')
    onboarding = WORLD / 'holylois/onboarding.json'
    data = json.loads(onboarding.read_text(encoding='utf-8'))
    for key in ('completed', 'pending'): data[key] = [u for u in data.get(key, []) if u not in REMOVE]
    onboarding.write_text(json.dumps(data, indent=2), encoding='utf-8')


def plain_dash_locales():
    """No em dashes in player-facing text: SkinsRestorer prefers a full copy in locales/custom over its repository file."""
    base = ROOT / 'config/skinsrestorer/locales'
    written = []
    for source in sorted((base / 'repository').glob('locale_*.json')):
        text = source.read_text(encoding='utf-8')
        target = base / 'custom' / source.name
        if '\u2014' in text and not target.exists():
            target.write_text(text.replace('\u2014', '-'), encoding='utf-8'); written.append(target)
    return written


def main():
    assert os.geteuid() == 0, 'Run as root'
    old_onboarding = sorted(MODS.glob('holylois-onboarding-*.jar')); old_extras = sorted(MODS.glob('holylois-extras-*.jar'))
    assert len(old_onboarding) == 1 and len(old_extras) == 1, (old_onboarding, old_extras)
    assert ONBOARDING_NEW.exists() and EXTRAS_NEW.exists() and STATS_NEW.exists() and MOTD.exists()
    assert shutil.disk_usage(ROOT).free > 8 * 1024**3, 'Less than 8 GB free'
    countdown()

    stamp = datetime.datetime.now(datetime.timezone.utc).strftime('%Y%m%dT%H%M%SZ')
    backup = Path('/opt/minecraft-backups/maintenance') / ('release173-' + stamp)
    backup.mkdir(mode=0o700)
    MAINTENANCE.touch()
    run('systemctl', 'stop', 'minecraft-console.socket', 'minecraft.service')
    installed, moved = [], []
    saved = [*old_onboarding, *old_extras, MOTD, STATS, ROOT / 'usercache.json', WORLD / 'holylois/onboarding.json']
    try:
        archive = backup / 'complete-server.tar.gz'
        run('tar', '--exclude=minecraft/backups', '-czf', str(archive), '-C', '/opt', 'minecraft')
        archive.chmod(0o600)
        run('tar', '-tzf', str(archive), stdout=subprocess.DEVNULL)
        for path in saved: shutil.copy2(path, backup / path.name)

        for jar in [ONBOARDING_NEW, EXTRAS_NEW]:
            target = MODS / jar.name
            run('install', '-o', 'minecraft', '-g', 'minecraft', '-m', '644', str(jar), str(target))
            installed.append(target)
        for old in old_onboarding + old_extras:
            if old not in installed: old.unlink()
        motd, count = re.subn(r'(?m)^(\s*line2=).*$', lambda m: m.group(1) + json.dumps(HEADLINE, ensure_ascii=False), MOTD.read_text(encoding='utf-8'), count=1)
        assert count == 1, 'MOTD line2 not found'
        MOTD.write_text(motd, encoding='utf-8')
        remove_profiles(backup, moved)
        installed += plain_dash_locales()
        run('chown', 'minecraft:minecraft', str(ROOT / 'usercache.json'), str(WORLD / 'holylois/onboarding.json'), str(MOTD), *map(str, installed))
        run('install', '-m', '755', str(STATS_NEW), str(STATS))

        since = time.strftime('%Y-%m-%d %H:%M:%S')
        run('systemctl', 'start', 'minecraft-console.socket', 'minecraft.service')
        log = wait_for_start(since)
        for needle in ['holylois-onboarding 1.6.1', 'holylois-extras 1.1.1', 'holylois_boombox', 'Holy Lois name day', 'Holy Lois discoveries']:
            assert needle in log, 'Not loaded: ' + needle
        assert 'Registry loading errors' not in log, 'A datapack failed to load'
    except Exception:
        subprocess.run(['systemctl', 'stop', 'minecraft-console.socket', 'minecraft.service'])
        for target in installed: target.unlink(missing_ok=True)
        for path, dest in moved: shutil.move(dest, path)
        for path in saved:
            if (backup / path.name).exists(): shutil.copy2(backup / path.name, path)
            if path.is_relative_to(ROOT): subprocess.run(['chown', 'minecraft:minecraft', str(path)])
        subprocess.run(['chown', '-R', 'minecraft:minecraft', str(WORLD / 'players'), str(WORLD / 'ec_player_profiles'), str(WORLD / 'modplayerdata')])
        subprocess.run(['systemctl', 'start', 'minecraft-console.socket', 'minecraft.service'])
        MAINTENANCE.unlink(missing_ok=True)
        print('Rolled back to the previous mods, settings and profiles. Backup kept at', backup)
        raise

    # Logins live in EasyAuth's database; its own command removes them (no direct database edits).
    console(f'bossbar remove {BAR}', 'gamerule send_command_feedback true', *(f'auth remove {name}' for name in REMOVE.values()))
    MAINTENANCE.unlink(missing_ok=True)
    subprocess.run(['systemctl', 'start', 'holylois-stats.service'])
    message = ("**Quick fix: Holy Lois 1.7.3 is live.** Close Minecraft, open the launcher and click Update.\n"
               "- Achievement tabs switch with a click again (1.7.2 broke them, sorry)\n"
               "- A placed boombox looks like a boombox instead of a pink cube\n"
               "- /support explains each crypto network when you hover it")
    result = subprocess.run(['python3', str(ALERT), 'message', message], capture_output=True, text=True)
    receipt = {'release': 'pack 1.7.3 server', 'backup': str(archive), 'onboarding': '1.6.1', 'extras': '1.1.1', 'motd': HEADLINE,
               'profiles_moved': sorted(REMOVE.values()), 'files_moved': len(moved),
               'discord': 'ok' if result.returncode == 0 else result.stderr.strip()[:200], 'result': 'Done'}
    (backup / 'receipt.json').write_text(json.dumps(receipt, indent=2, ensure_ascii=False) + '\n')
    print(json.dumps(receipt, indent=2, ensure_ascii=False))


if __name__ == '__main__':
    main()
