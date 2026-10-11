# Handoff — where work stopped (2026-10-11, cloud session)

## Latest topic: CORYDORAS SPAWNING RITUAL (V17.81, NOT committed yet — owner has to see it first)

New block `V17.81 CORYDORAS SPAWNING RITUAL` at the very end of the game HTML (style + IIFE), plus:
- two defaults in `ensureHealthState`: `st.coryEggs81=[]` (visible eggs `{x,y,k}`, fractions of the tank, k `g` glass / `l` leaf), `st.coryRitual81=null` (`{day}` = ritual due today);
- V17.12 cory engine, `coryBreeding` branch: reads `data-cory-face`/`data-cory-ang` into its own state and postpones its air dash 20-60 s, so the hand-back is smooth.

**Trigger:** a Main Tank water change that finishes in real time (not one closed by Next Day) with >=1 healthy adult cory male + 1 female
and no `st.corySpawn`. Runs only while the Main Tank is shown (the clock pauses elsewhere). The old path (`startCorySpawnV172`, >=4 cory,
only when Next Day closes an active water change) is untouched.

**Phases per round** (3-5 rounds, ~40 s each): nudge (male snout on her flank, forward nudges only) -> chase (sand bursts or up/down the
front glass, male follows her own path with a 0.38 s lag) -> cut (he arrives beside her snout and turns toward us) -> T (10-17 s, still,
fins only; male beside her snout nearly head-on, head toward her, drawn in front; `TP` opens it into a V with heads together; eggs fade
into her pelvic basket in the last 4 s) -> part -> carry (to the egg column on the front glass, or once per ritual a plant leaf found by
sampling the plant picture alpha, not behind wood/rocks) -> lay (nose up 3.5 s, 2-4 eggs dropped at the basket) -> leave -> rest.
Successive rounds alternate males. Eggs: 5 px, translucent white with a pale yellow core, column on the glass (z 41) or on the leaf (z 9).
`st.corySpawn={startDay,endDay:day+1,count:75% of eggs,v81:true}` is created at the first egg; `finishCorySpawnV172` (wrapped) hatches
them next day and clears `st.coryEggs81`. The old PNG `.coryEggCluster` is hidden for v81 spawns.

**T in 3D (second pass):** the male in the T is drawn by the V17.75 3D shader (`data-m3/psi/bank/thk/still` on the cory element; the
generic GL branch in V17.42 now passes `bank` and a thickness `thk` for cory only, default .12 there, .075 used here - more than ~.1 splits
the two flanks into a ring). He arrives in profile, turns his head toward us and toward her (`psi` from heading to PI/2+s*d0), holds,
opens to d1 (the V; more than ~.65 starts to look like a face-to-face stare), then turns back to profile and the flat sprite takes over.
`TP` = {d0,d1,bank,thk,dx,dy,z}.

**Measured (headless, 2M+1F, 3 full rituals):** no console errors, 0 backward-swimming frames, max step 4 px/frame (female), 6.8 (males in
the glass chase), re-render mid-T and tank switch OK (pauses), hatch -> fry OK. aquarium-reviewer: no blockers.

**Test hooks (flag):** `coryRitualV1781.start()` forces a ritual (refused while an old non-v81 spawn exists), `coryRitualDebugV1781()`
returns `{R,ctl,TP,leafSpot}`; `TP` = the male T pose (f0/f1 turn, a0/a1 tilt, dx/dy offset, z).

**Open / ask the owner:** does the T read well (2D sprite only, no 3D cory shader); carry to a far site can take ~14 s; hatch stays
"next day" like before (real: 3-5 days); the 2-3 cory case now spawns (old path needed 4).

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
Talk Romanian; do not repeat the same frames over and over; show a COMPLETE clip, never cut-offs; the female must not tilt ("does not exist"); no tail trembling; measure instead of guessing; he pays for credits, so batch work and verify before showing. Commit and push only when he asks.
