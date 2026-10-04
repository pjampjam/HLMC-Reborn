# Playing Holy Lois: Reborn

For pack 1.7.1 and launcher 1.2.2. Start with the [download and setup steps](README.md#download-and-play), then select **Holy Lois: Reborn** in Minecraft Launcher or SKlauncher. The server is already saved in Multiplayer.

## Joining

Offline accounts see a centered registration or login form. Register with a server password of at least five characters, without spaces. Use a separate password from your Minecraft account. Your login is remembered for **24 hours on the same IP**. Verified premium accounts skip the form.

On your first registration, wait for the arrival screen to finish while the server finds a safe starting location. You can press Escape to leave if needed.

## Voice and controls

| Key | Action |
| --- | --- |
| **V** | Choose your microphone, output device and voice settings. |
| **Hold Caps Lock** | Talk to nearby players. |
| **Page Down** | Show or hide your body in first person. |
| **Tab** | Player list with your ping, server TPS and uptime, playtime, the day, server location, Latvian name days and leaderboards. |
| **J** | Open the world map. |
| **Y** / **U** / **Z** | Minimap settings, waypoint list, larger minimap. |
| **M** | Mute your microphone (unchanged). |
| **C** | Zoom. |
| **Hold `** (left of 1) | Mine the whole ore vein or tree while breaking a block. The HUD shows how many blocks will break. |

Map keys are added only where the key was free, and Holy Lois fixes known clashes when the pack updates. If one does nothing, open **Options > Controls > Key Binds**: the search bar and the conflict filter show what shares a key. Jade shows a small label for whatever you look at, including crop growth.

If your body clips through the view, press **Page Down** to use the simpler view while keeping animated arms. Shaders start off; choose a supplied shader in Minecraft's video settings when ready. **Disable shaders** in Holy Lois is available if rendering causes trouble.

## Homes

Use a name such as `base` for a saved location. Replace it with your own home name.

| Command | What it does |
| --- | --- |
| `/home set base` | Save your current location. |
| `/home tp base` | Return to that location. |
| `/home list` | Show your saved homes. |
| `/home delete base` | Remove that saved home. |
| `/home` | Go to your only home. With several, it goes to the one named `home` (save it with `/home set home`), otherwise it lists them to click. |

Home names that differ only in capitals (`Home` and `home`) count as the same name, and `/Home` works like `/home`. Clicking a command in chat, such as a home in that list or a tpa accept, runs it right away. These are the pack's [Essential Commands home commands](https://github.com/John-Paul-R/Essential-Commands#commands).

## Teleporting

Replace `NAME` with the player's name.

| Command | What it does |
| --- | --- |
| `/tpa NAME` | Ask to visit a player. |
| `/tpaccept NAME` | Accept that player's request. |
| `/tpdeny NAME` | Decline that player's request. |
| `/rtp` | Find a safe new place, never in or next to someone's land. Stand still for 3 seconds; five-minute cooldown. |

The request commands come from [Essential Commands](https://github.com/John-Paul-R/Essential-Commands#commands); `/rtp` is Holy Lois's own and stays within the server's prepared area. Teleports do not work during a fight (see **Fights** below).

Walking back through a Nether portal takes you to the portal you came from, not to whichever portal is nearest. The world is 20,000 blocks wide (10,000 out from the centre in each direction).

## Protect your land

Land is claimed in whole chunks (16 x 16 blocks, from bedrock to sky) with **Open Parties and Claims**.

1. Press **J** for the world map, right-click a chunk near you and choose **Claim**. Drag over several chunks to claim an area. You can also stand in a chunk and type `/oclaims claim`.
2. Claimed land shows on the minimap and world map in your colour. Other players cannot build, break, open chests or hurt animals there.
3. Give your land a name and colour: press **'** (OPAC menu), open your player config and set **Claimed Area Name** and the claim colour. The zone title then shows "Name (Owner)".

You don't need a team to claim. Everyone, admins included, claims under the same limits.

**How much land?** Everyone gets **16 chunks free**, earns **1 more for every 2 hours played** (up to 48), and can buy more with coins: `/claims` shows your numbers, `/claims buy` buys the next chunk (500 coins, each next one 15% more) and `/claims sell` sells one back for half price.

**Teams:** `/oparties create`, then `/oparties invite NAME`. Team members can build on each other's land. When you walk into someone's land, the zone title at the top of the screen says whose it is; outside claims it says **Wilderness**.

See the [Open Parties and Claims wiki](https://github.com/thexaero/open-parties-and-claims/wiki) for every option.

## Sell to other players

List items on the auction house with `/ah`, or post a buy request with `/orders`. See **Money and the auction house** below.

## Cooking and furniture

**Farmer's Delight** adds real meals. Start with a **knife** (a stick plus flint, iron, gold or diamond) and a **cutting board** (planks and sticks). Place an ingredient on the cutting board, then right-click it with the knife to slice it: pumpkins become pumpkin slices, cabbages become leaves, fish become sushi ingredients. A **cooking pot** over a campfire or **stove** makes soups and stews; a **skillet** fries. Try hamburgers, salmon and cod rolls (sushi), pies and stuffed pumpkins. Wild cabbages, tomatoes, onions and rice grow in newly explored land. Your recipe book shows every recipe once you hold the ingredients.

**Macaw's Furniture** adds chairs and benches you can sit on (right-click), tables, desks, drawers, wardrobes and kitchen cabinets. Most pieces are made from planks or logs of the wood you want; drawers and wardrobes store items like chests.

**Macaw's Holidays** adds Christmas trees, string lights, garlands, wreaths, candy canes, presents and Halloween pumpkins and decorations.

Right-click a fully grown crop to harvest it and replant automatically. One player sleeping in a bed is enough to skip the night.

## Explore

Newly explored land has **Dungeons and Taverns** (taverns, crypts, illager camps and manors, shrines, wells and more) and **Towns and Towers** (new village styles and towers). Their chests can roll Runeforged stones and gear: vaults and boss rooms give the best rewards. Areas you already explored stay as they are.

The first time anyone walks into a big structure, the whole server sees who discovered it. Villages, wells, camps and small ruins stay quiet. Type `/structures` to see which structure you are standing in. Hold **Tab** to see the leaderboards; each time the page comes round it shows another one, from diamonds and ancient debris to playtime and fish caught.

## Your own music

Put your own songs on music discs and goat horns. They play through voice chat, so other players hear them nearby and caves echo.

1. Type `/audioplayer`, click **Upload audio via Filebin**, and follow the link to upload an MP3 or WAV (up to 20 MB, 5 minutes).
2. Back in game, click the confirm message. Hold a music disc or goat horn and click **put on item**.
3. Play the disc in a jukebox. `/audioplayer volume` changes your own listening volume.

Only upload music you are allowed to share.

## Daily gifts and the Holy Lootbox

Log in once a day (Riga time) for a small gift: food, ores, books or rockets. Every 7th day in a row you get a **Holy Lootbox**, a gold present; right-click it to open. Lootboxes hold diamonds, Runeforged stones, golden apples and more, and sometimes a named tool or weapon with your name on it. Each finished week raises the lootbox tier, up to tier 3. Missing a day starts the streak again. Holidays such as Christmas, New Year, Jāņi, Halloween and 18 November bring their own greeting and gift.

## Money and the auction house

Everyone starts with 250 coins. `/sell` turns spare items into coins, `/ah` opens the auction house to buy and list items, `/orders` lets you ask for items at your price, `/pay NAME AMOUNT` sends coins and `/bal` shows your balance. `/daily` adds 100 coins each day; when you log in, the daily gift message has a **[Claim]** button for them.

## Boombox

Craft a boombox from string (top), iron ingot + jukebox + iron ingot (middle) and amethyst shard + redstone + amethyst shard (bottom).

- **Carry it**: hold it in either hand and right-click the air to play internet radio. Everyone within 24 blocks hears it through voice chat, and it follows you. Right-click again for the next station, sneak + right-click to stop. Sneak + scroll while holding it, or while looking at a placed one, sets its volume from 1 to 10; louder also reaches a little further. It stops when you drop it or put it away.
- **Set it down**: right-click a block with it. Right-click the placed boombox to play or switch stations; sneak with an empty hand and right-click to turn it off. It keeps playing while anyone is nearby, even after a restart. Break it to pick it up again.

The song title shows above your hotbar, music notes float from a playing boombox, and the game's own music pauses while a boombox plays near you. Your own Boombox volume slider is in the voice chat settings (press V, then the volume button). `/boombox stations` lists the stations.

## Achievements and recipes

Press **L**; the **Holy Lois** tab comes first. Some goals are hidden until you get close, such as visiting every kind of dungeon or eating every Farmer's Delight meal. In your inventory, hover an item and press **R** for its recipe or **U** for what it is used in. **R** over an empty slot sorts your inventory instead.

## After death

Chat tells you where you died, and the minimap marks the spot until you reach it. Your dropped items stay for **30 minutes of loaded-world time**, and only you can pick them up for the first 5 minutes. Time does not advance while the area is unloaded. Recover them promptly: **fire, lava and the void can still destroy items**.

## Fights

Hitting another player, or being hit by one, puts you both **in combat for 20 seconds** (a red counter above the hotbar). While in combat, `/rtp`, `/home`, `/tpa`, `/spawn` and `/back` do not work, and **logging out kills you**. A PvP death drops your loot unlocked for the winner, with no coordinates in chat and no minimap marker. Getting hit by a monster only blocks teleports for 5 seconds. PvP still needs both players' consent (rule 5).

## Help, reports and donations

- `/support MESSAGE`: pjampjam gets it on Discord right away and replies in game. Start with `bug`, `help` or `grief` if it fits.
- `/report NAME REASON`: report a player privately.
- `/donate`: crypto wallets if you want to help pay for the server. Donations never buy anything in game.

## Keep your pack updated

You can launch the saved pack directly from Minecraft Launcher or SKlauncher after installation. Open Holy Lois periodically to check for updates. Before updating, close Minecraft and its launcher, install the update in Holy Lois, then open your launcher again.

If the SKlauncher entry was deleted or moved, close both Minecraft and SKlauncher and use **Repair / check files** in Holy Lois. It restores the managed files and adds the Holy Lois profile automatically.

Sorting remains available in your inventory. Profile overlays, matching-item hover highlights, slot locking, continuous crafting and failed-replacement alerts are off by default. Tools and armor show quiet remaining/max durability numbers in their tooltips. When a tool breaks, a spare of the same kind from your inventory takes its place, unenchanted and most worn first, with a soft chime. Enchantment descriptions show while you hold Shift over an item.
