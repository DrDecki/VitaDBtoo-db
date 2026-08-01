import json, os, sys, time, urllib.request, urllib.error

ROOT = os.path.dirname(os.path.abspath(__file__))
CACHE = os.path.join(ROOT, 'wayback_cache.json')
PREFIX = 'https://web.archive.org/web/%sid_/https://www.rinnegatamante.eu/vitadb/get_hb_url.php?id=%s'
EXTS = ('.vpk', '.zip', '.psarc', '.7z', '.rar')

targets = json.load(open(os.path.join(ROOT, 'wayback_targets.json')))
cache = json.load(open(CACHE)) if os.path.exists(CACHE) else {}

def is_good(res):
    if 'error' in res or res.get('code') != 200:
        return False
    return res.get('url', '').lower().endswith(EXTS)

purged = [k for k, v in cache.items() if 'error' in v and v['error'] != 404]
for k in purged:
    del cache[k]
print('purged %d transient failures from cache' % len(purged))

class Head(urllib.request.Request):
    def get_method(self):
        return 'HEAD'

def resolve(app_id, ts):
    req = Head(PREFIX % (ts, app_id), headers={'User-Agent': 'vitadbtoo'})
    for attempt in range(4):
        try:
            with urllib.request.urlopen(req, timeout=60) as r:
                return {'url': r.url, 'size': r.headers.get('Content-Length', ''), 'code': r.status}
        except urllib.error.HTTPError as e:
            if e.code == 404:
                return {'error': 404}
            if attempt < 3:
                time.sleep(10 * (attempt + 1))
                continue
            return {'error': e.code}
        except Exception as e:
            if attempt < 3:
                time.sleep(10 * (attempt + 1))
                continue
            return {'error': str(e)[:50]}
    return {'error': 'giveup'}

todo = [k for k in targets if k not in cache]
print('%d targets, %d cached, %d to fetch' % (len(targets), len(targets) - len(todo), len(todo)))
print('')

ok = bad = 0
for i, app_id in enumerate(todo, 1):
    res = resolve(app_id, targets[app_id])
    cache[app_id] = res
    if is_good(res):
        ok += 1
    else:
        bad += 1
    if i % 20 == 0:
        json.dump(cache, open(CACHE, 'w'))
        print('  %d/%d   ok=%d  failed=%d' % (i, len(todo), ok, bad))
    time.sleep(1.0)

json.dump(cache, open(CACHE, 'w'))

good, fail = {}, []
for app_id, res in cache.items():
    if is_good(res):
        good[app_id] = {'url': res['url'], 'size': res.get('size', ''), 'via': 'wayback'}
    else:
        fail.append('%s  %s' % (app_id, res.get('error', res.get('url', 'no url')[:90])))

json.dump(good, open(os.path.join(ROOT, 'wayback_resolved.json'), 'w'), indent=1)
open(os.path.join(ROOT, 'wayback_report.txt'), 'w').write('\n'.join(sorted(fail)) + '\n')

print('')
print('resolved : %d' % len(good))
print('failed   : %d' % len(fail))
