@file:OptIn(ExperimentalMaterial3AdaptiveApi::class)

package com.example.app.ui

import androidx.compose.foundation.layout.Box
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.Row
import androidx.compose.foundation.layout.Spacer
import androidx.compose.foundation.layout.fillMaxHeight
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.width
import androidx.compose.material3.adaptive.ExperimentalMaterial3AdaptiveApi
import androidx.compose.material3.adaptive.currentWindowAdaptiveInfo
import androidx.compose.material3.windowsizeclass.isWidthAtLeastBreakpoint
import androidx.compose.material3.windowsizeclass.WIDTH_DP_MEDIUM_LOWER_BOUND
import androidx.compose.material3.windowsizeclass.WIDTH_DP_EXPANDED_LOWER_BOUND
import androidx.compose.runtime.Composable
import androidx.compose.runtime.getValue
import androidx.compose.runtime.produceState
import androidx.compose.ui.Modifier
import androidx.compose.ui.platform.LocalContext
import androidx.compose.ui.unit.dp
import androidx.window.layout.FoldingFeature
import androidx.window.layout.WindowInfoTracker
import kotlinx.coroutines.flow.distinctUntilChanged

// ─── DevicePosture ────────────────────────────────────────────────────────────
//
// "Resizable" covers both foldables and multi-window:
//   • Foldable half-opened  → TableTopPosture or BookPosture (split at hinge)
//   • Foldable flat + isSeparating=true → SeparatingPosture (dual-screen, e.g. Surface Duo)
//   • Foldable flat + isSeparating=false → NormalPosture (full single screen)
//   • Multi-window (no FoldingFeature) → NormalPosture; layout reacts via WindowSizeClass alone
//
// Always use produceState + WindowInfoTracker — never collect in a raw coroutine scope
// (that leaks on config change / activity recreation).

sealed interface DevicePosture {
    data object NormalPosture : DevicePosture
    data class  TableTopPosture(val hingePosition: FoldingFeature) : DevicePosture
    data class  BookPosture(val hingePosition: FoldingFeature) : DevicePosture
    data class  SeparatingPosture(val hingePosition: FoldingFeature) : DevicePosture
}

@Composable
fun rememberDevicePosture(): DevicePosture {
    val context = LocalContext.current
    val posture by produceState(initialValue = DevicePosture.NormalPosture as DevicePosture) {
        WindowInfoTracker
            .getOrCreate(context)
            .windowLayoutInfo(context)
            .distinctUntilChanged()
            .collect { layoutInfo ->
                val fold = layoutInfo.displayFeatures
                    .filterIsInstance<FoldingFeature>()
                    .firstOrNull()
                value = when {
                    fold == null -> DevicePosture.NormalPosture
                    fold.state == FoldingFeature.State.HALF_OPENED &&
                        fold.orientation == FoldingFeature.Orientation.HORIZONTAL ->
                        DevicePosture.TableTopPosture(fold)
                    fold.state == FoldingFeature.State.HALF_OPENED &&
                        fold.orientation == FoldingFeature.Orientation.VERTICAL ->
                        DevicePosture.BookPosture(fold)
                    fold.state == FoldingFeature.State.FLAT && fold.isSeparating ->
                        DevicePosture.SeparatingPosture(fold)
                    else -> DevicePosture.NormalPosture
                }
            }
    }
    return posture
}

// ─── Root composable ──────────────────────────────────────────────────────────

@Composable
fun ResizableApp() {
    // WindowSizeClass — call ONCE at composition root, pass down as parameter.
    // This handles multi-window resize automatically (phone side-by-side = Compact width).
    val adaptiveInfo   = currentWindowAdaptiveInfo()
    val windowSizeClass = adaptiveInfo.windowSizeClass

    // Posture — lifecycle-safe observation via produceState.
    val posture = rememberDevicePosture()

    ResizableLayout(
        windowSizeClass = windowSizeClass,
        posture         = posture,
    )
}

@Composable
fun ResizableLayout(
    windowSizeClass: androidx.compose.material3.windowsizeclass.WindowSizeClass,
    posture: DevicePosture,
    modifier: Modifier = Modifier,
) {
    val isExpanded = windowSizeClass.isWidthAtLeastBreakpoint(WIDTH_DP_EXPANDED_LOWER_BOUND)
    val isMedium   = windowSizeClass.isWidthAtLeastBreakpoint(WIDTH_DP_MEDIUM_LOWER_BOUND)

    when {
        // ── Foldable: TableTop ─────────────────────────────────────────────────
        // Device half-opened horizontally. Top half = primary content,
        // bottom half = secondary (controls, metadata).
        posture is DevicePosture.TableTopPosture -> {
            val hingeHeight = posture.hingePosition.bounds.height().dp
            Column(modifier = modifier.fillMaxSize()) {
                Box(modifier = Modifier.weight(1f).fillMaxWidth()) {
                    PrimaryContent()
                }
                Spacer(modifier = Modifier.fillMaxWidth().width(hingeHeight))
                Box(modifier = Modifier.weight(1f).fillMaxWidth()) {
                    SecondaryContent()
                }
            }
        }

        // ── Foldable: Book ────────────────────────────────────────────────────
        // Device half-opened vertically. Left = primary, right = detail/secondary.
        posture is DevicePosture.BookPosture -> {
            val hingeWidth = posture.hingePosition.bounds.width().dp
            Row(modifier = modifier.fillMaxSize()) {
                Box(modifier = Modifier.weight(1f).fillMaxHeight()) {
                    PrimaryContent()
                }
                Spacer(modifier = Modifier.fillMaxHeight().width(hingeWidth))
                Box(modifier = Modifier.weight(1f).fillMaxHeight()) {
                    SecondaryContent()
                }
            }
        }

        // ── Foldable: Separating (dual-screen flat) ───────────────────────────
        // Two distinct screens with a physical gap. Treat the same as BookPosture
        // but the hinge gap is larger and non-interactive.
        posture is DevicePosture.SeparatingPosture -> {
            val hingeWidth = posture.hingePosition.bounds.width().dp
            Row(modifier = modifier.fillMaxSize()) {
                Box(modifier = Modifier.weight(1f).fillMaxHeight()) {
                    PrimaryContent()
                }
                Spacer(modifier = Modifier.fillMaxHeight().width(hingeWidth))
                Box(modifier = Modifier.weight(1f).fillMaxHeight()) {
                    SecondaryContent()
                }
            }
        }

        // ── Large/expanded window (tablet, foldable fully open, large multi-window)
        // Two-pane side-by-side without a physical hinge.
        isExpanded -> {
            Row(modifier = modifier.fillMaxSize()) {
                Box(modifier = Modifier.weight(1f).fillMaxHeight()) {
                    PrimaryContent()
                }
                Box(modifier = Modifier.weight(1f).fillMaxHeight()) {
                    SecondaryContent()
                }
            }
        }

        // ── Medium window (small tablet, phone landscape, foldable outer screen)
        // Primary content only; secondary accessible via navigation.
        isMedium -> {
            Box(modifier = modifier.fillMaxSize()) {
                PrimaryContent()
            }
        }

        // ── Compact (phone portrait, multi-window narrow slot) ─────────────────
        else -> {
            Box(modifier = modifier.fillMaxSize()) {
                PrimaryContent()
            }
        }
    }
}

// ─── Stub screens ─────────────────────────────────────────────────────────────

@Composable fun PrimaryContent()   { /* TODO: main content pane  */ }
@Composable fun SecondaryContent() { /* TODO: detail / controls  */ }
