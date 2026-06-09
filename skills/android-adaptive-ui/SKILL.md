---
name: "android-adaptive-ui"
description: "Audit, fix, generate, and preview Android UI code across phones, tablets, resizable/foldable, TV, Wear OS, and Android Auto — with sketch analysis, UX pattern generation, localhost feedback preview, and structured reporting."
---

# Android Adaptive UI Architect

Audit, fix, generate, and preview Android UI code for all screen classes: phones, tablets, resizable/foldable, TV, Wear OS, Android Auto.

**Baseline:** Compose BOM 2026.04.01 · Kotlin 2.3.10 · Material3 Adaptive 1.2.0 · WindowManager 1.5.1

**Commands:**
```
analyze_ui --src <path>                      scoped audit (recommended)
analyze_ui --src <path> --module <name>      single-module audit
analyze_ui                                   full project audit (⚠ not recommended — see §4)
apply_responsiveness [--track X] [--only Y]  targeted fix
fix:deps | fix:optin | fix:nav | fix:critical atomic single-concern fixes
fix:content-density                          replace hardcoded column counts with adaptive grids
add_form_factor <phone|tablet|resizable|tv|wear|auto>
analyze_sketch --img <path>                  analyze a UI screenshot or sketch (vision)
analyze_sketch --img <path> --target <ff>    generate adaptive version for target form factor
generate_layout --prd <path>                 generate adaptive scaffold from a PRD/spec file
generate_layout --from-sketch               use last analyze_sketch result
generate_layout --pattern <id>              generate from a named playbook pattern
ux_preview [--src <path>] [--port 8080]     localhost feedback page for scanned path
ux_preview --pattern <id>                   preview a named playbook pattern
ux_preview --from-sketch                    preview last analyze_sketch result
```

---

## 1 — Session Start: Skill Ecosystem Probe

Run this BEFORE any workflow. Check the available skills list in your current session context and activate companions silently.

| Skill to probe | If present, activate as |
|---|---|
| `gsd-graphify` | **Graph store** — sync audit findings as graph nodes; query before scanning to skip already-known issues |
| `gsd-intel` | **Intel reader** — read `.planning/intel/` first; may already have component maps that replace `os.walk` |
| `gsd-scan` or `gsd-map-codebase` | **Discovery** — delegate initial project structure mapping instead of raw file traversal |
| `gsd-thread` | **Session persistence** — wrap each workflow in a thread so context survives Claude resets |
| `gsd-note` or `gsd-add-todo` | **Task tracker** — capture every CRITICAL finding as a trackable todo automatically |
| `gsd-debug` | **Debugger** — hand off to systematic debugging when an applied fix introduces a new error |
| `feature-dev:feature-dev` | **Builder** — delegate `add_form_factor` implementation when it requires significant new code |
| `claude-md-management:revise-claude-md` | **Doc sync** — after any `add_form_factor`, update CLAUDE.md with new patterns |
| `android-adaptive-ui` memory file | **Primary store** — `.adaptive-ui-memory.json` JSON-LD; always write here regardless of other skills |
| `solutions-playbook.json` | **Pattern cache** — read `references/solutions-playbook.json` at session start; skip re-reasoning on known patterns |
| `ux-patterns.md` | **UX rules** — read `references/ux-patterns.md` for content discovery feed, nav rail, hero, and grid composition rules used by `analyze_sketch`, `generate_layout`, and `ux_preview` |

**Probe output (emit once at session start):**
```
COMPANIONS ─────────────────────────────────────
Active: gsd-graphify · gsd-intel · gsd-thread
Inactive (not installed): gsd-scan · gsd-debug
Memory: .adaptive-ui-memory.json
Playbook: 13 patterns loaded (references/solutions-playbook.json)
UX Patterns: references/ux-patterns.md
```

