import json, os, re, sys, time, urllib.request, urllib.error

ROOT = os.path.dirname(os.path.abspath(__file__))
TOKEN = os.environ.get('GH_TOKEN', '').strip()
if not TOKEN:
    print('GH_TOKEN not set'); sys.exit(1)

CACHE = os.path.join(ROOT, 'resolve_cache.json')
cache = json.load(open(CACHE)) if os.path.exists(CACHE) else {}
EXT = ('.vpk', '.suprx', '.skprx', '.zip', '.7z', '.rar', '.exe')

def api(url):
    req = urllib.request.Request(url, headers={'User-Agent': 'vitadbtoo',
        'Authorization': 'Bearer ' + TOKEN, 'Accept': 'application/vnd.github+json'})
    for a in range(3):
        try:
            with urllib.request.urlopen(req, timeout=30) as r:
                return json.load(r)
        except urllib.error.HTTPError as e:
            if e.code == 404: return None
            time.sleep(8)
        except Exception:
            time.sleep(5)
    return None

def repo_of(a):
    for field in ('release_page', 'source'):
        m = re.match(r'https?://github\.com/([^/]+)/([^/#?]+)', a.get(field) or '')
        if m:
            return '%s/%s' % (m.group(1), m.group(2).replace('.git', ''))
    return None

for fname in ('apps.json', 'psp_apps.json', 'preserved/plugins.json', 'preserved/tools.json'):
    path = os.path.join(ROOT, fname)
    d = json.load(open(path))
    by_size = by_latest = 0
    for a in d:
        if 'get_hb_url.php' not in a['url']:
            continue
        key = repo_of(a)
        if not key:
            continue
        if key in cache:
            rel = cache[key]
        else:
            rel = api('https://api.github.com/repos/%s/releases?per_page=30' % key)
            if rel is None:
                continue
            cache[key] = rel
            time.sleep(0.1)
        want = a.get('size') or ''
        exact = None
        newest = None
        for r in rel:
            for asset in r.get('assets', []):
                nm = asset['name'].lower()
                if not nm.endswith(EXT):
                    continue
                if str(asset['size']) == want:
                    exact = asset['browser_download_url']
                if newest is None:
                    newest = (asset['browser_download_url'], str(asset['size']))
        if exact:
            a['url'] = exact
            by_size += 1
        elif newest:
            a['url'] = newest[0]
            a['size'] = newest[1]
            by_latest += 1
    with open(path, 'w') as f:
        json.dump(d, f, indent=4, ensure_ascii=False)
    print('%-26s exakt: %-4d neuestes Asset: %-4d' % (fname, by_size, by_latest))

json.dump(cache, open(CACHE, 'w'))
print('fertig')
