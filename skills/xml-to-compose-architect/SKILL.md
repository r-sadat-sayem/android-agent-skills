# XML to Compose Architect Skill

This skill is for migrating legacy Android XML UI to Jetpack Compose with strict guardrails.
It is architecture-first, question-first, and performance-aware.

## Skill Contract

When this skill is active, the agent MUST follow all phases in order.
The agent MUST NOT skip directly to code unless the user explicitly says "skip questions and implement now".

## Required Workflow

### Phase 0: Intake and Clarifying Questions (MUST)

Ask clarifying questions before implementation. Ask only what changes architecture or behavior.

Minimum required topics:

1. Screen purpose and primary user flows
2. State ownership (ViewModel vs screen vs child composable)
3. Navigation and side effects (snackbar, toast, one-off events)
4. Form behavior, validation, and error handling strategy
5. UI states required for preview (loading, success, empty, error)
6. Performance-sensitive areas (lists, animations, frequently changing state)
7. Existing design system/theme constraints


If key answers are missing, stop at analysis/recommendation and do not generate final implementation code.

### Phase 1: Architecture Recommendation (MUST)

Provide at least 2 viable options and 1 recommendation.

For each option:

1. Pattern (for example: Stateless Screen + State Holder, UDF/MVI, Presenter-like)
2. Pros
3. Cons
4. Why/when to choose

Recommendation format:

1. Recommended pattern
2. Why this fits this screen
3. Trade-offs accepted
4. File/module boundaries

### Phase 2: Migration Plan (MUST)

Before coding, provide:

1. XML-to-Compose component mapping summary
2. State model design (`UiState`, `UiAction`, `UiEvent` if applicable)
3. Composable tree outline
4. Preview matrix plan
5. Performance risk list and mitigation plan

### Phase 3: Implementation Rules (STRICT)

#### UI design rules
1. Prefer small, modular composables.
2. Default to stateless composables; hoist state to parent/state holder.
3. Every reusable composable accepts `modifier: Modifier = Modifier`.
4. Keep business logic out of leaf composables.
5. Split screen container (stateful) and content (stateless).

#### Performance and recomposition rules
Follow: https://developer.android.com/develop/ui/compose/performance/bestpractices

1. Use `remember` for expensive calculations done in composition.
2. Provide stable keys in lazy lists (`items(..., key = ...)`).
3. Use `derivedStateOf` for computed state driven by frequently changing inputs.
4. Defer state reads as long as possible.
5. Prefer lambda-based modifiers where appropriate for frequent changes.
6. Avoid backwards writes (never write state after it has been read in the same composition pass).

#### API and state-hoisting rules
1. Stateless composables receive data + callbacks.
2. No direct ViewModel access inside deeply nested UI nodes.
3. Event callbacks must be explicit (`onClick`, `onValueChange`, `onRetry`, etc.).
4. One-off effects should be modeled intentionally (event stream/effect handler).

### Phase 4: Preview Requirements (MUST)

Each significant composable must include `@Preview` coverage for:

1. Light mode
2. Dark mode
3. Large font scale (if text-dense)
4. At least one non-happy-path state (empty or error)
5. Optional: loading state for async-heavy screens

### Phase 5: Documentation Output (MUST)

Every implementation response must include:

1. Architecture decision summary
2. State-hoisting explanation
3. Recomposition/performance notes
4. Preview coverage summary
5. Known trade-offs and follow-up recommendations

## Hard Guardrails

The agent MUST:

1. Ask clarifying questions before implementation.
2. Recommend a pattern before coding.
3. Keep UI modular and primarily stateless.
4. Include previews for relevant states.
5. Call out recomposition/performance decisions explicitly.

The agent MUST NOT:

1. Dump one giant composable for the whole screen.
2. Mix heavy business logic into UI leaf nodes.
3. Ignore lazy keys in mutable/reordered lists.
4. Write to state in composition in a way that risks backwards writes.
5. Claim performance optimization without explaining why.

## Output Template Contract

Use `templates/analysis-report-template.md` for analysis output.
Use `checklists/pre-implementation-checklist.md` before coding.
Use `checklists/post-implementation-checklist.md` before finalizing.

## Directory Usage

1. `references/`: core mapping + architecture + performance knowledge
2. `templates/`: reusable output and code templates
3. `assets/`: examples and optional starter snippets
4. `scripts/`: optional automation and validation tooling

