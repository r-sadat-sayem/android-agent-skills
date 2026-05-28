// AFTER: Fully adaptive screen — all issues from example-input.kt resolved
//
// Changes applied:
//   1. calculateWindowSizeClass()  → currentWindowAdaptiveInfo()
//   2. BottomNavigation            → NavigationSuiteScaffold (auto bar/rail/drawer)
//   3. WindowWidthSizeClass ==     → isWidthAtLeastBreakpoint()
//   4. @file:OptIn added           (ExperimentalMaterial3AdaptiveApi)
//   5. Text()                      → overflow + maxLines added
//   6. Column                      → .verticalScroll(rememberScrollState()) added

@file:OptIn(ExperimentalMaterial3AdaptiveApi::class)

package com.example.app.ui

import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.rememberScrollState
import androidx.compose.foundation.verticalScroll
import androidx.compose.material3.Icon
import androidx.compose.material3.Text
import androidx.compose.material3.adaptive.ExperimentalMaterial3AdaptiveApi
import androidx.compose.material3.adaptive.currentWindowAdaptiveInfo
import androidx.compose.material3.adaptive.navigationsuite.NavigationSuiteScaffold
import androidx.compose.material3.windowsizeclass.WIDTH_DP_EXPANDED_LOWER_BOUND
import androidx.compose.material3.windowsizeclass.isWidthAtLeastBreakpoint
import androidx.compose.runtime.Composable
import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.saveable.rememberSaveable
import androidx.compose.runtime.setValue
import androidx.compose.ui.Modifier
import androidx.compose.ui.text.style.TextOverflow
import androidx.compose.ui.tooling.preview.Preview

@Composable
fun MainScreen() {
    // Fix 1 + 3: currentWindowAdaptiveInfo() called once at root; use breakpoint method
    val adaptiveInfo = currentWindowAdaptiveInfo()
    val windowSizeClass = adaptiveInfo.windowSizeClass
    val isExpanded = windowSizeClass.isWidthAtLeastBreakpoint(WIDTH_DP_EXPANDED_LOWER_BOUND)

    var selectedTab by rememberSaveable { mutableStateOf(0) }

    // Fix 2: NavigationSuiteScaffold automatically switches
    //   Compact  → BottomNavigationBar
    //   Medium   → NavigationRail
    //   Expanded → PermanentNavigationDrawer
    NavigationSuiteScaffold(
        navigationSuiteItems = {
            item(
                selected = selectedTab == 0,
                onClick = { selectedTab = 0 },
                icon = { Icon(TODO(), contentDescription = "Home") },
                label = { Text("Home") },
            )
            item(
                selected = selectedTab == 1,
                onClick = { selectedTab = 1 },
                icon = { Icon(TODO(), contentDescription = "Search") },
                label = { Text("Search") },
            )
        }
    ) {
        // Fix 5: overflow + maxLines prevent clipping on compact screens
        Text(
            text = "Welcome back, User with a very long display name",
            maxLines = 1,
            overflow = TextOverflow.Ellipsis,
        )

        // Fix 6: .verticalScroll added so column is not clipped on compact heights
        Column(modifier = Modifier.verticalScroll(rememberScrollState())) {
            Text("Item 1")
            Text("Item 2")
            Text("Item 3")
            Text("Item 4")
            Text("Item 5")
            Text("Item 6")
        }
    }
}

@Preview(name = "Compact — 360dp", widthDp = 360, heightDp = 800)
@Composable
private fun MainScreenCompactPreview() {
    MainScreen()
}

@Preview(name = "Medium — 700dp", widthDp = 700, heightDp = 1000)
@Composable
private fun MainScreenMediumPreview() {
    MainScreen()
}

@Preview(name = "Expanded — 1200dp", widthDp = 1200, heightDp = 900)
@Composable
private fun MainScreenExpandedPreview() {
    MainScreen()
}
