"""One-time move of every backup on the VM to Google Drive (owner decision 2026-10-04). Run as root, only after the
owner said "delete" for the local copies.

Each item is uploaded to "gdrive:Holy Lois Backups", checked against Drive's sizes and MD5 hashes, and only then deleted.
Anything that fails to upload or verify stays on the disk. Just Enough Backups keeps its newest full archive and the
newest differential locally, because the next differential is built against them (both are on Drive already).
The terrain job's state folder (/opt/minecraft-backups/terrain-expansion) is not a backup and stays.
"""
import json, subprocess, sys, time
from pathlib import Path

REMOTE = "gdrive:Holy Lois Backups"
BACKUPS = Path("/opt/minecraft-backups")
JEB = Path("/opt/minecraft/backups/world")


def rclone(*args):
    return subprocess.run(["rclone", *args], check=True, capture_output=True, text=True)


def move(local, remote):
    try:
        if local.is_dir():
            rclone("copy", str(local), remote)
            rclone("check", str(local), remote, "--one-way")
        else:
            rclone("copyto", str(local), remote)
            rclone("check", str(local.parent), remote.rsplit("/", 1)[0], "--one-way", "--include", "/" + local.name)
    except subprocess.CalledProcessError as error:
        print(f"KEPT {local}: {error.stderr.strip()[:200]}")
        return 0
    size = sum(f.stat().st_size for f in local.rglob("*") if f.is_file()) if local.is_dir() else local.stat().st_size
    subprocess.run(["rm", "-rf", "--", str(local)], check=True)
    print(f"moved {local} ({size / 1024**3:.2f} GB)")
    return size


def main():
    freed = 0
    for item in sorted((BACKUPS / "maintenance").iterdir()):
        freed += move(item, f"{REMOTE}/maintenance/{item.name}")
    for item in sorted(BACKUPS.iterdir()):
        if item.name not in ("maintenance", "terrain-expansion"):  # terrain-expansion is the terrain job's live state
            freed += move(item, f"{REMOTE}/legacy/{item.name}")
    fulls = sorted(JEB.glob("full-*.zip"), key=lambda p: p.stat().st_mtime)
    diffs = sorted(JEB.glob("differential-*.zip"), key=lambda p: p.stat().st_mtime)
    keep = set(fulls[-1:] + diffs[-1:])
    for item in sorted(JEB.iterdir()):
        # skip archives JEB may still be writing
        if item not in keep and item.is_file() and time.time() - item.stat().st_mtime > 600:
            freed += move(item, f"{REMOTE}/world/{item.name}")
    print(json.dumps({"freed_gb": round(freed / 1024**3, 2), "kept_locally": sorted(p.name for p in keep)}))


if __name__ == "__main__":
    sys.exit(main())
