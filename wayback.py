import json, os, sys, time, urllib.request, urllib.error

ROOT = os.path.dirname(os.path.abspath(__file__))
CACHE = os.path.join(ROOT, 'wayback_cache.json')
PREFIX = 'https://web.archive.org/web/%sid_/https://www.rinnegatamante.eu/vitadb/get_hb_url.php?id=%s'

targets = json.load(open(os.path.join(ROOT, 'wayback_targets.json')))
cache = {}
if os.path.exists(CACHE):
    cache = json.load(open(CACHE))

class Head(urllib.request.Request):
    def get_method(self):
        return 'HEAD'

def resolve(app_id, ts):
    req = Head(PREFIX % (ts, app_id), headers={'User-Agent': 'vitadbtoo'})
    for attempt in range(3):
        try:
            with urllib.request.urlopen(req, timeout=60) as r:
                return {'url': r.url, 'size': r.headers.get('Content-Length', ''),
                        'code': r.status}
        except urllib.error.HTTPError as e:
            if e.code in (429, 503, 504) and attempt < 2:
                time.sleep(15)
                continue
            return {'error': e.code}
        except Exception as e:
            if attempt < 2:
                time.sleep(8)
                continue
            return {'error': str(e)[:60]}
    return {'error': 'giveup'}

todo = [k for k in targets if k not in cache]
print('%d targets, %d already cached, %d to fetch' % (len(targets), len(targets) - len(todo), len(todo)))
print('')

ok = bad = 0
for i, app_id in enumerate(todo, 1):
    res = resolve(app_id, targets[app_id])
    cache[app_id] = res
    if 'error' in res or not res.get('url', '').endswith(('.vpk', '.zip', '.psarc', '.VPK')):
        bad += 1
    else:
        ok += 1
    if i % 20 == 0:
        json.dump(cache, open(CACHE, 'w'))
        print('  %d/%d   ok=%d  failed=%d' % (i, len(todo), ok, bad))
    time.sleep(0.3)

json.dump(cache, open(CACHE, 'w'))

good = {}
fail = []
for app_id, res in cache.items():
    u = res.get('url', '')
    if 'error' not in res and res.get('code') == 200 and '/files/vitadb' in u:
        good[app_id] = {'url': u, 'size': res.get('size', ''), 'via': 'wayback'}
    else:
        fail.append('%s  %s' % (app_id, res.get('error', u[:90] or 'no url')))

json.dump(good, open(os.path.join(ROOT, 'wayback_resolved.json'), 'w'), indent=1)
with open(os.path.join(ROOT, 'wayback_report.txt'), 'w') as f:
    f.write('\n'.join(sorted(fail)) + '\n')

print('')
print('resolved : %d' % len(good))
print('failed   : %d' % len(fail))
print('wayback_resolved.json + wayback_report.txt written')
