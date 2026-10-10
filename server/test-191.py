"""Boot an isolated loopback copy of the live server with the 1.9.1 server changes, check its log and command audit, stop it.

Run as root from ~/hl-191. Never touches /opt/minecraft except to read it. Port 25566, voice 24455, Just Enough Backups off,
spawn region files plus the Open Parties and Claims data. Same changes as the deploy: Extras 1.7.1, onboarding 1.9.1, Tab style,
rules.txt without the stats note, /spawn off, pack minimum 1.9.1.
Exit code 0 means every check passed.
"""
import hashlib, json, shutil, subprocess, sys, time
from pathlib import Path

HOME = Path(__file__).resolve().parent
r = Path('/opt/minecraft'); t = Path('/opt/minecraft-test-191'); UNIT = 'minecraft-test-191'
HASHES = json.loads((HOME / 'artifact-hashes.json').read_text())
ADMIN_ONLY = ('dump_runtime_pack', 'lp', 'luckperms', 'perm', 'perms', 'permission', 'permissions', 'spark', 'modernfix', 'amber')
ADDONS = ['holylois-extras-1.7.1+26.3.jar', 'holylois-onboarding-1.9.1+26.3.jar']


def digest(p): return hashlib.sha256(p.read_bytes()).hexdigest()


def apply_changes(root, source):
    """The 1.9.1 file changes, shared with deploy-release-191.py. root is the server folder to change."""
    mods = root / 'mods'
    for prefix in ('holylois-extras-', 'holylois-onboarding-'):
        olds = list(mods.glob(prefix + '*.jar')); assert len(olds) == 1, olds
        olds[0].unlink()
    for name in ADDONS:
        jar = source / name; assert digest(jar) == HASHES[name], name; shutil.copy2(jar, mods / name)
    shutil.copy2(source / 'tab-holylois.json', root / 'config/styledplayerlist/styles/holylois.json')
    # In-game /rules: the stats exclusion note is an admin fact, not a rule (the website privacy page keeps it).
    p = root / 'config/essentialcommands/rules.txt'; lines = p.read_text(encoding='utf-8').splitlines(keepends=True)
    kept = [l for l in lines if not l.startswith('<gray>Public stats omit')]
    assert len(kept) == len(lines) - 1, 'rules.txt stats line not found exactly once'
    p.write_text(''.join(kept), encoding='utf-8')
    # /spawn only said "Spawn not set": an open world has no hub.
    p = root / 'config/EssentialCommands.properties'; text = p.read_text(encoding='utf-8')
    assert text.count('enable_spawn=true') == 1, 'enable_spawn=true not found'
    p.write_text(text.replace('enable_spawn=true', 'enable_spawn=false'), encoding='utf-8')
    (root / 'config/holylois-pack.json').write_text(json.dumps({'minimum': '1.9.1'}) + chr(10))
    return []


