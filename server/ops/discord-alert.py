"""Post Holy Lois server down/up alerts to a Discord webhook.

  discord-alert.py check     every 2 minutes (timer): alerts after two failed status checks, and on recovery
  discord-alert.py failure   OnFailure= hook of minecraft.service: immediate crash report
  discord-alert.py test      sends a test message
  discord-alert.py message TEXT
Every restart, planned or not, is announced once with the group's restart call: "Maaarek nahhul!".

The webhook URL lives only in /etc/holylois/discord-webhook (root, mode 600), written by the owner.
Without it every mode exits quietly. /run/holylois-maintenance silences alerts during planned work.
"""
import glob, json, os, shutil, socket, struct, subprocess, sys, time, urllib.request
from pathlib import Path

WEBHOOK = Path("/etc/holylois/discord-webhook")
STATE = Path("/var/lib/holylois/discord-alert.json")
MAINTENANCE = Path("/run/holylois-maintenance")
ROOT = Path("/opt/minecraft")
GOLD, RED, GREEN = 0xF4C542, 0xC2362F, 0x34D27B
MEME = "**Maaarek nahhul!**"


def post(title, description, color, fields=()):
    if not WEBHOOK.exists():
        print("No Discord webhook configured; nothing sent.")
        return
    url = WEBHOOK.read_text().strip()
    if not url.startswith("https://discord.com/api/webhooks/") and not url.startswith("https://discordapp.com/api/webhooks/"):
        print("The webhook file does not contain a Discord webhook URL.")
        return
    embed = {"title": title, "description": description[:3900], "color": color,
             "fields": [{"name": n, "value": v[:1000] or "-", "inline": False} for n, v in fields],
             "footer": {"text": "Holy Lois: Reborn server monitor"}}
    body = json.dumps({"username": "Holy Lois Server", "embeds": [embed]}).encode()
    request = urllib.request.Request(url, data=body, headers={"Content-Type": "application/json", "User-Agent": "HolyLoisMonitor/1.0"})
    urllib.request.urlopen(request, timeout=15).read()


def varint(value):
    out = bytearray()
    while True:
        b = value & 127; value >>= 7
        out.append(b | (128 if value else 0))
        if not value:
            return bytes(out)


def online():
    """Returns the online player count, or None when the server does not answer a status ping."""
    try:
        with socket.create_connection(("127.0.0.1", 25565), timeout=8) as s:
            host = b"localhost"
            packet = b"\x00" + varint(0) + varint(len(host)) + host + struct.pack(">H", 25565) + b"\x01"
            s.sendall(varint(len(packet)) + packet + b"\x01\x00")
            data, deadline = b"", time.time() + 8
            while time.time() < deadline:
                chunk = s.recv(65536)
                if not chunk:
                    break
                data += chunk
                start = data.find(b"{")
                if start >= 0:
                    try:
                        return json.loads(data[start:].decode("utf-8"))["players"]["online"]
                    except ValueError:
                        continue
    except OSError:
        return None
    return None


def diagnostics():
    status = subprocess.run(["systemctl", "show", "minecraft", "-p", "ActiveState,SubState,Result,NRestarts,ExecMainStatus"],
                            capture_output=True, text=True).stdout.strip().replace("\n", ", ")
    journal = subprocess.run(["journalctl", "-u", "minecraft", "-n", "400", "--no-pager", "-o", "cat"],
                             capture_output=True, text=True, errors="replace").stdout.splitlines()
    errors = [l for l in journal if any(k in l for k in ("ERROR", "Exception", "FATAL", "Caused by", "OutOfMemory", "Crash"))]
    crash = ""
    reports = sorted(glob.glob(str(ROOT / "crash-reports" / "*.txt")), key=os.path.getmtime)
    if reports and time.time() - os.path.getmtime(reports[-1]) < 3600:
        text = Path(reports[-1]).read_text(errors="replace").splitlines()
        description = next((l for l in text if l.startswith("Description:")), "Description: unknown")
        first = next((i for i, l in enumerate(text) if l.strip() and l[0] not in "-/ " and "Exception" in l), None)
        crash = description + ("\n" + "\n".join(text[first:first + 6]) if first is not None else "") + f"\n({Path(reports[-1]).name})"
    disk = shutil.disk_usage("/")
    memory = Path("/proc/meminfo").read_text().split("\n")
    available = next((l.split()[1] for l in memory if l.startswith("MemAvailable")), "0")
    health = f"Disk free {disk.free / 1024**3:.1f} GB, memory available {int(available) / 1024**2:.1f} GB"
    log_tail = "\n".join((errors or journal)[-12:])
    return status, crash, health, log_tail


