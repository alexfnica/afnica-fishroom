# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What this is

AFNICA Aquarium: a browser game where you run a fishroom. You keep tanks, breed fish (guppy, molly, platy, xipho, neon, corydoras, ancistrus/bristlenose), do daily care like feeding, water changes and cleaning, treat disease, fill market orders and aquascape the tanks.

The whole game is one file: `AFNICA_Aquarium_V17_40_Bristlenose_Breeding.html`. It has no build step, no dependencies and no tests. To run it, open the file in a browser. The repo is on GitHub: `origin` = https://github.com/alexfnica/afnica-fishroom (branch `main`). On the owner's laptop git is installed at `D:\Git`; if `git` isn't found in the shell, refresh PATH from the Machine/User environment variables.

The code was built up over many AI prompts (Codex, then Claude). Each feature was added as a new block with a version tag (V7 … V17.69 so far), and older blocks were usually left in place. The file name still says `V17_40`; don't rename it unless the owner asks. Older and newer generations of the same system often exist side by side.

## Working with the file safely

- **Never Read the file without `offset`/`limit`.** It is about 22.5 MB (~10 900 lines). Some lines are megabytes of base64:
  - line ~3363: `ancCaveMarkupV1728`, about 3.3 MB of PNG
  - line ~3365: the `.ancArt` CSS sprites, about 1.3 MB
  - lines ~3836–3875: per-species `fry/juvenile/adult_f/adult_m` data-URI sprites
  - many `url("data:image/...")` lines in the CSS
- Use Grep with `-o` and a short, bounded pattern (e.g. `function\s+\w+V17\w*`) so long lines don't flood the output. Look up line numbers first, then Read small ranges.
- Grep function names as whole words. `healthLabel` and `healthLabelFor` are different functions.

## Architecture

The file is layered. What runs is decided by source order: later `<style>`/`<script>` blocks override or patch earlier ones.

1. **CSS, lines ~6–3366.** Stacked version sections, each starting with a header like `/* ===== V17.x ... ===== */`. Later sections override earlier ones, often with `!important`. Before editing a rule, check whether a later section overrides it.
2. **Main game script, lines ~3372–6845.** One global script with no modules. Everything is a top-level function or global:
   - `MODELS`: inline SVG fish per species and life stage. `S`: the species table (name, adult age, rarity, price).
   - `st`: the single global game state, loaded from and saved to `localStorage['afnicaFreshRestart1789317515442']`. `save()` writes it and refreshes the coin/egg counters.
   - `ensureHealthState()` is the save-migration step. It fills in defaults for every field added over time. **When you add a field to `st`, add a default there** so existing saves keep working. Don't rename or restructure existing fields.
   - `render()` / `renderV8(screen)` build the screens (`home`, `dex`, `breed`, `shop`). `switchTankV8(id)` switches tanks (`main`, `fry`, `breeder`, `tank3`; tanks 4–6 were removed in V17.57). A tank shows at most 7 fish.
   - `bootAfnica()`, near line ~6319, is the entry point. It runs on `DOMContentLoaded`. It starts `startWaterRuntimeLoop()` (a 250 ms `setInterval` that calls `refreshPersistentWaterUI()`, the real-time water-change clock), then renders. The loop restarts on window focus and `visibilitychange`.
   - V16 motion engine, from line ~6358: `V16_MOTION_PRESETS`, `v16MotionStates`, and `v16MotionLoop` driven by `requestAnimationFrame`. V16.8 neon schooling follows.
3. **Species patch blocks, lines ~6846–7784.** These are self-contained IIFEs plus `<style>`, added later:
   - Corydoras-only locomotion (V17.12): a separate rAF loop with its own `states` map
   - the V17.13 saved clock
   - cory hatch UI
   - bristlenose motion
   - bristlenose breeding (V17.40). This wraps `renderV103Breeder` through `oldRenderAnc40`.
