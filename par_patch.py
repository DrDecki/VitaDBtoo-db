import re

p = 'mirror_gh.py'
s = open(p, encoding='utf-8').read()

s = s.replace('import hashlib, json, os, re, subprocess, sys, time, urllib.request',
              'import hashlib, json, os, queue, re, subprocess, sys, threading, time, urllib.request', 1)

s = s.replace("STATE = os.path.join(ROOT, 'mirror_state.json')",
              "WORKERS = int(sys.argv[2]) if len(sys.argv) > 2 else 6\nlock = threading.Lock()\nSTATE = os.path.join(ROOT, 'mirror_state.json')", 1)

old1 = "ok = fail = 0\nfor i, (fname, aid, nm, url, sz) in enumerate(todo, 1):\n    if aid in done:\n        continue"
new1 = """cnt = {'ok': 0, 'fail': 0, 'n': 0}
work = queue.Queue()
for t in todo:
    if t[1] not in done:
        work.put(t)
total = work.qsize()
print('%d offen, %d Threads' % (total, WORKERS), flush=True)

def worker():
  while True:
    try:
        fname, aid, nm, url, sz = work.get_nowait()
    except queue.Empty:
        return"""
assert s.count(old1) == 1, 'Schleifenanfang'
s = s.replace(old1, new1, 1)

old2 = """        open(path, 'wb').write(blob)
        subprocess.run(['gh', 'release', 'upload', TAG, path, '--clobber'],
                       cwd=ROOT, check=True, capture_output=True, timeout=900)
        done[aid] = {'url': BASE + asset, 'size': str(len(blob)),
                     'hash': hashlib.md5(blob).hexdigest()}
        os.unlink(path)
        ok += 1
        print('  %4d/%d  %-30s %7.1f MB' % (i, len(todo), nm[:30], len(blob) / 1048576.0), flush=True)
    except Exception as e:
        fail += 1
        print('  %4d/%d  FEHLER %-24s %s' % (i, len(todo), nm[:24], str(e)[:45]), flush=True)
        if os.path.exists(path):
            os.unlink(path)
    if i % 10 == 0:
        json.dump(done, open(STATE, 'w'), indent=1)
    time.sleep(0.5)"""
new2 = """        with open(path, 'wb') as fh:
            fh.write(blob)
        with lock:
            subprocess.run(['gh', 'release', 'upload', TAG, path, '--clobber'],
                           cwd=ROOT, check=True, capture_output=True, timeout=1800)
            done[aid] = {'url': BASE + asset, 'size': str(len(blob)),
                         'hash': hashlib.md5(blob).hexdigest()}
            cnt['ok'