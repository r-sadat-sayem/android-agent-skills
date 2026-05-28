package com.example.app.ui.foldable

import android.graphics.Rect
import androidx.compose.runtime.Composable
import androidx.compose.runtime.State
import androidx.compose.runtime.remember
import androidx.compose.ui.platform.LocalContext
import androidx.lifecycle.compose.collectAsStateWithLifecycle
import androidx.window.layout.FoldingFeature
import androidx.window.layout.WindowInfoTracker

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
 * Must be called inside a composable. Uses [collectAsStateWithLifecycle] to prevent
 * leaks when the composable leaves the composition.
 *
 * Gradle dependencies required:
 *   implementation("androidx.window:window:1.5.1")
 *   implementation("androidx.lifecycle:lifecycle-runtime-compose:2.9.0")
 */
@Composable
fun rememberDevicePosture(): State<DevicePosture> {
    val context = LocalContext.current

    val windowInfoTracker = remember(context) {
        WindowInfoTracker.getOrCreate(context)
    }

    return windowInfoTracker
        .windowLayoutInfo(context)
        .collectAsStateWithLifecycle(
            initialValue = androidx.window.layout.WindowLayoutInfo(emptyList()),
        )
        .let { layoutInfoState ->
            // Map WindowLayoutInfo → DevicePosture
            remember(layoutInfoState.value) {
                val foldingFeature = layoutInfoState.value.displayFeatures
                    .filterIsInstance<FoldingFeature>()
                    .firstOrNull()
                    ?: return@remember object : State<DevicePosture> {
                        override val value: DevicePosture = DevicePosture.NormalPosture
                    }

                val posture = mapFoldingFeatureToPosture(foldingFeature)
                object : State<DevicePosture> {
                    override val value: DevicePosture = posture
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
