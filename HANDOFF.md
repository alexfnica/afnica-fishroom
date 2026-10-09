# Handoff — where work stopped (2026-10-09, end of the cloud session)

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
