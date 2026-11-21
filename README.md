# news-image-20261121 — Saturday 21 November 2026 in one image

[![make.fun](https://make.fun/badge/news-image-20261121.svg)](https://make.fun/bounty/news-image-20261121)
[![rank](https://make.fun/badge/news-image-20261121/SARIP-afk/news-image-20261121-entry/rank.svg)](https://make.fun/bounty/news-image-20261121)
[![reward](https://make.fun/badge/news-image-20261121/SARIP-afk/news-image-20261121-entry/reward.svg)](https://make.fun/bounty/news-image-20261121)

Entry for the [make.fun bounty "Sum up 21 November's world news in one
image"](https://make.fun/bounty/news-image-20261121): one front page
for Saturday 21 November 2026 — 42 stories across 7 regions, with
three lead stories (COP31 overtime, three Houthi missiles shot down
over Riyadh, the 6.7 Peru quake), twelve supporting cards, twenty-seven
briefs, a navy map with numbered pins, a giant numbers strip, and a
six-item DATE CHECK box for the stories that looked like 21 November
news but were first reported earlier.

v2 replaces v1 (33 stories, kept as `v1-entry.png` for comparison):
new heroes 2–3 and card 4 fix v1's selection miss (the Riyadh
interception, the Peru quake and the Kryvyi Rih double-tap were
missing from v1), the numbers strip is now six giant verified figures,
every hero and card carries a giant colour-block banner, scenes are
saturated and high-contrast, the map is navy, and the DATE CHECK is
cut from fourteen items to six. See `VERIFY-REPORT.md` for the
story-by-story sources and the DATE CHECK reasoning.

## How it works

`main.py` (Python 3.13, standard library only) copies `entry.png` —
the finished 1024×1024 front page, drawn beforehand by an offline
script — to `/output/entry.png`, after checking it is a valid 8-bit
RGB PNG no larger than 1 MiB. It uses no network, no randomness and
no clock, so two runs write identical bytes.

The page itself was built by `build_v2.py` (in this repo, PIL only;
`main.py` stays pure stdlib): it renders the 1024×1024 front page
from the story data in the script — masthead, numbers strip, three
heroes, twelve cards, navy map, briefs and DATE CHECK — after the
v2 diagnosis in `../news-image-20261121-diagnosis.md`. See
`VERIFY-REPORT.md` for the story-by-story sources and the DATE CHECK
reasoning.

## Run it

```sh
python3 main.py
# writes /output/entry.png (or $MAKEFUN_OUTPUT_DIR/entry.png)
```
