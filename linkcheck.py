import json, os, queue, sys, threading, urllib.request

ROOT = os.path.dirname(os.path.abspath(__file__))
WORKERS = 8
q = queue.Queue()
bad, lock = [], threading.Lock()
n = [0]

for f in ('apps.json', 'psp_apps.json', 'preserved/plugins.json', 'preserved/tools.json'):
    for a in json.load(open(os.path.join(ROOT, f), encoding='utf-8')):
        u = a.get('url', '')
        if u and 'get_hb_url' not in u and not u.endswith('.php'):
            q.put((f, a['id'], a['name'], u))

total = q.qsize()
dupes = {}
for f in ('apps.json', 'psp_apps.json', 'preserved/plugins.json', 'preserved/tools.json'):
    for a in json.load(open(os.path.join(ROOT, f), encoding='utf-8')):
        u = a.get('url', '')
        if u and 'get_hb_url' not in u and not u.endswith('.php'):
            t = a.get('titleid') or ''
            if t.strip('A') == '':
                t = ''
            dupes.setdefault(u, []).append((t or '-', a['id'], a['name']))
shared = {u: v for u, v in dupes.items() if len(v) > 1 and len(set(t for t, _, _ in v if t != '-')) > 1}
if shared:
    print()
    print('%d URLs von Eintraegen mit verschiedener titleid geteilt:' % len(shared))
    for u, v in shared.items():
        print('  %s' % u[:74])
        for t, i, nm in v:
            print('     %-10s %-6s %s' % (t, i, nm[:32]))
    print()

print('%d URLs, %d Threads' % (total, WORKERS), flush=True)

def run():
    while True:
        try:
            f, aid, nm, u = q.get_nowait()
        except queue.Empty:
            return
        code = 0
        try:
            r = urllib.request.Request(u, headers={'User-Agent': 'vitadbtoo'})
            r.get_method = lambda: 'HEAD'
            with urllib.request.urlopen(r, timeout=45) as resp:
                code = resp.status
        except Exception as e:
            code = getattr(e, 'code', 0) or type(e).__name__
        with lock:
            n[0] += 1
            if code != 200:
                bad.append((f, aid, nm, u, code))
            if n[0] % 100 == 0:
                print('  %d/%d geprueft, %d auffaellig' % (n[0], total, len(bad)), flush=True)

ts = [threading.Thread(target=run) for _ in range(WORKERS)]
[t.start() for t in ts]
[t.join() for t in ts]

print()
print('auffaellig: %d von %d' % (len(bad), total))
for f, aid, nm, u, c in sorted(bad, key=lambda x: str(x[4])):
    print('  %-6s %-26s %-14s %s' % (aid, nm[:26], c, u[:60]))
json.dump([{'file': f, 'id': i, 'name': nm, 'url': u, 'code': str(c)} for f, i, nm, u, c in bad],
          open(os.path.join(ROOT, 'linkcheck.json'), 'w'), indent=1)
