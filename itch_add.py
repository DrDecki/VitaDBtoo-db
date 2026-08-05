import hashlib, json, os, re, shutil, subprocess

ROOT = os.path.dirname(os.path.abspath(__file__))
DL = os.path.expanduser('~/Downloads')
BASE = 'https://github.com/DrDecki/VitaDBtoo-db/releases/download/mirror/'

paare = {
    '1441': 'imango.vpk',
    '1412': 'Wrecking_Wave.vpk',
    '1099': 'Parkour Labs.vpk',
    '1445': 'Chinese Social Credit Test PSVITA.vpk',
    '1372': 'v0.2.3.1.alpha.vpk',
    '766':  'hexagon.jumper 1.4.1.vpk',
    '1336': 'ABYSS.2.vpk',
}

d = json.load(open(os.path.join(ROOT, 'apps.json'), encoding='utf-8'))
idx = {a['id']: a for a in d}
for aid, fn in paare.items():
    src = os.path.join(DL, fn)
    a = idx.get(aid)
    if not a or not os.path.exists(src):
        print('%-5s FEHLT: %s' % (aid, fn))
        continue
    blob = open(src, 'rb').read()
    if str(len(blob)) != str(a.get('size')):
        print('%-5s %-26s Groesse weicht ab: %s statt %s' % (aid, a['name'][:26], len(blob), a.get('size')))
        continue
    asset = aid + '-' + re.sub(r'[^A-Za-z0-9._-]', '_', os.path.basename(fn))
    stage = os.path.join('/tmp', asset)
    shutil.copy(src, stage)
    subprocess.run(['gh', 'release', 'upload', 'mirror', stage, '--clobber'],
                   cwd=ROOT, check=True, capture_output=True, timeout=1800)
    a['url'] = BASE + asset
    a['hash'] = hashlib.md5(blob).hexdigest()
    os.unlink(stage)
    print('%-5s %-26s %8.1f MB  %s' % (aid, a['name'][:26], len(blob) / 1048576.0, asset))

json.dump(d, open(os.path.join(ROOT, 'apps.json'), 'w', encoding='utf-8'), indent=4, ensure_ascii=False)
print()
print('apps.json aktualisiert')
