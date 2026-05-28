# Compile Fixtures

Minimal compile-focused Android projects for each form factor path:

- `phone`
- `large-screen`
- `foldable`
- `wear`
- `auto`

Use these in CI to validate dependency snippets and core template imports:

```bash
./skills/android-adaptive-ui/scripts/compile_fixture_projects.sh
```

These are intentionally slim compile fixtures, not runnable product sample apps.
