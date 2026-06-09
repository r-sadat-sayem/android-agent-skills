# Test Prompts

Ready-to-paste prompts for testing the skill. Copy the prompt block into a Claude Code session opened at your Android project root.

---

## Scenario 1: Phone → Tablet Migration (Primary Test Case)

**Situation:** Mobile UI is live and shipping. You want to create a tablet version without breaking the phone layout.

**Step 1 — Audit the existing phone UI**

```
/android-adaptive-ui analyze_ui --src app/src/main/java/ui/
```

Expected output shape:
```
SCAN ───────────────────────────────────────────────
Form factors : Phone (baseline)
Files scanned: N kt · M xml

FINDINGS ───────────────────────────────────────────
1  CRITICAL  HomeScreen.kt:12    Navigation    BottomNavigation → NavigationSuiteScaffold
2  WARNING   HomeScreen.kt:45    LargeScreen   GridCells.Fixed(2) — not tablet-adaptive
3  WARNING   HomeScreen.kt:78    LargeScreen   HeroBanner fillMaxWidth — needs widthIn cap on tablet
4  INFO      FeedScreen.kt:33    Scrollability LazyColumn — OK for tablet, no change needed

PENDING: 1 CRITICAL · 2 WARNING · 1 INFO
Apply all? [all / one-by-one / critical-only / skip / ux_preview]
```

---

**Step 2 — Preview UX options before committing to a fix**

```
/android-adaptive-ui ux_preview --src app/src/main/java/ui/
```

This launches `http://localhost:8080` — a page showing:
- The `NavigationSuiteScaffold` migration option with its phone→rail→drawer auto-switching behavior
- The `GridCells.Adaptive` grid option vs the current `Fixed(2)` grid
- Thumbs feedback buttons per option

Vote on each option, then press Enter to stop the server. The skill reads `ux_preview_output/feedback.json` and shows a vote summary before proceeding.

---

**Step 3 — Apply the large-screen track only (safe: phone layout unchanged)**

```
/android-adaptive-ui apply_responsiveness --track large-screen
```

What this does (and does NOT do):
- Migrates `BottomNavigation` → `NavigationSuiteScaffold` (renders as bottom bar on Compact, rail on Medium+)
- Replaces `GridCells.Fixed(2)` with `GridCells.Adaptive(minSize = 150.dp)`
- Adds `widthIn(max = 800.dp)` cap to hero card
- Does NOT touch scroll, text overflow, orientation, or other concerns
- Phone users see zero change — `NavigationSuiteScaffold` renders identical bottom bar on Compact screens

---

**Step 4 — Fix dependencies and OptIn (no code change)**

```
/android-adaptive-ui fix:deps
/android-adaptive-ui fix:optin
```

Adds `material3-adaptive-navigation-suite` to `app/build.gradle.kts` and `@file:OptIn(ExperimentalMaterial3AdaptiveApi::class)` to affected files.

---

**Step 5 — Verify nothing broke**

```
/android-adaptive-ui analyze_ui --src app/src/main/java/ui/
```

Expect: 0 CRITICAL, navigation finding resolved, grid finding resolved.

---

## Scenario 2: Generate Tablet Layout from a PRD

**Situation:** You have a PRD file describing the tablet experience. You want the skill to generate the scaffold code directly.

```
/android-adaptive-ui generate_layout --prd docs/music-player-tablet-prd.md
```

The skill reads the PRD, extracts navigation type (Rail), content structure (Quick Access → Grid → Hero → Feed), and generates a diff showing the proposed `NavigationSuiteScaffold` + `LazyColumn` with `LazyVerticalGrid` scaffold. You confirm, it writes the files.

---

## Scenario 3: Analyze a UI Screenshot

**Situation:** You have a screenshot of the current phone home screen. You want the skill to detect what needs to change for tablet.

```
/android-adaptive-ui analyze_sketch --img screenshots/home-phone.png --target large-screen
```

The skill detects:
- Bottom navigation bar → flags as needing NavigationSuiteScaffold migration
- 2-column grid of album cards → flags as needing GridCells.Adaptive
- One hero banner → validates single-hero rule (pass)

Then automatically calls `generate_layout --from-sketch` to produce the tablet scaffold.

---

## Scenario 4: Single Atomic Fix (Fastest Path)

If you already know exactly what needs fixing:

```
/android-adaptive-ui fix:nav
```
Replaces `BottomNavigation` → `NavigationSuiteScaffold` in the entire project. No audit needed first.

```
/android-adaptive-ui fix:content-density
```
Replaces all `GridCells.Fixed(N)` with `GridCells.Adaptive(minSize = 150.dp)`. One command, whole project.

---

## Scenario 5: Preview a Known Pattern (No Project Needed)

Use this to understand what a pattern looks like before applying it to real code:

```
/android-adaptive-ui ux_preview --pattern navigation-suite-scaffold-migration
```

Opens `http://localhost:8080` showing the `NavigationSuiteScaffold` pattern card: code snippet, pros/cons, approach steps, thumbs feedback. No project scanning needed.

---

## What "Phone Layout Unchanged" Means

The critical guarantee of `--track large-screen`:

| Component | Phone (Compact) | Tablet (Medium/Expanded) |
|---|---|---|
| `NavigationSuiteScaffold` | Renders as `BottomNavigationBar` | Renders as `NavigationRail` or `PermanentNavigationDrawer` |
| `GridCells.Adaptive(150.dp)` | 2 columns on 360dp screen | 3-4+ columns on 840dp screen |
| `widthIn(max=800.dp)` hero | Full width (phone < 800dp) | Capped at 800dp, centered |

The phone user sees an identical layout. The tablet user gets the adapted version. This is the entire point of `NavigationSuiteScaffold` and `GridCells.Adaptive` — the breakpoint logic lives inside the component, not in your `if/when` branches.

---

## Quick Validation Checklist (Run After Any Large-Screen Migration)

```bash
# 1. Grep for any remaining hardcoded nav that was missed
grep -r "BottomNavigation(" app/src/main/java --include="*.kt"

# 2. Grep for any remaining fixed-column grids
grep -r "GridCells.Fixed(" app/src/main/java --include="*.kt"

# 3. Verify OptIn annotations present
grep -r "ExperimentalMaterial3AdaptiveApi" app/src/main/java --include="*.kt" -l

# 4. Run the fast post-fix verifier
./skills/android-adaptive-ui/scripts/validate_fixes.sh app/src/main/java

# 5. Run a scoped re-audit on changed files only
python ./skills/android-adaptive-ui/scripts/layout_audit.py \
  --src app/src/main/java/ui/ --format json
```
