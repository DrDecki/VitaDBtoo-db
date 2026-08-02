import json, re, os

ROOT = os.path.dirname(os.path.abspath(__file__))

def load(n):
    with open(os.path.join(ROOT, n), 'rb') as f:
        return json.loads(f.read().decode('utf-8', 'replace'))

used = set()
apps = load('apps.json')
for a in apps:
    m = re.search(r'files/vitadb/(.+)$', a['url'])
    if m:
        used.add(m.group(1))

arch = []
p = '/tmp/cdx_len.txt'
if os.path.exists(p):
    for line in open(p):
        q = line.split()
        if len(q) >= 3 and q[2] == '200':
            m = re.search(r'files/vitadb/(.+)$', q[0])
            if m and m.group(1) not in used:
                arch.append(m.group(1))

rows = []
for fname, label in (('apps.json', 'Vita'), ('psp_apps.json', 'PSP'),
                     ('preserved/plugins.json', 'Plugin'), ('preserved/tools.json', 'Tool')):
    for a in load(fname):
        if 'get_hb_url' in a['url']:
            src = a.get('release_page') or a.get('source') or ''
            rows.append((label, a['name'], a['version'], a['author'], a['size'], src))

out = []
out.append('# Wanted: missing downloads\n')
out.append('These %d entries survive in the catalogue with full metadata, but their download\n' % len(rows))
out.append('link died with the VitaDB webhost and could not be recovered automatically.\n\n')
out.append('If you have one of these files, or know where it lives now, please open an issue\n')
out.append('or a pull request. What is needed is a stable direct URL to the exact file.\n\n')
out.append('The file size below is the one VitaDB recorded, which makes it easy to confirm a\n')
out.append('candidate is the right build.\n\n')
out.append('| Type | Name | Version | Author | Size | Known source |\n')
out.append('| --- | --- | --- | --- | ---: | --- |\n')
for t, n, v, au, sz, src in sorted(rows):
    size = '%.1f MB' % (int(sz) / 1048576.0) if sz and sz.isdigit() else '?'
    link = '[link](%s)' % src if src else '-'
    out.append('| %s | %s | %s | %s | %s | %s |\n' % (t, n.replace('|', ''), v, au.replace('|', ''), size, link))

if arch:
    out.append('\n## Unmatched archived files\n\n')
    out.append('The Internet Archive holds %d further files from the old webhost that could not\n' % len(arch))
    out.append('be matched to an entry above. Filenames rarely match the display name, so this\n')
    out.append('needs someone who recognises them.\n\n```\n')
    for f in sorted(arch):
        out.append(f + '\n')
    out.append('```\n')

open(os.path.join(ROOT, 'WANTED.md'), 'w').write(''.join(out))
print('WANTED.md: %d fehlende Eintraege, %d unzugeordnete Archivdateien' % (len(rows), len(arch)))
