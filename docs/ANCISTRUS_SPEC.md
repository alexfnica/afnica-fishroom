# Ancistrus (common bristlenose) motion spec — owner's 7 points

Evidence level: **[P]** = peer-reviewed paper, **[R]** = reference work or press report of a paper, **[V]** = our reference clips
(B7RksQ1xU18, QqU5RsqYAOI, short R6KUQ73HhlI), **[E]** = my estimate where no measured source exists (to be checked against [V]).
Targets assume a 960x540 tank, adult ≈ 70 px body length (BL), 60 fps. They are pass/fail numbers for Phase 2.

**General:** loricariids are stiff fish. Their bony plates and the fused skull and pectoral girdle make the front body rigid, and
the bending happens behind the dorsal fin, in the rear body and tail [P: Bressman et al. 2021; Lujan & Armbruster 2012].
In any fish turn, a curvature pulse runs from head to tail: the head swings first, then the bend travels back
[P: Danos & Lauder 2007 and follow-up midline studies]. Bigger fish turn more slowly and bend less [P: zebrafish ontogeny].

| # | Point | What the real fish does | Measurable targets |
|---|---|---|---|
| 1 | Turning | Head leads, rear body follows in a **C** shape. The front stays fairly straight (rigid head shield), the bend sits from the dorsal fin back. Pectorals spread, the tail sweeps once. A slow pivot almost on the spot [V B7RksQ1xU18 0:25–0:28]. | Duration 1.6–2.4 s (sand pivot); peak bend: tail tip deflected 30–45° from the head axis, at 40–60 % of the turn; head yaw leads tail yaw by 0.15–0.3 s; the bend relaxes before the turn ends; drift ≤ 0.3 BL; no flat mirror frame. |
| 2 | Sand → glass | Swims or creeps head first to the glass, the snout touches first, the oral disc seals, then the body tilts up around the mouth while pectorals and pelvics press flat. The mouth is the pivot point [P: Geerinckx et al. 2007, attachment while breathing; Crop et al. 2013, mouth used alternately with the pelvic fins in non-undulatory crawling (Astroblepidae, the sister family)]. | Mouth position continuous (step ≤ 2 px/frame); body rotation 0→90° over 0.8–1.5 s, eased; **max position step ≤ 6 px/frame**; side↔belly view swap never shows two fish (≤ 5 % overlap); no hop in y at the swap. |
| 3 | Cut-offs on glass | Physical: the whole fish is visible on the front glass; only the cave or decor should ever hide it. | 0 frames with a clip-path or mask on a glass fish outside cave modes; sprite bounds inside the tank or canvas; no half-drawn layers. |
| 4 | Male cave entry | The male picks a dark cavity and guards it from everything, males above all [P/R: Sabaj, Armbruster & Page 1999]. He swims to the mouth, lines up and goes in **head first**, then turns so the tail sticks out, and fans [V QqU5RsqYAOI 1:14–1:49; memory note: guarding = head in, tail out]. | Continuous path to the mouth (no step > 6 px/frame, no pop in y > 2 px); align ≤ 1 s before entering; entry 0.8–1.5 s with a smooth depth clip at the mouth line; fish never overlaps the cave walls. |
| 5 | Male fights | Ritual display: the males lie **parallel, head to tail**, dorsal and caudal fins up, cheek odontodes everted. They beat their tails and push, and only if it escalates do they circle and strike at each other's head [R: Wikipedia *Ancistrus*, original source unverified; V R6KUQ73HhlI]. The circling is slow and partial (half circles), **not** spinning on the spot. The genus name means "hook" after the cheek spines. | Rotation speed ≤ 60°/s and ≤ 180° per bout; head-to-tail phase with 3–6 tail sweeps at ~2–3 Hz [E]; shove or strike < 1 s, fast in / slow out; total 6–15 s; loser pivots and darts off; no frozen "stare" > 1 s. |
| 6 | Tentacles | Fleshy odontode sheaths covered in taste buds, best developed in breeding males [P: Sabaj et al. 1999; Yan 2009 J Fish Biol]. They have no muscles, so their motion is **passive**: they trail and sway with water flow and head motion. | Always some sway (never 0); amplitude ~1–2 px at rest and 2–4 px when swimming or turning; lags the head by 0.1–0.2 s (spring); 0.5–1.5 Hz [E]; tips move more than bases. |
| 7 | Glass crawl + mouth | Attached by the oral disc while breathing through the gills. A muscular valve separates the disc from the mouth cavity [P: Geerinckx et al. 2007 + SICB abstract]. The jaws scrape left/right independently (bilateral mandibles) [P: Lujan & Armbruster 2012; Geerinckx et al. 2009]. Moves by short lunges: the body pushes with a pectoral/tail stroke, the disc slides and re-seals, then a still grip [V B7RksQ1xU18 1:34–1:41]. | Rasp: jaw open/close 2–4 Hz [E], disc rim pulse ≤ 5 % scale, disc stays the same shape (no ring artefacts); crawl = push 0.3–0.8 s (1–3 px/frame peak) + grip 0.5–1.5 s (0 px); avg 3–8 px/s; body stays straight on glass (small tail wave only during the push). |

**Sources**
- Sabaj, Armbruster & Page 1999, *Ichthyol. Explor. Freshwaters* 10(3) — spawning, cave guarding, tentacles: <https://webhome.auburn.edu/~armbrjw/Ancistrus.pdf>; via USFWS screening: <https://www.fws.gov/sites/default/files/documents/Ecological-Risk-Screening-Summary-Ancistrus-pirareta-freshwater-fish.pdf>
- Bressman, Morrison & Ashley-Ross 2021, *Ichthyology & Herpetology* — loricariid stiffness, reffling: <https://bioone.org/journals/ichthyology-and-herpetology/volume-109/issue-2/i2020084/Reffling--A-Novel-Locomotor-Behavior-Used-by-Neotropical-Armored/10.1643/i2020084.full>
- Geerinckx et al. 2007, *Belg. J. Zool.* 137(1) — *Ancistrus* head, adhesion while breathing: <https://biblio.naturalsciences.be/associated_publications/bjz/137-1/volume-137-1-pp-47-66.pdf>
- SICB abstract, suckermouth attachment and respiration (oral valve): <https://sicb.org/?p=26655>
- Lujan & Armbruster 2012 — bilateral jaws: <https://aquaticecology.tamu.edu/wp-content/uploads/sites/3/2014/07/Lujan-2012a.pdf>
- Geerinckx, Vlassenbroeck & Herrel 2009 — jaw mobility while scraping (abstract only): <https://mochokidae.myspecies.info/fr/node/21>
- Danos & Lauder 2007 — turn kinematics: <https://sites.harvard.edu/glauder/files/2022/03/Danos.Lauder.2007.pdf>; midline curvature pulse: <https://sicb.org/abstracts/midlines-in-motion-connecting-midline-curvature-dynamics-to-heading-change-and-center-of-mass-deflection-in-fishes>
- Tentacles, mucus/nutrition hypothesis (Yan 2009): <https://www.practicalfishkeeping.co.uk/fishkeeping-news/possible-role-of-bristlenose-tentacles-revealed/>
- Male display/circling (secondary, unverified): <https://en.wikipedia.org/wiki/Ancistrus>

**Gaps:** no paper measures loricariid turn bend, rasp frequency or glass gait speed. The [E] numbers should be checked
by timing the owner's reference clips (text only: seek and count frames, no images sent).