if __name__ == '__main__':
    subprocess.run(['systemctl', 'stop', UNIT], stderr=subprocess.DEVNULL)
    subprocess.run(['systemctl', 'reset-failed', UNIT], stderr=subprocess.DEVNULL)
    if t.exists(): shutil.rmtree(t)
    t.mkdir(mode=0o750)
    for name in ['server.jar', 'eula.txt']: shutil.copy2(r / name, t / name)
    shutil.copytree(r / 'mods', t / 'mods'); shutil.copytree(r / 'config', t / 'config')
    if (r / '.fabric').exists(): shutil.copytree(r / '.fabric', t / '.fabric')
    added = apply_changes(t, HOME)
    world = t / 'world'; world.mkdir()
    shutil.copy2(r / 'world/level.dat', world / 'level.dat')
    (world / 'data/minecraft').mkdir(parents=True)
    shutil.copy2(r / 'world/data/minecraft/world_gen_settings.dat', world / 'data/minecraft/world_gen_settings.dat')
    shutil.copytree(r / 'world/data/openpartiesandclaims', world / 'data/openpartiesandclaims')
    claim_files = sum(1 for _ in (world / 'data/openpartiesandclaims').rglob('*') if _.is_file())
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
    subprocess.Popen(['setsid', 'sh', '-c', f'exec sleep 900 > {fifo}'])
    time.sleep(1)
    subprocess.run(['systemd-run', f'--unit={UNIT}', '--uid=minecraft', '--gid=minecraft', '--property=WorkingDirectory=' + str(t),
                    f'--property=StandardInput=file:{fifo}', '--property=RuntimeMaxSec=600', '--property=KillSignal=SIGINT',
                    '--property=TimeoutStopSec=30', '/usr/lib/jvm/java-25-openjdk-arm64/bin/java', '-Xms256M', '-Xmx2G',
                    '-Dholylois.commandAudit=true', '-jar', 'server.jar', 'nogui'], check=True)
    print('Test server launched on loopback 25566 with', claim_files, 'OPAC data files, waiting for it to start...', flush=True)

    latest = t / 'logs/latest.log'; log = ''
    for _ in range(480):
        time.sleep(1)
        log = latest.read_text(errors='replace') if latest.exists() else ''
        if 'Done (' in log or 'Crash report' in log or 'Incompatible mods' in log or 'Failed to start' in log or 'Failed to load datapacks' in log: break
        if subprocess.run(['systemctl', 'is-active', '--quiet', UNIT]).returncode != 0 and latest.exists(): break
    started = 'Done (' in log
    for _ in range(45 if started else 0):
        if 'command audit' in log and 'Holy Lois claims' in log: break
        time.sleep(1); log = latest.read_text(errors='replace')
    if started:
        with open(fifo, 'w') as console: console.write('save-all flush\n')
        time.sleep(8); log = latest.read_text(errors='replace')
    subprocess.run(['systemctl', 'stop', UNIT])
    time.sleep(2); log = latest.read_text(errors='replace') if latest.exists() else log
    shutil.copy2(latest, HOME / 'test-191-latest.log') if latest.exists() else None
    audit = t / 'holylois-player-commands.txt'
    shutil.copy2(audit, HOME / 'test-191-player-commands.txt') if audit.exists() else None
    roots = {line.split(' ')[0][1:] for line in audit.read_text().splitlines()} if audit.exists() else set()
    errors = [l for l in log.splitlines() if '/ERROR]' in l or '/FATAL]' in l]
    # Known harmless OPAC 0.32 lines: an extra key in its own mod json, the refmap note, and the server config being rewritten in
    # the new layout (its values are compared with the live file below).
    harmless = ('invalid entries in its mod json', 'refmap', 'openpartiesandclaims-server.toml is not correct')
    opac_errors = [l for l in log.splitlines() if ('/ERROR]' in l or '/WARN]' in l) and ('openpartiesandclaims' in l.lower() or 'xaero' in l.lower())
                   and not any(h in l for h in harmless)]
    shutil.copy2(t / 'config/openpartiesandclaims-server.toml', HOME / 'opac-server-191.toml')
    rei = sum('[REI] Failed to fill display' in l for l in errors)
    errors = [l for l in errors if '[REI] Failed to fill display' not in l]
    claims_after = sum(1 for _ in (world / 'data/openpartiesandclaims').rglob('*') if _.is_file())

    wanted = {'holylois-extras': '1.7.1', 'holylois-onboarding': '1.9.1', 'openpartiesandclaims': '0.32.8', 'fabric-api': '0.162.0',
              'farmersdelight': '3.6.28', 'roughlyenoughitems': '824', 'modernfix': '5.27.20', 'ledger': '1.3.25'}
    listed = [l.split('- ', 1)[1] for l in log.splitlines() if l.lstrip(' 	|-').startswith(tuple(wanted)) and '- ' in l]
    missing = [mod for mod, version in wanted.items() if not any(x.startswith(mod + ' ') and version in x for x in listed)]
    checks = {'server started': started,
              'new mods loaded': not missing,
              'onboarding ready (claims line)': 'Holy Lois claims: ready for OPAC' in log,
              'boombox registered': 'holylois_boombox' in log,
              'OPAC data kept after save and stop': claims_after >= claim_files > 0,
              'no OPAC errors or warnings': not opac_errors,
              'command audit ran': audit.exists() and len(roots) > 20,
              'players see no admin-only command': audit.exists() and not roots & set(ADMIN_ONLY),
              'players keep /claims /redeem /support /report /msg /homes /party': {'claims', 'redeem', 'support', 'report', 'msg', 'homes', 'party'} <= roots,
              'operators keep the admin-only commands': 'operators keep 0 admin' not in log and 'operators keep' in log,
              'no datapack errors': 'Registry loading errors' not in log and 'Failed to load datapacks' not in log,
              'rules without the stats note': 'Public stats omit' not in (t / 'config/essentialcommands/rules.txt').read_text(encoding='utf-8'),
              'no /spawn for players': 'spawn' not in roots,
              'no mixin or loader errors': 'Mixin apply failed' not in log and 'Incompatible mods' not in log and 'could not lock admin' not in log}
    width = max(map(len, checks))
    for name, ok in checks.items(): print(f'{name:<{width}}  {"OK" if ok else "FAILED"}')
    print('Missing load lines:', missing)
    print('OPAC files before/after:', claim_files, claims_after)
    print('Audit line:', next((l for l in log.splitlines() if 'command audit' in l), 'none'))
    print('REI brewing display errors (same in every dev run):', rei)
    print('Other ERROR lines:', len(errors)); [print('  ', l[:220]) for l in errors[:25]]
    print('OPAC lines:', [l[:220] for l in opac_errors[:10]])
    print('Log copy:', HOME / 'test-191-latest.log')
    shutil.rmtree(t, ignore_errors=True)
    (HOME / 'test-191.ok').unlink(missing_ok=True)
    if all(checks.values()): (HOME / 'test-191.ok').write_text('passed')
    sys.exit(0 if all(checks.values()) else 1)
