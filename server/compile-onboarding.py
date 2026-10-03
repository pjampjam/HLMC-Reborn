"""Compile holylois-onboarding from /home/ubuntu/holylois-build-140 against the live server classpath (read-only)."""
import hashlib, json, pathlib, subprocess, zipfile
r = pathlib.Path('/opt/minecraft'); w = pathlib.Path('/home/ubuntu/holylois-build-140')
lib = w/'lib'; lib.mkdir(exist_ok=True)
jars = list((r/'libraries').rglob('*.jar')) + list((r/'versions').rglob('*.jar')) + list((r/'mods').glob('*.jar'))
seen = set()
def nested(p):
    with zipfile.ZipFile(p) as z:
        for n in z.namelist():
            if n.endswith('.jar') and n.startswith('META-INF/jars/'):
                data = z.read(n); h = hashlib.sha256(data).hexdigest(); out = lib/(h + '.jar')
                if h in seen: continue
                seen.add(h); out.write_bytes(data); jars.append(out); nested(out)
for p in list(jars): nested(p)
cp = ':'.join(map(str, jars)); java = '/usr/lib/jvm/java-25-openjdk-arm64/bin/java'
classes = w/'classes'
subprocess.run(['rm', '-rf', str(classes)], check=True); classes.mkdir()
sources = sorted(w.glob('*.java'))
subprocess.run([java, '-m', 'jdk.compiler/com.sun.tools.javac.Main', '-proc:none', '-Xlint:-options', '-source', '25', '-target', '25',
                '-cp', cp, '-d', str(classes), *map(str, sources)], check=True)
subprocess.run([java, '-cp', str(classes) + ':' + cp, 'holylois.OnboardingTest'], check=True)
meta = json.loads((w/'fabric.mod.json').read_text())
out = w/f"holylois-onboarding-{meta['version']}+26.3.jar"
with zipfile.ZipFile(out, 'w', zipfile.ZIP_DEFLATED) as z:
    z.writestr('fabric.mod.json', json.dumps(meta, indent=2))
    z.write(w/'holylois-onboarding.mixins.json', 'holylois-onboarding.mixins.json')
    z.write(w/'holylois-quotes.txt', 'holylois-quotes.txt')
    z.write(w/'holylois-namedays-lv.txt', 'holylois-namedays-lv.txt')
    for p in sorted(classes.rglob('*.class')):
        if p.name.startswith('OnboardingTest'): continue
        z.write(p, p.relative_to(classes).as_posix())
    for p in sources:
        if p.name != 'OnboardingTest.java': z.write(p, 'src/' + p.name)
print(json.dumps({'jar': str(out), 'sha256': hashlib.sha256(out.read_bytes()).hexdigest(), 'size': out.stat().st_size}))
