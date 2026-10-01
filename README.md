# Holy Lois: Reborn

A Windows launcher companion, Minecraft Fabric pack updater and private owner publishing tool.

**Launcher 0.3.0 / pack 1.5.0 / Minecraft 26.3 / Fabric 0.19.5 / Java 25**

## Players: install and play

Download [HolyLoisSetup.exe](https://github.com/pjampjam/HLMC-Reborn/releases/download/v0.3.0/HolyLoisSetup.exe). The installer is under 1 MB and downloads the complete app. You do not need a separate .NET installation. Setup creates Holy Lois Reborn shortcuts on your Desktop and in your Start menu.

1. Choose **Minecraft Launcher** or **SKlauncher** in Holy Lois.
2. Click **Install Holy Lois**.
3. Open your chosen launcher and select **Holy Lois: Reborn**.
4. Join the server already saved in Multiplayer.

For SKlauncher 4, import the prepared profile once: **Library > Import > Official launcher > Holy Lois**. Close SKlauncher, return to Holy Lois, click **Link SK game folder**, choose the imported folder, then **Repair / check files**. That connects future updates to the imported pack.

If you deleted the SK pack, Holy Lois now clears a missing folder link instead of failing on startup. Install again, reimport the profile through SKlauncher, and link its new folder. The app restores pack files; SKlauncher's own deleted library entry still needs its import step.

Microsoft Store and desktop Minecraft Launcher installs are detected. Store users do not need to locate an EXE. For unusual desktop installs, **Find launcher** accepts an EXE or shortcut.

Offline players register in Minecraft chat: `/register PASSWORD PASSWORD` once, then `/login PASSWORD`. Passwords need at least five characters and no spaces. Never enter a Minecraft password in Holy Lois. Press V in-game to choose your own microphone/output devices.

English is the default language. **Русский** and **Latviešu** are available from the language selector. Your selection is saved. Launcher branding, profile images and desktop icons use the owner's high-resolution crown artwork.

## Updates and settings

Holy Lois checks on opening, every two minutes while open, and before installing. Close Minecraft and its launcher before updating.

Pack 1.5.0 has 49 client mods, four resource packs and seven optional shaders. Chat Animation was added from the owner's successful practice install. **What changed** shows version history and added/removed/updated content.

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

All 14 shared client/server mods matched by SHA-256. The audit found 49 client mods and 29 server mods, with no client-only mod on the server. Dependencies were inspected including bundled Fabric libraries. These checks establish metadata and file consistency, not a guarantee that every mod feature is bug-free.

The updater tests cover bad signatures/downloads, rollback, interrupted commits, cancellation, private-file protection, personal-file preservation, shared-setting migration and same-version behavior. Fresh installation, deleted-instance recovery and linked updates are checked before release.

The installer verifies a pinned RSA-PSS signed app catalog and SHA-256. Pack metadata is signed separately. This is not Windows Authenticode signing: SmartScreen/antivirus warnings remain possible. Requires 64-bit Windows and internet access. Microsoft login, SK import and personal microphone setup require first-time player interaction.

GitHub content is English and uses simple hyphens. Translated in-app UI strings live in assets/strings.json. Language names use their own native spelling, and the WPF language tag follows the user's selection.

## Build

Use the .NET 10 SDK and `build.ps1 -Publish -Public -PublishFolder publish/public-release-0.3.0`. Build the native installer with `bootstrap/build-bootstrap.ps1` and the official llvm-mingw toolchain. `private/release-private.pem` stays private and is required only for owner signing.

Developer verification accepts `--data-dir ISOLATED_FOLDER --verify-install`, `--verify-recovery` and `--render-preview`. Add `--check-online` only when the signed public feed matches the current release. Owner mode uses `--owner-root PRIVATE_DEVELOPMENT_FOLDER`.
