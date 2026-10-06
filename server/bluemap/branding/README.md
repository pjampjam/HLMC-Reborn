# Holy Lois branding candidate

Released on 2026-10-06 with launcher 1.3.1 and pack 1.8.0. Tested for BlueMap 5.28. Future live writes, reloads or restarts still require explicit owner `deploy`.

- `holylois-brand/favicon-*`: exact owner-made favicon PNGs.
- `holylois-brand/apple-touch-icon.png`, `icon-192.png`, `icon-512.png`: correctly sized derivatives of the corresponding handmade exports.
- `assets/logo.png`: 200px derivative of the handmade outlined logo for BlueMap's error screen. Engine attribution stays visible.
- `index.html`: reviewed initial favicon, manifest, touch icon and social metadata. Existing frontend JS/CSS entry names stay intact.
- `server-icon.png`: exact handmade 64px favicon for the launcher's server-list entry, root fallback icon and active `config/MiniMOTD/icons/holy-lois.png` override.

The originals remain in the website repository's `brand/` folder, including its Affinity sources and `old/` archive. All artwork rights remain reserved by the owner.

The helper `../prepare-branding.py --root <isolated-copy> --overlay <this-folder>` refuses the live path and checks frontend entry names. It preserves other custom scripts while registering `holylois-brand/branding.js` in `config/bluemap/webapp.conf`. The hook restores document branding after webapp regeneration. BlueMap updates can regenerate `index.html` and `assets/logo.png`; reprepare and review those two files after an upgrade.

Custom-script mechanism: [BlueMap customisation guide](https://bluemap.bluecolored.de/community/Customisation.html).

## Deployment gate

After explicit approval, recheck live versions and players, take and verify a full backup, prepare automatic rollback, and apply only the reviewed files plus the webapp scripts-list entry. Refresh BlueMap settings through its supported light reload. MiniMOTD supplies the active server-list image and supports `minimotd reload`; changing only its icon does not need another live restart. The root PNG is the vanilla fallback. Verify the actual served favicon, not just a file hash. Do not run the test harness against the live root.

Launcher candidate is a separate forward-version build. Publish only after signed app catalog preparation and normal release checks. Embedded signed pack 1.8.0 and all add-on jars remain unchanged.
