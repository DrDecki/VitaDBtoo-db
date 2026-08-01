import json, os, collections

ROOT = os.path.dirname(os.path.abspath(__file__))

def load(name):
    with open(os.path.join(ROOT, name), 'rb') as f:
        return json.loads(f.read().decode('utf-8', 'replace'))

apps = load('apps.json') + load('psp_apps.json')
by_size = collections.defaultdict(list)
for a in apps:
    if a.get('size'):
        by_size[a['size']].append(a)

files = []
for line in open('/tmp/cdx_files.txt'):
    p = line.split()
    if len(p) >= 4 and p[2] == '200':
        files.append({'url': p[0], 'ts': p[1], 'len': p[3]})

print('archived files: %d' % len(files))
exact = sum(1 for f in files if f['len'] in by_size)
print('with an exactly matching app size: %d' % exact)
print('')
for f in files[:8]:
    hit = by_size.get(f['len'])
    print('%-58s len=%-11s %s' % (f['url'].split('/')[-1][:58], f['len'],
                                  hit[0]['name'][:30] if hit else '-'))
