---
name: android-17-migrate
description: Use when migrating an Android project to target API 37 (Android 17), or checking
  Android 17 compatibility. Scans manifest, build files, and Kotlin/Java sources for all breaking
  changes, applies fixes automatically, then writes MIGRATION_CHECKLIST.md.
---

# Android 17 (API 37) Migration

Scan → report → auto-fix → checklist. Four sequential phases. Do not skip phases or combine them.

## Phase 1 — Scan (read-only)

Load `references/scan-targets.md` from this skill directory before running any greps.

Run every detection target in `references/scan-targets.md` against the project. Record each positive hit as:
```
{ id, severity, file, line, snippet, autoFixable }
```

Scan locations:
- `**/build.gradle` and `**/build.gradle.kts` — compileSdk, targetSdk (source of truth), CameraX version
- `**/AndroidManifest.xml` — orientation, resizeableActivity, permissions, features, usesCleartextTraffic
- `**/*.kt` and `**/*.java` — reflection, MessageQueue, System.load, SMS, BluetoothSocket, BAL, ContactsContract
- `**/res/xml/network_security_config.xml` — CT and cleartext config
- `**/res/xml/*.xml` — network security configs

When checking `compileSdk`/`targetSdk`: the build files are the source of truth. If they delegate
to a version catalog or variable, trace through to the literal value and fix it there.

If no Android project is detected (no `build.gradle` or `AndroidManifest.xml` found), stop and tell the user.

## Phase 2 — Report

Print a severity-bucketed findings list. Format:

```
── CRITICAL ───────────────────────────────────────
[C1] CameraX < 1.5.2 — crashes ALL apps on Android 17 devices
     app/build.gradle:12  →  camerax-camera2:1.4.0

── HIGH ────────────────────────────────────────────
[H1] Missing ACCESS_LOCAL_NETWORK permission — LAN access blocked
     app/src/main/AndroidManifest.xml

── MEDIUM ──────────────────────────────────────────
...

── LOW ─────────────────────────────────────────────
...

── CLEAN ───────────────────────────────────────────
No issues found for: static-final-reflection, messagequeue-reflection, ...
```

If zero findings across all severities, print "✓ No Android 17 issues detected" and stop (skip phases 3–4).

## Phase 3 — Remediate

Load `references/fix-patterns.md` from this skill directory.

For each finding that is `autoFixable: true`:
1. Print `[FIXING] <id> — <description>  (<file>:<line>)`
2. Apply the fix using the Edit or Write tool
3. Print `[DONE] <one-line summary of what changed>`

For each finding that is `autoFixable: false`:
1. Print `[MANUAL] <id> — <description>`
2. Print the exact manual steps from `fix-patterns.md`

After all findings: print a summary table of fixed vs manual items.

## Phase 4 — Write Checklist

Load `checklists/checklist-template.md` from this skill directory.

Write `MIGRATION_CHECKLIST.md` to the project root. Include only sections whose issue IDs matched
during Phase 1. Omit sections for issues that were not found. Always include:
- Summary table (findings count by severity)
- Tools section
- "How to verify" header

Print `[CHECKLIST] Written to <project-root>/MIGRATION_CHECKLIST.md`

---

## Notes

- Games (Play Store category) are exempt from large-screen constraints — do not flag them.
- If CameraX is found, check ALL camera* dependency versions, not just camera-camera2.
- `setReadOnly()` must appear in the same method/block as `System.load()` to count as safe.
- A `BluetoothSocket` read loop is only flagged if it uses `InputStream.read()` without a `!= -1` check.
- Always show file:line references in every finding — never report issues without a location.
- Every fix applied to the codebase must include a `[DONE]` line with: what changed, the exact
  file(s) modified, and the line number(s) affected — so the developer has a clear audit trail of
  every automatic change made to their project.
