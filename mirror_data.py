import hashlib, json, os, re, subprocess, sys, urllib.parse, urllib.request

ROOT = os.path.dirname(os.path.abspath(__file__))
TAG = 'mirror'
BASE = 'https://github.com/DrDecki/VitaDBtoo-db/releases/download/' + TAG + '/'
STATE = os.path.join(ROOT, 'data_state.json')
limit = int(sys.argv[1]) if len(sys.argv) > 1 else 999

done = json.load(open(STATE)) if os.path.exists(STATE) else {}
d = json.load(open(os.path.join(ROOT, 'apps.json'), encoding='utf-8'))

tot = set()
if os.path.exists('/tmp/data_status.txt'):
    for line in open('/tmp/data_status.txt'):
        code, i, _ = line.strip().split('|', 2)
        if not code.startswith('20'):
            tot.add(i)
todo = []
for a in d:
    u = a.get('data') or ''
    if 'rinnegatamante' not in u or a['id'] in done or a['id'] in tot:
        continue
    todo.append(a)
todo.sort(key=lambda x: int(x.get('data_size') or 0))
print('%d Datendateien, %.2f GB' % (len(todo), sum(int(x.get('data_size') or 0) for x in todo) / 1073741824.0), flush=True)

ok = fail = 0
for i, a in enumerate(todo[:limit], 1):
    name = a['data'].rsplit('/', 1)[-1].split('?')[0]
    asset = a['id'] + '-data-' + re.sub(r'[^A-Za-z0-9._-]', '_', urllib.parse.unquote(name))
    stage = os.path.join('/tmp', asset)
    try:
        req = urllib.request.Request(a['data'], headers={'User-Agent': 'vitadbtoo'})
        with urllib.request.urlopen(req, timeout=900) as r:
            blob = r.read()
        if len(blob) < 100:
            raise ValueError('zu klein')
        open(stage, 'wb').write(blob)
        subprocess.run(['gh', 'release', 'upload', TAG, stage, '--clobber'],
                       cwd=ROOT, check=True, capture_output=True, timeout=3600)
        done[a['id']] = {'url': BASE + asset, 'size': str(len(blob)),
                         'hash': hashlib.md5(blob).hexdigest()}
        json.dump(done, open(STATE, 'w'), indent=1)
        os.unlink(stage)
        ok += 1
        print('  %2d/%d  %-26s %8.1f MB' % (i, min(len(todo), limit), a['name'][:26], len(blob) / 1048576.0), flush=True)
    except Exception as e:
        fail += 1
        print('  %2d/%d  %-26s FEHLER %s' % (i, min(len(todo), limit), a['name'][:26], type(e).__name__), flush=True)

print()
print('gespiegelt: %d, fehlgeschlagen: %d' % (ok, fail))
print('apps.json noch NICHT geaendert')
