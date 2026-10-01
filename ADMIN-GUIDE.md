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

Open Holy Lois and choose SKlauncher. A missing link is now cleared instead of blocking startup.

1. Click **Install Holy Lois** or **Repair / check files**.
2. Open SKlauncher: **Library > Import > Official launcher**. Import only **Holy Lois: Reborn**.
3. Close SKlauncher. In Holy Lois, click **Link SK game folder** and choose that imported game's folder.
4. Click **Repair / check files**, then open SKlauncher and play.

The updater restores pack files. SKlauncher's own library entry must be reimported through SKlauncher if you deleted it there.

## Official Minecraft Launcher

Microsoft Store and desktop installs are detected. Store users do not need to search for an EXE. Click **Open Minecraft Launcher**, then choose **Installations > Holy Lois: Reborn > Play**. Sign in inside Minecraft Launcher.

For an unusual desktop install, **Find launcher** accepts its EXE or a Windows shortcut. The profile and HQ icon are prepared separately from other Minecraft installations.

## Backups and space

Scheduled world backups: differential every 10 minutes and full every six hours. Keep twelve differential and two full backups within an approximately 8 GB budget, with a 2 GB free-space reserve. Each differential depends on its full backup; JEB keeps required bases. Automatic idle backups are skipped. Complete maintenance backups have a separate two-archive retention. Historical manual archives and uploads are not deleted automatically.

Old backups rotate, but worlds, DH data, logs and manual archives can still fill the disk. Check `df -h /` and successful backups with `/jeb list`. Copy important complete archives off the VM. They include private server data, so do not send them to friends.

## Current pack and tests

Pack 1.5.2 has 50 client mods, four resource packs and seven optional shaders. The server has 29 mods. All 14 shared mods match by hash. Required dependency metadata, including bundled Fabric libraries, was checked on both sides.

The shader helper addresses the supplied Iris enchanted-glint crash. The owner tested shaders successfully afterward. Brief coarse DH terrain and terrain-download retries are separate issues, not certified fully fixed.

The normal launcher defaults to English, with Russian and Latvian selectable. GitHub notes and owner documentation remain English. The native installer remains under 1 MB and does not need a separate .NET install. Windows Authenticode signing is still absent, so SmartScreen warnings remain possible.

Keep your SSH key and `private/release-private.pem` private. Friends receive only the public installer and signed downloads. More implementation detail is in [TECHNICAL-GUIDE.md](TECHNICAL-GUIDE.md).

## Login, arrival and inventory defaults

The owner confirmed pack 1.5.2 joins through the existing Minecraft Launcher and SKlauncher. Public launcher and installer downloads stay paused until Microsoft's final review result. The owner confirmed offline registration/RTP and premium joins; 1.5.2 is the stable pack.

The centered form uses the existing EasyAuth account database and does not store a password on the client. Premium verification and the 24-hour same-IP session stay enabled. Before authentication, EasyAuth blocks movement, combat, inventory actions and damage. Escape in the form offers Back and Disconnect.

First registration uses safe RTP inside the pregenerated Overworld, followed by a 1.5-second black arrival screen. Returning players keep their position. A death respawn uses RTP only when vanilla finds no usable bed or anchor; leaving the End alive does not count as death. Brief arrival damage protection is temporary.

Inventory Profiles Next sorting remains available. Slot locking is opt-in; failed-replacement and low-durability visual/sound alerts are off. Friends on older settings can open R + C to disable those options immediately.

The old chained backup schedule reached its size cap and stopped making new backups. It was replaced by the schedule above, and a full plus differential backup was restored and hash-checked separately. Rebuildable Distant Horizons SQLite caches are excluded from scheduled world backups; terrain and player data are included. Complete stopped-server maintenance backups still protect authentication, permissions, claims and configs outside the world. Other files can still fill storage, so verify completed backups and disk usage periodically.

Use [TEST-GUIDE.md](TEST-GUIDE.md) for the premium, offline, respawn, voice and non-operator checks. No additional server mods are required for this release. Test the existing features before adding more systems.
