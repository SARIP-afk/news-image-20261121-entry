# Verification notes — news-image-20261121 v4

Front page "Saturday 21 November 2026", built fresh as `build_v4.py`
(typed from scratch in this session, not copied from `build_v2.py` /
`build_v3.py`). v4 is a full re-budget of the page: v3 fixed the
clipped scenes but paid for it by shrinking the hero scenes 110 ->
77 px and the map 140 -> 88 px. v4 keeps hero scenes at 110 px, card
scenes at 60 px AND the map at 136 px, by re-budgeting every section
from zero instead of shrinking anything silently.

`entry.png` (v2, submitted, standing) was NOT touched on the server;
locally in this repo `entry.png` is now the v4 render (same pattern as
v2's repo, where entry.png was the v2 render). `main.py` now copies
`entry-v4.png` -> `entry.png` in the grader's output folder. No
submit, no push: build + verify + local commit only. Submitting v4
would spend the LAST slot (2/3 used) and waits for syarif's explicit
word.

## Space budget (1024 px, explicit -- asserted in build())

    kicker + rule ....................   0 -  19
    masthead title 46 pt .............  21 -  67
    deck line 13 pt ..................  69 -  82
    numbers strip (6 giant numbers) ..  86 - 148
    region bar ....................... 152 - 165
    heroes: banner 24 + scene 110 .... 169 - 386
    cards header ..................... 390 - 405
    cards: 3 rows x 134, pitch 137 .. 409 - 817
    bottom header .................... 821 - 836
    map 136 + briefs ................. 840 - 976
    DATE CHECK box (3 lines) ......... 980 - 1019
    bottom margin .................... 1019 - 1024

Two 1 px overflows were found by the asserts during the build and
fixed in the open (hero deck +1 px, card deck pitch 11 -> 10.5) --
the build FAILS loudly instead of shrinking something silently.
The standalone footer line of v2/v3 was dropped for space; its
content survives in the kicker ("EVERY ONE DATED SATURDAY
21 NOVEMBER 2026") and the cards-header right note ("SOURCES NAMED
BESIDE EACH STORY").

## Determinism + files

- Rendered twice: byte-identical, sha256
  `c47b6f73c93aa9f76e3efcc4b582cee039de96dd832a647feec8e4a2843a0100`
  both runs (builder's render).
- **Coordinator fix (after independent visual check):** the Peru
  seismograph line crossed the first house's roof (see "What is
  still not perfect" below). The coordinator moved the two houses
  below the seismograph flat line (roof peaks 0.60h / 0.64h vs the
  0.55h trace) and moved the ground crack to the far bottom-right
  corner, re-rendered twice: byte-identical, NEW sha256
  `b3cebc943b8b79aebd74ec5545695b16e70d21b3d8a2b2407828ea88868a59bb`.
  Audit re-run after the fix: 0 errors (data untouched). `main.py`
  re-run twice into separate folders: byte-identical, same new sha.
  Kit check re-run after the fix: same result (4 passed, 1 failed
  transcripts_present as expected).
- `entry-v4.png`: 1024x1024, RGB, 201,858 bytes (197.1 KiB), under
  the 1 MiB cap.
- `entry.png` in this repo is now the same v4 render (201,875 bytes).

## Factual audit (data diff v4 vs v2/v3)

Automated comparison of the data structures -- HEROES, CARDS,
BRIEFS, NUMBERS, REGIONS, DATE_CHECK, PINS, DOTS, CONTINENTS --
all IDENTICAL. 3 heroes + 12 cards + 27 briefs = 42 stories.
No headline, deck, source tag, brief, number, region count, pin/dot
position, or DATE CHECK word was changed. Audit script:
`/tmp/audit_v4.py` (imports build_v3.py data as reference).

## Kit check (build-only, from the kit dir)

`node cli/makefun.mjs check --kit . --repo <v4 dir> --worktree`
(MAKEFUN_OFFLINE=1), 21 Nov 12:00 WIB:

- PASS: competition_open, snapshot (16 files, 1,416,543 bytes),
  license_osi (MIT), entrypoint (main.py -> python3.13).
- FAIL: transcripts_present -- no transcripts were uploaded. This is
  EXPECTED at this stage: nothing has been submitted, and this
  competition does not take recorded transcripts (HTTP 400 on the
  transcript route); the submit flow is bundle/loose files. Every
  other transcript check skips behind it (nothing to read).
- At submission (site-side, not checkable here): repo_public,
  repo_owner, repo_created_after_open, commit_in_repo,
  duplicate_snapshot. The same repo already carried the v2 submit,
  so these are as they were for v2.
- "not ready: fix transcripts_present" -- the only failing check,
  and it is the known, expected one. No local grade exists for this
  competition; the server grades every entry alone.

## Visual check, per scene (1024 px full + 300 px thumbnail)

All 15 scenes inspected at full size (crops) and again at 300 px.
No element is cut, sliced, or spilling out of its frame anywhere.
Banner -> scene -> text, strictly vertical, everywhere.

- H1 COP31 (110 px): globe whole; thermometer whole (tube + red
  bulb + ticks); glowing sun whole top-right; clock whole on the
  roofline; new red temperature line rising across the tile; chip
  "NO DEAL · DAY 13" inside the tile.
- H2 Riyadh (110 px): crescent moon, skyline + lit windows whole;
  3 missile trails + 3 starbursts whole inside the tile; stars whole;
  chip "3 SHOT DOWN" inside.
- H3 Peru (110 px): sun whole; two snow-capped peaks whole; village
  (2 houses) on the slope; red seismograph end-to-end inside the
  tile; ground crack whole; chip "00:09 UTC · 108 KM DEEP" inside.
- 4 Kryvyi Rih (60 px, redrawn rich): 3-layer main flame + second
  flame, rising embers, smoke puffs, city row with lit windows,
  rubble at the base, ambulance-cross glow top-right -- reads as
  fire, not an abstract triangle.
- 5 Davao (60 px, redrawn rich): pointed nose, cockpit + 5 cabin
  windows, red cheatline, tail fin, swept wing, 2 engines, landing
  gear, orange slide with 2 passengers to the runway -- reads as a
  jet, not a white wedge.
- 6 Bitcoin: gold coin whole with drawn "B"; falling chart + white
  dots whole; "-3.9%" fully inside the tile.
- 7 Rahul (60 px, redrawn rich): stands + crowd dots at the top,
  green outfield, tan pitch with 2 crease lines, stumps + bails,
  bat, red ball with seam, 2 fielders -- reads as cricket, not a
  beige box.
- 8 ICJ: 5 columns + beam + steps whole; gold scales centred.
- 9 Kyiv: buildings whole; red "NO" bubble whole; small blue-yellow
  flag on a rooftop.
- 10 UK-EU: EU circle + 8 stars whole; wheat stalks whole; union
  jack hint whole.
- 11 Tokyo: tanker + bridge + red stripe whole; red sun whole; wake
  lines; sea band; 2 barrels whole.
- 12 NSW: lamp glow whole top-right; excavator (tracks, body, cab,
  arm, bucket) whole; 4 coal chunks whole.
- 13 Kenya: mountain + snowcap whole; 3 teal crystals whole;
  pickaxe whole; acacia tree; sun whole.
- 14 South Africa: buildings whole; candle + big flame whole; wick;
  stars.
- 15 US swoop: red + blue siren glows + light beams whole; both
  handcuff rings + chain + centre link whole.
- Numbers strip: 6 giant numbers + 2-line labels, labels clear of
  the bottom rule. Region bar: all 7 regions + counts.
- Map: navy, 136 px tall, pins 1-15 + dots 16-42 all plotted,
  caption in the bottom header ("PINS 1-15 LEADS · DOTS 16-42
  BRIEFS"). Briefs 16-42: all 27 present, 3 columns x 9 rows.
- DATE CHECK: 3 lines, fully inside the red box with padding on all
  sides (box 980-1019, page ends 1024).

At 300 px (judge view): masthead, 6 giant numbers, 3 hero banners
+ 110 px scenes, 12 card banners + 60 px scenes, and the navy map
all read; hierarchy matches v2, with hero scenes and map visibly
larger than v3's. Side-by-side sheet: `v2-v3-v4-300px.png`.

## What is still not perfect (honest)

- The Peru seismograph line crossed the roof of the first village
  house (the flat 0.55h segment passed over the roof peak at
  0.45h). **FIXED by the coordinator after its own visual check:**
  houses moved below the trace (roof peaks now 0.60h / 0.64h),
  ground crack moved to the far bottom-right corner; re-rendered
  and re-verified (new sha256 `b3cebc943…59bb`, audit 0 errors,
  kit check unchanged). Verified visually at full size: the red
  trace now runs cleanly above both roofs with brown mountain
  between them.
- The Riyadh crescent moon reads as a pale disc at 300 px; the
  crescent cutout is subtle.
- The "B" on the bitcoin coin is a plain letter B, not the
  double-stroke ₿ symbol (the font lacks the glyph) -- same as v2/v3.
- The Rahul bat is a thick diagonal bar; it reads as a bat at 300 px
  but is not a detailed drawing.
- Hero decks that needed the shrink (Peru at 10 pt) are one size
  smaller than the others -- visible only side by side.
- The standalone footer line is gone (see budget note above); the
  attestation now lives in the kicker + cards header instead.
- v4 has NOT been judged: no dev duels, no judge score. The only
  thing proven before a submit is the side-by-side at 300 px +
  factual audit + kit check above. Replacing v2 (dev #429/5,592,
  42 stories) spends the last slot; the call is syarif's.
