package com.example.wear.ui.util

import androidx.compose.foundation.layout.BoxWithConstraints
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.runtime.Composable
import androidx.compose.ui.Modifier
import androidx.compose.ui.platform.LocalConfiguration
import androidx.wear.compose.material3.Text

// ─── Screen shape detection ───────────────────────────────────────────────────

/**
 * Branches layout based on whether the Wear OS device has a round or square screen.
 *
 * Most layout differences between round and square are best handled via
 * TransformingLazyColumn's automatic curved-padding behavior. Use this composable
 * only when you need fundamentally different layouts, not just different padding.
 *
 * Examples of when branching is justified:
 *   - A watch face that displays text arcs on round but straight lines on square
 *   - A dial/gauge that must be circular on round and rectangular on square
 *   - A complication layout where round needs a different number of slots
 */
@Composable
fun WearRoundSquareLayout(
    roundContent: @Composable () -> Unit,
    squareContent: @Composable () -> Unit,
) {
    val isRound = LocalConfiguration.current.isScreenRound
    if (isRound) {
        roundContent()
    } else {
        squareContent()
    }
}

// ─── Display size detection ───────────────────────────────────────────────────

// Wear OS display sizes: small ~38mm ≈ 192dp, standard ~44mm ≈ 225dp, large ~45mm+
private const val LARGE_DISPLAY_BREAKPOINT_DP = 225

/**
 * Returns true when the Wear OS display is at or above the large-display breakpoint.
 *
 * Use to:
 *   - Show more list items without scrolling
 *   - Use larger text sizes for glanceability
 *   - Enable additional complication slots on a watch face
 */
@Composable
fun isLargeWearDisplay(): Boolean =
    LocalConfiguration.current.screenWidthDp >= LARGE_DISPLAY_BREAKPOINT_DP

// ─── Responsive padding helper ────────────────────────────────────────────────

/**
 * Returns the recommended horizontal padding for Wear list content.
 *
 * Round displays need more padding at the edges to prevent text from being
 * obscured by the circular bezel. Square displays can use smaller padding.
 *
 * For TransformingLazyColumn, prefer using the contentPadding from ScreenScaffold
 * instead of adding manual padding — this helper is for non-list content.
 */
@Composable
fun wearHorizontalPadding(): androidx.compose.ui.unit.Dp {
    val isRound = LocalConfiguration.current.isScreenRound
    val isLarge = isLargeWearDisplay()
    return when {
        isRound && isLarge -> 36.dp
        isRound -> 28.dp
        else -> 16.dp
    }
}

private val Int.dp get() = androidx.compose.ui.unit.dp.run { this@dp.dp }

// ─── Preview ──────────────────────────────────────────────────────────────────

@androidx.wear.compose.ui.tooling.preview.WearPreviewDevices
@Composable
private fun WearRoundSquarePreview() {
    WearRoundSquareLayout(
        roundContent = { Text("Round screen layout") },
        squareContent = { Text("Square screen layout") },
    )
}