def advice(crash, health):
    tips = ["It usually restarts by itself within a minute; this channel says when it is back."]
    if "OutOfMemory" in crash:
        tips.append("Out of memory: someone may have loaded a huge area. Check /spark health after it is back.")
    if "Disk free 0." in health or "Disk free 1." in health:
        tips.append("The disk is almost full. Free space before the next backup.")
    tips.append("If it stays down, open Holy Lois Admin > Server start / stop / update > Status and Logs, or send this message to the assistant.")
    return "\n".join(f"- {t}" for t in tips)


def invocation():
    """systemd gives every start of the service a new id, so any restart is noticed."""
    return subprocess.run(["systemctl", "show", "minecraft", "-p", "InvocationID", "--value"], capture_output=True, text=True).stdout.strip() or None


def restart_count():
    value = subprocess.run(["systemctl", "show", "minecraft", "-p", "NRestarts", "--value"], capture_output=True, text=True).stdout.strip()
    return int(value) if value.isdigit() else 0


def load():
    return json.loads(STATE.read_text()) if STATE.exists() else {"up": True, "failures": 0, "down_since": None}


def save(state):
    STATE.parent.mkdir(mode=0o700, parents=True, exist_ok=True)
    STATE.write_text(json.dumps(state))


def report_down(state, reason):
    status, crash, health, tail = diagnostics()
    post("Holy Lois server is DOWN", f"{reason}\nSince {time.strftime('%d.%m %H:%M UTC', time.gmtime(state['down_since']))}.", RED,
         [("Service", status), ("Crash report", crash or "No recent crash report."), ("Recent errors", f"```{tail[-900:]}```"),
          ("Health", health), ("What to do", advice(crash, health))])


def main():
    mode = sys.argv[1] if len(sys.argv) > 1 else "check"
    if mode == "test":
        post("Holy Lois monitor test", "Alerts are connected. You will hear from me when the server goes down and when it is back.", GOLD)
        return
    if mode == "message":
        post("Holy Lois server", " ".join(sys.argv[2:]), GOLD)
        return
    if MAINTENANCE.exists():
        print("Planned maintenance; alerts paused.")
        return
    state = load()
    if mode == "failure":
        if state["up"]:
            state.update(up=False, down_since=time.time(), alerted=True)
            save(state)
            report_down(state, "The Minecraft service crashed or exited with an error.")
        return
    restarts = restart_count()
    run = invocation()
    players = online()
    if players is not None:
        restarted = state.get("invocation") not in (None, run)
        if not state["up"] and state.get("alerted"):
            minutes = int((time.time() - (state["down_since"] or time.time())) / 60)
            post("Holy Lois server is back online", f"{MEME}\nDown for about {minutes} minute(s). {players} player(s) online.", GREEN)
        elif restarts > state.get("restarts", restarts):
            # A crash that restarted between two checks: report it once, with its crash report.
            status, crash, health, tail = diagnostics()
            post("Holy Lois server crashed and restarted itself", f"{MEME}\nIt is back up with {players} player(s) online.", GOLD,
                 [("Crash report", crash or "No recent crash report."), ("Recent errors", f"```{tail[-900:]}```"), ("Health", health)])
        elif restarted:
            # Planned restarts (updates, the owner's restart button) get a short friendly note.
            post("Holy Lois server restarted", f"{MEME}\nBack up with {players} player(s) online.", GREEN)
        save({"up": True, "failures": 0, "down_since": None, "restarts": restarts, "invocation": run})
        return
    state["restarts"] = restarts
    state["failures"] = state.get("failures", 0) + 1
    if state["up"] and state["failures"] >= 2:
        state.update(up=False, down_since=time.time() - 240, alerted=True)
        report_down(state, "The server stopped answering status checks for about 4 minutes.")
    save(state)


if __name__ == "__main__":
    main()
