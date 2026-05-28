# PSI Audit Tool

Kotlin PSI-backed checker for core adaptive UI signals.

## Checks

- Deprecated `calculateWindowSizeClass(...)`
- Missing `@OptIn(...ExperimentalMaterial3AdaptiveApi::class)` on adaptive API usage
- `Text()` calls missing `overflow`/`maxLines`
- `Column` blocks with high child-signal count and no `verticalScroll`

## Run

From repo root:

```bash
./skills/android-adaptive-ui/scripts/layout_audit_psi.sh --src ./app/src/main --format json
```

Direct Gradle invocation:

```bash
cd skills/android-adaptive-ui/tools/psi-audit
gradle --no-daemon run --args='--src ../../templates --format text'
```