**Playbook usage rules:**
- At session start, read `references/solutions-playbook.json` and index patterns by `detection_signals`.
- Also read `references/ux-patterns.md` — these rules govern `analyze_sketch`, `generate_layout`, and `ux_preview`.
- Before writing any fix: check if `detection_signals` of the current finding match a playbook entry. If yes, use `approach` and `code_sketch` directly — do NOT re-reason from scratch.
- After successfully applying a fix: increment `success_count` on the matched pattern and update `last_applied` timestamp in the local playbook.
- After any new pattern is discovered and proven: append it to the local playbook using the schema below.
- Playbook is agent-only (JSON) — never render its raw contents to the user unless explicitly asked.

**New pattern schema (for appending):**
```json
{
  "id": "kebab-case-unique-id",
  "category": "WindowSizeClass|Navigation|Scrollability|Foldable|Wear|Auto|LargeScreen|TextOverflow|Density",
  "form_factors": ["phone|large-screen|foldable|wear|auto"],
  "detection_signals": ["code strings that identify this pattern in source"],
  "problem": "One sentence: what goes wrong without this fix.",
  "approach": ["Numbered steps to apply the fix."],
  "code_sketch": "Minimal Kotlin snippet showing the fix.",
  "template_ref": "templates/relative/path.kt or null",
  "constraints": ["Hard constraints — things that must not be done."],
  "atomic_fix": "fix:command name if one exists, else null",
  "success_count": 1,
  "last_applied": "ISO-8601 timestamp",
  "contributor": "your-github-handle or 'seed'"
}
```

**Integration rules:**
- If `gsd-intel` active → read `.planning/intel/*.md` first; skip scanning files already catalogued there.
- If `gsd-graphify` active → after each audit, call `/gsd-graphify` to store findings as `AdaptiveUIFinding` nodes linked to file nodes.
- If `gsd-thread` active → open/resume a thread named `adaptive-ui-<project>` at session start; write audit state to it so future sessions resume mid-flow.
- If `gsd-note` / `gsd-add-todo` active → after `analyze_ui`, call the skill once per CRITICAL finding to create a tracked todo.
- If `feature-dev:feature-dev` active → when `add_form_factor` requires creating > 3 new files, delegate to that skill with the template as context.
- If `claude-md-management:revise-claude-md` active → call after any `add_form_factor` completes.
- If no companion skills → proceed with only the memory file. Never block on missing companions.

---

## 2 — Form Factor Detection

Run before any work. A project may match multiple tracks.

| Signal | Track |
|---|---|
| `:wear` module OR `androidx.wear.compose.*` import | `wear` |
| `CarAppService` subclass OR `:auto`/`:automotive` module | `auto` |
| `:tv` module OR `androidx.tv.*` import OR `android.software.leanback` feature | `tv` |
| `FoldingFeature` OR `WindowInfoTracker` OR `DevicePosture` OR multi-window resize handling | `resizable` |
| `ListDetailPaneScaffold` / `SupportingPaneScaffold` / `NavigationSuiteScaffold` OR `sw600dp` dirs | `tablet` |
| None of the above | `phone` (baseline) |

If detection is ambiguous, ask the developer which form factors they intend to support.

---

## 3 — Output Format (apply to ALL workflow responses)

Every response must follow this structure. No prose paragraphs.
Use `templates/audit-report-template.md` as the fillable output contract.

```
SCAN ───────────────────────────────────────────────
Form factors : <detected list>
Files scanned: <N> kt · <M> xml  (<C> cached, <S> non-UI skipped)
Memory file  : <path>
Companions   : <active skill list or "none">

FINDINGS ───────────────────────────────────────────
#  SEV       FILE:LINE                CATEGORY
1  CRITICAL  HomeScreen.kt:42         WindowSizeClass
2  WARNING   SettingsScreen.kt:18     Scrollability

BEFORE → AFTER ─────────────────────────────────────
FILE                  BEFORE                           AFTER                         ACTION
HomeScreen.kt:42      calculateWindowSizeClass()       currentWindowAdaptiveInfo()   REPLACE
SettingsScreen.kt:18  Column { … }                     Column + .verticalScroll(…)   ADD

PENDING: <X> CRITICAL · <Y> WARNING · <Z> INFO
Apply all? [all / one-by-one / critical-only / skip / ux_preview]
```

