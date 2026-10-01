# Holy Lois: Reborn - owner test

Keep Windows Defender enabled. The original launcher and installer passed the local scan with definitions 1.459.503.0 on October 1. Microsoft reports no positive detection, but the final determination is still pending. The owner chose to keep public launcher and installer downloads paused until Microsoft's final result. Use the existing Minecraft Launcher or SKlauncher for these tests.

## Premium account

1. Open Minecraft Launcher and play the Holy Lois: Reborn installation.
2. Join the saved server. Your verified premium account should skip the password form. Your inventory, UUID and location should be unchanged.
3. Check another player's movement and eyes, then your own character in F5. Try a shader and inspect the outer skin layer from both sides.
4. Press V and check the microphone. Test proximity sound with a second player, including a stone wall and a cave.
5. Quit Minecraft before changing launcher profiles or updating files.

## SKlauncher: new offline player

1. Open SKlauncher and select the Holy Lois pack. Use a new, ordinary username that you own, not a premium player's name.
2. Join. The screen should be black with a centered Create account form. Your username still follows the server's standard 3-16 letters, digits or underscores rule.
3. Enter your own server password twice. Minimum five characters; no spaces. The form masks it and does not save it locally. Do not use your Microsoft account password.
4. Try mismatched fields once to check the inline error, then submit matching fields.
5. Movement, attacks and inventory interaction should be blocked until authentication. Escape should offer Back and Disconnect.
6. After registration, wait for safe random placement inside the pregenerated Overworld. The black screen should disappear about 1.5 seconds after the teleport. The welcome and command tips should then be visible.
7. Disconnect and rejoin from the same IP. The existing 24-hour remembered session should skip the password form. This is intended.

## SKlauncher: force a login test

From the authenticated offline character, use `/logout`. This invalidates its session. Rejoin if necessary. The centered Log in form should appear. Test one wrong password, then the correct password. Three wrong attempts trigger the existing protection.

If Escape is opened while authentication is pending, gameplay must remain blocked. Closing the form or deleting the client helper must never grant authentication: older clients continue using EasyAuth's chat commands.

## Death respawn

Use a disposable test character or empty its inventory before testing death.

1. Without a bed or respawn anchor, respawn and check that placement is random inside the pregenerated area.
2. Set a valid bed spawn, die again, and check that the bed is used.
3. Break that bed, die again, and check random placement is restored.

Leaving the End alive must not trigger a random death respawn. Joining again with an existing character must not randomly move it.

## Friends' permissions and updates

With a non-operator account, test `/home set base`, `/home tp base`, `/tpa NAME`, `/tpaccept NAME`, `/rtp`, claims and shopping. Administrative auth, backup, permission and world-generation commands must remain restricted.

After the signed pack update is published, test both an existing install and a fresh install. Confirm the server is prelisted, resource packs activate, Iris skin compatibility is enabled, personal voice devices remain personal, and the update changelog appears.

## Backups

World backups are now differential every ten minutes and full every six hours. Keep twelve differential backups and two full backups within an 8 GB budget, with a 2 GB free-space reserve and idle skipping. Each differential depends on a full backup, so JEB preserves that dependency when rotating files. Rebuildable DH caches are excluded; terrain, player data and onboarding state are included.

The new full backup passed CRC and manifest SHA-256 checks and was extracted into a separate test location. A complete stopped-server archive also protects authentication, claims, permissions, configs and mod data outside the world.

Check `/jeb list` and `/jeb next`. A budget can still stop backups when protected files cannot fit. Exploration, caches and historical manual archives have separate storage costs. Check `df -h /` periodically and copy important complete archives to your own PC.

## Inventory defaults

Slot locking is off by default; inventory sorting remains enabled. Low-durability and failed-replacement alerts are disabled visually and audibly. The purple refill indicators remain hidden. If a friend has not updated yet, open Inventory Profiles Next with R + C and turn off Enable Lock Slots, Visual Alert on Failed Replace and Sound Alert on Failed Replace. The default lock gesture in this build is Alt plus left-click, not an ordinary click. A remembered lock-configuration mode or a changed binding can make clicks behave differently.

These choices apply on the next pack-version update. Friends can enable locking later if they want it. Server permissions do not control this client-side inventory feature.

The owner confirmed new registration and RTP in SKlauncher. The 1.5.2 helper suppresses routine authentication reminders before the form opens, keeping only the welcome/command tips after login. Wrong-password feedback is preserved. The owner also confirmed premium joins and preserved player data. Valid/invalid-bed death checks still need an in-game test.

Pack 1.5.2 hides routine auth chat, native resource-pack progress and the repeated unverified-chat popup only on Holy Lois. Real download failures still show. Runtime tests verified that progress on other servers remains visible. The owner confirmed both premium and offline joins.
