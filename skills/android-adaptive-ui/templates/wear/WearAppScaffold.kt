package com.example.wear.ui

// ─── CRITICAL: Import ONLY from androidx.wear.compose — NEVER from androidx.compose.material3
import androidx.compose.runtime.Composable
import androidx.compose.ui.Modifier
import androidx.compose.ui.tooling.preview.Preview
import androidx.wear.compose.foundation.lazy.TransformingLazyColumn
import androidx.wear.compose.foundation.lazy.rememberTransformingLazyColumnState
import androidx.wear.compose.material3.AppScaffold
import androidx.wear.compose.material3.Button
import androidx.wear.compose.material3.ListHeader
import androidx.wear.compose.material3.MaterialTheme          // wear.compose.material3 — NOT compose.material3
import androidx.wear.compose.material3.ScreenScaffold
import androidx.wear.compose.material3.Text
import androidx.wear.compose.material3.TimeText
import androidx.wear.compose.material3.lazy.rememberTransformationSpec
import androidx.wear.compose.material3.lazy.transformedHeight
import androidx.wear.compose.ui.tooling.preview.WearPreviewDevices
import androidx.wear.compose.ui.tooling.preview.WearPreviewFontScales

// ─── Root entry point ─────────────────────────────────────────────────────────

/**
 * Root Wear OS app composable.
 *
 * Structure:
 *   AppScaffold  — manages TimeText and overlays at the app level
 *   └─ ScreenScaffold  — manages scroll-aware vignette and edge padding per screen
 *      └─ TransformingLazyColumn  — the current recommended scrollable list for Wear OS
 *
 * Never use androidx.compose.material3 components in this file.
 * The MaterialTheme here is from androidx.wear.compose.material3 — they are incompatible.
 */
@Composable
fun WearApp() {
    MaterialTheme {
        AppScaffold(
            timeText = { TimeText() },
        ) {
            WearMainScreen()
        }
    }
}

// ─── Screen ───────────────────────────────────────────────────────────────────

@Composable
fun WearMainScreen() {
    val columnState = rememberTransformingLazyColumnState()
    val transformationSpec = rememberTransformationSpec()

    ScreenScaffold(scrollState = columnState) { contentPadding ->
        TransformingLazyColumn(
            state = columnState,
            contentPadding = contentPadding,
        ) {
            item {
                ListHeader {
                    Text("My App")
                }
            }

            items(10) { index ->
                Button(
                    modifier = Modifier.transformedHeight(this, transformationSpec),
                    onClick = { /* TODO */ },
                ) {
                    Text("Item $index")
                }
            }

            // TODO: Replace with your actual content items
        }
    }
}

// ─── Previews ─────────────────────────────────────────────────────────────────
// @WearPreviewDevices renders on all Wear device shapes (round, square, rectangular)
// @WearPreviewFontScales renders across font size accessibility settings

@WearPreviewDevices
@WearPreviewFontScales
@Composable
private fun WearMainScreenPreview() {
    MaterialTheme {
        AppScaffold {
            WearMainScreen()
        }
    }
}