Rules:
- BEFORE→AFTER only for CRITICAL and WARNING. INFO = count only unless asked.
- One-line fix. No API explanations. Reference template by path only.
- After confirmation, apply silently and show a DONE block.

```
DONE ────────────────────────────────────────────────
✓  HomeScreen.kt:42     calculateWindowSizeClass → currentWindowAdaptiveInfo()
✓  SettingsScreen.kt:18 .verticalScroll() added
─  ProfileScreen.kt:7   skipped (INFO)
Memory updated · Todos created (2) · Graph synced
```

---

## 4 — Workflow: `analyze_ui`

### Scoped audit — always prefer this

```
analyze_ui --src <path>
analyze_ui --src <path> --module <module-name>
```

**Examples:**
```
analyze_ui --src app/src/main/java/ui/
analyze_ui --src app/src/main/java/ui/HomeScreen.kt
analyze_ui --src app/src/main/java/ui/ app/src/main/res/layout/
analyze_ui --src feature/feed/src/main --module :feature:feed
```

Split large projects by feature module or UI package — run one at a time. This is the recommended approach for all real-world use.

### Full project audit — ⚠ Not Recommended

```
analyze_ui
```

> **Why not recommended:** Scans every `.kt` and `.xml` file from the project root. On a medium-sized project (300+ UI files) this reads thousands of lines into context, producing a findings table too large to act on in a single session. Token cost is high and the "Apply all?" prompt becomes impractical.
>
> **When it is acceptable:** Greenfield projects with fewer than ~50 UI files, or when you specifically want a one-shot inventory to triage manually before fixing.

### Steps (both modes)

1. If `gsd-intel` active → read `.planning/intel/` first; note already-catalogued files.
2. For scoped: use `--src` path directly. For full: infer project root from open file, or ask once.
3. Run: `python scripts/layout_audit.py --src <path> --format json --memory <root>/.adaptive-ui-memory.json`
4. Run (lower-noise Kotlin path): `scripts/layout_audit_psi.sh --src <path> --format json`
5. Render using format in Section 3.
6. If `gsd-note`/`gsd-add-todo` active → create one todo per CRITICAL finding now.
7. If `gsd-graphify` active → sync findings to graph now.
8. Prompt for confirmation before any code changes.

---

## 4a — Workflow: `analyze_sketch --img <path>`

Analyze a UI screenshot or design sketch using vision. Outputs findings in the same format as `analyze_ui`.

```
analyze_sketch --img <path>
analyze_sketch --img <path> --target <form-factor>
```

### Detection Steps (run in this order)

1. **Navigation pattern** — bottom bar? rail? drawer? none?
2. **Content pattern** — map visual elements using `references/ux-patterns.md` Content Detection table:
   - Circular items in a row → Quick Access row
   - Square cards in a row/grid → Discovery grid
   - Large rectangular banner → Hero content
   - Text list with thumbnails → Content feed
3. **Layout pattern** — single column? multi-column? split pane?
4. **Device classification** — infer from navigation + density + proportions
5. **Match detected patterns** against playbook `detection_signals`

### Output (same FINDINGS format as §3)

```
SKETCH ANALYSIS ────────────────────────────────────
Source        : <path>
Detected form : Phone (inferred from bottom navigation bar)
Patterns found: 3

FINDINGS ───────────────────────────────────────────
#  SEV      COMPONENT         PATTERN DETECTED
1  WARNING  NavigationBar     Bottom nav — will not adapt on tablet (navigation-rail-migration)
2  WARNING  ContentGrid       GridCells.Fixed(2) inferred — use GridCells.Adaptive (discovery-grid-responsive)
3  INFO     HeroBanner        Hero content present — verify single above-fold rule (hero-content-pattern)

Generate adaptive version? [yes / ux_preview / skip]
```

If `--target <form-factor>` is set, skip the prompt and call `generate_layout --from-sketch` automatically.

---

## 4b — Workflow: `generate_layout`

Generate adaptive Kotlin scaffold code from a PRD, sketch analysis, or named playbook pattern.

