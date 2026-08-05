import html, json, os, re, time, urllib.request

ROOT = os.path.dirname(os.path.abspath(__file__))
SUBS = ('vitahacks', 'VitaPiracy')
UA = 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0 Safari/537.36'
SEEN = os.path.join(ROOT, 'watch_seen.json')
EIGENE = ('vitadbtoo', 'drdecki.github.io')
# Hilfe-Anfragen beginnen fast immer so. Nur der Titelanfang wird geprueft,
# weil Ankuendigungstexte weiter unten oft selbst um Rueckmeldung bitten.
FRAGEN = ('help', 'how do i', 'how to', 'how can i', 'is there a way', 'anyone know',
          'does anyone', 'can someone', 'can anyone', 'need help', 'looking for',
          'why is', 'why does', 'what is the best', 'question', 'issue with',
          'problem with', 'trouble with')

seen = set(json.load(open(SEEN))) if os.path.exists(SEEN) else set()

def entries(xml):
    for block in re.findall(r'<entry>(.*?)</entry>', xml, re.S):
        g = lambda p: (re.search(p, block, re.S) or [None, ''])[1]
        yield {
            'id': html.unescape(g(r'<id>([^<]+)</id>')),
            'title': html.unescape(g(r'<title>([^<]*)</title>')).strip(),
            'url': html.unescape(g(r'<link[^>]*href="([^"]+)"')),
            'text': re.sub(r'<[^>]+>', ' ', html.unescape(g(r'<content[^>]*>(.*?)</content>')))[:1200],
        }

kandidaten = []
for sub in SUBS:
    try:
        req = urllib.request.Request('https://www.reddit.com/r/%s/new/.rss?limit=50' % sub,
                                     headers={'User-Agent': UA})
        with urllib.request.urlopen(req, timeout=60) as r:
            xml = r.read().decode('utf-8', 'replace')
    except Exception as e:
        print('r/%-14s %s' % (sub, getattr(e, 'code', type(e).__name__)))
        continue
    alle = list(entries(xml))
    neu = 0
    for e in alle:
        if not e['id'] or e['id'] in seen:
            continue
        seen.add(e['id'])
        neu += 1
        e['sub'] = sub
        low = (e['title'] + ' ' + e['text']).lower()
        titel = e['title'].lower().lstrip('[( ')
        frage = titel.startswith(FRAGEN) or e['title'].rstrip().endswith('?')
        eigen = any(w in low for w in EIGENE)
        e['uebersprungen'] = 'eigenes Projekt' if eigen else ('Frage' if frage else '')
        kandidaten.append(e)
    print('r/%-14s %d neue von %d' % (sub, neu, len(alle)))
    time.sleep(15)

json.dump(sorted(seen), open(SEEN, 'w'))
json.dump(kandidaten, open(os.path.join(ROOT, 'watch_new.json'), 'w'), indent=1, ensure_ascii=False)
print()
uebrig = [k for k in kandidaten if not k['uebersprungen']]
print('%d neue Beitraege, %d nach dem Vorfilter' % (len(kandidaten), len(uebrig)))
