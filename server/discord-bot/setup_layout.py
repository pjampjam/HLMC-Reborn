"""One-off, idempotent layout of the Holy Lois Discord (needs only Manage Channels). Run on the server as root.

INFO (read-only): address and website display channels, #welcome, #rules, #announcements, #server-status, #new-members
COMMUNITY: #general, #minecraft-chat, #screenshots, #suggestions, #help
VOICE: General. STAFF stays private.
Old empty categories are removed once their channels have moved. Message content is never deleted.
"""
import json, time, urllib.request, urllib.error

TOKEN = open("/etc/holylois/discord-bot-token").read().strip()
H = {"Authorization": "Bot " + TOKEN, "User-Agent": "DiscordBot (https://holylois.com, 1.0)", "Content-Type": "application/json"}
VIEW, SEND, CONNECT = 1 << 10, 1 << 11, 1 << 20


def api(method, path, body=None):
    for _ in range(5):
        req = urllib.request.Request("https://discord.com/api/v10" + path, method=method, headers=H,
                                     data=json.dumps(body).encode() if body is not None else None)
        try:
            raw = urllib.request.urlopen(req).read()
            return json.loads(raw) if raw else {}
        except urllib.error.HTTPError as error:
            if error.code == 429:
                time.sleep(json.loads(error.read()).get("retry_after", 2) + 0.5); continue
            raise RuntimeError(f"{method} {path}: {error.code} {error.read()[:200]}")
    raise RuntimeError("rate limited")


gid = api("GET", "/users/@me/guilds")[0]["id"]
me = api("GET", "/users/@me")["id"]
everyone = gid


def channels():
    return api("GET", f"/guilds/{gid}/channels")


def find(name, kind=None):
    return next((c for c in channels() if c["name"] == name and (kind is None or c["type"] == kind)), None)


def category(name, private=False):
    c = find(name, 4)
    if c: return c
    overwrites = [{"id": everyone, "type": 0, "allow": "0", "deny": str(VIEW)}, {"id": me, "type": 1, "allow": str(VIEW | SEND), "deny": "0"}] if private else []
    return api("POST", f"/guilds/{gid}/channels", {"name": name, "type": 4, "permission_overwrites": overwrites})


def place(*args, **kwargs):
    # Channels the bot cannot see or permissions it does not hold are reported and left for the owner.
    try: return _place(*args, **kwargs)
    except RuntimeError as error: print("skipped (needs the owner or admin rights):", kwargs.get("name") or (args[0] or {}).get("name"), "-", str(error)[:80])


def _place(channel, parent, position, name=None, topic=None, read_only=False, voice_locked=False, create_type=0):
    if channel is None:
        body = {"name": name, "type": create_type, "parent_id": parent["id"]}
        channel = api("POST", f"/guilds/{gid}/channels", body)
    patch = {"parent_id": parent["id"], "position": position}
    if name and channel["name"] != name: patch["name"] = name
    if topic is not None and channel["type"] == 0: patch["topic"] = topic
    if read_only:
        patch["permission_overwrites"] = [{"id": everyone, "type": 0, "allow": "0", "deny": str(SEND)}, {"id": me, "type": 1, "allow": str(SEND | VIEW), "deny": "0"}]
    if voice_locked:
        patch["permission_overwrites"] = [{"id": everyone, "type": 0, "allow": "0", "deny": str(CONNECT)}]
    result = api("PATCH", f"/channels/{channel['id']}", patch)
    print("placed", result["name"], "->", parent["name"])
    return result


info = category("📌 INFO")
community = category("💬 COMMUNITY")
voice = category("🔊 VOICE")
staff = find("ADMIN CATEGORY", 4) or find("🛠 STAFF", 4)
if staff and staff["name"] != "🛠 STAFF":
    try: api("PATCH", f"/channels/{staff['id']}", {"name": "🛠 STAFF"}); print("renamed staff category")
    except RuntimeError as error: print("staff category is private to the bot; left as is")

place(find("IP: MC.HOLYLOIS.EU", 2) or find("🟢 play.holylois.com", 2), info, 0, name="🟢 play.holylois.com", voice_locked=True, create_type=2)
place(find("www.holylois.eu", 2) or find("🌐 holylois.com", 2), info, 1, name="🌐 holylois.com", voice_locked=True, create_type=2)
place(find("helpful-links") or find("welcome"), info, 2, name="welcome", topic="Start here: what Holy Lois is, how to join and every link")
place(find("rules"), info, 3, topic="Read before playing")
place(find("announcements"), info, 4, name="announcements", topic="Updates and server news")
place(find("server-status"), info, 5, topic="Live status of play.holylois.com")
place(find("👑latest-members") or find("new-members"), info, 6, name="new-members", topic="Who just joined the Discord")

place(find("general"), community, 0, topic="Talk about anything")
place(find("minecraft-chat"), community, 1, topic="Talk with players in game. Messages here appear in Minecraft chat.")
place(find("screenshots"), community, 2, name="screenshots", topic="Builds, views and funny moments (F2 in game)")
place(find("suggestions"), community, 3, name="suggestions", topic="Ideas for the server, mods and events")
place(find("help"), community, 4, name="help", topic="Stuck with the launcher or the game? Ask here")

place(find("General", 2), voice, 0)

for old in ["HOLY LOIS", "Holy Lois Server", "TEXT CHANNELS", "VOICE CHANNELS", "WELCOME"]:
    c = find(old, 4)
    if c and not any(ch.get("parent_id") == c["id"] for ch in channels()):
        api("DELETE", f"/channels/{c['id']}"); print("removed empty category", old)

for name, pos in [("📌 INFO", 0), ("💬 COMMUNITY", 1), ("🔊 VOICE", 2)]:
    c = find(name, 4)
    if c: api("PATCH", f"/channels/{c['id']}", {"position": pos})
print("layout done")
