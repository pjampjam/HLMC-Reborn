# Holy Lois: Reborn - easy owner guide

Your CurseForge profile is where you edit and test. The Holy Lois Admin app publishes your tested changes. Friends use the normal Holy Lois app to install them.

Launcher 0.4.0 updates itself and its small startup checker before opening. Players do not rerun the installer for each launcher release. First setup offers a launcher choice and optional Desktop and Start menu shortcuts. Deleted shortcuts stay deleted, and existing players keep their setup. Your Admin shortcuts are separate and are not recreated by the player updater.

## Add a mod, resource pack or shader

1. Close Minecraft.
2. Open your **Holy Lois: Reborn** CurseForge profile and choose **Open Folder**.
3. Put the download in the right folder:

| Download | Folder | Server too? |
| --- | --- | --- |
| Client mod JAR | `mods` | No |
| Gameplay mod JAR | `mods` | If its download page says required on the server |
| Resource pack ZIP | `resourcepacks` | Usually no |
| Shader ZIP | `shaderpacks` | No |

Choose the exact **Minecraft 26.3 Fabric** file and add its required dependencies. Keep only one release of each mod. Do not unzip JARs or pack ZIPs. Do not use Paper plugins.

4. Launch the profile. Enable the resource packs you want players to use. Test the new feature, joining the server, resource reloads and shaders if relevant.
5. Close Minecraft and its launcher.

The app checks mod dependencies and official download metadata before preparing a release. It can stop if a download is incompatible, an unreviewed alpha, or has no verified source. Fix the reported file rather than bypassing the check.

## Send the update to friends

Open **Holy Lois Admin** on your Desktop or Start menu. Friends get **Holy Lois Reborn** in both places when they install.

1. **Choose folder**: select your tested CurseForge profile folder, the one containing `mods`, `config` and `options.txt`.
2. Enter a new version such as **1.5.3** and a short description of your changes.
3. Review **Shared settings**. Existing reviewed files start checked. New config files start unchecked so you can choose what players should receive. Never select account, voice-device or personal map files.
4. Tick the box confirming that you tested the profile and closed Minecraft.
5. Click **Prepare update**. The app checks files, captures the selected settings and creates a signed release.
6. If a mod needs the server, update the server before the next step.
7. Click **Publish to friends**.

The first publish needs **Connect GitHub once**. Complete GitHub's sign-in and permission review yourself in its browser/window. Holy Lois never asks you to enter a GitHub password or token. The owner tool uses the official GitHub CLI already included in your local toolchain.

After publishing, friends see an update on the next check, normally within two minutes while Holy Lois is open. They close their game/launcher, then click **Update Holy Lois**. They do not need a new EXE for each mod change.

A new release applies changed shared settings as part of installation, before the next game launch. JSON/options/properties merge changed published values. Unrelated personal values remain. Changed TOML/JSON5/other shared files are replaced as complete reviewed files. Changed keybinds in `options.txt`, voice devices, accounts, worlds and caches stay personal. The previous settings are retained in the update recovery backup. Repairing the same version does not repeatedly reset settings.

Starting graphics stay at render distance 12, DH distance 64, shaders off. Resource-pack activation follows the shared Minecraft options. Adding a shader does not turn shaders on.

If you make a mistake, prepare a **higher** version containing the last good content. For example, fix 1.5.3 by publishing 1.5.4. Never edit an already released version or lower its number.

## Update the server

All paths below are examples. Keep your real SSH host, username and key location private. Configure `HOLYLOIS_SSH_HOST` and `HOLYLOIS_SSH_USER` locally, or pass `-HostName`, `-User`, `-Key` and `-Stage` to Server-Admin.ps1.

The server is separate from the client release. Your survival world is kept.

1. Close Minecraft. Put only the new **server-compatible JARs**, plus dependencies, in:

```text
%USERPROFILE%\Downloads\server-mods
```

Keep one version of each mod in that staging folder. Client-only animations, shaders and interface mods stay off the server.

