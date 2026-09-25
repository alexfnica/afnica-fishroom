# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What this is

AFNICA Aquarium: a browser game where you run a fishroom. You keep tanks, breed fish (guppy, molly, platy, xipho, neon, corydoras, ancistrus/bristlenose), do daily care like feeding, water changes and cleaning, treat disease, fill market orders and aquascape the tanks.

The whole game is one file: `AFNICA_Aquarium_V17_40_Bristlenose_Breeding.html`. It has no build step, no dependencies and no tests. To run it, open the file in a browser. The folder is a local git repo (branch `main`, no remote). Git is installed at `D:\Git`; if `git` isn't found in the shell, refresh PATH from the Machine/User environment variables.

The code was built up over many AI prompts (Codex). Each feature was added as a new block with a version tag (V7 … V17.40), and older blocks were usually left in place. Older and newer generations of the same system often exist side by side.

## Working with the file safely

- **Never Read the file without `offset`/`limit`.** It is about 18 MB. Some lines are megabytes of base64:
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
   - `render()` / `renderV8(screen)` build the screens (`home`, `dex`, `breed`, `shop`). `switchTankV8(id)` switches tanks (`main`, `fry`, `breeder`, `tank3`, plus `st.extraTanks.tank4–6`).
   - `bootAfnica()`, near line ~6319, is the entry point. It runs on `DOMContentLoaded`. It starts `startWaterRuntimeLoop()` (a 250 ms `setInterval` that calls `refreshPersistentWaterUI()`, the real-time water-change clock), then renders. The loop restarts on window focus and `visibilitychange`.
   - V16 motion engine, from line ~6358: `V16_MOTION_PRESETS`, `v16MotionStates`, and `v16MotionLoop` driven by `requestAnimationFrame`. V16.8 neon schooling follows.
3. **Species patch blocks, lines ~6846–7784.** These are self-contained IIFEs plus `<style>`, added later:
   - Corydoras-only locomotion (V17.12): a separate rAF loop with its own `states` map
   - the V17.13 saved clock
   - cory hatch UI
   - bristlenose motion
   - bristlenose breeding (V17.40, the last block). This wraps `renderV103Breeder` through `oldRenderAnc40`.

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

## Conventions

- New features go in a new version-tagged block, and the file name carries the current version (`..._V17_40_...`). Follow this pattern unless the user asks for a refactor.
- Wrap code in the boot and render paths in `try/catch` with `console.error('AFNICA ...', e)`, so one broken subsystem doesn't block rendering.
- Any change to a function name or to `st` must be checked for callers and save compatibility.

## Project subagents (`.claude/agents/`, instructions written in Romanian)

- `code-archaeologist`: read-only. Finds the "live" version of a system and dead or duplicate code.
- `aquarium-reviewer`: use it proactively after any edit to the game HTML, especially near health, motion, breeding or save logic. It reports risks and does not fix them.
