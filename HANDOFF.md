# Handoff — where work stopped (2026-10-12, cloud session)

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