2. In **Holy Lois Admin**, click **Server start / stop / update**.
3. Choose **Check staged mods**. Read the replacement plan.
4. Choose **Back up and install staged mods**.
5. Wait for the tool to report successful startup and **Done**. Test joining before publishing the client update.

The tool stops Minecraft, makes and verifies a complete maintenance backup, replaces the staged mod IDs, starts the service and checks startup. A failed startup restores the previous JARs and retains the backup. It does not wipe your world. Some mods can change data before failing; full restoration is a separate stopped-server operation.

## Start, stop or check the server

Use **Server start / stop / update** in Holy Lois Admin. Choose **Status**, **Start**, **Stop**, **Restart** or **Logs**.

If you prefer a fresh Windows PowerShell window, connect with:

```powershell
ssh -i "$env:USERPROFILE\.ssh\id_ed25519" SSH_USER@SERVER_HOST
```

Once connected, run the command you need in the **Ubuntu shell**:

```bash
sudo systemctl status minecraft --no-pager -l
sudo systemctl start minecraft
sudo systemctl stop minecraft
sudo systemctl restart minecraft
sudo journalctl -u minecraft -n 100 --no-pager
df -h /
exit
```

Closing SSH does not stop the server. `/rtp`, `/tpa NAME` and other player commands belong in **Minecraft chat**.

## If a friend's SK pack was deleted

Close Minecraft and SKlauncher, then reopen Holy Lois so it updates to launcher 1.0.3 or newer.

1. Choose **SKlauncher** and click **Install Holy Lois** or **Repair / check files**.
2. Click **Play** in Holy Lois. Open **Library > Holy Lois: Reborn** in SKlauncher.
3. If SKlauncher shows **Install**, click it once to prepare Minecraft and Java, then **Play**.

The updater installs directly into SKlauncher's own instance folder and restores a deleted Library entry automatically. Manual import and folder linking are no longer needed. Personal files and unrelated instances are preserved.

## Official Minecraft Launcher

Microsoft Store and desktop installs are detected. Store users do not need to search for an EXE. Click **Open Minecraft Launcher**, then choose **Installations > Holy Lois: Reborn > Play**. Sign in inside Minecraft Launcher.

For an unusual desktop install, **Find launcher** accepts its EXE or a Windows shortcut. The profile and HQ icon are prepared separately from other Minecraft installations.

## Backups and space

Backups live on Google Drive (`Holy Lois Backups`), not on the VM disk (owner decision, 2026-10-04). Since release 1.7.4:

- **World (JEB)**: differential every 30 minutes, full every 3 hours, at most one full and two differentials locally within 6 GB. The off-site job uploads the newest of each.
- **Release backups**: each deploy still makes a complete stopped-server backup under `/opt/minecraft-backups/maintenance/` first (rollback needs it locally). The off-site job uploads it, checks every file's size and MD5 against Drive and only then deletes the local copy. Release folders without `receipt.json` (deploy not finished) wait.
- **One-time move**: `server/ops/move-backups-to-drive.py` moved the older maintenance folders, legacy archives and old JEB files to `maintenance/`, `legacy/` and `world/` on Drive, each verified before deletion. `/opt/minecraft-backups/terrain-expansion` is the terrain job's state, not a backup, and stays.
- **Restore**: `sudo rclone copy "gdrive:Holy Lois Backups/maintenance/NAME" /opt/restore/NAME`, then restore with the server stopped. The archives include private server data, so never send them to friends.

Check `df -h /` now and then; the world and BlueMap tiles are what grows.

## Server release for pack 1.7.4

`server/deploy-release-174.py` (run as root from `~/hl-174`) replaces Flan with Open Parties and Claims 0.31.6 and installs onboarding 1.7.0 and Holy Lois Extras 1.2.0. Same safety as earlier releases: 0 players or a one-minute countdown, complete verified backup, rollback if startup fails. Afterwards it sets the world border, updates the Discord bot and the off-site backup job.

