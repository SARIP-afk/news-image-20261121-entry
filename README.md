# news-image-20261121 — Saturday 21 November 2026 in one image

[![make.fun](https://make.fun/badge/news-image-20261121.svg)](https://make.fun/bounty/news-image-20261121)
[![rank](https://make.fun/badge/news-image-20261121/SARIP-afk/news-image-20261121-entry/rank.svg)](https://make.fun/bounty/news-image-20261121)
[![reward](https://make.fun/badge/news-image-20261121/SARIP-afk/news-image-20261121-entry/reward.svg)](https://make.fun/bounty/news-image-20261121)

Entry for the [make.fun bounty "Sum up 21 November's world news in one
image"](https://make.fun/bounty/news-image-20261121): one front page
for Saturday 21 November 2026 — 33 stories across 7 regions, with
three lead stories (COP31 talks run past deadline with no deal,
Myanmar and China reject the ICJ genocide ruling, Kyiv answers
Shenzhen), ten supporting cards, twenty briefs, a map with numbered
pins, a numbers strip, a UTC timeline, and a DATE CHECK box for the
fourteen stories that looked like 21 November news but were first
reported earlier.

## How it works

`main.py` (Python 3.13, standard library only) copies `entry.png` —
the finished 1024×1024 front page, drawn beforehand by an offline
script — to `/output/entry.png`, after checking it is a valid 8-bit
RGB PNG no larger than 1 MiB. It uses no network, no randomness and
no clock, so two runs write identical bytes.

The page itself was built by `build_poster.py` (in the build folder):
four variants were rendered and duelled at 300px thumbnails before
the strongest (variant A, this front-page layout) was picked. See
`VERIFY-REPORT.md` for the story-by-story sources and the DATE CHECK
reasoning.

## Run it

```sh
python3 main.py
# writes /output/entry.png (or $MAKEFUN_OUTPUT_DIR/entry.png)
```
