# Verification notes — news-image-20261121 v4 POLISH round

Polish round on top of v4 (HEAD 8925396, sha `b3cebc94…59bb`),
fixing the four small items in VERIFY-REPORT-V4.md "What is still
not perfect". No rebuild from scratch, no layout change, no
story/data change. No push, no submit — local commit only.

## Coordinator independent verification (not builder's claims)

Re-run by the coordinator itself, 21 Nov ~12:15 WIB:

- **Determinism — PASS:** `build_v4.py` run twice in sequence,
  both runs printed sha256
  `5bf9215b3cf9e4ef85e2cdb1a052ba6f77a89d415180474243d7d92c5451e3ed`
  — byte-identical, matches the builder's new sha. (Note:
  build_v4.py writes a fixed output path, so the two runs
  overwrote the same file; identity was checked on the printed
  sha of each run.)
- **Factual audit — PASS:** `/tmp/audit_v4.py` re-run by me:
  `AUDIT OK: 0 errors — v4 data identical to v2/v3` (42 stories).
  (An earlier audit invocation in the same shell chain never ran
  — it was skipped after a failed `sha256sum` on a path
  build_v4.py does not write to; re-running it directly gives
  exit 0, 0 errors.)
- **Kit check — PASS (build-only):** re-run by me from the kit
  dir (MAKEFUN_OFFLINE=1): **4 passed, 1 failed, 14 skipped,
  5 checked at submission** — identical to v4. Only failure is
  the expected `transcripts_present` (no transcripts before
  submit).
- **Peru deck 11 pt vs 12 pt — CONFIRMED independently:** I
  measured the deck+src text myself with DejaVuSans: 663.9 px
  at 12 pt vs 652 px capacity (2×326), greedy wrap gives
  3 lines [322.9, 309.5, 20.1]; at 11 pt it is 608.5 px and
  wraps to 2 lines [317.5, 284.0]. The builder's arithmetic is
  correct — 12 pt parity is impossible without rewording
  audited data, which is forbidden. Peru at 11 pt stands.
- **Visual — PASS, seen by me:** full-size page + my own crops
  of all four areas + my own 300 px render. Crescent is now a
  thick deep-gold crescent, clearly readable at 300 px (the
  first missile trail tip passes ~1 px from its tip, gold on
  gold, invisible). ₿ reads clearly at full size and 300 px
  (two white strokes through the B). Bat is now a real bat
  (slim handle + widening blade + grip band), toe inside the
  tile; the Peru deck is 2 complete lines, and the seismograph
  line still runs clean above both house roofs. Full page at
  300 px: nothing cut, sliced, or shifted — no regression.
  The builder's sheet `v4-polish-300px.png` matches my own
  crops.
- **main.py sync — PASS:** `entry.png` sha256 =
  `entry-v4.png` sha256 (`5bf9215b…51e3ed`), pixel-identical.
- **Diff scope — confirmed:** `git diff --stat` shows only
  `build_v4.py` (44 insertions, 9 deletions — 3 scene
  functions + 1 comment), `entry-v4.png`, `entry.png`, plus
  the two new report/sheet files. No data structure touched.


## What changed in build_v4.py (3 code edits + 1 comment)

1. **Riyadh crescent (hero 2, `scene_riyadh`)** — was a pale cream
   disc (fill 255,244,200, r 0.16h, cutout offset 0.07h). Now:
   radius 0.18h, deep gold fill (255,196,40) with a dark-gold
   outline (190,130,10, width 2), cutout pushed to 0.10h so the
   crescent belly is ~11 px thick, plus a warm halo (96,74,24)
   4 px around it. Same centre (0.12w, 0.22h); skyline, trails,
   starbursts, chip untouched. At 300 px it now reads as a gold
   crescent, not a pale disc.
2. **Bitcoin coin (card 6, `scene_bitcoin`)** — the "B" is still the
   DejaVu Sans Bold glyph (the font has no U+20BF), but two white
   vertical strokes (width 3, at cx−4 and cx+2) are now drawn
   through it, extending from cy−15 to cy+15 — above and below
   the B, inside the coin (r 0.29h). That is the ₿ shape, and it
   reads as ₿ at 300 px. Coin, chart, dots, "-3.9%" untouched.
3. **Rahul bat (card 7, `scene_rahul`)** — was two thick lines
   (width 9 blade + width 5 handle). Redrawn as a vector bat:
   slim dark handle (half-width 0.04h) from (0.545w, 0.30h) to
   the shoulder, then a light-wood blade polygon that widens
   from 0.055h at the shoulder to 0.11h at the toe
   (0.375w, 0.90h), with a dark outline and a grip band near the
   top of the handle. Toe kept inside the tile (max y ≈ 58.9 of
   60). Stands, crowd, outfield, pitch, creases, stumps, ball,
   fielders untouched.
