import os, sys, time, urllib.request

ROOT = os.path.dirname(os.path.abspath(__file__))
DEST = os.path.join(ROOT, 'videos')
BASE = 'https://www.rinnegatamante.eu/vitadb/videos/'
MAXMB = float(sys.argv[1]) if len(sys.argv) > 1 else 30.0

todo = []
for line in open('/tmp/tr_size.txt'):
    sz, name = line.split(None, 1)
    name = name.strip()
    sz = int(sz)
    if 0 < sz <= MAXMB * 1048576 and not os.path.exists(os.path.join(DEST, name + '.mp4')):
        todo.append((sz, name))
todo.sort()
print('%d Trailer bis %.0f MB, zusammen %.0f MB' % (len(todo), MAXMB, sum(s for s, _ in todo) / 1048576.0), flush=True)

ok = fail = 0
geladen = 0
for i, (sz, name) in enumerate(todo, 1):
    try:
        req = urllib.request.Request(BASE + name + '.mp4', headers={'User-Agent': 'vitadbtoo'})
        with urllib.request.urlopen(req, timeout=300) as r:
            blob = r.read()
        if len(blob) < 10000:
            raise ValueError('zu klein')
        with open(os.path.join(DEST, name + '.mp4'), 'wb') as g:
            g.write(blob)
        ok += 1
        geladen += len(blob)
        print('  %2d/%d  %-22s %6.1f MB' % (i, len(todo), name[:22], len(blob) / 1048576.0), flush=True)
    except Exception as e:
        fail += 1
        print('  %2d/%d  %-22s FEHLER %s' % (i, len(todo), name[:22], type(e).__name__), flush=True)
    time.sleep(1)

print()
print('geladen: %d, fehlgeschlagen: %d, %.0f MB' % (ok, fail, geladen / 1048576.0))
