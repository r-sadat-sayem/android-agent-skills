# Android Adaptive UI Skill

A Codex/Claude-compatible skill that audits and fixes Android UI code for every screen class: phones, tablets, foldables, Wear OS, and Android Auto.

**Baseline:** Jetpack Compose · BOM 2026.04.01 · Kotlin 2.3.10 · Material3 Adaptive 1.2.0

---

## Contents

- [What This Skill Does](#what-this-skill-does)
- [Installation](#installation)
- [Claude Code CLI Usage](#claude-code-cli-usage)
  - [Full Audit](#full-audit)
  - [Targeted Fix — `apply_responsiveness` Flags](#targeted-fix--apply_responsiveness-flags)
  - [Atomic Sub-commands](#atomic-sub-commands)
  - [Add a Form Factor](#add-a-form-factor)
  - [Running the Audit Script Directly](#running-the-audit-script-directly)
- [Skill Ecosystem Integration](#skill-ecosystem-integration)
- [Audit Script (Standalone)](#audit-script-standalone)
- [File Structure](#file-structure)
- [Form Factor Coverage](#form-factor-coverage)
- [Using with Other Agents](#using-with-other-agents)
- [Limitations](#limitations)
- [Quick Reference Card](#quick-reference-card)

---

## What This Skill Does

| Capability | Details |
|---|---|
| **UI-only scan** | Header-scans files first (4 KB) — only reads files that contain `@Composable`, `@Preview`, Compose/Wear/Auto/Window imports, or are layout XML. Data classes, repos, and network layers are never read. |
| **Targeted audit** | Single file, single directory, or mixed list of paths via `--src` |
| **Memory cache** | JSON-LD knowledgebase (`.adaptive-ui-memory.json`) — unchanged clean files are skipped on subsequent runs |
| **Atomic fixes** | Eight `fix:X` sub-commands apply one concern at a time without a prior full audit |
| **Templates** | Production-ready Kotlin/Compose scaffolds for each form factor, paste-ready |
| **Gradle snippets** | Version catalog + KTS dependency blocks, copy only what you need |
| **Skill ecosystem** | Probes for companion skills at session start and activates them automatically |

---

## Installation

From this repository root:

```bash
# install into both Codex and Claude default locations
./scripts/install-skill.sh --skill android-adaptive-ui --target both
```

Codex-only or Claude-only:

```bash
./scripts/install-skill.sh --skill android-adaptive-ui --target codex
./scripts/install-skill.sh --skill android-adaptive-ui --target claude
```

Development mode (symlink):

```bash
./scripts/install-skill.sh --skill android-adaptive-ui --mode link
```

Verify installation:

```bash
ls -la ~/.codex/skills/android-adaptive-ui
ls -la ~/.claude/skills/android-adaptive-ui
```

---
## Claude Code CLI Usage

Start a session in your Android project root:

```bash
cd /path/to/your/android/project
claude
```

At session start Claude probes for companion skills and prints a one-line `COMPANIONS` card. See [Skill Ecosystem Integration](#skill-ecosystem-integration) for details.

---

### Full Audit

```
> /android-adaptive-ui analyze_ui
```

Scans all UI files, emits a compact scan card + findings table + before/after diff, then asks:
```
Apply all? [all / one-by-one / critical-only / skip]
```

Audit a specific path instead of the whole project:
```
> /android-adaptive-ui analyze_ui --src app/src/main/java/ui/
```

---

### Targeted Fix — `apply_responsiveness` Flags

`apply_responsiveness` without flags processes everything — use flags to scope it to exactly what you need.

#### `--track` — one form factor at a time

```
> /android-adaptive-ui apply_responsiveness --track phone
> /android-adaptive-ui apply_responsiveness --track large-screen
> /android-adaptive-ui apply_responsiveness --track foldable
> /android-adaptive-ui apply_responsiveness --track wear
> /android-adaptive-ui apply_responsiveness --track auto
> /android-adaptive-ui apply_responsiveness --track density
```

| Flag | Scope | Speed |
|---|---|---|
| `--track phone` | Navigation scaffold + scroll guards | Fast |
| `--track large-screen` | ListDetail / SupportingPane scaffolds | Medium |
| `--track foldable` | PostureDetector + FoldAwareLayout | Medium |
| `--track wear` | WearAppScaffold, module isolation check | Medium |
| `--track auto` | CarAppService skeleton, manifest check | Fast |
| `--track density` | Resource folder audit only | Very fast |

#### `--only` — one concern across all tracks

```
> /android-adaptive-ui apply_responsiveness --only deps
> /android-adaptive-ui apply_responsiveness --only optin
> /android-adaptive-ui apply_responsiveness --only nav
> /android-adaptive-ui apply_responsiveness --only api
> /android-adaptive-ui apply_responsiveness --only text
> /android-adaptive-ui apply_responsiveness --only critical
```

| Flag | What it does |
|---|---|
| `--only deps` | Add missing Gradle dependencies only — no code changes |
| `--only optin` | Add `@file:OptIn(ExperimentalMaterial3AdaptiveApi::class)` where missing |
| `--only nav` | Fix navigation scaffold (`BottomNavigation` → `NavigationSuiteScaffold`) |
| `--only api` | Replace deprecated `calculateWindowSizeClass` with `currentWindowAdaptiveInfo()` |
| `--only text` | Add `overflow`/`maxLines` to bare `Text()` calls |
| `--only critical` | Apply CRITICAL findings from last audit only |

#### Combining flags

```
> /android-adaptive-ui apply_responsiveness --track large-screen --only deps
```

---

### Atomic Sub-commands

The fastest option — no prior audit needed, no form factor detection, one concern only.

```
> /android-adaptive-ui fix:deps
> /android-adaptive-ui fix:optin
> /android-adaptive-ui fix:api
> /android-adaptive-ui fix:nav
> /android-adaptive-ui fix:text
> /android-adaptive-ui fix:scroll
> /android-adaptive-ui fix:orientation
> /android-adaptive-ui fix:critical
```

| Command | Does exactly one thing |
|---|---|
| `fix:deps` | Check `app/build.gradle.kts`, add any missing Gradle entries from `references/dependencies.md` |
| `fix:optin` | Grep for adaptive API usage, add `@file:OptIn` to files missing it |
| `fix:api` | Replace all `calculateWindowSizeClass(` with `currentWindowAdaptiveInfo().windowSizeClass` |
| `fix:nav` | Migrate `BottomNavigation` / hard-coded `NavigationBar` to `NavigationSuiteScaffold` |
| `fix:text` | Add `overflow = TextOverflow.Ellipsis, maxLines = 1` to bare `Text()` calls |
| `fix:scroll` | Add `.verticalScroll(rememberScrollState())` to `Column` blocks with ≥5 children |
| `fix:orientation` | Remove or set to `unspecified` any `android:screenOrientation` lock in the manifest |
| `fix:critical` | Re-read `.adaptive-ui-memory.json`, apply all open CRITICAL findings |

**Example output:**
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

### Add a Form Factor

```
> /android-adaptive-ui add_form_factor wear
> /android-adaptive-ui add_form_factor auto
> /android-adaptive-ui add_form_factor foldable
> /android-adaptive-ui add_form_factor large-screen
```

Claude checks your Gradle setup, walks through module isolation requirements, integrates the relevant template step by step, then auto-runs `fix:optin` and `fix:deps` as a post-check. If `claude-md-management:revise-claude-md` is active, it updates CLAUDE.md automatically.

---

### Running the Audit Script Directly

From inside a Claude Code session using the `!` prefix:

```
> ! python ./skills/android-adaptive-ui/scripts/layout_audit.py \
    --src ./app/src/main \
    --memory ./.adaptive-ui-memory.json
```

Single file:
```
> ! python ./skills/android-adaptive-ui/scripts/layout_audit.py \
    --src app/src/main/java/ui/HomeScreen.kt
```

Multiple paths:
```
> ! python ./skills/android-adaptive-ui/scripts/layout_audit.py \
    --src app/src/main/java/ui/ app/src/main/res/layout/
```

JSON output for piping:
```
> ! python ./skills/android-adaptive-ui/scripts/layout_audit.py \
    --src ./app/src/main --format json > /tmp/audit.json && cat /tmp/audit.json
```

---

## Skill Ecosystem Integration

At the start of every session this skill probes the available skills list and activates companions automatically. No configuration required — if a companion skill is missing, the workflow continues in memory-file-only mode.

```
COMPANIONS ─────────────────────────────────────
Active: gsd-graphify · gsd-intel · gsd-thread
Inactive (not installed): gsd-scan · gsd-debug
Memory: .adaptive-ui-memory.json
```

### Companion Behaviors

| Companion skill | How it's used |
|---|---|
| **`gsd-graphify`** | After each audit, findings are stored as `AdaptiveUIFinding` graph nodes linked to file nodes. Before scanning, the graph is queried to skip already-known clean files. |
| **`gsd-intel`** | Reads `.planning/intel/*.md` before scanning. Files already catalogued there are skipped, reducing traversal on large projects. |
| **`gsd-scan` / `gsd-map-codebase`** | Delegates initial project structure mapping instead of raw `os.walk` — faster on monorepos. |
| **`gsd-thread`** | Wraps each workflow in a named thread (`adaptive-ui-<project>`). Audit state survives Claude context resets and can be resumed mid-flow in future sessions. |
| **`gsd-note` / `gsd-add-todo`** | Creates one tracked todo per CRITICAL finding immediately after `analyze_ui`. |
| **`gsd-debug`** | If an applied fix introduces a new compilation error, hands off to systematic debugging automatically. |
| **`feature-dev:feature-dev`** | When `add_form_factor` requires creating more than 3 new files, delegates to this skill with the relevant template as context. |
| **`claude-md-management:revise-claude-md`** | Called automatically after any `add_form_factor` to update CLAUDE.md with new patterns. |

### Memory File (always active)

`.adaptive-ui-memory.json` is the primary persistence layer regardless of which companion skills are installed. It's a JSON-LD knowledgebase that stores:

- Per-file SHA-1 hash + findings — clean unchanged files skipped on next run
- Accumulated form factor detection across runs
- Open and resolved finding history
- `resolvedFindings` audit trail with timestamps

```bash
# Inspect the memory file
cat .adaptive-ui-memory.json | python3 -m json.tool | head -40
```

---

## Audit Script (Standalone)

Works independently of Claude Code — use in CI or before starting a session.

### Requirements

- Python 3.9+ · No external dependencies (stdlib only)

### Usage

```bash
# Directory
python scripts/layout_audit.py --src ./app/src/main

# Single file
python scripts/layout_audit.py --src app/src/main/java/ui/HomeScreen.kt

# Multiple targets (files and/or directories, mixed)
python scripts/layout_audit.py \
  --src app/src/main/java/ui/ \
        app/src/main/res/layout/activity_main.xml

# With memory cache
python scripts/layout_audit.py \
  --src ./app/src/main \
  --memory ./.adaptive-ui-memory.json

# JSON output
python scripts/layout_audit.py --src ./app/src/main --format json

# Expand INFO findings
python scripts/layout_audit.py --src ./app/src/main --show-info
```

### Exit codes

| Code | Meaning |
|---|---|
| `0` | No CRITICAL findings |
| `1` | One or more CRITICAL findings |
| `2` | Bad arguments or path not found |

### CI integration (GitHub Actions)

```yaml
- name: Android Adaptive UI Audit
  run: |
    python ./skills/android-adaptive-ui/scripts/layout_audit.py \
      --src app/src/main \
      --memory .adaptive-ui-memory.json \
      --format json > audit-report.json

- name: Wear template smoke check
  run: |
    python ./skills/android-adaptive-ui/scripts/template_smoke_check.py

- name: Upload audit report
  uses: actions/upload-artifact@v4
  with:
    name: adaptive-ui-audit
    path: audit-report.json
```

### Template smoke check (local/CI)

```bash
python ./skills/android-adaptive-ui/scripts/template_smoke_check.py
```

This check is intentionally lightweight and catches compile-breaking template anti-patterns (for example invalid custom `Int.dp` extension helpers) before templates are copied into app code.

### What the audit checks

| Checker | What it catches |
|---|---|
| `HardcodedDpChecker` | `.dp` literals > 100dp not assigned to a named `val`; XML hardcoded `layout_width`/`layout_height` |
| `ScrollabilityChecker` | `Column` with 5+ children and no `.verticalScroll`; XML `LinearLayout` with no `ScrollView` ancestor |
| `OrientationLockChecker` | `android:screenOrientation` locked; CRITICAL if `targetSdk >= 36` |
| `WindowSizeClassApiChecker` | Deprecated `calculateWindowSizeClass()`; enum equality; missing `@OptIn`; wrong import package |
| `FormFactorComplianceChecker` | Wear/mobile `MaterialTheme` cross-contamination; Compose in Auto `Screen`; `WindowInfoTracker` without lifecycle collection |
| `TextOverflowChecker` | `Text()` without `overflow` or `maxLines` |

### What the audit does not check (yet)

| Not checked | Detail |
|---|---|
| Full Kotlin AST semantics | Regex + heuristic based checks only. |
| Runtime behavior | No emulator/device execution. |
| View system fix generation | XML findings are reported, but templates are Compose-first. |
| Compose compiler compatibility matrix | Assumes project uses compatible Compose/Kotlin versions. |
| KMP source-set correctness | Does not validate `commonMain` vs `androidMain` boundaries. |

Rule IDs and changelog: `references/audit-rules.md`

---

## File Structure

```
android-adaptive-ui/
│
├── SKILL.md                              ← Claude's instruction backbone (9 sections)
│
├── scripts/
│   └── layout_audit.py                  ← Standalone audit script, no pip dependencies
│   └── template_smoke_check.py          ← Wear template compile-safety smoke checks
│
├── templates/
│   ├── phone/
│   │   ├── AdaptiveScaffold.kt          ← NavigationSuiteScaffold + correct WindowSizeClass API
│   │   └── BoxWithConstraintsGuard.kt   ← Safety net composable for unusual window sizes
│   │
│   ├── tablet-large-screen/
│   │   ├── ListDetailScreen.kt          ← NavigableListDetailPaneScaffold (master-detail)
│   │   └── SupportingPaneScreen.kt      ← SupportingPaneScaffold (document / productivity)
│   │
│   ├── foldable/
│   │   ├── PostureDetector.kt           ← DevicePosture sealed class + rememberDevicePosture()
│   │   └── FoldAwareLayout.kt           ← TableTop / Book / Separating / Normal layout branches
│   │
│   ├── wear/
│   │   ├── WearAppScaffold.kt           ← AppScaffold + ScreenScaffold + TransformingLazyColumn
│   │   └── WearRoundSquareLayout.kt     ← isScreenRound branching + large display detection
│   │
│   └── auto/
│       ├── MyCarAppService.kt           ← CarAppService + Session skeleton + manifest snippet
│       └── MainScreen.kt               ← ListTemplate with driver distraction rules
│
├── references/
│   ├── breakpoints.md                   ← All 5 WindowSizeClass width breakpoints + posture matrix
│   ├── density-table.md                 ← ldpi → xxxhdpi table, Compose vs XML, anti-patterns
│   ├── dependencies.md                 ← Gradle TOML blocks per form factor
│   └── audit-rules.md                  ← Rule IDs + audit behavior changelog
│
└── gradle/
    ├── libs.versions.toml.snippet       ← Paste-ready version catalog entries
    └── build.gradle.snippet             ← Labeled KTS dependency blocks per form factor
```

---

## Form Factor Coverage

### Phone / Compact
- `NavigationSuiteScaffold` with automatic `BottomBar → Rail → Drawer` switching
- `BoxWithConstraintsGuard` for min/max width guards and compact-height auto-scroll

### Tablets & Large Screens
- `NavigableListDetailPaneScaffold` for master-detail (`ListDetailScreen.kt`)
- `SupportingPaneScaffold` for document / productivity layouts (`SupportingPaneScreen.kt`)
- All 5 `WindowSizeClass` breakpoints: Compact / Medium / Expanded / Large / ExtraLarge
- `AnimatedPane` wrappers + predictive back gesture support

### Foldables
- `DevicePosture` sealed class: `NormalPosture`, `TableTopPosture`, `BookPosture`, `SeparatingPosture`
- Hinge-aware `Spacer` sizing via `FoldingFeature.bounds`
- Lifecycle-safe observation via `collectAsStateWithLifecycle`

### Wear OS
- `TransformingLazyColumn` (replaces `ScalingLazyColumn`)
- `AppScaffold` + `ScreenScaffold` + `TimeText` structure
- Round vs square detection · large display detection (225dp threshold)
- Enforces `:wear` module isolation from mobile `MaterialTheme`

### Android Auto
- `CarAppService` + `Session` + `Screen` skeleton
- `ListTemplate` with driver-distraction-compliant item limits (6 on API 1-2)
- No Compose — template model only, enforced by audit checker
- `app-projected` vs `app-automotive` distinction documented

### Density / Resources
- Full ldpi → xxxhdpi → tvdpi / nodpi / anydpi table
- Bitmap vs vector vs mipmap strategy + pixel size cheat sheet
- Anti-patterns: `px` in Compose, bitmap-only in `drawable/`, `anyDensity="false"`

---

## Using with Other Agents

### Cursor

```bash
cat ~/.claude/skills/android-adaptive-ui/SKILL.md >> .cursorrules
```

### Windsurf

```bash
cat ~/.claude/skills/android-adaptive-ui/SKILL.md >> .windsurfrules
```

### GitHub Copilot

```bash
cat ~/.claude/skills/android-adaptive-ui/SKILL.md >> .github/copilot-instructions.md
```

### Aider

```bash
aider --read ~/.claude/skills/android-adaptive-ui/SKILL.md \
      app/src/main/java/com/example/HomeScreen.kt
```

### Any agent (audit-first workflow)

```bash
python ./skills/android-adaptive-ui/scripts/layout_audit.py \
  --src ./app/src/main --format json > /tmp/audit.json

# Paste /tmp/audit.json into the agent with:
# "Fix all CRITICAL findings using templates at ~/.claude/skills/android-adaptive-ui/templates/"
```

---

## Limitations

| Limitation | Detail |
|---|---|
| **Compose-only templates** | All fix templates are Jetpack Compose. The audit script checks XML, but no View-based fix templates exist. |
| **Android target only** | Templates import `androidx.*`. Compose Multiplatform (`org.jetbrains.compose.*`) is not covered. |
| **KMP partial support** | Audit script doesn't understand KMP source set boundaries. Won't warn if Android-only API appears in `commonMain`. |
| **Heuristic-based audit** | Regex + heuristics, not a full Kotlin AST. May produce false positives on unusual formatting. Use `--format json` to filter. |
| **No runtime testing** | Audits source files only — no emulator, no APK install, no runtime verification. |
| **Companion skills optional** | Ecosystem integrations (graphify, intel, thread) enhance the workflow but are never required. |

---

## Quick Reference Card

```
INSTALL     cp -r android-adaptive-ui ~/.claude/skills/

── Full workflows ────────────────────────────────────────────
AUDIT       /android-adaptive-ui analyze_ui
            /android-adaptive-ui analyze_ui --src app/src/main/java/ui/

FIX ALL     /android-adaptive-ui apply_responsiveness

── Targeted (fast) ──────────────────────────────────────────
BY TRACK    /android-adaptive-ui apply_responsiveness --track <phone|large-screen|foldable|wear|auto|density>
BY CONCERN  /android-adaptive-ui apply_responsiveness --only <deps|optin|nav|api|text|critical>
COMBINED    /android-adaptive-ui apply_responsiveness --track large-screen --only deps

── Atomic sub-commands (fastest) ────────────────────────────
            /android-adaptive-ui fix:deps
            /android-adaptive-ui fix:optin
            /android-adaptive-ui fix:api
            /android-adaptive-ui fix:nav
            /android-adaptive-ui fix:scroll
            /android-adaptive-ui fix:text
            /android-adaptive-ui fix:orientation
            /android-adaptive-ui fix:critical

── Add form factor ───────────────────────────────────────────
EXPAND      /android-adaptive-ui add_form_factor <wear|auto|foldable|large-screen>

── Script (standalone / CI) ─────────────────────────────────
            python scripts/layout_audit.py --src ./app/src/main
            python scripts/layout_audit.py --src HomeScreen.kt
            python scripts/layout_audit.py --src ui/ res/layout/ --memory .adaptive-ui-memory.json
            python scripts/layout_audit.py --src ./app/src/main --format json

── Templates ─────────────────────────────────────────────────
            templates/phone/AdaptiveScaffold.kt
            templates/tablet-large-screen/ListDetailScreen.kt
            templates/foldable/PostureDetector.kt
            templates/wear/WearAppScaffold.kt
            templates/auto/MyCarAppService.kt

── Deps ──────────────────────────────────────────────────────
            gradle/libs.versions.toml.snippet   ← merge into version catalog
            gradle/build.gradle.snippet          ← copy block for your form factor
```
