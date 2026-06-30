# Contributing

Thanks for helping improve this skill. There are three meaningful ways to contribute.

---

## 1. Adding a playbook pattern

Patterns live in `skills/android-adaptive-ui/references/solutions-playbook.json`. A pattern is worth adding when:

- You hit a real-world adaptive UI problem not covered by the existing 13 entries
- You have a working code fix (not just a description)
- The fix is Jetpack Compose or WindowManager — not View-system-only

**Schema** (all fields required):

```json
{
  "id": "kebab-case-unique-id",
  "category": "WindowSizeClass|Navigation|Scrollability|Foldable|Wear|Auto|LargeScreen|TextOverflow|Density",
  "form_factors": ["phone", "large-screen", "foldable", "wear", "auto"],
  "detection_signals": ["exact code strings that identify this pattern in source"],
  "problem": "One sentence: what goes wrong without this fix.",
  "approach": ["Numbered steps to apply the fix."],
  "code_sketch": "Minimal Kotlin snippet showing the fix.",
  "template_ref": "templates/relative/path.kt or null",
  "constraints": ["Things that must not be done."],
  "atomic_fix": "fix:command if one covers this, else null",
  "success_count": 1,
  "last_applied": "2026-01-01T00:00:00Z",
  "contributor": "your-github-handle"
}
```

**PR checklist for new patterns:**
- [ ] `id` is unique and kebab-case
- [ ] `detection_signals` contains at least one string that would actually appear verbatim in source code
- [ ] `code_sketch` compiles (paste it into Android Studio or run `template_smoke_check.py`)
- [ ] `template_ref` points to a real file in `templates/` or is `null`
- [ ] JSON is valid (`python3 -m json.tool solutions-playbook.json`)

---

## 2. Submitting a new Kotlin template

Templates live in `skills/android-adaptive-ui/templates/<form-factor>/`. They are paste-ready production scaffolds — not minimal examples.

**Standards for templates:**
- Use `currentWindowAdaptiveInfo()` — never the deprecated `calculateWindowSizeClass()`
- Include `@file:OptIn(ExperimentalMaterial3AdaptiveApi::class)` at the top of every file that uses adaptive APIs
- No hardcoded dp values > 100dp outside a named `val`
- `Column` with 5+ children must have `.verticalScroll(rememberScrollState())`
- Wear templates must not import `androidx.compose.material3`
- TV templates must not import `androidx.tv.*` alongside phone `MaterialTheme`
- Run `python scripts/template_smoke_check.py` before submitting — this catches the most common compile-breaking patterns

**PR checklist for new templates:**
- [ ] Template compiles (smoke check passes)
- [ ] Hard constraints from `SKILL.md §12` are all satisfied
- [ ] A matching entry in `solutions-playbook.json` references this template via `template_ref`
- [ ] Added to the File Structure section of `README.md`

---

## 3. Reporting a bug

Use the **Bug Report** issue template. The most useful reports include:

- The exact command you ran (e.g. `analyze_ui --src app/src/main/java/ui/`)
- The audit script JSON output: `python scripts/layout_audit.py --src <path> --format json`
- Expected vs actual behaviour
- Kotlin/Compose version if it's a false positive or missed detection

---

## Development setup

```bash
git clone https://github.com/r-sadat-sayem/android-agent-skills.git
cd android-agent-skills

# Symlink install (changes to the repo are reflected immediately)
./scripts/install-skill.sh --skill android-adaptive-ui --mode link --target claude

# Verify
ls -la ~/.claude/skills/android-adaptive-ui
```

Run the test suite before submitting a PR:

```bash
# Audit script unit tests
python -m pytest skills/android-adaptive-ui/tests/ -v

# Template smoke check
python skills/android-adaptive-ui/scripts/template_smoke_check.py

# Fast fix validator
./skills/android-adaptive-ui/scripts/validate_fixes.sh \
  skills/android-adaptive-ui/tests/fixtures/layout/
```

---

## What we don't accept

- View-system fix templates (audit detection is fine; templates are Compose-only)
- Compose Multiplatform patterns — this skill targets Android only
- KMP source-set patterns — out of scope until the audit script understands KMP boundaries
- Patterns that require external Gradle plugins not in AOSP or Google Maven
