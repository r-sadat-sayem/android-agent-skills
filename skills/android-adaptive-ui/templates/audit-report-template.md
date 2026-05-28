# Android Adaptive UI Audit Report

Use this template for manual reports and agent-generated reports.

## 1) Scan Context

- Project:
- Scan date:
- Scanned paths:
- Memory file:
- Companions active:

## 2) Form Factor Detection

- Detected tracks:
- Target tracks requested by team:
- Ambiguities to confirm:

## 3) Scan Summary

- Files scanned: `<N> kt` · `<M> xml`
- Skipped: `<cached>` cached · `<non_ui>` non-UI
- Pending findings: `<critical>` CRITICAL · `<warning>` WARNING · `<info>` INFO

## 4) Findings Index

| # | SEV | FILE:LINE | CATEGORY | Rule ID |
|---|---|---|---|---|
| 1 |  |  |  |  |
| 2 |  |  |  |  |

## 5) Before -> After Plan

| FILE | BEFORE | AFTER | ACTION | TEMPLATE/REF |
|---|---|---|---|---|
|  |  |  |  |  |
|  |  |  |  |  |

## 6) Critical Fix Queue

1. 
2. 
3. 

## 7) Track-Level Decisions

- Phone:
- Large-screen:
- Foldable:
- Wear:
- Auto:
- Density:

## 8) Risks and Trade-offs

- False-positive/heuristic risks:
- Backward-compatibility risks:
- Module isolation risks:
- Team capacity risks:

## 9) Validation Snapshot

- `layout_audit.py` result:
- `validate_fixes.sh` result:
- Smoke/template checks:

## 10) Execution Decision

- [ ] Apply all
- [ ] Apply critical-only
- [ ] One-by-one
- [ ] Skip

Notes:
