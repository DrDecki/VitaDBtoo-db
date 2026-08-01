import json, os

ROOT = os.path.dirname(os.path.abspath(__file__))

def load(name):
    with open(os.path.join(ROOT, name), 'rb') as f:
        return json.loads(f.read().decode('utf-8', 'replace'))

res = {}
for name, tag in (('resolved.json', 'github'), ('wayback_resolved.json', 'wayback')):
    p = os.path.join(ROOT, name)
    if os.path.exists(p):
        d = json.load(open(p))
        for k, v in d.items():
            res.setdefault(k, v)
        print('loaded %s: %d entries' % (name, len(d)))

stats = {'url': 0, 'size': 0, 'skipped': 0}
for fname in ('apps.json', 'psp_apps.json'):
    apps = load(fname)
    for a in apps:
        r = res.get(a.get('id'))
        if not r:
            stats['skipped'] += 1
            continue
        a['url'] = r['url']
        stats['url'] += 1
        newsize = str(r.get('size') or '')
        if newsize and newsize.isdigit() and newsize != a.get('size'):
            a['size'] = newsize
            stats['size'] += 1
    with open(os.path.join(ROOT, fname), 'w') as f:
        json.dump(apps, f, indent=4, ensure_ascii=False)
    print('wrote %s (%d apps)' % (fname, len(apps)))

print('')
print('urls set      : %d' % stats['url'])
print('sizes updated : %d' % stats['size'])
print('left untouched: %d' % stats['skipped'])

raw = open(os.path.join(ROOT, 'apps.json'), encoding='utf-8').read()
checks = ['"name": "', '"url": "', '"data": "', '"hash": "', '"titleid": "']
print('')
for c in checks:
    print('parser format %-16s %s' % (c.strip(), 'OK' if c in raw else 'BROKEN'))
