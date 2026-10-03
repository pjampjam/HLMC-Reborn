"""Build an isolated loopback copy of the server with the full 1.6.1 server set and boot it with a console FIFO.

Run as root from ~/hl-161. Never touches /opt/minecraft except to read it.
"""
import hashlib, json, pathlib, shutil, subprocess, time

HOME = pathlib.Path('/home/ubuntu/hl-161')
r = pathlib.Path('/opt/minecraft'); t = pathlib.Path('/opt/minecraft-test-161')
manifest = json.loads((HOME / 'new-mods.json').read_text())
jars = []
for slug in manifest['sides']['server'] + manifest['sides']['server161']:
    m = manifest['mods'][slug]; jar = HOME / 'server-mods' / m['filename']
    assert hashlib.sha512(jar.read_bytes()).hexdigest() == m['sha512'], slug
    jars.append(jar)
subprocess.run(['systemctl', 'stop', 'minecraft-test-161'], stderr=subprocess.DEVNULL)
subprocess.run(['systemctl', 'reset-failed', 'minecraft-test-161'], stderr=subprocess.DEVNULL)
if t.exists(): shutil.rmtree(t)
t.mkdir(mode=0o750)
for name in ['server.jar', 'eula.txt']: shutil.copy2(r / name, t / name)
shutil.copytree(r / 'mods', t / 'mods'); shutil.copytree(r / 'config', t / 'config')
(t / 'mods/holylois-onboarding-1.3.0+26.3.jar').unlink()
shutil.copy2('/home/ubuntu/holylois-build-140/holylois-onboarding-1.4.0+26.3.jar', t / 'mods')
for jar in jars: shutil.copy2(jar, t / 'mods' / jar.name)
spl = t / 'config/styledplayerlist/styles'; spl.mkdir(parents=True, exist_ok=True)
shutil.copy2(HOME / 'spl/config.json', spl.parent / 'config.json'); shutil.copy2(HOME / 'spl/styles/holylois.json', spl / 'holylois.json')
monsters = t / 'config/runeforged-monsters.json'; data = json.loads(monsters.read_text())
known = {e['loot_table'] for e in data['chest_loot_tables']}
data['chest_loot_tables'] += [e for e in json.loads((HOME / 'runeforged-chest-additions.json').read_text()) if e['loot_table'] not in known]
monsters.write_text(json.dumps(data, indent=1))
(t / 'config/holylois-botwall.json').write_text(json.dumps({"today": 3407, "allTime": 3407, "banned": 2, "latest": ["root", "admin", "test"],
                                                           "top": [{"name": "root", "count": 1435, "lastSeen": "03.10 20:34"}]}))
world = t / 'world'; world.mkdir()
shutil.copy2(r / 'world/level.dat', world / 'level.dat')
(world / 'data/minecraft').mkdir(parents=True)
shutil.copy2(r / 'world/data/minecraft/world_gen_settings.dat', world / 'data/minecraft/world_gen_settings.dat')
shutil.copytree(HOME / 'holylois-structure-tuning', world / 'datapacks/holylois-structure-tuning')
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
subprocess.run(['systemd-run', '--unit=minecraft-test-161', '--uid=minecraft', '--gid=minecraft', '--property=WorkingDirectory=' + str(t),
                f'--property=StandardInput=file:{fifo}', '--property=RuntimeMaxSec=600', '--property=KillSignal=SIGINT',
                '--property=TimeoutStopSec=30', '/usr/lib/jvm/java-25-openjdk-arm64/bin/java', '-Xms256M', '-Xmx2G', '-jar', 'server.jar', 'nogui'], check=True)
print('Test server launched on loopback 25566; console at', fifo)
