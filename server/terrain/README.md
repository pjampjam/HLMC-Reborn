# Terrain expansion job

Pregenerates the whole Overworld inside the world border (20,000 wide, so a radius-10,000 square around 0,0) with Chunky 1.5.3, then raises `/rtp` and first-join placement to 5,000 blocks.

- `expand-terrain.py` runs one short step per timer tick. It generates only while no players are online and at least 6 GB is free, and pauses Chunky as soon as someone joins.
- RTP changes only after Chunky reports natural completion of the job's own task **and** all 1,565,001 chunks in the square are stored with matching coordinates and `Status=full`. MCA files or headers alone are never treated as proof.
- Any unexpected state blocks the job and disables its timer. It never trims or deletes terrain.
- `test-expand-terrain.py` holds 21 synthetic tests. It never touches a real server.

## Install (server stopped)

1. Archive any existing `config/chunky/tasks/minecraft/overworld.properties` and old `/opt/minecraft-backups/terrain-expansion/job.json`.
2. Copy `expand-terrain.py` to `/usr/local/lib/holylois/` and the `.service`/`.timer` units to `/etc/systemd/system/`.
3. Start Minecraft, then `systemctl daemon-reload` and `systemctl enable --now holylois-terrain-expansion.timer`.

Check progress with `sudo journalctl -u holylois-terrain-expansion -n 20 --no-pager` and `sudo cat /opt/minecraft-backups/terrain-expansion/job.json`.
