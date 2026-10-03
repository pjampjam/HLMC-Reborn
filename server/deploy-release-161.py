"""Holy Lois server release for pack 1.6.1. Run as root on the server from ~/hl-161.

Mods: Farmer's Delight, Macaw's Furniture (both sides), Styled Player List, RightClickHarvest + Jamlib,
Krypton, Alternate Current, Dungeons and Taverns, Towns and Towers + Cristel Lib, AudioPlayer, onboarding 1.4.0.
Also: Tab style, village spacing datapack, Runeforged chest tiers for the new structures, one-player sleep,
tuned JVM flags, a 12 GB backup budget, fail2ban, the bot wall, Discord monitor, nightly Google Drive backup
and the terrain expansion timer. Refuses while players are online, makes a complete verified backup first
and restores the previous files if the server does not start.
"""
import datetime, hashlib, json, os, shutil, socket, struct, subprocess, time
from pathlib import Path

HOME = Path('/home/ubuntu/hl-161')
ROOT = Path('/opt/minecraft')
MODS = ROOT / 'mods'
ONBOARDING_OLD = MODS / 'holylois-onboarding-1.3.0+26.3.jar'
ONBOARDING_NEW = Path('/home/ubuntu/holylois-build-140/holylois-onboarding-1.4.0+26.3.jar')
SPL = ROOT / 'config/styledplayerlist'
JEB = ROOT / 'config/justenoughbackups.json'
MONSTERS = ROOT / 'config/runeforged-monsters.json'
DATAPACK = ROOT / 'world/datapacks/holylois-structure-tuning'
DROPIN = Path('/etc/systemd/system/minecraft.service.d/jvm.conf')
LIB = Path('/usr/local/lib/holylois')
UNITS = Path('/etc/systemd/system')
JAIL = Path('/etc/fail2ban/jail.d/holylois-sshd.local')
TASK = ROOT / 'config/chunky/tasks/minecraft/overworld.properties'
JOB = Path('/opt/minecraft-backups/terrain-expansion')
MAINTENANCE = Path('/run/holylois-maintenance')
FIFO = Path('/run/minecraft-console.fifo')
OPS_UNITS = ['holylois-botwall.service', 'holylois-botwall.timer', 'holylois-monitor.service', 'holylois-monitor.timer',
             'holylois-offsite-backup.service', 'holylois-offsite-backup.timer']
TIMERS = ['holylois-botwall.timer', 'holylois-monitor.timer', 'holylois-offsite-backup.timer', 'holylois-terrain-expansion.timer']


def run(*args, **kw):
    return subprocess.run(list(args), check=True, **kw)


def varint(value):
    out = bytearray()
    while True:
        b = value & 127; value >>= 7
        out.append(b | (128 if value else 0))
        if not value: return bytes(out)


def online_players():
    with socket.create_connection(('127.0.0.1', 25565), timeout=5) as s:
        host = b'localhost'
        packet = b'\x00' + varint(0) + varint(len(host)) + host + struct.pack('>H', 25565) + b'\x01'
        s.sendall(varint(len(packet)) + packet + b'\x01\x00')
        data = b''; s.settimeout(5)
        while True:
            chunk = s.recv(65536)
            if not chunk: break
            data += chunk
            start = data.find(b'{')
            if start >= 0:
                try: return json.loads(data[start:].decode('utf-8'))['players']['online']
                except ValueError: continue
    raise IOError('No status reply')


def journal(since):
    return subprocess.run(['journalctl', '-u', 'minecraft', '--since', since, '--no-pager', '-o', 'cat'],
                          capture_output=True, text=True, errors='replace').stdout


def wait_for_start(since):
    for _ in range(360):
        time.sleep(1)
        log = journal(since)
        if 'Done (' in log: return log
        if 'Failed to start' in log or 'Crash report' in log or 'Incompatible mods' in log:
            raise RuntimeError('Minecraft failed to start')
    raise RuntimeError('Startup timeout')


