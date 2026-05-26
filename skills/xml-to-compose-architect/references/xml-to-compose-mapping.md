# XML to Compose Mapping Reference

## Common Containers

| XML | Compose |
|---|---|
| `LinearLayout` (vertical) | `Column` |
| `LinearLayout` (horizontal) | `Row` |
| `FrameLayout` | `Box` |
| `ScrollView` | `Column` + `verticalScroll(...)` |
| `RecyclerView` | `LazyColumn` / `LazyRow` |
| `ConstraintLayout` | Compose `ConstraintLayout` or simpler `Row`/`Column`/`Box` |

## Common Widgets

| XML | Compose |
|---|---|
| `TextView` | `Text` |
| `EditText` | `TextField` / `OutlinedTextField` |
| `Button` | `Button` |
| `ImageView` | `Image` / `AsyncImage` |
| `ProgressBar` | `CircularProgressIndicator` / `LinearProgressIndicator` |
| `CardView` | `Card` |
| `Switch` | `Switch` |
| `CheckBox` | `Checkbox` |

## Attribute Patterns

1. `match_parent` -> `fillMaxWidth()` / `fillMaxHeight()`
2. `wrap_content` -> default size behavior (often no explicit modifier needed)
3. XML margins -> often `Spacer` or parent-level arrangement/padding decisions
4. IDs -> usually replaced by explicit state/events and composition structure

## Stateful vs Stateless Target

1. Prefer `ScreenRoute` (stateful + ViewModel integration) and `ScreenContent` (stateless UI).
2. Stateless composables receive:
   - immutable-ish UI data
   - callbacks for user actions
   - `modifier`
3. Keep side-effect handling out of pure visual components.

