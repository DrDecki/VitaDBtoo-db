import json, os, re, sys, time, urllib.parse, urllib.request

ROOT = os.path.dirname(os.path.abspath(__file__))
SUBS = ('vitahacks', 'VitaPiracy', 'vitahacksdev')
UA = 'VitaDBtoo/0.1 by DrDecki (github.com/DrDecki/VitaDBtoo-db)'
SEEN = os.path.join(ROOT, 'watch_seen.json')

cid = os.environ.get('REDDIT_ID')
sec = os.environ.get('REDDIT_SECRET')
if not cid or not sec:
    print('REDDIT_ID und REDDIT_SECRET fehlen, nichts zu tun')
    sys.exit(0)

def token():
    data = urllib.parse.urlencode({'grant_type': 'client_credentials'}).encode()
    req = urllib.request.Request('https://www.reddit.com/api/v1/access_token', data=data,
                                 headers={'User-Agent': UA})
    import base64
    auth = base64.b64encode(('%s:%s' % (cid, sec)).encode()).decode()
    req.add_header('Authorization', 'Basic ' + auth)
    with urllib.request.urlopen(req, timeout=60) as r:
        return json.load(r)['access_token']

def get(url, tok):
    req = urllib.request.Request(url, headers={'User-Agent': UA, 'Authorization': 'Bearer ' + tok})
    with urllib.request.urlopen(req, timeout=60) as r:
        return json.load(r)

seen = set(json.load(open(SEEN))) if os.path.exists(SEEN) else set()
namen = set()
for f in ('apps.json', 'psp_apps.json', 'preserved/plugins.json', 'preserved/tools.json'):
    for a in json.load(open(os.path.join(ROOT, f), encoding='utf-8')):
        namen.add(re.sub(r'[^a-z0-9]', '', a['name'].lower()))

tok = token()
kandidaten = []
for sub in SUBS:
    try:
        d = get('https://oauth.reddit.com/r/%s/new?limit=50' % sub, tok)
    except Exception as e:
        print('r/%s: %s' % (sub, getattr(e, 'code', type(e).__name__)))
        continue
    posts = d.get('data', {}).get('children', [])
    neu = 0
    for p in posts:
        x = p['data']
        if x['id'] in seen:
            continue
        seen.add(x['id'])
        neu += 1
        txt = (x.get('title', '') + ' ' + (x.get('selftext') or ''))[:1500]
        slug = re.sub(r'[^a-z0-9]', '', x.get('title', '').lower())
        bekannt = any(n and len(n) > 4 and n in slug for n in namen)
        kandidaten.append({'id': x['id'], 'sub': sub, 'title': x.get('title', ''),
                           'url': 'https://reddit.com' + x.get('permalink', ''),
                           'link': x.get('url_overridden_by_dest') or '',
                           'text': txt, 'im_katalog': bekannt})
    print('r/%-14s %d neue von %d' % (sub, neu, len(posts)))
    time.sleep(2)

json.dump(sorted(seen), open(SEEN, 'w'))
json.dump(kandidaten, open(os.path.join(ROOT, 'watch_new.json'), 'w'), indent=1, ensure_ascii=False)
print()
print('%d neue Beitraege, davon %d zu bereits katalogisierten Homebrews'
      % (len(kandidaten), sum(1 for k in kandidaten if k['im_katalog'])))
