# Android Adaptive UI Skill

A Codex/Claude-compatible skill that audits, fixes, generates, and previews Android UI code for every screen class: phones, tablets, resizable/foldable, TV, Wear OS, and Android Auto.

**Baseline:** Jetpack Compose · BOM 2026.04.01 · Kotlin 2.3.10 · Material3 Adaptive 1.2.0 · Version 1.1.0

---

## Contents

- [Use Cases](#use-cases)
- [What This Skill Does](#what-this-skill-does)
- [Installation](#installation)
- [Updating](#updating)
- [Testing: Phone → Tablet Migration](#testing-phone--tablet-migration)
- [Claude Code CLI Usage](#claude-code-cli-usage)
  - [Scoped Audit](#scoped-audit-recommended)
  - [Targeted Fix — `apply_responsiveness` Flags](#targeted-fix--apply_responsiveness-flags)
  - [Atomic Sub-commands](#atomic-sub-commands)
  - [UX Preview Server](#ux-preview-server)
  - [Sketch Analysis](#sketch-analysis)
  - [Generate Layout from PRD](#generate-layout-from-prd)
  - [Add a Form Factor](#add-a-form-factor)
  - [Running the Audit Script Directly](#running-the-audit-script-directly)
- [Skill Ecosystem Integration](#skill-ecosystem-integration)
  - [Recommended: install superpowers](#recommended-install-superpowers-for-significantly-better-results)
- [Audit Script (Standalone)](#audit-script-standalone)
- [File Structure](#file-structure)
- [Form Factor Coverage](#form-factor-coverage)
- [Using with Other Agents](#using-with-other-agents)
- [Limitations](#limitations)
- [Quick Reference Card](#quick-reference-card)

---

## Use Cases

See [`USECASES.md`](USECASES.md) for step-by-step workflows covering every scenario:

| # | Scenario |
|---|---|
| 1 | Greenfield — design from a sketch or hand-drawing |
| 2 | Greenfield — generate from a PRD or spec doc |
| 3 | Live phone app → tablet |
| 4 | Live phone app → tablet with visual feedback first |
| 5 | Add a new form factor (TV, Wear, Auto, Resizable) |
| 6 | Fix a known issue without running a full audit |
| 7 | Migrate deprecated Window APIs |
| 8 | Audit a single feature module |
| 9 | Multi-module monorepo — module-by-module |
| 10 | Learn a pattern before applying it |
| 11 | Run in CI without Claude |
| 12 | Recover from a fix that broke something |

---

## What This Skill Does

| Capability | Details |
|---|---|
| **Compose + XML scope** | Compose/Kotlin is the primary target. XML is also audited for key issues (orientation lock, hardcoded dp, scroll ancestry), but XML fix templates are limited. |
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

Remote bootstrap install (download, inspect, run):

```bash
curl -fsSL https://raw.githubusercontent.com/r-sadat-sayem/android-agent-skills/main/scripts/bootstrap-install.sh -o /tmp/bootstrap-install.sh
less /tmp/bootstrap-install.sh
bash /tmp/bootstrap-install.sh --repo https://github.com/r-sadat-sayem/android-agent-skills.git --skill android-adaptive-ui --target both
```

---

## Updating

### What happens when you install via `bootstrap-install.sh`

The script clones the repo to a temp directory, copies the skill to `~/.claude/skills/android-adaptive-ui/`, and deletes the temp clone. This means:

- **No local repo is left behind** — you cannot run `git pull` to update
- **The install location is a plain copy**, not a symlink to any git repository
- A `.skill-source` file is written inside the installed skill directory recording the GitHub URL, ref, and install timestamp — this is what `update-skill.sh` reads to know where to pull from

To check what `.skill-source` contains:
```bash
cat ~/.claude/skills/android-adaptive-ui/.skill-source
# repo=https://github.com/r-sadat-sayem/android-agent-skills.git
# ref=main
# installed_at=2026-06-09T00:00:00Z
```

### Update commands

**Update one skill** (reads `.skill-source`, re-clones, re-installs):
```bash
./scripts/update-skill.sh --skill android-adaptive-ui
```

**Update all installed skills:**
```bash
./scripts/update-skill.sh --all
```

**Only update the Claude install (not Codex):**
```bash
./scripts/update-skill.sh --skill android-adaptive-ui --target claude
```

**Pull a specific tag or branch:**
```bash
./scripts/update-skill.sh --skill android-adaptive-ui --ref v1.2.0
```

**Dry-run — see installed version vs remote version without changing anything:**
```bash
./scripts/update-skill.sh --check --skill android-adaptive-ui
# Claude  android-adaptive-ui  installed=1.0.0   remote=1.1.0
```

### If you installed with `--mode link`

The skill directory is a symlink pointing directly at your local repo clone. `update-skill.sh` detects this and prints a reminder — just run `git pull` in the repo instead. The symlink will immediately reflect the updated files.

### Version file

Each skill ships a `VERSION` file. The current version of this skill:
```bash
cat ~/.claude/skills/android-adaptive-ui/VERSION
```

---

## Testing: Phone → Tablet Migration

Full test prompts are in `references/test-prompts.md`. The core scenario:

**Your mobile UI is live. You want a tablet version without touching the phone layout.**

```
# Step 1 — Audit the phone UI
/android-adaptive-ui analyze_ui --src app/src/main/java/ui/

# Step 2 — Preview UX options in browser before committing
/android-adaptive-ui ux_preview --src app/src/main/java/ui/

# Step 3 — Apply large-screen track only (phone layout unchanged)
/android-adaptive-ui apply_responsiveness --track large-screen

# Step 4 — Fix deps and OptIn annotations
/android-adaptive-ui fix:deps
/android-adaptive-ui fix:optin

# Step 5 — Re-audit to verify 0 CRITICAL
/android-adaptive-ui analyze_ui --src app/src/main/java/ui/
```

**The key guarantee:** `NavigationSuiteScaffold` renders as a standard `BottomNavigationBar` on Compact-width screens (phones) — the phone user sees zero difference. On Medium+ screens (tablets) it auto-promotes to `NavigationRail` or `PermanentNavigationDrawer`.

See `references/test-prompts.md` for 5 full scenarios including screenshot analysis, PRD-to-layout generation, and atomic single-fix flows.

---
## Claude Code CLI Usage

Start a session in your Android project root:

```bash
cd /path/to/your/android/project
claude
```

At session start Claude probes for companion skills and prints a one-line `COMPANIONS` card. See [Skill Ecosystem Integration](#skill-ecosystem-integration) for details.

---

### Scoped Audit (Recommended)

Always scope your audit to a path, module, or feature package. This keeps token usage predictable and the findings table actionable.

```
> /android-adaptive-ui analyze_ui --src app/src/main/java/ui/
> /android-adaptive-ui analyze_ui --src app/src/main/java/ui/HomeScreen.kt
> /android-adaptive-ui analyze_ui --src feature/feed/src/main --module :feature:feed
> /android-adaptive-ui analyze_ui --src app/src/main/java/ui/ app/src/main/res/layout/
```

Emits a compact scan card + findings table + before/after diff, then asks:
```
Apply all? [all / one-by-one / critical-only / skip]
```

**Split strategy for large projects:** run one module or feature package per session. Fixes are tracked in `.adaptive-ui-memory.json` so each run knows what was already resolved.

---

### Full Project Audit — ⚠ Not Recommended

```
> /android-adaptive-ui analyze_ui
```

> **Why not recommended:** Scans every `.kt` and `.xml` UI file from the project root. On a medium-sized project (300+ UI files) this loads a findings table too large to act on in a single session. Token cost is high and the "Apply all?" confirmation becomes impractical.
>
> **When acceptable:** Greenfield or very small projects with fewer than ~50 UI files, or when you want a one-shot inventory to triage before fixing in scoped sessions.

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
| `--track tablet` | ListDetail / SupportingPane scaffolds | Medium |
| `--track resizable` | ResizableLayout + posture detection + multi-window | Medium |
| `--track tv` | TvAppScaffold, D-pad focus, module isolation | Medium |
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
| `fix:content-density` | Replace `GridCells.Fixed(N)` with `GridCells.Adaptive(minSize = 150.dp)` project-wide |

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

### UX Preview Server

Launch a localhost webpage showing adaptive UX options with thumbs feedback — use this before committing to a fix approach.

```
> /android-adaptive-ui ux_preview --src app/src/main/java/ui/
> /android-adaptive-ui ux_preview --pattern navigation-suite-scaffold-migration
> /android-adaptive-ui ux_preview --from-sketch
```

```
UX Preview Server
  URL      : http://localhost:8080
  Patterns : 3
  Feedback : ux_preview_output/feedback.json

Press Enter to stop the server.
```

The page shows pattern cards (one per finding), each with: code snippet, form factor tags, pros/cons list, approach steps, and 👍/👎 feedback buttons. Votes are written to `ux_preview_output/feedback.json`. After you press Enter the skill summarizes the votes.

Run directly without Claude:
```bash
python ./skills/android-adaptive-ui/scripts/ux_preview_server.py \
  --pattern navigation-suite-scaffold-migration --port 8080
```

---

### Sketch Analysis

Analyze a UI screenshot or design mockup — the skill uses vision to detect navigation patterns, content structure, and layout, then maps them to playbook patterns.

```
> /android-adaptive-ui analyze_sketch --img screenshots/home-phone.png
> /android-adaptive-ui analyze_sketch --img mockups/home.png --target large-screen
```

Detection runs in priority order: Navigation → Content → Layout → Device class. Output uses the same FINDINGS format as `analyze_ui`. Adding `--target large-screen` automatically calls `generate_layout --from-sketch` after detection.

---

### Generate Layout from PRD

Generate adaptive Kotlin scaffold code directly from a PRD file, a previous sketch analysis, or a named playbook pattern.

```
> /android-adaptive-ui generate_layout --prd docs/music-player-tablet-prd.md
> /android-adaptive-ui generate_layout --from-sketch
> /android-adaptive-ui generate_layout --pattern content-discovery-feed
```

The skill shows a BEFORE→AFTER diff of what will be created, waits for confirmation, then writes the scaffold files and runs `fix:optin` + `fix:deps` as post-checks.

---

### Add a Form Factor

```
> /android-adaptive-ui add_form_factor phone
> /android-adaptive-ui add_form_factor tablet
> /android-adaptive-ui add_form_factor resizable
> /android-adaptive-ui add_form_factor tv
> /android-adaptive-ui add_form_factor wear
> /android-adaptive-ui add_form_factor auto
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

### Recommended: install `superpowers` for significantly better results

[`superpowers`](https://github.com/obra/superpowers) is the companion skill that makes the biggest difference. It gives this skill structured orchestration capabilities it cannot do on its own:

| Without `superpowers` | With `superpowers` |
|---|---|
| `add_form_factor tv` generates code immediately | Runs brainstorming first — surfaces module structure questions, D-pad navigation decisions, and manifest requirements *before* writing files |
| `generate_layout --prd` writes a scaffold directly | Uses `writing-plans` to produce a reviewable plan you approve before any code is written |
| Compilation error after a fix → Claude improvises | `systematic-debugging` takes over with a structured hypothesis→test→fix loop |
| Complex multi-file changes happen sequentially | `executing-plans` and `dispatching-parallel-agents` run independent tasks concurrently |

**Install via AI agent** — paste into Claude Code or Codex:

```
Install the superpowers skill from https://github.com/obra/superpowers

1. Clone the repo:
   git clone https://github.com/obra/superpowers.git /tmp/superpowers
2. Copy skills into Claude:
   cp -r /tmp/superpowers/skills/* ~/.claude/skills/
3. Verify these are present:
   ls ~/.claude/skills/ | grep -E "brainstorming|writing-plans|systematic-debugging|executing-plans"
4. Clean up:
   rm -rf /tmp/superpowers
```

**Install manually:**

```bash
git clone https://github.com/obra/superpowers.git /tmp/superpowers
cp -r /tmp/superpowers/skills/* ~/.claude/skills/
rm -rf /tmp/superpowers
```

Once installed, the skill probe at session start will show them as active:

```
COMPANIONS ─────────────────────────────────────
Active: superpowers:brainstorming · superpowers:writing-plans
        superpowers:systematic-debugging · superpowers:executing-plans
        gsd-graphify · gsd-intel · gsd-thread
Memory: .adaptive-ui-memory.json
```

### Other Companion Behaviors

| Companion skill | How it's used |
|---|---|
| **`superpowers:brainstorming`** | Runs before `add_form_factor` and `generate_layout` — surfaces design decisions before any code is written |
| **`superpowers:writing-plans`** | Creates a reviewable step-by-step plan before multi-file scaffold generation |
| **`superpowers:systematic-debugging`** | Takes over automatically when an applied fix introduces a new compilation error |
| **`superpowers:executing-plans`** | Runs independent fix tasks in parallel — faster on large audits |
| **`gsd-graphify`** | After each audit, findings are stored as `AdaptiveUIFinding` graph nodes linked to file nodes. Before scanning, the graph is queried to skip already-known clean files. |
| **`gsd-intel`** | Reads `.planning/intel/*.md` before scanning. Files already catalogued there are skipped, reducing traversal on large projects. |
| **`gsd-scan` / `gsd-map-codebase`** | Delegates initial project structure mapping instead of raw `os.walk` — faster on monorepos. |
| **`gsd-thread`** | Wraps each workflow in a named thread (`adaptive-ui-<project>`). Audit state survives Claude context resets and can be resumed mid-flow in future sessions. |
| **`gsd-note` / `gsd-add-todo`** | Creates one tracked todo per CRITICAL finding immediately after `analyze_ui`. |
| **`gsd-debug`** | Fallback systematic debugger when `superpowers:systematic-debugging` is not installed. |
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

- name: PSI audit (core Kotlin checks)
  run: |
    ./skills/android-adaptive-ui/scripts/layout_audit_psi.sh \
      --src ./skills/android-adaptive-ui/templates \
      --format json

- name: Verify target project build (project-local)
  run: |
    ./skills/android-adaptive-ui/scripts/verify_project_build.sh \
      --project-dir . \
      --module app

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

### Fast fix validation (local/CI)

```bash
./skills/android-adaptive-ui/scripts/validate_fixes.sh ./app/src/main
```

Use this for quick post-fix verification without running the full audit. It checks for:
- Deprecated `calculateWindowSizeClass(...)`
- Remaining `BottomNavigation`/`NavigationBar`
- Manifest orientation locks
- Adaptive API usage without `@OptIn(ExperimentalMaterial3AdaptiveApi::class)`

### PSI audit (AST-backed, local/CI)

```bash
./skills/android-adaptive-ui/scripts/layout_audit_psi.sh \
  --src ./app/src/main \
  --format json
```

Use this path when you want lower-noise Kotlin checks (call-expression based) over regex heuristics.

### What the audit checks

| Checker | What it catches |
|---|---|
| `HardcodedDpChecker` | `.dp` literals > 100dp not assigned to a named `val`; XML hardcoded `layout_width`/`layout_height` |
| `ScrollabilityChecker` | `Column` with 5+ children and no `.verticalScroll`; XML `LinearLayout` with no `ScrollView` ancestor |
| `OrientationLockChecker` | `android:screenOrientation` locked; CRITICAL if `targetSdk >= 36` |
| `WindowSizeClassApiChecker` | Deprecated `calculateWindowSizeClass()`; enum equality; missing `@OptIn`; wrong import package |
| `FormFactorComplianceChecker` | Wear/mobile `MaterialTheme` cross-contamination; Compose in Auto `Screen`; `WindowInfoTracker` without lifecycle collection |
| `TextOverflowChecker` | `Text()` without `overflow` or `maxLines` |

PSI-backed core checks are also available via `scripts/layout_audit_psi.sh` (`tools/psi-audit/`), covering:
- deprecated `calculateWindowSizeClass(...)`
- adaptive API use without `@OptIn(...)` (including fully-qualified annotation form)
- `Text()` overflow/maxLines omissions
- `Column` scrollability signals

### What the audit does not check (yet)

| Not checked | Detail |
|---|---|
| Full-project Kotlin AST coverage | PSI audit currently covers core Kotlin checks; XML and some heuristics remain regex-based. |
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
├── USECASES.md                           ← Step-by-step workflows for every scenario
├── VERSION                               ← Skill version (read by update-skill.sh)
│
├── scripts/
│   └── layout_audit.py                  ← Standalone audit script, no pip dependencies
│   └── layout_audit_psi.sh              ← Kotlin PSI-backed audit wrapper
│   └── template_smoke_check.py          ← Wear template compile-safety smoke checks
│   └── validate_fixes.sh                ← Fast grep-based post-fix verifier
│   └── verify_project_build.sh          ← Verifies target project build using its own Gradle config
│   └── ux_preview_server.py             ← Localhost UX preview + feedback server (stdlib only)
│
├── templates/
│   ├── phone/
│   │   ├── AdaptiveScaffold.kt          ← NavigationSuiteScaffold + correct WindowSizeClass API
│   │   └── BoxWithConstraintsGuard.kt   ← Escape hatch for component-level edge cases only
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
│   ├── dependencies.md                  ← Gradle TOML blocks per form factor
│   ├── form-factor-decision-guide.md    ← Signals -> recommendation -> complexity
│   ├── audit-rules.md                   ← Rule IDs + audit behavior changelog
│   ├── ux-patterns.md                   ← Content discovery feed, nav rail, hero, grid composition rules
│   ├── solutions-playbook.json          ← 13 proven fix patterns (9 technical + 4 UX)
│   └── test-prompts.md                  ← Ready-to-paste prompts for 5 test scenarios
│
├── gradle/
│   ├── libs.versions.toml.snippet       ← Paste-ready version catalog entries
│   └── build.gradle.snippet             ← Labeled KTS dependency blocks per form factor
│
└── tools/
    └── psi-audit/                       ← Kotlin compiler PSI-based checker (Gradle project)
```

---

## Form Factor Coverage

### Phone
- `NavigationSuiteScaffold` with automatic `BottomBar → Rail → Drawer` switching
- `BoxWithConstraintsGuard` kept as an escape hatch only (not a primary adaptive strategy)

### Tablet
- `NavigableListDetailPaneScaffold` for master-detail (`ListDetailScreen.kt`)
- `SupportingPaneScaffold` for document / productivity layouts (`SupportingPaneScreen.kt`)
- All 5 `WindowSizeClass` breakpoints: Compact / Medium / Expanded / Large / ExtraLarge
- `AnimatedPane` wrappers + predictive back gesture support

### Resizable (Foldable + Multi-Window)
- `DevicePosture` sealed class: `NormalPosture`, `TableTopPosture`, `BookPosture`, `SeparatingPosture`
- `ResizableLayout.kt` — single composable handles all postures + multi-window resize via `WindowSizeClass`
- Hinge-aware `Spacer` sizing via `FoldingFeature.bounds`
- Lifecycle-safe observation via `produceState` + `WindowInfoTracker`

### Android TV
- `TvAppScaffold.kt` — `NavigationDrawer` + `TvLazyColumn` / `TvLazyRow` content layout
- `Surface {}` required at root — mandatory for TV focus ripple and background
- D-pad-navigable `Card` components with automatic focused/selected states
- Separate `:tv` module — never mix `androidx.tv.*` with the phone `:app`
- Manifest requires `android.software.leanback` + `android.hardware.touchscreen required="false"`

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
| **Mixed parser strategy** | Default audit is regex + heuristics. Use `layout_audit_psi.sh` for lower-noise Kotlin checks where precision matters. |
| **No runtime testing** | Audits source files only — no emulator, no APK install, no runtime verification. |
| **Companion skills optional** | Ecosystem integrations (graphify, intel, thread) enhance the workflow but are never required. |

---

## Quick Reference Card

```
INSTALL     bootstrap-install.sh --repo <url> --skill android-adaptive-ui --target both
UPDATE      ./scripts/update-skill.sh --skill android-adaptive-ui
CHECK VER   ./scripts/update-skill.sh --check --skill android-adaptive-ui

── Phone → Tablet (primary test flow) ───────────────────────
AUDIT       /android-adaptive-ui analyze_ui --src app/src/main/java/ui/
PREVIEW     /android-adaptive-ui ux_preview --src app/src/main/java/ui/
FIX TABLET  /android-adaptive-ui apply_responsiveness --track large-screen
DEPS        /android-adaptive-ui fix:deps
OPTIN       /android-adaptive-ui fix:optin
VERIFY      /android-adaptive-ui analyze_ui --src app/src/main/java/ui/

── UX design workflows (new) ────────────────────────────────
SKETCH      /android-adaptive-ui analyze_sketch --img screenshots/home.png
GENERATE    /android-adaptive-ui generate_layout --prd docs/prd.md
PREVIEW     /android-adaptive-ui ux_preview --pattern <id>

── Full workflows ────────────────────────────────────────────
AUDIT ALL   /android-adaptive-ui analyze_ui
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
            /android-adaptive-ui fix:content-density   ← NEW: GridCells.Fixed → Adaptive

── Add form factor ───────────────────────────────────────────
EXPAND      /android-adaptive-ui add_form_factor <phone|tablet|resizable|tv|wear|auto>

── Script (standalone / CI) ─────────────────────────────────
            python scripts/layout_audit.py --src ./app/src/main
            python scripts/layout_audit.py --src HomeScreen.kt
            python scripts/layout_audit.py --src ui/ res/layout/ --memory .adaptive-ui-memory.json
            python scripts/layout_audit.py --src ./app/src/main --format json
            ./scripts/layout_audit_psi.sh --src ./app/src/main --format json
            ./scripts/validate_fixes.sh ./app/src/main
            ./scripts/verify_project_build.sh --project-dir . --module app
            python scripts/ux_preview_server.py --pattern <id> --port 8080

── Templates ─────────────────────────────────────────────────
            templates/phone/AdaptiveScaffold.kt
            templates/tablet-large-screen/ListDetailScreen.kt
            templates/resizable/ResizableLayout.kt
            templates/tv/TvAppScaffold.kt
            templates/wear/WearAppScaffold.kt
            templates/auto/MyCarAppService.kt
            templates/audit-report-template.md

── Deps ──────────────────────────────────────────────────────
            gradle/libs.versions.toml.snippet   ← merge into version catalog
            gradle/build.gradle.snippet          ← copy block for your form factor

── Decision support ──────────────────────────────────────────
            references/form-factor-decision-guide.md
            references/ux-patterns.md
            references/test-prompts.md          ← 5 test scenarios (phone→tablet, PRD, sketch...)
```
