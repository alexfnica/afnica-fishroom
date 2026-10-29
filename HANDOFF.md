# Handoff - 2026-10-29: FISH STORE Phase 2 (art) mockup shown, awaiting owner OK (docs/store_mockup.svg; design approved in docs/STORE_DESIGN.md). Proposed: layered vector 2D (SVG) people with CSS walk cycles, real in-game fish sprites in display tanks.

# Handoff - where work stopped (2026-10-29: FISH STORE feature, Phase 1 design written, awaiting owner OK)

## Fish store (new feature, no game code changed yet)
- Phase 0 (code survey) and Phase 1 (docs/STORE_DESIGN.md) done. Next: owner OKs the design, then Phase 2 = art style + ONE mockup (store, 2 customers, receptionist), then Phase 3 build (block tag V17.120), Phase 4 test + aquarium-reviewer.
- Key hooks: sellValueV9, gradeV10, fullGrownV1763, f.finTorn, v8Nav (6 tabs, add a 7th), renderV10Market as screen model, ensureHealthState for st.store / st.storeFish defaults, tankArrayV14 + moveToBreederV103 as the move pattern.
- Open decision: display-tank fish rendering (recommended: lightweight sprites, not the V16/V17 motion engines).

# Handoff — where work stopped (2026-10-29: V17.111 cave INSPECT with real footage, NOT committed; V17.110 rewrite also NOT committed)

## V17.111 cave inspect = Gemini footage instead of the vector canvas (2026-10-29, NOT committed)
- Owner wants a realistic wriggler animation (Gemini + photo, Blender only if needed). Assets so far in `assets_blender/incoming`:
  `anc_wriggler_side.webp` (yolk-sac larva side view, + `_cut`/`_cut_dark` PNG via `anc3d/cut_wriggler.py`), `anc_wriggler_free.webp`
  (free fry after the yolk, new photo; v1 kept), `anc_wriggler_heap.webp` (Gemini heap in the cave, tight heap of long larvae).
  Top view (B) never arrived as a file. Real clip: `D:\ClaudeWork\wriggler_clip\clip.mp4` (memory note anc-wriggler-clip): hatched larvae are
  orange beads with a faint tail, scattered along the wall near glassy empty shells - NOT a tight heap; so the heap photo is an interim only.
- A composite still (my larva cut-outs on a patched cave floor, `docs/wriggler_heap_still.jpg`) looked bad -> rejected; route chosen: Gemini
  image-to-video from corrected heap images (full / half / low yolk).
- Code: `anc3d/block111.js` + `anc3d/install111.py` (embeds footage as data URIs between `<!-- V17.111 BEGIN/END -->`, re-runnable). It wraps
  `window.inspectAncCave40` and, while the single clutch is in the yolk stage, replaces the V17.43 canvas `#ancInspect43` with a looping video
  by yolk left (`full` < 1/3 of the stage gone, `half` < 2/3, `low` after) or, with no video, the interim poster (the heap photo, slow breathing +
  drifting dust). Eggs / two broods / no assets keep the V17.43 canvas. Switch `window.ANC111=false`. Tested headless (`trailer/measure_inspect111.py`):
  eggs -> canvas, yolk (3 stages) -> `.anc111box` with the poster, 0 errors, syntax 0 errors. The popup itself was NOT seen on screen (the rig's
  screenshot only captures the tank). Reviewer not run on this small block.
- UPDATE (owner: Gemini video needs a paid subscription): no video needed any more. The popup now runs a 'living still' on the stage stills
  `anc_wriggler_scene_full/half/low.webp` (Gemini images 1-3; image 3 has a different framing = the tunnel view, 1+2 the angled view):
  per larva (`LARVAE` table, head/tail-tip positions read off a 50 px grid, `anc3d/grid_stills111.py`) an upright patch of the rear body is
  wave-warped in strips for a 0.5-1.2 s tail twitch every 2.5-10 s, dust drifts through the beam, the beam flickers. Canvas 768x419 inside the
  popup box. Measured (`trailer/measure_living111.py`, headless): canvas live, 0 errors, tail positions differ frame to frame without artifacts.
  Videos (`anc_wriggler_heap_*.mp4`) still take precedence if ever added. Larva positions are eyeballed (+-10 px), so a twitch may sit a little
  off a tail; stage stills: only `full`/`half`/`low` keys, popup keeps the V17.43 canvas for eggs. Not seen on screen (rig cannot capture the popup).
- NEXT: owner generates 3 corrected heap images + 6 s loop videos (`anc_wriggler_heap_full/half/low.mp4`, prompts given in chat), then
  `python anc3d/install111.py` (shrink to ~480p / 1-2 MB each first; install warns above 3 MB). Also still open from V17.110: nursery with no
  decoration (corner case) and the cave panel button layout were not seen.

# Handoff — where work stopped (2026-10-29: V17.110 bristlenose FRY yolk sac + staying grouped, NOT committed; owner to review)

## V17.110 bristlenose fry: yolk sac, stay together (2026-10-29; rewritten after the owner's correction, NOT committed since the rewrite)
- Owner: "yolk-sac fry do not roam the tank: they stay next to each other in the cave until the yolk is used up; if the user takes
  them out to the nursery they stay grouped in a corner or under a decoration"; the cave can be inspected (existing viewer).
  First version (commit db66bf1, pushed) wrongly let yolk fry heap on open sand and shortened the cave yolk period - superseded.
- Now: cave yolk stage back to 4-6 days (`yolkIn=4+rand3` in the 3 laying sites, text restored + "you can move the wrigglers to the nursery").
  Fry released from the cave have no yolk (free fry, age 1+). New button "MOVE WRIGGLERS TO NURSERY" next to the cave status (both
  yolk branches of `ancClutchStatus40`) -> `moveAncWrigglers110(slot)` (block V17.110): the brood becomes fish in `st.fry` with optional
  fields `yolkStart110` / `yolkEnd110` (game days; absent = no yolk), clutch stage 'released' + `movedNursery110`.
- Yolk fish (k=(end-st.day)/(end-start) > 0): sac drawn on the fry photo (`ancYolkV17110`, record (172,93) 32x20, size by k, top fades into
  the belly), huddle +-14 px under the first decoration standing on the sand of their tank (`[data-v177-editable]`, the fish z-index = decor z-1)
  or in a corner, rest still, a 3-7 px twitch every 4-12 s, never roam. After the yolk (and for cave-released fry): free fry, age < 5, loose
  group (> 110 px from the group spot walks back). Steering = existing 'move'/'rest' modes. Switch `window.ANC110=false`,
  debug `ancFryDebugV17110()`.
- Measured (`trailer/measure_fry110c.py`, Fry Tank, 5 yolk + 1 free fry + adult, scattered start): yolk fish gather at x 327-354 around the
  decoration spot 346 (3 of 5 move only 16-21 px over the last 2/3 of 100 s; the others were still walking in, ~5 px/s), sac k .75, after
  `st.day+=5` k 0 and 0 amber px, `moveAncWrigglers110` adds 4 fish with yolk fields, 0 errors. Syntax 0 errors.
- Reviewer fixes: the moved clutch gets `emerged43=true` (else the breeder tank played the "fry leave the cave" animation), the z-index tweak is
  cleared when the yolk is gone (`data-z110`). Left: `yolkSpot` ignores a CSS scale on the tank and caches the spot 15 s, `st.fry` takes all
  fry at once (7 shown, like released fry), other blocks also write z-index on the fish.
- Visibility fix (owner: "i don't see it"): fry were drawn at scale .11 = 13 px, an invisible speck. `sizeFor` is wrapped: bristlenose age < 5 get x2.4
  (yolk fry scale .26 = 32 px, free fry .46). Huddle spread +-45 px (was +-14, they overlapped into one fish). A moved brood starts AT the huddle
  spot (`s.init110`), it does not walk across the tank. Where things are in the game: breeding box = BREED (heart) nav -> Bristlenose Breeding Tank
  screen; nursery = Fry Tank (MAIN TANK | FRY TANK switch at the top of the Tanks screen). Frame: `docs/huddle110.jpg` (7 fry, yellow sacs).
