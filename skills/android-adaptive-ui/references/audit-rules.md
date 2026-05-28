# Audit Rules and Changelog

Use this file to track audit behavior changes over time.

## Rule IDs

| Rule ID | Checker | Severity | Description |
|---|---|---|---|
| `AUDIT-SCROLL-001` | `ScrollabilityChecker` | WARNING | Compose `Column` with 5+ child indicators and no `.verticalScroll(...)`. |
| `AUDIT-SCROLL-002` | `ScrollabilityChecker` | WARNING | XML `LinearLayout` with 5+ direct children and no `ScrollView`/`NestedScrollView` ancestor for that element. |
| `AUDIT-DP-001` | `HardcodedDpChecker` | WARNING | Kotlin `.dp` literal above threshold without extraction. |
| `AUDIT-DP-002` | `HardcodedDpChecker` | WARNING | XML hardcoded large `dp` values in size/padding attrs. |
| `AUDIT-ORIENT-001` | `OrientationLockChecker` | CRITICAL/WARNING | `android:screenOrientation` lock in manifest (`targetSdk` aware). |
| `AUDIT-WSC-001` | `WindowSizeClassApiChecker` | CRITICAL | Deprecated `calculateWindowSizeClass(...)`. |
| `AUDIT-WSC-002` | `WindowSizeClassApiChecker` | WARNING | Fragile enum-equality comparisons for size classes. |
| `AUDIT-WSC-003` | `WindowSizeClassApiChecker` | WARNING | Deprecated `windowsizeclass` import package. |
| `AUDIT-WSC-004` | `WindowSizeClassApiChecker` | CRITICAL | Adaptive APIs used without `@OptIn(ExperimentalMaterial3AdaptiveApi::class)`. |
| `AUDIT-WEAR-001` | `FormFactorComplianceChecker` | CRITICAL | Wear and mobile Material imports mixed in one file. |
| `AUDIT-AUTO-001` | `FormFactorComplianceChecker` | CRITICAL | `setContent {}` used in Android Auto `Screen` subclass. |
| `AUDIT-FOLD-001` | `FormFactorComplianceChecker` | WARNING | `WindowInfoTracker` without lifecycle-safe collection. |
| `AUDIT-TEXT-001` | `TextOverflowChecker` | INFO | `Text()` without overflow/maxLines guard. |

## Changelog

### 2026-05-28

- `AUDIT-SCROLL-002`: fixed to evaluate scroll ancestry per `LinearLayout` element (was incorrectly document-level).
- `AUDIT-SCROLL-002`: finding message now includes a specific element descriptor (`Tag[@id]` when available) and source line hint.
- Added Wear template smoke guard via `scripts/template_smoke_check.py` to catch compile-breaking `Int.dp` extension misuse.
