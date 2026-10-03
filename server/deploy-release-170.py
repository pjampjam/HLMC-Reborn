"""Holy Lois server release for pack 1.7.0. Run as root on the server from ~/hl-170.

Adds Macaw's Holidays and Holy Lois Extras (boombox; both sides), REI + Architectury (recipe sync), Clumps,
EconomyCraft (auction house, no admin shop), BlueMap (renders only while the server is empty, web on 127.0.0.1)
and onboarding 1.5.0 (daily gifts and Holy Lootbox, achievements, holiday events, paused time while empty,
leaderboards, discoveries, death coordinates, shapeless vein mining, no quote of the day). Also the Holy Lois
advancement datapack, the locator bar off, and the Trade Shop mod removed (replaced by /ah). Also: the cleaner Tab style, a server list line without the old tagline,
view-distance 12 (more real chunks before Distant Horizons takes over), the restart call in Discord alerts
and the weekly Discord recap. Refuses while players are online, makes a complete verified backup first and
restores the previous files if the server does not start.
"""
import datetime, hashlib, json, os, re, shutil, socket, struct, subprocess, time
from pathlib import Path

HOME = Path('/home/ubuntu/hl-170')
ROOT = Path('/opt/minecraft')
MODS = ROOT / 'mods'
ONBOARDING_OLD = MODS / 'holylois-onboarding-1.4.0+26.3.jar'
TRADE_SHOP = MODS / 'universal_shops-1.16.0+26.3.jar'
ONBOARDING_NEW = Path('/home/ubuntu/holylois-build-150/holylois-onboarding-1.5.0+26.3.jar')
HOLIDAYS = HOME / 'mcw-holidays-1.1.2-mc26.3fabric.jar'
EXTRAS = Path('/home/ubuntu/holylois-extras/holylois-extras-1.0.0+26.3.jar')
SERVER_MODS = sorted((HOME / 'server-mods').glob('*.jar'))
ADVANCEMENTS = ROOT / 'world/datapacks/holylois-advancements'
FIFO = Path('/run/minecraft-console.fifo')
STYLE = ROOT / 'config/styledplayerlist/styles/holylois.json'
MOTD = ROOT / 'config/MiniMOTD/main.conf'
QUOTES = ROOT / 'config/holylois-quotes.txt'
PROPERTIES = ROOT / 'server.properties'
LIB = Path('/usr/local/lib/holylois')
UNITS = Path('/etc/systemd/system')
MAINTENANCE = Path('/run/holylois-maintenance')
ALERT = LIB / 'discord-alert.py'
VIEW_DISTANCE = 12


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
        if 'Done (' in log and 'Holy Lois discoveries' in log: return log
        if 'Failed to start' in log or 'Crash report' in log or 'Incompatible mods' in log:
            raise RuntimeError('Minecraft failed to start')
    raise RuntimeError('Startup timeout')


