# Avatar roster prompts (Gemini)

Paste the base prompt first, then ONE character line. Generate every character in the same chat as the reference pictures so the render look stays the same.

## Base prompt
3D animated film character, Pixar-style render, soft subsurface skin, large expressive eyes, stylized proportions, detailed fabric and hair. Full body, walking pose seen from the side facing right, mid-stride, both feet fully visible, arms swinging naturally, relaxed friendly expression. Plain solid bright green chroma-key background, no floor, no props on the ground, no text, soft even studio lighting, single character, centered, portrait orientation.

For the standing version (Home room) replace the walking part with: "standing still, front three-quarter view, arms relaxed, slight smile".
If the green is not flat, add: "pure #00FF00 green background, no shadow on the background".

## Characters
1. A teenage girl with a short black bob, pink hoodie, light jeans and white sneakers, light skin.
2. A young man with curly dark hair and a short beard, olive jacket, white t-shirt, dark jeans and brown boots, medium-brown skin.
3. A tall woman with a long blonde ponytail, mustard sweater, blue skinny jeans and brown ankle boots.
4. A stocky older man with a bald head, white beard and round glasses, green fishing vest over a plaid shirt, khaki trousers and rubber boots.
5. A girl with two thick braids and freckles, yellow raincoat, red boots and denim shorts, tan skin.
6. A cool teenage boy with an orange mohawk, black leather jacket, ripped jeans and chunky sneakers, light skin.
7. A woman with a huge curly afro, purple tee, high-waist cargo shorts and white sneakers, dark brown skin.
8. A friendly man in his thirties with a man-bun, round glasses and a teal flannel shirt, rolled-up jeans and canvas shoes, medium skin.
9. A young woman in a hijab, long beige cardigan, wide trousers and loafers, warm brown skin.
10. An elderly woman with silver hair in a bun, lavender cardigan with a floral scarf, long skirt and comfortable shoes, carrying a small watering can.
11. A boy about 10 years old with messy brown hair, backpack, striped t-shirt, shorts and light-up sneakers.
12. A woman with a short pixie cut dyed pink, denim jacket with pins, black leggings and combat boots, light skin.
13. A muscular man with a shaved head, black tank top, grey joggers, headphones around the neck and bright running shoes, dark skin.
14. A young woman with long straight black hair and bangs, cream knit sweater, plaid skirt, tights and loafers, east-Asian features.
15. A man in a smart navy blazer with a tie and tidy side-parted hair, chinos and brown leather shoes, carrying a briefcase.
16. A woman in a white lab coat over a blue shirt, hair in a ponytail, clipboard in one hand, flat shoes.
17. A chef: a man with a mustache, white chef jacket and hat, checked trousers and clogs.
18. A woman with long red wavy hair and a green sweater, tote bag over one shoulder, mom jeans and sneakers.
19. A teenage boy with dreadlocks tied back, oversized grey hoodie, skate shoes and a skateboard under one arm, dark skin.
20. A gardener woman in her fifties with a short grey bob and sun hat, apron over a checked shirt, work trousers and boots, carrying a small potted plant.

## Where to put the results
Save the pictures in `assets_blender/incoming/chars/` as `walk_01.png` ... `walk_20.png` (walking) and `stand_01.png` ... `stand_20.png` (standing), numbered like the list above. Keep the existing `char01.jpg` ... `char18.jpg` there too (the original references).

---

# FRONT-FACING versions (the ones the game needs now)

Name each result `front_NN` with the same number as the walking picture (`front_05` = the girl in the raincoat). 3 to 5 characters are enough to start.

## A) With the walking picture uploaded (best: keeps the same person)
Upload the walking picture, then paste:
> Same character, same face, hair and outfit as this image, but standing still and facing the camera straight on (front view), looking directly at the viewer with a friendly smile, arms relaxed at the sides, feet together, full body visible from head to shoes. Pixar-style 3D render, same style and lighting as the image. Plain solid flat bright green background (#00FF00), no floor, no shadow, no text, portrait orientation.

## B) Text only (no upload)
Paste this first, then ONE line from the list:
> 3D animated film character, Pixar-style render, soft subsurface skin, large expressive eyes, stylized proportions, detailed fabric and hair. Standing still, facing the camera straight on (front view), looking directly at the viewer with a friendly smile, arms relaxed at the sides, feet together, full body visible from head to shoes. Plain solid flat bright green background (#00FF00), no floor, no shadow, no text, single character, centered, portrait orientation.

01. A teenage girl with a short black bob, pink hoodie, light jeans and white sneakers, light skin.
02. A young man with curly dark hair and a short beard, olive jacket, white t-shirt, dark jeans and brown boots, medium-brown skin.
03. A tall woman with a long blonde ponytail, mustard sweater, blue skinny jeans and brown ankle boots.
04. A stocky older man with a bald head, white beard and round glasses, green fishing vest over a plaid shirt, khaki trousers and rubber boots.
05. A girl with two thick black braids and freckles, yellow raincoat, red rubber boots and denim shorts, tan skin.
06. A cool teenage boy with an orange mohawk, black leather jacket, ripped jeans and red rubber boots, light skin.
07. A woman with a huge curly afro, purple tee, high-waist olive cargo shorts and white sneakers, dark brown skin.
08. A friendly man with a man-bun, round glasses and a teal plaid flannel shirt over a white tee, rolled-up jeans and white canvas shoes, medium skin.
09. A young woman in a beige hijab, long beige cardigan, wide brown trousers and burgundy loafers, warm brown skin.
10. An elderly woman with silver hair in a bun, lavender cardigan with a floral scarf, long sage-green skirt and dark loafers, holding a copper watering can.
11. A boy about 10 with messy brown hair, blue backpack, blue-striped t-shirt, grey cargo shorts and light-up sneakers, holding a copper watering can.
12. A woman with a short pink pixie cut, denim jacket with pins over a grey tee, backpack, black leggings and black combat boots, light skin.
13. A muscular man with a shaved head, black tank top, grey joggers, headphones around the neck and colourful light-up running shoes, dark skin.
14. A young woman with long straight black hair and bangs, cream cable-knit sweater, plaid pleated skirt, black tights, burgundy loafers and headphones around the neck, east-Asian features.
15. A man in a navy blazer with a striped tie and tidy side-parted brown hair, khaki chinos and brown leather shoes, holding a brown leather briefcase.
16. A woman in a white lab coat over a light blue shirt, black hair in a ponytail, dark trousers and flat shoes, holding a clipboard.
17. A chef: a man with a mustache, white double-breasted chef jacket and tall chef hat, black-and-white checked trousers and black clogs, holding a clipboard.
18. A woman with long red wavy hair and a green sweater, tote bag over one shoulder, blue mom jeans and white sneakers.
19. A teenage boy with dreadlocks tied back, oversized grey hoodie, dark baggy cargo jeans and skate shoes, holding a skateboard under one arm, dark skin.
20. A gardener woman in her fifties with a short grey bob and straw sun hat, beige apron over a green plaid shirt, olive work trousers and brown boots, holding a small potted plant.
