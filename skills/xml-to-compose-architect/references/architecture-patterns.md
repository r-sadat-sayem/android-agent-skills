# Architecture Patterns for XML -> Compose Migration

## Pattern A: Stateful Route + Stateless Content (Recommended Default)

### Shape
1. `FeatureRoute` collects state from ViewModel and emits events.
2. `FeatureContent` renders UI from `UiState` and callbacks.

### Pros
1. Clean state hoisting.
2. Easy previews for `FeatureContent`.
3. Simple testability for rendering and interaction.

### Cons
1. Requires clear contracts (`UiState`, callbacks).

## Pattern B: UDF/MVI Style

### Shape
1. `UiState` + `UiAction` + reducer/event processing.
2. One stream of actions and one render model.

### Pros
1. Predictable behavior for complex screens.
2. Strong traceability for events/state transitions.

### Cons
1. More boilerplate.
2. Higher setup cost for simple screens.

## Pattern C: Local State + Callback Bridge

### Shape
1. Screen stores some local remembered state.
2. Pushes major actions upward.

### Pros
1. Fast to implement for simple screens.
2. Lower ceremony.

### Cons
1. Can drift into mixed concerns.
2. Harder to scale consistently.

## Selection Guidance

1. Simple static-ish screens: Pattern A.
2. Complex business workflows/events: Pattern B.
3. Temporary migration stepping stone: Pattern C, then refactor to A/B.

