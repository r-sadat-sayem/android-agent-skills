# android-17-migrate

Scan → report → auto-fix → checklist for Android 17 (API 37) migration.

---

## Workflow

```
/android-17-migrate
        │
        ▼
┌─────────────────────────────┐
│  PHASE 1 — SCAN (read-only) │
│                             │
│  Loads scan-targets.md      │
│  Runs ~14 grep patterns     │
│  across:                    │
│  • build.gradle(s)          │
│  • AndroidManifest.xml      │
│  • *.kt / *.java            │
│  • res/xml/*.xml            │
└─────────────────────────────┘
        │
        ├── 0 findings ──► "✓ No issues" — STOP
        │
        ▼
┌─────────────────────────────┐
│  PHASE 2 — REPORT           │
│                             │
│  Buckets findings by:       │
│  CRITICAL / HIGH /          │
│  MEDIUM / LOW / CLEAN       │
│                             │
│  Every finding shows        │
│  file:line reference        │
└─────────────────────────────┘
        │
        ▼
┌─────────────────────────────┐
│  PHASE 3 — REMEDIATE        │
│                             │
│  Loads fix-patterns.md      │
│                             │
│  autoFixable=true:          │
│    [FIXING] → Edit/Write    │
│    → [DONE] audit trail     │
│                             │
│  autoFixable=false:         │
│    [MANUAL] + exact steps   │
│                             │
│  Summary table at end       │
└─────────────────────────────┘
        │
        ▼
┌─────────────────────────────┐
│  PHASE 4 — CHECKLIST        │
│                             │
│  Loads checklist-template   │
│  Writes MIGRATION_          │
│  CHECKLIST.md scoped to     │
│  only found issues          │
│                             │
│  Includes: summary table,   │
│  regression tests, tools    │
└─────────────────────────────┘
```

---

## Issue IDs

The letter prefix indicates severity; the number is a sequence within that severity.

| ID | Severity | Issue | Auto-fix? |
|----|----------|-------|-----------|
| **P1** | REQUIRED | compileSdk / targetSdk not set to 37 | Conditional |
| **C1** | CRITICAL | CameraX < 1.5.2 — launch crash on Android 17 | Yes |
| **H1** | HIGH | Missing `ACCESS_LOCAL_NETWORK` — LAN silently blocked | Yes |
| **H2** | HIGH | Background audio without `mediaPlayback` FGS — audio stops | No |
| **H3** | HIGH | SMS OTP via direct broadcast — OTP delayed 3 hours | No |
| **H4** | HIGH | Deprecated BAL constant — background activity launch fails | Yes |
| **M1** | MEDIUM | Static final field reflection — `IllegalAccessException` | No |
| **M2** | MEDIUM | `MessageQueue` internal reflection — `IllegalAccessException` | No |
| **M3** | MEDIUM | `System.load()` without `setReadOnly()` — `UnsatisfiedLinkError` | Yes |
| **M4** | MEDIUM | `BluetoothSocket` read loop without EOF check — hangs on disconnect | No |
| **M5** | MEDIUM | Contacts `ACCOUNT_NAME`/`ACCOUNT_TYPE` from Data table — silently null | No |
| **M6** | MEDIUM | `ContactsContract.Data` without `READ_CONTACTS` — `StrictGrammar` exception | No |
| **M7** | MEDIUM | Certificate Transparency disabled in NSC config — TLS failures | Yes |
| **M8** | MEDIUM | Orientation / resize locks — broken layout on tablets and foldables | Yes |
| **L1** | LOW | `usesCleartextTraffic` in manifest — deprecation | Yes |
| **L2** | LOW | NPU/ML library without feature declaration — Play Store targeting | Yes |

> **P1 is a gate.** If `targetSdk` is not 37, none of the Android 17 behavior changes are active and the migration is incomplete regardless of other fixes.

---

## Knowledge Base Files

All detection and fix logic lives in these three files — not hard-coded in the skill:

| File | Purpose |
|------|---------|
| `scan-targets.md` | One entry per breaking change: grep commands, positive-match criteria, severity, auto-fixable flag |
| `fix-patterns.md` | Exact before/after code for every auto-fixable issue; manual steps for the rest |
| `checklist-template.md` | Template for `MIGRATION_CHECKLIST.md` — conditional sections per issue ID, regression tests, tools table |

---

## Prerequisites

- An Android project in the working directory (needs at least one `build.gradle` and `AndroidManifest.xml`)
- Read/write access to project files (Phase 3 edits files in place)
- The three knowledge base files above present in the skill directory
