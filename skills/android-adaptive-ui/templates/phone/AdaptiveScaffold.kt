@file:OptIn(ExperimentalMaterial3AdaptiveApi::class)

package com.example.app.ui

import androidx.compose.material3.Icon
import androidx.compose.material3.Text
import androidx.compose.material3.adaptive.ExperimentalMaterial3AdaptiveApi
import androidx.compose.material3.adaptive.currentWindowAdaptiveInfo
import androidx.compose.material3.adaptive.navigationsuite.NavigationSuiteScaffold
import androidx.compose.material3.adaptive.navigationsuite.NavigationSuiteScaffoldDefaults
import androidx.compose.material3.adaptive.navigationsuite.NavigationSuiteType
import androidx.compose.material3.windowsizeclass.WIDTH_DP_EXPANDED_LOWER_BOUND
import androidx.compose.material3.windowsizeclass.isWidthAtLeastBreakpoint
import androidx.compose.runtime.Composable
import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.saveable.rememberSaveable
import androidx.compose.runtime.setValue
import androidx.compose.ui.graphics.vector.ImageVector
import androidx.compose.ui.tooling.preview.Preview
import androidx.compose.ui.unit.dp

// ─── Destinations ────────────────────────────────────────────────────────────

sealed interface AppDestination {
    val label: String
    val icon: ImageVector

    data object Home : AppDestination {
        override val label = "Home"
        override val icon get() = TODO("Replace with Icons.Default.Home")
    }

    data object Search : AppDestination {
        override val label = "Search"
        override val icon get() = TODO("Replace with Icons.Default.Search")
    }

    data object Profile : AppDestination {
        override val label = "Profile"
        override val icon get() = TODO("Replace with Icons.Default.Person")
    }
}

private val ALL_DESTINATIONS: List<AppDestination> = listOf(
    AppDestination.Home,
    AppDestination.Search,
    AppDestination.Profile,
)

// ─── Root scaffold ────────────────────────────────────────────────────────────

@Composable
fun AdaptiveApp() {
    // Call currentWindowAdaptiveInfo() ONCE at the composition root.
    // Pass windowSizeClass down as a plain parameter — do not re-call deep in the tree.
    val adaptiveInfo = currentWindowAdaptiveInfo()
    val windowSizeClass = adaptiveInfo.windowSizeClass

    var currentDestination by rememberSaveable { mutableStateOf<AppDestination>(AppDestination.Home) }

    // Derive the navigation layout from the window size.
    // NavigationSuiteScaffoldDefaults.calculateFromAdaptiveInfo() returns:
    //   Compact  → NavigationBar  (bottom)
    //   Medium   → NavigationRail (side)
    //   Expanded → PermanentDrawer (always visible side)
    // Override layoutType here if your product requires a custom mapping.
    val navType = NavigationSuiteScaffoldDefaults.calculateFromAdaptiveInfo(adaptiveInfo)

    // Example: force NavigationRail on Expanded too (e.g., for a chat app)
    // val navType = if (windowSizeClass.isWidthAtLeastBreakpoint(WIDTH_DP_EXPANDED_LOWER_BOUND)) {
    //     NavigationSuiteType.NavigationRail
    // } else {
    //     NavigationSuiteScaffoldDefaults.calculateFromAdaptiveInfo(adaptiveInfo)
    // }

    NavigationSuiteScaffold(
        layoutType = navType,
        navigationSuiteItems = {
            ALL_DESTINATIONS.forEach { destination ->
                item(
                    selected = currentDestination == destination,
                    onClick = { currentDestination = destination },
                    icon = { Icon(destination.icon, contentDescription = destination.label) },
                    label = { Text(destination.label) },
                )
            }
        },
    ) {
        // TODO: Replace with your NavHost or destination composable
        when (currentDestination) {
            AppDestination.Home -> HomeScreen(windowSizeClass)
            AppDestination.Search -> SearchScreen(windowSizeClass)
            AppDestination.Profile -> ProfileScreen(windowSizeClass)
        }
    }
}

// ─── Stub screens (replace with your actual screens) ─────────────────────────

@Composable
fun HomeScreen(windowSizeClass: androidx.compose.material3.windowsizeclass.WindowSizeClass) {
    // TODO: implement
}

@Composable
fun SearchScreen(windowSizeClass: androidx.compose.material3.windowsizeclass.WindowSizeClass) {
    // TODO: implement
}

@Composable
fun ProfileScreen(windowSizeClass: androidx.compose.material3.windowsizeclass.WindowSizeClass) {
    // TODO: implement
}

// ─── Previews ─────────────────────────────────────────────────────────────────

@Preview(name = "Compact phone — 360dp", widthDp = 360, heightDp = 800)
@Composable
private fun AdaptiveAppCompactPreview() {
    AdaptiveApp()
}

@Preview(name = "Medium tablet — 700dp", widthDp = 700, heightDp = 1000)
@Composable
private fun AdaptiveAppMediumPreview() {
    AdaptiveApp()
}

@Preview(name = "Expanded tablet — 1200dp", widthDp = 1200, heightDp = 900)
@Composable
private fun AdaptiveAppExpandedPreview() {
    AdaptiveApp()
}
