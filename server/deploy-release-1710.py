"""Holy Lois server release for pack 1.7.10. Run as root on the server from ~/hl-1710.

- Onboarding 1.8.0: AFK time stops counting (Essential Commands decides who is AFK; achievements, land claims, leaderboards, stats, weekly
  recap and the Tab list use playtime minus AFK), quiet names (config/holylois-quiet.json: no join/leave/AFK/advancement/discovery
  announcements for the owner, deaths still show in game chat) and /redeem CODE (the secret code of the day from holylois.com, secret in
  config/holylois-daily.secret, one prize per player per UTC day).
- Holy Lois Extras 1.5.0 (both sides): Quick Play from the title screen (the launcher writes holylois-quickplay.json), new window icons.
- Terrain job lag guard: short slices with rests and a long rest when the server falls behind; max-tick-time 120000 so a long tick is not
  killed by the watchdog. The blocked job is resumed from its Chunky checkpoint.
- Discord bot and Tab list follow quiet names and AFK-free playtime; stats and weekly recap subtract AFK time; datapack gets its logo.
- Rules (in game and Discord #rules): only the launcher's mods. New server icon.
Online players get a one-minute countdown, then a kick with a Holy Lois message. A complete verified backup comes first and everything
returns automatically if the server does not start.
"""
import datetime, json, os, re, shutil, subprocess, sys, time
from pathlib import Path

from importlib import util
spec = util.spec_from_file_location('previous', '/home/ubuntu/hl-174/deploy-release-174.py'); previous = util.module_from_spec(spec); spec.loader.exec_module(previous)
online_players, wait_for_start, run, console, say = previous.online_players, previous.wait_for_start, previous.run, previous.console, previous.say

HOME = Path('/home/ubuntu/hl-1710')
ROOT = Path('/opt/minecraft')
MODS = ROOT / 'mods'
ONBOARDING_NEW = Path('/home/ubuntu/holylois-build-180/holylois-onboarding-1.8.0+26.3.jar')
EXTRAS_NEW = Path('/home/ubuntu/holylois-extras-150/holylois-extras-1.5.0+26.3.jar')
ADVANCEMENTS_NEW, ADVANCEMENTS = HOME / 'holylois-advancements', ROOT / 'world/datapacks/holylois-advancements'
ICON_NEW, ICON = HOME / 'server-icon.png', ROOT / 'server-icon.png'
SECRET_NEW, SECRET = HOME / 'holylois-daily.secret', ROOT / 'config/holylois-daily.secret'
PROPERTIES = ROOT / 'server.properties'
STYLE = ROOT / 'config/styledplayerlist/styles/holylois.json'
RULES_TXT = ROOT / 'config/essentialcommands/rules.txt'
OLD_RULE, NEW_RULE = 'No cheats: hacked clients, x-ray, duping or bug abuse. Launcher mods are fine.', \
    "No cheats: hacked clients, x-ray, duping or bug abuse. Only the launcher's mods: extra mods are turned away."
RULES_MD_NEW, RULES_MD = HOME / 'RULES.md', Path('/opt/holylois-bot/RULES.md')
BOT_NEW, BOT = HOME / 'bot.py', Path('/opt/holylois-bot/bot.py')
LIB = Path('/usr/local/lib/holylois')
SCRIPTS = {'weekly-recap.py': LIB / 'weekly-recap.py', 'make-stats.py': LIB / 'make-stats.py', 'expand-terrain.py': LIB / 'expand-terrain.py'}
TERRAIN_STATE = Path('/opt/minecraft-backups/terrain-expansion/job.json')
MOTD = ROOT / 'config/MiniMOTD/main.conf'
MAINTENANCE = Path('/run/holylois-maintenance')
ALERT = LIB / 'discord-alert.py'
# Server list line under the name: always the newest exciting change, capital letter after "New:".
HEADLINE = '<#FFAD42>✦ New:</#FFAD42> <white>Quick Play, one click and you are in!</white>'
COUNTDOWN = 60
BAR = 'holylois:restart'


