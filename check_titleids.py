import io, json, os, struct, sys, time, urllib.request, zipfile

ROOT = os.path.dirname(os.path.abspath(__file__))
IDS = '15 25 303 639 640 641 657 658 737 738 1083 1121 1169 1279 17 33 83 162 177 224 292 310 379 458 557 782 834 1155 1049 1159 1274 1280 1397'.split()

def sfo(buf):
    magic, ver, kt, dt, n = struct.unpack_from('<4sIIII', buf, 0)
    out = {}
    for i in range(n):
        ko, fmt, dlen, dmax, do = struct.unpack_from('<HHIII', buf, 20 + i * 16)
        k = buf[kt + ko:buf.index(b'\0', kt + ko)].decode()
        v = buf[dt + do:dt + do + dlen]
        if fmt == 0x0204:
            out[k] = v.rstrip(b'\0').decode('utf-8', 'replace')
    return out

d = {a['id']: a for a in json.load(open(os.path.join(ROOT, 'apps.json'), encoding='utf-8'))}
abw, gleich, fehler = [], 0, 0
for i in IDS:
    a = d.get(i)
    if not a:
        continue
    try:
        req = urllib.request.Request(a['url'], headers={'User-Agent': 'vitadbtoo'})
        with urllib.request.urlopen(req, timeout=600) as r:
            blob = r.read()
        z = zipfile.ZipFile(io.BytesIO(blob))
        p = sfo(z.read('sce_sys/param.sfo'))
        echt = p.get('TITLE_ID', '?')
        if echt != a.get('titleid'):
            abw.append((i, a['name'], a.get('titleid'), echt))
            print('  %-5s %-28s %s -> %s' % (i, a['name'][:28], a.get('titleid'), echt), flush=True)
        else:
            gleich += 1
    except Exception as e:
        fehler += 1
        print('  %-5s %-28s FEHLER %s' % (i, a['name'][:28], type(e).__name__), flush=True)
    time.sleep(0.5)

json.dump([{'id': i, 'name': n, 'alt': o, 'neu': e} for i, n, o, e in abw],
          open('/tmp/tid_pruefung.json', 'w'), indent=1, ensure_ascii=False)
print()
print('%d abweichend, %d korrekt, %d Fehler' % (len(abw), gleich, fehler))
