import json, os, sys, urllib.request

ROOT = os.path.dirname(os.path.abspath(__file__))
NEW = os.path.join(ROOT, 'watch_new.json')
key = os.environ.get('ANTHROPIC_API_KEY')

if not os.path.exists(NEW):
    print('keine watch_new.json, nichts zu bewerten')
    sys.exit(0)
kand = json.load(open(NEW, encoding='utf-8'))
kand = [k for k in kand if not k['im_katalog']]
if not kand:
    print('keine unbekannten Beitraege')
    sys.exit(0)
if not key:
    print('ANTHROPIC_API_KEY fehlt, %d Beitraege bleiben unbewertet' % len(kand))
    sys.exit(0)

SYS = ('You screen Reddit posts for a PSVITA homebrew catalogue. For each post decide whether it '
       'announces a downloadable PSVITA or PSP homebrew, plugin, or tool release. Ignore questions, '
       'help requests, piracy discussion, and hardware talk. Reply with a JSON array only, no prose, '
       'one object per post: {"i": index, "release": true|false, "name": "", "author": "", '
       '"link": "", "why": "short reason"}. Leave fields empty when unknown.')

items = [{'i': n, 'title': k['title'], 'link': k['link'], 'text': k['text'][:700]}
         for n, k in enumerate(kand)]

req = urllib.request.Request(
    'https://api.anthropic.com/v1/messages',
    data=json.dumps({'model': 'claude-sonnet-4-6', 'max_tokens': 4000, 'system': SYS,
                     'messages': [{'role': 'user', 'content': json.dumps(items, ensure_ascii=False)}]}).encode(),
    headers={'Content-Type': 'application/json', 'x-api-key': key,
             'anthropic-version': '2023-06-01'})
with urllib.request.urlopen(req, timeout=180) as r:
    resp = json.load(r)

txt = ''.join(b.get('text', '') for b in resp.get('content', []) if b.get('type') == 'text')
txt = txt.replace('```json', '').replace('```', '').strip()
try:
    urteile = json.loads(txt)
except Exception:
    print('Antwort nicht lesbar:')
    print(txt[:600])
    sys.exit(1)

treffer = []
for u in urteile:
    if not u.get('release'):
        continue
    k = kand[u['i']]
    treffer.append({**u, 'post': k['url'], 'sub': k['sub'], 'title': k['title']})

if not treffer:
    print('%d Beitraege geprueft, keine Veroeffentlichung' % len(kand))
    sys.exit(0)

lines = ['Possible new homebrew found while watching Reddit.', '']
for t in treffer:
    lines.append('- **%s** by %s' % (t.get('name') or t['title'][:50], t.get('author') or 'unknown'))
    lines.append('  - post: %s (r/%s)' % (t['post'], t['sub']))
    if t.get('link'):
        lines.append('  - link: %s' % t['link'])
    lines.append('  - %s' % t.get('why', ''))
lines.append('')
lines.append('Verify before adding anything to the catalogue.')
open(os.path.join(ROOT, 'watch_issue.md'), 'w', encoding='utf-8').write('\n'.join(lines))
print('%d moegliche Veroeffentlichungen von %d Beitraegen' % (len(treffer), len(kand)))
