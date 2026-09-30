# Holy Lois: Reborn

A Windows launcher companion and signed Minecraft client-pack updater. Minecraft 26.3, Fabric 0.19.5, Java 25. Launcher 0.2.0 ships pack 1.4.1 with 48 mods, four resource packs and seven optional shaders. IPN Auto Refill indicators are hidden in inventory slots and the HUD hotbar by default. The [owner guide](ADMIN-GUIDE.md) covers adding mods, publishing updates and server administration.

## Install and play

Download **HolyLoisSetup.exe** from the [launcher release](https://github.com/pjampjam/HLMC-Reborn/releases/tag/v0.2.0). It is under 1 MB and downloads the self-contained app separately. Friends do not need to install .NET. A 64-bit Windows PC and internet connection are required.

1. Choose Minecraft Launcher or SKlauncher. Install your chosen launcher from its official site if needed.
2. Click **Install Holy Lois**. The app creates a separate game folder and adds the server to Multiplayer.
3. Official launcher: select **Holy Lois: Reborn** under Installations, sign in with your purchased account, and play.
4. SKlauncher 4: use Library's Import flow to import the prepared Official launcher profile. Select only Holy Lois. After importing, close SKlauncher, click **Link imported SK instance** in Holy Lois, choose the imported game folder, and run **Verify & update**. Subsequent updates use that linked folder.
5. Join the saved server. Offline accounts use `/register PASSWORD PASSWORD` once and `/login PASSWORD` later. Passwords need at least five characters and no spaces. Enter them only in Minecraft. Press V to configure your own microphone and output device.

The official-profile import was tested with SKlauncher 4.0.54 beta. SK import and Microsoft sign-in require first-time interaction. The app does not collect credentials or silently install another launcher. It is an updater companion, not a replacement for either game's launcher.

Shaders default to off. The supplied crash reports showed Iris 1.11.7 uploading the enchanted-glint texture inside an active render pass. The included Holy Lois Glint Preload client helper loads those textures before rendering. The owner tested Reimagined and other shaders successfully afterward and reported faster DH loading after overlap/blending adjustments. This is a targeted workaround, not an official Iris fix or a guarantee of stability for every shader. If enabling shaders causes crashes, close Minecraft and click **Disable shaders**. Other graphics settings are preserved, with a backup of the prior Iris settings.

## Updates

The app checks signed GitHub release metadata on opening, every two minutes while open, and before updates. New releases show **Update Holy Lois**. Close Minecraft and its launcher before updating. Downloads come directly from approved publishers and are verified by byte length and SHA-256. Version rollback, invalid signatures and changed content under an existing version are rejected.

Worlds, personal configs, microphone settings, unowned extra mods, other server entries and launcher accounts are preserved. Managed obsolete files are removed after a successful staged update. Interrupted updates recover from a transaction journal. YOSBR supplies defaults only where files are missing; it does not overwrite players' personal settings on every update.

The small installer checks a signed app catalog, downloads the self-contained app, and creates a desktop shortcut. The app is currently **unsigned by Windows Authenticode**. Release metadata signing is separate from Windows publisher signing. SmartScreen or antivirus warnings cannot be ruled out.

## Maintaining the pack

Keep your CurseForge profile as the editing and testing workspace. Local edits become public only after a tested, versioned release is published. Pack updates do not require rebuilding the friends' launcher.

The maintainer publisher command is `prepare-pack PRIVATE_KEY BASE_MANIFEST PROFILE NEW_VERSION DEFAULTS_ZIP OUTPUT`. It checks new mod files against publisher metadata for final 26.3 Fabric releases and prepares signed release files. New files without a verified Modrinth match fail for manual source review. Required dependencies and gameplay still need testing before publishing.

Publish `defaults.zip` in a new immutable release named `pack-vVERSION`. Then replace `pack.json` and `pack.json.sig` together in the `pack-stable` release. Mark pack releases **None**, and leave the launcher release marked **Latest**, because HolyLoisSetup uses its app catalog. The app notices the new pack on its next check. Never change the bytes of an already released pack version.

Client releases do not automatically update the server. Gameplay mods required on both sides must be tested and deployed to the server separately before clients are prompted to use them.

Keep `private/release-private.pem` private and back it up securely. It is excluded from the repository and public packages. Never include worlds, auth databases, SSH keys, voice device settings or account files in releases. Clients need no GitHub account or token.

## Build and validation

Use the .NET 10 SDK. `build.ps1 -Publish -Public` builds the self-contained x64 production app and runs 17 updater test groups. Without `-Public`, the app runs as an isolated preview. Build the native bootstrap using `bootstrap/build-bootstrap.ps1` and a trusted llvm-mingw toolchain, with the exact app catalog URL.

The publisher also supports `keys PRIVATE_DIR ASSETS_DIR`, `sign PRIVATE_KEY FILE SIGNATURE`, and `catalog PRIVATE_KEY APP.exe APP_VERSION VERSIONED_HTTPS_URL OUTPUT`.

Validation includes bad downloads and signatures, rollback and interrupted commit recovery, cancellation, ownership conflicts, preservation of personal files and profiles, server-list NBT, resource-pack activation, defaults privacy, shader recovery, a fresh network installation, and a linked update of the real imported SK instance. The owner confirmed dropped-item and chest animations, premium server login, offline registration, and post-workaround shader gameplay. Prolonged stability, every shader and two-player microphone/acoustics behavior are not yet certified.

Developer-only verification: `HolyLoisReborn.exe --data-dir ISOLATED_FOLDER --verify-install`. Add `--check-online` to test the signed public feed. A linked update test also requires `--launcher-test-root EXISTING_MINECRAFT_LIBRARY --link-sk-instance IMPORTED_HOLY_LOIS_FOLDER`. Close both game and launcher first. Ordinary preview runs do not modify existing launcher libraries.

Third-party mods and shaders remain at their publishers; source packages contain no mod JARs. Artwork is provided by the server owner. The app uses the bundled .NET runtime and Windows APIs.
