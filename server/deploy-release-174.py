"""Holy Lois server release for pack 1.7.4 ("Land and zones"). Run as root on the server from ~/hl-174.

- Open Parties and Claims replaces Flan (no Flan claims existed): chunk claims on the Xaero world map, parties, claim
  protection. config/openpartiesandclaims-server.toml: 16 free chunks, 2 forceloads, OPAC welcome messages off
  (Holy Lois Extras shows zone titles instead).
- Onboarding 1.7.0: /claims (earned and bought chunks), claim-safe /rtp (Essential Commands' rtp is switched off),
  PvP combat tag, death loot without Flan, /donate (wallets), /support and /report to Discord.
- Holy Lois Extras 1.2.0 (both sides): zone titles, no minimap death marker after a PvP death.
- Discord bot: #support channel with "On my way" / "Solved" buttons.
- Backups live on Google Drive (owner decision): Just Enough Backups keeps only the newest full + 2 differentials
  locally, the off-site job runs every 3 hours and also uploads, verifies and then deletes release backups. This
  release's own backup is offloaded 15 minutes after a successful start.
Online players get a one-minute countdown, then a kick with a Holy Lois message. A complete verified backup comes first
and everything returns automatically if the server does not start.
"""
import datetime, json, os, re, shutil, subprocess, sys, time
from pathlib import Path

from importlib import util
spec = util.spec_from_file_location('previous', '/home/ubuntu/hl-170/deploy-release-170.py'); previous = util.module_from_spec(spec); spec.loader.exec_module(previous)
online_players, wait_for_start, run = previous.online_players, previous.wait_for_start, previous.run

HOME = Path('/home/ubuntu/hl-174')
ROOT = Path('/opt/minecraft')
MODS = ROOT / 'mods'
ONBOARDING_NEW = Path('/home/ubuntu/holylois-build-170/holylois-onboarding-1.7.0+26.3.jar')
EXTRAS_NEW = Path('/home/ubuntu/holylois-extras-120/holylois-extras-1.2.0+26.3.jar')
OPAC_NEW = HOME / 'open-parties-and-claims-fabric-26.3-0.31.6.jar'
OPAC_CONFIG_NEW = HOME / 'openpartiesandclaims-server.toml'
OPAC_CONFIG = ROOT / 'config/openpartiesandclaims-server.toml'
ESSENTIALS = ROOT / 'config/EssentialCommands.properties'
RULES_TXT = ROOT / 'config/essentialcommands/rules.txt'
RULES_MD_NEW, RULES_MD = HOME / 'RULES.md', Path('/opt/holylois-bot/RULES.md')
OLD_CLAIM_RULE, NEW_CLAIM_RULE = 'Claim your land with a golden hoe, then /flan menu.', 'Claim your land on the map (M, right-click a chunk), see /claims.'
BOT_NEW = HOME / 'bot.py'
JEB_CONFIG = ROOT / 'config/justenoughbackups.json'
OFFSITE_NEW, OFFSITE = HOME / 'offsite-backup.py', Path('/usr/local/lib/holylois/offsite-backup.py')
TIMER_NEW, TIMER = HOME / 'holylois-offsite-backup.timer', Path('/etc/systemd/system/holylois-offsite-backup.timer')
BOT = Path('/opt/holylois-bot/bot.py')
FIFO = Path('/run/minecraft-console.fifo')
MOTD = ROOT / 'config/MiniMOTD/main.conf'
MAINTENANCE = Path('/run/holylois-maintenance')
ALERT = Path('/usr/local/lib/holylois/discord-alert.py')
# Server list line under the name: always the newest exciting change, capital letter after "New:".
HEADLINE = '<#FFAD42>✦ New:</#FFAD42> <white>Claim your land right on the map!</white>'
COUNTDOWN = 60
# World border: 14,000 blocks wide around spawn covers everything explored so far (x -6,650..4,600) with room to spare.
BORDER = 14000
BAR = 'holylois:restart'


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
            say(f'Server restarts in {label} for an update: land claims on the map, zone titles, /support. '
                'Afterwards close Minecraft and open the Holy Lois launcher to update.')
    # The goodbye title stays up until everyone is kicked with the same message (owner request), instead of the bare
    # "Server closed" screen a stop would show.
    console(f'bossbar remove {BAR}', 'gamerule send_command_feedback true', 'title @a times 0 200 0',
            'title @a subtitle ' + json.dumps({'text': 'Back in a few minutes', 'color': 'yellow'}),
            'title @a title ' + json.dumps({'text': 'Maaarek nahhul!', 'color': 'gold', 'bold': True}))
    time.sleep(3)
    console('kick @a Maaarek nahhul! The server is updating, back in a few minutes. '
            'Open the Holy Lois launcher and click Update before you rejoin.')
    time.sleep(2)


