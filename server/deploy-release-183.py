"""Pack 1.8.3: verified full backup, existing countdown, changed-file rollback and health checks.
Run as root from ~/hl-182; --check validates only. Client-only Auth UI stays out of the server.
"""
from pathlib import Path
from importlib import util
import datetime, hashlib, json, os, re, shutil, subprocess, sys, tarfile

spec=util.spec_from_file_location('previous','/home/ubuntu/hl-174/deploy-release-174.py')
previous=util.module_from_spec(spec);spec.loader.exec_module(previous)
ROOT=Path('/opt/minecraft'); KIT=Path(__file__).resolve().parent
MAINTENANCE=Path('/run/holylois-maintenance')
HEADLINE='<#FFAD42>✦ New:</#FFAD42> <white>Your name, your progress!</white>'
MOTD=ROOT/'config/MiniMOTD/main.conf'
MINIMUM=ROOT/'config/holylois-pack.json'
HIDDEN=ROOT/'config/holylois-stats-hidden.json'
QUIET=ROOT/'config/holylois-quiet.json'
STATS=Path('/usr/local/lib/holylois/make-stats.py')
RULES=ROOT/'config/essentialcommands/rules.txt'
BOT_RULES=Path('/opt/holylois-bot/RULES.md')
def run(*args,**kwargs):return subprocess.run(args,check=True,**kwargs)
def digest(p):return hashlib.sha256(p.read_bytes()).hexdigest()

