"""Public server stats for holylois.com, written as one JSON file (read-only on the world).

Sources: vanilla stats and advancement files, usercache.json, the Holy Lois datapack (titles), discoveries, daily
streaks, EconomyCraft balances and the published pack changelog. Only usernames and game numbers leave the server: no UUIDs, IPs or coordinates.
Names with slurs are masked (first letter + stars, the row stays); names listed in /etc/holylois/stats-hidden.txt never appear.
Usage: python3 make-stats.py [SERVER_ROOT] OUTPUT_JSON
"""
import datetime, json, os, re, sys, tempfile, urllib.request
from pathlib import Path

ROOT = Path(sys.argv[1]) if len(sys.argv) > 2 else Path('/opt/minecraft')
OUT = Path(sys.argv[-1])
WORLD = ROOT / 'world'
HIDDEN_FILE = Path('/etc/holylois/stats-hidden.txt')
SLURS = re.compile(r'n[i1!]gg|f[a@]gg?[o0]t|f[a@]g$|r[e3]t[a@]rd|p[i1]d[o0a]r|п[иі]д[оа]р|k[i1]ke|ch[i1]nk|tr[a@]nny', re.I)
TOP = 5
PACK_FEED = 'https://github.com/pjampjam/HLMC-Reborn/releases/download/pack-stable/pack.json'


def read(path, default=None):
    try: return json.loads(Path(path).read_text(encoding='utf-8'))
    except (OSError, ValueError): return default


def mask(name):
    """Keep the row but never the word: 'N*****'. Fixed length, so the mask does not hint at the original."""
    return name[0].upper() + '*****'


def names():
    hidden = {line.strip().lower() for line in HIDDEN_FILE.read_text().splitlines() if line.strip()} if HIDDEN_FILE.exists() else set()
    result, raw = {}, {}
    for entry in read(ROOT / 'usercache.json', []):
        name = entry.get('name', '')
        if not name or name.lower() in hidden: continue
        shown = mask(name) if SLURS.search(name) else name
        while shown in result.values(): shown += '*'
        result[entry['uuid']] = shown; raw[name] = shown
    return result, raw


def online_now():
    """Players online right now, from a status ping to the local server (None if it does not answer)."""
    import socket, struct
    def varint(n):
        out = b''
        while True:
            byte, n = n & 0x7f, n >> 7
            out += bytes([byte | (0x80 if n else 0)])
            if not n: return out
    try:
        with socket.create_connection(('127.0.0.1', 25565), 5) as s:
            hello = b'\x00' + varint(770) + varint(9) + b'localhost' + struct.pack('>H', 25565) + varint(1)
            s.sendall(varint(len(hello)) + hello + b'\x01\x00')
            data = b''
            while chunk := s.recv(65536):
                data += chunk
                try: return json.loads(data[data.index(b'{'):].decode())['players']['online']
                except ValueError: continue
    except (OSError, KeyError):
        return None


def holylois_advancements():
    base = WORLD / 'datapacks/holylois-advancements/data/holylois/advancement'
    found = {}
    for file in sorted(base.rglob('*.json')):
        data = read(file, {})
        display = data.get('display')
        path = file.relative_to(base).with_suffix('').as_posix()
        if display and path != 'root':
            found['holylois:' + path] = {'title': display.get('title', path), 'description': display.get('description', ''),
                                         'secret': bool(display.get('hidden')), 'frame': display.get('frame', 'task')}
    return found


def when(text):
    try: return datetime.datetime.strptime(text, '%Y-%m-%d %H:%M:%S %z').astimezone(datetime.timezone.utc)
    except (TypeError, ValueError): return None


