# Holy Lois release history

Historical player notes, retained from the README. Current setup and play instructions are in [README.md](README.md).

## What's new in pack 1.8.2

- Party members are protected from friendly fire, with an optional health and food panel.
- Use /rally to share a meeting point with your party for 90 seconds.
- Daily supplies appear in a clear reward card, with daily coins claimed through their existing reward system.
- Voice chat can recover its connection after login; /voicefix requests another attempt.
- Cleaner login messages and matching release news across the website and launcher.

## What's new in pack 1.8.1

- Placed relics keep their name and lore.
- Fishing crates give their proper enchanted rewards.
- Bows, maps and fishing rods work better with the first-person body view.
- Combat teleports and land protection behave more reliably.
- Login and registration quiet world sounds.
- At most two placed boomboxes play per chunk, with six streams across the server.
- Your selected server skin appears on your statistics head.

## What's new in pack 1.8.0

- Catch ten kinds of fish in different waters, weather and times of day.
- Fish range from Common to Legendary in size. Rare catches keep their weight and your name as trophies.
- Reel in loot crates, messages in bottles and buried treasure maps.
- Find named relics in dungeon, tavern and town chests. Complete their sets to earn achievements.

## What's new in launcher 1.3.1

- Handmade server-list icon, matching the refreshed website and BlueMap branding. No gameplay changes.

## What's new in launcher 1.3.0

- **Fast start**: press Play and Minecraft opens straight from the Holy Lois launcher with your player name. No SKlauncher. Java 25, Minecraft and Fabric come from Mojang and Fabric, are checked by hash and are reused from another launcher on the PC when it already has them. A start window shows each step; if the game crashes, the launcher comes back with a report you can copy.
- **Join Holy Lois on start** for everyone, also for bought accounts in Minecraft Launcher. Turn it off in Settings for singleplayer.
- **Player names** with history: a new name is a new player on the server, so the launcher warns first, keeps every earlier name one click away and allows three new names a day. A name that belongs to a bought Minecraft account is refused.
- Pack stays 1.7.11, no server restart.

## What's new in pack 1.7.11

- **Quick Play is removed.** In testing it never joined the server by itself, so Play did the same as the old way. **Launcher 1.2.7** drops the setting: Play opens your Minecraft launcher, then you join from Multiplayer (singleplayer works as before). Holy Lois Extras 1.5.1 no longer contains the Quick Play part.
- ~~Coming later: Integrated start~~ (arrived as fast start in launcher 1.3.0).
- No server restart for this release.

## What's new in pack 1.7.10

- ~~Quick Play~~ (removed in 1.7.11, it never joined by itself).
- **Launcher 1.2.6** closes Minecraft and its launcher for you when an update needs it, after you press **Agree**. Greener Play button, new icons for the launcher and the Minecraft window.
- **AFK time no longer counts as playing**: achievements, land claims, leaderboards, stats and the Tab list skip it (Essential Commands decides who is AFK; it starts counting from this release).
- **Secret code**: a code of the day hides somewhere on holylois.com. `/redeem CODE` in game gives one prize per player per day.
- **Quieter owner**: no join, leave, AFK, advancement or discovery notices for the server owner; deaths still show.
- **Calmer world generation**: the terrain job works in short slices with rests, so the server does not fall behind while the border grows.
- **Rules**: rule 3 says to play with the launcher's mods and nothing else (the mod check from 1.7.8); shaders and resource packs stay your choice as long as they are not x-ray.

## What's new in pack 1.7.8

- **One pack for everyone**: the server checks the mod list when you join. Extra mods are turned away with a message that says how to fix it; shaders, resource packs and your own settings stay yours. The launcher's **Play** button moves extra mods out of the Holy Lois folder (kept in a quarantine folder, never deleted), repairs changed pack files and switches the pack's resource packs back on.
- **New crown icon**: the Minecraft window and taskbar icon is the Holy Lois crown, crisp at every size, and the server list has a new icon.
- **Clearer achievements**: new texts for Discoverer, Dungeon Delver, Deeper Still and Odd Pillar.
- The server restarts once (a one-minute countdown first).

## What's new in pack 1.7.7

- **Fixes from the 1.7.6 test**: the first-person body may sink into a wall a little, the camera is lifted in bed so your eyes are not inside your head, and the tool swap line reads "Switched to ...".
- **Dynamic lights follow your shader setting**: with a shader pack on, the shader lights what you hold and dropped torches and mobs still glow; with shaders off, dynamic lights are fully on again.
- No server restart for this one.

## What's new in pack 1.7.6

- **Dungeons**: every underground dungeon (small, medium and large, in plains, ice and sand styles) and every obelisk is announced when someone first finds it, with new achievements: Dungeon Delver, Deeper Still, Dungeon Master and Odd Pillar. Their chests can drop Runeforged runes.
- **Boombox**: it now reaches from 16 blocks on volume 1 up to 48 blocks on volume 10.
- **Tools**: a broken tool is replaced by an unenchanted spare of the same kind, lowest material first. Your enchanted tools are never swapped in for you.
- **Fixes**: **R** on an empty slot sorts without opening a recipe, the first-person body steps forward when a wall is behind you and hides while you sleep, and with a shader pack on torches light yellow (dynamic lights pause while shaders are on).
- **Mods**: all Holy Lois mods now show the logo, author and links in Mod Menu.

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
- **Discoveries**: the first visit to a big structure (Ancient City, Tavern, Illager Manor, any dungeon and many more) is announced to everyone.
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