def main():
    assert os.geteuid()==0,'Run as root'
    manifest=json.loads((KIT/'pack.json').read_text());assert manifest['version']=='1.8.3'
    hashes=json.loads((KIT/'artifact-hashes.json').read_text())
    pairs=[]
    for prefix in ('holylois-extras-','holylois-onboarding-'):
        sources=list(KIT.glob(prefix+'*.jar')); olds=list((ROOT/'mods').glob(prefix+'*.jar'))
        assert len(sources)==len(olds)==1
        source=sources[0]; old=olds[0];assert source.name!=old.name,'Already deployed'
        item=hashes[source.name]
        assert source.stat().st_size==item['size'] and digest(source)==item['sha256']
        if prefix=='holylois-extras-':
            assert next(x for x in manifest['files'] if x['path']=='mods/'+source.name)['sha256']==item['sha256']
        pairs.append((source,old))
    assert not list(KIT.glob('*probe*.jar')),'Test mod must never deploy'
    assert all(p.exists() for p in (MOTD,MINIMUM,STATS,KIT/'make-stats.py',KIT/'holylois-stats-hidden.json'))
    assert shutil.disk_usage(ROOT).free>30*1024**3,'Backup space too low'
    defaults=json.loads((KIT/'holylois-stats-hidden.json').read_text())['names']
    hidden=json.loads(HIDDEN.read_text()) if HIDDEN.exists() else {'names':[]}
    assert isinstance(hidden.get('names'),list)
    hidden['names']=sorted(set(hidden['names'])|set(defaults))
    quiet=json.loads(QUIET.read_text()) if QUIET.exists() else {'names':[]}
    assert isinstance(quiet.get('names'),list)
    quiet['names']=sorted(set(quiet['names'])|set(json.loads((KIT/'holylois-quiet.json').read_text())['names']))
    print('Online players:',previous.online_players(),flush=True)
    if sys.argv[1:]==['--check']:
        print('All pre-checks passed; nothing changed.',flush=True);return
    original=previous.say
    previous.say=lambda text:original(text.replace('land claims on the map, zone titles, /support','private account recovery and launcher setup fixes'))
    try:previous.countdown()
    finally:previous.say=original
    stamp=datetime.datetime.now(datetime.timezone.utc).strftime('%Y%m%dT%H%M%SZ')
    backup=Path('/opt/minecraft-backups/maintenance')/('release183-'+stamp);backup.mkdir(mode=0o700)
    archive=backup/'complete-server.tar'
    saved=[*(old for _,old in pairs),MOTD,MINIMUM,HIDDEN,QUIET,STATS,RULES,BOT_RULES]
    existed={p:p.exists() for p in saved}; installed=[]
    timer_active=subprocess.run(['systemctl','is-active','--quiet','holylois-stats.timer']).returncode==0
    MAINTENANCE.touch()
    try:
        run('systemctl','stop','holylois-stats.timer','holylois-stats.service')
        run('systemctl','stop','minecraft-console.socket','minecraft.service')
        for n,p in enumerate(saved):
            if existed[p]:shutil.copy2(p,backup/f'original-{n}')
        print('Creating fresh complete server backup...',flush=True)
        run('tar','--exclude=minecraft/backups','-cf',str(archive),'-C','/opt','minecraft');archive.chmod(0o600)
        with tarfile.open(archive) as tar:
            members=tar.getmembers();names={m.name for m in members}
            for name in ('minecraft/world/level.dat','minecraft/server.jar','minecraft/config','minecraft/mods','minecraft/EasyAuth'):
                assert name in names,'Missing required backup path'
            assert all(m.offset_data+m.size<=archive.stat().st_size for m in members if m.isfile())
            for n,p in enumerate(saved):
                if existed[p] and p.is_relative_to(ROOT):
                    assert tar.extractfile('minecraft/'+p.relative_to(ROOT).as_posix()).read()==(backup/f'original-{n}').read_bytes(),'Restore-byte mismatch'
        print('Full archive structure, required paths and changed-file restore bytes verified.',flush=True)
        for source,old in pairs:
            target=ROOT/'mods'/source.name
            run('install','-o','minecraft','-g','minecraft','-m','644',str(source),str(target));installed.append(target);old.unlink()
        run('install','-m','755',str(KIT/'make-stats.py'),str(STATS))
        run('install','-o','minecraft','-g','minecraft','-m','644',str(KIT/'rules.txt'),str(RULES))
        run('install','-m','644',str(KIT/'RULES.md'),str(BOT_RULES))
        HIDDEN.write_text(json.dumps(hidden,indent=2)+'\n')
        QUIET.write_text(json.dumps(quiet,indent=2)+'\n')
        MINIMUM.write_text(json.dumps({'minimum':'1.8.3'})+'\n')
        text,count=re.subn(r'(?m)^(\s*line2=).*$',lambda m:m[1]+json.dumps(HEADLINE,ensure_ascii=False),MOTD.read_text(),count=1)
        assert count==1;MOTD.write_text(text)
        run('chown','minecraft:minecraft',str(HIDDEN),str(QUIET),str(MINIMUM),str(MOTD))
        since=datetime.datetime.now(datetime.timezone.utc).isoformat()
        run('systemctl','start','minecraft-console.socket','minecraft.service')
        log=previous.wait_for_start(since)
        for needle in ('holylois-extras 1.6.3','holylois-onboarding 1.8.3','Holy Lois claims: ready for OPAC','holylois_boombox'):
            assert needle in log,'Missing startup marker: '+needle
        assert not any(needle in log for needle in ('Mixin apply failed','Registry loading errors','Failed to start','Encountered an unexpected exception'))
        previous.console('bossbar remove holylois:restart','gamerule send_command_feedback true')
    except BaseException:
        print('Deployment failed. Restoring original add-ons and settings automatically...',flush=True)
        run('systemctl','stop','minecraft-console.socket','minecraft.service')
        for target in installed:target.unlink(missing_ok=True)
        for n,p in enumerate(saved):
            if existed[p] and (backup/f'original-{n}').exists():shutil.copy2(backup/f'original-{n}',p)
            elif not existed[p]:p.unlink(missing_ok=True)
        for p in saved:
            if p.exists() and p.is_relative_to(ROOT):run('chown','minecraft:minecraft',str(p))
        run('systemctl','start','minecraft-console.socket','minecraft.service')
        raise
    finally:
        MAINTENANCE.unlink(missing_ok=True)
        if timer_active:run('systemctl','start','holylois-stats.timer')
    receipt={'result':'Done','pack':'1.8.3','backup':str(archive),'backup_verification':'complete tar structure, required paths, exact changed-file restore bytes',
             'addons':{source.name:digest(ROOT/'mods'/source.name) for source,_ in pairs},'motd':HEADLINE,'pack_minimum':'1.8.3'}
    for destination in (backup/'receipt.json',KIT/'deploy-receipt.json'):destination.write_text(json.dumps(receipt,indent=2)+'\n')
    print(json.dumps(receipt,indent=2),flush=True)

if __name__=='__main__':main()
