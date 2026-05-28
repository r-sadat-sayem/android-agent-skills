# Compose Performance Best Practices (Reference)

Source of truth:
- https://developer.android.com/develop/ui/compose/performance/bestpractices

Use this file as a migration-time checklist for performance-sensitive Compose code.

## Key Practices

1. Minimize expensive work in composition.
2. Cache expensive derived values with `remember`.
3. Use stable keys for `LazyColumn`/`LazyRow` items.
4. Use `derivedStateOf` when UI depends on rapidly changing state but should not recompose on every tiny change.
5. Defer state reads as long as possible; read state in the narrowest scope that needs it.
6. Prefer lambda modifier variants for frequently changing values when it avoids unnecessary composition work.
7. Avoid backwards writes: never write to state after reading it in the same composition flow.

## Migration Review Questions

1. Is any list sorting/filtering done on every recomposition?
2. Are lazy list items keyed with stable IDs?
3. Does rapidly changing state trigger broad recompositions?
4. Can state be read later in layout/draw or child scope?
5. Is any state written in composition that could cause recomposition loops?

