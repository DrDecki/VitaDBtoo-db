import json, os, re, sys, time, urllib.request, urllib.error

ROOT = os.path.dirname(os.path.abspath(__file__))
TOKEN = os.environ.get('GH_TOKEN', '').strip()
if not TOKEN:
    print('GH_TOKEN not set')
    sys.exit(1)

CACHE = os.path.join(ROOT, 'resolve_cache.json')
cache = json.load(open(CACHE)) if os.path.exists(CACHE) else {}

def api(url):
    req = urllib.request.Request(url, headers={
        'User-Agent': 'vitadbtoo', 'Authorization': 'Bearer ' + TOKEN,
        'Accept': 'application/vnd.github+json'})
    for attempt in range(3):
        try:
            with urllib.request.urlopen(req, timeout=30) as r:
                return json.load(r)
        except urllib.error.HTTPError as e:
            if e.code == 404:
                return None
            time.sleep(10)
        except Exception:
            time.sleep(5)
    return None

for fname in ('plugins.json', 'tools.json'):
    path = os.path.join(ROOT, 'preserved', fname)
    d = json.load(open(path))
    resolved = 0
    mismatch = 0
    gone = 0
    for a in d:
        rp = a.get('release_page') or ''
        m = re.match(r'https?://github\.com/([^/]+)/([^/#?]+)', rp)
        if not m:
            continue
        key = '%s/%s' % (m.group(1), m.group(2).replace('.git', ''))
        if key in cache:
            rel = cache[key]
        else:
            rel = api('https://api.github.com/repos/%s/releases?per_page=30' % key)
            if rel is None:
                gone += 1
                continue
            cache[key] = rel
            time.sleep(0.1)
        want = a.get('size') or ''
        hit = None
        for r in rel:
            for asset in r.get('assets', []):
                if str(asset['size']) == want:
                    hit = asset['browser_download_url']
        if hit:
            a['url'] = hit
            resolved += 1
        else:
            mismatch += 1
    with open(path, 'w') as f:
        json.dump(d, f, indent=4, ensure_ascii=False)
    print('%-14s aufgeloest: %-4d  Groesse abweichend: %-4d  Repo weg: %d' % (fname, resolved, mismatch, gone))

json.dump(cache, open(CACHE, 'w'))
print('fertig')
