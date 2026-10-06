# Holy Lois: Reborn - easy owner guide

Your CurseForge profile is where you edit and test. The Holy Lois Admin app publishes your tested changes. Friends use the normal Holy Lois app to install them.

Launcher 0.4.0 updates itself and its small startup checker before opening. Players do not rerun the installer for each launcher release. First setup offers a launcher choice and optional Desktop and Start menu shortcuts. Deleted shortcuts stay deleted, and existing players keep their setup. Your Admin shortcuts are separate and are not recreated by the player updater.

## Add a mod, resource pack or shader

**Mods also need the mod check.** The server only lets in the mod ids listed in `config/holylois-mods.json` (see **Mod check** below). A new mod has to be added there (`work/make-mod-allowlist.py`, or its fabric.mod.json ids including nested jars) before the pack that ships it goes live, or everyone who updates is turned away.

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

## Server release for pack 1.8.1

`config/holylois-quiet.json` includes pjampjam and pjamtest. The existing hot-reload suppresses join/leave, AFK, advancement and discovery broadcasts. Discord also omits their automatic death notices and status-list entries. Typed chat still forwards; in-game death messages retain the previous policy. Existing additional quiet names are preserved. The follow-up config was tested in the isolated copy and against synthetic Discord events, then applied with exact restore bytes from the verified 1.8.1 backup; no further restart.

`server/deploy-release-181.py` installs Extras 1.6.1 and onboarding 1.8.1, statistics exports/visibility defaults, pack minimum 1.8.1 and the MOTD. Auth UI 1.0.4 is client-only. The loopback regression probe covers relic recovery/restart, crate rewards, combat teleports, protected mob damage/push and radio controls/caps. Deployment takes a full verified backup and restores changed files automatically if startup fails. Keep launcher/app-stable 1.3.1 unchanged and move pack-stable immediately after a healthy server start.

Owner/test exclusions merge with `/etc/holylois/stats-hidden.txt` and `config/holylois-stats-hidden.json`; they remove public rankings, totals, discoveries and head exports without deleting game progress. SkinsRestorer remains the skin store. The bridge exports only vetted Mojang texture URLs to `world/holylois/skin-textures.json`, with no authentication data. Personal privacy commands, nickname migration and password recovery grants are not implemented in this patch.

## Server release for pack 1.8.0

`server/deploy-release-180.py` (run as root from `~/hl-180`; `--check` only runs the pre-checks) installs Fish of Thieves, Fishing Loot Crates and any required library the server does not run yet (jars and SHA-512 from `new-mods.json`, made by `make-pack-180.py` from Modrinth), Holy Lois Extras 1.6.0, `config/holylois-legends.json`, `config/holylois-fish.json`, the advancements (legends and fishing), the new mod ids in `config/holylois-mods.json`, pack minimum 1.8.0 and the MOTD. Same safety as earlier releases: 0 players or a one-minute countdown, complete verified backup, rollback if startup fails. Test first with `server/stage-and-test-180.py` (loopback copy on port 25566 that checks its own log and stops).

- **Legends** (`server/legends/holylois-legends.json`): each legend has an id, a name, a chat colour and items. An item has an id, a base item (`treasure_map` for a real buried treasure map), a name, lore lines, `where` (`chests`, `fishing` or `both`), a weight, optional enchantments and an optional `light`. `chestChance` (1.2%) is per structure chest (`chestTables`, `*:chests/*`), `crateChance` (5%) per fished loot crate (`crateTables`), `treasureChance` (30%) per vanilla fishing treasure catch, which then becomes a bottle, a map or a fishing legend item by `treasure` weights. Edit the file and run `/legends reload`; run `python server/advancements/make-advancements.py` too when items or legends change, because the achievements are made from the same file.
- **Fish weights** (`server/legends/holylois-fish.json`): lightest and heaviest kg per species; other edible items in `#minecraft:fishes` or the `fishofthieves` namespace use `fallback`. `curve` 2.5 gives about 76% Common, 13% Uncommon, 7% Rare, 3% Epic and 1% Legendary.
- **Commands** (operators): `/legends list`, `/legends reload`, `/legends give <item id | bottle | map | fish>`.
- **Mod check**: Fabric Loader's own built-ins (java, minecraft, fabricloader, mixinextras) are always allowed now, so the hotfix `allow-loader-mods.py` is no longer needed for new lists.
- Held legend items with `light` glow through LambDynamicLights (`assets/holylois/dynamiclights/item/legend_light.json` in the Extras jar); this is an owner check in game.

## Server release for pack 1.7.11

`server/deploy-release-1711.py` (run as root from `~/hl-1711`; `--check` only runs the pre-checks). Pack 1.7.11 removes Quick Play: Holy Lois Extras 1.5.1 drops `QuickPlayClient`, launcher 1.2.7 drops the setting and deletes a leftover `holylois-quickplay.json` on Play. The server keeps extras 1.5.0 (the removed part was client-only, so the server behaves the same) and does not restart. The step replaces the MOTD headline that still promised Quick Play, runs `minimotd reload`, puts the old `main.conf` back if the reload fails, and posts the Discord note. Next server release installs extras 1.5.1 or newer with its other changes.