def main():
    people, shown_as = names()
    stats, done = {}, {}
    for file in (WORLD / 'players/stats').glob('*.json'):
        if file.stem in people: stats[file.stem] = read(file, {}).get('stats', {})
    # AFK time does not count as played (ledger of the onboarding add-on, 20 ticks per AFK second).
    afk = read(WORLD / 'holylois/afk.json', {}).get('seconds', {})
    for uuid, mine in stats.items():
        played = mine.get('minecraft:custom', {})
        if uuid in afk and 'minecraft:play_time' in played: played['minecraft:play_time'] = max(0, played['minecraft:play_time'] - afk[uuid] * 20)
    for file in (WORLD / 'players/advancements').glob('*.json'):
        if file.stem not in people: continue
        mine = {}
        for key, value in read(file, {}).items():
            if isinstance(value, dict) and value.get('done') and not key.startswith('minecraft:recipes/') and '/recipes/' not in key:
                times = [t for t in map(when, value.get('criteria', {}).values()) if t]
                mine[key] = max(times) if times else None
        done[file.stem] = mine

    custom = lambda uuid, key: stats.get(uuid, {}).get('minecraft:custom', {}).get('minecraft:' + key, 0)
    group = lambda uuid, kind: stats.get(uuid, {}).get('minecraft:' + kind, {})
    distance = lambda uuid: sum(v for k, v in group(uuid, 'custom').items() if k.endswith('_one_cm') and 'fall' not in k) / 100_000
    diamonds = lambda uuid: sum(v for k, v in group(uuid, 'mined').items() if k.endswith('diamond_ore'))
    defined = holylois_advancements()
    holy = lambda uuid: sum(1 for key in done.get(uuid, {}) if key in defined)
    daily = read(WORLD / 'holylois/daily.json', {}).get('players', {})
    coins = read(ROOT / 'config/economycraft/data/balances.json', {})

    boards = [
        ('playtime', 'Most time played', 'hours', lambda u: round(custom(u, 'play_time') / 72000, 1)),
        ('achievements', 'Holy Lois achievements', f'of {len(defined)}', holy),
        ('advancements', 'All advancements', 'done', lambda u: len(done.get(u, {}))),
        ('diamonds', 'Diamonds mined', 'ores', diamonds),
        ('distance', 'Distance travelled', 'km', lambda u: round(distance(u), 1)),
        ('mobs', 'Mobs defeated', 'mobs', lambda u: custom(u, 'mob_kills')),
        ('fish', 'Fish caught', 'fish', lambda u: custom(u, 'fish_caught')),
        ('blocks', 'Blocks mined', 'blocks', lambda u: sum(group(u, 'mined').values())),
        ('streak', 'Longest daily streak', 'days', lambda u: daily.get(u, {}).get('best', 0)),
        ('coins', 'Richest', 'coins', lambda u: coins.get(u, 0)),
        ('deaths', 'Most deaths', 'deaths', lambda u: custom(u, 'deaths')),
    ]
    leaderboards = []
    for key, title, unit, value in boards:
        rows = sorted(((people[u], value(u)) for u in people if u in stats or u in done or u in daily or u in coins), key=lambda r: (-r[1], r[0].lower()))
        rows = [{'name': n, 'value': v} for n, v in rows if v][:TOP]
        if rows: leaderboards.append({'id': key, 'title': title, 'unit': unit, 'entries': rows})

    achievements = []
    for key, info in defined.items():
        earners = sorted(((t, people[u]) for u, mine in done.items() if key in mine for t in [mine[key]]), key=lambda r: (r[0] is None, r[0] or 0))
        known = bool(earners) or not info['secret']
        achievements.append({'id': key, 'title': info['title'] if known else 'Secret achievement',
                             'description': info['description'] if known else 'Nobody has found this one yet.',
                             'frame': info['frame'], 'secret': info['secret'], 'earned_by': len(earners),
                             'first': {'name': earners[0][1], 'date': earners[0][0].date().isoformat() if earners[0][0] else None} if earners else None})
    achievements.sort(key=lambda a: (-a['earned_by'], a['title']))
    earned = [a for a in achievements if a['earned_by']]
    rarest = sorted(earned, key=lambda a: (a['earned_by'], a['first']['date'] or ''))[:3]

    firsts = []
    for entry in read(WORLD / 'holylois/discoveries.json', {}).get('found', []):
        name = entry.get('player', '')
        firsts.append({'what': entry.get('name', ''), 'player': shown_as.get(name, 'Someone'),
                       'date': datetime.datetime.fromtimestamp(entry.get('time', 0), datetime.timezone.utc).date().isoformat()})
    firsts.sort(key=lambda f: f['date'], reverse=True)

    # The live pack's own changelog, so the website's update list follows each release by itself.
    pack = (read(OUT, {}) or {}).get('pack')
    try:
        manifest = json.loads(urllib.request.urlopen(PACK_FEED, timeout=15).read())
        pack = {'version': manifest['version'], 'history': manifest.get('history', [])[:8]}
    except Exception:
        pass

    everyone = list(stats)
    report = {
        'pack': pack,
        'generated': datetime.datetime.now(datetime.timezone.utc).isoformat(timespec='seconds'),
        # 'players' is everyone who has joined (kept for old readers); 'online' is a live ping at generation time.
        'server': {'address': 'play.holylois.com', 'players': len(people), 'registered_players': len(people), 'online': online_now(), 'world_day': read(WORLD / 'holylois/events.json', {}).get('lastDay')},
        'totals': {
            'hours_played': round(sum(custom(u, 'play_time') for u in everyone) / 72000),
            'km_travelled': round(sum(distance(u) for u in everyone)),
            'blocks_mined': sum(sum(group(u, 'mined').values()) for u in everyone),
            'mobs_defeated': sum(custom(u, 'mob_kills') for u in everyone),
            'diamonds': sum(diamonds(u) for u in everyone),
            'fish_caught': sum(custom(u, 'fish_caught') for u in everyone),
            'deaths': sum(custom(u, 'deaths') for u in everyone),
            'cake_slices': sum(custom(u, 'eat_cake_slice') for u in everyone),
            'achievements_earned': sum(a['earned_by'] for a in achievements),
        },
        'leaderboards': leaderboards,
        'achievements': {'total': len(defined), 'rarest': rarest, 'list': achievements},
        'world_firsts': firsts[:20],
    }
    text = json.dumps(report, indent=2, ensure_ascii=False) + '\n'
    assert not SLURS.search(text), 'A filtered name reached the output'
    OUT.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.NamedTemporaryFile('w', dir=OUT.parent, delete=False, encoding='utf-8') as temp: temp.write(text)
    os.chmod(temp.name, 0o644); os.replace(temp.name, OUT)
    print(f'{OUT}: {len(people)} players, {len(leaderboards)} boards, {len(earned)}/{len(defined)} achievements earned, {len(firsts)} world firsts')


if __name__ == '__main__':
    main()
