# Realistic customers for the store (same look as the owner's outro)

The receptionist is a cut-out of the outro render. The customers should match: 3D animated-film style, full body, same lighting.
The game cuts each image out and walks it with a bob/rock/squash, so every person is ONE image.

## What to generate (6-8 people, one image each)

Use the outro frame as the style reference (attach `outro.mp4` frame or `D:\ClaudeWork\outro\f2.png`) and send this prompt once per person:

> Full-body 3D animated-film character (Pixar-like, same style, proportions and lighting as the reference), standing in a relaxed walking
> pose, **side view, facing RIGHT**, feet on the ground, arms relaxed. Person: **<describe>**. Plain flat **bright green (#00FF00)** background,
> no floor, no shadow, no text on the clothes, whole body visible head to shoes, 1024x1536 portrait.

Person ideas (mix of the 3 customer types): young woman in a red jacket / older man with a cap and glasses / teenage boy with a backpack /
woman with a ponytail and a sweater / collector type: man in a vest with a notebook / mum in a coat (kid version later) / student with headphones / grandma with a scarf.

## Install

1. Save the images in `assets_blender/store/people_src/` (png or webp, any names).
2. `D:/Blender/5.2/python/bin/python.exe assets_blender/store/cut_people.py`  (keys out the green, trims, resizes to 220 px tall -> `assets_blender/store/people/`)
3. `D:/Blender/5.2/python/bin/python.exe assets_blender/store/install120.py`  (embeds them; with no people images the vector customers are used)
