import json, os, threading, queue, time, urllib.request, urllib.error

ROOT = os.path.dirname(os.path.abspath(__file__))
CACHE = os.path.join(ROOT, 'wayback_cache.json')
PREFIX = 'https://web.archive.org/web/%sid_/https://www.rinnegatamante.eu/vitadb/get_hb_url.php?id=%s'
EXTS = ('.vpk', '.zip', '.psarc', '.7z', '.rar')
WORKERS = 3

targets = json.load(open(os.path.join(ROOT, 'wayback_targets.json')))
cache = json.load(open(CACHE)) if os.path.exists(CACHE) else {}

def is_good(res):
    return 'error' not in res and res.get('code') == 200 and res.get('url', '').lower().endswith(EXTS)

purged = [k for k, v in cache.items() if 'error' in v and v['error'] != 404]
for k in purged:
    del cache[k]
print('purged %d transient failures' % len(purged))

class Head(urllib.request.Request):
    def get_method(self):
        return 'HEAD'

lock = threading.Lock()
q = queue.Queue()
done = [0]
todo = [k for k in targets if k not in cache]
for k in todo:
    q.put(k)

def worker():
    while True:
        try:
            app_id = q.get_nowait()
        except queue.Empty:
            return
        req = Head(PREFIX % (targets[app_id], app_id), headers={'User-Agent': 'vitadbtoo'})
        res = {'error': 'giveup'}
        for attempt in range(3):
            try:
                with urllib.request.urlopen(req, timeout=90) as r:
                    res = {'url': r.url, 'size': r.headers.get('Content-Length', ''), 'code': r.status}
                    break
            except urllib.error.HTTPError as e:
                if e.code == 404:
                    res = {'error': 404}
                    break
                res = {'error': e.code}
            except Exception as e:
                res = {'error': str(e)[:50]}
            time.sleep(5 * (attempt + 1))
        with lock:
            cache[app_id] = res
            done[0] += 1
            if done[0] % 20 == 0:
                json.dump(cache, open(CACHE, 'w'))
                ok = sum(1 for v in cache.values() if is_good(v))
                print('  %d/%d done   total ok=%d' % (done[0], len(todo), ok), flush=True)
        q.task_done()

print('%d targets, %d cached, %d to fetch with %d workers' % (len(targets), len(targets) - len(todo), len(todo), WORKERS))
print('')
start = time.time()
threads = [threading.Thread(target=worker, daemon=True) for _ in range(WORKERS)]
for t in threads:
    t.start()
for t in threads:
    t.join()

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
print('elapsed  : %d min' % ((time.time() - start) / 60))
print('resolved : %d' % len(good))
print('failed   : %d' % len(fail))