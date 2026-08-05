import json, os, subprocess, time, urllib.request, collections

ROOT = os.path.dirname(os.path.abspath(__file__))
WORK = '/tmp/gbsurvey'
UA = 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0 Safari/537.36'
REF = 'https://www.gamebrew.org/wiki/Main_Page'
os.makedirs(WORK, exist_ok=True)

gb = json.load(open(os.path.join(ROOT, 'gamebrew_refs.json'), encoding='utf-8'))

def offen(f):
    d = json.load(open(os.path.join(ROOT, f), encoding='utf-8'))
    return [a for a in d if ('get_hb_url' in a['url'] or a['url'].endswith('.php'))
            and (gb.get(str(a['id'])) or {}).get('dl')]

def klasse(names):
    low = [n.lower() for n in names]
    has = lambda e: any(n.endswith(e) for n in low)
    if has('.skprx') or has('.suprx'):
        return 'Plugin direkt'
    if any('eboot.pbp' in n for n in low):
        return 'PSP Ordner'
    if has('.vpk'):
        return 'VPK'
    if has('.zip') or has('.7z') or has('.rar'):
        return 'nur Archive (verschachtelt)'
    return 'unklar'

rows = []
for f in ('preserved/plugins.json', 'psp_apps.json'):
    for a in offen(f):
        dl = gb[str(a['id'])]['dl']
        fn = os.path.join(WORK, dl.rsplit('/', 1)[-1].split('?')[0])
        try:
            if not os.path.exists(fn):
                req = urllib.request.Request(dl, headers={'User-Agent': UA, 'Referer': REF})
                with urllib.request.urlopen(req, timeout=180) as r, open(fn, 'wb') as g:
                    g.write(r.read())
                time.sleep(2)
            out = subprocess.run(['7z', 'l', '-ba', fn], capture_output=True, text=True).stdout
            names = [l[53:].strip() for l in out.splitlines() if l[53:].strip()]
            names = [n for n in names if n.lower() != 'gamebrew.url']
            rows.append((f.split('/')[-1][:7], a['id'], a['name'], klasse(names), names))
        except Exception as e:
            rows.append((f.split('/')[-1][:7], a['id'], a['name'], 'FEHLER %s' % type(e).__name__, []))

for t, i, n, k, names in rows:
    print('%-7s %-5s %-26s %-28s %s' % (t, i, n[:26], k, ', '.join(names[:3])[:46]))
print()
c = collections.Counter(r[3] for r in rows)
for k, v in c.most_common():
    print('  %-30s %3d' % (k, v))
json.dump([{'typ': t, 'id': i, 'name': n, 'klasse': k, 'inhalt': names} for t, i, n, k, names in rows],
          open(os.path.join(WORK, 'survey.json'), 'w'), indent=1)
