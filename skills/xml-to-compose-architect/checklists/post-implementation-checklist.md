# Post-Implementation Checklist

- [ ] Composables are modular and primarily stateless.
- [ ] Leaf composables do not hold business logic.
- [ ] All reusable composables accept `modifier: Modifier = Modifier`.
- [ ] Previews include light, dark, and at least one non-happy-path state.
- [ ] Lazy lists use stable keys where ordering can change.
- [ ] Expensive calculations are not repeated per recomposition.
- [ ] No backwards-write anti-pattern exists.
- [ ] Final output includes architecture + state hoisting + recomposition notes.

