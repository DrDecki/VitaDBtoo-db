import json, os, re

ROOT = os.path.dirname(os.path.abspath(__file__))

def load(name):
    with open(os.path.join(ROOT, name), 'rb') as f:
        return json.loads(f.read().decode('utf-8', 'replace'))

apps = load('apps.json') + load('psp_apps.json')
all_ids = set(a['id'] for a in apps)
resolved = json.load(open(os.path.join(ROOT, 'resolved.json')))

arch = {}
for line in open('/tmp/cdx_hb.txt'):
    p = line.split()
    if len(p) < 3 or p[2] != '302':
        continue
    m = re.search(r'id=(\d+)', p[0])
    if m:
        arch[m.group(1)] = p[1]

unresolved = all_ids - set(resolved)
targets = unresolved & set(arch)

print('apps total            : %d' % len(all_ids))
print('resolved via GitHub   : %d' % len(resolved))
print('still unresolved      : %d' % len(unresolved))
print('')
print('archived redirects    : %d' % len(arch))
print('  of which unresolved : %d   <- requests needed' % len(targets))
print('  already resolved    : %d' % len(set(arch) & set(resolved)))
print('')
print('apps with no source at all: %d' % len(unresolved - set(arch)))

json.dump({k: arch[k] for k in sorted(targets)}, open(os.path.join(ROOT, 'wayback_targets.json'), 'w'), indent=1)
print('')
print('wayback_targets.json written (%d entries)' % len(targets))