```
generate_layout --prd <path>
generate_layout --from-sketch
generate_layout --pattern <id>
```

### Steps

1. **Source input:**
   - `--prd <path>` → read the PRD file; extract: navigation type, content sections, form factors, responsive rules
   - `--from-sketch` → use findings from the last `analyze_sketch` session
   - `--pattern <id>` → load the named entry from `references/solutions-playbook.json`
2. Read `references/ux-patterns.md` for composition rules relevant to detected content type
3. Select template(s) from `templates/` as the backbone (see §8 Form Factor Reference)
4. Show BEFORE→AFTER diff of what will be created — never paste full file contents, show diffs only
5. Wait for confirmation before writing any files
6. After confirmation: write scaffold files, run `fix:optin` + `fix:deps` as post-checks
7. Run scoped `analyze_ui --src <new files>` as final validation

### PRD Extraction Rules

When reading a PRD:

| PRD signal | Maps to |
|---|---|
| "Bottom Navigation" / tabs | `NavigationSuiteScaffold` |
| "Navigation Rail" | `NavigationSuiteScaffold` at Medium+ width |
| "Multi-column" / "grid" | `GridCells.Adaptive(minSize = 150.dp)` |
| "Hero" / "Featured" / "Continue Listening" | Hero content pattern, `widthIn(max = 800.dp)` on tablet |
| "Horizontal scroll row" | `LazyRow` with `horizontalArrangement = Arrangement.spacedBy(8.dp)` |
| "Single column vertical scroll" | `LazyColumn` with `NavigationSuiteScaffold` |

---

## 4c — Workflow: `ux_preview`

Launch a localhost webpage showing adaptive UX options and collecting user feedback.

```
ux_preview [--src <path>] [--port 8080]
ux_preview --pattern <id>
ux_preview --from-sketch
```

### Steps

1. Determine pattern set:
   - `--src` → run `analyze_ui --src <path>` silently first, take all WARNING+ findings → map each to a playbook pattern
   - `--pattern <id>` → load single named pattern
   - `--from-sketch` → use patterns from last `analyze_sketch`
2. Run: `python scripts/ux_preview_server.py [--src <path>] [--pattern <id>] [--port 8080]`
3. Report URL to user: `UX Preview → http://localhost:8080`
4. Server blocks until the user clicks **Submit** in the browser — Submit IS the confirmation
5. Read `ux_preview_output/feedback.json` — extract the `selected` field from the last entry
6. **Automatically proceed to implementation** — no additional prompt:
   - Call `generate_layout --pattern <selected-id>` using the selected pattern
   - Show the BEFORE→AFTER diff of what will be written
   - Write the scaffold files
   - Run `fix:optin` then `fix:deps` as post-checks
   - Run `analyze_ui --src <new files>` as final validation
7. Emit a DONE block:

```
DONE ────────────────────────────────────────────────
Selected  : navigation-suite-scaffold-migration
Generated : app/src/main/java/ui/AdaptiveScaffold.kt
✓  fix:optin   — @OptIn added to 2 files
✓  fix:deps    — material3-adaptive-navigation-suite added
✓  analyze_ui  — 0 CRITICAL · 0 WARNING on new files
```

If `feedback.json` has no `selected` entry (server was cancelled with Ctrl-C): report "No selection recorded — nothing applied."

### What the page shows

- **Pattern cards** — one per finding, each with: pattern name · category · problem statement · code snippet · pros/cons · approach steps
- **Single-select radio** — click a card to select it (green ring); only one selection allowed
- **Submit button** — fixed at bottom of page; enabled once a card is selected; clicking Submit records the choice, shows "✓ Selection recorded", and shuts the server down automatically
- **Zero external deps** — pure stdlib Python, single-file HTML output

---

## 5 — Workflow: `apply_responsiveness [--track X] [--only Y]`

Without flags: runs all tracks, all concerns. Heavy — use flags to scope.

### `--track` flag (one form factor at a time)

