"""Holy Lois server release for pack 1.7.2. Run as root on the server from ~/hl-172.

Onboarding 1.6.0 (daily coin [Claim] button and streak bar, /support, new achievement hooks), Holy Lois Extras 1.1.0
(boombox you can set down, music pause signal, instant stop when dropped; both sides) and the updated achievement
datapack. The server list line announces the update. The owner allowed a restart with players online after a
countdown (2026-10-04), so online players get a five-minute warning instead of a refusal. A complete verified backup
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
MAINTENANCE = Path('/run/holylois-maintenance')
ALERT = Path('/usr/local/lib/holylois/discord-alert.py')
# Server list line under the name: always the newest exciting change.
HEADLINE = '<#FFAD42>✦ New:</#FFAD42> <white>set your boombox down and party!</white>'
WARNINGS = [(300, '5 minutes'), (120, '2 minutes'), (60, '1 minute'), (30, '30 seconds'), (10, '10 seconds')]


def say(text):
    line = json.dumps([{'text': '[Holy Lois] ', 'color': 'gold', 'bold': True}, {'text': text, 'color': 'yellow', 'bold': False}])
    with FIFO.open('w') as stream: stream.write('tellraw @a ' + line + '\n')


def countdown():
    if online_players() == 0: return
    start = time.monotonic(); total = WARNINGS[0][0]
    for left, label in WARNINGS:
        time.sleep(max(0, total - left - (time.monotonic() - start)))
        say(f'Server restarts in {label} for a quick update (boombox you can set down, achievement tab fix). '
            'Afterwards close Minecraft and open the Holy Lois launcher to update.')
        if online_players() == 0: return
    time.sleep(max(0, total - (time.monotonic() - start)))


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
    saved = [*old_onboarding, *old_extras, MOTD]
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
