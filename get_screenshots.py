import os, sys, time, urllib.request

ROOT = os.path.dirname(os.path.abspath(__file__))
DEST = os.path.join(ROOT, 'screenshots')
BASE = 'https://www.rinnegatamante.eu/vitadb/screenshots/'
limit = int(sys.argv[1]) if len(sys.argv) > 1 else 99999

fehlt = [l.strip() for l in open('/tmp/ss_fehlt.txt') if l.strip()]
todo = [f for f in fehlt if not os.path.exists(os.path.join(DEST, f))]
print('%d fehlen, %d noch zu laden, Limit %d' % (len(fehlt), len(todo), limit), flush=True)

ok = fail = 0
bytes_total = 0
t0 = time.time()
for i, f in enumerate(todo[:limit], 1):
    try:
        req = urllib.request.Request(BASE + f, headers={'User-Agent': 'vitadbtoo'})
        with urllib.request.urlopen(req, timeout=120) as r:
            blob = r.read()
        if len(blob) < 100:
            raise ValueError('zu klein')
        with open(os.path.join(DEST, f), 'wb') as g:
            g.write(blob)
        ok += 1
        bytes_total += len(blob)
    except Exception as e:
        fail += 1
        print('  FEHLER %s %s' % (f[:16], type(e).__name__), flush=True)
    if i % 50 == 0:
        el = time.time() - t0
        print('  %d/%d  %.0f MB  %.0f s' % (i, min(len(todo), limit), bytes_total / 1048576.0, el), flush=True)
    time.sleep(0.3)

print()
print('geladen: %d, fehlgeschlagen: %d, %.0f MB' % (ok, fail, bytes_total / 1048576.0))
