"""Holy Lois server release for pack 1.7.2. Run as root on the server from ~/hl-172.

Onboarding 1.6.0 (daily coin [Claim] button and streak bar, /support, new achievement hooks), Holy Lois Extras 1.1.0
(boombox you can set down, music pause signal, instant stop when dropped; both sides) and the updated achievement
datapack. The server list line announces the update. The owner allowed a restart with players online after a
countdown (2026-10-04), so online players get a one-minute warning instead of a refusal. A complete verified backup
comes first and the previous files return automatically if the server does not start.
"""
import datetime, json, os, re, shutil, subprocess, sys, time
from pathlib import Path

sys.path.insert(0, '/home/ubuntu/hl-170')
from importlib import util
spec = util.spec_from_file_location('previous', '/home/ubuntu/hl-170/deploy-release-170.py'); previous = util.module_from_spec(spec); spec.loader.exec_module(previous)
online_players, journal, wait_for_start, run = previous.online_players, previous.journal, previous.wait_for_start, previous.run

HOME = Path('/home/ubuntu/hl-172')
ROOT = Path('/opt/minecraft')
MODS = ROOT / 'mods'
ONBOARDING_NEW = Path('/home/ubuntu/holylois-build-160/holylois-onboarding-1.6.0+26.3.jar')
EXTRAS_NEW = Path('/home/ubuntu/holylois-extras-110/holylois-extras-1.1.0+26.3.jar')
ADVANCEMENTS = ROOT / 'world/datapacks/holylois-advancements'
FIFO = Path('/run/minecraft-console.fifo')
MOTD = ROOT / 'config/MiniMOTD/main.conf'
STYLE = ROOT / 'config/styledplayerlist/styles/holylois.json'
MAINTENANCE = Path('/run/holylois-maintenance')
ALERT = Path('/usr/local/lib/holylois/discord-alert.py')
# Server list line under the name: always the newest exciting change.
HEADLINE = '<#FFAD42>✦ New:</#FFAD42> <white>set your boombox down and party!</white>'
COUNTDOWN = 60  # seconds; the owner asked for one minute on 2026-10-04
RULE = '<color #5a5a5a><strikethrough>{}</strikethrough></color>'


def wider_tab(style):
    """Tab list: longer divider lines and a little padding, so text no longer touches the edges."""
    def line(text):
        if 'strikethrough' in text:
            return text.replace(RULE.format(' ' * 14) + RULE.format(' ' * 14), RULE.format(' ' * 64)).replace(RULE.format(' ' * 14), RULE.format(' ' * 22))
        return '    ' + text + '    ' if text else text
    style['list_header'] = [line(x) for x in style['list_header']]
    style['list_footer']['values'] = [[line(x) for x in page] for page in style['list_footer']['values']]
    return style


def console(*commands):
    with FIFO.open('w') as stream:
        for command in commands: stream.write(command + '\n')


def say(text):
    console('tellraw @a ' + json.dumps([{'text': '[Holy Lois] ', 'color': 'gold', 'bold': True}, {'text': text, 'color': 'yellow', 'bold': False}]))


def countdown():
    """A boss bar at the top of the screen counts down; chat reminders at the start, 30 s and 10 s; big numbers for the last 10 s."""
    if online_players() == 0: return
    bar = 'holylois:restart'
    console(f'bossbar remove {bar}', f'bossbar add {bar} ' + json.dumps({'text': 'Server restart for an update'}),
            f'bossbar set {bar} max {COUNTDOWN}', f'bossbar set {bar} value {COUNTDOWN}', f'bossbar set {bar} color yellow',
            f'bossbar set {bar} style notched_10', f'bossbar set {bar} players @a', 'title @a times 0 25 5')
    start = time.monotonic()
    for left in range(COUNTDOWN, 0, -1):
        time.sleep(max(0, COUNTDOWN - left - (time.monotonic() - start)))
        label = f'{left} second{"s" if left != 1 else ""}'
        commands = [f'bossbar set {bar} value {left}', f'bossbar set {bar} players @a',
                    f'bossbar set {bar} name ' + json.dumps({'text': f'Server restarting in {label} - update after with the launcher', 'color': 'yellow' if left > 10 else 'red'})]
        if left == 10: commands.append(f'bossbar set {bar} color red')
        if left <= 10:
            commands += ['title @a subtitle ' + json.dumps({'text': 'Then open the Holy Lois launcher and click Update', 'color': 'yellow'}),
                         'title @a title ' + json.dumps({'text': str(left), 'color': 'gold', 'bold': True}),
                         'execute as @a at @s run playsound minecraft:block.note_block.hat master @s ~ ~ ~ 1 ' + ('2' if left <= 3 else '1')]
        console(*commands)
        if left in (COUNTDOWN, 30, 10):
            say(f'Server restarts in {label} for an update: boomboxes you can set down, achievement tabs fixed, daily coin button. '
                'Afterwards close Minecraft and open the Holy Lois launcher to update.')
    console('title @a title ' + json.dumps({'text': 'Maaarek nahhul!', 'color': 'gold', 'bold': True}),
            'title @a subtitle ' + json.dumps({'text': 'Back in a few minutes', 'color': 'yellow'}))
    time.sleep(2)


