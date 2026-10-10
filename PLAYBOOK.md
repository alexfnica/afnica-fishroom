# PLAYBOOK — how to work on AFNICA efficiently

Read with `CLAUDE.md` (rules, file map) and `HANDOFF.md` (where work stopped). This file is the practical know-how:
what the owner wants, ready-made test scenes, how to measure, the 3D fish system, the video pipeline.

## 1. The owner's taste (approved / rejected)

- **Realism first.** Copy real fish behaviour; when unsure, ask for a reference clip and copy frames from it. Never iterate by guessing: show ONE static image or a few frames, get an OK, then animate.
- **No teleporting, no jitter, no instant flips.** Every move eases in and out; turns go through depth (3D), never a flat mirror flip.
- **Never swim backwards** (except a slight courtship "backing" toward the female). Head first toward where the fish goes.
- **No "cowboy stare"** (two fish frozen face to face). Fish keep gliding, arcing, repositioning.
- **The sword is a rigid straight ray**, never bent; a swordtail's flare raises only the dorsal (tail and sword stay).
- **Fins and gonopodium must line up**: measure contact (gonopodium tip on the vent ≤ 5 px, nip snout on the flank ≤ 5 px).
- Fights: same species only; liked: 3D carousel spin, tail-beating on a tight head-to-tail circle, fast nip + C-start flee, counter-bite, burst pursuit. Rejected: snout-to-snout lock (removed for xipho), trembling tails, downward J curl in courtship ("horrendous").
- Talk Romanian, code/comments/commits English; commit only when asked, push only on "push".

## 2. Test scene in the Browser pane (never touch the real save)

```js
window.save=()=>{};for(let i=0;i<60&&typeof calibV1773==='undefined';i++)await new Promise(r=>setTimeout(r,500));window.save=()=>{};
window.__afHourOverride=12;   // daytime (no night resting)
const mk=(sp,sex,age,id,fins)=>({id,name:id,species:sp,sex,age,genes:{color:92,pattern:82,fins,vitality:90,mutation:null},health:100,dead:false,disease:null,treatment:null,hungerDays:0,sickDays:0});
const a=tankArrayV14('main');a.length=0;
a.push(mk('xipho','M',36,'x1',98),mk('xipho','M',28,'x2',86),mk('xipho','F',24,'xf1',85));   // max 7 fish shown
try{st.broods45=(st.broods45||[]).filter(b=>b.tank!=='main')}catch(e){}
switchTankV8('main');
```
- Ages: adult = `S[sp].adult` (+4 days to be safe); full grown ≈ 2.2 × adult (xipho: 36 is full grown). `fullGrownV1763(f)`.
- Control systems: `courtshipV1744.main={next:0}` (court now) / `{next:1e15}` (none); `fightDebugV1748().NEXT.main=0` (fight now) / `1e15`; `showOffDebugV1752().NX.main=1e15`; `huntDebugV1746().NEXT.main=1e15`.
- Force fight moves: `const f=fightDebugV1748().FIGHT.main; f.seq=['spin','slap','nip']; f.si=0; f.seg='spin'; f.segT=performance.now(); f.segEnd=f.segT+3000;`
- Keep a looping scene with `setInterval` re-triggering (and clear `f.inseminatedDay/spermBroods/gestStart` on females to keep courtship going).
- The page only animates while the Browser pane is visible (rAF ≈ 1 fps when hidden) — check fps before measuring.
- A `location.reload()` restores the real save; rebuild the scene after every reload.

## 3. Measure instead of guessing (cheap, no screenshots)

- Per-frame recorder: in a `requestAnimationFrame` loop push `v16MotionStates.get(id)` x/y; report the max step per frame (> 6–8 px = a jump, unless it is an intended dart), speeds, and frame gaps (skip frames with gap > 40 ms).
- Backward swimming: compare the sign of the body-middle x velocity with the drawn facing (`cos(+el.dataset.psi)` in 3D, else the `scaleX` sign).
- Fight frame cost: wrap `requestAnimationFrame` and time the `tick` callback (healthy ≈ 3 ms).
- Console errors: wrap `console.error` and count.
- Screenshots: only at the end, zoomed on one fish; or copy a fish canvas (`[data-fish-id=..] canvas.realFishAsset`) into an overlay grid.

## 4. The 3D fish (V17.75, in the fin-motion block)

- Shader `M3_GLSL` (used when `el.dataset.m3==='1'`): yaw `psi` (0 = facing right, PI = left, PI/2 = toward us), lateral curvature `kap` + `side`, head/tail bend ratio `kf` (front half bends `kf` × as much), vertical curl `vk`, `pit` (+ = nose down), `bank`, body thickness (two flanks), rigid sword (`swordRoot`).
- Helpers in the V17.48 rivalry block: `pose3g(el,state,fw,curl,psi,kap,side,bank,qv,ref,pit,vk,kf)` (exposed as `window.pose3gV1775`), `startYaw`, `yawStep` (smooth turn), `follow3` (3D yaw for engine-steered moves). `state.fvOv` keeps the element unmirrored while GL draws the yaw; `v17TurnScale` wrapper hands back to the flat sprite (`m3Sign`).
- `data-still='1'` = held pose (no swim wave, no tail beat); `data-quiver` = faster/bigger tail beat; `data-t3` = an ordinary 3D turn (all livebearers + neons).
- Exact moves return `{...,snap:60,spin:true}` (followed as given, clamped to `v16Bounds`).
- Pectorals/breathe overlays are skipped while 3D-drawn; `finGrowV1763` only on the flat sprite.

## 5. Video clips (laptop only: Chrome + Blender)

- `assets_blender/trailer`: `takes_<sp>.py <take>` films raw frames to `raw/<take>/`; `timeline_<sp>.py` = shots, texts, music style (A cinematic, B marimba, C chill); render: `AF_TL=timeline_<sp> D:/Blender/5.2/python/bin/python.exe compose.py` → `out/AFNICA_whats_new_<sp>.mp4`; copy to the repo root as `AFNICA_WhatsNew_<Sp>_vN.mp4`.
- Two rigs in parallel: `AF_PORT=9334`. Run long jobs in the background. Re-film only changed takes.

## 6. Keep credits low

- One chat per topic; start it with "read CLAUDE.md, HANDOFF.md, PLAYBOOK.md".
- Opus for new animation/3D/behaviour systems; Sonnet for texts, git, number tweaks, clips from an approved plan.
- Batch feedback; few screenshots; measure in text.
- At the end: update `HANDOFF.md`, commit, push, merge into `main`; the laptop does `git pull`.
