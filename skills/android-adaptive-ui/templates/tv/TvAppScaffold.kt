package com.example.app.tv.ui

import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Box
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.PaddingValues
import androidx.compose.foundation.layout.Row
import androidx.compose.foundation.layout.fillMaxHeight
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.layout.width
import androidx.compose.foundation.selection.selectableGroup
import androidx.compose.runtime.Composable
import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableIntStateOf
import androidx.compose.runtime.remember
import androidx.compose.runtime.setValue
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.unit.dp
import androidx.tv.foundation.lazy.list.TvLazyColumn
import androidx.tv.foundation.lazy.list.TvLazyRow
import androidx.tv.foundation.lazy.list.items
import androidx.tv.material3.Card
import androidx.tv.material3.ExperimentalTvMaterial3Api
import androidx.tv.material3.MaterialTheme
import androidx.tv.material3.NavigationDrawer
import androidx.tv.material3.NavigationDrawerItem
import androidx.tv.material3.Surface
import androidx.tv.material3.Text

// ─── CRITICAL: TV module rules ────────────────────────────────────────────────
// 1. This file lives in a SEPARATE :tv Gradle module (com.android.application).
// 2. Only import androidx.tv.* — never import androidx.compose.material3.*
// 3. No touch input — every interactive element must be reachable via D-pad.
// 4. Surface {} wrapper is REQUIRED at the root — TV Material3 needs it for
//    focus ripple and background to work correctly.
// 5. Cards and items MUST have explicit focused/selected state styling.
// ─────────────────────────────────────────────────────────────────────────────

@OptIn(ExperimentalTvMaterial3Api::class)
@Composable
fun TvApp() {
    // Surface is mandatory as the root — never omit it on TV
    Surface(modifier = Modifier.fillMaxSize()) {
        TvAppLayout()
    }
}

// ─── Navigation + content layout ─────────────────────────────────────────────

sealed interface TvDestination {
    val label: String

    data object Home    : TvDestination { override val label = "Home"    }
    data object Movies  : TvDestination { override val label = "Movies"  }
    data object Series  : TvDestination { override val label = "Series"  }
    data object Search  : TvDestination { override val label = "Search"  }
    data object Settings: TvDestination { override val label = "Settings"}
}

private val ALL_DESTINATIONS: List<TvDestination> = listOf(
    TvDestination.Home,
    TvDestination.Movies,
    TvDestination.Series,
    TvDestination.Search,
    TvDestination.Settings,
)

@OptIn(ExperimentalTvMaterial3Api::class)
@Composable
private fun TvAppLayout() {
    var selectedIndex by remember { mutableIntStateOf(0) }

    Row(modifier = Modifier.fillMaxSize()) {
        // NavigationDrawer auto-collapses to icons-only when not focused —
        // standard TV sidebar pattern (D-pad left from content to open it).
        NavigationDrawer(
            drawerContent = {
                Column(
                    modifier = Modifier
                        .fillMaxHeight()
                        .padding(vertical = 16.dp)
                        .selectableGroup(),
                    verticalArrangement = Arrangement.spacedBy(4.dp),
                ) {
                    ALL_DESTINATIONS.forEachIndexed { index, dest ->
                        NavigationDrawerItem(
                            selected  = selectedIndex == index,
                            onClick   = { selectedIndex = index },
                            content   = { Text(dest.label) },
                        )
                    }
                }
            }
        ) {
            // Main content area — receives focus first on launch
            Box(modifier = Modifier.fillMaxSize()) {
                when (ALL_DESTINATIONS[selectedIndex]) {
                    TvDestination.Home     -> TvHomeScreen()
                    TvDestination.Movies   -> TvBrowseScreen(title = "Movies")
                    TvDestination.Series   -> TvBrowseScreen(title = "Series")
                    TvDestination.Search   -> TvSearchScreen()
                    TvDestination.Settings -> TvSettingsScreen()
                }
            }
        }
    }
}

// ─── Home screen — carousel + content rows ────────────────────────────────────

@OptIn(ExperimentalTvMaterial3Api::class)
@Composable
fun TvHomeScreen() {
    TvLazyColumn(
        modifier = Modifier.fillMaxSize(),
        contentPadding = PaddingValues(vertical = 32.dp),
        verticalArrangement = Arrangement.spacedBy(24.dp),
    ) {
        item {
            // Replace with androidx.tv.material3.Carousel for auto-advancing hero
            TvHeroBanner(
                modifier = Modifier
                    .fillMaxWidth()
                    .padding(horizontal = 48.dp)
            )
        }
        item { TvContentRow(title = "Continue Watching") }
        item { TvContentRow(title = "Recommended for You") }
        item { TvContentRow(title = "New Releases") }
        item { TvContentRow(title = "Top Picks") }
    }
}

// ─── Generic content row ──────────────────────────────────────────────────────

@OptIn(ExperimentalTvMaterial3Api::class)
@Composable
fun TvContentRow(
    title: String,
    modifier: Modifier = Modifier,
) {
    Column(modifier = modifier.padding(horizontal = 48.dp)) {
        Text(
            text  = title,
            style = MaterialTheme.typography.titleMedium,
            modifier = Modifier.padding(bottom = 12.dp),
        )
        // TvLazyRow is the D-pad-navigable horizontal list for TV.
        // Each item must be focusable — Card handles this automatically.
        TvLazyRow(
            horizontalArrangement = Arrangement.spacedBy(12.dp),
            contentPadding = PaddingValues(end = 48.dp),
        ) {
            items(count = 10, key = { it }) { idx ->
                TvContentCard(
                    label = "Item $idx",
                    modifier = Modifier.width(200.dp),
                )
            }
        }
    }
}

// ─── Content card — focused state is handled by Card automatically ────────────

@OptIn(ExperimentalTvMaterial3Api::class)
@Composable
fun TvContentCard(
    label: String,
    modifier: Modifier = Modifier,
) {
    Card(
        modifier = modifier,
        onClick = { /* handle selection */ },
    ) {
        Box(
            modifier = Modifier
                .fillMaxWidth()
                .padding(16.dp),
            contentAlignment = Alignment.Center,
        ) {
            Text(text = label)
        }
    }
}

// ─── Stub screens ─────────────────────────────────────────────────────────────

@Composable fun TvBrowseScreen(title: String) { /* TODO */ }
@Composable fun TvSearchScreen()              { /* TODO */ }
@Composable fun TvSettingsScreen()            { /* TODO */ }

@OptIn(ExperimentalTvMaterial3Api::class)
@Composable
fun TvHeroBanner(modifier: Modifier = Modifier) {
    Surface(
        modifier = modifier,
        onClick = {},
    ) {
        Box(
            modifier = Modifier.padding(32.dp),
            contentAlignment = Alignment.CenterStart,
        ) {
            Column(verticalArrangement = Arrangement.spacedBy(8.dp)) {
                Text("Featured Title", style = MaterialTheme.typography.displaySmall)
                Text("Subtitle or description", style = MaterialTheme.typography.bodyLarge)
            }
        }
    }
}