def main():
    assert os.geteuid() == 0, 'Run as root'
    assert hashlib.sha512(HOLIDAYS.read_bytes()).hexdigest() == (HOME / 'holidays.sha512').read_text().strip(), 'Holidays jar hash'
    assert ONBOARDING_OLD.exists() and ONBOARDING_NEW.exists()
    assert not (MODS / HOLIDAYS.name).exists(), 'Holidays already installed'
    assert EXTRAS.exists() and len(SERVER_MODS) == 5, 'Extras jar or the five server mods are missing'
    assert not ADVANCEMENTS.exists() and not (ROOT / 'config/economycraft').exists() and not (ROOT / 'config/bluemap').exists()
    assert shutil.disk_usage(ROOT).free > 8 * 1024**3, 'Less than 8 GB free'
    style = json.loads((HOME / 'spl/styles/holylois.json').read_text())
    assert not any('holylois:quote' in line for page in style['list_footer']['values'] for line in page)
    assert 'Adventure' not in (HOME / 'minimotd-main.conf').read_text()
    players = online_players()
    assert players == 0, f'{players} player(s) online; deployment deferred'

    stamp = datetime.datetime.now(datetime.timezone.utc).strftime('%Y%m%dT%H%M%SZ')
    backup = Path('/opt/minecraft-backups/maintenance') / ('release170-' + stamp)
    backup.mkdir(mode=0o700)
    MAINTENANCE.touch()
    run('systemctl', 'stop', 'minecraft-console.socket', 'minecraft.service')
    installed = []
    saved = [ONBOARDING_OLD, TRADE_SHOP, STYLE, MOTD, PROPERTIES, QUOTES, ALERT]
    try:
        archive = backup / 'complete-server.tar.gz'
        run('tar', '--exclude=minecraft/backups', '-czf', str(archive), '-C', '/opt', 'minecraft')
        archive.chmod(0o600)
        run('tar', '-tzf', str(archive), stdout=subprocess.DEVNULL)
        for path in saved:
            if path.exists(): shutil.copy2(path, backup / path.name)

        for jar in [HOLIDAYS, ONBOARDING_NEW, EXTRAS, *SERVER_MODS]:
            target = MODS / jar.name
            run('install', '-o', 'minecraft', '-g', 'minecraft', '-m', '644', str(jar), str(target))
            installed.append(target)
        ONBOARDING_OLD.unlink()
        # No player shops exist (owner, 2026-10-04); the auction house replaces them.
        TRADE_SHOP.unlink(missing_ok=True)
        QUOTES.unlink(missing_ok=True)
        shutil.copytree(HOME / 'holylois-advancements', ADVANCEMENTS)
        shutil.copytree(HOME / 'config', ROOT / 'config', dirs_exist_ok=True)
        run('chown', '-R', 'minecraft:minecraft', str(ADVANCEMENTS), str(ROOT / 'config/economycraft'), str(ROOT / 'config/bluemap'))
        shutil.copy2(HOME / 'spl/styles/holylois.json', STYLE)
        shutil.copy2(HOME / 'minimotd-main.conf', MOTD)
        properties = PROPERTIES.read_text()
        properties, count = re.subn(r'(?m)^view-distance=\d+$', f'view-distance={VIEW_DISTANCE}', properties)
        assert count == 1, 'view-distance line not found'
        PROPERTIES.write_text(properties)
        run('chown', 'minecraft:minecraft', str(STYLE), str(MOTD), str(PROPERTIES))

        for script in ['discord-alert.py', 'weekly-recap.py']:
            shutil.copy2(HOME / 'ops' / script, LIB / script); (LIB / script).chmod(0o755)
        for unit in ['holylois-weekly-recap.service', 'holylois-weekly-recap.timer']:
            shutil.copy2(HOME / 'ops/units' / unit, UNITS / unit); (UNITS / unit).chmod(0o644)
        run('systemctl', 'daemon-reload')

        since = time.strftime('%Y-%m-%d %H:%M:%S')
        run('systemctl', 'start', 'minecraft-console.socket', 'minecraft.service')
        log = wait_for_start(since)
        for needle in ['mcwholidays', 'holylois-onboarding 1.5.0', 'holylois-extras', 'economycraft', 'bluemap', 'roughlyenoughitems', 'clumps',
                       'Holy Lois name day', 'Holy Lois discoveries']:
            assert needle in log, 'Not loaded: ' + needle
        assert 'Registry loading errors' not in log, 'A datapack failed to load'
        time.sleep(3)
        mark = time.strftime('%Y-%m-%d %H:%M:%S')
        with FIFO.open('w') as stream: stream.write('gamerule locator_bar false\n')
        time.sleep(3)
        assert 'locator_bar is now set to false' in journal(mark), 'Locator bar gamerule was not applied'
    except Exception:
        subprocess.run(['systemctl', 'stop', 'minecraft-console.socket', 'minecraft.service'])
        for target in installed:
            target.unlink(missing_ok=True)
        shutil.rmtree(ADVANCEMENTS, ignore_errors=True)
        shutil.rmtree(ROOT / 'config/economycraft', ignore_errors=True)
        shutil.rmtree(ROOT / 'config/bluemap', ignore_errors=True)
        for path in saved:
            if (backup / path.name).exists():
                shutil.copy2(backup / path.name, path)
                subprocess.run(['chown', 'root:root' if path == ALERT else 'minecraft:minecraft', str(path)])
        subprocess.run(['systemctl', 'start', 'minecraft-console.socket', 'minecraft.service'])
        MAINTENANCE.unlink(missing_ok=True)
        print('Rolled back to the previous mods and settings. Backup kept at', backup)
        raise

    notes = []
    result = subprocess.run(['systemctl', 'enable', '--now', 'holylois-weekly-recap.timer'], capture_output=True, text=True)
    notes.append('weekly recap timer: ' + ('ok' if result.returncode == 0 else result.stderr.strip()[:200]))
    # The first recap run only records a baseline; the first real recap arrives next Sunday.
    result = subprocess.run(['python3', str(LIB / 'weekly-recap.py')], capture_output=True, text=True)
    notes.append('weekly recap baseline: ' + (result.stdout.strip() or result.stderr.strip()[:200]))
    MAINTENANCE.unlink(missing_ok=True)
    message = ("**Maaarek nahhul!** Holy Lois 1.7.0 is live. Reopen the launcher and click Update. New address: **play.holylois.com**\n"
               "- Boombox: hold it and play internet radio for everyone nearby\n"
               "- Daily gifts, and a Holy Lootbox every 7th day in a row\n"
               "- Holy Lois achievement tab with secret challenges (press L)\n"
               "- Auction house: /ah, /sell, /pay, /daily\n"
               "- Recipe lookup (R / U in your inventory), holiday decorations and Latvian holiday events\n"
               "- Tab leaderboards, structure discoveries, death coordinates, live map at https://map.holylois.com\n"
               "- Fixes: J opens the map, chest flicker, key clashes, shapeless vein mining, merged XP orbs")
    result = subprocess.run(['python3', str(ALERT), 'message', message], capture_output=True, text=True)
    notes.append('discord: ' + ('ok' if result.returncode == 0 else result.stderr.strip()[:200]))
    receipt = {'release': 'pack 1.7.0 server', 'backup': str(archive), 'mods_added': [p.name for p in [HOLIDAYS, EXTRAS, *SERVER_MODS]],
               'onboarding': '1.5.0', 'view_distance': VIEW_DISTANCE, 'services': notes, 'result': 'Done'}
    (backup / 'receipt.json').write_text(json.dumps(receipt, indent=2) + '\n')
    print(json.dumps(receipt, indent=2))


if __name__ == '__main__':
    main()
