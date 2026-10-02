# Playing Holy Lois: Reborn

For pack 1.5.4 and launcher 1.1.0. Start with the [download and setup steps](README.md#download-and-play), then select **Holy Lois: Reborn** in Minecraft Launcher or SKlauncher. The server is already saved in Multiplayer.

## Joining

Offline accounts see a centered registration or login form. Register with a server password of at least five characters, without spaces. Use a separate password from your Minecraft account. Your login is remembered for **24 hours on the same IP**. Verified premium accounts skip the form.

On your first registration, wait for the arrival screen to finish while the server finds a safe starting location. You can press Escape to leave if needed.

## Voice and controls

| Key | Action |
| --- | --- |
| **V** | Choose your microphone, output device and voice settings. |
| **Hold Caps Lock** | Talk to nearby players. |
| **Page Down** | Show or hide your body in first person. |

If your body clips through the view, press **Page Down** to use the simpler view while keeping animated arms. Shaders start off; choose a supplied shader in Minecraft's video settings when ready. **Disable shaders** in Holy Lois is available if rendering causes trouble.

## Homes

Use a name such as `base` for a saved location. Replace it with your own home name.

| Command | What it does |
| --- | --- |
| `/home set base` | Save your current location. |
| `/home tp base` | Return to that location. |
| `/home list` | Show your saved homes. |
| `/home delete base` | Remove that saved home. |

These are the pack's [Essential Commands home commands](https://github.com/John-Paul-R/Essential-Commands#commands).

## Teleporting

Replace `NAME` with the player's name.

| Command | What it does |
| --- | --- |
| `/tpa NAME` | Ask to visit a player. |
| `/tpaccept NAME` | Accept that player's request. |
| `/tpdeny NAME` | Decline that player's request. |
| `/rtp` | Find a safe new place. The server uses a five-minute cooldown. |

The request and random-teleport commands come from [Essential Commands](https://github.com/John-Paul-R/Essential-Commands#commands). `/rtp` stays within the server's prepared area.

## Protect your land

1. Hold a **golden hoe**.
2. Right-click a block at one corner of your land, then another block at the opposite corner.
3. Check the server's confirmation that the claim was created.
4. Stand inside your claim and use `/flan menu` to manage permissions and access for friends.

See Flan's official [claiming guide](https://github.com/Flemmli97/BlazingDocs/blob/main/docs/flan/user_guides/Getting-Started.md) and [menu command](https://github.com/Flemmli97/BlazingDocs/blob/main/docs/flan/user_guides/Commands.md).

## Make a shop

Craft a **Trade Shop** with **4 planks, 1 wool and 1 iron ingot**. Put the ingredients in these two rows of a crafting table:

| Plank | Wool | Plank |
| --- | --- | --- |
| Plank | Iron ingot | Plank |

Place the Trade Shop against the **top or side of a chest**. Its settings open so you can choose what you sell and what buyers pay. Fill the chest with your stock. Buyers click the shop and select the offered item. The official [Universal Shops guide](https://github.com/Patbox/UniversalShops#using-trade-shops) explains the item and price settings.

## After death

Your dropped items stay protected for your own pickup for **30 minutes of loaded-world time**. Time does not advance while the area is unloaded. Recover them promptly: **fire, lava and the void can still destroy items**. This protection does not make drops indestructible.

## Keep your pack updated

You can launch the saved pack directly from Minecraft Launcher or SKlauncher after installation. Open Holy Lois periodically to check for updates. Before updating, close Minecraft and its launcher, install the update in Holy Lois, then open your launcher again.

If the SKlauncher entry was deleted or moved, close both Minecraft and SKlauncher and use **Repair / check files** in Holy Lois. It restores the managed files and adds the Holy Lois profile automatically.

Sorting remains available in your inventory. Profile overlays, matching-item hover highlights, slot locking, continuous crafting and failed-replacement alerts are off by default. Tools and armor show quiet remaining/max durability numbers in their tooltips.
