# Ancistrus spawning in the cave — spec (step 0, 2026-10-23)

Scope: the live in-game bristlenose (1 male + 1 female + cave), in-game model only. Game times are compressed; the real
times are listed only for proportion. BL = body length (the adult sprite is about 70 px). All motion: max drawn step
≤ 2.5 px/frame (the V17.106 limit), and no fish pixels outside the tube clip except the two fish overlapping inside.

| # | Stage | What the real fish does (source) | Game target |
|---|---|---|---|
| 1 | Invite | Males take a cave and clean it, then lure a ripe female to it. A male often sits partly out of the mouth and fans with his pectoral and pelvic fins. He first chases the female off, and admits her once he has shown he can hold the cave. [A][E][F] | Head out at the mouth, small fin bouts. Optionally 1–2 short chases of the female (≤ 1 BL) before he admits her. 6–12 s. |
| 2 | Female arrives, male makes room | No source describes this step. In the documented layout the eggs are at the back of the tube on the ceiling, and the male stays between the eggs and the entrance [B]. | Female walks to the mouth at ≤ 0.4 BL/s. The male backs in 0.5–0.8 BL at ≤ 0.3 BL/s. 3–5 s. |
| 3 | Female enters | **No source supports tail first.** Guides say only that the female goes in and lays a cluster on the ceiling or walls at the back [C][D]. The only "backwards entry" I found is a male L-number pleco backing in to fertilise (anecdotal, not Ancistrus) [G]. | See *Conflict* below. Slow, smooth slide, 0.15–0.25 BL/s, 4–6 s, no pop at the lip. |
| 4 | Spawning | Inside, the male lies at the entrance side and blocks it with his body; the cave should "just fit" him [D]. Fanning is done mainly with the **pectoral and pelvic fins** [B][E][F]. No source gives a fin-beat rhythm, the male's exact position over the female, or how long spawning lasts (hobby reports say hours, unverified). | Male over and slightly behind the female, his body overlapping hers. Fin beat in bouts of 4–8 beats at ~2–3 Hz with 1–2 s pauses (the V17.106 rhythm). The tail wave is soft and secondary: 2–4 px amplitude, travelling to the tip, never rigid. 20–40 s (compressed from hours). |
| 5 | Female leaves, male guards | The male drives the female out; she plays no further role [C][H]. He then stays between the eggs and the entrance, beats pectoral and ventral fins to make a flow over the eggs, and cleans them with his mouth. Hatching takes 5–6 days, and care lasts about 2 weeks in total [B]; other sources give 4–10 days [E]. | Female backs/slides out at ≤ 0.25 BL/s, 4–6 s, then swims off (can be nudged by one short male chase). Male settles **head in, tail out, fanning**, which hands over to the existing egg/fry guard. |

## Conflict with the brief, and my proposal

1. **Tail-first entry is not documented** for Ancistrus. The real female goes in head first so she can lay at the back.
   The two choreographies:
   - **A, as you described:** the male backs in, the female backs in tail first, and the male lies over her. It reads
     well on screen, but it is not documented.
   - **B, as in the sources (recommended):** the male steps out of the mouth to the side and the female walks in
     **head first**, slowly, to the back. The male follows **head first** and lies over and behind her, blocking the
     entrance with his tail out and fanning. When she backs out past him, he is *already* head in, tail out, so stage 5
     links to the guard pose with no turn inside the tube. This also matches your cave-pose rule.
2. **Fanning is mostly fins, not tail.** I will keep the soft tail wave you asked for, but make the pectoral/pelvic beat
   the main motion and the tail a gentle travelling wave on top.
3. Spawning time, the fin-beat rate and the exact male-over-female geometry have no published numbers. The game
   values above are design choices.

## Sources
- [A] PlanetCatfish forum, "My first Ancistrus Claro spawn" (male defends the cave, then admits the female): <https://www.planetcatfish.com/forum/viewtopic.php?p=271964>
- [B] Secutti & Trajano 2009, *Neotropical Ichthyology* 7(3):479–490, *Ancistrus cryptophthalmus* (eggs on the ceiling, male between the eggs and the entrance, pectoral + ventral fanning, 5–6 d hatching, 2 weeks of care): <https://scielo.br/j/ni/a/v9sw5QwHyYyWK67qsbXpZgP/?lang=en>
- [C] Gensou, bristlenose breeding guide (female lays on the ceiling or walls; male drives her out): <https://gensou.sg/bristlenose-pleco-breeding-guide-complete/>
- [D] ancistrus.at, keeping and breeding (cave just fits the male, who blocks the entrance; pectoral fanning; he stays until the young leave): <https://www.ancistrus.at/en/bristlenose-catfishes-ancistrus-in-the-aquarium-keeping-care-and-breeding/>
- [E] USFWS risk screening, *A. pirareta* (pectoral fanning, removes bad eggs, 4–10 d): <https://www.fws.gov/sites/default/files/documents/Ecological-Risk-Screening-Summary-Ancistrus-pirareta-freshwater-fish.pdf>
- [F] PlanetCatfish forum, "Bristlenose breeding" (male hangs part way out of the cave, fanning with pectoral and pelvic fins): <https://www.planetcatfish.com/forum/viewtopic.php?p=30291>
- [G] zebrapleco.com forum, "Head to Tail?" (L-number male backing in; anecdotal): <https://www.zebrapleco.com/forum/viewtopic.php?p=32083>
- [H] Aquahoy, Ancistrus breeding (female expelled after spawning; pectoral fanning): <https://aquahoy.com/ancistrus-fish-types-feeding-breeding-and-care/>
- Not read: Sabaj, Armbruster & Page 1999 (*Ichthyol. Explor. Freshwaters* 10:217) is a scanned PDF with no text layer, and no OCR is available here.
