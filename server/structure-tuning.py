"""Link Dungeons and Taverns + Towns and Towers chests to Runeforged tiers and tune village density.

Usage: python structure-tuning.py WORK_DIR, where WORK_DIR/server-mods-161/ holds the structure mod jars.
Outputs (in WORK_DIR/structure-161/):
- runeforged-chest-additions.json: new chest_loot_tables entries (merged into the live config at deploy)
- holylois-structure-tuning/: a world datapack that spaces out the extra village sets
"""
import json, re, sys, zipfile
from pathlib import Path

work = Path(sys.argv[1]) if len(sys.argv) > 1 else Path.cwd()
jars = sorted((work / "server-mods-161").glob("dungeons-and-taverns-*.jar")) + sorted((work / "server-mods-161").glob("t_and_t-*.jar"))
out = work / "structure-161"
out.mkdir(exist_ok=True)

# Best rewards: bosses, treasure rooms, big end/nether/illager strongholds.
T1 = re.compile(r"(treasure|boss|secret|vault|evoker|end_castle|citadel|keep|donjon|manor|monument|sealing|lair|reward|toxic)")
# Common rewards: homes, camps, food, small ruins and village buildings.
T3 = re.compile(r"(village|house|town|kitchen|food|wool|tavern|camp|well|cart|farm|barrel|supply|generic|library|map|witch_hut|hut|fisher|shepherd|tannery|mason|weaponsmith|toolsmith|butcher|cartographer|fletcher|temple_dispenser|remnant)")

def tier(table):
    path = table.split(":", 1)[1]
    if T1.search(path): return "t1"
    if T3.search(path): return "t3"
    return "t2"

entries = {}
for jar in jars:
    with zipfile.ZipFile(jar) as z:
        for name in z.namelist():
            m = re.match(r"data/([^/]+)/loot_table/(chests/.+)\.json$", name)
            if not m or m.group(2).endswith("_base"): continue
            table = f"{m.group(1)}:{m.group(2)}"
            entries[table] = tier(table)

additions = [{"loot_table": t, "tier_id": entries[t]} for t in sorted(entries)]
(out / "runeforged-chest-additions.json").write_text(json.dumps(additions, indent=1) + "\n", encoding="utf-8")
counts = {k: sum(1 for v in entries.values() if v == k) for k in ("t1", "t2", "t3")}
print(len(additions), "chest tables", counts)

# Vanilla villages stay at 34/8. The two extra village sets move from 51 to 68 chunks apart,
# so the world has about 1.5x vanilla village density instead of about 2x.
pack = out / "holylois-structure-tuning"
(pack / "pack.mcmeta").parent.mkdir(parents=True, exist_ok=True)
for jar, ns, set_name in [(jars[0], "nova_structures", "villages"), (jars[1], "t_and_t", "towns")]:
    with zipfile.ZipFile(jar) as z:
        source = [n for n in z.namelist() if n.endswith(f"/worldgen/structure_set/{set_name}.json")]
        assert len(source) == 1, (jar.name, source)
        data = json.loads(z.read(source[0]))
        ns = source[0].split("/")[1]
        data["placement"]["spacing"], data["placement"]["separation"] = 68, 20
        target = pack / "data" / ns / "worldgen" / "structure_set" / f"{set_name}.json"
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")
        print("tuned", source[0], "-> spacing 68 / separation 20")
(pack / "pack.mcmeta").write_text(json.dumps({"pack": {"description": "Holy Lois structure tuning: fewer duplicate villages",
                                                        "min_format": [121, 0], "max_format": [121, 0]}}, indent=2) + "\n",
                                  encoding="utf-8")
for sample in ["nova_structures:chests/illager_manor", "minecraft:chests/illager_mansion/secret_room", "minecraft:chests/village/village_jungle_house"]:
    print(sample, entries.get(sample))
