# Gradle Dependencies by Form Factor

Copy the relevant sections into your project. Version catalog entries go in `gradle/libs.versions.toml`; dependency declarations go in `app/build.gradle.kts`.

See also: `gradle/libs.versions.toml.snippet` and `gradle/build.gradle.snippet` for paste-ready blocks.

---

## Core (All Projects)

```toml
# gradle/libs.versions.toml [versions]
kotlin = "2.3.10"
agp = "8.9.1"
composeBom = "2026.04.01"

# [libraries]
compose-bom = { group = "androidx.compose", name = "compose-bom", version.ref = "composeBom" }
compose-ui = { group = "androidx.compose.ui", name = "ui" }
compose-ui-tooling-preview = { group = "androidx.compose.ui", name = "ui-tooling-preview" }
compose-material3 = { group = "androidx.compose.material3", name = "material3" }
compose-activity = { group = "androidx.activity", name = "activity-compose", version = "1.10.1" }
```

```kotlin
// app/build.gradle.kts dependencies
implementation(platform(libs.compose.bom))
implementation(libs.compose.ui)
implementation(libs.compose.material3)
implementation(libs.compose.activity)
debugImplementation(libs.compose.ui.tooling.preview)
```

---

## Adaptive / Large Screen

Requires `@file:OptIn(ExperimentalMaterial3AdaptiveApi::class)` in every file that uses these APIs.

```toml
# [versions]
material3Adaptive = "1.2.0"

# [libraries]
adaptive = { group = "androidx.compose.material3.adaptive", name = "adaptive", version.ref = "material3Adaptive" }
adaptive-layout = { group = "androidx.compose.material3.adaptive", name = "adaptive-layout", version.ref = "material3Adaptive" }
adaptive-navigation = { group = "androidx.compose.material3.adaptive", name = "adaptive-navigation", version.ref = "material3Adaptive" }
material3-nav-suite = { group = "androidx.compose.material3", name = "material3-adaptive-navigation-suite" }
```

```kotlin
// app/build.gradle.kts dependencies
// === FORM FACTOR: Large Screen / Tablets ===
implementation(libs.adaptive)
implementation(libs.adaptive.layout)
implementation(libs.adaptive.navigation)
implementation(libs.material3.nav.suite)
```

> The `adaptive` group artifacts are still annotated `@ExperimentalMaterial3AdaptiveApi`. Add `@file:OptIn(ExperimentalMaterial3AdaptiveApi::class)` at the top of each file using `ListDetailPaneScaffold`, `SupportingPaneScaffold`, `NavigationSuiteScaffold`, or `AdaptiveNavigationSuite`.

---

## Foldable

```toml
# [versions]
windowManager = "1.5.1"
lifecycleRuntimeCompose = "2.9.0"

# [libraries]
window-manager = { group = "androidx.window", name = "window", version.ref = "windowManager" }
window-testing = { group = "androidx.window", name = "window-testing", version.ref = "windowManager" }
lifecycle-runtime-compose = { group = "androidx.lifecycle", name = "lifecycle-runtime-compose", version.ref = "lifecycleRuntimeCompose" }
```

```kotlin
// app/build.gradle.kts dependencies
// === FORM FACTOR: Foldable ===
implementation(libs.window.manager)
implementation(libs.lifecycle.runtime.compose)
debugImplementation(libs.window.testing)
```

---

## Wear OS

**CRITICAL:** These dependencies must be in a **separate `:wear` Gradle module**. Never add them to the `:app` (mobile) module. The two `MaterialTheme` implementations are incompatible and will cause runtime crashes or invisible UI if mixed.

```toml
# [versions]
wearCompose = "1.6.1"

# [libraries]
wear-compose-material3 = { group = "androidx.wear.compose", name = "compose-material3", version.ref = "wearCompose" }
wear-compose-foundation = { group = "androidx.wear.compose", name = "compose-foundation", version.ref = "wearCompose" }
wear-compose-navigation = { group = "androidx.wear.compose", name = "compose-navigation", version.ref = "wearCompose" }
wear-compose-tooling = { group = "androidx.wear.compose", name = "compose-ui-tooling", version.ref = "wearCompose" }
```

```kotlin
// wear/build.gradle.kts dependencies
// === FORM FACTOR: Wear OS (separate :wear module ONLY) ===
implementation(libs.wear.compose.material3)
implementation(libs.wear.compose.foundation)
implementation(libs.wear.compose.navigation)
debugImplementation(libs.wear.compose.tooling)
```

> The `:wear` module also needs `compileSdk = 36` (or the latest Wear SDK level), `wearApp project(':wear')` in the `:app` module, and `apply plugin: 'com.android.application'` (not library) to generate a standalone APK for the watch.

---

## Android Auto / Automotive OS

**CRITICAL:** Choose `app-projected` OR `app-automotive` — never both.

| Artifact | When to use |
|---|---|
| `car-app` (base) | Shared code between projected and automotive |
| `car-app-projected` | Android Auto (phone-projected to car head unit). Testing via DHU (Desktop Head Unit). |
| `car-app-automotive` | Android Automotive OS (runs natively on the car's hardware, no phone needed). Different store: Automotive App Store. |

```toml
# [versions]
carApp = "1.7.0"

# [libraries]
car-app = { group = "androidx.car.app", name = "app", version.ref = "carApp" }
car-app-projected = { group = "androidx.car.app", name = "app-projected", version.ref = "carApp" }
car-app-automotive = { group = "androidx.car.app", name = "app-automotive", version.ref = "carApp" }
car-app-testing = { group = "androidx.car.app", name = "app-testing", version.ref = "carApp" }
```

```kotlin
// For Android Auto (phone-projected):
// === FORM FACTOR: Android Auto ===
implementation(libs.car.app)
implementation(libs.car.app.projected)
androidTestImplementation(libs.car.app.testing)

// For Android Automotive OS (replace projected with automotive):
// implementation(libs.car.app.automotive)
```

> The Auto module should be a separate `com.android.application` or `com.android.library` module. It registers a `<service>` in its own `AndroidManifest.xml`. Mixing it into the phone `:app` module adds car-specific permissions to the phone APK.
