// BEFORE: Non-adaptive phone screen
// Issues this file demonstrates:
//   1. calculateWindowSizeClass() — deprecated API
//   2. BottomNavigation — does not adapt to large screens
//   3. WindowWidthSizeClass enum equality — breaks with L/XL classes
//   4. screenOrientation lock in manifest (see example-manifest-input.xml)
//   5. Text() without overflow/maxLines
//   6. Column with many children and no .verticalScroll

package com.example.app.ui

import androidx.activity.ComponentActivity
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.padding
import androidx.compose.material3.BottomNavigation
import androidx.compose.material3.BottomNavigationItem
import androidx.compose.material3.Icon
import androidx.compose.material3.Scaffold
import androidx.compose.material3.Text
import androidx.compose.material3.windowsizeclass.WindowWidthSizeClass
import androidx.compose.material3.windowsizeclass.calculateWindowSizeClass
import androidx.compose.runtime.Composable
import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.saveable.rememberSaveable
import androidx.compose.runtime.setValue
import androidx.compose.ui.Modifier
import androidx.compose.ui.tooling.preview.Preview

@Composable
fun MainScreen(activity: ComponentActivity) {
    // Issue 1: deprecated API — use currentWindowAdaptiveInfo() instead
    val windowSizeClass = calculateWindowSizeClass(activity)
    var selectedTab by rememberSaveable { mutableStateOf(0) }

    Scaffold(
        bottomBar = {
            // Issue 2: BottomNavigation never adapts — shows bottom bar on tablets too
            BottomNavigation {
                BottomNavigationItem(
                    selected = selectedTab == 0,
                    onClick = { selectedTab = 0 },
                    icon = { Icon(TODO(), contentDescription = "Home") },
                    label = { Text("Home") }
                )
                BottomNavigationItem(
                    selected = selectedTab == 1,
                    onClick = { selectedTab = 1 },
                    icon = { Icon(TODO(), contentDescription = "Search") },
                    label = { Text("Search") }
                )
            }
        }
    ) { paddingValues ->
        // Issue 3: enum equality — breaks when Large/ExtraLarge classes are added
        val isExpanded = windowSizeClass.widthSizeClass == WindowWidthSizeClass.Expanded

        // Issue 5: Text() without overflow or maxLines — clips on compact screens
        Text(text = "Welcome back, User with a very long display name")

        // Issue 6: Column with 6 children and no .verticalScroll
        Column(modifier = Modifier.padding(paddingValues)) {
            Text("Item 1")
            Text("Item 2")
            Text("Item 3")
            Text("Item 4")
            Text("Item 5")
            Text("Item 6")
        }
    }
}
