"""Boot an isolated loopback copy of the live server with onboarding 1.8.4 swapped in, check its log and command audit, stop it.

Run as root from ~/hl-184. Never touches /opt/minecraft except to read it. Port 25566, voice 24455, Just Enough Backups off,
spawn region files only. Exit code 0 means every check passed.
"""
import json, shutil, subprocess, sys, time
from pathlib import Path

HOME = Path(__file__).resolve().parent
r = Path('/opt/minecraft'); t = Path('/opt/minecraft-test-184'); UNIT = 'minecraft-test-184'
JAR = HOME / 'holylois-onboarding-1.8.4+26.3.jar'
ADMIN_ONLY = ('dump_runtime_pack', 'lp', 'luckperms', 'perm', 'perms', 'permission', 'permissions', 'spark', 'modernfix', 'amber')

subprocess.run(['systemctl', 'stop', UNIT], stderr=subprocess.DEVNULL)
subprocess.run(['systemctl', 'reset-failed', UNIT], stderr=subprocess.DEVNULL)
if t.exists(): shutil.rmtree(t)
t.mkdir(mode=0o750)
for name in ['server.jar', 'eula.txt']: shutil.copy2(r / name, t / name)
shutil.copytree(r / 'mods', t / 'mods'); shutil.copytree(r / 'config', t / 'config')
if (r / '.fabric').exists(): shutil.copytree(r / '.fabric', t / '.fabric')  # remapped/cached jars: faster, proven bootstrap
for old in (t / 'mods').glob('holylois-onboarding-*.jar'): old.unlink()
shutil.copy2(JAR, t / 'mods' / JAR.name)
world = t / 'world'; world.mkdir()
shutil.copy2(r / 'world/level.dat', world / 'level.dat')
(world / 'data/minecraft').mkdir(parents=True)
shutil.copy2(r / 'world/data/minecraft/world_gen_settings.dat', world / 'data/minecraft/world_gen_settings.dat')
shutil.copytree(r / 'world/datapacks', world / 'datapacks')
regions = r / 'world/dimensions/minecraft/overworld/region'
region = world / regions.relative_to(r / 'world'); region.mkdir(parents=True)
for source in regions.glob('r.*.*.mca'):
    parts = source.name.split('.')
    if abs(int(parts[1])) <= 1 and abs(int(parts[2])) <= 1: shutil.copy2(source, region / source.name)
(t / 'server.properties').write_text('server-ip=127.0.0.1\nserver-port=25566\nonline-mode=true\nenforce-secure-profile=false\nmax-players=1\n'
                                     'view-distance=2\nsimulation-distance=2\nlevel-name=world\npause-when-empty-seconds=0\n')
p = t / 'config/voicechat/voicechat-server.properties'; p.write_text(p.read_text().replace('port=24454', 'port=24455').replace('bind_address=\n', 'bind_address=127.0.0.1\n'))
p = t / 'config/justenoughbackups.json'; j = json.loads(p.read_text()); j['automaticBackupsEnabled'] = False; p.write_text(json.dumps(j))
fifo = t / 'console.fifo'; subprocess.run(['mkfifo', str(fifo)], check=True)
subprocess.run(['chown', '-R', 'minecraft:minecraft', str(t)], check=True)
subprocess.Popen(['setsid', 'sh', '-c', f'exec sleep 900 > {fifo}'])  # keeps the FIFO open so stdin never sees EOF
time.sleep(1)
subprocess.run(['systemd-run', f'--unit={UNIT}', '--uid=minecraft', '--gid=minecraft', '--property=WorkingDirectory=' + str(t),
                f'--property=StandardInput=file:{fifo}', '--property=RuntimeMaxSec=600', '--property=KillSignal=SIGINT',
                '--property=TimeoutStopSec=30', '/usr/lib/jvm/java-25-openjdk-arm64/bin/java', '-Xms256M', '-Xmx2G',
                '-Dholylois.commandAudit=true', '-jar', 'server.jar', 'nogui'], check=True)
print('Test server launched on loopback 25566, waiting for it to start...', flush=True)

latest = t / 'logs/latest.log'; log = ''
for _ in range(480):
    time.sleep(1)
    log = latest.read_text(errors='replace') if latest.exists() else ''
    if 'Done (' in log or 'Crash report' in log or 'Incompatible mods' in log or 'Failed to start' in log or 'Failed to load datapacks' in log: break
    if subprocess.run(['systemctl', 'is-active', '--quiet', UNIT]).returncode != 0 and latest.exists(): break
started = 'Done (' in log
for _ in range(45 if started else 0):  # Holy Lois start-up lines come a few seconds after Done
    if 'command audit' in log and 'Holy Lois claims' in log: break
    time.sleep(1); log = latest.read_text(errors='replace')
subprocess.run(['systemctl', 'stop', UNIT])
shutil.copy2(latest, HOME / 'test-184-latest.log') if latest.exists() else None
audit = t / 'holylois-player-commands.txt'
shutil.copy2(audit, HOME / 'test-184-player-commands.txt') if audit.exists() else None
roots = {line.split(' ')[0][1:] for line in audit.read_text().splitlines()} if audit.exists() else set()

checks = {'server started': started,
          'onboarding 1.8.4 loaded': 'holylois-onboarding 1.8.4' in log,
          'onboarding ready (claims line)': 'Holy Lois claims: ready for OPAC' in log,
          'command audit ran': audit.exists() and len(roots) > 20,
          'players see no admin-only command': audit.exists() and not roots & set(ADMIN_ONLY),
          'players keep /claims /redeem /support /report /msg': {'claims', 'redeem', 'support', 'report', 'msg'} <= roots,
          'operators keep the admin-only commands': 'operators keep 0 admin' not in log and 'operators keep' in log,
          'no datapack errors': 'Registry loading errors' not in log and 'Failed to load datapacks' not in log,
          'no mixin or loader errors': 'Mixin apply failed' not in log and 'Incompatible mods' not in log and 'could not lock admin' not in log}
width = max(map(len, checks))
for name, ok in checks.items(): print(f'{name:<{width}}  {"OK" if ok else "FAILED"}')
print('Audit line:', next((l for l in log.splitlines() if 'command audit' in l), 'none'))
print('Log copy:', HOME / 'test-184-latest.log')
shutil.rmtree(t, ignore_errors=True)
(HOME / 'test-184.ok').unlink(missing_ok=True)
if all(checks.values()): (HOME / 'test-184.ok').write_text('passed')
sys.exit(0 if all(checks.values()) else 1)
