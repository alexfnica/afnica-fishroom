# Handoff — where work stopped (2026-10-10, cloud session)

Read this first when continuing. Topic: **guppy male SIGMOID display** (the S-dance in courtship). Code tag **V17.81**.
Previous topic (swordtail courtship V17.74–V17.76) is finished; its notes are in git history (`git show 63ed01f:HANDOFF.md`).

## Reference
The owner sent a real clip, "Blue Moscow guppy mating" (4 s, vertical). Frame by frame:
- he stops IN FRONT of her snout, heading the way she heads;
- his rear half bends sideways into the depth until the tail fin is edge-on: a vertical blade at her face (~0.5 s, tremor);
- he pivots fast through the depth toward the camera (C-bend);
- he ends FACING her in an S: nose up toward her face, tail fanned down and back (~0.3–0.6 s);
- she turns her head toward him, then swims off over him and he follows.
Earlier attempts (vertical sine on the flat sprite, static lateral S, slow pivoting "breathing" S) were rejected as unnatural.

## Done (V17.81, uncommitted until the owner says so)
**3D body (fin-motion block, shader `M3_GLSL`, `glBent`)**
- Guppy males now get the full 3D pose in the generic path: kf (head/tail ratio), vk, bank, plus dorsal/tail flare (`FLAREP.guppy`).
- New uniform `uVf` (vertical bend of the head half, `pose3g` 14th param `vf`, `data-vf`).
- New uniform `uHr`: **rigid head** for guppy (bend stops 0.4 × front half in front of the middle, the head goes on straight). The owner called the bent head "horrendous".
- Inner body slices (`uLay` 1, .5, 0, -.5) for guppy **only when |cos psi| < .75**: a head-on view during the turn is solid, not a hollow white outline.
- Pectorals while 3D: the procedural pectoral (`pf80Motion`/`pf80Draw`) is drawn into a per-fish texture (`s.tex3`, `o3.src`) that `glBent` uploads every frame, so the fins beat and stay attached in 3D.
- `data-still` may be fractional (0..1): the swim wave fades in/out instead of switching. Old '0'/'1' behave as before.

**Display logic (new block at the end of the file, `window.gupDanceV1781` / `window.gupFemV1781`)**
- Called first in `chaseCoreV1744`, guppy male branch (the old S code below it is only a fallback when it returns null).
- ONE display per courtship with AT MOST ONE TURN (the owner rejected repeated spins and the raised-head pose):
  - he swims in with the normal engine, head first (mul 1.7, a bit below her when coming from behind); the 3D pose starts only when he is within 0.75 body of his spot, from his current yaw (`startYawV1775`), so there is no flip;
  - from BEHIND her: tail blade at her snout (1 or 2 blades if the window is ≥ 7.4 s, relaxed in place between them), then ONE turn toward her along a small arc (head first, C peaks mid-turn, bank .3, nose down .12), then a LEVEL lateral S facing her (no pitch, no tail-down) with short S pulses every 1.6 s, relaxed facing her at the window end;
  - from IN FRONT of her: no blade, no turn — straight to the S facing her.
- Every pose value goes through a critically damped follow (ω 14), the heading is wrapped to the nearest turn, her heading `dd` is latched when the display starts, snap ramps with distance.
- Measured turns of the courting male (`gtest` counts heading flips): from behind 2 in 12 s (the display turn + the old thrust code's turn), from in front 1 (only the thrust code's).
- Positions: A = her snout + his half length (his tail at her snout), B a bit further, all relative to her live position; mirrored for a left-heading female (psi → PI − psi, kap sign flips).
- She turns her head toward him (yaw .75, flat sprite narrowed, no tilt) while he faces her (`c.g81f`).
- Tuning constants in `K` at the top of the block.

## Measured (headless Chromium, fake clock from `assets_blender/trailer/cdp.py`)
- PLAYBOOK §2 scene (2 M + 2 F guppy, looping courtship, sneak off, hold 7–7.5 s): 2 display cycles, 0 console errors, male max step 9.4 px/frame (in the old thrust phase), max yaw change 0.34 rad/frame. Big steps of the female / other male are the old flinch dash and sneaky dart (intended).
- Frame cost (software WebGL in the container, so absolute numbers are inflated): median during the display 33 ms vs 34 ms with none of the V17.81 GL additions; the slices doubled it until limited to head-on views. Check on the laptop with a GPU.
- Syntax check: `with syntax errors 0`. NOTE: shader compile errors are not caught by it - check visually.
- `aquarium-reviewer` pass done. Fixed: her heading is latched only when the pose starts (not during the approach); a pose never starts if it cannot finish inside the display window (short hold 4.5 s tested: he is relaxed at the window end, the hand-back to the flat sprite is seamless); a guppy cut off mid-display lowers its fins (courtship-end cleanup); on an exception her head turn is reset and the error is logged once. Its "texture binding leak" finding was a false positive (`glBent` re-binds `tx` before drawing, line ~8324). Still open: `data-fb` is never cleared (pre-existing), `vf`/`uVf` plumbing exists but the display passes 0 (unused). Not tested: a tank mixing a 3D guppy with a 3D molly/xipho at the same time.

## Not done / next
- **The owner approved the in-game display (`guppy_S_in_joc_v2.mp4`, single turn) on 2026-10-10: "gata, e bine".**
- Flat-sprite flash: exactly head-on during the pivot the head still looks a bit squashed (flat sprite seen from the front).
- Ideas not done: a tremor ripple on the tail edge (fine, the owner dislikes trembling tails), eye/head tracking her, random variation per courtship (tail curl toward/away, 1–3 cycles, blade only without the pivot).
- Female in the game keeps her old slow "watch" drift; in the test scene she also swims off over him at the end. In the game the old post-display code (thrust or swim off) follows the display.
- The test rigs (`clip*.js`, `gtest.js`, `perf.js`) live only in the cloud scratchpad, not in the repo.
- Clips in the repo root (untracked): `guppy_S_clip_*.mp4`, `guppy_S_in_joc.mp4`, `guppy_S_variante.png`, `guppy_S_ref_vs_joc.jpg`. Decide with the owner which to keep before committing.

## Test-only globals left in the code (from V17.76, flag, do not rely on them)
`window.__xvarForce`, `window.__xcycForce`, `window.__resForce`, `window.__sideS`. Harmless when undefined.

## Owner preferences learned
Romanian; copy a real clip instead of guessing; smooth transitions (no velocity kinks); turns must read as 3D; the head is rigid (no rubber head); show complete clips; measure; commit/push only when asked.
