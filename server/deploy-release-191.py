"""Pack 1.9.1 server release. Run as root from ~/hl-191; --check validates only and changes nothing.

Same file changes as the passed loopback test (test-191.py apply_changes): Extras 1.7.1 and onboarding 1.9.1, the balanced Tab
list, /rules without the stats note, /spawn off (open world), pack minimum 1.9.1, MOTD headline.
Online players get the approved one-minute countdown first. A fresh complete backup is verified (structure, required paths, exact
restore bytes of every changed file) before anything changes; if the server does not come up healthy, mods, config and the OPAC
data return automatically. pack-stable is moved from the owner's PC right after this script reports Done.
"""
from pathlib import Path
from importlib import util
import datetime, hashlib, json, os, re, shutil, subprocess, sys, tarfile, time


def load(name, path):
    spec = util.spec_from_file_location(name, path); module = util.module_from_spec(spec); spec.loader.exec_module(module); return module


base = load('base', '/home/ubuntu/hl-170/deploy-release-170.py')      # online_players, journal
helpers = load('helpers', '/home/ubuntu/hl-174/deploy-release-174.py')  # console, say, countdown
KIT = Path(__file__).resolve().parent
test = load('test191', str(KIT / 'test-191.py'))                         # apply_changes, HASHES, ADDONS
ROOT = Path('/opt/minecraft')
MOTD = ROOT / 'config/MiniMOTD/main.conf'
MAINTENANCE = Path('/run/holylois-maintenance')
BAR = 'holylois:restart'
# Server list line under the name: the newest exciting change, capital letter after "New:".
HEADLINE = '<#FFAD42>✦ New:</#FFAD42> <white>Boombox music right in your ears!</white>'
OLD_ADDONS = ['holylois-extras-1.7.0+26.3.jar', 'holylois-onboarding-1.9.0+26.3.jar']
# Everything apply_changes or the first start may rewrite; restored as a whole on rollback.
TREES = [ROOT / 'mods', ROOT / 'config', ROOT / 'world/data/openpartiesandclaims']
CHANGED = ['config/styledplayerlist/styles/holylois.json', 'config/essentialcommands/rules.txt', 'config/EssentialCommands.properties',
           'config/holylois-pack.json', 'config/MiniMOTD/main.conf']
FATAL = ('Failed to start', 'Crash report', 'Incompatible mods', 'Failed to load datapacks', 'Mixin apply failed',
         'Registry loading errors', 'Encountered an unexpected exception', 'could not lock admin-only commands')
MARKERS = ('holylois-onboarding 1.9.1', 'holylois-extras 1.7.1', 'openpartiesandclaims 0.32.8', 'Holy Lois claims: ready for OPAC', 'holylois_boombox')


def run(*args, **kwargs): return subprocess.run(args, check=True, **kwargs)


def countdown():
    """The approved 1.7.4 countdown (boss bar, big numbers, goodbye title, kick with the update hint); only the chat line differs."""
    original = helpers.say
    helpers.say = lambda text: original(text.replace('land claims on the map, zone titles, /support',
                                                     'boombox music in your ears and a smarter cinematic camera'))
    try: helpers.countdown()
    finally: helpers.say = original


def start_and_check():
    """Start and wait for Done plus the Holy Lois start-up lines; one more try only for the old REI datapack race."""
    for attempt in (1, 2):
        since = datetime.datetime.now(datetime.timezone.utc).isoformat()
        run('systemctl', 'start', 'minecraft-console.socket', 'minecraft.service')
        log = ''
        for _ in range(480):
            time.sleep(1)
            log = base.journal(since)
            if 'Done (' in log and 'Holy Lois claims: ready for OPAC' in log: break  # 'command audit' only prints on test servers
            if any(needle in log for needle in FATAL): break
        if 'Failed to load datapacks' in log and attempt == 1:
            print('Startup hit the known datapack race; trying once more.', flush=True)
            run('systemctl', 'stop', 'minecraft-console.socket', 'minecraft.service'); continue
        assert 'Done (' in log, 'Server did not finish starting'
        for needle in MARKERS: assert needle in log, 'Missing startup marker: ' + needle
        bad = [needle for needle in FATAL if needle in log]
        assert not bad, 'Startup errors: ' + ', '.join(bad)
        return attempt


