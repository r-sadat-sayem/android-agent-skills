# Window Size Class Breakpoints & Folding Posture Reference

## Width Breakpoints (5 classes)

| Class | Lower Bound (dp) | Typical Devices |
|---|---|---|
| Compact | 0 | Phones in portrait, wearables |
| Medium | 600 | Small tablets, phones in landscape, foldables (outer screen) |
| Expanded | 840 | Tablets, foldables (inner screen open), large landscape phones |
| Large | 1200 | Large tablets, Chromebooks, desktop windows |
| ExtraLarge | 1600 | External displays, very large tablets |

> **Note:** Large and ExtraLarge require opt-in. See "L/XL Opt-In" below.

## Height Breakpoints (3 classes)

| Class | Lower Bound (dp) | Typical Devices |
|---|---|---|
| Compact | 0 | Phones in landscape |
| Medium | 480 | Most tablets, phones in portrait |
| Expanded | 900 | Large tablets, foldables |

---

## Correct API Usage

### Standard (Compact / Medium / Expanded only)
```kotlin
val adaptiveInfo = currentWindowAdaptiveInfo()
val windowSizeClass = adaptiveInfo.windowSizeClass

val isExpanded = windowSizeClass.isWidthAtLeastBreakpoint(WIDTH_DP_EXPANDED_LOWER_BOUND)
val isMedium = windowSizeClass.isWidthAtLeastBreakpoint(WIDTH_DP_MEDIUM_LOWER_BOUND)
    && !windowSizeClass.isWidthAtLeastBreakpoint(WIDTH_DP_EXPANDED_LOWER_BOUND)
```

### With Large / ExtraLarge Opt-In
```kotlin
// Add to file: @file:OptIn(ExperimentalMaterial3WindowSizeClassApi::class)
val adaptiveInfo = currentWindowAdaptiveInfo(supportLargeAndXLargeWidth = true)
val isLarge = adaptiveInfo.windowSizeClass.isWidthAtLeastBreakpoint(WIDTH_DP_LARGE_LOWER_BOUND)
val isXL = adaptiveInfo.windowSizeClass.isWidthAtLeastBreakpoint(WIDTH_DP_EXTRA_LARGE_LOWER_BOUND)
```

---

## Breakpoint Method vs. Enum Equality (Why the Method Wins)

| Old approach (DO NOT USE) | Current approach |
|---|---|
| `windowSizeClass.widthSizeClass == WindowWidthSizeClass.Expanded` | `windowSizeClass.isWidthAtLeastBreakpoint(WIDTH_DP_EXPANDED_LOWER_BOUND)` |
| Breaks when L/XL classes are added — `Expanded` no longer means "largest" | Additive: adding L/XL doesn't break existing `isWidthAtLeastBreakpoint(EXPANDED)` checks |
| Forces exhaustive `when` on a sealed class that may gain new members | Just a boolean; no exhaustive handling needed |

The method approach is forward-compatible. Enum equality is frozen at 3 classes.

---

## Navigation Component Decision Table

| Width Class | `NavigationSuiteType` | Component Rendered |
|---|---|---|
| Compact | `NavigationBar` | Bottom navigation bar |
| Medium | `NavigationRail` | Side rail (icon + optional label) |
| Expanded | `PermanentNavigationDrawer` | Always-visible side drawer |
| Large | `PermanentNavigationDrawer` | Always-visible side drawer (wider) |
| ExtraLarge | `PermanentNavigationDrawer` | Always-visible side drawer (widest) |

`AdaptiveNavigationSuite` and `NavigationSuiteScaffold` handle this automatically. Only override `layoutType` when you have a product reason to deviate.

---

## Folding Posture Matrix

Maps `FoldingFeature` properties to the `DevicePosture` sealed class defined in `templates/foldable/PostureDetector.kt`.

| `FoldingFeature.state` | `FoldingFeature.orientation` | `isSeparating` | Posture | Layout Strategy |
|---|---|---|---|---|
| `STATE_HALF_OPENED` | `HORIZONTAL` | any | `TableTopPosture` | Top half = primary, bottom half = secondary; `Spacer` for hinge |
| `STATE_HALF_OPENED` | `VERTICAL` | any | `BookPosture` | Left half = primary, right half = secondary; `Spacer` for hinge |
| `STATE_FLAT` | any | `true` | `SeparatingPosture` | Treat as two screens; `Spacer` for hinge gap |
| `STATE_FLAT` | any | `false` | `NormalPosture` | Single-pane standard layout |
| `TYPE_FOLD` only | — | — | — | `TYPE_HINGE` separates screens; `TYPE_FOLD` is a crease only |

**Important:** `SeparatingPosture` (`STATE_FLAT + isSeparating=true`) is a dual-screen device (e.g., Surface Duo) fully opened flat. Do not confuse with `BookPosture` (`STATE_HALF_OPENED`), which is a single foldable screen folded partially.

---

## `currentWindowAdaptiveInfo()` vs. `calculateWindowSizeClass()` Migration

```kotlin
// DEPRECATED — do not use
val windowSizeClass = calculateWindowSizeClass(activity)

// CURRENT — call once at composition root, pass windowSizeClass down as a parameter
val windowSizeClass = currentWindowAdaptiveInfo().windowSizeClass
```

`currentWindowAdaptiveInfo()` is a `@Composable` function. It must be called inside a composable scope. It also returns `WindowAdaptiveInfo` which contains both `windowSizeClass` and (when using Jetpack WindowManager) posture info.
