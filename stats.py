import json, os, re, zipfile

ROOT = os.path.dirname(os.path.abspath(__file__))
ORIG = os.path.expanduser('~/Downloads/VitaDB.zip')

def load(n):
    with open(os.path.join(ROOT, n), 'rb') as f:
        return json.loads(f.read().decode('utf-8', 'replace'))

def live(a):
    return 'get_hb_url' not in a.get('url', '')

cats = [('PSVITA homebrews', 'apps.json'), ('Plugins', 'preserved/plugins.json'),
        ('PSP homebrews', 'psp_apps.json'), ('PC tools', 'preserved/tools.json')]

rows, tot, ok = [], 0, 0
for label, f in cats:
    d = load(f)
    n = sum(1 for a in d if live(a))
    rows.append((label, len(d), n))
    tot += len(d)
    ok += n

icons = len([x for x in os.listdir(os.path.join(ROOT, 'icons')) if x.endswith('.png')])
need = set()
for f in ('apps.json', 'psp_apps.json'):
    for a in load(f):
        if a.get('icon'):
            need.add(a['icon'])

ss_have = len([x for x in os.listdir(os.path.join(ROOT, 'screenshots'))
               if x.endswith('.png')]) if os.path.isdir(os.path.join(ROOT, 'screenshots')) else 0
tr_have = len([x for x in os.listdir(os.path.join(ROOT, 'videos'))
               if x.endswith('.mp4')]) if os.path.isdir(os.path.join(ROOT, 'videos')) else 0

ss_total = tr_total = 0
if os.path.exists(ORIG):
    z = zipfile.ZipFile(ORIG)
    orig = json.loads(z.read('VitaDB/apps.json').decode('utf-8', 'replace'))
    ss_total = len(set(m for a in orig for m in re.findall(r'[0-9a-f]{64}\.png', a.get('screenshots') or '')))
    tr_total = sum(1 for a in orig if a.get('trailer'))

data_missing = sum(1 for a in load('apps.json') if a.get('data') and 'rinnegatamante' in a['data'])

out = ['<!-- STATS -->\n']
out.append('| | Entries | With a working download |\n| --- | ---: | ---: |\n')
for label, n, k in rows:
    out.append('| %s | %d | %d |\n' % (label, n, k))
out.append('| **Total** | **%d** | **%d (%.0f%%)** |\n\n' % (tot, ok, 100.0 * ok / tot))
out.append('| Asset | Recovered |\n| --- | ---: |\n')
out.append('| Metadata | 100%% (%d entries) |\n' % tot)
out.append('| Icons | %.0f%% (%d) |\n' % (100.0 * len(need & set(os.listdir(os.path.join(ROOT, 'icons')))) / max(len(need), 1), icons))
if ss_total:
    out.append('| Screenshots | %.0f%% (%d of %d) |\n' % (100.0 * ss_have / ss_total, ss_have, ss_total))
if tr_total:
    out.append('| Trailers | %.0f%% (%d of %d) |\n' % (100.0 * tr_have / tr_total, tr_have, tr_total))
out.append('| Data files | 0%% (%d missing) |\n' % data_missing)
out.append('| Trophy data | 0% |\n')
out.append('<!-- /STATS -->')

readme = os.path.join(ROOT, 'README.md')
s = open(readme, encoding='utf-8').read()
block = ''.join(out)
if '<!-- STATS -->' in s:
    s = re.sub(r'<!-- STATS -->.*?<!-- /STATS -->', block, s, flags=re.S)
else:
    s = s.replace('## Files', block + '\n\n## Files', 1)
open(readme, 'w', encoding='utf-8').write(s)
print('README aktualisiert: %d von %d installierbar (%.0f%%)' % (ok, tot, 100.0 * ok / tot))
