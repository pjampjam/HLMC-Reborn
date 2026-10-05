"""Boot an isolated loopback copy of the server with the full 1.8.0 set, check its log and stop it again.

Run as root from ~/hl-180 after the extras build. Never touches /opt/minecraft except to read it. Port 25566, voice 24455,
Just Enough Backups off, a few region files around spawn. Exit code 0 means every check passed.
"""
import json, re, shutil, subprocess, sys, time
from pathlib import Path

from importlib import util
spec = util.spec_from_file_location('release', '/home/ubuntu/hl-180/deploy-release-180.py'); release = util.module_from_spec(spec); spec.loader.exec_module(release)

r = Path('/opt/minecraft'); t = Path('/opt/minecraft-test-180'); HOME = release.HOME
UNIT = 'minecraft-test-180'
manifest, jars = release.planned()
subprocess.run(['systemctl', 'stop', UNIT], stderr=subprocess.DEVNULL)
subprocess.run(['systemctl', 'reset-failed', UNIT], stderr=subprocess.DEVNULL)
if t.exists(): shutil.rmtree(t)
t.mkdir(mode=0o750)
for name in ['server.jar', 'eula.txt']: shutil.copy2(r / name, t / name)
shutil.copytree(r / 'mods', t / 'mods'); shutil.copytree(r / 'config', t / 'config')
for old in (t / 'mods').glob('holylois-extras-*.jar'): old.unlink()
shutil.copy2(release.EXTRAS_NEW, t / 'mods')
for _, jar in jars: shutil.copy2(jar, t / 'mods' / jar.name)
for source, target in release.CONFIGS.items(): shutil.copy2(source, t / target.relative_to(r))
(t / 'config/holylois-pack.json').write_text(json.dumps({'minimum': '1.8.0'}) + '\n')
world = t / 'world'; world.mkdir()
shutil.copy2(r / 'world/level.dat', world / 'level.dat')
(world / 'data/minecraft').mkdir(parents=True)
shutil.copy2(r / 'world/data/minecraft/world_gen_settings.dat', world / 'data/minecraft/world_gen_settings.dat')
shutil.copytree(r / 'world/datapacks', world / 'datapacks')
shutil.rmtree(world / 'datapacks/holylois-advancements'); shutil.copytree(release.ADVANCEMENTS_NEW, world / 'datapacks/holylois-advancements')
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
# A sleeping writer keeps the FIFO open so the server's stdin never sees EOF.
subprocess.Popen(['setsid', 'sh', '-c', f'exec sleep 900 > {fifo}'])
time.sleep(1)
subprocess.run(['systemd-run', f'--unit={UNIT}', '--uid=minecraft', '--gid=minecraft', '--property=WorkingDirectory=' + str(t),
                f'--property=StandardInput=file:{fifo}', '--property=RuntimeMaxSec=600', '--property=KillSignal=SIGINT',
                '--property=TimeoutStopSec=30', '/usr/lib/jvm/java-25-openjdk-arm64/bin/java', '-Xms256M', '-Xmx2G', '-jar', 'server.jar', 'nogui'], check=True)
print('Test server launched on loopback 25566, waiting for it to start...')

latest = t / 'logs/latest.log'
log = ''
for _ in range(420):
    time.sleep(1)
    log = latest.read_text(errors='replace') if latest.exists() else ''
    if 'Done (' in log or 'Crash report' in log or 'Incompatible mods' in log or 'Failed to start' in log: break
    if subprocess.run(['systemctl', 'is-active', '--quiet', UNIT]).returncode != 0 and latest.exists(): break
started = 'Done (' in log
if started:
    with fifo.open('w') as console:
        console.write('legends list\n')
        console.write('execute in minecraft:overworld positioned 0 120 0 run loot spawn ~ ~ ~ loot holylois:gameplay/treasure_map\n')
        console.write('execute in minecraft:overworld positioned 0 120 0 run loot spawn ~ ~ ~ loot minecraft:gameplay/fishing\n')
    time.sleep(8)
    log = latest.read_text(errors='replace')
subprocess.run(['systemctl', 'stop', UNIT])
shutil.copy2(latest, HOME / 'test-180-latest.log') if latest.exists() else None

checks = {'server started': started,
          'extras 1.6.0 loaded': 'holylois-extras 1.6.0' in log,
          'legends config read (3 legends)': 'Holy Lois legends: 3 legends' in log,
          'fish config read (14 species)': 'fish weights: 14 species' in log,
          'legends command works': 'Legend items: circlet_of_the_wanderer' in log,
          'treasure map loot table runs': 'Unknown loot table' not in log and 'holylois:gameplay/treasure_map' not in ''.join(l for l in log.splitlines() if 'rror' in l),
          'no datapack errors': 'Registry loading errors' not in log,
          'holylois advancements load': not re.search(r'(?i)(error|couldn.t|failed)[^\n]{0,120}holylois:', log),
          'no mixin or loader errors': 'Mixin apply failed' not in log and 'Incompatible mods' not in log}
for mod_id, jar in jars: checks[f'{mod_id} loaded ({jar.name})'] = f'- {mod_id} ' in log
width = max(map(len, checks))
for name, ok in checks.items(): print(f'{name:<{width}}  {"OK" if ok else "FAILED"}')
print('Log copy:', HOME / 'test-180-latest.log')
sys.exit(0 if all(checks.values()) else 1)
