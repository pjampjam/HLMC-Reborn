"""Count usernames that SSH bots try and publish a small snapshot for the Holy Lois Tab list.

Runs every 10 minutes as root. Reads only new ssh journal lines (journalctl cursor file), never stores
IP addresses, and writes /opt/minecraft/config/holylois-botwall.json atomically for the server add-on.
"""
import datetime, json, os, re, subprocess, tempfile
from collections import Counter
from pathlib import Path
from zoneinfo import ZoneInfo

STATE_DIR = Path("/var/lib/holylois")
STATE = STATE_DIR / "botwall-state.json"
CURSOR = STATE_DIR / "botwall.cursor"
OUTPUT = Path("/opt/minecraft/config/holylois-botwall.json")
RIGA = ZoneInfo("Europe/Riga")
# "Invalid user admin from" (unknown account) and "authenticating user root" (real account, no key).
ATTEMPT = re.compile(r"(?:Invalid user (\S*) from|Connection closed by authenticating user (\S+) )")
SAFE = re.compile(r"[^A-Za-z0-9_.@-]")


def clean(name):
    return SAFE.sub("", name)[:16] or "(blank)"


def new_attempts():
    STATE_DIR.mkdir(mode=0o700, parents=True, exist_ok=True)
    args = ["journalctl", "-u", "ssh", "--no-pager", "-o", "short-iso", "--show-cursor"]
    # journalctl accepts only one of --since/--after-cursor, so the cursor is kept here instead of --cursor-file.
    args.append(f"--after-cursor={CURSOR.read_text().strip()}" if CURSOR.exists() else "--since=-24h")
    lines = subprocess.run(args, capture_output=True, text=True, encoding="utf-8", errors="replace").stdout.splitlines()
    if lines and lines[-1].startswith("-- cursor: "):
        CURSOR.write_text(lines.pop()[len("-- cursor: "):])
    for line in lines:
        match = ATTEMPT.search(line)
        if match:
            yield line[:25], clean(match.group(1) if match.group(1) is not None else match.group(2))


def banned_now():
    try:
        out = subprocess.run(["fail2ban-client", "status", "sshd"], capture_output=True, text=True, timeout=10).stdout
        found = re.search(r"Currently banned:\s*(\d+)", out)
        return int(found.group(1)) if found else 0
    except (OSError, subprocess.SubprocessError):
        return 0


def main():
    today = datetime.datetime.now(RIGA).date().isoformat()
    state = json.loads(STATE.read_text()) if STATE.exists() else {}
    if state.get("day") != today:
        state.update(day=today, today=0)
    counts = Counter(state.get("counts", {}))
    last = dict(state.get("last", {}))
    latest = list(state.get("latest", []))
    for stamp, name in new_attempts():
        counts[name] += 1
        local = datetime.datetime.fromisoformat(stamp).astimezone(RIGA) if stamp[:4].isdigit() else None
        last[name] = local.strftime("%d.%m %H:%M") if local else stamp
        state["today"] = state.get("today", 0) + 1
        state["all_time"] = state.get("all_time", 0) + 1
        latest = ([name] + [n for n in latest if n != name])[:10]
    # Keep the state small: only the 500 most common names.
    keep = dict(counts.most_common(500))
    state.update(counts=keep, last={n: last[n] for n in keep if n in last}, latest=latest)
    STATE.write_text(json.dumps(state))
    snapshot = {
        "today": state.get("today", 0), "allTime": state.get("all_time", 0), "banned": banned_now(), "latest": latest[:3],
        "top": [{"name": n, "count": c, "lastSeen": last.get(n, "")} for n, c in counts.most_common(10)],
    }
    fd, temporary = tempfile.mkstemp(dir=OUTPUT.parent, prefix=".botwall.")
    with os.fdopen(fd, "w") as stream:
        json.dump(snapshot, stream)
    os.chmod(temporary, 0o644)
    os.replace(temporary, OUTPUT)


if __name__ == "__main__":
    main()
