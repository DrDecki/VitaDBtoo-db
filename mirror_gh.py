import hashlib, json, os, queue, re, subprocess, sys, threading, time, urllib.parse, urllib.request

ROOT = os.path.dirname(os.path.abspath(__file__))
TAG = 'mirror'
BASE = 'https://github.com/DrDecki/VitaDBtoo-db/releases/download/' + TAG + '/'
TMP = '/tmp/gh_stage'
os.makedirs(TMP, exist_ok=True)

LIMIT = int(sys.argv[1]) * 1048576 if len(sys.argv) > 1 else 10 ** 12
WORKERS = int(sys.argv[2]) if len(sys.argv) > 2 else 6
lock = threading.Lock()
STATE = os.path.join(ROOT, 'mirror_state.json')
done = json.load(open(STATE)) if os.path.exists(STATE) else {}

files = ('apps.json', 'psp_apps.json', 'preserved/plugins.json', 'preserved/tools.json')

todo = []
for fname in files:
    with open(os.path.join(ROOT, fname), 'rb') as f:
        d = json.loads(f.read().decode('utf-8', 'replace'))
    for a in d:
        u = a.get('url', '')
        risky = 'web.archive.org' in u or ('rinnegatamante.eu/files' in u)
        if risky and int(a.get('size') or 0) < LIMIT:
            todo.append((fname, a['id'], a['name'], a['url'], int(a.get('size') or 0)))
todo.sort(key=lambda x: x[4])
print('%d Dateien, %.2f GB' % (len(todo), sum(x[4] for x in todo) / 1073741824.0), flush=True)

cnt = {'ok': 0, 'fail': 0, 'n': 0}
work = queue.Queue()
for t in todo:
    if t[1] not in done:
        work.put(t)
total = work.qsize()
print('%d offen, %d Threads' % (total, WORKERS), flush=True)

def worker():
  while True:
    try:
        fname, aid, nm, url, sz = work.get_nowait()
    except queue.Empty:
        return
    m = re.search(r'files/vitadb/(.+)$', url)
    orig = m.group(1).split('/')[-1] if m else aid + '.vpk'
    safe = re.sub(r'[^A-Za-z0-9._-]', '_', orig)
    asset = aid + '-' + safe
    path = os.path.join(TMP, asset)
    try:
        safe_url = urllib.parse.quote(url, safe=':/?&=%')
        req = urllib.request.Request(safe_url, headers={'User-Agent': 'vitadbtoo'})
        with urllib.request.urlopen(req, timeout=600) as r:
            blob = r.read()
        if len(blob) < 1000:
            raise ValueError('too small')
        with open(path, 'wb') as fh:
            fh.write(blob)
        lock.acquire()
        subprocess.run(['gh', 'release', 'upload', TAG, path, '--clobber'],
                       cwd=ROOT, check=True, capture_output=True, timeout=900)
        done[aid] = {'url': BASE + asset, 'size': str(len(blob)),
                     'hash': hashlib.md5(blob).hexdigest()}
        lock.release()
        os.unlink(path)
        cnt['ok'] += 1
        cnt['n'] += 1
        print('  %4d/%d  %-30s %7.1f MB' % (cnt['n'], total, nm[:30], len(blob) / 1048576.0), flush=True)
    except Exception as e:
        if lock.locked():
            lock.release()
        cnt['fail'] += 1
        cnt['n'] += 1
        print('  %4d/%d  FEHLER %-24s %s' % (cnt['n'], total, nm[:24], str(e)[:45]), flush=True)
        if os.path.exists(path):
            os.unlink(path)
    work.task_done()
    if cnt['n'] % 10 == 0:
        json.dump(done, open(STATE, 'w'), indent=1)

ths = [threading.Thread(target=worker, daemon=True) for _ in range(WORKERS)]
for t in ths:
    t.start()
for t in ths:
    t.join()

json.dump(done, open(STATE, 'w'), indent=1)

for fname in files:
    p = os.path.join(ROOT, fname)
    with open(p, 'rb') as f:
        d = json.loads(f.read().decode('utf-8', 'replace'))
    n = 0
    for a in d:
        v = done.get(a['id'])
        if v and ('web.archive.org' in a.get('url','') or 'rinnegatamante.eu/files' in a.get('url','')):
            a['url'], a['size'], a['hash'] = v['url'], v['size'], v['hash']
            n += 1
    if n:
        with open(p, 'w', encoding='utf-8') as f:
            json.dump(d, f, indent=4, ensure_ascii=False)
        print('%s: %d Eintraege umgestellt' % (fname, n))

print('---')
print('gespiegelt: %d, fehlgeschlagen: %d' % (cnt['ok'], cnt['fail']))
