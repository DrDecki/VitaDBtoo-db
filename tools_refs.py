import json, os, re, time, urllib.request

ROOT = os.path.dirname(os.path.abspath(__file__))
UA = 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0 Safari/537.36'

seiten = {
    '690': 'Guess_It_Customization_Tool_Vita',
    '317': 'AdrBubbleBooterCreator_Vita',
    '349': 'PSVitaStuff_Vita',
    '346': 'NPS_Browser_Vita',
    '343': 'NoMorePacKaGe_Vita',
    '322': 'Psvtools_Vita',
    '321': 'PkgDecrypt_Vita',
    '318': 'PSVTrimmer_Vita',
    '316': 'Psvimgtools_Vita',
    '314': 'Qcma_Vita',
}

d = {a['id']: a for a in json.load(open(os.path.join(ROOT, 'preserved/tools.json'), encoding='utf-8'))}
gefunden = {}

for aid, slug in seiten.items():
    url = 'https://www.gamebrew.org/wiki/' + slug
    nm = d.get(aid, {}).get('name', '?')
    try:
        req = urllib.request.Request(url, headers={'User-Agent': UA})
        with urllib.request.urlopen(req, timeout=60) as r:
            html = r.read().decode('utf-8', 'replace')
    except Exception as e:
        print('%-5s %-30s SEITE %s' % (aid, nm[:30], getattr(e, 'code', type(e).__name__)))
        time.sleep(2)
        continue
    links = re.findall(r'https://dlhb\.gamebrew\.org/[^"\' <]+', html)
    arch = [l for l in dict.fromkeys(links) if l.split('?')[0].lower().endswith(('.7z', '.zip', '.rar'))]
    if arch:
        gefunden[aid] = {'page': slug.replace('_', ' '), 'dl': arch[0]}
        print('%-5s %-30s %s' % (aid, nm[:30], arch[0].rsplit('/', 1)[-1]))
    else:
        print('%-5s %-30s kein Archiv (%d Links)' % (aid, nm[:30], len(links)))
    time.sleep(2)

print()
print('%d von %d mit Datei' % (len(gefunden), len(seiten)))
json.dump(gefunden, open('/tmp/tools_refs.json', 'w'), indent=1)