## Server release for pack 1.7.10

`server/deploy-release-1710.py` (run as root from `~/hl-1710`; `--check` only runs the pre-checks) installs onboarding 1.8.0, Holy Lois Extras 1.5.0, `config/holylois-daily.secret`, the datapack with its logo, the new server icon, `max-tick-time=120000`, the AFK-free Tab playtime, the pack-only rule in `rules.txt`, MOTD, then (after the server is up) the Discord bot, `make-stats.py`, `weekly-recap.py` and the lag-guard terrain job, and resumes the terrain job from its Chunky checkpoint. Same safety as earlier releases: 0 players or a one-minute countdown, complete verified backup, rollback if startup fails.

- **Quiet names**: `config/holylois-quiet.json` is `{"names": ["pjampjam"]}`, re-read when the file changes. Join, leave, AFK, advancement and discovery broadcasts about these names are not sent; death messages still are. The Discord bot reads the same file (hidden from the Players field, status and the join/leave lines; deaths never reach Discord for them).
- **AFK ledger**: `world/holylois/afk.json` adds one second per AFK second (Essential Commands decides, `auto_afk_time` is 15 minutes, `/afk` too). Playtime for achievements, claims, leaderboards, stats, recap and Tab is vanilla `play_time` minus the ledger, counted from this release on. If Essential Commands is missing the ledger waits and nothing is subtracted.
- **Secret code**: `/redeem CODE`. The code is HMAC-SHA256 of the UTC date with `config/holylois-daily.secret`, the same as the website (`docs/DAILY-CODE.md` in the website repo; Worker secrets `CODE_SECRET` and `DAILY_CODE=on`). Yesterday's code works until 01:00 UTC. One redeem per UUID per UTC day (`world/holylois/redeem.json`), 5 wrong tries per hour, prize rolled from player and date (coins 50%, lootbox 25%, diamonds 13%, rune find 11.5%, legendary 0.5%). The secret lives in `private/holylois-daily.secret`; never put it in a repository or chat. Rotating it changes every code from that moment.
- **Terrain job**: slices of 15 minutes with 10 minute rests, 20 minutes when the log shows 100 or more ticks behind (`server/terrain/README.md`). Test with `server/terrain/test-expand-terrain.py` (23 tests).
- **Launcher 1.2.6**: Play mode in Settings (Quick Play, removed again in 1.2.7). Update asks before closing Minecraft and its launcher.
- **Launcher 1.3.0 (fast start)**: player-name accounts ("name", and SKlauncher players unless they switch back) start Minecraft from the app. Java and Minecraft live in `%LOCALAPPDATA%\HolyLoisReborn\data\game` (files shared with other launchers are hard-linked), game output and the last start record in `data\logs`, names in `data\players.json` (kept on uninstall unless the player ticks "forget"). The game gets Minecraft's own `--quickPlayMultiplayer play.holylois.com` when Join Holy Lois on start is on; bought accounts get the same option in the Minecraft Launcher profile. Offline UUIDs are the standard `OfflinePlayer:NAME` ones, the same the server computes, so SKlauncher players keep their progress. Names that belong to a premium account are refused in the app (EasyAuth premium verification would ask for that account). A launcher-side name limit is only a courtesy: bots do not use the launcher, so real protection stays on the server (EasyAuth, the mod check).

## Server release for pack 1.7.8

`server/deploy-release-178.py` (run as root from `~/hl-178`) installs Holy Lois Extras 1.4.0, `config/holylois-mods.json`, the advancement texts and `server-icon.png`. Same safety as earlier releases: 0 players or a one-minute countdown, complete verified backup, rollback if startup fails (the mod list is removed again on rollback). The pack minimum stays 1.7.5.

- **Mod check**: `config/holylois-mods.json` is `{"mode": "enforce" | "warn" | "off", "missing": "warn" | "kick", "legacy": "allow" | "block", "exempt": ["name"], "allowed": ["modid"]}`. It is read on every join, so changes need no restart. In `enforce`, a client with a mod id that is not allowed is kicked with an EN/RU/LV message naming the mods. Missing pack mods are only logged unless `missing` is `kick`. Clients too old to answer (extras before 1.4.0) get in while `legacy` is `allow`. `exempt` names skip the check (the owner). The list holds every id of the pack including libraries nested in jars. If friends are locked out by mistake: set `"mode": "off"` and tell the owner. It stops accidents and casual extras, not a cheat client that fakes its list.
- **Loader mods in the mod check**: every client also reports what Fabric Loader itself provides (`fabricloader`, `java`, `minecraft`, `mixinextras`). The list made from the pack's jars lacked `mixinextras`, so every non-exempt player was turned away until `server/allow-loader-mods.py` (run as root, `--check` first; no restart) added them. Keep these four in the list whenever it is regenerated.
- **Launcher 1.2.4**: Play moves foreign jars from `mods/` to `state/quarantine/<time>` (never deletes), repairs changed pack mods and re-enables the pack resource packs.
- **Window icon**: crown icons drawn pixel-perfect for 16 to 64 px (`work/make-brand.py`). **Server icon**: new 64 px crown.