- **Claims (OPAC)**: `config/openpartiesandclaims-server.toml` (copy in `server/opac/`). Permissions through LuckPerms, 16 free chunks, 2 force-loaded chunks, OPAC's own welcome messages off because Holy Lois Extras draws the zone titles. Players claim on the map (M, right-click) or with `/oclaims`; teams with `/oparties`. Admins: `/opac` and `/oclaims` server claims.
- **Extra chunks**: `config/holylois-claims.json`. One earned chunk per 2 hours played (up to 48), bought chunks cost 500 coins for the first and 15% more each (up to 64), selling refunds half. Purchases are stored in `world/holylois/claims.json`; the add-on sets OPAC's bonus claim count to earned + bought every five minutes and at login.
- **/rtp**: handled by the add-on now (Essential Commands' rtp is off). Overworld only, 5-minute cooldown, 3 seconds standing still, and never within one chunk of a claim. First-join and bed-less respawn spots use the same rule.
- **Combat tag**: a PvP hit tags both players for 20 s, a mob hit only delays teleports for 5 s. Logging out while PvP-tagged kills the player and drops the loot. Teleport commands (rtp, home, tpa, spawn, back, warp) are refused while tagged.
- **Deaths**: normal deaths keep the drops for 30 minutes, owner-only for the first 5. PvP deaths get no coordinates, no pickup lock and no minimap death point.
- **/support and /report**: logged as `HOLYLOIS-SUPPORT {json}`; the Discord bot posts them to #support under STAFF with an owner ping and two buttons ("On my way", "Solved") that message the player in game. Five-minute cooldown each.
- **/donate**: the wallet list moved here from the old `/support`; addresses are in `DonateCommand.java`.
- **World border**: 14,000 blocks wide (7,000 from spawn), warning at 64 blocks. Raise it later with `worldborder set`; never lower it below land people live on.

## Server release for pack 1.7.0

`server/deploy-release-170.py` (run as root from `~/hl-170`) adds Macaw's Holidays and onboarding 1.5.0, installs the cleaner Tab style, removes the old tagline from the server list, raises `view-distance` to 12, updates the Discord monitor and enables the weekly recap. It refuses while players are online, backs up the complete server first and rolls back if the server does not start. Afterwards it posts the update notes to Discord.

- **Leaderboards** come from the vanilla stats files, refreshed every two minutes off the main thread.
- **Discoveries** are stored in `world/holylois/discoveries.json`. Delete an entry there to let a structure be announced again.
- **Weekly recap**: `holylois-weekly-recap.timer` posts on Sundays at 19:00 Riga time. A week with no play posts nothing.
- **Restart call**: every restart, planned or not, is announced once in Discord with "Maaarek nahhul!".
- **Daily gifts and events**: `world/holylois/daily.json` (streaks) and `world/holylois/events.json` (holiday gifts, day counter). Time and weather pause while the server is empty, so the day counter follows real play.
- **Economy**: EconomyCraft with the admin shop and sidebar scoreboard off (`config/economycraft/config.json`). Item prices are in `prices.json`.
- **Boombox stations**: `config/holylois-boombox.json`, then `/boombox reload`. Plain MP3 streams only; at most 6 play at once (held and placed together). Placed boomboxes that are switched on are listed in `world/holylois/boomboxes.json`.
- **Server list line**: `line2` in `config/MiniMOTD/main.conf` always announces the newest exciting change; update it with every release.
- **/donate** (named `/support` before 1.7.4): the wallet addresses and the hover help per network live in `DonateCommand.java` (onboarding add-on); keep holylois.com/donate in sync. Donations never buy anything in game (Minecraft server rules).
- **Restart countdown**: release scripts show a one-minute boss bar when players are online. Custom boss bars are saved in the world, so the scripts remove `holylois:restart` before stopping; if one is ever stuck, run `bossbar remove holylois:restart`.
- **Public stats**: `server/stats/make-stats.py` (installed in `/usr/local/lib/holylois/`). Names matching the slur filter are masked as first letter plus stars; names listed in `/etc/holylois/stats-hidden.txt` are left out entirely. `server.online` is a live count at generation time.
- **Removing old profiles**: release 1.7.3 moved test and duplicate accounts into `removed-profiles/` inside its backup folder (player data, stats, advancements, claims, homes), dropped them from `usercache.json` and onboarding, and removed their logins with `auth remove NAME`. Move the files back to restore one.
- **No em dashes for players**: SkinsRestorer translations that used them have dash-free copies in `config/skinsrestorer/locales/custom/` (they take priority over `repository/`). Delete a copy to get upstream text back.
- **BlueMap**: renders only while nobody is online and serves on 127.0.0.1:8100. It becomes public once the domain tunnel points `map.` at it.
- **Live map branding**: `bluemap/web/index.html` title and `assets/favicon-*.png` were replaced with the Holy Lois crown. A BlueMap update can restore its defaults; re-apply if the tab says BlueMap again.
- **Discord**: the bot (`holylois-discord-bot`) keeps #server-status, #minecraft-chat and #rules in sync; #rules comes from `/opt/holylois-bot/RULES.md` (copy of RULES.md), refreshed on bot restart.
- **Vein mining**: shapeless only; the add-on forces it on the server and Holy Lois Extras removes shape switching on clients.

## Server release for pack 1.6.1

`server/deploy-release-161.py` installed Farmer's Delight and Macaw's Furniture (required on both sides), and the server-only Styled Player List, RightClickHarvest with Jamlib, Krypton, Alternate Current, Dungeons and Taverns, Towns and Towers with Cristel Lib, AudioPlayer and onboarding 1.4.0. It refuses while players are online, makes a complete verified backup under `/opt/minecraft-backups/maintenance/release161-*` and restores the previous files if startup fails.

- **Player list:** `server/styledplayerlist/` holds the Tab header and footer (`config/styledplayerlist` on the server). Edit `styles/holylois.json` and run `/styledplayerlist reload` as an operator.
- **Quote of the day:** edit `/opt/minecraft/config/holylois-quotes.txt` (`quote | author`, one per line). Changes apply without a restart. The welcome message and `%holylois:quote%` share it.
- **Java:** `/etc/systemd/system/minecraft.service.d/jvm.conf` sets a fixed 6 GB heap with Aikar's G1 flags. If the VM is resized to 4 OCPU / 24 GB (the Oracle Always Free limit), raise both -Xms and -Xmx to 10G and run `sudo systemctl daemon-reload && sudo systemctl restart minecraft` while nobody is online.
- **Backups:** the JEB budget is 12 GB so two full backups of the larger world still fit. Watch `df -h /`.
- **Structures:** Dungeons and Taverns and Towns and Towers appear only in newly generated land. `world/datapacks/holylois-structure-tuning` spaces their extra villages to 68 chunks so villages are about 1.5x vanilla, not 2x. Their 223 chest loot tables are linked to Runeforged tiers in `config/runeforged-monsters.json` (vaults and bosses T1, dungeons T2, houses and camps T3).
- **Sleep:** `players_sleeping_percentage` is 1, so one sleeping player skips the night.
- **Terrain:** `holylois-terrain-expansion.timer` runs while the server is empty. It pregenerates a 4,000-block square while the server is empty, then raises RTP to 3,500. See `server/terrain/README.md`.

## Monitoring, bots and off-site backups

- **Discord alerts:** create a webhook in Discord (channel settings > Integrations > Webhooks > New Webhook > Copy Webhook URL), then on the server run `sudo nano /etc/holylois/discord-webhook`, paste it, save, and run `sudo chmod 600 /etc/holylois/discord-webhook && sudo python3 /usr/local/lib/holylois/discord-alert.py test`. The monitor checks every 2 minutes, reports crashes with the crash report and log tail, and says when the server is back. Planned deploys create `/run/holylois-maintenance` to stay quiet.
- **Bot wall:** `holylois-botwall.timer` counts the usernames SSH bots try (no IPs) for the Tab list and the operator command `/botwall`. fail2ban bans repeat knockers for an hour, longer for repeat offenders. SSH stays key-only.
- **Own Google client (since 2026-10-04):** rclone's built-in client is shared by all rclone users and gets rate limited (1 GB took 25 minutes). The remote now uses the owner's own OAuth client: Google Cloud project "Holy Lois Backups", Drive API enabled, Google Auth Platform External and **In production** (Testing logins expire after 7 days), no logo (a logo forces verification), home page holylois.com, privacy holylois.com/privacy, client type Desktop app. The owner typed the client ID and secret into `sudo rclone config` (edit `gdrive`) and signed in with `rclone authorize` on the PC; about 39 MB/s since. With scope drive.file a client sees only its own files, so backups made with the old client stay in the older "Holy Lois Backups" folder in Drive and new ones go into a fresh folder of the same name.
- **Google Drive:** run `sudo rclone config` once: `n` (new remote), name `gdrive`, storage `drive`, leave client id/secret empty, scope `3` (drive.file: rclone sees only its own files), no advanced config, and answer `n` to auto config. It prints a `rclone authorize "drive" ...` command: run that on your PC (install rclone with `winget install Rclone.Rclone`), sign in to Google in the browser, and paste the result back. Then `sudo systemctl start holylois-offsite-backup` uploads the first copy. Every 3 hours it uploads new world backups, changed server settings and finished release backups into `Holy Lois Backups` (release backups are then removed from the VM), and above 500 GB deletes the oldest while always keeping the newest 30 of each kind.

## Current pack and tests

Pack 1.5.2 has 50 client mods, four resource packs and seven optional shaders. The server has 29 mods. All 14 shared mods match by hash. Required dependency metadata, including bundled Fabric libraries, was checked on both sides.

The shader helper addresses the supplied Iris enchanted-glint crash. The owner tested shaders successfully afterward. Brief coarse DH terrain and terrain-download retries are separate issues, not certified fully fixed.

The normal launcher defaults to English, with Russian and Latvian selectable. GitHub notes and owner documentation remain English. The native installer remains under 1 MB and does not need a separate .NET install. Windows Authenticode signing is still absent, so SmartScreen warnings remain possible.

Keep your SSH key and `private/release-private.pem` private. Friends receive only the public installer and signed downloads. More implementation detail is in [TECHNICAL-GUIDE.md](TECHNICAL-GUIDE.md).

## Login, arrival and inventory defaults

The owner confirmed pack 1.5.2 joins through the existing Minecraft Launcher and SKlauncher. The original 0.4.0 downloads were withdrawn again after browser detection recurred. Microsoft diagnostic follow-up is required; see SECURITY-NOTICE.md. The owner confirmed offline registration/RTP and premium joins; 1.5.2 is the stable pack.

The centered form uses the existing EasyAuth account database and does not store a password on the client. Premium verification and the 24-hour same-IP session stay enabled. Before authentication, EasyAuth blocks movement, combat, inventory actions and damage. Escape in the form offers Back and Disconnect.

First registration uses safe RTP inside the pregenerated Overworld, followed by a 1.5-second black arrival screen. Returning players keep their position. A death respawn uses RTP only when vanilla finds no usable bed or anchor; leaving the End alive does not count as death. Brief arrival damage protection is temporary.

Inventory Profiles Next sorting remains available. Slot locking is opt-in; failed-replacement and low-durability visual/sound alerts are off. Friends on older settings can open R + C to disable those options immediately.

The old chained backup schedule reached its size cap and stopped making new backups. It was replaced by the schedule above, and a full plus differential backup was restored and hash-checked separately. Rebuildable Distant Horizons SQLite caches are excluded from scheduled world backups; terrain and player data are included. Complete stopped-server maintenance backups still protect authentication, permissions, claims and configs outside the world. Other files can still fill storage, so verify completed backups and disk usage periodically.

Use [TEST-GUIDE.md](TEST-GUIDE.md) for the premium, offline, respawn, voice and non-operator checks. No additional server mods are required for this release. Test the existing features before adding more systems.
