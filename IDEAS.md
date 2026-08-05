# Ideas and open ends

Notes on what is worth doing next, and on things that were tried and did not work,
so nobody spends an evening rediscovering them.

## A second copy of the mirror

Everything the catalogue serves that authors no longer host themselves lives in one
place: the `mirror` release tag on this repository. That is around 15 GB across 620
assets, tied to a single GitHub account. VitaDB itself disappeared because one host
went away, and this project currently has the same weakness.

A second copy somewhere unrelated would fix it. archive.org is the obvious candidate
but has suspended bulk uploads before, so it cannot be the only answer either.

This matters more than anything else on this page.

## Screenshots

561 of 2186 recovered. The rest were on the old webhost. They are cosmetic, but they
are also the largest remaining gap in the metadata.

## The 26 entries in WANTED.md

Every automatic route has been tried: GitHub releases, the Wayback Machine, and
GameBrew. What is left needs people. Several are itch.io games whose authors are
reachable, and a few of them are in touch with this project already.

`AdrBubbleBooterCreator` v1.3 is a specific case worth writing down: GameBrew has
only v0.7, the author's Google Sites page now demands a login, the GitHub repository
holds source but no build, and the Wayback Machine has nothing. Leecherman himself
is the remaining lead.

## Watching sources

`watch_reddit.py` and `watch_report.py` run daily and open an issue listing new
posts from the subreddits this catalogue watches. No API key and no account are
needed. Posts linking to a repository already in the catalogue are marked and sorted
to the bottom.

The list is deliberately unfiltered beyond that. A model could separate
announcements from support questions, and `watch_judge.py` did exactly that before
it was removed in favour of a plain list; the git history still has it. At forty
posts a day, reading the titles is faster than checking a model's verdict.

Reddit's JSON API and GBAtemp both answer 403 to anything that is not a browser,
and creating a Reddit API application no longer works without going through their
builder policy. The RSS feeds still work without any of that, which is what these
scripts use. They return 429 if called too quickly, hence the pause between
subreddits.

X has no affordable API at all. This is the awkward part, because the idea came from
devnoname120, who announces his own releases there and nowhere else. Posts on X will
keep arriving by hand.

## Download counts are frozen

The `downloads` figures are VitaDB's numbers from 31.07.2026 and will never change.
Static hosting cannot count. Sorting by popularity still works, it just describes the
day the site went down.
