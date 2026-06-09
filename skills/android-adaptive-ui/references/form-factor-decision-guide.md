# Form Factor Decision Guide

Use this guide before `add_form_factor` so decisions are based on product signals, not guesswork.

## Decision Matrix

| Signal | Recommendation | ROI | Complexity | Why |
|---|---|---|---|---|
| Tablet usage >= 30% DAU or PM target includes productivity/education dashboards | Add `tablet` now | High | Medium | Two-pane/adaptive nav directly impacts task completion and retention on wide screens. |
| App needs to resize gracefully in multi-window OR foldable usage >= 5-10% DAU | Add `resizable` after tablet baseline | Medium-High | Medium | Covers both foldable postures and multi-window; single track handles all resize scenarios. |
| Primary use case is glanceable wearable interactions (fitness, notifications, quick actions) | Add `wear` with separate `:wear` module | Medium-High | Medium-High | Watch flows are distinct; module isolation is mandatory to avoid theme/runtime conflicts. |
| Primary use case is in-car or automotive companion workflows | Add `auto` with `CarAppService` template model | High (for target users) | Medium | Android Auto requires template APIs; cannot be approximated by mobile Compose UI. |
| Content/media app targeting living-room users (streaming, games, music) | Add `tv` with separate `:tv` module | High (for target users) | Medium-High | TV requires D-pad navigation, focus management, and a separate material library — incompatible with phone UI. |
| Media-heavy or image-heavy app with bitmap assets and mixed device classes | Add `density` pass early | Medium | Low | Density hygiene prevents blur/memory waste and improves perceived quality. |
| Team is small and only phone traffic matters (<10% non-phone DAU) | Keep `phone` only for now; defer others | Low immediate ROI for expansion | Low | Avoid broad scope before product demand appears. |

## Prioritization Heuristics

1. Always stabilize `phone` first.
2. If tablet signal is strong, prioritize `tablet` before `resizable`.
3. `resizable` covers both foldables and multi-window — do both together, not separately.
4. Treat `wear`, `auto`, and `tv` as separate product surfaces with their own modules.
5. Run `density` checks whenever bitmap-heavy surfaces are present.

## Complexity Bands

| Form Factor | Complexity | Typical Work |
|---|---|---|
| `phone` | Low | Navigation/scroll/overflow hardening. |
| `tablet` | Medium | Pane scaffold integration, adaptive navigation, opt-in/API cleanup. |
| `resizable` | Medium | Posture detection, hinge-aware layouts, lifecycle-safe state collection, multi-window testing. |
| `wear` | Medium-High | New `:wear` module, wearable scaffold patterns, strict import separation. |
| `auto` | Medium | Car app service/session/template wiring, manifest metadata, distraction rules. |
| `tv` | Medium-High | New `:tv` module, D-pad navigation, focus management, TV material library. |
| `density` | Low | Resource audit and asset policy enforcement. |

## Recommended Rollout Order

1. `phone` baseline hardening
2. `tablet`
3. `resizable` (foldable + multi-window — add when foldable or desktop multi-window signal exists)
4. `wear`, `auto`, or `tv` (only when product scope requires — each is its own module)
5. `density` pass across all touched modules

## Readiness Checklist Before `add_form_factor`

- [ ] Product signal documented (usage or roadmap)
- [ ] Module boundaries known (`:app`, `:wear`, `:auto`)
- [ ] Dependency plan reviewed (`references/dependencies.md`)
- [ ] Acceptance criteria for the new form factor defined
- [ ] Validation command selected (`scripts/validate_fixes.sh` or full audit)
