"""Holy Lois server step for pack 1.7.11. Run as root on the server from ~/hl-1711 (copy deploy-release-1711.py there).

Pack 1.7.11 only removes Quick Play: the client part of Holy Lois Extras (QuickPlayClient) is gone in extras 1.5.1. The server keeps
extras 1.5.0, which behaves the same on a server (QuickPlayClient was a client entrypoint), so there is no restart and no countdown.
This step only replaces the MOTD headline that still promised Quick Play, reloads MiniMOTD and posts the Discord note.
The old main.conf is kept in the maintenance folder; if the reload fails the old file goes back.
"""
import datetime, json, re, shutil, subprocess, sys, time
from pathlib import Path

from importlib import util
spec = util.spec_from_file_location('previous', '/home/ubuntu/hl-174/deploy-release-174.py'); previous = util.module_from_spec(spec); spec.loader.exec_module(previous)
console, run = previous.console, previous.run

ROOT = Path('/opt/minecraft')
MOTD = ROOT / 'config/MiniMOTD/main.conf'
ALERT = Path('/usr/local/lib/holylois/discord-alert.py')
# Server list line under the name: always the newest exciting change, capital letter after "New:".
OLD_HEADLINE = 'Quick Play, one click and you are in!'
HEADLINE = '<#FFAD42>✦ New:</#FFAD42> <white>A secret code hides on holylois.com, /redeem it!</white>'


def main():
    assert subprocess.run(['id', '-u'], capture_output=True, text=True).stdout.strip() == '0', 'Run as root'
    text = MOTD.read_text(encoding='utf-8')
    assert re.search(r'(?m)^\s*line2=', text), 'MOTD line2 not found'
    assert OLD_HEADLINE in text, 'MOTD is not the 1.7.10 headline (already changed?)'
    assert sorted(p.name for p in (ROOT / 'mods').glob('holylois-extras-*.jar')) == ['holylois-extras-1.5.0+26.3.jar'], 'Server extras is not 1.5.0'
    assert subprocess.run(['systemctl', 'is-active', '--quiet', 'minecraft']).returncode == 0, 'Server is not running'
    if sys.argv[1:] == ['--check']:
        print('All pre-checks passed; nothing was changed.')
        return

    stamp = datetime.datetime.now(datetime.timezone.utc).strftime('%Y%m%dT%H%M%SZ')
    backup = Path('/opt/minecraft-backups/maintenance') / ('release1711-' + stamp)
    backup.mkdir(mode=0o700)
    shutil.copy2(MOTD, backup / MOTD.name)
    motd, count = re.subn(r'(?m)^(\s*line2=).*$', lambda m: m.group(1) + json.dumps(HEADLINE, ensure_ascii=False), text, count=1)
    assert count == 1
    since = time.strftime('%Y-%m-%d %H:%M:%S')
    try:
        MOTD.write_text(motd, encoding='utf-8'); run('chown', 'minecraft:minecraft', str(MOTD))
        console('minimotd reload')
        time.sleep(4)
        log = subprocess.run(['journalctl', '-u', 'minecraft', '--since', since, '--no-pager', '-o', 'cat'], capture_output=True, text=True).stdout
        assert 'Unknown or incomplete command' not in log and 'Exception' not in log, 'MiniMOTD reload failed:\n' + log[-1500:]
    except Exception:
        shutil.copy2(backup / MOTD.name, MOTD); subprocess.run(['chown', 'minecraft:minecraft', str(MOTD)])
        console('minimotd reload')
        (backup / 'receipt.json').write_text(json.dumps({'release': 'pack 1.7.11 server', 'result': 'Rolled back, old MOTD restored'}, indent=2) + '\n')
        print('Put the old MOTD back. Backup kept at', backup)
        raise

    message = ("**Holy Lois 1.7.11: Quick Play is gone.** Close Minecraft, open the launcher and click Update.\n"
               "- Quick Play never joined the server by itself, so it is removed. Play opens your Minecraft launcher as before: "
               "pick Holy Lois: Reborn, then join Holy Lois from Multiplayer (singleplayer works too)\n"
               "- Launcher 1.2.7 drops the Quick Play setting. A real one-click start (the launcher starts the game itself) is coming later\n"
               "- No server restart for this one, you can stay online")
    result = subprocess.run(['python3', str(ALERT), 'message', message], capture_output=True, text=True)
    receipt = {'release': 'pack 1.7.11 server', 'extras_on_server': '1.5.0 (unchanged, same server behavior as 1.5.1)', 'restart': False,
               'motd': HEADLINE, 'discord': 'ok' if result.returncode == 0 else result.stderr.strip()[:200], 'result': 'Done'}
    (backup / 'receipt.json').write_text(json.dumps(receipt, indent=2, ensure_ascii=False) + '\n')
    print(json.dumps(receipt, indent=2, ensure_ascii=False))


if __name__ == '__main__':
    main()