- USE THE EXISTING BREEDING BOX (owner: "we already have a breeding box"; my own `.mat110` NURSERY box was removed): the V17.86/V17.88 photo box
  (bought in the Shop, hangs on the front glass of the Fry Tank, `st.breedingBox86 {owned, fish:[ids]}`, geometry `breedBoxV1786(tank,id)`) now also takes
  bristlenose fry: its `young()` includes `anc` age < 5 (texts say "young fry"), the existing 📦 button moves/lets out all young fry, and
  `moveAncWrigglers110` adds the moved brood's ids to the box when owned (else they huddle in the Fry Tank's left corner, toast hints to buy the box),
  then closes the popup and switches to the Fry Tank. The cave button label says BREEDING BOX or FRY TANK accordingly. In `fry()` (V17.110): a fish in
  the box glides onto its floor (own `s.bx110/by110`, because the motion code resets s.x/s.y every frame, and the element's left/top/transform are rewritten
  in the post hook), lies still (twitch every 4-12 s while it has yolk), z-index 41 (between the box's back 40 and front 42), drawn x.75 of the open-tank size (max scale .24 = 29 px; owner: "too huge in the box", it was 1.6x) with a
  dark outline filter (the fry photo is pale on the white grate); let out = z-index/filter removed, it walks home. Frame `docs/box110.jpg`.
  Measured (`/d/ClaudeWork/eye109/box110.py`, movebox.py): 7 fry on the floor inside the box (x 625-778 of box 565-853), move test: 5 added, 5 in box after
  2 s (not purged), button "LET OUT x5", 0 errors. Not seen in the real pane; the box fry are small and pale against the grate.
- Box floor + sides (owner: "the fry look like they sit between the grate bars", "the floor must look like the sides", "make the sides realistic, the laterals are
  displayed wrong"): the V17.88 box photo has a slotted floor grate, black streaks beside the glass edges and flat side walls. `plasticFloor` (V17.110 block, runs once
  when the box exists) redoes both layers at runtime and sets them as `!important` background overrides (the embedded photo is untouched): dark pixels in the outer
  11 % columns of BACK and FRONT are faded (streaks gone), the floor band is cleared and a clear plastic FLOOR trapezoid is drawn narrowing from the front edge to the back
  corners, plus clear glass SIDE PANELS (lighter at the front, bright edge lines) from the front edges to the back corners (x .016 -> .094, y .16 / .835 / .945).
  Also applies to the young corydoras in the box. Round 2 (owner's crop: a 'reflection' beside the sides and grate still at the bottom): the glass panels/floor now stay INSIDE the front glass (xf .05, floor front y .925), the BACK layer's own outer edge columns (x < 4.7 % / > 95.3 %) are erased (they doubled the front edges), and the old floor band is cleared from y .79 with a soft fade-out from .66 (a hard cut left a visible darker band). The owner's crop showed the old grate because the page was not reloaded - reload after updating. A first attempt (a solid blue strip) was rejected. Fish in the box carry `data-inbox110`; the CSS z-index:41 rule loses
  to the motion code's inline important z-index (computed 46), so they draw above the front glass, fine visually. Frame `docs/box110.jpg`; tweak the numbers in `plasticFloor`.
- "Do all" round (2026-10-29): (a) FRY SPRITES from the owner's Gemini photos: `anc3d/install111.py` also embeds `window.ANC110_IMG` (cut-outs
  `anc_wriggler_side_cut.png` = yolk-sac larva, `anc_wriggler_free_cut.png` = free fry); `altRec()` clones the fry record `anc|120|238` into `anc|120|239` (larva,
  while > half of the yolk is left) and `anc|120|240` (free fry, with the painted sac while some yolk is left), `pickSprite()` points the fry canvas `data-wk` at them
  (`data-wk0` = original, restored at age >= 5); the motion code reads the record by data-wk every frame. (b) badge `×N fry` on the breeding box (only 7 are drawn), slow drift
  + small twitches for all fry in the box. (c) Checks: young corydoras on the new clear floor look fine, a tank without a box gathers the yolk fry in the left corner
  (x 81-147), the animated popup costs ~1.6 ms per frame (headless wall time). Frames `docs/sprites110.jpg`, `docs/box110.jpg`, `docs/box_cory110.jpg`.
  NOT done (needs the owner or is out of reach): regenerate image 3 in the same framing as images 1/2 (camera jump between half and low), eggs-stage images for the popup,
  better larva positions (eyeballed), eye on the 3D fight frames / glass roll (baked), a lights-off state (the game has none).
- Eggs stage in the cave popup (owner sent `anc_wriggler_scene_eggs.webp`, tunnel framing like image 3): `install111.py` embeds it as `poster_eggs`; `block111.js` `key()` returns
  'eggs' for the eggs stage, shown as a living still with no twitching larvae (dust + beam flicker only). Headless: eggs and yolk both give the animated canvas, 0 errors.
  Image 3 resent by the owner was the same picture (1 % pixel difference): still the tunnel framing vs the angled images 1/2.
- New image 3 (low yolk stage; owner: 'this is what it gave me'): `anc_wriggler_scene_low.webp` replaced (old = `_v1`), tunnel framing again (fewer, crisper fry with formed fins); `LARVAE.low` re-marked (9 larvae). Images 1/2 are still the angled view, eggs + low the tunnel view.
- Not done / not checked: the wriggler canvas in the cave is unchanged (already a heap), no sac in the glass (belly) view, "under" the decoration is
  only z-order (the first decoration on the sand is the wide driftwood, centre x), nursery with no decoration = corner (not seen), the cave panel
  button layout (not seen in the pane), what the Fry Tank shows when the yolk fish are sold or die (nothing special).

# Earlier (2026-10-24: V17.109 bristlenose EYE follows the light, NOT committed; owner to review)

## V17.109 bristlenose eye: round at night, crescent by day (2026-10-24, NOT committed)
- Research (no blink; dorsal iris operculum; slow light-driven pupil, Douglas/Collin/Corrigan 2002): the pupil is a
  crescent under the lobe in bright light, round in the dark. The photos only have the day crescent baked in.
- Code: hook at the end of V17.42 `draw()` (`ancEyeV17109(g,r,c,dyF,belly,pad)`, try/catch, switch off on error) + new
  block `<!-- V17.109 BEGIN/END -->` at the end of the file. It covers the baked pupil with iris colour (read once per record
  from `r.base`, cached `r.eye109`) and paints pupil + lobe. Eye in 260 px record space: male olive/black (198.8, 57, R 1.9),
  female (209.2, 70.5, R 2.4); y follows `dyF` + the belly stretch. Light = `ancDayNightFactorV17()` (honours
  `window.__afHourOverride`), smoothstep((f-.25)/.5), eased with tau 25 s (`window.ANC109TAU`), ONE shared level for all
  fish; nothing saved. Switch `window.ANC109=false`; debug `ancEyeDebugV17109()`.
- Follow-up checks (2026-10-28, no game edits): belly forced to -.25/0/+.25 (`trailer/measure_eye109b.py`): painted eye within
  .25 px of the baked one (the belly shift at the eye is only ~.2 px by the formula, u=.225). Digging: `nose` only moves u<.13,
  the eye is at u=.225, so no change. Turn/cave: they cut the same live canvas, so the eye is inherited (not filmed).
  Young fish (`trailer/dump_young109.py` -> `docs/young109_dump.png`): fry eye ~ (215, 28), juvenile ~ (213, 36) in record
  space. Then added (owner: "add young"): EYE entries anc|120|238 (214.7,55.9,R1.6; |0|238 aliased), anc|120|438 (211.4,71.6,1.5),
  anc|0|438 (206.4,59.9,1.6). Grid `docs/eye109_young_grid.png` (`trailer/measure_eye109c.py`): round -> half -> slit, aligned, 0 errors,
  syntax 0. The young pupil is only ~3 px wide, so day reads as a smaller slit rather than a clear crescent.
- Not covered: 3D fight frames (baked), the glass roll `drawRoll`. Young fish ARE covered (see below).
  The eye is tiny in game (pupil ~2 px of a 260 px record) - the change reads as round vs dark crescent, not detail.
  No tank-lamp / lights-off state exists yet; only the clock / hour override.
- Measured (`trailer/measure_eye109.py`, headless, 1M+1F): hour 12 -> 23, level 1.00 -> 0.82 (5 s) -> 0.30 (30 s) -> 0.09
  (60 s), monotone; pupil dark px male 6 -> 10 -> 13, female 31 -> 42 -> 47 (night / dusk / day), pupil centroid rises as
  it rounds; 0 errors. Grid `docs/eye109_grid.png` (rows night / dusk / day, male | female). Syntax check 0 errors.

# Earlier (2026-10-23: V17.108 bristlenose spawning in the cave, NOT committed; owner to review)

## V17.108 bristlenose SPAWNING in the cave (2026-10-23, NOT committed)
- Spec + sources: `docs/ANCISTRUS_SPAWNING_SPEC.md`. No source supports the female entering tail first, so the owner
  OK'd choreography B: male invites head out → walks out and aside → she slides in HEAD FIRST to the back → he follows
  head first and lies over and behind her (6 px higher, tail out of the mouth), fanning with the V17.106 bouts and soft
  tail → she backs out under him, pivots outside and leaves → he is already head in / tail out = the V17.89 egg guard.
  Owner-approved still of the poses: `docs/spawn108_still.jpg` (rig `trailer/still_spawn108.py`).
- Code: `assets_blender/anc3d/block108.js`, installed by `anc3d/install108.py` between `<!-- V17.108 BEGIN/END -->`
  right after the V17.90 block (install90 leaves it alone). It wraps `ancBreedingMotion40` and owns the pair in the breeder
  while `st.ancClutch.stage==='spawning'`: same phases, same save fields and eggs code as V17.40, positions in a runtime
  Map (no new st fields). It is a target-based state machine, so a reload mid-spawn resumes; trapped/laying/exit snap to
  the pose. It hands the male's position to the V17.89 cave cycle (`HAND` → `g.ph=null,g.x,g.y`). Speeds: walk 28, slide
  13, back 18 px/s (body 112 px). It keeps the cave/rim placed like V17.40. Switch: `window.ANC108=false`. Test hook
  `window.__T108={inv:s}`. An error hands that clutch back to V17.40 (`ERR`, logged once).
- Hooks in older code: V17.89 `ancDebugV1789()` exports place/caveGeo/fanOn/ys/tailPiece/malePos, and the V17.89 post
  returns early while `data-sp108` is set. In block90.js (reinstalled): `drawFish` no longer skips the pair (it used to
  skip all spawning fish, so they only got flat flips), the facing-follow ignores `data-back108` (backing out), and
  post106 runs for the male with `sp108==='fan'`.
- Turns: still fish use the V17.104 standing pivot (`s.turn`, which carries s.x). The male's turn deep inside the tube is
  an instant hidden flip (`anc90Debug().ST` df), because a pivot there would swing the tail out of the closed end.
- Measured (`trailer/measure_spawn108.py`, 1M+1F+cave, hour 12, 2 loops forced, trapped cut to 6 s, invite 4 s): max
  drawn step ≤ 2.4 px/frame outside turns; the V17.104 pivots 8.9–9.9 px/frame mid-snap (the approved turn, V17.104 measured
  ~11); 0 fish px over the tube, 0 faded frames, 0 errors. V17.106 tail on in all 662 spawning frames. The ~10 px/frame
  after the eggs is the female's ordinary V17.105 sand burst. Grid: `docs/spawn108_grid.jpg`.
- Owner round 2 (in the pane: "corruption", "male too high in the water column", "bodies still collide with the cave"),
  NOT committed yet:
  - The female's belly went below the opening and through the front lip. The rim layer does NOT hide fish here.
    New `mouthClip` is an even-odd `path()`: all of the fish left of the mouth plane, minus the tube's front face
    (half-ellipse 12 x 34), plus the opening (7 x 22.6). Bodies inside: the female's dy is -4 (the sprite's fins reach
    ~9 px under the box centre; the opening's bottom is T+64.6), the male lies on her at dy -9, and she goes less deep
    (snout +108), so her tail shows under his.
  - The male no longer lifts 18 px "aside". He walks out past her on the sand line, drawn behind her (z 42), and turns
    behind her. She waits at snout -40.
  - `ancInCave` (V17.89 fanning look: 65 % brightness and its own clip) is now only on the fanning male, and there is one
    mode label for all walks: both used to switch at the mouth. The female hands back through V17.89's `g.leave` blend
    (it was a 4.6 px drop). Re-measured: same numbers, the hand-back step is gone, 0 overlap, 0 errors. Close-ups rig:
    `trailer/probe_back108.py`.
  - Owner round 3 ("the ancistrus can still be seen through the cave"): the opening showed the fish inside. Now
    `mouthClip` = left of the tube photo's REAL outline (left edge per row from the cave img alpha, cached in `SIL`),
    with no opening; it is re-applied after the chain, so it also replaces V17.106's fan clip for the spawning male
    (only his tail outside shows). Close-ups clean (`probe_back108.py`).
  - Owner rounds 4-5: every clip line failed (vanishing on the terracotta / passing behind / body over the ring /
    seam). Measured with `probe_back108.py TRIPLE=1` (same frame: current clip, no fish clip, rim hidden): the V17.89
    rim layer (z 45) DOES hide fish behind the terracotta. The real problem was the opening: a transparent hole in the
    rim, so a fish inside showed through fully lit. FINAL (owner OK'd the close-ups): no special clip (V17.89 place()
    tube-wall clip only), plus `.anc108shade` = a dark gradient over the opening (z 45, clear at the mouth, near black
    inside), kept with the breeder cave (also for the egg guard). Cave line for passing the mouth = geo.cy-11 (centred
    on the opening); the male settles back to geo.cy for the guard.
  - FINAL after rounds 6-10 (owner OK'd in the pane on 2026-10-24; supersedes the shadow version above). The owner's rule: "the
    fish goes in through the opening, its body is visible as it goes in, never through the ceramic; the inside looks
    real". Fish at the cave are drawn OVER the rim layer (z 46-48; he walks behind her at 46) and `mouthClip` decides:
    left of the tube's outer edge (per row from the cave photo alpha, `SIL`), plus at the opening's height up to the
    opening's FAR edge (ellipse 7.6 x 23 at 13.8,42). `.anc108inner` (z 42, right after the cave) = inner terracotta wall
    fading into shadow; `.anc108shade` (z 49) = light depth shade over the fish in the opening. Line at the mouth
    cyO = geo.cy-5 (owner: "lower"); female dy +2, the male on her back dy 0, he settles to geo.cy (+5) for the guard.
    Rejected along the way: clip at the outer edge (looked like going behind), clip at the mouth plane (seam / body over
    the ring), transparent opening (see-through), black opening (unrealistic).
- Reviewer: no blockers. Fixed: a stall if the fish scale is above 1.01, the error latch, cave/rim placement. Open (low): the pair waits on
  each other through the runtime map, so if one of them is not rendered (8+ fish in the tank) the sequence pauses. Not
  tested: a reload in each phase, water change mid-spawn, cancel by disease (all reasoned OK by the reviewer). The
  invite phase is long (~28 s) when the male first has to walk to the cave from the far side.

# Earlier (2026-10-22: V17.104 photo-warp turn + V17.105 sand rasp/hitch/burst + no contact shadow, committed; owner watching the 1M+2F test tank)

## V17.106 bristlenose CAVE with the in-game model (2026-10-22, NOT committed; owner to review)
- Owner: entry/exit was a static pose and used the Blender render (look switched at the mouth); fanning tail "stiff board".
- Diagnosis: V17.90 drawFish hid the male (opacity 1-a) in CAVEMODES + cave-approach and drew atlas C2 frames instead
  (entry swap 4 frames, render up to 8.9 px off the photo, steps 3.9 px/frame; exit/turn = flat mirror flips). Fan tail =
  render_cave2 single-curvature bend + 2-frame cross-fade; the in-game V17.89 fallback squashed the whole caudal at once.
  NOTE: the live anc model is the 2D photo canvas (ANC3D_V1789=false, sprite 260x192), so shader/psi tricks do nothing.
- Now (block90.js, V17.106, switch `window.ANC106=false`): his own element stays visible all cycle; `post106` clips it
  (whole left of the mouth plane L+13.8, only through the mouth ellipse 7x22.6 behind it); no turns inside the tube; the
  turn outside the mouth = V17.104 photo-warp timed by the V17.89 cycle (`cave106`); fanning rhythm = bouts of 4-8 beats
  at ~2.3 Hz with 0.4-1.2 s pauses (fanPh89/fanEnv89 rewritten); `warp106` (in the ancPectV1789 wrapper) redraws the tail
  region in 20 strips with a wave base->tip (strip foreshortening + shading + slight vertical flex; A106/K106/V106).
  Atlas C2 is now only used for the empty tube (C_tube00) - candidate to slim the ~150 MB decoded atlas.
- Measured (`trailer/measure_cave106.py`, 1M+1F+cave, fan/guard shortened): max drawn step 2.5 px/frame in all cave
  phases, 0 fish px over the tube unclipped, 0 errors; breeder with eggs: stays fanning, no errors. Reviewer: no blockers
  (fixed: scaleX 0 guard in the clip, stale fan106 flag). The ref clip QqU5RsqYAOI 4:30-5:00 shows fry feeding, not fanning.
- V17.107 (owner: "too up" entering/fanning): V17.89 caveGeo body line T+46 -> T+61 (T+53 was still "too up"), so the fish rests on the tube
  floor: the opening reads dark down to ~T+67; fanning tail now spans y 330-357 (was 322-349). Affects all cave poses incl. female/spawning.

## V17.104 bristlenose TURN = the photo itself, warped (owner: "don't swap the picture")
- Path taken today (all rejected on the way, for the record): V17.103 arc + camera rising to 20 deg ("turns like a
  shark"), V17.104 3D snap turn from render_turn6.py (motion liked, but "a highlight / corruption / outline when it
  turns"). The 3D skin differs from the photo however it is matched (raw Blender frames: white speckle all over, lighter
  fins, loose specks under the chin); every swap photo -> 3D -> photo read as a flash. Tone/texture/edge matching scripts
  from that attempt stay in anc3d/ (norm_frames103, screen_match104, soften104, edge104) but are no longer in use.
- Now (block90.js turn draw): the fish's own live photo canvas (`.ancArt canvas[data-wk^="anc|"]`, with its moving fins)
  is cut into 36 strips laid along a spine that rotates PI in 0.6 s (`ancTurnSecV1789=.6`) about a point .22 BL behind
  the snout (the owner's calico clip `D:\ClaudeWork\calico\clip.mp4`, 6.6-7.4 s: head holds its spot, the tail kicks
  round in a C, ~0.5 s); tail lags (C-bend from the turn rate), strips narrow edge-on (+30 % of the body width so no
  paper sliver; 90 % made a box) and mirror past it, far strips first. The fish's x is carried .56 BL forward with the
  body (`tt.x104/h104`, held back at the glass); turn canvas widened to 360 css (720 backing), mirror axis
  4*(OX+60). Measured on screen (`D:\ClaudeWork\scratch104\probe_hl.py`): start 0.5 px / end 0.3 px from the photo,
  luma and p99 = the photo's all through, max step ~11 px/frame mid-turn (the snap), 0 errors.
- Contact shadow removed (owner: "remove the shadow under it, looks weird"): block90 hides `[data-anc-shadow]`.
- atlas104_T (3D turn frames, render_turn6 TURN_SIDE=1) is still packed by install90 but NOT drawn any more - drop it
  (and the @@ATLAS_T@@ slot) to save ~0.45 MB when convenient. Backups: `out/block90_v103_backup.js`,
  `out/block90_v104_3d_backup.js` (3D snap turn), `out/block90_v104_backup.js` (before V17.105).
- Not tested: juveniles/fry turning (same code path, own photo canvas), a turn reversed mid-way, WebGL photo canvas
  (gl89=1: bbox read falls back to the full canvas width).

## V17.105 bristlenose ON THE SAND: rasp, hitch, burst (owner: "sometimes it walks like a shark"; "they rasp much more,
## on the substrate and the glass"; "jerks, bursts sometimes, like in the clip")
- Ref B7RksQ1xU18 0:15-0:22.5 (frames `D:\ClaudeWork\scratch101\mv2`): >6 s parked rasping, then a C-snap burst out
  of frame in < 0.5 s. Ours before: grazing = continuous slow slide ("mow"), trips > 1.3 BL = steady 0.75 BL/s cruise.
- block90.js section V17.105 (after V17.95; switch `window.ANC105=false`, counters `anc90Debug().D105`): graze rasp
  4-10 s, every mow/shift -> one hitch (0.12-0.25 BL in 0.3-0.45 s); graze sessions 20-45 s; glass patch held 10-18 s,
  next one half as far; sand trips = pause / hitch / burst (> .9 BL: up to 2.5-3.2 BL/s, decay ~.24 s, swim flag only
  in the burst), V17.95's slow dart replaced; spontaneous burst every 25-60 s. Fights, cave, breeder, glass trips untouched.
- Measured (measure_move95.py, 180 s, female): grazing 91 -> 110-138 s, moving 28 % -> 12-18 %, bouts 0.4 s, bursts
  1 -> 3, max step 7.9 px/frame, 0 errors. NOTE: measure_move95's `AT1` env is a JS snippet, `AT1=1` does nothing.
- Clip `AFNICA_Anc105_sand.mp4` (2 females, `D:\ClaudeWork\scratch104\film_sand105.py`). Owner is watching a 1 male +
  2 female test tank in the Browser pane (launch.json "afnica", save() blocked) - no verdict yet.
- Reviewer NOT run on the V17.104 photo warp or V17.105 (owner asked to push first) - run it next.

## V17.103 bristlenose TURN, seen from above (owner: "the turn looks bad, not realistic"; then "do whatever pleases the players' eyes")
- Comparison (clip B7RksQ1xU18 25.7-27.5 s vs ours, 10 frames each ~0.2 s apart; clip frames grabbed at 0.1 s with
  `D:\ClaudeWork\scratch101\yt_frames_b7.py` -> `scratch101\turnref103`, no robot check): `AFNICA_Anc103_turn_compare.jpg`
  (before) / `AFNICA_Anc103_turn_after.jpg` (after), root, git-ignored. Composer `D:\ClaudeWork\scratch103\comp103.py`.
- Diagnosis: the turn is pre-rendered (atlas T, block90 draws one of 61 frames per game frame, quick photo hand-over, no
  flip conflict). The 3 deg side camera made mid-turn a thin head-on sliver; the real fish is seen from a little above
  (broad back + flat head + legs-wide pectorals), walks a wider arc and keeps a long C-bend.
- `anc3d/render_turn5.py` (from render_turn4): camera pitch 3 -> PMAX 20 deg mid-turn (sin^2, 3 deg at both ends = the
  photo; shift keeps the mid-body ground point fixed), arc RX .40 / RZ .30 L (was .30/.15), smoothstep timing (yaw spread
  over the turn, was bunched mid-turn), C-bend cap 1.3 gain 2.2 full 22-78 %, pectorals 1+.55*flare. -> `out/turn103_raw`
  -> lut_match_photo100 -> norm_frames102 -> `out/atlas103_T` (same layout, 1.09 MB; pack q .8). install90 packs it.
  block90 glass hold-back uses .4 BL + smoothstep. **Commit: `git add -f assets_blender/anc3d/out/atlas103_T.*`**.
- Measured (probe_turn102.py, a1/a2 males, f2 female, WALL=1): 1.97 s, max step 4.35 px/frame (was 4.97), end drift
  <= 2.4 px, 0 backward, 0 errors, 7.6 px clear of the glass. The lowest drawn point dips 12.5 px mid-turn (snout toward
  the viewer seen from above - intended; if the owner reads it as sinking, lower PMAX, e.g. PMAX=14, re-run the pipeline).
- **V17.103b (owner: "a dubious highlight when it turns - keep shape, colour, contrast")**: the mid-turn 3D views were
  milky (male p10 38 -> 50, p98 187 -> 168, sd 42 -> 33; norm_frames102 only held the mean). New `norm_frames103.py`
  (replaces norm_frames102 in the pipeline): quantile-maps every frame's fish luma onto frame 00 as an RGB gain (hue kept).
  After: sd 41.8-42.2 on every frame, p10/p50/p98 fixed; in the game (probe_turnho) fish luma 65.1-66.8 vs photo 66.8
  (male), 63.6-64.8 vs 64.7 (female). atlas103_T 1.12 MB. Clip `AFNICA_Anc103_turns.mp4` (root, ignored; filmed with
  `D:\ClaudeWork\scratch103\film_turn103.py`). Shape still changes as it must in a 3D turn; if the owner wants less,
  lower PMAX.
- Reviewer: no blockers. Untested: juveniles in the game, a reversal at u~.5 (biggest pose change), the dip at the lowest
  sand row / near the bottom nav, click target stays at the photo spot (up to .4 BL away mid-turn, as before).

## V17.102 bristlenose ARC TURN (owner: "turn naturally like a normal ancistrus"; "don't lift the specimen")
- Investigation (ref. B7RksQ1xU18 25.0-27.75 s, grid `D:\ClaudeWork\scratch101\turnref_grid.jpg`): the real fish walks
  forward round a curve while turning (~0.5 BL), body bent, tail swinging wide; ours (V17.95 pivot) spun on the spot and
  passed through a flat head-on frame. Owner OK'd the still `AFNICA_Anc102_turn_still.jpg`.
- `anc3d/render_turn4.py` (replaces render_turn3 for the T atlas): mid-body walks a half ellipse (RX .3 L forward, RZ .15 L
  toward the viewer), heading = path tangent (head first), C-bend from the path ahead/behind (cap 1.05, 0 at both ends),
  fin lift measured once on frame 0 and kept (no lift / bob), camera follows the fish's depth so the sand line stays put.
  4 types → `out/turn102_raw` → `lut_match_photo100.py` → `out/turn102` (brightness 90/67/81/42 vs photo 91/68/82/43) →
  `out/atlas102_T` (same layout as atlas100b_T, 2.2 MB). install90 packs it. **Commit: `git add -f
  assets_blender/anc3d/out/atlas102_T.*`**.
- block90.js turn draw: quick hand-over (3D in by u .06, photo gone by .1, reverse at the end; the old .15-.25 timing
  showed a ghost double fish because the 3D walks off at once); at the glass the 3D is held back by the overshoot (nose
  against the glass, reach 24 → 10 px, 7 px clear).
- Measured (`trailer/probe_turn102.py`, FID/SEX/WALL=1): 2.0 s turns, max step 3.6-3.8 px/frame, belly line range 2 px,
  end drift <= 1.6 px, 0 backward, 0 errors; natural 3 min (`measure_turn95.py`): 6 turns incl. a moving 1 s follow turn,
  no errors. Video `AFNICA_Anc102_turns.mp4` (`trailer/film_turn102.py`).
- Reviewer: no blockers. Not tested: a turn reversed mid-way (small vertical pop possible), juveniles in the game (frames
  checked offline only), click target / shadow during the turn (they stay at the photo spot, up to ~24 px from the 3D).
- **V17.102b (owner: "it hovers during the turn and highlights / changes colour - don't")**: measured in the game
  (`D:\ClaudeWork\scratch101\probe_turnho.py`, FID/SEX): the baked turn shadow reached ~5 px below the fish (the photo has
  NO shadow - the game's ancContactShadow is display:none in older code ~HTML 7960) and the lit 3D was 3-7 % brighter,
  drifting as it turned. Fixes: anc_build2 `FLAT` option (texture as pure emission, no light; default False);
  render_turn4 sets FLAT and hides the shadow-catcher floor; `norm_frames102.py` scales each turn frame to its frame 00
  brightness; block90: ctx.filter brightness .967 (black male, MB) / .965 (females), female turn canvas 2 px lower.
  After: black male / olive male / both female colours - fish bottom within ~1 px of the photo, luma within ~1.5 %.
  Not measured: juveniles (JO/JB). Reviewer: no blockers (a shadow-walking attempt was a no-op and was removed).
- **V17.102c (owner: "the image doubles when he turns")**: the V17.100 neighbour-frame blend (frame k + k2 at `mix`)
  drew two frames a few px / degrees apart over each other mid-turn = a ghost double fish (semi-transparent px peak
  1293 vs 689 without; rig `D:\ClaudeWork\scratch101\probe_ghost.py`, MIX=0). Now: no blend, 61 frames (render_turn4
  TURN_N 60), the nearest one per game frame (one per frame of the 2 s turn); atlas102_T 244 cells 6240x4180, 1.26 MB
  (~104 MB decoded, was ~88). The brightness filters were removed again (the blend had added opacity). After: ghost px =
  baseline (max 701), max step 5 px/frame, colour within 2-3 % of the photo for both males and both female colours,
  ground line within ~1.3 px, 0 backward, 0 errors. `window.ANC102MIX` hook gone with the blend.
- Fight stills with the same rules (FLAT skin, everything on the sand, pair turned 30 deg) were rendered
  (`AFNICA_Anc102_fight_still.jpg`, render_fight.py now has FLAT + no lifts/rears) but NOT animated or installed -
  the owner's "no hover / no highlight" message was about the turn; ask before continuing the fight.
- NEXT (owner chose "turn first"): the fight - owner: "doesn't look good", "they hover like airplanes". Plan agreed in
  chat: far male stays on the sand (no .32 lift / nose-up), pair turned more toward the viewer instead; no gliding -
  approach / break-away as real crawling baked in the frames, pushes move only a few px with visible effort.

## V17.101 bristlenose male fight, head to head (owner's ref. youtube.com/watch?v=FbPG89ootMs; all 3 phases OK'd up to the grid)
- Clip read (45 frames, 720p): males lie side by side facing the SAME way, flanks pressed, heads level (25-27 s, 69-83 s);
  V / T / one over the other's back at 31-59 s; long near-still shoving holds, short ~1 s whirl bursts (81.2-82.2 s);
  dorsals up, pectorals spread; slow pair pivot over ~60 s; ends apart, no chase. Cheek odontodes not visible at 720p.
- Still (owner OK'd): `anc3d/still_fight101.py` → `AFNICA_Anc101_fight_stills.jpg` (clip 25.4 / 82.2 s next to the renders).
  The game camera is side-on, so the pair is turned 18 deg toward the viewer and the far male rides up on the near one's
  shoulder (lift .32, front up 10 deg), else he is hidden.
- `render_fight.py` rewritten (old: `out/render_fight_v99_backup.py`): S settle 12 (photos → hold pose), H hold 16 cyclic
  (push: far male presses in, near braces, slow tail sway, ±2 deg pair drift), W whirl 15 (tails thrown apart, two whips,
  back to the hold). Layers P1 = near male, P2 = far. `out/fight101_raw` → `lut_match99.py out/fight97_raw out/fight97 ...`
  → `out/fight101` → `out/atlas101_P` (86 cells, 7200x2080, 1.24 MB; atlas99_P was 1.86 MB / 7200x2600). install90 packs it.
  **Commit needs `git add -f assets_blender/anc3d/out/atlas101_P.*`.**
- block90.js fight: `SEQ101(T)` (T 20-28 s, runs 18-30 s): S, then rounds of H (2-4 pushes at 10 fps = 3.2-6.4 s) + W
  (25 % two in a row), last push, S backwards to the photos. Walk-in: the intruder walks to the rival's x (from in front:
  16 px past, then one pivot - the HTML move code ~7939 backs a fish up instead of turning for targets < 14 px behind,
  that was the old "stacked 2-4 px apart" walk-in failure); follows a still-gliding rival; one "walk on" retry if stopped
  the wrong way round; aligned = same facing, |dx| <= 12. Canvas on the intruder, mirrored with him when facing left
  (`F.sg`). Ending unchanged: winner rests, loser darts on.
- Measured (`trailer/measure_fight101.py`, headless, 2 adult males, no female, noon; LEFT=1 makes them face left first):
  right + left fights "done" in 21.6-25.8 s, walk-in 11-14 s, backward frames 0, photo step max 2.58 px/frame outside
  darts, 3D pair centroid max 3.3 px/frame (whirl), photos 0 % under the 3D, errors 0. Grid `AFNICA_Anc101_fight_grid.jpg`.
- Reviewer: no blockers. Watch: a rival resting < 70 px from a wall can't be lined up (go96 clamp) → clean 'misaligned',
  30 s cooldown, may retry fruitlessly; tank switch / water change mid-fight not re-tested (same release paths as V17.96).
  Not done: the slow pair rotation over the fight, cheek-spine hooking, the T / on-top variants (only one hold pose).
- **Hand-over fix (owner: "they teleport in and out of the animation")**, block90.js (backup `out/block90_v101a_backup.js`):
  (1) the 3D pair stands on flat sand: no fight when the rival lies on / beside the cave tube (V17.89 ramp zone
  `s.cave89` ±56 px, where `ovl89` lifts an arriving fish up to ~50-64 px) - roles swap if the other male is free, else a
  15 s cooldown; after arrival they wait up to 2.5 s for `ovl89/ovA89/lift89` to settle, else 'uneven'. (2) layer 1 (near)
  = the photo drawn on top (z-index, then DOM order), so the colours never swap. (3) fades: the 3D fades in over the
  still-opaque photos (.4 s), the photos go (.2 s); at the end the reverse - no half see-through frames (a first
  version blanked both for 2 frames, fixed). (4) each male's layer starts / ends on his own photo (dx, dy) and eases to
  the pair spot over the 0.8 s settle. (5) the loser lies still 0.8-1.3 s before leaving (`P101` queue in tank96).
  Rigs: `D:\ClaudeWork\scratch101\probe_ho2.py` (start/end every 0.1 s → `ho2_grid.jpg`), `probe_uneven.py`.
  Re-measured right + left: "done", 0 backward, 2.58 px/frame max outside darts, 0 errors. Reviewer: one bug fixed
  (loser pulled into a new fight lost his hold), rest minor (P101 is global across tanks but only touches its own fish).
- **V17.101b movement (owner: "they overlap before the fight; during it they stay on one spot" → "do all")**
  (backups `out/block90_v101b_backup.js`, `out/render_fight_v101a_backup.py`):
  - Walk-in: the intruder stops 0.9 BL BEHIND the rival (F.D0); if he is in front, the rival pivots round first (leg 3)
    so nobody walks through anybody.
  - New frames (render_fight.py): A approach (pose only; A00 held 0.6 s while the photos go, then the game slides the far
    male's layer in from 0.9 BL over 1.5 s), Q pivot (pair turns 30 deg more toward us, played forward + back),
    Y / Z break-away (near / far male leaves; game slides him 0.75 BL forward in 0.9 s, done before the photos return).
    A/Y/Z rendered `solo` (5th arg; no holdout - a sliding layer with holdout holes showed fragments); the game draws the
    far layer first. S dropped. Layers: P1 = rival (near, canvas host), P2 = intruder (far).
  - Drift: plan101 gives each push / whirl a shove (8-22 px per push, .3 BL per whirl, 60 % in the facing direction),
    kept off the walls (room for the break-away) and out of the cave tube zone; the pair travels ~100 px in a fight.
    At the break-away start (photos hidden) both photos are moved to where the 3D ends.
  - Canvas 880x260 (440 css), cell drawn at +140 px. atlas101_P: 172 cells, 7200x3900, 2.5 MB (~112 MB decoded, was ~54).
  - Measured (`measure_fight101.py`, now FISH env, LEFT=1|R nudges, fixed no-SEED bug): 5 headless fights + 3 in the
    pane "done" 20-26 s, 0 backward frames, photo steps <= 2.58 px/frame, 3D pair <= 4.65 px/frame (whirl lunge), 0 errors.
    All of them happened to face LEFT (the scenes put the intruder on the right); the right-facing path is the same code
    with sg = +1, checked by hand, not seen running since this change.
    Grid `AFNICA_Anc101b_fight_grid.jpg`; start/end rig `D:\ClaudeWork\scratch101\probe_ho2.py`.
  - Reviewer fixes: a start spot near a wall / the tube makes plan101 shove the pair out of it, and the loser's
    break-away spot is clamped to 70..W-70; the intruder's y offset is eased back in at the end too; an abort mid-fight
    puts the photos where the pair drifted to. Left as is (minor): fixed layer order (rival always near), leg 3 when
    the rival is against the wall can still walk through him (rare). **Memory**: recol97 caches a 600x260 canvas per
    cell per colour key with no eviction - a black male fighting adds up to ~100 MB over many fights on top of the
    ~112 MB decoded atlas; check on phones / Safari, an LRU in recol97 is the obvious fix.
- **V17.101c (owner: "they don't fight with the head / the horns any more, only tails"; "a highlight on the body at the
  start, still a small teleport")**:
  - Measured the start (`D:\ClaudeWork\scratch101\probe_start101.py`, photo vs 3D A00 per fish, clip x3): 3D dorsal
    6-10 px lower (START had fold .3), olive 3D body 3.6 px lower, local specular shine on head/back.
  - anc_build2.py: module vars `ROUGH, SHINE` (defaults unchanged .55/.28); render_fight.py renders matte (.85/.06),
    START fold 0. New phase K (18 frames, 12 fps): head / bristle strikes - the far male swings his head (about his
    mid-body, `turn_mid`) into the near one's snout, front up, the near one's head knocked away; then the near one
    rears and strikes back. All 208 frames re-rendered → `out/fight101c` (LUT) ×1.06 brightness → atlas101_P
    (7200x4680, 3.1 MB, ~135 MB decoded). Game: bursts K 65 % (30 % twice) / W 35 %, K drift .12 BL; near layer -2 px,
    far +2 px y nudge eased over the first / last .8 s. After: olive 3D vs photo luma 89.9/90.5, centroid within ~1 px;
    black male 3D 4.7 % lighter (his colour comes from the shared MB map - not touched).
  - Measured: 3 fights "done", 0 backward, 3D pair <= 4.6 px/frame, 0 errors; sequences like AHWHKHKHZ.
    Video `AFNICA_Anc101_fight.mp4` (`trailer/film_fight101.py`, ZOOM=2.6, SEED 3).
  - Reviewer: no blockers. Black male's fight layers drawn with `ctx.filter brightness(.955)` (key MB) → luma 68.5 vs
    photo 68.3 (no effect where ctx.filter is unsupported). Fights now run ~22-31 s (double K bursts overrun the
    20-28 s plan a little). Memory: atlas101_P ~135 MB decoded - still the open item above.

## V17.100 (owner: "fish only a fragment on the sand"; "2 sets of bottom fins, double tail")
- **Fragment on the sand (real cause)**: a load race in the V17.42 fin code. The V17.90 block swaps the bristlenose CSS to
  the 4-column V17.97 sheet only on `window.load`; fish articulated earlier captured the OLD 2-column sheet (1254x1254)
  as `dataset.originalImage`, and `ancSheetImg()` kept the first image forever. Columns 0/120 exist in both sheets, but the
  colour-for-life cells 240 (black male) / 360 (brown female) were cropped from the wrong image: the base had the fish at
  rows 94-151 of 152 (the dorsal only, ~980 px drawn instead of ~3900). Reproduced on the owner's real save too
  (`anc|360|38` broken). Intermittent = depends on load timing. `mk()` test fish are fine (same fields as real saves).
  Fix (V17.42 code, `ancSheetImg/Load/Check/Reset`): after `window.load` (setTimeout 0, so after the V17.90 handler)
  `ancSheetCheck` reads the sheet URL from the V17.90 rule `html .ancArt i`; from then on only that URL is used (a stale
  originalImage never brings the old sheet back - tested in the pane). If the image in use differs it is swapped and
  `ancSheetReset` drops every `anc|`/`ancg|` record, rewrites the sides' originalImage + body/tail pieces, removes the fin
  canvases/classes (re-adopted next tick) and rebuilds the glass ::after style (which now uses the live sheet URL).
  Reviewer watch-outs left: body/tail pieces keep their inline background-size/position (hidden under .finWarp); a reset
  landing in the cave hand-over frame can pop up to ~14 px once (photo99 null); per-canvas fin states restart.
  After: all 8 records sane (240 = 0, 360 = 120), every fish draws 3769-4070 px; rig `D:\ClaudeWork\scratch100\
  probe_frag100.py` (headless, 2 males a1/a2, fights forced every 10 s).
- **Nav overlap (separate, real at 1024x768)**: with the page at the top, the fixed bottom navs (`.v8nav` + the old
  `nav.nav`, top y 683) covered the tank's last 45 px (tank bottom 728). Not the cause of the fragment (my first
  diagnosis was wrong). Fix: new block "V17.100 TANK BOTTOM CLEAR OF THE NAV" (before
  `<!-- V17.90 BEGIN -->`): after load and every `switchTankV8` (60 + 400 ms), scroll down just enough that the tank
  bottom clears the nav (never up, not within 1.5 s of wheel/touch, capped so the tank top stays). `tankClearV17100()`.
  Measured at 1024x768: tank bottom 676 < nav 683; 2 males 25 s swimming: always 100 % visible, lowest bottom 669.
  PLAYBOOK §2 updated (anc test fish + forced fights).
- **Belly view (glass)**: two causes in the sheet build. (1) `make_sheet.py`: the belly photo faded out AT the vent, cutting
  its pelvics (they reach ~45 photo px past it), and the 3D render's own fins showed round them = a second fin set. Now
  `SEAM` M 650 / F 580 (35 px fade), render masked to show only behind the seam. (2) `recolor_sheet.py`: the render's
  edge-on tail stick lay over the caudal fan and poked past its notch = "double tail". Now the stick is erased (except the
  last 20 % at the stalk join), the fan lies on top. Backups `out/*_v99_backup*`. Rebuilt sheet90 → sheet97 → install90.
  (A longer male photo seam, 728, was tried and reverted: the fan length is measured from the stick, the fan got short.)
- **Seam lines** on the glass belly: V17.99 FIN99 pectoral-zone bands met with anti-aliased edges → each band now reaches
  1 px into the inner one (drawVentral). Row-profile dip 9-17 → max 3, 0 of 131 glass frames > 6.
- Syntax 0 errors after each edit; reviewer: no blockers. Reviewer watch-outs: keyboard/scrollbar scrolling is not
  detected by the nav block (only wheel/touch); check breeder/shop/dex at 1024x768 for page jumps; FIN99 zones / mouth
  spot were tuned on the old belly look (looked fine in the pane, not measured).
- Fights: 1 full forced fight after the fix (walk → fight → done), fight canvas 553-683, fish fully visible. 3 more forced
  fights all ended in the walk-in (`misaligned` / timeout, males stacked 2-4 px apart facing the same way) = existing
  V17.96 walk-in weakness, not touched. Element boxes reaching 696-702 px are a1's rotated box at the glass corner
  (height 132-139), not visible pixels.
- **Turn glitch + "fins vanish when they turn"** (owner): (1) the 3D turn frames had no visible paired fins: the photo's
  fins/chin bristles hang below its belly (= ground) line, the build clamped them to z >= .012 and the shadow-catcher floor
  hid the rest. `anc_build2.HANG` (default False, only render_turn3 sets it): no clamp, fins never longer than the photo
  (rr <= 1), spread > 1 = wider (tilt .5*spread); render_turn3 lifts the fish to the lowest vertex (0.14-0.16 u = ~5 px)
  and shifts the camera up the same, so the body stays where the photo has it. Re-rendered all 4 → `out/turn100_raw`.
  (2) colour: new `lut_match_photo100.py` matches each type's frame 00 to its own photo cell in sheet97 (brightness raw
  114/89/100/64 → 90/67/81/42, photo 91/68/82/43; the old frames were lighter/yellower) → `out/turn100` →
  `out/atlas100_T` (same names/cells/size as atlas99_T, 1.2 MB). install90 packs atlas100_T. **Commit needs
  `git add -f assets_blender/anc3d/out/atlas100_T.*`** (out/ is ignored; atlas99_T was force-added).
  (3) block90.js turn draw: the photo faded out while the 3D faded in on top → both half-faded = a ~75 % opaque,
  see-through fish at the start and end of every turn. Now the photo stays opaque under the 3D while it fades and only
  fades itself while the 3D is fully opaque (u .15-.25 / .75-.85). Measured (headless, black male): photo 1.00 on every
  3D-fade frame; 3D brightness 68-71 vs photo 67 (olive 88-92 vs 91); 3D px 3228-3490 vs photo ~3900 (was ~2750-3160).
  Grid `AFNICA_Anc100_turn_grid.jpg` (root, git-ignored). Probe `D:\ClaudeWork\scratch100\probe_turn100.py`.
  **49 turn frames** (owner OK'd): the mid-turn pale halo = two neighbouring turn frames blended (k + k2 at mix) while
  ~14 deg apart at peak yaw speed. render_turn3 `TURN_N` (default 48) → `out/turn100b_raw` → `out/turn100b` →
  `out/atlas100b_T` (196 cells, 6240x3520, 2.28 MB WebP, ~88 MB decoded vs 44); block90 turn draw kf=48*u. Game file
  31.3 → 33.0 MB. Halo px from blending (offline, same blend as the game): male mean 248 → 130 / peak 1817 → 966, female
  214 → 105 / 1617 → 810. Cost (headless, 3 males + brown female, turns forced every 2 s, 60 s, wall ms incl. CDP):
  median 15.3 → 16.9, p95 33 → 35, first-turn hitch 618 → 580 ms (the existing atlas decode, unchanged), hitches > 50 ms
  11 → 2 (noise). A faint ghost remains where the tail sweeps fastest. Probe `D:\ClaudeWork\scratch100\
  probe_turncost100.py` (its rAF timer reads 0: the rig's fake clock bypasses requestAnimationFrame; use wall time).
  Grid `AFNICA_Anc100_turn49_grid.jpg`. **Commit: `git add -f assets_blender/anc3d/out/atlas100b_T.*`** (atlas100_T, the
  25-frame version, is no longer used). Brown female turn colour checked: 86-90 vs photo 90 (FO map OK); her 3D frames
  are ~22 % smaller than the photo (fins show less). maps97 (built from turn95) unchanged.
  Reviewer (no blockers): decoded atlases now ~310 MB in total (C2 ~150 + P ~75 + T ~88), heavy for phones/iOS; the
  first-turn hitch (~0.6 s) is the lazy T decode - a one-time off-screen warm-up draw at boot is untested (the earlier
  keep-warm every 2 s was worse). `out/atlas100_T.*` is a leftover, keep it out of git.
- **Two on the glass on top of each other** (owner screenshot): the glass neighbour test was 48 px with the height x .7
  (a head-up fish is ~70 x 120 px → half a body could overlap) and only ran while grazing; the climb always lands in the
  wall corner (s.x = lo/hi) and moves on the glass never looked. V17.100 (HTML ~7870-7945): climb picks a wall whose
  corner is free (no glass fish within 130 px of lo/hi, nobody climbing there) else the other wall else stays on the
  sand (`wl100`); glass graze + glass move refuse a step that overlaps (|dx| < 60, |dy| < 110, x scale) AND gets closer
  (`ov100`/`blk100`; moving apart always allowed); next patch 70/45 px away. Probe `D:\ClaudeWork\scratch100\
  probe_glass100.py` (180 s, 2M+1F, climbs nudged every 3 s): HEAD 3462 frames with 2 on the glass, all > 25 % overlap
  (worst 100 %); now 1510 frames, 0 overlap, no errors. After the reviewer: a fish in toEdgeG counts as taking that
  corner; short of oxygen (`up`) a fish always climbs (the freer wall). Rerun 120 s: 2382 frames with 2 on the glass,
  0 overlap. Not tested: low-oxygen mode with 3+ fish (glass band only ~45 px tall there), young fish, a very narrow
  tank (one glass fish can make both corners "busy"); fish meeting head-on on the glass both stop and wait 15-30 s.
- **Rasping on the glass** (owner: "now I have no rasping"): it runs (V17.99 jaw99, ±7 deg turn of the inner mouth inside
  the still disc, in bouts) - rig: black male mouth area changes on 433/1008 glass frames (HEAD 316), female 113 - but
  it is nearly invisible at game size (mean pixel change 2-5/255 on a ~10 px disc). Before today the brown female's glass
  picture came from the wrong sheet (the load race), which may have looked "active".
  **New rasp (owner OK'd the mock-up `AFNICA_Anc100_rasp_mock.png`)**: `jaw99` (V17.42 fin code) now slides the two jaw
  halves (body side / snout side of the inner disc) apart along the fish axis and back, the dark mouth opening between
  them; lip ring still; smooth tanh push (sh .38 ri, soft .2 ri), same bouts and 3 Hz strokes. Cached per record
  (`r.j100`: src ImageData taken once from r.base, warped per frame on a ~27x27 patch). .22 was too small at game
  resolution (~2.2 px per css px); .6 breaks up. Measured: mouth change black male mean 4.3 (was 2.2, peak 20 vs 5.4),
  female 704/1202 glass frames moving (was 113). Images: `AFNICA_Anc100_rasp_game.png` (game resolution x10),
  `AFNICA_Anc100_rasp_game_burst.jpg` (12 frames of a burst from the game canvas). Mock-up script
  `D:\ClaudeWork\scratch100\rasp_mock100.py`, probe `probe_rasp100.py`. Reviewer: no blockers; patch now snapped to
  whole pixels (no soft mouth at a bout start); 40 s rerun black male: 660/1008 glass frames moving, mean 6.7. Still to
  eyeball in the pane: a faint double edge at the patch rim at peak opening (non-premultiplied alpha).
  After the commit (4d3a126), NOT committed: rasp slowed 3 → 1.8 strokes/s (owner: "a little too fast"); male belly tail
  (owner: "the tail looks wrong" - thin render neck then a small fan): make_sheet SEAM M (690, 14), no render in the
  male belly cell; recolor_sheet male branch hangs the side photo's caudal on the end of the photo's broad stalk.
  Owner feedback rounds: (690 seam + 110 px fan) put the fan right behind the pelvics, body looked short → final: SEAM M
  (733, 12) = the photo stalk to its end (long, like the real belly), fan `FAN_L` 88 px / `FAN_H` .85, 15 % overlap,
  and every fan column re-centred on the body axis (owner: "the caudal must look straight, not diagonal"). Female
  unchanged. Images `AFNICA_Anc100_tail_long.png` / `_tail_straight.png`. Backups `out/sheet9x_v100a_backup.webp`.
  Then the owner's reference photos (real bristlenose seen from below): resting, the caudal stands upright against the
  glass → seen edge-on, a thin line continuing the tapering stalk; moving, the tail curves. → `FAN_H` .22 (edge-on
  caudal, `AFNICA_Anc100_tail_edge.png`) and drawVentral(..., bend): the tail lags glass turns as a C-bend (gain .16 BL at
  90 deg/s, max .2, from the element's rotation speed smoothed; sign worked out for both scaleX) and the crawl sway is
  .055 (was .032, bristle layer too). Rig `D:\ClaudeWork\scratch100\probe_bend100.py` → `AFNICA_Anc100_tail_bend.jpg`:
  curves while turning, straight at rest, no errors. Female glass tail still the old fan (her photo curls).
  Owner: "the tail looks very shortened" → make_sheet `MK100` .86: the male belly photo drawn 14 % smaller around the
  mouth (same cell length, mouth spot unchanged), the stalk ends at x 149 and the edge-on caudal fills the cell to the
  tail edge (`FAN_L` auto = (xe-6)/.85, max 170). Tail ≈ 40 % of the fish from the pelvic tips (reference ~45 %).
  `AFNICA_Anc100_tail_prop.png`, `_tail_bend2.jpg`. Watch: FIN99 pectoral zone (u .23-.62) and the t99 bristle cut-outs
  were tuned on the old scale (pectorals now ~.03 u nearer the snout) - looked fine in the rig, not measured.
  Owner: "a thinner part between tail and body" = the squashed caudal root (12 px) under the stalk end (29 px) →
  every caudal column at least a straight taper from the stalk's end height (measured 10 px inside the stalk) over 45 %
  of the caudal; root no longer faded. Height along the tail now 47 → 34 → 24 → 16, caudal tip ~24
  (`AFNICA_Anc100_tail_join.png`).
  Owner: "visual corruption" at the join (per-column squash/re-centre = jagged, streaky; fin root lines; the photo's
  feathered cut edge). Male caudal rebuilt in recolor_sheet.py as one smooth shape: anchored at the first clean stalk
  column xg = stalk end + 25 px (the last 25 px are the photo's feathered cut edge, trimmed and covered), outline =
  one taper from the stalk's height at xg to ~10 px at the tip (no waist/spearhead), fin texture mapped across it
  (anti-aliased), root textured with the stalk's last 30 px mirrored back and forth (scutes continue) blending into the
  fin texture toward the tip, root fade over 15 px of clean stalk. Height along the tail 54 → 13 px, monotonic.
  `AFNICA_Anc100_tail_join2.png` (zoom), `AFNICA_Anc100_tail_final.png`.
  Owner: "the end of the tail doesn't look right" = the tip was cut flat by the cell edge (caudal started at x < 0).
  Now Lf = stalk end - 4 (tip 4 px inside the cell) and the taper ends in a soft ~3 px point.
  Owner's reference pair (still on the glass = thin edge-on tail; moving = curved tail + the caudal turned into view as a
  fan): drawVentral(..., bend, fan) - males only: the fan is the fish's own side-view caudal (cropped once at runtime
  from the side record 'anc|col|38', 21 % of its BL, cached as r.fan100, retried until the side record exists), drawn
  from the fin root (.17 BL from the tip) along the bent tail, height edge-on → full with `open`; open = smoothed
  (rate 4/s) min(1, stroke*.8 + |bend|/.1) → closes when he holds still. `AFNICA_Anc100_tail_fan_moving.jpg`.
  Not yet: the female (her glass tail is still the old fan), the fan's own flutter.
  **REJECTED by the owner ("that's not how a bristlenose moves his tail", "like a helicopter")**: the turn bend and the
  opening fan were invented, not copied from footage. Both switched OFF (test flags `window.ANC100BEND` /
  `window.ANC100FAN`, never set by the game); crawl sway back to .032. Kept: the thin edge-on tail at rest (from the
  owner's photo). Next: get a real clip of a bristlenose crawling/turning on the glass (belly to camera), copy it frame
  by frame, show a still/few frames first.
  Owner's clip: `C:\Users\Alexandru Nica\Downloads\The Ancistrus catfish dances on the glass...mp4` (copy in
  `D:\ClaudeWork\anc_clip\clip.mp4`, 18 s, 720x1280; frames via headless Chrome `D:\ClaudeWork\scratch100\clip_frames.py`,
  no ffmpeg on the laptop). Read at 15.0-15.8 s (15 fps): head + body stiff to the pelvics, only the stalk + caudal (rear
  45 %) wag side to side ~2.1 Hz, tip ±~12 % BL, tip lagging; caudal edge-on crossing the middle, ~half open at each end;
  only while moving, still = straight + edge-on. Implemented behind the test switch `window.ANC100WAG` (off): wag term in
  drawVentral (rear 45 %, ^1.6, lag .9 rad), envelope from the real glass speed (bounding-box centre, smoothed) or the
  stroke gate, the side-view caudal drawn as the twisting fan (open .5·|sin|). Rig `probe_wag100.py` →
  `AFNICA_Anc100_wag_game.jpg` vs `AFNICA_Anc100_wag_clip.jpg`. Owner OK'd → ON by default (`window.ANC100WAG=false`
  switches it off). Males only; female glass tail not done yet. Owner: "the tail duplicates" = the separate side-view fan
  overlay sat beside the wagging sheet caudal → overlay removed; the caudal columns (u > .85) themselves get taller with
  the twist (x 1 + open·2.2), one tail (`AFNICA_Anc100_wag_game2` = scratch wag2.jpg).
- Dark smudges under the male's fins on the sand (owner): leftover background in `incoming/anc_mfull_side_cut.png`
  (since V17.98 or earlier). Cleaned copy `incoming/anc_mfull_side_cut_clean100.png` (original kept): the flat dark block
  under the pectoral edge (x 902-933, y 413-441, max rgb < 55 → transparent, 564 px) + loose pieces not connected to the
  fish below the belly line and behind the head (y >= 395, x < 1130: under the pelvic, a speck under the head; 806 px in
  all - the bristle tips that look detached stay). make_sheet SIDE M uses the clean copy. Dark opaque px under the
  pectoral 83 → 19 (olive) / 32 (black) = the fin's own. `AFNICA_Anc100_side_clean.png`. 3D renders still use the
  original photo (not needed).
- Open: male stalk between pelvics and fan is a bit narrow/soft at the photo→render join; female not checked on the
  glass in this session; fight walk-in aborts.

# Earlier (2026-10-18: V17.99 ANCISTRUS FIXES, all 7 owner points APPROVED, NOT committed)

## V17.99 bristlenose fixes (owner's 7 complaints; spec `docs/ANCISTRUS_SPEC.md`, sources + targets)
Order done: 2 → 3 → 4 → 7 → 6 → 5 → 1, each measured, one frame grid each (`AFNICA_Anc99_*_grid.jpg` in the root),
reviewer after each. Syntax check 0 errors after every edit. **Nothing committed** (owner decides). V17.97/98 also still
uncommitted (see below).
- **2 sand → glass "teleport"**: the fish was INVISIBLE ~1.5 s of every climb (V17.97 side/belly opacity swap at glass .42-.58
  while the belly canvas only shows from .999). block90.js: swap at .999, following the canvases' real visibility. Rig:
  0 invisible frames (was 45).
- **3 cut-offs + tail + roll**: male belly bristles ran past the 120 px cell, female fin past 70 px → `make_sheet.py`
  MDX -5 / FDY -2 css px (adult belly cells only), ::after mouth CSS moved for adults (young rows keep the old spots);
  belly tail fan 70 % (was 30 %, "stick with a blob") in `recolor_sheet.py`; drawRoll LAG 0 (whole body rolls, no
  half-side/half-belly twist). Sheet rebuilt (backups `out/*_v98_backup*`). 0 opaque border px on adult belly cells.
- **4 cave entry**: walk-in frames ramped over the lip, ~10 px off the fanning pose → `render_cave2.py` pose('i') levels onto
  the floor from d 30 and arrives at d 74 in the fan pose; d >= 32 re-rendered (`out/cave99`) → `out/atlas99_C2`.
  block90.js `xfade99`: photo→cave hand-over registered (alpha centroids). Jumps 10-12 px → < 1 px; hand-over 4-8 → ~1 px.
- **7 glass crawl + mouth** (2nd attempt): V17.42 `drawVentral` FIN99 = pectorals swing out as a continuous warp (0 at the
  body, ~8 deg), `jaw99` = jaws rasp ±7° at 3 Hz in bouts inside a still disc (::after bubble hidden), midline seam
  closed; glass rock 3.5 → 1.5°.
- **6 bristles**: V17.42 `t99prep/t99draw`: adult male side + belly cells, bristles cut out by alpha opening, head drawn
  without them, bristle layer moved per pixel (tip-weighted spring trailing the head + slow sway). Rest ~1 px, moving up
  to 3.2 + 2 px. Test hook `window.__T99` (never set by the game). 3D frames (turn/cave/fight) still have baked bristles.
- **5 fights**: `render_fight.py` re-posed (yaw ≤ 8° was 22, curl ≤ .34 was 1.05, tail beats 2.5 Hz, shoves along the body)
  → `out/fight99` (colour by LUT `lut_match99.py` from fight97_raw→fight97, exact) → `out/atlas99_P`. Walk-in: no walk
  round the rival's head + U-turn; if the intruder is behind, the rival turns to face him (leg 3), else straight in.
- **1 turning**: `render_turn3.py` head leads, tail lags 0.24 s, C-bend peak ~35° at the oblique views → `out/turn99`
  (`lut_match_turn99.py`) → `out/atlas99_T`. block90.js: attach/detach/wallHold/toEdgeG no longer steer the drawn facing
  (the corner slide flipped him flat): 0 flat flips outside the cave (was 2-4 per fish / 4 min).
- install90.py now packs atlas99_T / atlas99_C2 / atlas99_P. Rigs (trailer/): `measure_diag99.py` (SCN=cave|cave2|fight,
  PC=1 pixel centroids, CV=1 cave canvas, XF=1 hand-over), `probe_roll99/cut99/cells99/cave99/fin99/tent99/t99.py`,
  `grid99.py` (GRID=roll|cave|glass|tent|fight|turn, SEX=M). `measure_fight96.py` needs SEED set (else a JS error).
- Open / not checked: female + juvenile on the glass (fins/jaws), bristle pop at the roll start/end, frame cost with 3+
  males, walking out of the cave hand-over, cheek odontodes not modelled (fights), fight walk-in took 12.8 s once.
- **Perf (after the push, commit 43071fb)**: 3 males cost ~2.6 ms/frame more than 4 females (bristle layer). Fixed a
  ~1.3 s freeze at the first cave approach (xfade99 read the huge atlas on the CPU → precomputed CEN99; recol97 no
  willReadFrequently; atlas99_C2 repacked 8160x4620). STILL OPEN: 0.3-0.5 s hitch in busy tanks when the cave male first
  draws / a fight starts = Chrome re-decoding an evicted atlas (~150 MB RGBA) in drawCave blit's restore (profile:
  `trailer/probe_prof99.py A B`). Tried: smaller repack (no help), 1 px keep-warm draw every 2 s (worse: re-decode each
  time, reverted). Untried: createImageBitmap per atlas (~270 MB kept decoded) - owner to decide. Rig `probe_cost99.py`.
- Owner: no session clips / frame grids in git (ignored `/AFNICA_Anc9*.mp4|jpg`, kept on disk); atlases/sheet/maps tracked.
- **Owner's C: drive is full** (81 MB free): `C:\Users\Alexandru Nica\.claude\file-history` = 3.9 GB of Claude edit
  backups; suggested robocopy /MOVE to D:\ClaudeData + mklink /J (owner does it with the app closed). Scratch now in
  `D:\ClaudeWork\scratch99`.

# Earlier (2026-10-17: Phases 1-3 APPROVED — turn V17.95, movement V17.95, male fights V17.96)

## In progress: V17.95 PIVOT TURN (owner prompt: Phase 1 turns → Phase 2 movement → Phase 3 male fights)
- Diagnosis done + owner OK'd the pivot plan. Ref turn: B7RksQ1xU18 0:25.4–0:27.8 (dark common bristlenose pivots almost
  on the spot ~2–2.4 s, pectorals spread, gentle curve, head away / tail toward viewer). Before: old `turn()` (line ~7739)
  freezes the fish 0.8 s, V17.94 walks the drawn fish 39 px out and back = **6.2 px/frame** (rig `trailer/measure_turn95.py`,
  60 s, 1M+1F: 4 turns, all old-driven, 0–1 backward frames, no errors).
- Done (NOT installed in the game HTML yet): `anc3d/render_turn3.py` (pivot frames, R .12, bend .3, smootherstep),
  rendered + colour-matched to `anc3d/out/turn95/`, packed `anc3d/out/atlas95_T.webp/.json` (same names/cells as atlas92_T).
  `anc3d/block90.js` patched: `ancTurnSecV1789=2`, facing-follow turns `TF=min(T,1)`, walk/translate removed
  (backup `out/block90_v94_backup.js`).
- INSTALLED 2026-10-17 (install90.py → atlas95_T), syntax 0 errors. Measured (seeds 3/7, 60 s, before → after): turn
  0.8 s → 2.0 s, drawn drift 39 px → 0, max step 6.2 → ≤1.0 px/frame (fish-wide max now 2.58 = cave approach, unchanged),
  no errors. Female backward frames (graze 19–42, attach 20) exist before and after: old code slides a grazing fish before
  the facing-follow turn reacts (0.6 s) + the attach corner move → Phase 2 / first-list item 7.
- Reviewer: no blocker. Watch for: old turn() holds the fish still for the whole 2 s (by design) but ignores a target
  flip mid-turn → up to ~4 s still (wafer crossing the fish, cave doorway ±3); fry follow-turns (1 s) slide while the old
  code moves them; stale `ancTurnSecV1789=1` at ~line 13201 (overridden later).
- **Owner APPROVED the pivot turn (2026-10-17)** after checking it in the Browser pane. Not committed yet.
- Phase 2 (movement, ref. B7RksQ1xU18 whole clip): video table given to the owner (rests flat 0:09-0:14/1:04/1:28, creep
  0:15-0:22, dart 0:22.3, glide 0:32-0:36, head-down rasping 0:43-1:02, glass slide-down TAIL FIRST 1:34-1:41). Owner picked
  1-3, skipped 4 (leaving the glass; open question: is the real tail-first slide allowed?).
- **V17.95 BRISTLENOSE MOVEMENT** (section in `anc3d/block90.js`, installed; switch `window.ANC95=false`; counters
  `anc90Debug().D95`): darts (25 % per move/toWall trip once facing the target + a timer every ~1-2.5 min × activity from
  graze/rest, pivots first if the room is behind; burst ≤ 1.6 s, peak 1.8 BL/s = 6.0 px/frame — owner-accepted exception;
  never across the cave or into a wall), longer rests (30 % of grazes → rest, 6-15 s) with dorsal flat and still tail,
  grazing sessions 10-20 s with 3-6 s rasp phases and a head-down tilt ≤ 11° around the snout (stacks on V17.89's 2.4°).
  Skipped in the breeder (`via==='breed'`) and for young/fry/cave modes/glass. Rig `trailer/measure_move95.py`
  (AT1 = put the female on open sand: in the rig scene she lives in the 100 px gap between cave and wall, no dart room).
  Measured (180 s, before → after): rests ~3 s → 10-19 s; rasp tilt 2.4° → 11°; darts 0 → 2-3 per 3 min, 1.6 s each;
  max step outside darts 2.58 (unchanged); night: shorter rests/grazes (more active); no errors.
  Still open: backward frames in attach/detach (old corner move = item 4).
- **Owner APPROVED Phase 2 (2026-10-17).** Not committed yet.
- Phase 3 (male fights, ref. youtube.com/shorts/R6KUQ73HhlI) started: check existing anc male code, analyse the short,
  propose, then a still of the pose before animating.
  - Existing code: only `ancTerritorialClashCheck40` (line ~8105, daily 6 % health hit + toast, no animation); V17.48
    fights cover livebearers only. Owner OK'd the plan: trigger 2+ adult males within ~1.2 BL (x4 with a cave or female
    near), one fight per tank, cooldown per pair, more at night; sequence approach → broadside (dorsal up) → head-to-tail
    with 3-6 tail sweeps → short head shove (< 1 s, never frozen) → half circle, maybe repeat; winner = cave holder > size >
    health + luck; loser pivots + darts away and avoids the cave; health stays with the daily check (fight is visual).
  - Still: `anc3d/still_fight.py` → `AFNICA_Anc95_fight_still.jpg` (head-to-tail, dorsals up, rear male curled).
    Owner OK'd the still (2026-10-17).
  - **V17.96 BRISTLENOSE MALE FIGHTS** (section in `anc3d/block90.js`, installed; switch `window.ANC96=false`; force the
    next fight `window.anc96Force=1`; debug `anc90Debug().F96/CD96/C96`): pair frames `anc3d/render_fight.py` (60 frames:
    A settle 12, B tail sweep 12 cyclic, C shove 15, D half circle 21, 15 fps, both males in one 300x130 frame, pitch 8)
    → `out/fight96` → `out/atlas96_P` (1.0 MB). Rates: 1/20 s within 2.5 BL, 1/60 s farther (one seeks the other), x4 cave
    holder (last 2 min) or female near, more at night; cooldown 3 min per pair. Attacker walks (round the rival's head if
    from behind), rival lies still; 3D plays 3-6 sweeps + shove + half circle (30 % twice), photos faded; winner rests,
    loser darts away. Not in the breeder. Rig `trailer/measure_fight96.py` (2 males, 5 min): 1 fight in 4 of 6 runs,
    walk 6-7 s, 3D 6-12 s, ends "done", max step outside darts 2.58, no errors; end + tank-switch abort leave no
    frozen fish / canvas / faded photos.
  - KNOWN GAPS: a male in his cave cycle never fights (with a female in the tank the cave male is busy most of the time,
    so no fights there) → cave defence = follow-up; loser does not avoid the cave; walk-in passes over the rival's body;
    a water change mid-fight leaves both frozen until it ends. Reviewer otherwise OK.
  - **Owner APPROVED Phase 3 (2026-10-17)** after checking it in the Browser pane. All three phases approved; nothing
    committed yet (owner decides when). Next candidates: cave defence (task card proposed), leaving the glass (item 4,
    needs the owner's ruling on the tail-first slide), the items from the owner's first prompt list.
- After the push (f72d546), NOT committed yet (owner feedback while watching the pane, 2026-10-17):
  - Rasping must not lift the body at all: V17.95 pose off (`const on=false`), V17.89 rasp tilt off (`0*s.tilt89` in the
    HTML). The remaining sand tilt is the V17.89 climb over the cave tube (ovA89), not rasping.
  - Glass "corruption" at the mouth = the old `.ancGlass::after` mouth patch squashed an oval smaller than the disc
    (ring + smeared tentacles). Owner then missed the mouth movement → V17.97: a circular copy of the oral disc swells up to
    10 % (always covers the original; tentacles untouched). Black male keeps the photo's pale oral disc (recolor_sheet.py).
  - Glass view tail: a 30 %-high fan of the side photo's caudal laid under the edge-on tail line (recolor_sheet.py).
    Male bristles: sway ~3x stronger (r.W/60 instead of /170, HTML fin code) and never stop (phase speed >= .6).
  - Cave "teleport": the old 'cave-turn' mode (he backs out to the mouth and goes in again) was missing from V17.90
    CAVEMODES → the photo popped up ~13 px higher for 0.5 s while the 3D still showed. Added; rig shows only the smooth
    approach fade now.
  - Glass gait (owner: "swims on the glass"): V17.89 glide was a steady 12 px/s. V17.97 wraps ancGlideV1789 into push
    (0.4-0.8 s, eased) + grip (0.5-1.2 s), peak 0.68 px/frame, avg ~5 px/s (switch window.ANC97GAIT=false); the stroke
    signal (ancStroke: pectoral steps, tail wave) follows the pushes (HTML ~13318). Glass tentacles froze while gripping
    (phase only advanced with strokes) → always >= .5 speed (HTML fin code).
  - Fish sunk below the sand in a short tank (Browser pane 813x388: sand strip only 68 px, fish line at 56 % of it put
    the 70 px sprite past the bottom edge): bristlenose `base` now = min(old, h-52*scale) (HTML ~7766); 960x540 unchanged.
  - Fish "cut off" away from the cave: V17.89 place() leaves its cave clip-path polygon on the element after the cave
    cycle; V17.97 removes it in every ordinary mode (rig 2x300 s: 0 masked frames outside cave modes).
  - Female mouth pulse off (`.ancFemale .ancGlass::after{display:none}`): the ghost second ring in the female belly
    photo made the copied disc look broken. Males keep the pulse. (Fixing the female belly asset itself = follow-up.)
  - Side <-> belly view on glass transitions: was a linear cross-fade over the whole transition (double image ~70 % of
    it); now a quick smoothstep swap around --anc-glass .42-.58 via --anc-sop/--anc-gop (both visible 5 %).
  - V17.98 turn: the pivot swung the head away, so mid-turn showed only the tail fan (owner: "cut-off"). render_turn3.py
    now turns the other way (head toward the viewer, face + bristles mid-turn) → `out/atlas98_T`.
  - V17.98 fight: owner: "they don't circle each other, they hit each other with their spines". Phase D = spine strikes
    (rear male jerks his head into the other's flank, fast in / slow out, then the front male strikes back; nobody changes
    sides, so the photo flip is off: F.nD=0) → `out/atlas98_P`. Rig: 3 mixed fights "done", no errors.
  - Turn bend (owner: "turn with a bend of the body, not flat"): render_turn3.py bend -.95 (C-curl mid-turn) → atlas98_T.
  - Turn flicker / "vanish + corruption on the glass transition": 3D turns started during attach/detach and were cut
    after a few frames (photo dipped to 0, side frames over the belly view); one female's facing-follow turn reversed every
    frame and sat at u~0 for 27 s (ghost 3D over the photo). Now: no 3D turn while glass>.02 or attach/detach/wallHold/
    toEdgeG (TRANS97), and a facing-follow turn starts or reverses only after the wanted facing held .25 s. Rig 150 s:
    every turn one clean 63-frame run, no blips.
  - Mouth on the glass: V17.89 set --anc-mouth 1 during every hold (5-14 s) → no rasping while still. Removed (HTML
    ~13318); mouth pulses 80 % of glass grazing. Females get a milder pulse (circle 6.4 px, up to 1.05).
  - OPEN (owner, 2026-10-17, end of this chat): "fish disappear / appear, cut-offs". 45 s of per-frame sampling in the
    Browser pane (2M+2F, fights forced) found 0 frames with a fish invisible outside cave/fight 3D; could be an old copy
    in the owner's own browser tab (Ctrl+F5). Next session: reproduce in the owner's window size, record the exact moment.
  - Other open items: female belly photo has a faint second ring around the mouth disc (sheet asset); dex/shop thumbnails
    use the photo colours; water-change freeze (fish stuck above the water line); cave defence (task card); leaving the
    glass tail first (owner's ruling). ALL of V17.97/98 is uncommitted (owner did not confirm yet).
  - **V17.97 colour for life**: every non-fry fish keeps its id-hash colour ('o' olive-brown / 'b' black) as an adult.
    Sheet 4 columns (`recolor_sheet.py` → `out/sheet97.webp`: col 240 black male, col 360 brown female; brightness
    histogram match + tint). 3D frames (turn T, cave male layers C2, fight P) recoloured per frame on demand in the
    browser (`recol97`, maps `make_maps97.py` → `out/maps97.json`). Fight atlas now per-fish layers (`render_fight.py`
    4th arg = layer, holdout) → `out/atlas97_P` (1.7 MB); odd number of half circles flips both photos at the final fade.
    HTML patches outside the block: fin-canvas cell mapping (~8721), PFIN aliases 240/360 (~13474), male bristles for
    'anc|240|38' and 'ancg|240|138'. Checked headless: all 4 adult colours, juvenile→adult keeps colour, mixed fights end
    "done" with correct facing, no errors. Reviewer OK after fixes. Not shown: dex/shop thumbnails still use the photo
    colours. Water-change freeze (fish stuck above the water line) = next, owner asked.

# Earlier handoff (2026-10-13)

## Latest: BRISTLENOSE 3D (V17.90) — in the game, not committed; owner watching the 1 male + 2 females session

Owner judged V17.89 "hideous"; audit image `AFNICA_Anc90_audit.jpg` (9 states, ref vs game). Method chosen: real 3D
fish made in Blender, rendered to sprite frames. Everything is in `assets_blender/anc3d/` (see the header of each script).
- **Models** (`anc_build2.py`, `anc_build.py` = cave/scene/clearance helpers): built from the owner's Gemini specimen photos
  in `assets_blender/incoming/` (memory "anc-specimen-photos"): full-grown male olive-brown with bristles, female black
  (owner: keep both colours, "the fry will come out mixed"). Side photo -> flanks/dorsal/caudal, top photo -> back +
  pectoral/pelvic fins (flat like wings), belly photo -> underside. Male top photo nostrils toned down (`prep_photos.py`).
  Photos cut by `cut_photo.py`. 3D bristles = curves. Units: 1 = 32.5 game px.
- **Frames** (`render_frames.py`, `render_cave.py`, packed by `pack_atlas.py` into WebP sheets): per sex yaw 0..90 (mirrored
  for the other half), crawl x8, rasp x2, swim x6, glass belly x3 (160x90 game px, pivot 77.7,48.4). Cave: tube + male
  together, 340x110 at (cave.left-160, cave.top-30), mouth (173.8,72): empty, in -20..140, fan x12 (tail out), out -50..120.
  Every cave frame is checked: no fish point inside the clay (`clearance`).
- **Game block** V17.90 at the end of the HTML, between `<!-- V17.90 BEGIN/END -->`, source `anc3d/block90.js`, installed by
  `install90.py` (re-run after any change; it replaces the block). Wraps `ancPostV1789`; draws only. Turn = real yaw through
  depth (`ancTurnSecV1789`), crawl frames advanced by distance, drawn facing follows sustained movement on the sand (never
  drawn backwards), glass blend by `--anc-glass`, male in cave modes -> composite cave frame (his element opacity 0).
  Spawning visit (breeder, stage 'spawning') keeps the OLD drawing; young/fry use the adult frames (male frames if no sex).
  Switch `window.ANC90=false`; debug `anc90Debug()`.
- **Old-code fixes** (marked V17.90): attach/detach duration scales with height (was a fixed 7 s: up to 6.4 px/frame);
  glass grazing turns head first toward the patch and glides only when aligned (used to slide down tail first);
  toEdgeG heading +180 instead of -angle; with eggs/fry the male keeps fanning head-in/tail-out (no head-out guard; owner:
  head-out = inviting a female, memory "bristlenose-cave-poses").
- **Measured** (`trailer/measure90.py`, seeds 3/7/11/19, 90 s, main tank 1M+2F): max step 2.58 px/frame, male 0 backward
  frames, females 0-2 on the sand (the rest are the corner manoeuvres of attach/detach), glass 0-6 % against the heading
  (while turning), 45 cave frames used, no console errors. Spawning visit test (`trailer/test90spawn.py`) ok.
- Clips: `AFNICA_Anc90_clip1.mp4` (first 3D test), `AFNICA_Anc90_session.mp4` (game session 1M+2F, `trailer/takes90.py`).
  Browser pane: `.claude/launch.json` has `afnica-pane` (port 8791) - the pane can only open servers it starts itself.
- aquarium-reviewer: fixed spawning() (st is a top-level let, not window.st), shadow class cleanup, male-only cave frames,
  broken-image guard, old cave hidden only after the new tube is drawn. Left: the old fin canvas / anc3dV1789 still run
  hidden (cost only); young fish need their own frames; on-the-glass belly photos were never generated.
- **v2 (owner: "complete shit", "look like a placeholder")**: side-on frames (yaw00, crawl, rasp, swim) are now the owner's
  photos themselves (`photo_frames.py`, soft painted contact shadow); 3D only for the turn (yaw15-90: dorsal up, paired
  fins + bristles cut from the SIDE photo = `paired='side'` in anc_build2, EMIT .75, pitch 3) and the cave frames.
  Still `AFNICA_Anc90_ingame_v2.jpg`. Open: in the cave the side-photo fins dip ~0.03 units (1 px) into the clay floor
  inside the tube (invisible, but tuck them tighter); young/fry frames.
- **v3 (owner: "fins don't move, no rasping on the glass - a step back")**: the OLD animated drawing is back (V17.42 fin
  canvas: stepping fins, body flex, breathing; V17.89 flat pectorals; glass mouth pulse) but runs on the owner's photos:
  `make_sheet.py` rebuilds the old 1254x1254 sheet layout (side photos aligned to the old snout/tail/belly line; belly cells =
  belly photo mouth->vent over the 3D glass render) = `SHEET` in the block, applied by `html .ancArt i{background-image}`.
  Female flat-fin polygons replaced at load (`ancDebugV1789().PFIN['anc|120|38']`, from `sheet90_pfin.json`).
  `ANC3D_V1789=false` (the shader path did not step the fins). V17.90 now draws only the TURN (3D yaw frames while
  f.turn / s.turn, old drawing hidden, that fish's shadow hidden) and the CAVE composites. Clip `AFNICA_Anc90_session_v3.mp4`.
- **V17.91 BRISTLENOSE LIFE 2** (owner: "do all - more realistic"), logic in `anc3d/block90.js` (section V17.91) + small
  hooks in the old code (`anc3d/patch_v91_game.py`, all marked V17.91): `DFOLD` dorsal fold in V17.42 draw(); per-fish inputs
  via `window.ancCanvasV1791` (fold at rest, raised when moving/swimming/fanning/courting/another anc within 75 px; snout
  pressed down when crawling, grip pulse ~1.5 Hz when rasping on the sand; tail sway; swim = stronger faster beat; male
  bristles idle sway); breathing `BRS.anc` r 50 + `vis` 2.2 (visible low gill slit); glass mouth grip-and-release
  (`--anc-mouth`) + small head turns; crawling in bouts (wrapper on `ancSandSpeedV1789`: 1.6-3.4 s walk, 0.35-0.95 s stop);
  pause 0.8-1.4 s with the snout at the cave mouth (main-tank first entry + V17.89 'enter'); cave in/out frames with wriggle
  variants a/b (bend +-0.2) picked by distance moved (`wig91`), depth normalised by the male's scale; chin bristles never
  below the ground. 118 cave frames, all clear of the clay. Drawn facing follows sustained movement again (old code slides
  a grazing fish out of the cave zone sideways). Clips `AFNICA_Anc91_tank.mp4`, `AFNICA_Anc91_cave.mp4`.
  Item 8: FRY done - owner's fry photos (side/top/belly, `incoming/anc_fry_*`, cut with `anc3d/cut_soft.py` to keep the glassy
  fins) are new rows of the sheet (now 240x620 css: fry side y 238, belly 338; juvenile rows 438/538 reserved); a fish
  younger than 5 days gets `.ancArt[data-stage91=fry]` (`stage91()` in the block) and the V17.42 fin canvas crops
  `anc|sx|238` / glass `ancg|sx|338` (adoptAnc / adoptAncGlass patched, marked V17.91). JUVENILES (age 5..S.anc.adult):
  `data-stage91=juv` + `data-col91` o/b chosen from a mixed hash of the fish id (owner: "the fry will come out mixed");
  sheet rows 438 (side) / 538 (belly), column 0 olive, 1 black; both side photos are in (`incoming/anc_juv_olive_side*`, `anc_juv_black_side*`),
  missing cells are filled with the adult cell of that column by `make_sheet.py` until the photos arrive (black juvenile
  side, juvenile belly). Adults still take their colour from the sex (male olive, female black).
  Later the same day: all juvenile photos in (side/top/belly, olive + black; belly photos placed whole with the cut tail end
  faded), nostrils toned down (`prep_photos.py` -> `*_top_fix.png`), 3D juveniles `SPEC['JO'/'JB']` in anc_build2 ->
  turn atlases `atlas90_JO/JB` (ATL.JO/JB in the block); fry keep the flat turn; facing thresholds scale with the fish
  (young react after 0.3 s). Reviewer fixes: body/tail pieces re-pointed on a stage change, `typeof S` for the adult age,
  juveniles never use the adult cave frames. Mixed tank (2 adults, 2 fry, 3 juveniles, 90 s): max 2.58 px/frame, no
  errors; 3-9 % backward frames on the young, mostly the corner climb (attach) and short hops. Clip `AFNICA_Anc91_family.mp4`.
  Note (old code): young males are drawn as females (no bristles) until they mature, so they show the female/black cell.
- **V17.92 natural turn + cave entry** (owner: "fix how they turn and how the male enters the cave"):
  turn = 13 U-turn frames per fish (`anc3d/render_turn.py`: head swings toward the viewer, body curled in a C, tail
  follows), colour-matched to the photos (`colour_match.py`), driven by the old turn's own timer `s.turn` (fish stays put)
  or the facing-follow; photo <-> 3D cross-fade over the first/last 12 %, the old shadow fades with the photo; only when
  level (rotate < 10 deg). Cave = tube alone (`C_tube00`) + the male as two layers split by the mouth plane
  (`render_cave2.py`: `_out` in front, `_in` shown only through the mouth ellipse 7x22.6 at 173.8,72), frames every 4 px
  + the remainder as a sub-pixel shift (smooth), path: side-on at d -64, lines up with the tube by -10, climbs over the
  lip edge (straight body resting on the edge, tail on the sand, levels inside), body undulation tied to distance;
  hand-over cross-fades d -64..-48 / 108..124. Folded fins now lie back along the body (anc_build2 side fins). Clay check:
  entry/exit climb clean; level-inside/fanning poses <= 0.0106 units (0.3 px) and only in the hidden `_in` layer.
  Atlases `atlas92_T` (0.47 MB), `atlas92_C2` (1.2 MB); old M/F/C/JO/JB atlases dropped (block 2.8 MB, was 3.6).
  install90.py now retries the write (the file is sometimes locked by a reader). Clips `AFNICA_Anc92_cave.mp4`, `AFNICA_Anc92_turns.mp4`.
- **V17.93 round 2** (owner: male drops from above the sand to the cave level; fanning tail not smooth; turns still
  unnatural): the tube stands ~17 px lower on screen than the fish lane (closer to the viewer) -> the male walks down to
  it gradually (`dy` in caveState: d -64..-10 in, 70..124 out); his outside layer is a second canvas `anc90cv.front`
  (z 47, above the other fish: he is closer). Fanning 24 frames a beat, neighbours blended by the fractional phase.
  Turn 25 frames, neighbours blended, small loop toward the viewer (0.45 units) and back, pectorals flared (spread 1.35)
  mid-turn, dorsal up (ref. QqU5RsqYAOI 10:05), cross-fade 8 %. Measured: max 2.58 px/frame, male 0 backward, no errors.
  Clips `AFNICA_Anc93_cave.mp4`, `AFNICA_Anc93_turns.mp4`. Note: the photo's paired fins hang ~8 px below its belly line
  (the 3D fins stop at the ground), so the photo/3D blend at the turn ends still shows a slight difference.
- **Adults looked "badly cropped" (owner)**: the V17.89 flat-fin hook (PFIN polygons, tuned for the OLD sprite) erased the
  photo's pectoral/pelvic fins and redrew them flat -> PFIN emptied at load for all keys (the photos show the fins as they
  lie); the old `.ancSide{transform:scaleY(.91)}` squash and the saturate/contrast filter are off for the photos; the male
  side photo had the photo's floor shadow under the chin/fins -> removed in `incoming/anc_mfull_side_cut.png` (grey
  below the belly, dark low-saturation core under the chin, flecks). Before/after `AFNICA_Anc93_adults_fix.jpg`.
  **V17.94 walking U-turn** (owner: "everything" about the turn was wrong): `render_turn2.py` - the fish walks a U-turn,
  heading follows the path, curving AWAY into the tank (tail toward the viewer mid-turn, no face-on lump), body bent along
  the arc, small crawl wave, 25 frames 240x110 (`canvas.anc94t`, pivot 110,64); the forward part of the walk is applied
  in-game as the element `translate` (photo and 3D move together during the 15 % cross-fades) and sized to the free space
  ahead (`f.tr94.R` <= 39 px: walls / cave - turns usually happen at an obstacle); `ancTurnSecV1789` 0.8 s, heading eased
  (smooth ends, fastest mid). Session clip `AFNICA_Anc94_session.mp4` (3 adults + 3 fry): max 2.58 px/frame, no errors.
- Next: owner feedback on the session; female cave frames for the spawning visit (both fish inside); fry/juvenile frames
  (mixed colours); then commit when asked.

## Earlier: BRISTLENOSE LIFE (V17.89, end of the game HTML)

Reference: Foisy Aquatics, youtube.com/watch?v=QqU5RsqYAOI (mostly longfin albino / super red; behaviour only, the game keeps
the wild-type sprites; 2:39-4:03, 5:03-5:15, 7:24-7:42 are a zebra pleco L046, ignored). Not in the video (do not invent):
rasping close-up, bristle display, male-vs-male chases, wigglers. Owner said "do all" for the 6 points:
1 **Fanning:** male lies head-in with the tail ~24 px OUT of the cave mouth; slow sweeps (0.38-0.52 s) with 0.55-1.25 s
  holds drive the V17.42 fin canvas (`data-fan-ph89/fan-amp89`). Before: 1.75 Hz wiggle clipped to a circle.
2 **Spawning visit:** she walks in HEAD FIRST (old code backed her in), goes deeper, turns hidden inside, lies facing out
  a little lower than him; both drawn during male-approach/male-enter/trapped/laying (were invisible); his tail churns
  (fast irregular sweeps); she pushes 9 px to the mouth every 4-9 s and settles back slowly (<0.2 px/frame).
3 **Young:** 65% of their bouts are still clings of 6-16 s; hops go toward the group's centre (max 3 body lengths); wall
  trips every 7th step instead of 3rd. On a wafer: per-fish distance factor `s.pileK` (heads-in overlapping pile), they eat
  at 0.5x their size (`WAFERS_V1743[].eaten`) and stay twice as long. Fry leaving the cave (V17.43 canvas) settle in a loose
  group and hold 3-8 s.
4 **Glass:** after a new grazing patch, 55% chance of a 5-14 s still hold (no pectoral steps, mouth still); otherwise a
  continuous glide at ~11 px/s (no stroke gating). Turn on the sand 0.55 s (`ancTurnSecV1789`, was 1 s).
5 **Brood glimpse:** `canvas.ancBrood89` (z 43, clipped to the mouth hole) draws the clutch in the mouth: bright orange
  grape clump, darker with eye spots after 55%, fungus white; yolk stage = twitching wrigglers. Breeder tank only.
6 **Guarding:** cycle fan (18-40 s) -> deeper -> hidden flip -> head + bristles in the entrance (8-16 s) -> leaves head first
  -> turns outside (0.55 s) -> walks back in head first. Never backwards. Main tank (readiness days) and breeder (eggs/yolk).
- Bug fixed in passing: the V17.40 breeder choreography never set `position:absolute` on the fish, so after
  `renderV103Breeder()` re-created an element (e.g. starting a breeding) that fish was laid out ~40 px too low.
- Hooks (one-liners in old code): `ancPostV1789` (anc main loop, before `el.title=`), `ancTurnSecV1789`, `ancYoungTxV1789`,
  young rest choice, `s.steps%(s.young?7:3)`, `ancGlideV1789`, fin canvas `fanPh89`. No new `st` fields (all runtime).
- Measured (headless rig, fake clock): male cycle max 1.1 px/frame, 0 backward frames; female 1.4 px/frame, 1 borderline
  frame; young cluster spread ~100-230 px, 56-74% still; glass holds 5.6-10 s, glide 10-11 px/s; no console errors.
- Test hooks: `ancDebugV1789().DBG` {force, fan, guard} (fixed bout lengths, test only).
- Clips: `AFNICA_Anc89_{fan,spawn,young,emerge,turn,glass,brood}.mp4` in the repo root (review only, untracked).
  Rig: `assets_blender/trailer/anc_rig.py` + `takes_anc89.py <fan|spawn|young|emerge|glass|brood|mainready> [--film]`
  (landscape 960x540, breeder via `renderV103Breeder`, caption follows the camera), encoder `encode_plain.py` (no audio).
  **Use a different `AF_PORT` for every rig running at the same time** - two rigs on 9333 attach to the same Chrome.
- aquarium-reviewer pass: no blocking bugs; fixed: live-sibling filter (`s.seen89`, old motion states are never deleted),
  dead male skipped, `.ancBrood89` removed when the dad is gone, eggs canvas redrawn only on change (wrigglers ~15 fps).
  Not changed: `st.ancClutch2` brood is not drawn (the dad's cycle follows `st.ancClutch` only, as before);
  `ancTurnSecV1789` shortens every anc turn (wall/wafer too).
- **Owner corrections, round 2 (2026-10-12), all done:**
  - Eggs belong at the BACK of the cave: no clump in the mouth any more; `.ancBrood89` is only a faint glint at the far
    end of the opening, behind the male (owner chose "faint glint"); INSPECT CAVE still shows the clump.
  - Cave clipping: the old rim mask (ellipse 22x20 at 32,46) was bigger/lower than the painted opening, so fish showed
    over the wooden lip. CSS override `.ancCaveRim` mask = ellipse 20x15 at 33,41 (measured: opening x 10-56, y 24-58 of
    the 160x77 cave); fish centre line `caveGeo().cy = T+43`; `.ancCaveShade89` (z 45) darkens the opening toward the back.
  - Pleco fins: ref. 10:02.85 / 10:03.85 / 0:57.3 / 0:59.4 - pectorals and pelvics are flat horizontal plates, they don't
    scull. Hook in V17.42 `pectoral()` -> `ancPectV1789`: erases the sprite's hanging pectoral + pelvic below a belly line,
    covers the part over the belly with sampled belly colour, redraws the same fin pixels rotated flat and squashed; small
    fore-aft row while crawling. Polygons per sprite record in `PFIN` ('anc|0|38' male, 'anc|120|38' female, 260x152
    records only). Sprites themselves unchanged.
  - Sand gait (owner chose burst-glide-stop; the clip has no sand-walking footage): `ancSandSpeedV1789` replaces the
    constant 24 px/s slide in 'move', 'toWall' and the cave approach: peak in 0.15 s (~0.3 BL per bout, peak ~124 px/s
    for an adult), exponential glide, dead stop 0.4-1.6 s. Measured: 0 backward frames, max 4.1 px/frame at burst peaks.
  - Reviewer round 2 fixed: fin cache (`r.pfc89`, was rebuilt every frame), size guard, erase limited to the fin bbox,
    gait returns 0 when blocked. Clips re-filmed: fan, spawn, brood, young, sand (`AFNICA_Anc89_sand.mp4` new);
    comparison stills `AFNICA_Anc89_compare*.jpg`.
- **Round 3 - new cave (owner: "still corruption at the cave, change the cave if needed"):** the 3/4 driftwood log
  (`ancCaveMarkupV1728` PNG) is replaced at runtime by a terracotta tube seen from the side (`caveSVG()` in V17.89, SVG
  with clay noise, algae film, contact shadow; like the clay caves at 0:39 / 2:08 of the ref. clip). `window.ancCaveMarkupV1728`
  now returns the SVG; existing caves are swapped by `useCave()`. Back layer z 42 = tube + dark inside; rim z 45 = same
  tube, CSS mask cuts only the mouth interior (ellipse 6.3x18.4 at 17.6,48). Fish inside are fully hidden except what is
  in the mouth or sticks out. Constants: `MOUTH`, `caveGeo().cy = T+50`, in-tube clip T+28..T+69, x L+10..L+154.
  Texts "driftwood cave" -> "breeding cave". The old PNG is still in the file (line ~3367) but unused.
- **Round 4 - photo cave:** the SVG tube is replaced by the owner's Gemini photo (`assets_blender/incoming/anc_cave_photo.jpg`),
  cut by `assets_blender/cut_anc_cave.py` -> `incoming/anc_cave_cut.png` (320x135, 2x; floor shadow kept as alpha),
  embedded as `CAVEIMG89`, shown 160x67.5 at the bottom of the 160x77 cave box. Mouth interior (measured on the photo by
  hand; the auto-detection also caught the shaded underside): centre 13.8,42, radii 7.6x23.5 -> rim mask ellipse 7.2x23,
  `caveGeo().cy = T+46`, in-tube clip x L+8..L+156, y T+18..T+70. Fish that are not using the cave pass BEHIND it (z 41);
  a fish facing into the mouth with its tail still outside is drawn under the rim (z 44) so it really goes in.
- **Round 5 - sand gait from a new reference** (youtube.com/watch?v=ILotQrXzuu0, wild-type bristlenose: 4-22 s barely
  moves on wood, 26-29 s slow smooth crawl ~0.15-0.2 BL/s over a root onto sand, head pressed down, 28.6-30 s rasps in
  place; no bursts). `ancSandSpeedV1789` = slow crawl 0.2 BL/s (young 0.32) with ease-in and braking; trips > 1.3 BL =
  a low swim (~0.75 BL/s, lifted 6 px via `translate`, only while mode 'move'); head-down tilt 2.4 deg while rasping
  (`rotate`); fins row 0.12/0.07; sand turn back to 1 s. Old bug fixed: the male walked to the cave doorway BACKWARDS
  when the cave was on his left (cave branch `turn(s,1,dt)`). Fry emerge from the photo-cave mouth (L+10, T+52).
  Only the dad / fish in cave-approach/enter go under the rim; everyone else passes behind the tube (z 41).
  Reviewer round 3 done (fixes applied). Measured: male 1.1 px/frame max, 4 backward frames (the doorway pivot);
  female still 49% of sand frames, 'detach' wall descent is old code. Clip `AFNICA_Anc89_sand.mp4` re-filmed.
- **Gills (owner: "bristlenose don't have gills like the other fish, in the same place"):** V17.53 `breathe()` drew the
  usual mid-head gill-cover arch for anc. `BRS.anc.low=1` now draws only a short faint slit low on the side, right above
  the pectoral base (no operculum flap). Male fin erase line lowered at the head end (`belly` 198,85) - it was cutting a
  notch under the chin.
- **Cave as obstacle (owner screenshots: fish behind the tube looked skewered):** no fish passes behind or through the
  tube any more. A trip that really crosses it (move target / toWall / the male's walk to the doorway from the far side)
  swims OVER it: `s.ovl89` lift profile (rises 48 px ahead, belly ~4 px over the tube top, tilt <= 14 deg), rate-limited
  70 px/s (max ~2.3 px/frame); the trip is flagged as a swim in `ancSandSpeedV1789`. A grazing/wandering fish stops at the
  tube's edge; a move target on the tube is moved to the near side. (A "crawl over it" version looked wrong in profile.)
- **Fanning tail (owner: "the up-down tail beat is not ok", "faster"):** the vertical wave is off while fanning
  (`fanAmp89` .006); the caudal fin is redrawn narrower/wider about the tail base (turning toward / away from the viewer =
  a sideways stroke seen from the side), strokes 0.2-0.28 s with 0.18-0.55 s holds (spawning churn 0.12-0.2 s).
- **3D bristlenose (owner chose "the game's 3D shader" over Unity/Blender):** the anc side canvas now renders through
  V17.42 `glBent` (M3 two-flank shader) via `anc3dV1789` (hook in the anc tick, `c.dataset.gl89` = 1 when used; switch
  `window.ANC3D_V1789=false` for the old flat path). Texture = the sprite with the fins baked flat (`bake3d`,
  `flatFins`). Fanning = real sideways tail bend (kap from the beat, side flips), crawling = small lateral wave.
  Turns: yaw <= 0.5 rad + a brief narrowing while the side switches (`turn3V1789`) - beyond ~30 deg the shader's far
  flank shows through the head (same limit as the cory note). Fanning beat now continuous and smooth, 2.3 Hz (spawning
  3.2 Hz), strength drifting 0.56-1 (owner: "faster and smoother, not bursts").
  Old bug fixed: fish driven by the breeder choreography were never articulated (no fin canvas) - the breeding male
  was always the plain flat sprite in the Breeder Tank. The breeder wrapper now articulates them.
- Old-code note: a young fish coming down a side wall (`detach`, fixed 7 s) moves ~3.4 px/frame when it was high up.
- Next: owner feedback on the clips; then commit. Possible follow-ups: eggs on the cave ceiling instead of the floor;
  male shifting over the clump; fry clinging on the cave/wood top (they only use sand + glass now).

---

# Earlier (2026-10-12, cloud session)

## Latest: CORYDORAS PHOTO MODELS (V17.87) + PHOTO BREEDING BOX (V17.88) — merged to main 2026-10-12

### Corydoras story clip (2026-10-12): `AFNICA_Cory_Story_v2.mp4` (v1 superseded)
- New format instead of "What's new": opening splash, "What we've been working on", a mini-story in 2-3 s shots with
  big first-person captions, icon + splash end, socials card. `takes_cory.py`, `timeline_cory.py`; PLAYBOOK §5 has the
  format and the cloud render settings. Owner feedback applied in v2: slower transitions, splash first, nursery shows
  only eggs and day-1 larvae. Copy to D:\Retirement on the laptop.

### V17.87 corydoras photos (end of file)
- Every cory stage is now a Gemini photo, cut out with `assets_blender/cut_translucent_np.py` (cut-outs in
  `assets_blender/incoming/cory_*_gemini_cut.png`): larva 0-2, fry 3-6, juvenile 7-13, adult 14-30 (`cory|adultM87`,
  `cory|adultF87`), full grown 31+ (`cory|fullM87`, `cory|fullF87`; `coryFullGrownV1783`).
- Per sprite: `PECTWK_V1773[key]` pectoral box, V17.83 `GEO[key]` (eye, drawn barbels with width `w` / opacity `a`, cut).
  Photo females are not height-stretched (CSS `:has([data-wk=...])`). V17.81 `BASKET=[.58,.86]`, `SNOUT=[.97,.60]`.
- To swap a photo: cut it to 260 px wide, re-measure eye/barbels/pectoral on a 4x grid, update the constants.
- Seen once, not reproduced: a thin dark horizontal line near a full-grown female's dorsal fin.

### V17.88 photo breeding box (end of file)
- Gemini photo cut by `assets_blender/cut_breeding_box.py` (difference matting + hand-set solid regions for the white
  rim/hooks/grate) into BACK (inside, grate; behind fish) and FRONT (rim, hooks, edges) layers on the V17.86 elements.
- Box keeps the photo aspect, `top:-3px` so the hooks run over the tank rim. `window.boxGeoV1788={l,r,floor:.89}` tells
  V17.86 where the grate and walls are (fish floor and eggs).

## Earlier topic: CORYDORAS SPAWNING (V17.81) + LIVE FOOD (V17.82)

### V17.81 spawning ritual (end of the game HTML)
- **Trigger (owner: "sometimes, the NEXT day"):** a finished main-tank water change is stored in `st.coryCond81.wc`; live food fed
  in the main tank pushes the day into `st.coryCond81.food`. At each day change (`nextDay` wrapped -> `roll()`): chance
  1-(1-w)(1-f), w=.5 if water change yesterday, f=.25 per live feeding in the last 3 days (max .65). Measured: live food only ~24%,
  WC + 2 feeds ~70%. Success sets `st.coryRitual81={day,delay}`; the ritual starts after the Main Tank has been watched `delay`
  (20-90) s. The OLD path (`startCorySpawnV172`, instant fry when Next Day closed a running water change) is replaced: it now only
  records the water change.
- **Phases:** nudge -> chase (sand bursts / up the glass) -> cut -> T -> part -> carry -> lay -> leave -> rest, 3-5 rounds, eggs in
  `st.coryEggs81`, hatch next day via `st.corySpawn{v81}` and the wrapped `finishCorySpawnV172`.
- **T pose (owner's correction + his clip `Panda_Corydora_spawning.mp4`):** the MALE presses his snout into the middle of HER flank
  (low, `TP.fu/fv`), his body angled into the tank (3D yaw `md` .75 from profile, nose a little up), drawn in front of her. She bends
  only slightly (3D `fpit/fkap/fvk`, `fang`) and TREMBLES in bursts (`trem`: ~10 Hz, <0.5 px / 0.8 deg). Both drawn through the
  V17.75 shader (`data-m3/psi/kap/side/vk/kf/bank/thk/still` on the cory element; V17.42's generic GL branch passes bank/thk/vk/kf
  for cory only). **Keep the 3D turn <= ~45 deg from profile:** the shader draws two flat flanks; a round cory turned nearer head-on
  shows them crossing (double dorsal, two masks, hollow ring head-on) - this was the "asset error when he turns" the owner saw.
  `kap` in the data attribute is curvature per sprite px (c.kap radians / (canvas width*.55)).
- Note for the owner (literature): most sources describe the female's mouth at the male's vent/flank and the male clasping her
  barbels with his pectoral spine; implemented the owner's version (male snout on her middle). Swapping is a TP change.

### Second pass (owner: items 1-7 "do everything that would help")
1 male pectoral spine locked against her in the T (`clasp()`, svg.coryClasp81 over the tank, z 33);
2 'clean' phase: her mouth rubs the spot 1.6 s (site `cs` = snout on the spot), then she slides up and lays;
3 belly: `femaleBellyV1743` wrapped - conditioned (live food 3 days / water change) .55, spawning today 1, during the ritual
  shrinks round by round; after the ritual `condBirthDay` = today (drawn in, recovers in 3 days);
4 predation: every 40-90 s of watching, a random livebearer is sent (wrapped `waferTargetV1743`, eat radius 16 px) to eat one
  egg; button "EGGS ×n → FRY TANK" (`moveCoryEggsV1781`) sets `st.corySpawn.tank='fry'` (eggs render there, safe);
5 incubation 3-4 days (`endDay`), egg {d: day laid, b: unfertilized ~20%}; classes e81s1 (amber) / e81s2 (dark + eye spots) /
  e81b1 (chalk white) / e81b2 (fungus halo) - NOT .s1/.s2, the game has global classes with those names; count = good eggs;
  zero good eggs -> nothing hatches; the spawn panel text is rewritten live (days left, good/bad counts);
6 up to 4 males; 7 bouts: `R.breaks` (rounds 3-6, a 40-90 s break of normal life after round ~half), phase 'break'.

### aquarium-reviewer pass (2026-10-11) - fixed
An error inside the ritual loop now clears `st.coryRitual81` (no start/stop loop at 60 Hz); egg/UI/predation code has its own
try/catch; `start()` calls `stop()` if the female vanishes (no fish left with class coryBreeding); no visible eggs for an old non-v81
spawn; the zero-good-eggs hatch saves; live food counts once per day for the spawn chance; LIVE button follows the WAFER button;
svg.coryClasp81 opts out of the game's global svg rules (size, dimming filter). Not changed (by design): live food pre-empts the
egg hunter for the same fish.

### V17.83 CORYDORAS LIFE (end of file) + spawning extras in V17.81
Owner asked for everything from the idea list plus a smaller adult stage:
- **Size:** cory adults start at x0.82 and reach the old adult size (now "full grown") at 2.2 x adult age (`sizeFor` wrapped, `coryFullGrownV1783`).
- **V17.12 hooks (2 small edits):** `coryFrameV1783(s,t,dt,tank,all)` can take a fish over for a frame (V17.12 then just draws);
  `coryArriveV1783(s,t,tank)` returns {rest,wait} when a fish reaches its spot (rest instead of digging, shy/bold pause lengths).
- **Group foraging:** wrapped `coryWaferTargetV1743` (food/wafers first): one patch per tank that drifts every 25-45 s.
  **Resting together:** every 2.5-5 min a 20-35 s rest in a row, all turning to one direction. **Perching:** ~every few minutes one
  adult rises to a plant leaf (`coryLeafSpotV1781`), stays 15-40 s, glides down. **Company:** <3 cory = shy (near cover, long pauses),
  5+ = bold (short pauses).
- **Looks (painted on the cory canvas after V17.42):** sprite barbels are cut away (destination-out right/below the snout) and drawn
  again, swaying, feeling the sand when digging, shorter and reddish when worn (`f.barbel83` 0..1, +.22/day in dirty water - health
  <55 or waste >6, -.15/day when clean; a toast when it passes .5); the eye "wink" (pale crescent sweeps over the pupil, every 8-25 s,
  more when resting); sand puffs at the mouth and the gills while digging (`.coryPuff83`); juveniles paler, colouring up by adulthood
  (CSS filter on `.coryBodyShape`). Sprite geometry in `GEO` (adult_m and juvenile).
- **Stress:** during a water change + 15 s they huddle by cover with locked pectoral spines (`data-lock`, `CORYPECT_V1781.lock`);
  tank health <70/<50 makes air dashes 1.33x/2x as frequent (`o2DashMulV1766` wrapped).
- **Wigglers:** age <= 2 lie on the yolk and twitch every 4-10 s; from age 3 cory fry hunt BBS, banana worms and daphnia (V17.82).
- **Spawning extras (V17.81):** female eats one of her eggs (30%, only her first 2 spawns, `f.spawns81`); eggs on driftwood/stones
  (`hardSpot`, kind 'w', layer `.hard` z 14); soft stridulation clicks during courtship (WebAudio, only with sound on).
- Test hooks: `coryLifeDebugV1783()` -> {startRest, perchNow, scare}.
- Measured: no console errors; group spread 700 -> 280 px; max step 1.7 px/frame outside V17.12's own air dash.
- Reviewer pass fixed: no size jump on the adult day (juvenile growth now ends at .82); per-frame DOM queries cached; one perch try
  per tank every 2-5 min (leaf search is costly); wink/barbel timing in real time; lock flag cleared when the fright ends; belly
  during 'eat'; air-dash factor uses the lower of V17.66 and health (no double counting). Note: existing adult cory younger than
  full-grown age shrink once to the young-adult size on the first load (owner asked for the smaller adult stage).

### V17.84 YOUNG CORYDORAS MOTION + V17.85 GLASS SURFING (end of file)
- Larva (age 0-2) and fry (3-6) drawings (`coryFryAssetV1717`) are registered with the V17.42 fin layer as `cory|larva84` /
  `cory|fry84` (sized SVG data URLs in `REAL_FISH_ASSETS_V154.cory`, `realAssetKeyV154` wrapped), so their tail and body wave.
  No pectoral/gill overlays on them (V17.42 line guarded). Their locomotion runs in the V17.83 frame hook (V17.84 wrapper):
  larva lies nose-up on its yolk and wriggles 15-35% of a body length every 4-12 s (quiver 1); fry dart 0.3-0.9 body length in
  0.32-0.5 s (peak ~3.4 BL/s), turn on the spot first, pause 0.6-2.4 s with little pecks, dart toward small live food.
  Juvenile (7 to adult) gait via `coryGaitV1784` in V17.12 (hop rhythm 8.6 Hz, longer stops, speed 30) + quiver .2.
  Measured: larva <=1.3 px/frame, fry <=5.5 (headless ~40 ms frames), juvenile <1 outside the air dash.
- Glass surfing (owner: the telltale sign before spawning): while `st.coryRitual81` is pending today and the ritual has not
  started, adult cory in the Main Tank do bouts of 2-4 climbs up the front glass (where they are) or the nearest side glass:
  nose up, pitch over at the top, head first down, level out; 4-12 s of foraging between bouts; a toast/log the first time.
  The pre-ritual wait is now 60-140 s of watching. A climb in progress is finished when the ritual starts.
- Test note: the game switches back to the Main Tank 100 ms after the page `load` event (old code near the bristlenose
  setup); tests must wait for `load` before switching tanks.

### Group glass surfing, hiding young, breeding box (V17.85 rewrite, V17.84 edits, V17.86)
- Glass surfing is now a GROUP behaviour (owner): one bout per tank (`G` in V17.85): all adults gather at one spot of the
  front glass (side by side, .48 body apart) or a side glass (tight bunch), then climb together on a shared rhythm, each fish
  0-1.2 s behind (random order); 2-4 climbs; 6-14 s between bouts. Measured: 93% of climbing frames have 2+ fish up together.
- Larvae and fry stay grouped and hidden (owner): one shelter per tank (the biggest stone/wood/plant, kept 2.5-5 min); each
  youngster has its own place under it, sits 5-12 px further back and is drawn behind the decoration (z-index 7 !important;
  the fish CSS uses !important); first time in a tank it starts at the shelter.
- Breeding Box (owner chose "new item"): bought once (120 coins), hangs on the Fry Tank front glass (two divs: back z40, front
  z42; fish inside z41). 📦 button moves all young cory (<7 days) in/out; inside they do not hide, keep to the box floor,
  sizeFor x1.2; at 7 days they are let out. With a box, the Main Tank EGGS button moves the clutch into the box
  (`st.corySpawn.tank='box'`, eggs drawn on the box floor with the V17.81 development classes); hatched fry stay in the box.
  Saved: `st.breedingBox86 {owned, fish:[ids]}` (default in ensureHealthState).

### Cory pectorals (V17.42 `pectoral()`, `window.CORYPECT_V1781`)
Cory pectoral = thick bony serrated spine: no sculling. Held stiff, spread out-down while sitting (rest -.28 rad), pressed back at
speed (fold +.14), slow small drift, a quick outward flick when a hop starts (speed jump > `kick`). Drawn as one rigid piece.

### V17.82 live food (end of file)
Shop card LIVE FOOD (tubifex 60, blackworms 70, baby brine shrimp 50, banana worms 40, daphnia 50; 3 portions each) -> `st.liveFood`.
Tank button "LIVE ×n" next to WAFER opens a menu; a portion counts as the day's feeding (hunger 0, +.6 waste) and calls
`coryLiveFoodV1781`. Items are drawn on a per-tank canvas (z 28): tubifex sink fast as a clump, bury heads and wave tails; blackworms
crawl; BBS jerk in mid-water; banana worms drift down; daphnia hop. Swimmers hunt via the wrapped `waferTargetV1743` (bite pause
0.7-1.4 s, full after 5-9 bites for 40-70 s, only ~35% bother with worms on the sand); cory via wrapped `coryWaferTargetV1743` /
`coryWaferNearV1743` and eat with their low snout. Neons (school preset) do not hunt it yet. Items are not saved.

### Test hooks (flag)
`coryRitualV1781.start()/stop()/roll()`, `coryRitualDebugV1781()` -> {R,ctl,TP}, `liveFoodDebugV1782()`.

---

# Earlier handoff (2026-10-09): xipho courtship

Read this first when continuing. Topic so far: **xipho (swordtail) COURTSHIP** ("curtarea" = courtship, not cleaning).
Everything below is in the V17.74–V17.76 blocks of the game HTML.

## Done and approved by the owner

**Earlier (V17.74–V17.75, already committed before this session)**
- Guppy size scale, newborn livebearers x1.15, show-off only toward own species, lag fix.
- Sword stays straight; swordtail flare = dorsal only; two fights at once; no snout-to-snout lock.
- Swordtail FIGHT fully 3D (M3_GLSL): carousel spin, nip, tail-beating, counter-bite, burst pursuit. 3D turns for all livebearers and neons. Gonopodium len 48.

**This session: the swordtail courtship display (V17.76)**
All of it is in `chaseCoreV1744`, in the block `c.sp==='xipho'&&window.pose3gV1775&&T<1+hold`, plus the female branch just below it.
One of four displays is picked at random per courtship (`c.xvar`):
- **0 – round her**: he swims alongside (tropicaltanktv clip), then goes round her snout on the fight-carousel circle (about 184 deg, 3D body bent to the circle, kf 1, bank .28, no screen-space tilt), then backs in tail-first toward her snout, then returns alongside.
- **1 – cornering sweep**: he bursts in front of her, head away, tail tip at her snout, and swings round her snout like a clock hand (tail and sword sweep across her face), small hook at the tip.
- **2 – head left, she faces left**: in front of her snout, head to the LEFT of the screen, turned about 3/4 toward us, tail and sword curling away into the depth.
- **3 – she faces right** (variant 2 when `c.ff>0`, flag `c.xv3`): face to face on her right, head left, body bent in a C round her snout so his tail and sword go round her and he blocks her way. Turned about 138 deg (not head-on: head-on squashed the snout, owner said it looked odd).
- **Burst and flight cycles (variants 1–3)**: he bursts across her path (0.5–0.9 s, cubic ease-out, head first, turns to his final heading only at arrival, small lift over her). She flinches (short recoil, still facing forward), turns round (`c.ff` flips) and bolts. He overtakes and bursts again. 2 or 3 cycles (`c.xcyc`, 1.5 s each), then she freezes while he blocks her, and near the end she edges toward him.
- **She yields, he fertilizes**: the accept/refuse answer is decided once at the start (`c.resPre`, same rule as `settle()`, which now uses it). When the courtship ends in a thrust and she accepts, she stops fleeing and holds still through his approach under her; `settle()` then stores the sperm as before. If she refuses, the old behaviour stays (she bolts at the end).
- **Female reaction** for variant 0 is only: she slows and holds while he circles.

**Bugs found on the way (fixed — worth knowing)**
- V17.58 flips `c.ff` when the female nears the glass. My block now smooths his side (`c.xds`, `dd`) and latches it per burst cycle, otherwise he teleported (one-frame flip of yaw and side).
- A TDZ error (a `const` used before its declaration) in the block is swallowed by the try/catch around the motion chain, so the fish silently falls back to the old behaviour. `syntax_check_node.py` does NOT catch it. Always check `el.dataset.m3/psi/kap` in a headless run after editing this block.
- The 3D body centring shift `P3.dx` pulled the male back toward her. For variants 2–3 the yaw reference passed to `pose3gV1775` is his own heading (`psiF`), so no shift.
- Fish positions are clamped to the tank (`v16Bounds`): a target outside the tank is silently pinned to the glass.

## Test-only globals left in the code (flag, do not rely on them)
`window.__xvarForce` (0–2), `window.__xcycForce` (cycles), `window.__resForce` (1 = she accepts), `window.__sideS` (curvature side). They are harmless when undefined. Remove them if the owner wants a clean file.

## How it was tested in the cloud (nothing of this is in the repo)
Headless Chromium through Playwright (`/opt/pw-browsers/chromium-1194/chrome-linux/chrome`, node module at `/opt/node22/lib/node_modules/playwright`): load the HTML, `window.save=()=>{}`, build a tank with `tankArrayV14`, set `window.__afHourOverride=12`, force the courtship (`courtshipV1744.main={next:0}` and the `COURT_FIX` from `assets_blender/trailer/takes.py`), log with `requestAnimationFrame` (state x/y, `data-psi/kap/side/bank/kf`), record video with `recordVideo`. A 1100x900 viewport gives a 1050x390 tank, where the female no longer hits the glass. YouTube is blocked in the cloud: the owner uploads clips and frames are cut with ffmpeg.

## Not done / next
- The owner has NOT yet seen the final yield and fertilization clip on his own machine; ask for feedback first.
- Display 0 has no burst-and-flight cycles and no flinch; decide with the owner if it should.
- The vertical caudal "blade" from the tropicaltanktv clip (frames f75–f80) is not done (needs a shader change).
- The refusal case (she does not yield, bolts) was never filmed.
- Residual: when the female turns at the glass at the very moment the circle starts there can still be a fast turn of about 2 rad in 0.1 s (narrow tank only; the wide tank rarely triggers it).
- Burst peaks reach about 8.8 body lengths per second in the longest crossing (variant 3); may be too fast.
- Then, as before: molly fight and courtship.

## Owner preferences learned this session
Talk English (changed 2026-10-11, was Romanian); do not repeat the same frames over and over; show a COMPLETE clip, never cut-offs; the female must not tilt ("does not exist"); no tail trembling; measure instead of guessing; he pays for credits, so batch work and verify before showing. Commit and push only when he asks.
