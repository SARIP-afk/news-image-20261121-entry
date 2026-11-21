# Verification notes — news-image-20261121 v3

Front page "Saturday 21 November 2026", built fresh as `build_v3.py`
(typed from scratch in this session, not copied from `build_v2.py`).
v3 fixes exactly one defect of v2 — the clipped/overlapping scenes —
and changes nothing else. `entry.png` (v2, submitted) and `main.py`
were not touched; no submit, commit, or push was done.

## What was wrong in v2 (confirmed from entry.png)

1. The colour-block banner was painted ON TOP of the scene: the card
   banner (15 px) covered the top 15 px of a 36 px scene strip — 42%
   of the artwork gone. The hero banner (26 px) covered the top of
   the hero scene (thermometer/sun of COP31 cut at the top).
2. Scene functions drew with absolute coordinates written for a
   326x110 hero frame. Inside a 243x36 card frame elements spilled
   out of the frame and over neighbouring cards (bitcoin chart and
   "-3.9%" cut at the right edge of card 6, black triangles of card
   12 sliced, cards 8/9/10 messy/clipped).
3. DATE CHECK: 36 px box, text 3 lines from dy+4 at 11 px pitch —
   the third line touched/crossed the bottom border.

## How v3 fixes it (construction only)

- Every scene is drawn on its own tile of exactly the frame size
  (`Image.new` + its own `ImageDraw`, local coordinates as fractions
  of the tile, radii as fractions of tile height), then pasted onto
  the page. Clipping is guaranteed by construction — nothing can
  spill out of a frame. The map is a tile the same way.
- Strict vertical stack everywhere: banner -> scene tile -> loc ->
  headline -> deck. The banner never overlaps the scene.
- Card scenes are 60 px tall (was a 36 px strip, of which only ~21 px
  was visible under the banner). Hero scenes are 77 px, fully visible
  (v2: 110 px with 26 px covered = 84 px effective). Layout
  re-budgeted to stay 1024x1024: masthead 54 pt, numbers strip 68 px,
  region bar 13 px.
- DATE CHECK: the text is wrapped FIRST, then the box is sized as
  lines × 12 px pitch + 5 px padding top/bottom (3 lines -> 46 px).
  Text sits inside the box with clearance on all sides (asserted in
  code: box bottom <= 1010).
- Two rendering bugs found during v3's own visual check and fixed in
  the same session: (a) the numbers-strip labels crossed the bottom
  rule in the first v3 render — strip widened 62 -> 68 px, labels now
  end ~11 px above the rule; (b) the COP31 clock was swallowed by
  the roofline polygon (drawn after it) — roofline now drawn first,
  clock/thermometer/globe on top. The Peru house was also moved from
  bottom-left (hidden behind the chip) to the mountainside, and the
  globe raised clear of the chip.

## Determinism + file

- Rendered twice: byte-identical, sha256
  `05c4237ad666ae846bf0a3cde25ccffb97c3878169118f6deaab740f3d8f646b`
  both runs.
- `entry-v3.png`: 1024x1024, RGB, 212,492 bytes (207.5 KiB), under
  the 1 MiB cap.
- `entry.png` untouched (sha256 still
  `96a34ffb930a2cd6bbc4617accb6d0979177f3efbf2b343e71a3de1b48d593d1`).

## Factual audit (data diff v3 vs v2)

Automated comparison of the imported data structures — HEROES,
CARDS, BRIEFS, NUMBERS, REGIONS, DATE_CHECK, PINS, DOTS, CONTINENTS
— all IDENTICAL. 3 heroes + 12 cards + 27 briefs = 42 stories.
No headline, deck, source tag, brief, number, region count, pin/dot
position, or DATE CHECK word was changed.

