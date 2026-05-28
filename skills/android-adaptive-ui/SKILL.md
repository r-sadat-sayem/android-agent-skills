# Android Adaptive UI Architect

Audit and fix Android UI code for all screen classes: phones, tablets, foldables, Wear OS, Android Auto.

**Baseline:** Compose BOM 2026.04.01 · Kotlin 2.3.10 · Material3 Adaptive 1.2.0 · WindowManager 1.5.1

**Commands:**
```
analyze_ui                                   full audit
apply_responsiveness [--track X] [--only Y]  targeted fix
fix:deps | fix:optin | fix:nav | fix:critical atomic single-concern fixes
add_form_factor <wear|auto|foldable|large-screen>
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

**Probe output (emit once at session start):**
```
COMPANIONS ─────────────────────────────────────
Active: gsd-graphify · gsd-intel · gsd-thread
Inactive (not installed): gsd-scan · gsd-debug
Memory: .adaptive-ui-memory.json
Playbook: 9 patterns loaded (references/solutions-playbook.json)
```

**Playbook usage rules:**
- At session start, read `references/solutions-playbook.json` and index patterns by `detection_signals`.
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
| `:wear` module OR `androidx.wear.compose.*` import | Wear OS |
| `CarAppService` subclass OR `:auto`/`:automotive` module | Android Auto |
| `FoldingFeature` OR `androidx.window:window` dep | Foldable |
| `ListDetailPaneScaffold` / `SupportingPaneScaffold` / `NavigationSuiteScaffold` OR `sw600dp` dirs | Large Screen |
| None of the above | Phone (baseline) |

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
Apply all? [all / one-by-one / critical-only / skip]
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

## 4 — Workflow: `analyze_ui [--src <path>]`

1. If `gsd-intel` active → read `.planning/intel/` first; note already-catalogued files.
2. Infer project root from open file, or use `--src` path, or ask once.
3. Run: `python scripts/layout_audit.py --src <root> --format json --memory <root>/.adaptive-ui-memory.json`
4. Render using format in Section 3.
5. If `gsd-note`/`gsd-add-todo` active → create one todo per CRITICAL finding now.
6. If `gsd-graphify` active → sync findings to graph now.
7. Prompt for confirmation before any code changes.

---

## 5 — Workflow: `apply_responsiveness [--track X] [--only Y]`

Without flags: runs all tracks, all concerns. Heavy — use flags to scope.

### `--track` flag (one form factor at a time)

| Flag | Scope | Typical token cost |
|---|---|---|
| `--track phone` | Navigation scaffold + scroll guards | Low |
| `--track large-screen` | ListDetail / Supporting pane scaffolds | Medium |
| `--track foldable` | PostureDetector + FoldAwareLayout | Medium |
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
2. `wear` → confirm separate `:wear` module exists or scaffold it. If `feature-dev:feature-dev` active and > 3 new files needed → delegate.
3. `auto` → confirm separate `:auto`/`:automotive` module or flavor.
4. `foldable` / `large-screen` → can live in `:app` module.
5. Add deps from `references/dependencies.md`, integrate template step by step.
6. Run `fix:optin` and `fix:deps` as post-checks.
7. If `claude-md-management:revise-claude-md` active → call it now.
8. Run scoped `analyze_ui --src <new files>` as final validation.
9. Run `scripts/validate_fixes.sh <project-root>` as fast post-fix verification.

---

## 8 — Form Factor Reference (compact)

| Track | Templates | Key constraint |
|---|---|---|
| Phone | `phone/AdaptiveScaffold.kt`, `phone/BoxWithConstraintsGuard.kt` | `currentWindowAdaptiveInfo()` once at root |
| Large Screen | `tablet-large-screen/ListDetailScreen.kt`, `SupportingPaneScreen.kt` | All panes in `AnimatedPane {}` · needs `@OptIn` |
| Foldable | `foldable/PostureDetector.kt`, `foldable/FoldAwareLayout.kt` | `collectAsStateWithLifecycle` — never raw coroutine |
| Wear OS | `wear/WearAppScaffold.kt`, `wear/WearRoundSquareLayout.kt` | Separate `:wear` module — never mix `compose.material3` |
| Android Auto | `auto/MyCarAppService.kt`, `auto/MainScreen.kt` | Template model only — no Compose, no `setContent {}` |
| Density | `references/density-table.md` | Vectors in `drawable/`; bitmaps need mdpi + xxhdpi minimum |

Breakpoints → `references/breakpoints.md` · Dependencies → `references/dependencies.md` · Decision guide → `references/form-factor-decision-guide.md`

---

## 9 — Hard Constraints (never violate)

1. No `setContent {}` in any `Screen` subclass (Android Auto).
2. Never import `androidx.compose.material3` in a Wear source set.
3. Never lock `android:screenOrientation` for `targetSdk >= 36` + sw600dp targets.
4. Every file using `adaptive`/`adaptive-layout`/`adaptive-navigation` must have `@file:OptIn(ExperimentalMaterial3AdaptiveApi::class)`.
5. `currentWindowAdaptiveInfo()` called once at composition root — never deep in the tree.
6. `calculateWindowSizeClass(activity)` is deprecated — always replace with `currentWindowAdaptiveInfo().windowSizeClass`.
7. Auto item limit: 6 items max on `minCarApiLevel` 1-2. Suggest pagination, not ignoring the limit.
8. Never block a workflow because a companion skill is absent. Degrade gracefully to memory-file-only mode.