| Flag | Scope | Typical token cost |
|---|---|---|
| `--track phone` | Navigation scaffold + scroll guards | Low |
| `--track tablet` | ListDetail / Supporting pane scaffolds | Medium |
| `--track resizable` | PostureDetector + ResizableLayout + multi-window | Medium |
| `--track tv` | TvAppScaffold, D-pad focus, module isolation check | Medium |
| `--track wear` | WearAppScaffold, module isolation check | Medium |
| `--track auto` | CarAppService skeleton, manifest check | Low |
| `--track density` | Resource folder audit only | Very low |

### `--only` flag (one concern across all tracks)

| Flag | What it does |
|---|---|
| `--only deps` | Add missing Gradle dependencies only — no code changes |
| `--only optin` | Add `@file:OptIn(ExperimentalMaterial3AdaptiveApi::class)` to files missing it |
| `--only nav` | Fix navigation scaffold (`BottomNavigation → NavigationSuiteScaffold`) only |
| `--only text` | Add `overflow`/`maxLines` to bare `Text()` calls only |
| `--only critical` | Apply CRITICAL findings from last audit only |
| `--only api` | Replace deprecated API calls only (`calculateWindowSizeClass` → `currentWindowAdaptiveInfo`) |

### Steps (for any combination of flags)

1. Detect active tracks — skip any not matching `--track` if specified.
2. If `--only deps` → jump directly to deps check; skip all code scanning.
3. Search for existing scaffold: `Scaffold(`, `NavHost(`, `NavigationBar(`, `BottomNavigation(`.
4. Show BEFORE→AFTER diff only for the scoped concern — never paste full template.
5. Apply after confirmation.
6. If `gsd-thread` active → write progress checkpoint to thread.
7. Run `analyze_ui` scoped to changed files only as a post-check.

---

## 6 — Atomic Fix Sub-commands

These run a single targeted concern without a prior audit. Fastest option for known issues.

| Command | Does exactly one thing |
|---|---|
| `fix:deps` | Read `references/dependencies.md`, check `app/build.gradle.kts`, add missing entries |
| `fix:optin` | Grep for adaptive API usage, add `@file:OptIn` to files missing it |
| `fix:api` | Find all `calculateWindowSizeClass(` calls, replace with `currentWindowAdaptiveInfo()` |
| `fix:nav` | Find `BottomNavigation(` / `NavigationBar(`, replace with `NavigationSuiteScaffold` pattern |
| `fix:text` | Find bare `Text(` without overflow/maxLines, add them |
| `fix:critical` | Re-read last audit from `.adaptive-ui-memory.json`, apply all open CRITICAL items |
| `fix:scroll` | Find `Column {` blocks with ≥5 children and no scroll modifier, add `.verticalScroll` |
| `fix:orientation` | Find `android:screenOrientation` locks in manifest, remove or set to `unspecified` |
| `fix:content-density` | Find `GridCells.Fixed(` with hardcoded column counts, replace with `GridCells.Adaptive(minSize = 150.dp)` |

**Output format for atomic fixes:**
```
FIX:OPTIN ──────────────────────────────────────
Scope   : @OptIn annotation on adaptive API files
Files   : 3 candidates → 2 need fix, 1 already correct

CHANGES
HomeScreen.kt:1   ADD  @file:OptIn(ExperimentalMaterial3AdaptiveApi::class)
DetailScreen.kt:1 ADD  @file:OptIn(ExperimentalMaterial3AdaptiveApi::class)

Apply? [yes / no]
```

---

## 7 — Workflow: `add_form_factor <name>`

Before starting, consult `references/form-factor-decision-guide.md` to validate ROI and complexity for the target form factor.

