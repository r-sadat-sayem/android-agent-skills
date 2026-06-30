# Changelog

All notable changes to this project are documented here.

---

## [1.2.0] — 2026-06-10

### Added
- TV form factor support: `TvAppScaffold.kt` template, D-pad navigation, leanback manifest requirements
- Resizable/foldable support: `ResizableLayout.kt`, `PostureDetector.kt`, `FoldAwareLayout.kt`
- `superpowers:verification-before-completion` companion integration — build verified before DONE is emitted; falls back to `verify_project_build.sh` when skill is absent
- `superpowers:subagent-driven-development` companion integration — fixes applied in parallel when ≥5 CRITICAL findings confirmed; falls back to serial execution when skill is absent
- `fix:content-density` atomic command — replaces `GridCells.Fixed(N)` with `GridCells.Adaptive(minSize = 150.dp)`
- `update-skill.sh` — update one or all installed skills from the recorded source URL; supports `--check` dry-run and `--ref` for specific tags
- UX preview server (`ux_preview_server.py`) — localhost pattern feedback page, stdlib only, no pip dependencies
- `generate_layout` workflow — generate adaptive scaffold from PRD file, sketch analysis, or named playbook pattern
- `analyze_sketch` workflow — vision-based detection of navigation pattern, content structure, and device class from a UI screenshot or mockup
- Resizable template track added to `apply_responsiveness --track resizable`
- `verify_project_build.sh` — project-local Gradle build verification script

### Changed
- SKILL.md section numbering: `§4a/4b/4c` → `§5/6/7`; `§5–§9` → `§8–§12` (flat, no sub-sections)
- `add_form_factor` step list: fixed duplicate step numbers (steps 5–7 appeared twice)
- COMPANIONS probe output now shows verification and parallel-exec status lines

### Fixed
- README version string updated from `1.1.0` to `1.2.0`
- COMPANIONS card in README updated to reflect current probe output format
- `fix:content-density` removed `← NEW` tag in Quick Reference Card

---

## [1.1.0] — 2026-05-20

### Added
- PSI-backed Kotlin audit: `layout_audit_psi.sh` + `tools/psi-audit/` Gradle project — lower-noise call-expression-based checks alongside the regex audit
- CI workflow: fixture compilation check, PSI audit, template smoke check
- `validate_fixes.sh` — fast grep-based post-fix verifier (deprecated API, orientation lock, missing `@OptIn`)
- `template_smoke_check.py` — catches compile-breaking Wear template anti-patterns before copy-paste
- Test fixtures in `tests/fixtures/layout/` covering all checker categories
- `references/audit-rules.md` — rule IDs and audit behaviour changelog
- `scripts/install-skill.sh` skill name validation and safer install logic
- `.skill-source` metadata file written on install for `update-skill.sh` to read

### Changed
- Audit script: `HardcodedDpChecker` now skips dp literals assigned to named `val`s (reduces false positives)
- Session start probe output reformatted as compact `COMPANIONS` card

### Fixed
- `FormFactorComplianceChecker` false positive on `WindowInfoTracker` usage outside lifecycle scope
- Bootstrap install script: temp directory cleanup on failure

---

## [1.0.0] — 2026-04-15

### Added
- Initial release: `analyze_ui`, `apply_responsiveness`, `add_form_factor`, `ux_preview`
- Audit checkers: `HardcodedDpChecker`, `ScrollabilityChecker`, `OrientationLockChecker`, `WindowSizeClassApiChecker`, `FormFactorComplianceChecker`, `TextOverflowChecker`
- Templates: phone, tablet/large-screen, foldable, wear, auto
- `solutions-playbook.json` with 13 seed patterns
- `references/`: breakpoints, density table, dependencies, form-factor decision guide, UX patterns
- `scripts/layout_audit.py` — standalone audit, no pip dependencies, JSON output, memory cache
- `scripts/ux_preview_server.py` — localhost UX feedback page
- `scripts/bootstrap-install.sh` — remote one-shot install
- `scripts/install-skill.sh` — local install (copy or symlink)
- Companion skill probe at session start with graceful degradation
- Multi-agent support: Cursor, Windsurf, GitHub Copilot, Aider
- GitHub Actions CI integration examples in README
