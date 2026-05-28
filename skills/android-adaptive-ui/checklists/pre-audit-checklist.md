# Pre-Audit Checklist

- [ ] Target source path confirmed (`--src` argument or project root identified).
- [ ] Form factors the project intends to support are known or will be detected.
- [ ] `android:targetSdk` or `targetSdk` in `build.gradle.kts` is ≥ 36 (affects CRITICAL vs WARNING severity for orientation locks).
- [ ] Memory file path agreed (`.adaptive-ui-memory.json` at project root recommended).
- [ ] Companion skills probed and active companions noted (`gsd-graphify`, `gsd-intel`, `gsd-thread`).
- [ ] Audit scope clarified: full project, single module, or specific files only.
- [ ] Developer aware that audit is source-only — no emulator or runtime verification.
