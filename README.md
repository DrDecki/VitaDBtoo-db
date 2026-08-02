# VitaDBtoo-db

A community-run rescue of [VitaDB](https://www.rinnegatamante.eu/vitadb), the homebrew
database for PSVITA/PSTV, after the official service went offline on 2026-07-31.

This repository is the catalogue: application metadata, icons and screenshots, served as
static files over GitHub Pages at `https://drdecki.github.io/VitaDBtoo-db/`.

## What survived

The metadata comes from a local client cache (`ux0:data/VitaDB`) captured on **2026-07-31**,
the last state of the database before shutdown. The plugin and PC tool catalogues were
recovered from the Internet Archive. Download links were then resolved individually, either
to the author's GitHub release or to an archived copy of the original file.

Every entry keeps its original curated metadata: name, version, author, description,
changelog, requirements, category, release date and download count. That part cannot be
reconstructed from repositories, which is what makes this catalogue worth keeping.


<!-- STATS -->
| | Entries | With a working download |
| --- | ---: | ---: |
| PSVITA homebrews | 1019 | 930 |
| Plugins | 123 | 62 |
| PSP homebrews | 127 | 21 |
| PC tools | 27 | 14 |
| **Total** | **1296** | **1027 (79%)** |

| Asset | Recovered |
| --- | ---: |
| Metadata | 100% (1296 entries) |
| Icons | 100% (1341) |
| Screenshots | 3% (56 of 2186) |
| Trailers | 3% (2 of 62) |
| Data files | 0% (133 missing) |
| Trophy data | 0% |
<!-- /STATS -->

## Files

| Path | Contents |
| --- | --- |
| `apps.json` | PSVITA homebrews |
| `psp_apps.json` | PSP homebrews |
| `minimal.json` | id, titleid and hashes, for the update daemon |
| `icons/` | app icons, `<sha256>.png` |
| `icons.zip` | all icons as one archive |
| `screenshots/` | recovered screenshots |
| `preserved/plugins.json` | plugin catalogue |
| `preserved/tools.json` | PC tool catalogue |
| `WANTED.md` | entries whose download is still missing |

The plugin and tool catalogues live under `preserved/` because the original client never
listed them; they were separate sections of the VitaDB website. They are kept in the same
schema so a client can consume them the same way.

## Using this catalogue

Every entry carries a direct download URL in its `url` field, so a client does not need a
redirect endpoint. Downloads point either at a GitHub release asset or at an archived copy
on `web.archive.org`; both have been verified on hardware.

If you are writing a client against this, note that download counts are frozen at their
2026-07-31 values. Static hosting cannot count downloads, so sorting by popularity reflects
the state at shutdown and will not change.

Known consumers: [VitaForge](https://github.com/josephinoo) by josephinoo, and
[VitaDBtoo](https://github.com/DrDecki/VitaDBtoo), a fork of the original client.

## What is missing

- **269 downloads**, listed in [WANTED.md](WANTED.md). Contributions welcome.
- **Screenshots**: 56 of roughly 2200 were archived.
- **Trailers and trophy data**: almost nothing was archived.

Themes are unaffected and continue to work: they have always been hosted separately at
[CatoTheYounger97/vitaDB_themes](https://github.com/CatoTheYounger97/vitaDB_themes).

## Maintaining

Adding a homebrew, given a direct URL to its VPK:

```
python3 add_app.py --url <vpk-url> --type port --author "Name" --desc "Short description" \
                   --source https://github.com/... --release-page https://github.com/.../releases
python3 build_db.py
```

`add_app.py` reads the title, title ID, version and icon out of the VPK itself and computes
size and MD5. `build_db.py` regenerates `minimal.json` and `icons.zip` and verifies icon
coverage. Run it after any change to `apps.json`, `psp_apps.json` or `icons/`.

`mkwanted.py` regenerates `WANTED.md`.

## Credits and takedowns

VitaDB was created and run by **Rinnegatamante**. The catalogue is his work and that of
every homebrew author in it; this repository only keeps it reachable.

If you are an author and want your application removed, open an issue and it will be taken
down.
