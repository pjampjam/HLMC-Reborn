# Holy Lois: Reborn

A Minecraft modpack for our friends, with a Windows launcher that installs the pack and keeps it updated.

**Launcher 1.2.3 / pack 1.7.5 / Minecraft 26.3 / Fabric 0.19.5 / Java 25**

## Download and play

[Download HolyLoisReborn.exe](https://github.com/pjampjam/HLMC-Reborn-Packaging-Lab/releases/latest/download/HolyLoisReborn.exe) - about 67 MB, for Windows x64. Its runtime is included, so no separate .NET installation is needed.

1. Open the EXE. Choose **Minecraft Launcher** or **SKlauncher** and your optional Desktop and Start menu shortcuts.
2. Close Minecraft and your Minecraft launcher, then click **Install Holy Lois**.
3. Click **Play** beneath the logo. Select **Holy Lois: Reborn** in your chosen launcher. In SKlauncher, click **Install** there once to prepare Minecraft and Java, then **Play**.
4. Open Multiplayer and join the saved Holy Lois server (**play.holylois.com**). Website: https://holylois.com, Discord: https://discord.gg/FzBJSZwY2c

SKlauncher profiles are added automatically. Microsoft Store and desktop Minecraft Launcher installations are detected automatically too; **Settings** has a manual launcher choice if needed. English is the default, with Russian and Latvian available on the main screen.

See the [player guide](PLAYER-GUIDE.md) for joining, voice chat, maps, cooking, furniture, homes, teleporting, claims and shops.

## What's new in pack 1.7.5

- **Boombox**: sneak + scroll changes its volume (1-10, louder reaches further), music notes float while it plays, and six new stations: dubstep, drum and bass, trap, lo-fi, hardstyle and techno.
- **Smarter keys**: **R** on an item shows its recipe, **R** on an empty slot sorts. A broken tool is replaced by the same kind, cheapest first, with a soft chime. Enchantment descriptions show while you hold Shift.
- **Homes and portals**: with several homes, `/home` goes to the one named `home`; `/Home` works too. Walking back through a Nether portal takes you to the portal you came from. Clicking a command in chat runs it without the confirm screen.
- **Bigger world**: the border is 20,000 blocks wide. New land is prepared while the server is empty, and `/structures` tells you what you are standing in.
- **Polish**: no flickering lines between glass blocks with shaders, a crown window icon, 30 FPS in the background, and a launcher that shows new updates in a gold card with an Update now button.
- **Correction**: the world map opens with **J** (the 1.7.4 notes said M).

## What's new in pack 1.7.4

- **Land on the map**: press **J** for the world map, right-click a chunk and claim it (Open Parties and Claims replaces Flan). 16 chunks are free, playtime earns more and `/claims buy` adds extra ones for coins. Teams with `/oparties`.
- **Zone titles**: entering a new biome or someone's land shows its name at the top of the screen, or Wilderness.
- **Fair fights**: logging out mid-fight kills you; PvP deaths leave the loot for the winner with no death marker. `/rtp` never drops you into or next to someone's land.
- **Help**: `/support MESSAGE` reaches the owner on Discord right away, `/report PLAYER REASON` for player problems, `/donate` for the wallets.

## What's new in pack 1.7.3

- **Hotfix**: achievement tabs switch with a left click (1.7.2 broke them), a placed boombox shows its real texture instead of a pink cube.
- **Text**: game and mod text uses plain hyphens; `/support` lists TRON, labels Bitcoin SegWit and explains each network on hover.

## What's new in pack 1.7.2

- **Boombox**: set it down on any block and it keeps playing for everyone nearby. Game music pauses while one plays near you.
- **Fixes**: achievement tabs switch again with Num Lock on, Holy Lois comes first, one enchantment description instead of two.
- **Daily coins** get a [Claim] button at login, seven new achievements, and `/support`.
- **Defaults**: the recipe list shows only while you search, plain tools are used until they break, the first-person body sits a bit further back.

## What's new in pack 1.7.0

- **Boombox**: a portable speaker that plays internet radio to everyone nearby through voice chat.
- **Daily gifts**: a small gift every day you log in, and a **Holy Lootbox** every 7th day in a row.
- **Achievements**: a Holy Lois advancement tab with secret challenges such as Grand Tour and Five-Star Chef.
- **Auction house**: `/ah`, `/sell`, orders and `/pay` with server coins.
- **Recipe lookup** with Roughly Enough Items, and descriptions for every modded enchantment.
- **Macaw's Holidays**: Christmas trees, lights, garlands, candy canes and Halloween decorations, plus gifts and fireworks on Latvian holidays.
- **Tab leaderboards**: diamonds, ancient debris, playtime, mob kills, blocks mined and more, a new board each time the page comes round.
- **Discoveries**: the first visit to a big structure (Ancient City, Tavern, Illager Manor and many more) is announced to everyone.
- **After death**: chat shows where you died, and the minimap death point disappears when you get there.
- **Looks**: framed rarity tooltips, held torches light up the area, falling leaves, connected glass, effect timer bars and shulker box previews.
- **Fixes**: J opens the world map again, no more chest flicker with shaders, no key clashes, and real chunks load further out before the distant view takes over.

## What's new in pack 1.6.x

- **Farmer's Delight** cooking: knife, cutting board, cooking pot, burgers, sushi rolls, pumpkin slices and new crops.
- **Macaw's Furniture**: chairs you can sit on, tables, drawers, wardrobes and kitchen cabinets.
- **Xaero's Minimap and World Map** (J opens the map, M stays voice mute) and **Jade** block info.
- **Dungeons and Taverns** and **Towns and Towers** in newly explored land, with Runeforged loot in their chests.
- **Custom music discs** with `/audioplayer`, played through voice chat.
- Hold **Tab** for live server stats, Latvian name days and leaderboards. Right-click ripe crops to harvest and replant. One sleeping player skips the night.

## Updates

Open Holy Lois whenever you want to check for updates. The app checks for its own updates before opening the main window, so you do not need another installer. Pack updates are checked on opening and every two minutes while the app is open. Close Minecraft and its launcher before installing an update.

After installation, you can also open the saved pack directly in Minecraft Launcher or SKlauncher. Return to Holy Lois to receive new pack versions.

Updates preserve worlds, personal voice-device choices and extra client mods or shaders. Changed shared defaults apply once per new pack version; unrelated preferences remain. **What changed** lists release history. Deleted shortcuts stay deleted. **Settings > Clear completed downloads** removes verified duplicate downloads and shows the space recovered; the working app, rollback copy and game data are retained.

## For the owner

Use **Holy Lois Admin** to choose your tested CurseForge profile, prepare a new version, deploy server-required changes and publish the update. Follow the [admin guide](ADMIN-GUIDE.md); use [technical notes](TECHNICAL-GUIDE.md) for the detailed workflow and [test guide](TEST-GUIDE.md) before promotion. The trusted-friends setup does not need an additional anti-cheat addon.

This repository holds the signed pack channel and admin documentation. Current launcher source and app releases live in the [launcher repository](https://github.com/pjampjam/HLMC-Reborn-Packaging-Lab). Its [setup and reset guide](https://github.com/pjampjam/HLMC-Reborn-Packaging-Lab/blob/main/RESET-AND-TEST.md) covers clean installation tests and app removal. The source archive here preserves the original companion source with current pack assets and game helpers; use the launcher repository to build the current player app.

## Release and privacy notes

The app has no Windows publisher certificate, so SmartScreen may display **Unknown publisher**. Antivirus results can differ between computers. Historical installer notices are kept in [SECURITY-NOTICE.md](SECURITY-NOTICE.md); privacy and source-sharing rules are in [PRIVACY.md](PRIVACY.md).
