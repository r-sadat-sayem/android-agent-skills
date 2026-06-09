# Use Cases

Step-by-step workflows for every scenario this skill covers. Each use case starts with the situation you're in, shows the exact prompts to type, and describes what the agent does and what you will see at each step.

**Prerequisites for all use cases:**
- Claude Code or Codex open at your Android project root (`cd /path/to/your/project && claude`)
- Skill installed: `~/.claude/skills/android-adaptive-ui/` exists
- Python 3.9+ available (for audit scripts and preview server)

---

## Contents

1. [Greenfield — Design from a Sketch or Hand-Drawing](#1-greenfield--design-from-a-sketch-or-hand-drawing)
2. [Greenfield — Generate from a PRD or Spec Doc](#2-greenfield--generate-from-a-prd-or-spec-doc)
3. [Live Phone App → Tablet](#3-live-phone-app--tablet)
4. [Live Phone App → Tablet (Visual Feedback First)](#4-live-phone-app--tablet-visual-feedback-first)
5. [Add a New Form Factor to a Live App](#5-add-a-new-form-factor-to-a-live-app)
6. [Fix a Known Issue (Atomic — No Audit Needed)](#6-fix-a-known-issue-atomic--no-audit-needed)
7. [Migrate Deprecated Window APIs](#7-migrate-deprecated-window-apis)
8. [Audit a Single Feature Module](#8-audit-a-single-feature-module)
9. [Multi-Module Monorepo — Module-by-Module](#9-multi-module-monorepo--module-by-module)
10. [Learn a Pattern Before Applying It](#10-learn-a-pattern-before-applying-it)
11. [Run in CI Without Claude](#11-run-in-ci-without-claude)
12. [Recover from a Fix That Broke Something](#12-recover-from-a-fix-that-broke-something)

---

## 1. Greenfield — Design from a Sketch or Hand-Drawing

**Situation:** You have a hand-drawn wireframe or a screenshot of a reference app. You want to turn it into adaptive Kotlin scaffold code without writing anything yourself first.

**When to use:** Starting a new screen from visual input rather than a written spec.

---

**Step 1 — Point the skill at your image**

```
/android-adaptive-ui analyze_sketch --img designs/home-wireframe.png
```

The agent reads the image using vision and runs detection in priority order:
1. Identifies the navigation pattern (bottom bar → phone baseline)
2. Maps content blocks to UX components (circular row → Quick Access, card grid → Discovery Grid, tall banner → Hero Content)
3. Classifies the device from proportions and density
4. Matches each detected component to a playbook pattern

You see:

```
SKETCH ANALYSIS ────────────────────────────────────
Source        : designs/home-wireframe.png
Detected form : Phone (bottom navigation bar detected)
Patterns found: 3

FINDINGS
1  WARNING  NavigationBar   Will not adapt on tablet → navigation-suite-scaffold-migration
2  WARNING  ContentGrid     2-column inferred → discovery-grid-responsive
3  INFO     HeroBanner      Single hero — rule satisfied

Generate adaptive version? [yes / ux_preview / skip]
```

---

**Step 2 — Preview UX options and pick one**

Type `ux_preview` at the prompt, or run:

```
/android-adaptive-ui ux_preview --from-sketch
```

The browser opens automatically at `http://localhost:8080`. You see one card per detected pattern, each showing the code approach, pros, and watch-outs. Click the card that matches your intent. Click **Submit**.

The browser closes. The agent reads your selection.

---

**Step 3 — Agent implements automatically**

No further prompt needed. After Submit the agent:
- Calls `generate_layout --pattern <your-selection>`
- Shows a BEFORE→AFTER diff of the files it will create
- Writes the scaffold files after you confirm the diff
- Runs `fix:optin` → `fix:deps` → re-audit

You see:

```
DONE ────────────────────────────────────────────────
Selected  : navigation-suite-scaffold-migration
Generated : app/src/main/java/ui/HomeScreen.kt
✓  fix:optin   — @OptIn added to 1 file
✓  fix:deps    — material3-adaptive-navigation-suite added
✓  analyze_ui  — 0 CRITICAL · 0 WARNING on new files
```

---

**Step 4 — Target a specific form factor directly (optional shortcut)**

If you already know you want the tablet version, skip the interactive preview entirely:

```
/android-adaptive-ui analyze_sketch --img designs/home-wireframe.png --target tablet
```

The agent detects, generates, writes — in one command.

---

## 2. Greenfield — Generate from a PRD or Spec Doc

**Situation:** A product manager or designer has written a PRD (Product Requirements Document) describing the app screens, navigation, and responsive rules. You want to generate the Kotlin scaffold directly from that document.

**When to use:** Spec-driven development where the layout requirements are already written down.

---

**Step 1 — Point the skill at your PRD**

```
/android-adaptive-ui generate_layout --prd docs/music-player-prd.md
```

The agent reads the PRD and extracts:
- Navigation type (`"Bottom Navigation"` → `NavigationSuiteScaffold`)
- Content sections (Quick Access, Discovery Cards, Featured Content, Feed)
- Responsive rules (`"Navigation Rail on tablet"` → Medium+ breakpoint)
- Form factors mentioned (`"Phone and Tablet"` → phone + tablet track)

It selects the matching templates from `templates/` and shows a diff of the files to create.

---

**Step 2 — Review the diff and confirm**

The agent shows a compact BEFORE→AFTER diff (not the full file). Review the structure. Type `yes` to proceed.

The agent writes the scaffold, runs `fix:optin` + `fix:deps`, and audits the new files.

---

**Step 3 — Iterate if needed**

If the generated scaffold doesn't match a section of the PRD, ask the agent to adjust:

```
The PRD says the hero banner should be full-width on tablet too. Update the hero section.
```

The agent applies the targeted change without regenerating everything.

---

## 3. Live Phone App → Tablet

**Situation:** Your phone app is live and shipping. You want to add a tablet layout without touching or breaking the phone experience. This is the most common use case.

**The guarantee:** `NavigationSuiteScaffold` renders as an identical `BottomNavigationBar` on Compact-width screens (phones). Tablet users get the rail. Phone users see zero change.

---

**Step 1 — Audit the phone UI**

```
/android-adaptive-ui analyze_ui --src app/src/main/java/ui/
```

The agent scans your UI files and shows a findings table:

```
FINDINGS
1  CRITICAL  HomeScreen.kt:12    Navigation    BottomNavigation → NavigationSuiteScaffold
2  WARNING   HomeScreen.kt:45    LargeScreen   GridCells.Fixed(2) — not tablet-adaptive
3  WARNING   HomeScreen.kt:78    LargeScreen   HeroBanner fillMaxWidth — cap on tablet
4  INFO      FeedScreen.kt:33    Scrollability LazyColumn — no change needed

PENDING: 1 CRITICAL · 2 WARNING · 1 INFO
Apply all? [all / one-by-one / critical-only / skip / ux_preview]
```

---

**Step 2 — Apply the tablet track only**

This applies all tablet-related findings and leaves everything else untouched:

```
/android-adaptive-ui apply_responsiveness --track tablet
```

What changes:
- `BottomNavigation` → `NavigationSuiteScaffold`
- `GridCells.Fixed(2)` → `GridCells.Adaptive(minSize = 150.dp)`
- `HeroBanner` gets `widthIn(max = 800.dp)` cap

What does NOT change:
- Scroll behavior, text overflow, orientation, any non-tablet code

---

**Step 3 — Add missing Gradle dependencies**

```
/android-adaptive-ui fix:deps
```

Adds `material3-adaptive-navigation-suite` to `app/build.gradle.kts` if missing.

---

**Step 4 — Add OptIn annotations**

```
/android-adaptive-ui fix:optin
```

Adds `@file:OptIn(ExperimentalMaterial3AdaptiveApi::class)` to every file that uses adaptive APIs.

---

**Step 5 — Verify**

```
/android-adaptive-ui analyze_ui --src app/src/main/java/ui/
```

Expect: 0 CRITICAL, 0 WARNING on previously-flagged files.

---

## 4. Live Phone App → Tablet (Visual Feedback First)

**Situation:** Same as Use Case 3, but you want to see the UX options in a browser and pick which approach to apply before any code is written. Useful when there are multiple valid patterns and you want to align with your team.

---

**Step 1 — Audit**

```
/android-adaptive-ui analyze_ui --src app/src/main/java/ui/
```

---

**Step 2 — Open the preview instead of applying immediately**

At the `Apply all?` prompt, type `ux_preview`, or run directly:

```
/android-adaptive-ui ux_preview --src app/src/main/java/ui/
```

The browser opens. You see a card for each finding — `NavigationSuiteScaffold`, `GridCells.Adaptive`, hero width cap — each with code snippet, pros, and watch-outs.

---

**Step 3 — Pick the approach and click Submit**

Click the card that matches your team's decision. Click **Submit**. Browser closes.

---

**Step 4 — Agent implements automatically**

The agent reads your selection from `feedback.json` and proceeds without another prompt:
- Generates the scaffold
- Shows the diff
- Writes files after your diff confirmation
- Runs `fix:optin` → `fix:deps` → re-audit

---

## 5. Add a New Form Factor to a Live App

**Situation:** Your phone app works well. Now you need to support a completely new surface — TV, Wear OS, Android Auto, or resizable/foldable — as a product requirement.

**When to use:** Expanding platform coverage, not just improving an existing layout.

---

**Step 1 — Check the decision guide first**

```
/android-adaptive-ui add_form_factor tv
```

Before writing any code, the agent reads `references/form-factor-decision-guide.md` and checks your project's Gradle setup.

If `superpowers:brainstorming` is installed, it runs a structured session first — surfacing module structure decisions, manifest requirements, and D-pad navigation constraints before touching any files.

---

**Step 2 — Agent scaffolds the new module**

For `tv`, `wear`, and `auto` — which require separate Gradle modules — the agent:
1. Confirms whether the `:tv` (or `:wear` / `:auto`) module exists or needs to be created
2. Adds the correct dependencies from `references/dependencies.md`
3. Integrates the template step by step (`templates/tv/TvAppScaffold.kt`, etc.)
4. Runs `fix:optin` + `fix:deps` as post-checks
5. Audits the new files

For `resizable` and `tablet` — which live in `:app` — no new module is needed.

---

**Step 3 — Validate**

```
/android-adaptive-ui analyze_ui --src tv/src/main/java/
```

---

**Form factor commands:**

| What you want | Command |
|---|---|
| Harden phone navigation + scroll | `add_form_factor phone` |
| Add tablet two-pane layout | `add_form_factor tablet` |
| Support foldables + multi-window | `add_form_factor resizable` |
| Add Android TV support | `add_form_factor tv` |
| Add Wear OS companion | `add_form_factor wear` |
| Add Android Auto support | `add_form_factor auto` |

---

## 6. Fix a Known Issue (Atomic — No Audit Needed)

**Situation:** You already know what's wrong — a code reviewer flagged it, you spotted it yourself, or CI is failing. You don't need a full audit.

**When to use:** Targeted single-concern fixes when the problem is already identified.

---

**Pick the command that matches your problem:**

```
/android-adaptive-ui fix:nav
```
Migrates all `BottomNavigation(` and standalone `NavigationBar(` calls to `NavigationSuiteScaffold` across the entire project. One command, no scanning.

```
/android-adaptive-ui fix:content-density
```
Replaces all `GridCells.Fixed(N)` with `GridCells.Adaptive(minSize = 150.dp)`. Fixes hardcoded grid columns project-wide.

```
/android-adaptive-ui fix:api
```
Replaces deprecated `calculateWindowSizeClass(activity)` with `currentWindowAdaptiveInfo().windowSizeClass`. Safe to run repeatedly — only touches files with the old call.

```
/android-adaptive-ui fix:text
```
Adds `overflow = TextOverflow.Ellipsis, maxLines = 1` to bare `Text()` calls missing them.

```
/android-adaptive-ui fix:scroll
```
Adds `.verticalScroll(rememberScrollState())` to `Column` blocks with 5+ children that have no scroll modifier.

```
/android-adaptive-ui fix:orientation
```
Removes or sets to `unspecified` any `android:screenOrientation` lock in the manifest. Required for targetSdk 36+ on large-screen targets.

```
/android-adaptive-ui fix:deps
```
Checks `app/build.gradle.kts` and adds any missing adaptive Gradle entries. No code changes.

```
/android-adaptive-ui fix:optin
```
Adds `@file:OptIn(ExperimentalMaterial3AdaptiveApi::class)` to files that use adaptive APIs but are missing the annotation. Build error fix.

---

**What you see for each atomic fix:**

```
FIX:NAV ─────────────────────────────────────────
Scope   : BottomNavigation → NavigationSuiteScaffold
Files   : 4 candidates → 3 need fix, 1 already correct

CHANGES
HomeScreen.kt:12    REPLACE  BottomNavigation { } → NavigationSuiteScaffold(…)
SettingsScreen.kt:8 REPLACE  NavigationBar { }    → NavigationSuiteScaffold(…)
ProfileScreen.kt:6  REPLACE  BottomNavigation { } → NavigationSuiteScaffold(…)

Apply? [yes / no]
```

Type `yes`. Done.

---

## 7. Migrate Deprecated Window APIs

**Situation:** You're upgrading to a newer version of Material3 Adaptive and the build is failing or showing deprecation warnings because of old `calculateWindowSizeClass(activity)` calls or `WindowWidthSizeClass.Expanded ==` enum equality checks.

---

**Step 1 — Run the API migration fix**

```
/android-adaptive-ui fix:api
```

The agent finds every `calculateWindowSizeClass(` call in the project and replaces it with `currentWindowAdaptiveInfo().windowSizeClass`. It also flags any `WindowWidthSizeClass.Compact ==` / `.Expanded ==` enum equality checks and replaces them with `isWidthAtLeastBreakpoint(WIDTH_DP_EXPANDED_LOWER_BOUND)`.

---

**Step 2 — Add OptIn (likely needed after the API migration)**

```
/android-adaptive-ui fix:optin
```

---

**Step 3 — Verify no regressions**

```
/android-adaptive-ui analyze_ui --src app/src/main/java/ui/
```

Expect: `WindowSizeClass` category shows 0 findings.

---

**Why the enum equality check matters:**

`WindowWidthSizeClass.Expanded` breaks when Google adds `Large` and `ExtraLarge` classes — code that checks `== Expanded` stops matching the new larger classes. `isWidthAtLeastBreakpoint(WIDTH_DP_EXPANDED_LOWER_BOUND)` is a forward-compatible boolean that keeps working as new size classes are added.

---

## 8. Audit a Single Feature Module

**Situation:** You're working on one feature (`feed`, `profile`, `search`) and want to check only that module without loading the full project into context.

**When to use:** Day-to-day development, PR reviews, pre-merge checks on a specific feature.

---

**Scope by directory:**

```
/android-adaptive-ui analyze_ui --src feature/feed/src/main/java/
```

---

**Scope by module name:**

```
/android-adaptive-ui analyze_ui --src feature/feed/src/main --module :feature:feed
```

---

**Scope by single file:**

```
/android-adaptive-ui analyze_ui --src app/src/main/java/ui/HomeScreen.kt
```

---

**Scope mixed paths (Kotlin + XML together):**

```
/android-adaptive-ui analyze_ui --src app/src/main/java/ui/ app/src/main/res/layout/
```

---

The agent scans only the specified paths. Clean files (unchanged since last run) are skipped using the `.adaptive-ui-memory.json` cache — subsequent runs on the same files are much faster.

---

## 9. Multi-Module Monorepo — Module-by-Module

**Situation:** Large project with many feature modules. You want to audit the whole project without loading everything into context at once.

**When to use:** Projects with 50+ UI files. Attempting a full project audit on these is not recommended — the findings table becomes too large to act on.

---

**Strategy: one module per session, work through the list.**

The memory file (`.adaptive-ui-memory.json`) tracks which files have already been audited and resolved. Each session picks up where the last one left off.

---

**Session 1 — Home feature**

```
/android-adaptive-ui analyze_ui --src feature/home/src/main --module :feature:home
```

Fix findings, commit.

---

**Session 2 — Feed feature**

```
/android-adaptive-ui analyze_ui --src feature/feed/src/main --module :feature:feed
```

Fix findings, commit.

---

**Session 3 — Shared UI components**

```
/android-adaptive-ui analyze_ui --src common/ui/src/main/java/
```

---

**Check what's still open across all previous sessions:**

```
/android-adaptive-ui fix:critical
```

This re-reads `.adaptive-ui-memory.json` and applies all findings that were flagged CRITICAL but not yet resolved across any previous session.

---

## 10. Learn a Pattern Before Applying It

**Situation:** You want to understand what `NavigationSuiteScaffold` or `ListDetailPaneScaffold` looks like in practice — the code, the trade-offs, the constraints — before committing to using it in your project. Or you're onboarding a new team member and want to walk them through the options.

**When to use:** Education, team alignment, pre-implementation review.

---

**Open the preview for any named pattern:**

```
/android-adaptive-ui ux_preview --pattern navigation-suite-scaffold-migration
```

Browser opens. You see the full pattern card: problem statement, code snippet, pros, watch-outs, approach steps.

---

**Browse patterns by form factor:**

```
/android-adaptive-ui ux_preview --pattern list-detail-pane-large-screen
/android-adaptive-ui ux_preview --pattern content-discovery-feed
/android-adaptive-ui ux_preview --pattern discovery-grid-responsive
/android-adaptive-ui ux_preview --pattern foldable-posture-detection
```

---

**All available pattern IDs:**

| Pattern | Category |
|---|---|
| `navigation-suite-scaffold-migration` | Navigation |
| `navigation-rail-migration` | Navigation |
| `list-detail-pane-large-screen` | LargeScreen |
| `content-discovery-feed` | LargeScreen |
| `hero-content-pattern` | LargeScreen |
| `discovery-grid-responsive` | LargeScreen |
| `column-vertical-scroll` | Scrollability |
| `infinite-scroll-lazycolumn` | Scrollability |
| `text-overflow-ellipsis` | TextOverflow |
| `foldable-posture-detection` | Foldable |
| `wear-module-isolation` | Wear |
| `android-auto-template-model` | Auto |
| `window-size-class-api-migration` | WindowSizeClass |

---

**No project needed.** The preview server runs from the skill's own playbook — you don't need to be in an Android project directory.

---

## 11. Run in CI Without Claude

**Situation:** You want the audit running on every PR in GitHub Actions, failing the build on CRITICAL findings, without needing Claude Code in the pipeline.

**When to use:** Automated quality gates, preventing regressions on main.

---

**Step 1 — Add to your GitHub Actions workflow**

```yaml
- name: Android Adaptive UI Audit
  run: |
    python ./skills/android-adaptive-ui/scripts/layout_audit.py \
      --src app/src/main \
      --memory .adaptive-ui-memory.json \
      --format json > audit-report.json
    cat audit-report.json

- name: Fail on CRITICAL findings
  run: |
    CRITICALS=$(python3 -c "
    import json, sys
    data = json.load(open('audit-report.json'))
    findings = data.get('findings', [])
    criticals = [f for f in findings if f.get('severity') == 'CRITICAL']
    print(len(criticals))
    ")
    if [ "$CRITICALS" -gt "0" ]; then
      echo "Build failed: $CRITICALS CRITICAL adaptive UI findings"
      exit 1
    fi

- name: Upload audit report
  uses: actions/upload-artifact@v4
  with:
    name: adaptive-ui-audit
    path: audit-report.json
```

---

**Step 2 — Add fast post-fix validation (optional, runs in seconds)**

```yaml
- name: Fast adaptive UI check
  run: |
    ./skills/android-adaptive-ui/scripts/validate_fixes.sh app/src/main/java
```

This grep-based check catches the four most common regressions:
- Remaining `calculateWindowSizeClass(` calls
- Remaining `BottomNavigation(` without `NavigationSuiteScaffold`
- Manifest orientation locks
- Adaptive API usage without `@OptIn`

---

**Step 3 — PSI audit for lower-noise Kotlin checks (optional)**

```yaml
- name: PSI audit
  run: |
    ./skills/android-adaptive-ui/scripts/layout_audit_psi.sh \
      --src ./app/src/main \
      --format json
```

Uses the Kotlin compiler PSI (AST-backed) rather than regex — fewer false positives.

---

**Exit codes:**

| Code | Meaning |
|---|---|
| `0` | No CRITICAL findings |
| `1` | One or more CRITICAL findings |
| `2` | Bad arguments or path not found |

---

## 12. Recover from a Fix That Broke Something

**Situation:** You applied a fix and now the project doesn't compile, or a screen looks wrong. You need to diagnose and recover.

---

**If the build fails immediately after a fix — let the skill diagnose:**

If `superpowers:systematic-debugging` is installed, the skill hands off automatically when it detects a compilation error after applying a fix. You will see:

```
ERROR: Compilation failed after applying fix:nav
Handing off to systematic-debugging...
```

The debugger runs a hypothesis → test → fix loop and reports what went wrong.

---

**If you need to diagnose manually:**

```
/android-adaptive-ui analyze_ui --src app/src/main/java/ui/
```

Re-auditing the changed files immediately after a failed fix will surface any new CRITICAL findings introduced by the change. These are shown as new entries distinct from the original findings.

---

**If you want to scope the re-audit to only the files that were just changed:**

```
/android-adaptive-ui analyze_ui --src app/src/main/java/ui/HomeScreen.kt
```

---

**Common causes and their fixes:**

| Symptom | Likely cause | Fix |
|---|---|---|
| `Unresolved reference: NavigationSuiteScaffold` | Missing Gradle dep | `/android-adaptive-ui fix:deps` |
| `This declaration needs opt-in` | Missing `@OptIn` | `/android-adaptive-ui fix:optin` |
| `@Composable invocations can only happen from...` | `currentWindowAdaptiveInfo()` called outside composable | Move call to composition root |
| Scroll stops working | `.verticalScroll` added to a `LazyColumn` | Use `LazyColumn` directly — remove `.verticalScroll` |
| TV app missing from Play Store TV section | Missing manifest `<uses-feature>` | Add `android.hardware.touchscreen required="false"` |
| Wear app crashes on launch | Mixed `compose.material3` + `wear.compose.material3` | Move Wear code to separate `:wear` module |

---

## Quick Decision Guide

**"Which use case am I in?"**

```
I have a sketch or screenshot and no code yet
→ Use Case 1 (analyze_sketch)

I have a PRD/spec doc and no code yet
→ Use Case 2 (generate_layout --prd)

I have a working phone app and want tablet support
→ Use Case 3 or 4 (apply_responsiveness --track tablet)

I need to add TV / Wear / Auto / Foldable support
→ Use Case 5 (add_form_factor)

I know exactly which file/issue needs fixing
→ Use Case 6 (fix:nav / fix:api / fix:scroll / etc.)

I'm upgrading Material3 Adaptive versions
→ Use Case 7 (fix:api)

I want to check one feature module during development
→ Use Case 8 (analyze_ui --src feature/...)

Large project, want to audit without overwhelming the context
→ Use Case 9 (one module per session)

I want to understand a pattern before using it
→ Use Case 10 (ux_preview --pattern <id>)

I want automated checks on every PR
→ Use Case 11 (CI scripts)

Something broke after a fix
→ Use Case 12 (re-audit + systematic-debugging)
```
