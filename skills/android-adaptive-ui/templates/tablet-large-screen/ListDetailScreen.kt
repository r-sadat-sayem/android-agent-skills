@file:OptIn(ExperimentalMaterial3AdaptiveApi::class)

package com.example.app.ui

import android.os.Parcelable
import androidx.activity.compose.BackHandler
import androidx.compose.foundation.clickable
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.lazy.LazyColumn
import androidx.compose.foundation.lazy.items
import androidx.compose.material3.ListItem
import androidx.compose.material3.Scaffold
import androidx.compose.material3.Text
import androidx.compose.material3.adaptive.ExperimentalMaterial3AdaptiveApi
import androidx.compose.material3.adaptive.layout.AnimatedPane
import androidx.compose.material3.adaptive.layout.ListDetailPaneScaffoldRole
import androidx.compose.material3.adaptive.navigation.BackNavigationBehavior
import androidx.compose.material3.adaptive.navigation.NavigableListDetailPaneScaffold
import androidx.compose.material3.adaptive.navigation.rememberListDetailPaneScaffoldNavigator
import androidx.compose.runtime.Composable
import androidx.compose.ui.Modifier
import androidx.compose.ui.tooling.preview.Preview
import androidx.compose.ui.unit.dp
import kotlinx.parcelize.Parcelize

// ─── Content model ────────────────────────────────────────────────────────────

// ContentItem is the navigation key — it must be Parcelable so the system can
// restore it across process death and configuration changes.
@Parcelize
data class ContentItem(
    val id: Int,
    val title: String,
    val body: String,
) : Parcelable

private val SAMPLE_ITEMS = (1..20).map {
    ContentItem(id = it, title = "Item $it", body = "Detail body for item $it.")
}

// ─── Screen ───────────────────────────────────────────────────────────────────

/**
 * List-detail layout that adapts across all window size classes:
 *   Compact  → single pane, navigates between list and detail
 *   Medium   → two panes side by side
 *   Expanded → two panes, detail pane wider
 *
 * AndroidManifest.xml: add android:enableOnBackInvokedCallback="true" to your
 * <application> or <activity> tag to enable predictive back on API 33+.
 */
@Composable
fun ListDetailScreen() {
    val navigator = rememberListDetailPaneScaffoldNavigator<ContentItem>()
    BackHandler(navigator.canNavigateBack()) {
        navigator.navigateBack(BackNavigationBehavior.PopUntilScaffoldValueChange)
    }

    NavigableListDetailPaneScaffold(
        navigator = navigator,
        listPane = {
            AnimatedPane {
                ListPane(
                    items = SAMPLE_ITEMS,
                    onItemClick = { item ->
                        navigator.navigateTo(
                            pane = ListDetailPaneScaffoldRole.Detail,
                            contentKey = item,
                        )
                    },
                )
            }
        },
        detailPane = {
            AnimatedPane {
                val item = navigator.currentDestination?.contentKey
                if (item != null) {
                    DetailPane(item = item)
                } else {
                    EmptyDetail()
                }
            }
        },
        // extraPane is optional — remove if you don't need a third panel
        extraPane = {
            AnimatedPane {
                Text(
                    text = "Extra panel (e.g., metadata, actions)",
                    modifier = Modifier.padding(16.dp),
                )
            }
        },
    )
}

// ─── Pane composables ─────────────────────────────────────────────────────────

@Composable
private fun ListPane(
    items: List<ContentItem>,
    onItemClick: (ContentItem) -> Unit,
) {
    LazyColumn(modifier = Modifier.fillMaxSize()) {
        items(items, key = { it.id }) { item ->
            ListItem(
                headlineContent = { Text(item.title) },
                modifier = Modifier.clickable { onItemClick(item) },
            )
        }
    }
}

@Composable
private fun DetailPane(item: ContentItem) {
    Scaffold { padding ->
        Text(
            text = item.body,
            modifier = Modifier
                .fillMaxSize()
                .padding(padding)
                .padding(16.dp),
        )
    }
}

@Composable
private fun EmptyDetail() {
    Text(
        text = "Select an item to view details",
        modifier = Modifier.padding(16.dp),
    )
}

// ─── Previews ─────────────────────────────────────────────────────────────────

@Preview(name = "Compact — 360dp", widthDp = 360, heightDp = 800)
@Composable
private fun ListDetailCompactPreview() = ListDetailScreen()

@Preview(name = "Expanded — 1200dp", widthDp = 1200, heightDp = 900)
@Composable
private fun ListDetailExpandedPreview() = ListDetailScreen()