def main():
    assert os.geteuid() == 0, 'Run as root'
    old_onboarding = sorted(MODS.glob('holylois-onboarding-*.jar')); old_extras = sorted(MODS.glob('holylois-extras-*.jar'))
    old_flan = sorted(MODS.glob('flan-*.jar'))
    assert len(old_onboarding) == 1 and len(old_extras) == 1 and len(old_flan) == 1, (old_onboarding, old_extras, old_flan)
    assert not list(MODS.glob('open-parties-and-claims-*.jar')), 'OPAC is already installed'
    for path in [ONBOARDING_NEW, EXTRAS_NEW, OPAC_NEW, OPAC_CONFIG_NEW, BOT_NEW, MOTD, ESSENTIALS, JEB_CONFIG, OFFSITE_NEW, TIMER_NEW]: assert path.exists(), path
    assert 'enable_rtp=true' in ESSENTIALS.read_text(), 'Essential Commands rtp setting not found'
    assert OLD_CLAIM_RULE in RULES_TXT.read_text(encoding='utf-8') and RULES_MD_NEW.exists(), 'Rules text not as expected'
    assert shutil.disk_usage(ROOT).free > 8 * 1024**3, 'Less than 8 GB free'
    # Flan must not have real claims: they would be lost with the switch.
    for claims in (ROOT / 'world/dimensions').glob('*/*/data/claims'):
        assert not any(claims.iterdir()), f'Flan claims exist in {claims}'
    countdown()

    stamp = datetime.datetime.now(datetime.timezone.utc).strftime('%Y%m%dT%H%M%SZ')
    backup = Path('/opt/minecraft-backups/maintenance') / ('release174-' + stamp)
    backup.mkdir(mode=0o700)
    MAINTENANCE.touch()
    run('systemctl', 'stop', 'minecraft-console.socket', 'minecraft.service')
    installed = []
    saved = [*old_onboarding, *old_extras, *old_flan, MOTD, ESSENTIALS, JEB_CONFIG, RULES_TXT, BOT]
    try:
        archive = backup / 'complete-server.tar.gz'
        run('tar', '--exclude=minecraft/backups', '-czf', str(archive), '-C', '/opt', 'minecraft')
        archive.chmod(0o600)
        run('tar', '-tzf', str(archive), stdout=subprocess.DEVNULL)
        for path in saved: shutil.copy2(path, backup / path.name)

        for jar in [ONBOARDING_NEW, EXTRAS_NEW, OPAC_NEW]:
            target = MODS / jar.name
            run('install', '-o', 'minecraft', '-g', 'minecraft', '-m', '644', str(jar), str(target))
            installed.append(target)
        for old in old_onboarding + old_extras + old_flan:
            if old not in installed: old.unlink()
        run('install', '-o', 'minecraft', '-g', 'minecraft', '-m', '644', str(OPAC_CONFIG_NEW), str(OPAC_CONFIG))
        installed.append(OPAC_CONFIG)
        ESSENTIALS.write_text(ESSENTIALS.read_text().replace('enable_rtp=true', 'enable_rtp=false'))
        RULES_TXT.write_text(RULES_TXT.read_text(encoding='utf-8').replace(OLD_CLAIM_RULE, NEW_CLAIM_RULE), encoding='utf-8')
        motd, count = re.subn(r'(?m)^(\s*line2=).*$', lambda m: m.group(1) + json.dumps(HEADLINE, ensure_ascii=False), MOTD.read_text(encoding='utf-8'), count=1)
        assert count == 1, 'MOTD line2 not found'
        MOTD.write_text(motd, encoding='utf-8')
        jeb = json.loads(JEB_CONFIG.read_text())
        jeb['retention'].update({'full': 1, 'differential': 2, 'maxTotalSizeMb': 6144})
        jeb['automaticSchedule']['full']['intervalMinutes'] = 180
        jeb['automaticSchedule']['differential']['intervalMinutes'] = 30
        JEB_CONFIG.write_text(json.dumps(jeb, indent=2) + '\n')
        run('chown', 'minecraft:minecraft', str(MOTD), str(ESSENTIALS), str(JEB_CONFIG), str(RULES_TXT))

        since = time.strftime('%Y-%m-%d %H:%M:%S')
        run('systemctl', 'start', 'minecraft-console.socket', 'minecraft.service')
        log = wait_for_start(since)
        for needle in ['holylois-onboarding 1.7.0', 'holylois-extras 1.2.0', 'openpartiesandclaims 0.31.6', 'holylois_boombox',
                       'Loaded claims', 'Holy Lois claims: ready for OPAC', 'Holy Lois discoveries']:
            assert needle in log, 'Not loaded: ' + needle
        assert 'Registry loading errors' not in log, 'A datapack failed to load'
        assert not re.search(r'(?m)^\s+- flan ', log), 'Flan still loaded'
    except Exception:
        subprocess.run(['systemctl', 'stop', 'minecraft-console.socket', 'minecraft.service'])
        for target in installed: target.unlink(missing_ok=True)
        for path in saved:
            if (backup / path.name).exists() and path != BOT:
                shutil.copy2(backup / path.name, path); subprocess.run(['chown', 'minecraft:minecraft', str(path)])
        subprocess.run(['systemctl', 'start', 'minecraft-console.socket', 'minecraft.service'])
        MAINTENANCE.unlink(missing_ok=True)
        print('Rolled back to the previous mods and settings. Backup kept at', backup)
        raise

    console(f'bossbar remove {BAR}', 'gamerule send_command_feedback true', 'worldborder center 0 0', f'worldborder set {BORDER}',
            'worldborder warning distance 64')
    MAINTENANCE.unlink(missing_ok=True)
    # The bot only reads the log and writes to the console, so it can update after the server is up.
    run('install', '-m', '644', str(BOT_NEW), str(BOT))
    run('install', '-m', '644', str(RULES_MD_NEW), str(RULES_MD))
    subprocess.run(['systemctl', 'restart', 'holylois-discord-bot'])
    run('install', '-m', '755', str(OFFSITE_NEW), str(OFFSITE))
    run('install', '-m', '644', str(TIMER_NEW), str(TIMER))
    run('systemctl', 'daemon-reload')
    run('systemctl', 'restart', 'holylois-offsite-backup.timer')
    message = ("**Holy Lois 1.7.4 is live: land and zones!** Close Minecraft, open the launcher and click Update.\n"
               "- Claim land right on the world map (M, right-click a chunk). 16 chunks free, more by playing or with coins: /claims\n"
               "- Teams: /oparties create, then /oparties invite NAME. Your team can build on your land\n"
               "- Zone titles show the biome and whose land you are on\n"
               "- /rtp never drops you into someone's land\n"
               "- PvP: logging out during a fight kills you, and PvP loot is up for grabs\n"
               "- /support MESSAGE reaches pjampjam right away, /report for problems with players, /donate for the wallets")
    result = subprocess.run(['python3', str(ALERT), 'message', message], capture_output=True, text=True)
    receipt = {'release': 'pack 1.7.4 server', 'backup': str(archive), 'onboarding': '1.7.0', 'extras': '1.2.0', 'opac': '0.31.6',
               'flan_removed': [p.name for p in old_flan], 'motd': HEADLINE, 'world_border': BORDER,
               'discord': 'ok' if result.returncode == 0 else result.stderr.strip()[:200], 'result': 'Done'}
    (backup / 'receipt.json').write_text(json.dumps(receipt, indent=2, ensure_ascii=False) + '\n')
    print(json.dumps(receipt, indent=2, ensure_ascii=False))
    # Offload this backup to Google Drive once it has been quiet for 10 minutes (the job verifies before deleting).
    subprocess.run(['systemd-run', '--on-active=900', '--unit=holylois-offload-release174', 'systemctl', 'start', 'holylois-offsite-backup.service'])


if __name__ == '__main__':
    main()