## Server release for pack 1.7.6

`server/deploy-release-176.py` (run as root from `~/hl-176`) installs onboarding 1.7.2 and Holy Lois Extras 1.3.1. Same safety as earlier releases: 0 players or a one-minute countdown, complete verified backup, rollback if startup fails. The pack minimum stays 1.7.5 because nothing new is registered.

- **Discoveries**: all Epic Dungeons (`epic:*`, 9 dungeons and 3 obelisks) and the small undead and creeping crypts are announced. Other `small_` structures stay quiet. A large plains dungeon is `epic:large_dungeon`.
- **Achievements**: datapack `holylois-advancements` gained Dungeon Delver, Deeper Still, Dungeon Master (hidden, all 9 dungeons) and Odd Pillar (`server/advancements/make-advancements.py`).
- **Runeforged**: `server/structures/runeforged-epic-additions.json` adds the 17 `epic:chests/*` tables to `config/runeforged-monsters.json` (treasure tier 1, magic, scary, mineral, library, potions and the weapon tables tier 2, the rest tier 3). Epic dungeons are jigsaw structures that pick random rooms, so a dungeon may have no treasure room at all.
- **Boombox range**: `range(volume)` runs from 16 blocks (volume 1) to 48 (volume 10); `distance` in the config is no longer used.
- **Server list line** shortened to fit.

## Server release for pack 1.7.5

`server/deploy-release-175.py` (run as root from `~/hl-175`) installs onboarding 1.7.1 and Holy Lois Extras 1.3.0. Same safety as earlier releases: 0 players or a one-minute countdown, complete verified backup, rollback if startup fails.

- **Pack check**: `config/holylois-pack.json` holds `{"minimum": "1.7.5"}`. Joining clients send their pack version during login; an older pack gets a friendly EN/RU/LV "update in the Holy Lois launcher" message instead of registry errors. No file means no check. Raise `minimum` with every release that both sides need.
- **World border**: 20,000 blocks wide (10,000 from 0,0). `server/bluemap/set-render-bounds.py BORDER` keeps BlueMap inside it (the Nether gets 1/8). The old radius-4,000 terrain task and job state were moved into the release backup.
- **Terrain**: `expand-terrain.py` with `BORDER = 20000` pregenerates all 1,565,001 chunks inside the border while nobody is online (about 12 hours of empty server) and raises `/rtp` to 5,000 only after every chunk is proven `Status=full`.
- **Homes**: `/home` with several homes uses the one named `home` in any capitals; names that differ only in capitals are refused; `/Home` is an alias.
- **Portals**: a player who walks back into the portal they arrived at (within 16 blocks) returns to the portal they left from, if it still exists. In memory only, so a restart forgets it.
- **Recipes**: datapack `world/datapacks/holylois-recipes` removes the recovery compass recipe (copy in `server/datapacks/`).
- **Boombox stations**: the six new stations were appended to the live `config/holylois-boombox.json` (13 in total, the boombox cycles through at most 16).
- **Tab list**: `%holylois:slots%` shows online + 1, like the server list.

## Server release for pack 1.7.4

`server/deploy-release-174.py` (run as root from `~/hl-174`) replaces Flan with Open Parties and Claims 0.31.6 and installs onboarding 1.7.0 and Holy Lois Extras 1.2.0. Same safety as earlier releases: 0 players or a one-minute countdown, complete verified backup, rollback if startup fails. Afterwards it sets the world border, updates the Discord bot and the off-site backup job.

- **Claims (OPAC)**: `config/openpartiesandclaims-server.toml` (copy in `server/opac/`). Permissions through LuckPerms, 16 free chunks, 2 force-loaded chunks, OPAC's own welcome messages off because Holy Lois Extras draws the zone titles. Players claim on the world map (J, right-click; M is voice mute) or with `/oclaims`; teams with `/oparties`. Admins: `/opac` and `/oclaims` server claims.
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
- **Boombox stations**: `config/holylois-boombox.json`, then `/boombox reload`. Plain MP3 streams only; at most 6 play at once (held and placed together), and at most 2 placed speakers per chunk by default (`maxPlayingPerChunk`). Controls follow effective OPAC access. Placed boomboxes that are switched on are listed in `world/holylois/boomboxes.json`.
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
- **Terrain:** `holylois-terrain-expansion.timer` runs while the server is empty. Since 1.7.5 it pregenerates everything inside the 20,000 world border while the server is empty, then raises RTP to 5,000. See `server/terrain/README.md`.

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
