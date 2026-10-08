"""Server-only hotfix: onboarding 1.8.3 -> 1.8.4 (admin-only mod commands locked for players). Nothing changes for clients.
Verified full backup, short countdown only when players are online (no update needed), one jar swap, health checks and
automatic rollback. Run as root from ~/hl-184; --check validates only.
"""
from pathlib import Path
from importlib import util
import datetime, hashlib, json, os, shutil, subprocess, sys, tarfile, time

def load(name, path):
    spec = util.spec_from_file_location(name, path); module = util.module_from_spec(spec); spec.loader.exec_module(module); return module
base = load('base', '/home/ubuntu/hl-170/deploy-release-170.py')   # online_players, journal
helpers = load('helpers', '/home/ubuntu/hl-174/deploy-release-174.py')  # console, say
ROOT = Path('/opt/minecraft'); KIT = Path(__file__).resolve().parent
NEW = KIT / 'holylois-onboarding-1.8.4+26.3.jar'
NEW_SHA = '73ba490b4c909f1db8d692e8b8757579a089369ee7a46adfe080af61de8c90c3'
OLD_NAME = 'holylois-onboarding-1.8.3+26.3.jar'
MAINTENANCE = Path('/run/holylois-maintenance')
BAR, COUNTDOWN = 'holylois:restart', 60
FATAL = ('Failed to start', 'Crash report', 'Incompatible mods', 'Failed to load datapacks', 'Mixin apply failed',
         'Registry loading errors', 'Encountered an unexpected exception', 'could not lock admin-only commands')
def run(*args, **kwargs): return subprocess.run(args, check=True, **kwargs)
def digest(p): return hashlib.sha256(p.read_bytes()).hexdigest()

def countdown():
    """The approved boss bar countdown, worded for a quick restart: nobody has to update anything."""
    console = helpers.console
    console(f'bossbar remove {BAR}')
    if base.online_players() == 0: return
    console('gamerule send_command_feedback false', f'bossbar add {BAR} ' + json.dumps({'text': 'Quick server restart'}),
            f'bossbar set {BAR} max {COUNTDOWN}', f'bossbar set {BAR} value {COUNTDOWN}', f'bossbar set {BAR} color yellow',
            f'bossbar set {BAR} style notched_10', f'bossbar set {BAR} players @a', 'title @a times 0 25 5')
    start = time.monotonic()
    for left in range(COUNTDOWN, 0, -1):
        time.sleep(max(0, COUNTDOWN - left - (time.monotonic() - start)))
        label = f'{left} second{"s" if left != 1 else ""}'
        commands = [f'bossbar set {BAR} value {left}', f'bossbar set {BAR} players @a',
                    f'bossbar set {BAR} name ' + json.dumps({'text': f'Quick server restart in {label} - nothing to update', 'color': 'yellow' if left > 10 else 'red'})]
        if left == 10: commands.append(f'bossbar set {BAR} color red')
        if left <= 10:
            commands += ['title @a subtitle ' + json.dumps({'text': 'Quick restart, rejoin in a few minutes. No update needed', 'color': 'yellow'}),
                         'title @a title ' + json.dumps({'text': f'Restarting in {left}', 'color': 'gold', 'bold': True}),
                         'execute as @a at @s run playsound minecraft:block.note_block.hat master @s ~ ~ ~ 1 ' + ('2' if left <= 3 else '1')]
        console(*commands)
        if left in (COUNTDOWN, 30, 10):
            helpers.say(f'Quick server restart in {label} for a small server fix. Nothing to update, just rejoin in a few minutes.')
    console(f'bossbar remove {BAR}', 'gamerule send_command_feedback true', 'title @a times 0 200 0',
            'title @a subtitle ' + json.dumps({'text': 'Quick restart, back in a few minutes. No update needed', 'color': 'yellow'}),
            'title @a title ' + json.dumps({'text': 'Maaarek nahhul!', 'color': 'gold', 'bold': True}))
    time.sleep(3)
    console('kick @a Maaarek nahhul! Quick server restart, back in a few minutes. No update needed, just rejoin.')
    time.sleep(2)

