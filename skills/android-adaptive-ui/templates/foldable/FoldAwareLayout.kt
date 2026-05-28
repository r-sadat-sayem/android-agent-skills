package com.example.app.ui.foldable

import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.Row
import androidx.compose.foundation.layout.Spacer
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.height
import androidx.compose.foundation.layout.width
import androidx.compose.runtime.Composable
import androidx.compose.runtime.getValue
import androidx.compose.ui.Modifier
import androidx.compose.ui.platform.LocalDensity
import androidx.compose.ui.tooling.preview.Preview
import androidx.compose.ui.unit.dp

/**
 * A layout that branches based on the current device posture.
 *
 * Slot parameters:
 *   [topContent]    → shown in the top half during TableTop, or the left half during Book,
 *                     or as the full-screen content in Normal posture.
 *   [bottomContent] → shown below the hinge during TableTop posture.
 *   [sideContent]   → shown to the right of the hinge during Book or Separating posture.
 *
 * If your screen only needs to respond to one or two postures, you can ignore unused slots.
 */
@Composable
fun FoldAwareLayout(
    modifier: Modifier = Modifier,
    topContent: @Composable () -> Unit,
    bottomContent: @Composable () -> Unit = topContent,
    sideContent: @Composable () -> Unit = topContent,
) {
    val posture by rememberDevicePosture()
    val density = LocalDensity.current

    when (val currentPosture = posture) {
        is DevicePosture.TableTopPosture -> {
            // Device is folded like a laptop/stand — horizontal hinge
            // Top half: primary content (e.g., video, map, camera preview)
            // Bottom half: controls, keyboard, secondary info
            val hingeHeightDp = with(density) {
                currentPosture.hingePosition.height().toDp()
            }
            Column(modifier = modifier.fillMaxSize()) {
                Column(modifier = Modifier.weight(1f)) { topContent() }
                if (hingeHeightDp > 0.dp) Spacer(Modifier.height(hingeHeightDp))
                Column(modifier = Modifier.weight(1f)) { bottomContent() }
            }
        }

        is DevicePosture.BookPosture -> {
            // Device is folded like a book — vertical hinge
            // Left half: primary (list, navigation, reader page)
            // Right half: secondary (detail, next page, annotations)
            val hingeWidthDp = with(density) {
                currentPosture.hingePosition.width().toDp()
            }
            Row(modifier = modifier.fillMaxSize()) {
                Column(modifier = Modifier.weight(1f)) { topContent() }
                if (hingeWidthDp > 0.dp) Spacer(Modifier.width(hingeWidthDp))
                Column(modifier = Modifier.weight(1f)) { sideContent() }
            }
        }

        is DevicePosture.SeparatingPosture -> {
            // Dual-screen device (e.g., Surface Duo) fully opened flat.
            // Treat each screen as a distinct panel with a physical gap between them.
            val hingeWidthDp = with(density) {
                currentPosture.hingePosition.width().toDp()
            }
            Row(modifier = modifier.fillMaxSize()) {
                Column(modifier = Modifier.weight(1f)) { topContent() }
                // The physical gap between the two screens — do not render content here
                Spacer(Modifier.width(hingeWidthDp.coerceAtLeast(8.dp)))
                Column(modifier = Modifier.weight(1f)) { sideContent() }
            }
        }

        DevicePosture.NormalPosture -> {
            // Standard phone or fully-open foldable — single pane
            Column(modifier = modifier.fillMaxSize()) { topContent() }
        }
    }
}

// ─── Previews ─────────────────────────────────────────────────────────────────
// Note: To preview each posture, use FoldingFeature test builders in a debug
// source set. The previews below show the NormalPosture branch.

@Preview(name = "Normal posture — 360dp", widthDp = 360, heightDp = 800)
@Composable
private fun FoldAwareNormalPreview() {
    FoldAwareLayout(
        topContent = { androidx.compose.material3.Text("Top / Main content") },
        bottomContent = { androidx.compose.material3.Text("Bottom / Controls") },
        sideContent = { androidx.compose.material3.Text("Side / Detail") },
    )
}