def main():
    assert os.geteuid() == 0, 'Run as root'
    assert (KIT / 'test-191.ok').exists(), 'Isolated loopback test has not passed'
    assert json.loads((KIT / 'pack.json').read_text(encoding='utf-8'))['version'] == '1.9.1'
    for name, sha in test.HASHES.items():
        jar = KIT / name
        assert hashlib.sha256(jar.read_bytes()).hexdigest() == sha, 'Artifact hash: ' + name
    live = {p.name for p in (ROOT / 'mods').glob('holylois-*.jar')}
    assert set(OLD_ADDONS) <= live, 'Live add-ons are not the 1.9.0 ones: ' + str(sorted(live))
    assert not list(KIT.rglob('*probe*.jar')), 'Test mod must never deploy'
    assert len(re.findall(r'(?m)^\s*line2=', MOTD.read_text(encoding='utf-8'))) == 1, 'MOTD line2 not found'
    assert shutil.disk_usage(ROOT).free > 30 * 1024**3, 'Backup space too low'
    print('Online players:', base.online_players(), flush=True)
    if sys.argv[1:] == ['--check']:
        print('All pre-checks passed; nothing changed.', flush=True); return

    countdown()
    stamp = datetime.datetime.now(datetime.timezone.utc).strftime('%Y%m%dT%H%M%SZ')
    backup = Path('/opt/minecraft-backups/maintenance') / ('release191-' + stamp); backup.mkdir(mode=0o700)
    archive = backup / 'complete-server.tar'
    timer_active = subprocess.run(['systemctl', 'is-active', '--quiet', 'holylois-stats.timer']).returncode == 0
    changed = False
    MAINTENANCE.touch()
    try:
        run('systemctl', 'stop', 'holylois-stats.timer', 'holylois-stats.service')
        run('systemctl', 'stop', 'minecraft-console.socket', 'minecraft.service')
        for tree in TREES: shutil.copytree(tree, backup / 'trees' / tree.relative_to(ROOT), symlinks=True)
        print('Creating fresh complete server backup...', flush=True)
        run('tar', '--exclude=minecraft/backups', '-cf', str(archive), '-C', '/opt', 'minecraft'); archive.chmod(0o600)
        with tarfile.open(archive) as tar:
            members = tar.getmembers(); names = {m.name for m in members}
            for name in ('minecraft/world/level.dat', 'minecraft/server.jar', 'minecraft/config', 'minecraft/mods', 'minecraft/EasyAuth',
                         'minecraft/world/data/openpartiesandclaims'):
                assert name in names, 'Missing required backup path ' + name
            assert all(m.offset_data + m.size <= archive.stat().st_size for m in members if m.isfile())
            for rel in CHANGED + ['mods/' + n for n in OLD_ADDONS]:
                assert tar.extractfile('minecraft/' + rel).read() == (ROOT / rel).read_bytes(), 'Restore-byte mismatch: ' + rel
        print('Full archive structure, required paths and changed-file restore bytes verified.', flush=True)

        changed = True
        test.apply_changes(ROOT, KIT)
        text, count = re.subn(r'(?m)^(\s*line2=).*$', lambda m: m.group(1) + json.dumps(HEADLINE, ensure_ascii=False),
                              MOTD.read_text(encoding='utf-8'), count=1)
        assert count == 1; MOTD.write_text(text, encoding='utf-8')
        run('chown', '-R', 'minecraft:minecraft', str(ROOT / 'mods'), str(ROOT / 'config'))
        attempts = start_and_check()
        helpers.console(f'bossbar remove {BAR}', 'gamerule send_command_feedback true')
    except BaseException:
        print('Deployment failed. Restoring mods, config and claims data automatically...', flush=True)
        subprocess.run(['systemctl', 'stop', 'minecraft-console.socket', 'minecraft.service'])
        if changed:
            for tree in TREES:
                saved = backup / 'trees' / tree.relative_to(ROOT)
                if saved.exists():
                    shutil.rmtree(tree, ignore_errors=True); shutil.copytree(saved, tree, symlinks=True)
                    run('chown', '-R', 'minecraft:minecraft', str(tree))
        run('systemctl', 'start', 'minecraft-console.socket', 'minecraft.service')
        print('Rolled back. Complete backup kept at', archive, flush=True)
        raise
    finally:
        MAINTENANCE.unlink(missing_ok=True)
        if timer_active: subprocess.run(['systemctl', 'start', 'holylois-stats.timer'])

    receipt = {'result': 'Done', 'pack': '1.9.1', 'backup': str(archive), 'start_attempts': attempts,
               'backup_verification': 'complete tar structure, required paths, exact changed-file restore bytes',
               'removed': OLD_ADDONS,
               'added': {name: hashlib.sha256((ROOT / 'mods' / name).read_bytes()).hexdigest() for name in test.ADDONS},
               'pack_minimum': '1.9.1', 'spawn': 'off', 'motd': HEADLINE}
    for destination in (backup / 'receipt.json', KIT / 'deploy-receipt.json'):
        destination.write_text(json.dumps(receipt, indent=2, ensure_ascii=False) + '\n')
    print(json.dumps(receipt, indent=2, ensure_ascii=False), flush=True)
    subprocess.run(['systemd-run', '--on-active=900', '--unit=holylois-offload-release191', 'systemctl', 'start', 'holylois-offsite-backup.service'])


if __name__ == '__main__':
    main()
