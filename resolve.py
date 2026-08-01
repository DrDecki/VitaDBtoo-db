import json, os, re, sys, time, urllib.request, urllib.error

ROOT = os.path.dirname(os.path.abspath(__file__))
TOKEN = os.environ.get('GH_TOKEN', '').strip()
CACHE = os.path.join(ROOT, 'resolve_cache.json')

if not TOKEN:
    print('GH_TOKEN not set')
    sys.exit(1)

cache = {}
if os.path.exists(CACHE):
    cache = json.load(open(CACHE))

def api(url):
    req = urllib.request.Request(url, headers={
        'User-Agent': 'vitadbtoo',
        'Authorization': 'Bearer ' + TOKEN,
        'Accept': 'application/vnd.github+json'})
    for attempt in range(3):
        try:
            with urllib.request.urlopen(req, timeout=30) as r:
                return json.load(r), int(r.headers.get('X-RateLimit-Remaining', '9999'))
        except urllib.error.HTTPError as e:
            if e.code == 403 and attempt < 2:
                time.sleep(20)
                continue
            return None, -1
        except Exception:
            if attempt < 2:
                time.sleep(5)
                continue
            return None, -1
    return None, -1

def load(name):
    with open(os.path.join(ROOT, name), 'rb') as f:
        return json.loads(f.read().decode('utf-8', 'replace'))

apps = load('apps.json') + load('psp_apps.json')
targets = []
for a in apps:
    rp = a.get('release_page') or ''
    m = re.match(r'https?://github\.com/([^/]+)/([^/#?]+)', rp)
    if m:
        targets.append((a, m.group(1), m.group(2).replace('.git', '')))

print('%d apps with a GitHub release page' % len(targets))

resolved = {}
stats = {'size': 0, 'mismatch': 0, 'norelease': 0, 'error': 0}
report = []

for i, (a, owner, repo) in enumerate(targets, 1):
    key = '%s/%s' % (owner, repo)
    if key in cache:
        rel = cache[key]
    else:
        rel, remaining = api('https://api.github.com/repos/%s/%s/releases?per_page=30' % (owner, repo))
        if rel is None:
            stats['error'] += 1
            report.append('ERROR    %-40s %s' % (a['name'][:40], key))
            continue
        cache[key] = rel
        if i % 25 == 0:
            json.dump(cache, open(CACHE, 'w'))
            print('  %d/%d  (rate limit remaining: %s)' % (i, len(targets), remaining))
        time.sleep(0.1)

    if not rel:
        stats['norelease'] += 1
        report.append('NOREL    %-40s %s' % (a['name'][:40], key))
        continue

    want = a.get('size') or ''
    hits = []
    for r in rel:
        for asset in r.get('assets', []):
            if str(asset['size']) == want:
                hits.append((r['tag_name'], asset['name'], asset['browser_download_url']))
    if hits:
        vpk = [h for h in hits if h[1].lower().endswith('.vpk')]
        pick = (vpk or hits)[0]
        resolved[a['id']] = {'url': pick[2], 'tag': pick[0], 'asset': pick[1], 'via': 'size'}
        stats['size'] += 1
    else:
        stats['mismatch'] += 1
        latest = rel[0]['tag_name'] if rel else '?'
        report.append('MISMATCH %-40s %s (latest tag %s)' % (a['name'][:40], key, latest))

json.dump(cache, open(CACHE, 'w'))
json.dump(resolved, open(os.path.join(ROOT, 'resolved.json'), 'w'), indent=1)

print('')
print('exact size match : %d' % stats['size'])
print('size mismatch    : %d' % stats['mismatch'])
print('no releases      : %d' % stats['norelease'])
print('api errors       : %d' % stats['error'])
print('')
print('resolved.json written with %d entries' % len(resolved))
with open(os.path.join(ROOT, 'resolve_report.txt'), 'w') as f:
    f.write('\n'.join(report) + '\n')
print('unresolved detail in resolve_report.txt')