1. Check existing Gradle deps.
2. `phone` → harden navigation scaffold, scroll guards, text overflow. Lives in `:app`.
3. `tablet` → pane scaffolds (`ListDetailPaneScaffold`, `NavigationSuiteScaffold`). Lives in `:app`.
4. `resizable` → `ResizableLayout.kt` + `rememberDevicePosture()`. Lives in `:app`. Covers foldables AND multi-window.
5. `tv` → confirm separate `:tv` module (`com.android.application`) exists or scaffold it. Never mix `androidx.tv.*` into `:app`. If `feature-dev:feature-dev` active and > 3 new files needed → delegate.
6. `wear` → confirm separate `:wear` module exists or scaffold it. If `feature-dev:feature-dev` active and > 3 new files needed → delegate.
7. `auto` → confirm separate `:auto`/`:automotive` module or flavor.
5. Add deps from `references/dependencies.md`, integrate template step by step.
6. Run `fix:optin` and `fix:deps` as post-checks.
7. If `claude-md-management:revise-claude-md` active → call it now.
8. Run scoped `analyze_ui --src <new files>` as final validation.
9. Run `scripts/validate_fixes.sh <project-root>` as fast post-fix verification.
10. Run `scripts/verify_project_build.sh --project-dir <project-root> --module app` as final project-local verification.

---

## 8 — Form Factor Reference (compact)

| Track | Templates | Key constraint |
|---|---|---|
| `phone` | `phone/AdaptiveScaffold.kt` | `currentWindowAdaptiveInfo()` once at root — `BoxWithConstraintsGuard` is escape-hatch only |
| `tablet` | `tablet-large-screen/ListDetailScreen.kt`, `SupportingPaneScreen.kt` | All panes in `AnimatedPane {}` · needs `@OptIn` |
| `resizable` | `resizable/ResizableLayout.kt` | `rememberDevicePosture()` via `produceState` — covers foldable postures AND multi-window resize |
| `tv` | `tv/TvAppScaffold.kt` | Separate `:tv` module — never import `androidx.tv.*` in `:app` · `Surface {}` required at root · D-pad only |
| `wear` | `wear/WearAppScaffold.kt`, `wear/WearRoundSquareLayout.kt` | Separate `:wear` module — never mix `compose.material3` |
| `auto` | `auto/MyCarAppService.kt`, `auto/MainScreen.kt` | Template model only — no Compose, no `setContent {}` |
| `density` | `references/density-table.md` | Vectors in `drawable/`; bitmaps need mdpi + xxhdpi minimum |
| Desktop / Chromebook | `references/ux-patterns.md` | Rail → PermanentNavigationDrawer at Expanded; grid 6+ columns; no orientation lock |

Breakpoints → `references/breakpoints.md` · Dependencies → `references/dependencies.md` · Decision guide → `references/form-factor-decision-guide.md` · UX Patterns → `references/ux-patterns.md`

---

## 9 — Hard Constraints (never violate)

1. No `setContent {}` in any `Screen` subclass (Android Auto).
2. Never import `androidx.compose.material3` in a Wear source set.
3. Never import `androidx.tv.*` in the phone `:app` module — TV material is incompatible with mobile Material3.
4. Never lock `android:screenOrientation` for `targetSdk >= 36` + sw600dp targets.
5. Every file using `adaptive`/`adaptive-layout`/`adaptive-navigation` must have `@file:OptIn(ExperimentalMaterial3AdaptiveApi::class)`.
6. `currentWindowAdaptiveInfo()` called once at composition root — never deep in the tree.
7. `calculateWindowSizeClass(activity)` is deprecated — always replace with `currentWindowAdaptiveInfo().windowSizeClass`.
8. Auto item limit: 6 items max on `minCarApiLevel` 1-2. Suggest pagination, not ignoring the limit.
9. TV apps must declare `<uses-feature android:name="android.hardware.touchscreen" android:required="false"/>` — without this, Play Store will not list the app on TV devices.
10. `resizable` track covers both foldables and multi-window — never add them as separate tracks.
11. Never block a workflow because a companion skill is absent. Degrade gracefully to memory-file-only mode.
12. `GridCells.Fixed(2)` hardcoded in production is a WARNING — always flag and offer `fix:content-density`.
13. Maximum one hero-weight card above the fold — flag additional heroes as WARNING.
14. Never show `NavigationBar` and `NavigationRail` simultaneously — `NavigationSuiteScaffold` is the only correct way to handle both.
