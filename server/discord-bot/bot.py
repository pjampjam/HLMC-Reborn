"""Holy Lois Discord bot: live server status, a Minecraft <-> Discord chat bridge and a few slash commands.

- #server-status: one message, edited every minute (online, players, address, website, map).
- #minecraft-chat: game chat, joins, leaves, deaths, advancements and discoveries are posted here; messages
  written here appear in game as [Discord] Name: text.
- /status, /players, /ip, /map.

Runs as the holylois-discord-bot service. The token lives only in /etc/holylois/discord-bot-token.
Player IP addresses from the log are never forwarded.
"""
import asyncio, json, os, re, socket, struct, subprocess, time
from pathlib import Path

import discord
from discord import app_commands

TOKEN = Path("/etc/holylois/discord-bot-token").read_text().strip()
STATE = Path("/var/lib/holylois/discord-bot.json")
FIFO = "/run/minecraft-console.fifo"
ADDRESS, WEBSITE, MAP = "play.holylois.com", "https://holylois.com", "https://map.holylois.com"
CATEGORY, STATUS_CHANNEL, CHAT_CHANNEL = "Holy Lois Server", "server-status", "minecraft-chat"
GOLD, GREEN, RED = 0xF4C542, 0x34D27B, 0xC2362F

CHAT = re.compile(r"\]: (?:\[Not Secure\] )?<([A-Za-z0-9_]{3,16})> (.+)$")
LOGIN = re.compile(r"\]: ([A-Za-z0-9_]{3,16})\[/[^\]]+\] logged in with entity id")
SYSTEM = re.compile(r"\]: System chat: (.+)$")
NAME = re.compile(r"^[A-Za-z0-9_]{3,16}$")


def varint(value):
    out = bytearray()
    while True:
        b = value & 127; value >>= 7
        out.append(b | (128 if value else 0))
        if not value: return bytes(out)


def ping():
    """Server list ping on localhost: (online, max, names, version) or None."""
    try:
        with socket.create_connection(("127.0.0.1", 25565), timeout=5) as s:
            host = b"localhost"
            packet = b"\x00" + varint(0) + varint(len(host)) + host + struct.pack(">H", 25565) + b"\x01"
            s.sendall(varint(len(packet)) + packet + b"\x01\x00")
            data, deadline = b"", time.time() + 5
            while time.time() < deadline:
                chunk = s.recv(65536)
                if not chunk: break
                data += chunk
                start = data.find(b"{")
                if start >= 0:
                    try:
                        status = json.loads(data[start:].decode("utf-8"))
                    except ValueError:
                        continue
                    players = status.get("players", {})
                    names = [p.get("name", "") for p in players.get("sample", []) if NAME.match(p.get("name", ""))]
                    return players.get("online", 0), names, status.get("version", {}).get("name", "")
    except OSError:
        return None
    return None