4. **V17.41–V17.69 blocks, lines ~6400–end.** Each one starts with a header comment `/* ===== V17.xx TITLE ===== */` that explains what it does. The main ones (line numbers drift, grep the header):
   - V17.41 day/night lighting; V17.60 day/night behaviour (`restingV1760`, `morningV1760`; `window.__afHourOverride` forces an hour in tests)
   - V17.42 natural fin motion: every fish is redrawn each frame on a canvas from its sprite (`draw`, `glBent` WebGL curl, `drawGono`, `pectoral`, `breathe`, `finGrowV1763`; `window.curlDebugV1744()` exposes the sprite cache)
   - V17.43 calmer swimming, female condition (belly), spirulina wafer, brood in the cave
   - V17.44 livebearer courtship (`courtshipV1744[tank]`, `chaseTargetV1744`); V17.45 pregnancy and birth (`st.broods45`, the fry you catch with the net); V17.46 fry hunting (`fryHuntTargetV1746`, `huntDebugV1746()`)
   - V17.48 male rivalry and the alpha (`fightDebugV1748()`); V17.52 show-offs (`showOffDebugV1752()`); V17.61 female choice (`attractV1761`)
   - V17.63 black molly genetics (lyretail/roundtail), full-grown stage; V17.64 grazing, shimmies, surface gasping (`behaviorTargetV1764`, `behaviorDebugV1764()`); V17.65 molly algae eating; V17.66 oxygen shortage (`o2LevelV1766`); V17.67 shimmy look; V17.69 platy fry/juvenile colour
   - The motion chain in the wrapped `v16UpdateFish` asks, in order: food → wafer → courtship → fry hunt → fight → show-off → behaviour. The first non-null target wins.

   To change a system, first check whether a later block patches it.

### Overlapping systems and hazards

- **Several fish-motion systems run at the same time** (V13, V16, V168 schooling, cory-only, bristlenose). Know which one owns a species before changing movement.
- **Health labels:** `healthLabel` and `healthLabelFor` coexist.
- **Test code that runs in production:**
  - `bootAfnica()` calls `unlockAllTanksForTestingV172()`, which unlocks every tank for free.
  - `v1681SetupNeonOnlyTest()` runs on a fresh save.
  - One-time migrations overwrite saved state, guarded by the flags `corySchoolingTestV48`, `bristlenoseFreshSetup` and the neon→cory swap near line ~3425.

  Flag these rather than silently keeping them or removing them.
- Duplicate function declarations are rare. `frame` is declared 3 times, each inside a separate IIFE. Most "duplicates" are versioned copies with different names, like `fooV13` and `fooV16`. Find the live one by grepping for its callers.

## Working rules (from the owner)

- **Talk to the owner in Romanian.** Code, comments and commit messages stay in English.
- **Commit only when the owner asks, and push only when they say push.** No commit per change.
- **After every edit to the game HTML, run the syntax check:** `python assets_blender/syntax_check_node.py` (Node.js), or on the owner's laptop `D:/Blender/5.2/python/bin/python.exe assets_blender/syntax_check.py` (headless Chrome). Expect `with syntax errors 0`.
- **Inside the long one-line functions use `/* */` comments, never `//`.** A `//` there comments out the rest of the line (this once broke a whole block).
- **Never touch the owner's save when testing in a browser:** run `window.save=()=>{}` first and build test tanks in memory (`tankArrayV14('main')`, `switchTankV8`). A reload restores the real save.
- Edits are usually done with small Python patch scripts that replace an exact, unique snippet and assert it was found once (the file has very long lines). Note that some newer blocks use CRLF line endings.
- When a behaviour is tuned, measure it (positions, speeds, distances) rather than guessing; the owner notices teleporting, jitter and fins/gonopodium not lining up.

## Conventions

- New features go in a new version-tagged block, and the file name carries the current version (`..._V17_40_...`). Follow this pattern unless the user asks for a refactor.
- Wrap code in the boot and render paths in `try/catch` with `console.error('AFNICA ...', e)`, so one broken subsystem doesn't block rendering.
- Any change to a function name or to `st` must be checked for callers and save compatibility.

## Project subagents (`.claude/agents/`, instructions written in Romanian)

- `code-archaeologist`: read-only. Finds the "live" version of a system and dead or duplicate code.
- `aquarium-reviewer`: use it proactively after any edit to the game HTML, especially near health, motion, breeding or save logic. It reports risks and does not fix them.

## Video tools (owner's laptop only)

`assets_blender/trailer/` films the game in headless Chrome and builds the vertical clips (Blender at `D:\Blender` for music and encoding): `takes*.py` record raw frames, `timeline*.py` describe the edit, `AF_TL=timeline_platy python compose.py` renders one. These need Chrome and Blender, so they don't run in a cloud session.
