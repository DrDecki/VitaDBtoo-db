# VitaDBtoo-db

Static backend for [VitaDBtoo](https://github.com/DrDecki/VitaDBtoo), a community-run
continuation of the VitaDB homebrew store for PsVita/PSTV after the official service
went offline.

Served via GitHub Pages at `https://drdecki.github.io/VitaDBtoo-db/`.

## Data provenance

The metadata in this repository is a snapshot of the official VitaDB database taken
from a local client cache (`ux0:data/VitaDB`) on **2026-07-31**, the last state before
the service shut down.

- `apps.json` — 1019 PsVita homebrews
- `psp_apps.json` — 127 PSP homebrews
- `icons/` — 1341 app icons, full coverage of both databases

## Endpoint mapping

The original backend was PHP-based. Since VitaDBtoo is a fork of the client, the
query-parameter endpoints are patched out rather than emulated.

| Original | Replacement |
| --- | --- |
| `list_hbs_json.php` | `apps.json` |
| `list_psp_hbs_json.php` | `psp_apps.json` |
| `list_minimal_hbs_json.php` | `minimal.json` |
| `icons_zip.php` | `icons.zip` |
| `icons/<hash>.png` | `icons/<hash>.png` |
| `get_hb_url.php?id=X` | `url` field, read directly from the app entry |
| `get_psarc_url.php?id=X` | `data` field, read directly from the app entry |
| `get_page.php?id=X&type=src\|rel` | `source` / `release_page` fields |

Themes are unaffected: they have always been hosted separately at
[CatoTheYounger97/vitaDB_themes](https://github.com/CatoTheYounger97/vitaDB_themes)
and continue to work without changes.

## Icon layout

Two layouts are required and both are generated from `icons/`:

- `icons/<hash>.png` — flat, for single-icon fetches
- `icons.zip` — grouped into two-character subdirectories (`<hash[:2]>/<hash>.png`),
  because the client extracts the archive into `ux0:data/VitaDB/icons/` and then reads
  from `icons/<2 chars>/<hash>.png`

## Not yet available

- **Screenshots** (815 apps) and **trailers** (62 apps) were hosted on the original
  webhost and are not part of the cache snapshot.
- **Download hosting.** The `url` fields still point at the dead `get_hb_url.php`
  endpoint. 473 of 1019 apps carry a GitHub `release_page`, which can be resolved to
  the upstream release asset; the remaining 546 need another source.

## Rebuilding

After changing `apps.json`, `psp_apps.json` or `icons/`:

```
python3 build_db.py
```

This regenerates `minimal.json` and `icons.zip` and verifies icon coverage.

## Licensing

App metadata and icons are the work of the individual homebrew authors listed in the
database. This repository redistributes them to keep the store usable; takedown
requests from any author will be honoured.
