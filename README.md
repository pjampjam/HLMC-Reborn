# Holy Lois: Reborn

A Minecraft modpack for our friends, with a Windows launcher that installs the pack and keeps it updated.

**Launcher 1.1.0 / pack 1.5.4 / Minecraft 26.3 / Fabric 0.19.5 / Java 25**

## Download and play

[Download HolyLoisReborn.exe 1.1.0](https://github.com/pjampjam/HLMC-Reborn-Packaging-Lab/releases/download/v1.1.0/HolyLoisReborn.exe) - about 67 MB, for Windows x64. Its runtime is included, so no separate .NET installation is needed.

1. Open the EXE. Choose **Minecraft Launcher** or **SKlauncher** and your optional Desktop and Start menu shortcuts.
2. Close Minecraft and your Minecraft launcher, then click **Install Holy Lois**.
3. Click **Play** beneath the logo. Select **Holy Lois: Reborn** in your chosen launcher. In SKlauncher, click **Install** there once to prepare Minecraft and Java, then **Play**.
4. Open Multiplayer and join the saved Holy Lois server.

SKlauncher profiles are added automatically. Microsoft Store and desktop Minecraft Launcher installations are detected automatically too; **Settings** has a manual launcher choice if needed. English is the default, with Russian and Latvian available on the main screen.

See the [player guide](PLAYER-GUIDE.md) for joining, voice chat, homes, teleporting, claims and shops.

## Updates

Open Holy Lois whenever you want to check for updates. The app checks for its own updates before opening the main window, so you do not need another installer. Pack updates are checked on opening and every two minutes while the app is open. Close Minecraft and its launcher before installing an update.

After installation, you can also open the saved pack directly in Minecraft Launcher or SKlauncher. Return to Holy Lois to receive new pack versions.

Updates preserve worlds, personal voice-device choices and extra client mods or shaders. Changed shared defaults apply once per new pack version; unrelated preferences remain. **What changed** lists release history. Deleted shortcuts stay deleted. **Settings > Clear completed downloads** removes verified duplicate downloads and shows the space recovered; the working app, rollback copy and game data are retained.

## For the owner

Use **Holy Lois Admin** to choose your tested CurseForge profile, prepare a new version, deploy server-required changes and publish the update. Follow the [admin guide](ADMIN-GUIDE.md); use [technical notes](TECHNICAL-GUIDE.md) for the detailed workflow and [test guide](TEST-GUIDE.md) before promotion. The trusted-friends setup does not need an additional anti-cheat addon.

This repository holds the signed pack channel and admin documentation. Current launcher source and app releases live in the [launcher repository](https://github.com/pjampjam/HLMC-Reborn-Packaging-Lab). Its [setup and reset guide](https://github.com/pjampjam/HLMC-Reborn-Packaging-Lab/blob/main/RESET-AND-TEST.md) covers clean installation tests and app removal. The source archive here preserves the original companion source with current pack assets and game helpers; use the launcher repository to build the current player app.

## Release and privacy notes

The app has no Windows publisher certificate, so SmartScreen may display **Unknown publisher**. Antivirus results can differ between computers. Historical installer notices are kept in [SECURITY-NOTICE.md](SECURITY-NOTICE.md); privacy and source-sharing rules are in [PRIVACY.md](PRIVACY.md).
