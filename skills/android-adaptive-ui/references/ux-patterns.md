# UX Patterns Reference

Composition rules for adaptive Android UI. Used by `analyze_sketch`, `generate_layout`, and `ux_preview` workflows.

---

## Sketch Analysis Priority Order

When analyzing a screenshot or sketch, evaluate in this order:

1. **Navigation** — bottom bar / rail / drawer / none
2. **Content Hierarchy** — primary action, secondary sections, feed
3. **Discoverability** — search visibility, browse entry points
4. **Responsiveness** — column count, scroll axes, density
5. **Visual Density** — card size, spacing, information per viewport

---

## Content Discovery Feed

**Use for:** Music apps, OTT, news, learning apps — any app with a personalized home feed.

**Structure (top → bottom):**

| Slot | Component | Rules |
|---|---|---|
| Header | Profile avatar + optional badge | Compact — never full-width banner |
| Quick Access | Horizontal scroll row | Circular or square items; genres, shortcuts, recent |
| Recommendations | Discovery cards (2-col mobile, 3-6 col tablet) | Albums, playlists, media |
| Featured Content | Hero card | Max one above-the-fold; high visual priority |
| Content Feed | Vertical list or LazyColumn | Trending, artists, podcasts |
| Navigation | Bottom bar (phone) / Rail (tablet+) | See Navigation Rail Pattern |

**Phone rules:**
- Single column vertical scroll
- Bottom navigation bar (4 tabs: Home, Search, Library, Profile)
- Horizontal scroll rows for Quick Access and Recommendations

**Tablet rules:**
- Navigation Rail replaces bottom bar
- Multi-column grid for Recommendations (3+ columns)
- Search visible in main content area (not buried behind tab)
- Increase content density — more cards per row, not larger cards

**Phone → Tablet conversion:**
```
Bottom NavigationBar  →  NavigationRail (persistent)
Single column feed    →  Multi-column grid layout
Hidden search         →  Exposed search bar in content area
Horizontal scroll row →  Grid with 3-6 columns
```

---

## Navigation Rail Pattern

**Use when:** Tablet, foldable (expanded), desktop — any width >= Medium (600dp).

**Rules:**
- Replace `BottomNavigationBar` entirely — never show both simultaneously
- 3–7 destinations (Material 3 recommendation)
- Always visible (persistent) — not hidden behind a hamburger
- Labels visible alongside icons (unlike bottom bar which may hide labels)
- `NavigationSuiteScaffold` handles the phone→rail→drawer transition automatically

**Detection:** width >= 600dp OR NavigationRail/NavigationDrawer present in layout

**Never:**
- Duplicate items between bottom bar and rail
- Show rail on Compact-width screens
- Use a rail with < 3 or > 7 items

---

## Hero Content Pattern

**Use for:** Continue Listening, Featured Playlist, Editorial Recommendation, Promoted Content.

**Rules:**
- Maximum **one** hero section above the fold
- Full-width on phone; constrained max-width on tablet (avoid stretching to full screen width)
- High visual priority — large image, prominent title
- Always scrolls with the feed (never sticky/pinned)
- Card aspect ratio: 16:9 or 3:2 for landscape media

**Tablet adaptation:**
- Hero at full column width can look oversized — cap at ~800dp or use a 2:1 grid placement
- Consider promoting hero to a dedicated "Featured" pane alongside the rail

---

## Discovery Grid

**Column count by width:**

| Screen Width | Columns | Applies to |
|---|---|---|
| < 600dp (Compact) | 2 | Phones portrait |
| 600–840dp (Medium) | 3 | Small tablets, phones landscape, foldable outer |
| 840–1200dp (Expanded) | 4 | Tablets, foldable inner open |
| 1200–1600dp (Large) | 5–6 | Large tablets, Chromebooks |
| > 1600dp (ExtraLarge) | 6+ | External displays |

**Rules:**
- Increase **density** (more columns) before increasing **card size**
- Fixed-width cards are a code smell — use `fillMaxWidth` with a `weight` or `LazyVerticalGrid(GridCells.Adaptive(minSize = 150.dp))`
- Hardcoded `columns = 2` is a WARNING finding — replace with `GridCells.Adaptive`

```kotlin
LazyVerticalGrid(
    columns = GridCells.Adaptive(minSize = 150.dp),
    contentPadding = PaddingValues(16.dp),
    horizontalArrangement = Arrangement.spacedBy(8.dp),
    verticalArrangement = Arrangement.spacedBy(8.dp),
) {
    items(items, key = { it.id }) { CardItem(it) }
}
```

---

## Content Detection (for `analyze_sketch`)

Map visual elements to component types:

| Visual Element | Component |
|---|---|
| Circular items in a row | Quick Access row (genres, categories, shortcuts) |
| Square cards in a row/grid | Discovery grid (albums, playlists, media) |
| Large rectangular banner | Hero content (continue listening, featured) |
| Text list with thumbnails | Content feed (trending, artists, recommendations) |
| Bottom tabs (icons + labels) | BottomNavigationBar → phone |
| Vertical icon column on left edge | NavigationRail → tablet/desktop |
| Full left panel with icons + labels | NavigationDrawer → expanded/desktop |
| Search bar in top chrome | Exposed search (tablet pattern) |
| Search icon in bottom tab | Collapsed search (phone pattern) |
