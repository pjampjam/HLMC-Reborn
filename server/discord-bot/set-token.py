"""Owner helper: sudo python3 set-token.py. Asks for the new Discord bot token (hidden), strips terminal paste markers and
other junk, accepts exactly one token-shaped string, writes /etc/holylois/discord-bot-token (root, 600) and restarts the bot.
The token is never printed. Anything else (empty, two tokens) changes nothing.
"""
import getpass, os, re, subprocess, time
from pathlib import Path

TOKEN = Path('/etc/holylois/discord-bot-token')
pasted = getpass.getpass('Paste the new bot token (Ctrl+V; nothing shows), then press Enter: ')
found = sorted(set(re.findall(r'[A-Za-z0-9_-]{20,}\.[A-Za-z0-9_-]{5,}\.[A-Za-z0-9_-]{20,}', pasted)))
if len(found) != 1:
    print(f'Expected exactly one token, found {len(found)}. Nothing changed; copy just the token and try again.')
    raise SystemExit(1)
TOKEN.write_text(found[0]); os.chmod(TOKEN, 0o600)
subprocess.run(['systemctl', 'restart', 'holylois-discord-bot'], check=True)
time.sleep(10)
state = subprocess.run(['systemctl', 'is-active', 'holylois-discord-bot'], capture_output=True, text=True).stdout.strip()
print('Token saved (' + str(len(found[0])) + ' characters). Bot is ' + state + '.')
print('If it is not "active", the token was rejected by Discord: reset it again in the developer portal.')
