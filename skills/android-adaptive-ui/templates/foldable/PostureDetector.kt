package com.example.app.ui.foldable

import android.graphics.Rect
import androidx.compose.runtime.Composable
import androidx.compose.runtime.State
import androidx.compose.runtime.produceState
import androidx.compose.runtime.remember
import androidx.compose.ui.platform.LocalContext
import androidx.window.layout.FoldingFeature
import androidx.window.layout.WindowInfoTracker
import kotlinx.coroutines.flow.collectLatest

// ─── Posture sealed class ──────────────────────────────────────────────────────

/**
 * Maps the raw [FoldingFeature] state + orientation into an application-level posture.
 *
 * Build your layout decisions against these postures rather than against
 * FoldingFeature properties directly. This keeps the UI layer decoupled from
 * the Jetpack WindowManager API surface.
 *
 * Posture matrix:
 *   STATE_HALF_OPENED + HORIZONTAL  → TableTopPosture  (keyboard/stand mode)
 *   STATE_HALF_OPENED + VERTICAL    → BookPosture       (e-reader / card mode)
 *   STATE_FLAT       + isSeparating → SeparatingPosture (dual-screen, e.g. Surface Duo)
 *   everything else                 → NormalPosture     (standard single-pane)
 */
sealed class DevicePosture {
    data object NormalPosture : DevicePosture()

    data class TableTopPosture(
        val hingePosition: Rect,
    ) : DevicePosture()

    data class BookPosture(
        val hingePosition: Rect,
    ) : DevicePosture()

    data class SeparatingPosture(
        val hingePosition: Rect,
    ) : DevicePosture()
}

// ─── State producer ───────────────────────────────────────────────────────────

/**
 * Returns a [State] that reflects the current device posture, updating automatically
 * when the fold state changes.
 *
 * Must be called inside a composable. Uses [produceState] to keep collection
 * lifecycle-aware and tied to composition.
 *
 * Gradle dependencies required:
 *   implementation("androidx.window:window:1.5.1")
 */
@Composable
fun rememberDevicePosture(): State<DevicePosture> {
    val context = LocalContext.current

    val windowInfoTracker = remember(context) {
        WindowInfoTracker.getOrCreate(context)
    }

    return produceState<DevicePosture>(
        initialValue = DevicePosture.NormalPosture,
        key1 = windowInfoTracker,
        key2 = context,
    ) {
        windowInfoTracker.windowLayoutInfo(context).collectLatest { layoutInfo ->
            val foldingFeature = layoutInfo.displayFeatures
                .filterIsInstance<FoldingFeature>()
                .firstOrNull()

            value = if (foldingFeature == null) {
                DevicePosture.NormalPosture
            } else {
                mapFoldingFeatureToPosture(foldingFeature)
            }
        }
    }
}

// ─── Mapping logic ────────────────────────────────────────────────────────────

private fun mapFoldingFeatureToPosture(feature: FoldingFeature): DevicePosture {
    val hinge = feature.bounds.toRect()

    return when {
        feature.state == FoldingFeature.State.HALF_OPENED &&
                feature.orientation == FoldingFeature.Orientation.HORIZONTAL ->
            DevicePosture.TableTopPosture(hingePosition = hinge)

        feature.state == FoldingFeature.State.HALF_OPENED &&
                feature.orientation == FoldingFeature.Orientation.VERTICAL ->
            DevicePosture.BookPosture(hingePosition = hinge)

        feature.state == FoldingFeature.State.FLAT && feature.isSeparating ->
            DevicePosture.SeparatingPosture(hingePosition = hinge)

        else -> DevicePosture.NormalPosture
    }
}

private fun androidx.window.layout.DisplayFeature.Bounds.toRect(): Rect =
    Rect(left, top, right, bottom)
