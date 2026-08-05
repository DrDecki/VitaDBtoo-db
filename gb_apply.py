import json, os, shutil, sys

ROOT = os.path.dirname(os.path.abspath(__file__))
dry = '--write' not in sys.argv
done = json.load(open(os.path.join(ROOT, 'gb_state.json'), encoding='utf-8'))

byfile = {}
for aid, v in done.items():
    byfile.setdefault(v['file'], {})[aid] = v

for fname, mapping in byfile.items():
    p = os.path.join(ROOT, fname)
    d = json.load(open(p, encoding='utf-8'))
    n = 0
    for a in d:
        v = mapping.get(str(a['id']))
        if not v:
            continue
        if 'get_hb_url' not in a['url'] and not a['url'].endswith('.php'):
            print('  UEBERSPRUNGEN %s %s: URL ist nicht mehr offen' % (a['id'], a['name'][:24]))
            continue
        a['url'], a['size'], a['hash'] = v['url'], v['size'], v['hash']
        n += 1
    print('%-26s %3d von %3d Eintraegen umgestellt' % (fname, n, len(mapping)))
    if not dry:
        shutil.copy(p, p + '.bak')
        with open(p, 'w', encoding='utf-8') as f:
            json.dump(d, f, indent=4, ensure_ascii=False)

print()
print('Probelauf, nichts geschrieben' if dry else 'geschrieben, Sicherungen liegen als .bak daneben')