def uptime():
    value = subprocess.run(["systemctl", "show", "minecraft", "-p", "ActiveEnterTimestampMonotonic", "--value"], capture_output=True, text=True).stdout.strip()
    if not value.isdigit() or value == "0": return ""
    seconds = time.clock_gettime(time.CLOCK_MONOTONIC) - int(value) / 1e6
    hours, minutes = int(seconds // 3600), int(seconds % 3600 // 60)
    return f"{hours} h {minutes} min" if hours else f"{minutes} min"


def tellraw(name, text):
    """Shows a Discord message in game. Written without blocking, as JSON, so nothing can inject commands."""
    text = " ".join(text.split())[:240]
    if not text: return
    payload = json.dumps(["", {"text": "[Discord] ", "color": "#5865F2"}, {"text": name + ": ", "color": "gray"}, {"text": text, "color": "white"}], ensure_ascii=False)
    try:
        fd = os.open(FIFO, os.O_WRONLY | os.O_NONBLOCK)
        try: os.write(fd, ("tellraw @a " + payload + "\n").encode("utf-8"))
        finally: os.close(fd)
    except OSError:
        pass


def load_state():
    try: return json.loads(STATE.read_text())
    except (OSError, ValueError): return {}


def save_state(state):
    STATE.parent.mkdir(mode=0o700, parents=True, exist_ok=True)
    STATE.write_text(json.dumps(state))


class HolyLoisBot(discord.Client):
    def __init__(self):
        intents = discord.Intents.default()
        intents.message_content = True
        super().__init__(intents=intents)
        self.tree = app_commands.CommandTree(self)
        self.state = load_state()
        self.status_channel = self.chat_channel = None
        self.online = set()

    async def setup_hook(self):
        @self.tree.command(name="status", description="Is the Holy Lois server online?")
        async def status(interaction: discord.Interaction):
            await interaction.response.send_message(embed=self.status_embed())

        @self.tree.command(name="players", description="Who is playing right now?")
        async def players(interaction: discord.Interaction):
            result = ping()
            text = "The server is offline." if result is None else ("Nobody is online." if not result[0] else f"{result[0]} online: " + ", ".join(result[1]))
            await interaction.response.send_message(text)

        @self.tree.command(name="ip", description="The server address")
        async def ip(interaction: discord.Interaction):
            await interaction.response.send_message(f"Server address: **{ADDRESS}**\nDownload the launcher: {WEBSITE}")

        @self.tree.command(name="map", description="Open the live world map")
        async def world_map(interaction: discord.Interaction):
            await interaction.response.send_message(f"Live map: {MAP}")

    async def on_ready(self):
        if not self.guilds:
            print("Not in a Discord server yet; waiting for the invite.")
            return
        guild = self.guilds[0]
        self.status_channel, self.chat_channel = await self.ensure_channels(guild)
        self.tree.copy_global_to(guild=guild)
        await self.tree.sync(guild=guild)
        print(f"Ready in {guild.name}: #{self.status_channel.name}, #{self.chat_channel.name}")
        if not getattr(self, "_started", False):
            self._started = True
            self.loop.create_task(self.status_loop())
            self.loop.create_task(self.log_loop())

    async def on_guild_join(self, guild):
        await self.on_ready()

    async def ensure_channels(self, guild):
        category = discord.utils.get(guild.categories, name=CATEGORY) or await guild.create_category(CATEGORY)
        status = discord.utils.get(guild.text_channels, name=STATUS_CHANNEL)
        if status is None:
            overwrites = {guild.default_role: discord.PermissionOverwrite(send_messages=False), guild.me: discord.PermissionOverwrite(send_messages=True)}
            status = await guild.create_text_channel(STATUS_CHANNEL, category=category, overwrites=overwrites, topic=f"Live status of {ADDRESS}")
        chat = discord.utils.get(guild.text_channels, name=CHAT_CHANNEL) or await guild.create_text_channel(
            CHAT_CHANNEL, category=category, topic="Talk with players in game. Messages here appear in Minecraft chat.")
        return status, chat

    def status_embed(self):
        result = ping()
        if result is None:
            embed = discord.Embed(title="Holy Lois: Reborn is offline", description="It may be restarting or updating. Check back in a few minutes.", color=RED)
        else:
            count, names, version = result
            embed = discord.Embed(title="Holy Lois: Reborn is online", color=GREEN)
            embed.add_field(name="Players", value=(", ".join(names) if names else "Nobody right now") + f" ({count})", inline=False)
            embed.add_field(name="Version", value=version or "Minecraft 26.3", inline=True)
            up = uptime()
            if up: embed.add_field(name="Up for", value=up, inline=True)
        embed.add_field(name="Address", value=f"`{ADDRESS}`", inline=False)
        embed.add_field(name="Links", value=f"[Website and launcher]({WEBSITE}) - [Live map]({MAP})", inline=False)
        embed.set_footer(text="Updated every minute")
        embed.timestamp = discord.utils.utcnow()
        return embed

    async def status_loop(self):
        while not self.is_closed():
            try:
                embed = await asyncio.to_thread(self.status_embed)
                message = None
                if self.state.get("status_message"):
                    try: message = await self.status_channel.fetch_message(self.state["status_message"])
                    except discord.NotFound: message = None
                if message: await message.edit(embed=embed)
                else:
                    message = await self.status_channel.send(embed=embed)
                    self.state["status_message"] = message.id; save_state(self.state)
                result = ping()
                activity = discord.Game(f"{result[0]} on {ADDRESS}" if result else "server offline")
                await self.change_presence(activity=activity)
            except Exception as error:
                print("Status update failed:", error)
            await asyncio.sleep(60)

    async def log_loop(self):
        while not self.is_closed():
            process = await asyncio.create_subprocess_exec("journalctl", "-u", "minecraft", "-f", "-n", "0", "-o", "cat",
                                                           stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.DEVNULL)
            async for raw in process.stdout:
                line = raw.decode("utf-8", "replace").rstrip()
                try: await self.forward(line)
                except Exception as error: print("Forward failed:", error)
            await asyncio.sleep(5)

    async def forward(self, line):
        if self.chat_channel is None: return
        safe = discord.utils.escape_mentions
        if match := CHAT.search(line):
            name, text = match.groups()
            if text.startswith("/") or text.startswith("./"): return
            await self.chat_channel.send(f"**{name}**: {safe(discord.utils.escape_markdown(text))}"[:1900])
        elif match := LOGIN.search(line):
            self.online.add(match.group(1))
            await self.chat_channel.send(f"➕ **{match.group(1)}** joined the server")
        elif match := SYSTEM.search(line):
            text = match.group(1).lstrip("✦ ").strip()
            first = text.split(" ", 1)[0]
            if text.startswith("[") or not NAME.match(first): return
            if text.endswith("left the game"):
                self.online.discard(first)
                await self.chat_channel.send(f"➖ **{first}** left the server")
            elif "has made the advancement" in text or "has completed the challenge" in text or "has reached the goal" in text:
                await self.chat_channel.send(f"🏆 {safe(text)}")
            elif " discovered " in text or "Holy Lootbox" in text:
                await self.chat_channel.send(f"✦ {safe(text)}")
            elif first in self.online:
                await self.chat_channel.send(f"☠ {safe(text)}")

    async def on_message(self, message):
        if message.author.bot or self.chat_channel is None or message.channel.id != self.chat_channel.id: return
        text = message.clean_content
        if message.attachments: text = (text + " [attachment]").strip()
        await asyncio.to_thread(tellraw, message.author.display_name[:24], text)


if __name__ == "__main__":
    HolyLoisBot().run(TOKEN)
