# Post-Audit Checklist

- [ ] All CRITICAL findings resolved or explicitly deferred with a reason.
- [ ] `calculateWindowSizeClass()` replaced with `currentWindowAdaptiveInfo().windowSizeClass` in every file.
- [ ] `@file:OptIn(ExperimentalMaterial3AdaptiveApi::class)` present in every file using adaptive scaffold APIs.
- [ ] `currentWindowAdaptiveInfo()` called once at the composition root — not repeated deep in the tree.
- [ ] `BottomNavigation` / hardcoded `NavigationBar` replaced with `NavigationSuiteScaffold`.
- [ ] No `android:screenOrientation` lock remaining for targets with `targetSdk ≥ 36` + sw600dp.
- [ ] Wear OS code is isolated in a separate `:wear` module — no `androidx.compose.material3` imports in Wear source sets.
- [ ] Android Auto `Screen` subclasses do not call `setContent {}`.
- [ ] `WindowInfoTracker` usages collect via `collectAsStateWithLifecycle` — no raw coroutine collection.
- [ ] Memory file (`.adaptive-ui-memory.json`) saved and committed (or git-ignored if preferred).
- [ ] Scoped `analyze_ui` re-run on changed files confirms no regressions.
