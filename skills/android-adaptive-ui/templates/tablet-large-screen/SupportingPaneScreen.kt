@file:OptIn(ExperimentalMaterial3AdaptiveApi::class)

package com.example.app.ui

import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.Row
import androidx.compose.foundation.layout.Spacer
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.height
import androidx.compose.foundation.layout.padding
import androidx.compose.material3.Button
import androidx.compose.material3.Text
import androidx.compose.material3.adaptive.ExperimentalMaterial3AdaptiveApi
import androidx.compose.material3.adaptive.layout.AnimatedPane
import androidx.compose.material3.adaptive.layout.SupportingPaneScaffoldRole
import androidx.compose.material3.adaptive.navigation.BackNavigationBehavior
import androidx.compose.material3.adaptive.navigation.NavigableSupportingPaneScaffold
import androidx.compose.material3.adaptive.navigation.rememberSupportingPaneScaffoldNavigator
import androidx.compose.runtime.Composable
import androidx.compose.ui.Modifier
import androidx.compose.ui.tooling.preview.Preview
import androidx.compose.ui.unit.dp

/**
 * Supporting-pane layout for document, media, or productivity UIs where the
 * supporting pane supplements (rather than replaces) the main content.
 *
 * Window size behavior:
 *   Compact  → supporting pane overlays the main pane (navigate explicitly)
 *   Medium   → main pane + supporting pane at equal width
 *   Expanded → main pane (wider) + supporting pane side by side
 *
 * Typical use cases: document editor + outline, player + queue, feed + filters.
 */
@Composable
fun SupportingPaneScreen() {
    val navigator = rememberSupportingPaneScaffoldNavigator()

    NavigableSupportingPaneScaffold(
        navigator = navigator,
        mainPane = {
            AnimatedPane {
                MainContent(
                    onShowSupporting = {
                        navigator.navigateTo(SupportingPaneScaffoldRole.Supporting)
                    },
                )
            }
        },
        supportingPane = {
            AnimatedPane {
                SupportingContent(
                    onClose = {
                        if (navigator.canNavigateBack()) {
                            navigator.navigateBack(BackNavigationBehavior.PopUntilContentChange)
                        }
                    },
                )
            }
        },
    )
}

// ─── Pane composables ─────────────────────────────────────────────────────────

@Composable
private fun MainContent(onShowSupporting: () -> Unit) {
    Column(
        modifier = Modifier
            .fillMaxSize()
            .padding(16.dp),
    ) {
        Text("Main Content")
        Spacer(Modifier.height(8.dp))
        // On compact screens this button navigates to the supporting pane.
        // On medium/expanded the supporting pane is always visible — the button
        // can be hidden or repurposed.
        Button(onClick = onShowSupporting) {
            Text("Open supporting panel")
        }
        // TODO: replace with your main content
    }
}

@Composable
private fun SupportingContent(onClose: () -> Unit) {
    Column(
        modifier = Modifier
            .fillMaxSize()
            .padding(16.dp),
    ) {
        Text("Supporting Panel")
        Spacer(Modifier.height(8.dp))
        Button(onClick = onClose) {
            Text("Close")
        }
        // TODO: replace with your supporting content (outline, comments, filters, etc.)
    }
}

// ─── Previews ─────────────────────────────────────────────────────────────────

@Preview(name = "Compact — 360dp", widthDp = 360, heightDp = 800)
@Composable
private fun SupportingPaneCompactPreview() = SupportingPaneScreen()

@Preview(name = "Medium — 700dp", widthDp = 700, heightDp = 1000)
@Composable
private fun SupportingPaneMediumPreview() = SupportingPaneScreen()

@Preview(name = "Expanded — 1200dp", widthDp = 1200, heightDp = 900)
@Composable
private fun SupportingPaneExpandedPreview() = SupportingPaneScreen()
