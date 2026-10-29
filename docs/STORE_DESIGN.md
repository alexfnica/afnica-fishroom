# AFNICA Fish Store — design (Phase 1, draft for owner OK)

A new **STORE** screen: a small shop where NPC customers buy fish the player bred. Code goes in new version-tagged
blocks (working tag **V17.120**); nothing existing is renamed.

## 1. Layout

- Side view of one room, like the tank screens: back wall with display tanks on a shelf row, counter on the right, door on the left, floor strip in front.
- **Start with 3 display tanks**, 4 fish each (12 fish total). Upgrades: +1 tank each (max 6), +2 fish per tank slot upgrade (max 6 each).
- Decor (cosmetic, bought with coins): plants, poster, rug, "OPEN" sign. MVP: fixed decor only.

## 2. Stocking and care

- Stock from a **STOCK** panel: pick a fish from Main / Fry / Breeder tank (adult, alive, not sick) → moves into `st.storeFish`
  (same splice/push pattern as `moveToBreederV103`). **RETURN** moves it back.
- Store fish never enter `st.fish`/`st.fry`, so tank loops, orders and breeding ignore them (no double counting). Sold fish are removed from `st.storeFish`.
- **Care rule (simple, proposed):** no daily feed/clean for store fish. Instead a **Store upkeep** of 2 coins per displayed fish per day (food, water). If coins can't cover it,
  fish lose 5 health/day and show a "needs care" badge. A fish unsold for **7 days** loses 3 health/day (stress); health < 50 = not for sale until returned. Disease can't start in the store; sick or dead fish can't be stocked.
- Why not full care: it would pull the 250 ms water loop and tank hazards into a screen with no tank engine.

## 3. Pricing

- **Reference value** = `sellValueV9(f)` (species price × grade × health × mutation), then × `sizeMult` (juvenile 0.6, adult 1.0, full-grown `fullGrownV1763` 1.2) × `finMult` (1 − 0.06 × `f.finTorn`, min 0.7). A "Fair price" = reference.
- Player sets a price per fish: slider 50%–200% of fair price. Default = 115% (store markup). Quick-sell stays at 100% in the Tanks screen, so the store is a better but slower channel.
- **Willingness to pay**: each customer has `budget` and a `valueSense` (0.9–1.3). They buy if `price ≤ min(budget, fair × valueSense × (1 + 0.15·reputationLevel))` and the fish matches their taste. Over-priced fish are looked at, then skipped (customer may say "too expensive").

## 4. Customers

| Type | Wants | Budget | Notes |
|---|---|---|---|
| Beginner | common species, any grade | 20–80 | most frequent, buys 1 |
| Collector | rare/uncommon, grade A+ | 150–600 | picky, big sales |
| Kid + parent | colourful (high color gene), cheap | 15–50 | 2 NPCs, parent pays |
| Breeder | pairs of one species (M+F), grade B+ | 80–300 | buys 2 |
| Window shopper | nothing | 0 | adds life, may leave unhappy |

- **Arrival**: base one customer per 25–45 s real time (while the Store screen is open); scaled by hour (peak 10:00–19:00, none at night) and reputation. While the screen is closed, sales are **simulated in batch** from elapsed time when the player returns (capped at 40 customers) so the store earns offline without needing animation.
- **Max at once**: 4 customers visible (+1 at the counter).
- **State machine**: `enter` (door → floor slot) → `browse` (walk to 1–3 tanks, stop 3–6 s, look/point) → `choose` (pick best matching affordable fish or leave) → `queue` (walk to counter slot) → `pay` → `leave` (walk to door). Unhappy exit: no match, too expensive, or waited > 40 s in queue. Walk speed ~60 px/s with easing; each tank has 2 viewing slots and the counter has queue slots 1–3, so no overlap.

## 5. Receptionist

States: `idle` (small bobbing) → `greet` (when a customer reaches the counter) → `net` (nets the chosen fish; the fish disappears from the display tank) → `bag` (clear plastic bag with water and the fish, hands it over) → `payment` (coins pop, counter sound `sfxV141('coin')`) → `idle`. A whole sale takes ~6 s.

## 6. Progression

- **Reputation** 0–100: +2 happy sale, +1 fair-priced browse, −3 unhappy exit, −1 over-priced. Levels: every 20 points; each level adds +15% willingness and +arrival rate.
- **Upgrades** (coins): extra tank, extra slots, second clerk (halves the pay time, +1 counter slot), decor.
- **Daily summary** at day change: customers, sales, revenue, upkeep, best sale, reputation change. Shown as a small popup + log line. XP: `addXPV9` per sale (as in `sellFishV9`).
- Sale toast: `🪙 Sold <grade> <species> for N`.

## 7. Save data (`ensureHealthState()` defaults)

```
st.store = { unlocked:true, tanks:3, slotsPerTank:4, rep:0, markup:1.15, decor:[], clerks:1,
             lastSimAt:0, daySales:{day:0,count:0,revenue:0,upkeep:0,walkouts:0,best:0},
             totalSales:0, totalRevenue:0 }
st.storeFish = []   // fish objects as in st.fish, plus f.storePrice (number) and f.storeSince (game day)
```
Rules: create only if missing; never rename existing fields. Old saves load with an empty store.

## 8. Hook points

`v8Nav` gets a 7th tab **STORE** (grid-template-columns 7); `renderStoreV17120()` follows `renderV10Market` (`v8Top()` + `v8Nav('store')`); `setAfnicaScreenV104('store')`. All new code wrapped in try/catch with `console.error('AFNICA store', e)`. Switch `window.STORE120=false`.

## 9. Display tank rendering (decision needed in Phase 2)

Recommended: lightweight **canvas/SVG sprites** drawn from the existing fish assets with a small gentle swim loop, not the full V16/V17 motion engines (they are tied to `.tank` elements and the simulation state).

## 10. MVP vs later

**MVP:** 3 display tanks, stock/return UI, price slider, 3 customer types (beginner, collector, window shopper), full state machine with walking, one receptionist with net/bag/pay, coins + toast + daily summary, reputation, offline batch sim, save defaults.
**Later:** kid+parent and breeder types, upgrades shop (tanks, clerk, decor), special requests ("I want a red guppy"), haggling, seasonal rushes, sale posters, store stats screen, sound ambience.
