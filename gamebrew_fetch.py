import json, os, re, subprocess, sys, time, urllib.request

ROOT = os.path.dirname(os.path.abspath(__file__))
WORK = '/tmp/gamebrew'
UA = 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0 Safari/537.36'
REF = 'https://www.gamebrew.org/wiki/Main_Page'

limit = int(sys.argv[1]) if len(sys.argv) > 1 else 999

def load(n):
    return json.load(open(os.path.join(ROOT, n), encoding='utf-8'))

apps = load('apps.json')
gb = load('gamebrew_refs.json')
os.makedirs(WORK, exist_ok=True)

todo = []
for a in apps:
    if 'get_hb_url' not in a['url'] and not a['url'].endswith('.php'):
        continue
    dl = (gb.get(str(a['id'])) or {}).get('dl')
    if dl:
        todo.append((a, dl))

print('%d Kandidaten, Limit %d' % (len(todo), limit))
ok = fail = 0
report = []

for a, dl in todo[:limit]:
    name = dl.rsplit('/', 1)[-1].split('?')[0]
    arc = os.path.join(WORK, name)
    try:
        if not os.path.exists(arc):
            req = urllib.request.Request(dl, headers={'User-Agent': UA, 'Referer': REF})
            with urllib.request.urlopen(req, timeout=300) as r, open(arc, 'wb') as f:
                f.write(r.read())
        out = subprocess.run(['7z', 'l', '-ba', arc], capture_output=True, text=True).stdout
        vpks = [l[53:].strip() for l in out.splitlines() if l[53:].strip().lower().endswith('.vpk')]
        if len(vpks) != 1:
            report.append((a['id'], a['name'], 'vpk-Anzahl %d' % len(vpks), ''))
            fail += 1
            continue
        subprocess.run(['7z', 'e', '-y', '-o' + WORK, arc, vpks[0]], capture_output=True)
        got = os.path.join(WORK, vpks[0].rsplit('/', 1)[-1])
        size = os.path.getsize(got)
        report.append((a['id'], a['name'], 'OK %.1f MB' % (size / 1048576.0), vpks[0]))
        ok += 1
    except Exception as e:
        report.append((a['id'], a['name'], 'FEHLER %s' % type(e).__name__, ''))
        fail += 1
    time.sleep(2)

for i, n, s, v in report:
    print('  %-5s %-28s %-16s %s' % (i, n[:28], s, v[:34]))
print()
print('erfolgreich: %d, fehlgeschlagen: %d' % (ok, fail))
print('VPKs liegen in %s' % WORK)