def start_and_check():
    """Start, wait for Done plus the Holy Lois start-up lines. The REI + Farmer's Delight startup race (fixed in 1.9.0)
    can fail a start at random, so a datapack failure gets exactly one more try before the rollback."""
    for attempt in (1, 2):
        since = datetime.datetime.now(datetime.timezone.utc).isoformat()
        run('systemctl', 'start', 'minecraft-console.socket', 'minecraft.service')
        log = ''
        for _ in range(420):
            time.sleep(1)
            log = base.journal(since)
            if 'Done (' in log and 'Holy Lois claims: ready for OPAC' in log: break
            if any(needle in log for needle in FATAL): break
        if 'Failed to load datapacks' in log and attempt == 1:
            print('Startup hit the known datapack race; trying once more.', flush=True)
            run('systemctl', 'stop', 'minecraft-console.socket', 'minecraft.service'); continue
        assert 'Done (' in log, 'Server did not finish starting'
        for needle in ('holylois-onboarding 1.8.4', 'holylois-extras 1.6.3', 'Holy Lois claims: ready for OPAC', 'holylois_boombox'):
            assert needle in log, 'Missing startup marker: ' + needle
        bad = [needle for needle in FATAL if needle in log]
        assert not bad, 'Startup errors: ' + ', '.join(bad)
        return attempt

def main():
    assert os.geteuid() == 0, 'Run as root'
    assert NEW.exists() and digest(NEW) == NEW_SHA, 'Hotfix jar hash'
    olds = list((ROOT / 'mods').glob('holylois-onboarding-*.jar'))
    assert [o.name for o in olds] == [OLD_NAME], f'Expected exactly {OLD_NAME}, found {[o.name for o in olds]}'
    old = olds[0]
    assert not list(KIT.glob('*probe*.jar')), 'Test mod must never deploy'
    assert shutil.disk_usage(ROOT).free > 30 * 1024**3, 'Backup space too low'
    assert (KIT / 'test-184.ok').exists(), 'Isolated loopback test has not passed'
    print('Online players:', base.online_players(), flush=True)
    if sys.argv[1:] == ['--check']:
        print('All pre-checks passed; nothing changed.', flush=True); return
    countdown()
    stamp = datetime.datetime.now(datetime.timezone.utc).strftime('%Y%m%dT%H%M%SZ')
    backup = Path('/opt/minecraft-backups/maintenance') / ('hotfix184-' + stamp); backup.mkdir(mode=0o700)
    archive = backup / 'complete-server.tar'
    target = ROOT / 'mods' / NEW.name; installed = False
    timer_active = subprocess.run(['systemctl', 'is-active', '--quiet', 'holylois-stats.timer']).returncode == 0
    MAINTENANCE.touch()
    try:
        run('systemctl', 'stop', 'holylois-stats.timer', 'holylois-stats.service')
        run('systemctl', 'stop', 'minecraft-console.socket', 'minecraft.service')
        shutil.copy2(old, backup / old.name)
        print('Creating fresh complete server backup...', flush=True)
        run('tar', '--exclude=minecraft/backups', '-cf', str(archive), '-C', '/opt', 'minecraft'); archive.chmod(0o600)
        with tarfile.open(archive) as tar:
            members = tar.getmembers(); names = {m.name for m in members}
            for name in ('minecraft/world/level.dat', 'minecraft/server.jar', 'minecraft/config', 'minecraft/mods', 'minecraft/EasyAuth'):
                assert name in names, 'Missing required backup path ' + name
            assert all(m.offset_data + m.size <= archive.stat().st_size for m in members if m.isfile())
            assert tar.extractfile('minecraft/mods/' + old.name).read() == (backup / old.name).read_bytes(), 'Restore-byte mismatch'
        print('Full archive structure, required paths and changed-file restore bytes verified.', flush=True)
        run('install', '-o', 'minecraft', '-g', 'minecraft', '-m', '644', str(NEW), str(target)); installed = True; old.unlink()
        attempts = start_and_check()
        helpers.console(f'bossbar remove {BAR}', 'gamerule send_command_feedback true')
    except BaseException:
        print('Deployment failed. Restoring the original onboarding add-on automatically...', flush=True)
        run('systemctl', 'stop', 'minecraft-console.socket', 'minecraft.service')
        if installed: target.unlink(missing_ok=True)
        if not old.exists(): shutil.copy2(backup / old.name, old); run('chown', 'minecraft:minecraft', str(old))
        run('systemctl', 'start', 'minecraft-console.socket', 'minecraft.service')
        raise
    finally:
        MAINTENANCE.unlink(missing_ok=True)
        if timer_active: run('systemctl', 'start', 'holylois-stats.timer')
    receipt = {'result': 'Done', 'hotfix': 'onboarding 1.8.4 (server only)', 'backup': str(archive), 'start_attempts': attempts,
               'backup_verification': 'complete tar structure, required paths, exact changed-file restore bytes',
               'addons': {NEW.name: digest(target)}}
    for destination in (backup / 'receipt.json', KIT / 'deploy-receipt.json'): destination.write_text(json.dumps(receipt, indent=2) + '\n')
    print(json.dumps(receipt, indent=2), flush=True)

if __name__ == '__main__': main()