def main():
    assert os.geteuid() == 0, 'Run as root'
    old_onboarding = sorted(MODS.glob('holylois-onboarding-*.jar')); old_extras = sorted(MODS.glob('holylois-extras-*.jar'))
    assert len(old_onboarding) == 1 and len(old_extras) == 1, (old_onboarding, old_extras)
    assert ONBOARDING_NEW.exists() and EXTRAS_NEW.exists() and (HOME / 'holylois-advancements/pack.mcmeta').exists()
    assert ADVANCEMENTS.exists() and MOTD.exists()
    assert shutil.disk_usage(ROOT).free > 8 * 1024**3, 'Less than 8 GB free'
    # The staged 1.5.0 swap is superseded: 1.6.0 contains the same fixes.
    subprocess.run(['systemctl', 'stop', 'holylois-apply-onboarding'], stderr=subprocess.DEVNULL)
    countdown()

    stamp = datetime.datetime.now(datetime.timezone.utc).strftime('%Y%m%dT%H%M%SZ')
    backup = Path('/opt/minecraft-backups/maintenance') / ('release172-' + stamp)
    backup.mkdir(mode=0o700)
    MAINTENANCE.touch()
    run('systemctl', 'stop', 'minecraft-console.socket', 'minecraft.service')
    installed = []
    saved = [*old_onboarding, *old_extras, MOTD, STYLE]
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
        for old in old_onboarding + old_extras:
            if old not in installed: old.unlink()
        shutil.rmtree(ADVANCEMENTS)
        shutil.copytree(HOME / 'holylois-advancements', ADVANCEMENTS)
        run('chown', '-R', 'minecraft:minecraft', str(ADVANCEMENTS))
        motd, count = re.subn(r'(?m)^(\s*line2=).*$', lambda m: m.group(1) + json.dumps(HEADLINE, ensure_ascii=False), MOTD.read_text(encoding='utf-8'), count=1)
        assert count == 1, 'MOTD line2 not found'
        MOTD.write_text(motd, encoding='utf-8')
        style = json.loads(STYLE.read_text(encoding='utf-8'))
        if RULE.format(' ' * 64) not in json.dumps(style, ensure_ascii=False):
            STYLE.write_text(json.dumps(wider_tab(style), indent=2, ensure_ascii=False) + '\n', encoding='utf-8')

        since = time.strftime('%Y-%m-%d %H:%M:%S')
        run('systemctl', 'start', 'minecraft-console.socket', 'minecraft.service')
        log = wait_for_start(since)
        for needle in ['holylois-onboarding 1.6.0', 'holylois-extras 1.1.0', 'holylois_boombox', 'Holy Lois name day', 'Holy Lois discoveries']:
            assert needle in log, 'Not loaded: ' + needle
        assert 'Registry loading errors' not in log, 'A datapack failed to load'
        assert not re.search(r"Couldn't (parse|load).*holylois", log), 'A Holy Lois advancement failed to load'
    except Exception:
        subprocess.run(['systemctl', 'stop', 'minecraft-console.socket', 'minecraft.service'])
        for target in installed: target.unlink(missing_ok=True)
        for path in saved:
            shutil.copy2(backup / path.name, path); subprocess.run(['chown', 'minecraft:minecraft', str(path)])
        if (backup / 'holylois-advancements').exists():
            shutil.rmtree(ADVANCEMENTS, ignore_errors=True); shutil.copytree(backup / 'holylois-advancements', ADVANCEMENTS)
            subprocess.run(['chown', '-R', 'minecraft:minecraft', str(ADVANCEMENTS)])
        subprocess.run(['systemctl', 'start', 'minecraft-console.socket', 'minecraft.service'])
        MAINTENANCE.unlink(missing_ok=True)
        print('Rolled back to the previous mods and settings. Backup kept at', backup)
        raise

    MAINTENANCE.unlink(missing_ok=True)
    message = ("**Maaarek nahhul!** Holy Lois 1.7.2 is live. Close Minecraft, open the launcher and click Update.\n"
               "- Boombox: set it down on any block and it keeps playing for everyone nearby\n"
               "- Game music pauses while a boombox plays near you\n"
               "- Achievement tabs work again (Num Lock bug) and Holy Lois comes first\n"
               "- Daily coins get a [Claim] button when you log in, plus seven new achievements\n"
               "- Recipe viewer stays out of the way until you search; plain tools are used until they break\n"
               "- /support if you ever want to chip in (never buys anything in game)")
    result = subprocess.run(['python3', str(ALERT), 'message', message], capture_output=True, text=True)
    receipt = {'release': 'pack 1.7.2 server', 'backup': str(archive), 'onboarding': '1.6.0', 'extras': '1.1.0', 'motd': HEADLINE,
               'discord': 'ok' if result.returncode == 0 else result.stderr.strip()[:200], 'result': 'Done'}
    (backup / 'receipt.json').write_text(json.dumps(receipt, indent=2, ensure_ascii=False) + '\n')
    print(json.dumps(receipt, indent=2, ensure_ascii=False))


if __name__ == '__main__':
    main()