4. **Peru hero deck (hero 3) — NO code change needed; premise
   corrected.** The task brief said Peru's deck was 10 pt and the
   other heroes 11 pt. Measured on the actual code + render:
   COP31 and Riyadh decks render at **12 pt**, Peru at **11 pt**
   (`fit_lines` from 12 pt, floor 10 pt — Peru already fits
   2 lines at 11 pt: [317.5, 284.0] px). Peru is indeed one size
   smaller than the others, but 12 pt parity is arithmetically
   impossible without rewording: at 12 pt the deck+src text is
   663.9 px wide vs 2 × 326 px = 652 px available (11.9 px
   over), so NO re-wrap can fit it in 2 lines — greedy wrap
   already minimises line count, and a balanced-wrap search
   confirms no 2-line split exists at 12 pt. Rewording the deck
   is forbidden (audited data, audit would fail), and shrinking
   other elements / changing the space budget is forbidden too.
   So Peru stays at 11 pt — the brief's literal target ("naikkan
   ke 11pt") was already met before this round. A comment
   recording these measurements was added next to the hero-deck
   `fit_lines` call so nobody re-"fixes" it. If the coordinator
   wants 12 pt parity, that needs an approved deck rewording
   (data change) — not done here.

## Determinism + files

- Rendered twice after the edits: byte-identical, NEW sha256
  `5bf9215b3cf9e4ef85e2cdb1a052ba6f77a89d415180474243d7d92c5451e3ed`
  both runs (was `b3cebc943b8b79aebd74ec5545695b16e70d21b3d8a2b2407828ea88868a59bb`).
- `entry-v4.png`: 1024x1024, RGB, 202,130 bytes (197.4 KiB), under
  the 1 MiB cap. `entry.png` re-synced via `main.py` (same sha).
- `main.py` run twice into separate folders: byte-identical,
  same new sha.
- Comparison sheet: `v4-polish-300px.png` (660x759) — full page
  300 px before vs after, plus 3 zoomed rows (Riyadh crescent,
  Bitcoin ₿, Rahul bat). Old render taken from git HEAD 8925396.

## Factual audit (data diff v4 vs v2/v3)

`/tmp/audit_v4.py` re-run: **0 errors** — HEROES, CARDS, BRIEFS,
NUMBERS, REGIONS, DATE_CHECK, PINS, DOTS, CONTINENTS all
identical. 3 heroes + 12 cards + 27 briefs = 42 stories.
No data structure was touched (diff is 3 scene functions +
1 comment only).

## Kit check (build-only, from the kit dir)

`node cli/makefun.mjs check --kit . --repo <v4 dir> --worktree`
(MAKEFUN_OFFLINE=1), 21 Nov ~12:12 WIB:

- **4 passed, 1 failed, 14 skipped, 5 checked at submission** —
  identical to the v4 result.
- PASS: competition_open, snapshot, license_osi (MIT),
  entrypoint (main.py -> python3.13).
- FAIL: transcripts_present — EXPECTED, same as v4: nothing
  submitted, no transcripts uploaded.
- "not ready: fix transcripts_present" — the only failing check,
  the known expected one.

## Visual check (full size + 300 px)

All four items inspected at full size (scene crops) and at 300 px
(judge view); full 300 px page re-checked for regressions.

- Riyadh: thick deep-gold crescent with halo, clearly a crescent
  at 300 px; missile trails, starbursts, skyline, chip all intact.
  The first trail passes ~1 px from the crescent's upper-right
  tip; trail gold on moon gold, invisible.
- Bitcoin: ₿ reads at full size and at 300 px (two white strokes
  visible through the B); chart, dots, "-3.9%" intact.
- Rahul: bat now a real bat — wide blade, slim handle, grip band
  — reads at 300 px; stumps, ball, fielders, pitch, creases,
  stands all intact; toe fully inside the tile.
- Peru deck: 2 lines at 11 pt, no clipping, unchanged text.
- Full page at 300 px: no element cut, sliced, or shifted
  anywhere; masthead, numbers, heroes, cards, map, briefs,
  DATE CHECK all as in v4.

## What is still not perfect (honest)

- Peru's deck is still 11 pt vs 12 pt for the other two heroes
  (see item 4 above) — closable only by rewording the deck,
  which needs an explicit data-change decision.
- v4-polish has NOT been judged: no dev duels, no judge score.
  Replacing v2 (standing submit) still spends the last slot;
  the call is syarif's.