def countdown():
    """Same countdown as 1.7.4 (boss bar, big numbers, goodbye title, kick); only the chat line differs."""
    original = previous.say
    previous.say = lambda text: original(text.replace('land claims on the map, zone titles, /support',
                                                      'Quick Play, AFK time that does not count and calmer world generation'))
    try: previous.countdown()
    finally: previous.say = original


def unblock_terrain():
    """Resume the job that the watchdog crash blocked: Chunky kept its checkpoint, so the next timer step continues from it."""
    state = json.loads(TERRAIN_STATE.read_text(encoding='utf-8'))
    assert state.get('phase') == 'blocked' and state.get('started') and not state.get('complete'), state
    for key in ('error', 'blocked_at', 'pause_baseline', 'pause_requested_at', 'rest_until'): state.pop(key, None)
    state.update(phase='running', running=False, pause_pending=False)
    temporary = TERRAIN_STATE.with_suffix('.tmp')
    temporary.write_text(json.dumps(state, indent=2, sort_keys=True) + '\n', encoding='utf-8')
    os.chmod(temporary, 0o600); os.replace(temporary, TERRAIN_STATE)


def main():
    assert os.geteuid() == 0, 'Run as root'
    old_onboarding = sorted(MODS.glob('holylois-onboarding-*.jar')); old_extras = sorted(MODS.glob('holylois-extras-*.jar'))
    assert len(old_onboarding) == 1 and len(old_extras) == 1, (old_onboarding, old_extras)
    assert old_onboarding[0].name != ONBOARDING_NEW.name and old_extras[0].name != EXTRAS_NEW.name, 'Already deployed'
    for path in [ONBOARDING_NEW, EXTRAS_NEW, ADVANCEMENTS_NEW / 'pack.mcmeta', ADVANCEMENTS_NEW / 'pack.png', ICON_NEW, SECRET_NEW, RULES_MD_NEW, BOT_NEW,
                 *(HOME / n for n in SCRIPTS), PROPERTIES, STYLE, RULES_TXT, MOTD, ADVANCEMENTS, TERRAIN_STATE]:
        assert path.exists(), path
    assert len(SECRET_NEW.read_text().strip()) >= 32, 'Secret looks too short'
    assert not SECRET.exists(), 'Secret already installed'
    assert 'max-tick-time=60000' in PROPERTIES.read_text(), 'max-tick-time is not the old value'
    assert STYLE.read_text(encoding='utf-8').count('%player:playtime%') == 1, 'Tab style not as expected'
    assert OLD_RULE in RULES_TXT.read_text(encoding='utf-8'), 'Rules text not as expected'
    assert 'LAG_TICKS' in (HOME / 'expand-terrain.py').read_text(), 'Terrain job is not the lag guard version'
    assert 'quiet' in BOT_NEW.read_text().lower(), 'Bot is not the quiet version'
    assert shutil.disk_usage(ROOT).free > 8 * 1024**3, 'Less than 8 GB free'
    if sys.argv[1:] == ['--check']:
        print('All pre-checks passed; nothing was changed.')
        return
    countdown()

    stamp = datetime.datetime.now(datetime.timezone.utc).strftime('%Y%m%dT%H%M%SZ')
    backup = Path('/opt/minecraft-backups/maintenance') / ('release1710-' + stamp)
    backup.mkdir(mode=0o700)
    MAINTENANCE.touch()
    run('systemctl', 'stop', 'minecraft-console.socket', 'minecraft.service')
    installed = []
    saved = [*old_onboarding, *old_extras, MOTD, RULES_TXT, STYLE, PROPERTIES, *([ICON] if ICON.exists() else [])]
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
        run('install', '-o', 'minecraft', '-g', 'minecraft', '-m', '600', str(SECRET_NEW), str(SECRET)); installed.append(SECRET)
        run('install', '-o', 'minecraft', '-g', 'minecraft', '-m', '644', str(ICON_NEW), str(ICON))
        PROPERTIES.write_text(PROPERTIES.read_text().replace('max-tick-time=60000', 'max-tick-time=120000'))
        STYLE.write_text(STYLE.read_text(encoding='utf-8').replace('%player:playtime%', '%holylois:playtime%'), encoding='utf-8')
        RULES_TXT.write_text(RULES_TXT.read_text(encoding='utf-8').replace(OLD_RULE, NEW_RULE), encoding='utf-8')
        motd, count = re.subn(r'(?m)^(\s*line2=).*$', lambda m: m.group(1) + json.dumps(HEADLINE, ensure_ascii=False), MOTD.read_text(encoding='utf-8'), count=1)
        assert count == 1, 'MOTD line2 not found'
        MOTD.write_text(motd, encoding='utf-8')
        run('chown', '-R', 'minecraft:minecraft', str(ADVANCEMENTS), str(PROPERTIES), str(STYLE), str(RULES_TXT), str(MOTD))

        since = time.strftime('%Y-%m-%d %H:%M:%S')
        run('systemctl', 'start', 'minecraft-console.socket', 'minecraft.service')
        log = wait_for_start(since)
        for needle in ['holylois-onboarding 1.8.0', 'holylois-extras 1.5.0', 'holylois_boombox', 'Holy Lois discoveries', 'Holy Lois secret code: on', 'Holy Lois AFK ledger: counting']:
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
    # The rest only reads the log or the world files, so it can update after the server is up.
    shutil.copy2(TERRAIN_STATE, backup / 'terrain-job.json')
    for name, target in SCRIPTS.items():
        if target.exists(): shutil.copy2(target, backup / (target.name + '.old'))
        run('install', '-m', '755', str(HOME / name), str(target))
    shutil.copy2(BOT, backup / 'bot.py.old'); shutil.copy2(RULES_MD, backup / 'RULES.md.old')
    run('install', '-m', '644', str(BOT_NEW), str(BOT)); run('install', '-m', '644', str(RULES_MD_NEW), str(RULES_MD))
    subprocess.run(['systemctl', 'restart', 'holylois-discord-bot'])
    unblock_terrain()
    run('systemctl', 'daemon-reload')
    run('systemctl', 'enable', '--now', 'holylois-terrain-expansion.timer')
    message = ("**Holy Lois 1.7.10 is live: Quick Play!** Close Minecraft, open the launcher and click Update.\n"
               "- Quick Play: click Play and the game joins Holy Lois by itself from the title screen (premium and offline accounts). "
               "Pick Standard in the launcher Settings if you prefer the old way\n"
               "- The launcher closes Minecraft for you when an update needs it (you press Agree first)\n"
               "- AFK time no longer counts as playing: achievements, land claims, leaderboards and stats skip it\n"
               "- A secret code hides somewhere on holylois.com: `/redeem CODE` once a day for a prize\n"
               "- New icons for the game window and the launcher, calmer world generation, rule 3 now says only the launcher's mods")
    result = subprocess.run(['python3', str(ALERT), 'message', message], capture_output=True, text=True)
    receipt = {'release': 'pack 1.7.10 server', 'backup': str(archive), 'onboarding': '1.8.0', 'extras': '1.5.0', 'max_tick_time': 120000,
               'terrain_job': 'resumed from the Chunky checkpoint', 'motd': HEADLINE,
               'discord': 'ok' if result.returncode == 0 else result.stderr.strip()[:200], 'result': 'Done'}
    (backup / 'receipt.json').write_text(json.dumps(receipt, indent=2, ensure_ascii=False) + '\n')
    print(json.dumps(receipt, indent=2, ensure_ascii=False))
    subprocess.run(['systemd-run', '--on-active=900', '--unit=holylois-offload-release1710', 'systemctl', 'start', 'holylois-offsite-backup.service'])


if __name__ == '__main__':
    main()
