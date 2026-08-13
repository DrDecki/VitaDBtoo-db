import hashlib, json, os, re, subprocess, sys

ROOT = os.path.dirname(os.path.abspath(__file__))
TAG = 'mirror'
BASE = 'https://github.com/DrDecki/VitaHomebrewDB/releases/download/' + TAG + '/'
VPKS = '/tmp/gamebrew'
ARCS = '/tmp/gbsurvey'
TOOLS = '/tmp/gbtools'
limit = int(sys.argv[1]) if len(sys.argv) > 1 else 999

gb = json.load(open(os.path.join(ROOT, 'gamebrew_refs.json'), encoding='utf-8'))
STATE = os.path.join(ROOT, 'gb_state.json')
done = json.load(open(STATE)) if os.path.exists(STATE) else {}

plan = []
for fname, folder, want_vpk in (('apps.json', VPKS, True),
                                ('preserved/plugins.json', ARCS, False),
                                ('psp_apps.json', ARCS, False),
                                ('preserved/tools.json', TOOLS, False)):
    d = json.load(open(os.path.join(ROOT, fname), encoding='utf-8'))
    for a in d:
        if 'get_hb_url' not in a['url'] and not a['url'].endswith('.php'):
            continue
        dl = (gb.get(str(a['id'])) or {}).get('dl')
        if not dl or str(a['id']) in done:
            continue
        if want_vpk:
            src = None
            arc = os.path.join(VPKS, dl.rsplit('/', 1)[-1].split('?')[0])
            if os.path.exists(arc):
                out = subprocess.run(['7z', 'l', '-ba', arc], capture_output=True, text=True).stdout
                v = [l[53:].strip() for l in out.splitlines() if l[53:].strip().lower().endswith('.vpk')]
                if len(v) == 1:
                    cand = os.path.join(VPKS, v[0].rsplit('/', 1)[-1])
                    if os.path.exists(cand):
                        src = cand
        else:
            src = os.path.join(folder, dl.rsplit('/', 1)[-1].split('?')[0])
            if not os.path.exists(src):
                src = None
        if src:
            plan.append((fname, str(a['id']), a['name'], src))

print('%d Dateien zum Hochladen, Limit %d' % (len(plan), limit), flush=True)
ok = fail = 0
for i, (fname, aid, nm, src) in enumerate(plan[:limit], 1):
    asset = aid + '-' + re.sub(r'[^A-Za-z0-9._-]', '_', os.path.basename(src))
    stage = os.path.join('/tmp', asset)
    try:
        blob = open(src, 'rb').read()
        open(stage, 'wb').write(blob)
        subprocess.run(['gh', 'release', 'upload', TAG, stage, '--clobber'],
                       cwd=ROOT, check=True, capture_output=True, timeout=900)
        done[aid] = {'url': BASE + asset, 'size': str(len(blob)),
                     'hash': hashlib.md5(blob).hexdigest(), 'file': fname}
        json.dump(done, open(STATE, 'w'), indent=1)
        os.unlink(stage)
        ok += 1
        print('  %3d/%d  %-28s %8.1f MB' % (i, min(len(plan), limit), nm[:28], len(blob) / 1048576.0), flush=True)
    except Exception as e:
        fail += 1
        print('  %3d/%d  %-28s FEHLER %s' % (i, min(len(plan), limit), nm[:28], type(e).__name__), flush=True)

print()
print('hochgeladen: %d, fehlgeschlagen: %d' % (ok, fail))
print('Zustand in gb_state.json, apps.json noch NICHT geaendert')