def console(command):
    with FIFO.open('w') as stream:
        stream.write(command + '\n')


def main():
    assert os.geteuid() == 0, 'Run as root'
    manifest = json.loads((HOME / 'new-mods.json').read_text())
    staged = []
    for slug in manifest['sides']['server'] + manifest['sides']['server161']:
        m = manifest['mods'][slug]; jar = HOME / 'server-mods' / m['filename']
        assert hashlib.sha512(jar.read_bytes()).hexdigest() == m['sha512'], slug
        assert not (MODS / jar.name).exists(), 'Already installed: ' + jar.name
        staged.append(jar)
    assert ONBOARDING_OLD.exists() and ONBOARDING_NEW.exists()
    assert not TASK.exists(), 'An existing Chunky task must be archived first'
    assert not JOB.exists(), 'An existing terrain job state must be archived first'
    assert not DATAPACK.exists(), 'Structure datapack already present'
    assert shutil.disk_usage(ROOT).free > 8 * 1024**3, 'Less than 8 GB free'
    players = online_players()
    assert players == 0, f'{players} player(s) online; deployment deferred'

    # Packages first, while Minecraft still runs, to keep the downtime short.
    run('apt-get', 'install', '-y', '-q', 'fail2ban', 'rclone', stdout=subprocess.DEVNULL,
        env={**os.environ, 'DEBIAN_FRONTEND': 'noninteractive', 'NEEDRESTART_MODE': 'l'})

    stamp = datetime.datetime.now(datetime.timezone.utc).strftime('%Y%m%dT%H%M%SZ')
    backup = Path('/opt/minecraft-backups/maintenance') / ('release161-' + stamp)
    backup.mkdir(mode=0o700)
    MAINTENANCE.touch()
    run('systemctl', 'stop', 'minecraft-console.socket', 'minecraft.service')
    installed = []
    try:
        archive = backup / 'complete-server.tar.gz'
        run('tar', '--exclude=minecraft/backups', '-czf', str(archive), '-C', '/opt', 'minecraft')
        archive.chmod(0o600)
        run('tar', '-tzf', str(archive), stdout=subprocess.DEVNULL)
        for path in [ONBOARDING_OLD, JEB, MONSTERS]:
            shutil.copy2(path, backup / path.name)

        for jar in staged + [ONBOARDING_NEW]:
            target = MODS / jar.name
            run('install', '-o', 'minecraft', '-g', 'minecraft', '-m', '644', str(jar), str(target))
            installed.append(target)
        ONBOARDING_OLD.unlink()

        (SPL / 'styles').mkdir(parents=True, exist_ok=True)
        shutil.copy2(HOME / 'spl/config.json', SPL / 'config.json')
        shutil.copy2(HOME / 'spl/styles/holylois.json', SPL / 'styles/holylois.json')
        shutil.copytree(HOME / 'holylois-structure-tuning', DATAPACK)
        monsters = json.loads(MONSTERS.read_text())
        known = {e['loot_table'] for e in monsters['chest_loot_tables']}
        added = [e for e in json.loads((HOME / 'runeforged-chest-additions.json').read_text()) if e['loot_table'] not in known]
        monsters['chest_loot_tables'] += added
        MONSTERS.write_text(json.dumps(monsters, indent=1) + '\n')
        jeb = json.loads(JEB.read_text())
        jeb['retention']['maxTotalSizeMb'] = 12288
        JEB.write_text(json.dumps(jeb, indent=2) + '\n')
        run('chown', '-R', 'minecraft:minecraft', str(SPL), str(DATAPACK.parent), str(MONSTERS), str(JEB))

        shutil.copy2(HOME / 'systemd/jvm.conf', DROPIN); DROPIN.chmod(0o644)
        LIB.mkdir(parents=True, exist_ok=True)
        shutil.copy2(HOME / 'terrain/expand-terrain.py', LIB / 'expand-terrain.py')
        for script in ['botwall.py', 'discord-alert.py', 'offsite-backup.py']:
            shutil.copy2(HOME / 'ops' / script, LIB / script)
        for script in LIB.glob('*.py'):
            script.chmod(0o755)
        for unit in ['holylois-terrain-expansion.service', 'holylois-terrain-expansion.timer']:
            shutil.copy2(HOME / 'terrain' / unit, UNITS / unit)
        for unit in OPS_UNITS:
            shutil.copy2(HOME / 'ops/units' / unit, UNITS / unit)
        for unit in OPS_UNITS + ['holylois-terrain-expansion.service', 'holylois-terrain-expansion.timer']:
            (UNITS / unit).chmod(0o644)
        shutil.copy2(HOME / 'ops/units/holylois-sshd.local', JAIL); JAIL.chmod(0o644)
        Path('/etc/holylois').mkdir(mode=0o700, exist_ok=True)
        run('systemctl', 'daemon-reload')

        since = time.strftime('%Y-%m-%d %H:%M:%S')
        run('systemctl', 'start', 'minecraft-console.socket', 'minecraft.service')
        log = wait_for_start(since)
        for needle in ['farmersdelight', 'mcwfurnitures', 'styledplayerlist', 'rightclickharvest', 'krypton', 'alternate',
                       'dungeons', 't_and_t', 'audioplayer', 'holylois-onboarding 1.4.0']:
            assert needle in log, 'Not loaded: ' + needle
        time.sleep(5)
        mark = time.strftime('%Y-%m-%d %H:%M:%S')
        console('gamerule players_sleeping_percentage 1')
        time.sleep(3)
        assert 'players_sleeping_percentage is now set to 1' in journal(mark), 'Sleep gamerule was not applied'
    except Exception:
        subprocess.run(['systemctl', 'stop', 'minecraft-console.socket', 'minecraft.service'])
        for target in installed:
            target.unlink(missing_ok=True)
        if (backup / ONBOARDING_OLD.name).exists() and not ONBOARDING_OLD.exists():
            shutil.copy2(backup / ONBOARDING_OLD.name, ONBOARDING_OLD); run('chown', 'minecraft:minecraft', str(ONBOARDING_OLD))
        for path in [JEB, MONSTERS]:
            if (backup / path.name).exists(): shutil.copy2(backup / path.name, path)
        shutil.rmtree(DATAPACK, ignore_errors=True)
        DROPIN.unlink(missing_ok=True)
        subprocess.run(['systemctl', 'daemon-reload'])
        subprocess.run(['systemctl', 'start', 'minecraft-console.socket', 'minecraft.service'])
        MAINTENANCE.unlink(missing_ok=True)
        print('Rolled back to the previous mods and settings. Backup kept at', backup)
        raise

    # The game is up. Side services are best-effort and never roll back the release.
    notes = []
    for step in (['systemctl', 'restart', 'fail2ban'], ['python3', str(LIB / 'botwall.py')], ['systemctl', 'enable', '--now', *TIMERS]):
        result = subprocess.run(step, capture_output=True, text=True)
        notes.append(f"{' '.join(step[:3])}: {'ok' if result.returncode == 0 else result.stderr.strip()[:200]}")
    MAINTENANCE.unlink(missing_ok=True)
    receipt = {'release': 'pack 1.6.1 server', 'backup': str(archive), 'mods_added': [p.name for p in staged],
               'onboarding': '1.4.0', 'runeforged_chest_tables_added': len(added), 'structure_datapack': 'holylois-structure-tuning',
               'sleep': 'players_sleeping_percentage 1', 'jvm': '6G fixed heap, Aikar G1 flags', 'jeb_max_total_mb': 12288,
               'services': notes, 'result': 'Done'}
    (backup / 'receipt.json').write_text(json.dumps(receipt, indent=2) + '\n')
    print(json.dumps(receipt, indent=2))


if __name__ == '__main__':
    main()
