# Holy Lois: Reborn

## Current public launcher

[Download HolyLoisReborn.exe 1.0.0](https://github.com/pjampjam/HLMC-Reborn-Packaging-Lab/releases/download/v1.0.0/HolyLoisReborn.exe) - one self-contained Windows x64 app, about 67 MB. No separate installer or .NET installation is needed.

The full release uses the standard HolyLoisReborn application folder and clean Holy Lois: Reborn profile and shortcut names. Existing preview installations migrate with their data, while an older destination installation is retained as a backup. Choose your launcher and optional shortcuts, install the pack, then use Play beneath the logo. Existing users can close Minecraft and its launcher, then reopen Holy Lois to update and migrate through its signed app-stable channel.

The new app uses the existing signed modpack channel from this repository. Its launcher updates and source live in [Packaging Lab](https://github.com/pjampjam/HLMC-Reborn-Packaging-Lab). [Setup and test guide](https://github.com/pjampjam/HLMC-Reborn-Packaging-Lab/blob/main/RESET-AND-TEST.md).

The 1.0.0 artifact passed a local Defender scan and update/rollback tests, but has no Windows publisher certificate. SmartScreen may show Unknown publisher, and other antivirus results can differ. The withdrawn older installers are not restored by this release.

## Legacy installer and production source

The sections below describe the original 0.4.0 application and the shared modpack/admin tooling. For current player downloads and launcher setup, use the public 1.0.0 link above.


> **Original installers remain paused:** Browser downloading the original installer reproduced the Defender detection on 2026-10-01. The original installer and launcher executable assets in this repository are withdrawn. Keep protection enabled and do not whitelist them. See [SECURITY-NOTICE.md](SECURITY-NOTICE.md).

A Windows launcher companion, Minecraft Fabric pack updater and private owner publishing tool.

**Installer 0.4.0 / launcher 0.4.0 / pack 1.5.2 / Minecraft 26.3 / Fabric 0.19.5 / Java 25**

## Players: install and play

The 0.4.0 installer download is withdrawn again because browser download detection persists. The installer is under 1 MB and downloads the complete app. You do not need a separate .NET installation. First setup lets you choose Minecraft Launcher or SKlauncher and select Desktop and Start menu shortcuts separately. You can select neither. Deleted shortcuts stay deleted after launches, updates and installer reruns. Existing installations keep their choices.

1. On first setup, choose **Minecraft Launcher** or **SKlauncher**, choose your shortcuts, and click **Continue**.
2. Click **Install Holy Lois**.
3. Open your chosen launcher and select **Holy Lois: Reborn**.
4. Join the server already saved in Multiplayer.

For SKlauncher 4, import the prepared profile once: **Library > Import > Official launcher > Holy Lois**. Close SKlauncher, return to Holy Lois, click **Link SK game folder**, choose the imported folder, then **Repair / check files**. That connects future updates to the imported pack.

If you deleted the SK pack, Holy Lois now clears a missing folder link instead of failing on startup. Install again, reimport the profile through SKlauncher, and link its new folder. The app restores pack files; SKlauncher's own deleted library entry still needs its import step.

Microsoft Store and desktop Minecraft Launcher installs are detected. Store users do not need to locate an EXE. For unusual desktop installs, **Find launcher** accepts an EXE or shortcut.

The 1.5.2 release adds a centered, masked server-account form. Offline players register once with a password of at least five characters and no spaces. Existing same-IP sessions are remembered for 24 hours; verified premium accounts skip the form. Older clients retain `/register PASSWORD PASSWORD` and `/login PASSWORD` as chat fallback. Never enter a Minecraft password in Holy Lois. Press V in-game to choose your own microphone/output devices.

English is the default language. **Русский** and **Latviešu** are available from the language selector. Your selection is saved. Launcher branding, profile images and desktop icons use the owner's high-resolution crown artwork.

## Updates and settings

The small startup checker verifies and installs launcher updates before the main window opens. The signed main app also replaces its startup checker, so future launcher updates do not need another installer run. Opening the main EXE directly follows the same update check. A verified installed version can open if the release service is unavailable. Invalid signatures or changed content under the same version are rejected.

Modpack updates are separate: Holy Lois checks on opening, every two minutes while open, and before installing. Close Minecraft and its launcher before updating the pack.

Pack 1.5.2 has 50 client mods, four resource packs and seven optional shaders. Chat Animation was added from the owner's successful practice install. **What changed** shows version history and added/removed/updated content.

From pack 1.5.0, changed published shared settings apply during each new-version installation before the next game launch. JSON/options/properties merge changed values and keep unrelated preferences. Changed TOML/JSON5/other reviewed shared files are replaced as whole files. Keybind changes in options.txt, voice devices, account files, worlds and caches stay personal. Repairing the same version does not repeatedly reset settings. Updates retain the previous settings in their recovery backup.

Shaders initially stay off; normal render distance is 12 and DH distance 64. The owner's tested enchanted-glint helper targets the supplied Iris crash. It is a local workaround, not an official Iris fix. Brief coarse DH terrain and download retries remain separate issues. **Disable shaders** is available if a later rendering problem appears.

## Owners: publish from your CurseForge profile

Use the **Holy Lois Admin** Desktop or Start menu shortcut on the owner's PC:

1. Choose your tested CurseForge profile folder.
2. Enter a new version and short change notes.
3. Review the shared settings and confirm the game is closed.
4. Click **Prepare update**.
5. Deploy server-required mods using **Server start / stop / update**.
6. Click **Publish to friends**.

The owner tool checks Fabric dependencies and approved publisher metadata, captures selected settings, signs the release, publishes immutable defaults and promotes the stable feed. Mod/shader/resource-pack files remain at their publishers' download URLs. Your first publish needs the official GitHub CLI's one-time sign-in through **Connect GitHub once**. Complete its browser sign-in and permission review yourself. Holy Lois never asks for a token or password.

The [easy owner guide](ADMIN-GUIDE.md) covers these steps, recovery and server controls. [Technical notes](TECHNICAL-GUIDE.md) retain the detailed command workflow.

The admin tool is local to the owner development folder. Friends receive no private key, SSH key or server administration data. Source archives exclude runtime binaries, mod JARs, worlds, account files and keys. Restore toolchain paths if building the source elsewhere.

## Verification and limits

All 14 shared client/server mods matched by SHA-256. The latest audit found 50 client mods and 29 server mods, with no client-only mod on the server. Dependencies were inspected including bundled Fabric libraries. These checks establish metadata and file consistency, not a guarantee that every mod feature is bug-free.

The updater tests cover bad signatures/downloads, rollback, interrupted commits, cancellation, private-file protection, personal-file preservation, shared-setting migration and same-version behavior. Fresh installation, deleted-instance recovery and linked updates are checked before release.

The installer verifies a pinned RSA-PSS signed app catalog and SHA-256. Pack metadata is signed separately. This is not Windows Authenticode signing: SmartScreen/antivirus warnings remain possible. Requires 64-bit Windows and internet access. Microsoft login, SK import and personal microphone setup require first-time player interaction.

GitHub content is English and uses simple hyphens. Translated in-app UI strings live in assets/strings.json. Language names use their own native spelling, and the WPF language tag follows the user's selection.

## Build

Use the .NET 10 SDK and `build.ps1 -Publish -Public -PublishFolder publish/public-release-0.4.0`. The build script first builds the native checker with the official llvm-mingw toolchain, then embeds it in the app. `private/release-private.pem` stays private and is required only for owner signing.

Developer verification accepts `--data-dir ISOLATED_FOLDER --verify-install`, `--verify-recovery` and `--render-preview`. Add `--check-online` only when the signed public feed matches the current release. Owner mode uses `--owner-root PRIVATE_DEVELOPMENT_FOLDER`.

## Launcher release safety checks

Public executable publishing is blocked while SECURITY-NOTICE.md is present. A clean custom scan does not resolve the reproduced browser detection; explicit non-remediating threat rules also invalidate the local release check. Future public builds run maintainer/Check-Windows-Release.ps1 with Defender enabled, check that artifacts remain available after scanning, record hashes and Authenticode status, and reject detections. Trusted publisher signing can be required with -RequireTrustedPublisher. This local check does not replace vendor review or real browser-download verification and cannot guarantee absence of all antivirus detections.

## Pack 1.5.2 testing

Server helper 1.2.0 is running, and the final client helper is installed in all three owner profiles. The login form, first-registration arrival screen, opt-in inventory slot locks and silent low-durability alerts are included. The owner confirmed offline registration/RTP and premium joins with preserved inventory/location. The signed 1.5.2 pack is published to the stable feed. See [TEST-GUIDE.md](TEST-GUIDE.md).

Registration/login/arrival/Escape screens were rendered using the full client pack. Twenty auth-policy checks passed. Full and differential backups restored into a separate location with all manifest hashes verified. Premium and offline joins were confirmed by the owner; death/bed and two-player acoustic checks remain in the test guide.