Two small rendering-only improvements inside scenes (no content
change): the bitcoin coin now shows a drawn "B" — the U+20BF glyph
is tofu (empty rectangle) in this system's DejaVu Sans Bold, so v2's
coin showed a hollow box; and deck text now auto-shrinks (hero deck
min 10 pt, card deck min 9 pt) so the full deck fits in 2 lines —
in v2 the Peru hero deck spilled a 3rd line ("IGP") and the Kryvyi
Rih card deck was cut after "— Kyiv". Full wording is now visible.
Note: the task brief said card 6 showed "-9.9%" — the actual v2
data (and the strip) is "-3.9%", kept as-is.

## Visual check, per scene (1024 px full + 300 px thumbnail)

All 15 scenes inspected at full size (crops) and again at 300 px.
No element is cut, sliced, or spilling out of its frame anywhere.

- H1 COP31: sun whole top-right; globe whole, clear of the chip;
  thermometer whole (tube + red bulb); clock whole, visible on the
  roofline; rooflines whole. Chip "NO DEAL · DAY 13" inside tile.
- H2 Riyadh: skyline + lit windows whole; 3 missile trails + 3
  starbursts whole inside the tile; stars whole.
- H3 Peru: sun whole; mountains + snow cap whole; house fully
  visible on the mountainside; red seismograph end-to-end inside the
  tile; ground crack whole. Chip "00:09 UTC · 108 KM DEEP" inside.
- 4 Kryvyi Rih: 3-layer flame whole; buildings + windows whole;
  smoke whole; ambulance cross whole top-right.
- 5 Davao: plane (fuselage, fins, wing) whole; orange slide whole
  down to the runway; clouds + runway whole.
- 6 Bitcoin: gold coin whole with "B"; falling chart + 4 white dots
  whole; "-3.9%" fully inside the tile (was cut at the right edge
  in v2).
- 7 Rahul: pitch, stumps + bails, bat, red ball, crease line — all
  whole.
- 8 ICJ: 5 columns + beam whole; gold scales whole, centred between
  the middle columns.
- 9 Kyiv: buildings whole; red "NO" bubble whole, top centre.
- 10 UK–EU: EU circle + 8 stars whole; wheat stalks whole; union
  jack hint whole.
- 11 Tokyo: tanker + deck + red stripe whole; red sun whole; sea +
  2 barrels whole.
- 12 NSW: lamp glow whole top-right; excavator (body, cab, arm,
  bucket) whole; all 5 black coal triangles whole (were sliced in
  v2).
- 13 Kenya: mountain whole; 3 teal crystals whole; pickaxe whole;
  sun whole.
- 14 South Africa: buildings whole; candle + flame whole (flame top
  inside the tile); wick whole.
- 15 US swoop: siren glows whole; both handcuff rings + chain +
  centre dot whole.
- Numbers strip: 6 giant numbers + labels, labels clear of the
  bottom rule. Region bar: all 7 regions + counts.
- Map: navy, pins 1–15 + dots 16–42 all plotted, caption present.
  Briefs 16–42: all 27 present, 3 columns x 9 rows.
- DATE CHECK: 3 lines, fully inside the red box with padding.
  Footer line present below it.

At 300 px (judge view): masthead, 6 giant numbers, 3 hero banners
+ scenes, 12 card banners + scenes, and the navy map all read;
hierarchy matches v2, with scenes now intact instead of strips.

## What is still not perfect (honest)

- Hero scenes shrank 110 -> 77 px to pay for the taller card scenes;
  the trade is deliberate (cards were the broken part), but the hero
  artwork is somewhat smaller than v2's.
- The Davao plane and the Kryvyi flame are abstract flat-vector
  shapes; at 300 px they read as "plane" / "fire" but not as
  detailed drawings. Same style as v2, only now whole.
- The map is 88 px tall (was 140 px) to fit the taller cards; pins
  and dots are still legible, but the continents are small.
- Card decks that needed the shrink (Kryvyi Rih at 9 pt, Peru hero
  deck at 11 pt) are one size smaller than the others — visible
  only side by side.
- The "B" on the bitcoin coin is a plain letter B, not the double-
  stroke ₿ symbol (the font lacks the glyph).
