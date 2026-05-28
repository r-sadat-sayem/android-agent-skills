# Form Factor Decision Guide

Use this guide before `add_form_factor` so decisions are based on product signals, not guesswork.

## Decision Matrix

| Signal | Recommendation | ROI | Complexity | Why |
|---|---|---|---|---|
| Tablet usage >= 30% DAU or PM target includes productivity/education dashboards | Add `large-screen` now | High | Medium | Two-pane/adaptive nav directly impacts task completion and retention on wide screens. |
| Foldable usage >= 5-10% DAU OR premium/prosumer segment expected to over-index on foldables | Add `foldable` after large-screen baseline | Medium-High | Medium | Posture-aware layouts improve continuity and reduce awkward hinge splits. |
| Primary use case is glanceable wearable interactions (fitness, notifications, quick actions) | Add `wear` with separate `:wear` module | Medium-High | Medium-High | Watch flows are distinct; module isolation is mandatory to avoid theme/runtime conflicts. |
| Primary use case is in-car or automotive companion workflows | Add `auto` with `CarAppService` template model | High (for target users) | Medium | Android Auto requires template APIs; cannot be approximated by mobile Compose UI. |
| Media-heavy or image-heavy app with bitmap assets and mixed device classes | Add `density` pass early | Medium | Low | Density hygiene prevents blur/memory waste and improves perceived quality. |
| Team is small and only phone traffic matters (<10% non-phone DAU) | Keep `phone` only for now; defer others | Low immediate ROI for expansion | Low | Avoid broad scope before product demand appears. |

## Prioritization Heuristics

1. Always stabilize `phone` first.
2. If tablet signal is strong, prioritize `large-screen` before `foldable`.
3. Treat `wear` and `auto` as separate product surfaces, not just layout variants.
4. Run `density` checks whenever bitmap-heavy surfaces are present.

## Complexity Bands

| Form Factor | Complexity | Typical Work |
|---|---|---|
| `phone` | Low | Navigation/scroll/overflow hardening. |
| `large-screen` | Medium | Pane scaffold integration, adaptive navigation, opt-in/API cleanup. |
| `foldable` | Medium | Posture detection, hinge-aware layouts, lifecycle-safe state collection. |
| `wear` | Medium-High | New module setup, wearable scaffold patterns, strict import separation. |
| `auto` | Medium | Car app service/session/template wiring, manifest metadata, distraction rules. |
| `density` | Low | Resource audit and asset policy enforcement. |

## Recommended Rollout Order

1. `phone` baseline hardening
2. `large-screen`
3. `foldable` (if signal exists)
4. `wear` or `auto` (only when product scope requires)
5. `density` pass across all touched modules

## Readiness Checklist Before `add_form_factor`

- [ ] Product signal documented (usage or roadmap)
- [ ] Module boundaries known (`:app`, `:wear`, `:auto`)
- [ ] Dependency plan reviewed (`references/dependencies.md`)
- [ ] Acceptance criteria for the new form factor defined
- [ ] Validation command selected (`scripts/validate_fixes.sh` or full audit)
