# Handoff — where work stopped (2026-10-09)

Read this first when continuing. Topic: **xipho (swordtail) COURTSHIP display** (curtarea = courtship, not cleaning).


State after the long 2026-10-08/09 session (all in V17.74–V17.75 blocks/edits of the game HTML; committed).

**Done & approved by the owner**
- Guppy size scale (M .78, F .9), newborn livebearers ×1.15; show-off only toward own species; lag fix (per-sprite GL texture, no canvas resize).
- Sword stays straight (rigid ray behind the peduncle, GL + 2D); swordtail flare = dorsal only.
- Two fights at once (other species, ~1 in 4), weighted species pick; no snout-to-snout "lock" for xipho.
- Swordtail FIGHT fully 3D (M3_GLSL in the fin-motion block: yaw, curvature, perspective, body thickness, bank, pitch, vertical curl uVk, head/tail bend ratio uKf): carousel spin (tilted spiral), nip (aimed with real snout→flank, C-start flee), tail-beating = slow tight head-to-tail circle with both tails lashing (owner LIKES it), counter-bite, burst pursuit, follow3() 3D yaw for engine moves, never swim backwards, no "cowboy" staring.
- 3D turns for all livebearers + neons (v17TurnScale wrapper, data-t3).
- Full-grown xipho gonopodium len 62→48; contact 0.6–4 px.

**NOT done: xipho courtship display** (chaseCoreV1744, block `c.sp==='xipho'&&window.pose3gV1775`). Many guessed variants were rejected (trembling, downward J curl = "horrendous"). Owner's latest wishes: male IN FRONT of her, tail toward her snout, lateral hook "along the body" — owner picked option C (yaw −0.9 rad, tail curling toward viewer) and its depth-mirror when head faces viewer; TAIL must bend much more than the head (now kf .22); no tail beating. Literature: Hemens 1966 — male wraps body+sword in a U round the female's head (PMC8729911); sigmoid/C/8 shapes; backing.
**Next:** analyse https://www.youtube.com/shorts/rCztwJJ1T_U (owner's reference "courting dance") — take 3–4 key frames, show ONCE, get confirmation, then copy that exact pose. Do not iterate by guessing. Then molly fight/courtship.

**Why:** the owner felt the end of that session achieved little and cost a lot. **How to apply:** start from frames, keep screenshots few, prefer text measurements, batch questions. 
