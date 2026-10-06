"""Apply the reviewed overlay to an isolated copy only. Never deploys or restarts."""
from pathlib import Path
import argparse, re, shutil

p = argparse.ArgumentParser()
p.add_argument('--root', required=True, type=Path)
p.add_argument('--overlay', required=True, type=Path)
args = p.parse_args()
root = args.root.resolve()
if root == Path('/opt/minecraft') or root.is_relative_to(Path('/opt/minecraft')):
    raise SystemExit('Live writes are refused. Prepare in an isolated copy; deploy needs owner approval.')
web = root / 'bluemap/web'
web.mkdir(parents=True, exist_ok=True)
incoming = (args.overlay / 'index.html').read_text()
current = (web / 'index.html').read_text()
entry_assets = lambda text: set(re.findall(r'assets/index-[A-Za-z0-9_-]+\.(?:js|css)', text))
if entry_assets(incoming) != entry_assets(current):
    raise SystemExit('BlueMap frontend version changed; rebuild and review the overlay before applying it.')
shutil.copytree(args.overlay / 'holylois-brand', web / 'holylois-brand', dirs_exist_ok=True)
# Keep all existing scripts and enable the supported hook for future regeneration.
conf = root / 'config/bluemap/webapp.conf'
text = conf.read_text()
hook = 'holylois-brand/branding.js'
if f'"{hook}"' not in text:
    text, count = re.subn(r'(?m)^scripts:\s*\[', f'scripts: [\n  "{hook}",', text, count=1)
    if count != 1: raise SystemExit('Expected one scripts list, review webapp.conf manually.')
    conf.write_text(text)
(web / 'index.html').write_text(incoming)
shutil.copy2(args.overlay / 'assets/logo.png', web / 'assets/logo.png')
if (args.overlay / 'server-icon.png').exists():
    shutil.copy2(args.overlay / 'server-icon.png', root / 'server-icon.png')
    override = root / 'config/MiniMOTD/icons/holy-lois.png'
    if override.exists(): shutil.copy2(args.overlay / 'server-icon.png', override)
print('Isolated branding overlay prepared:', root)
