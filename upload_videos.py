import os, subprocess, sys

ROOT = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(ROOT, 'videos')
limit = int(sys.argv[1]) if len(sys.argv) > 1 else 999

vorhanden = set(subprocess.run(
    ['gh', 'release', 'view', 'mirror', '--json', 'assets', '--jq', '.assets[].name'],
    cwd=ROOT, capture_output=True, text=True).stdout.split())

todo = []
for f in sorted(os.listdir(SRC)):
    if not f.endswith('.mp4'):
        continue
    asset = 'trailer-' + f.replace(' ', '_')
    if asset not in vorhanden:
        todo.append((f, asset, os.path.getsize(os.path.join(SRC, f))))

print('%d Videos, %.0f MB' % (len(todo), sum(s for _, _, s in todo) / 1048576.0), flush=True)
ok = fail = 0
for i, (f, asset, sz) in enumerate(todo[:limit], 1):
    stage = os.path.join('/tmp', asset)
    try:
        if not os.path.exists(stage):
            os.link(os.path.join(SRC, f), stage)
        subprocess.run(['gh', 'release', 'upload', 'mirror', stage, '--clobber'],
                       cwd=ROOT, check=True, capture_output=True, timeout=3600)
        os.unlink(stage)
        ok += 1
        print('  %2d/%d  %-34s %7.1f MB' % (i, min(len(todo), limit), asset[:34], sz / 1048576.0), flush=True)
    except Exception as e:
        fail += 1
        print('  %2d/%d  %-34s FEHLER %s' % (i, min(len(todo), limit), asset[:34], type(e).__name__), flush=True)

print()
print('hochgeladen: %d, fehlgeschlagen: %d' % (ok, fail))
