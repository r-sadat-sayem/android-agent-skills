package com.example.app.ui.util

import androidx.compose.foundation.layout.Box
import androidx.compose.foundation.layout.BoxWithConstraints
import androidx.compose.foundation.layout.BoxWithConstraintsScope
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.rememberScrollState
import androidx.compose.foundation.verticalScroll
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.unit.Dp
import androidx.compose.ui.unit.dp

/**
 * Guards content against rendering below [minWidth] or above [maxWidth].
 *
 * Use when a composable has a known minimum usable width (e.g. a chart that breaks
 * below 280dp) or a maximum meaningful width (e.g. a form that looks odd beyond 600dp).
 *
 * For general window-size layout decisions, prefer WindowSizeClass breakpoints instead.
 */
@Composable
fun BoxWithConstraintsGuard(
    minWidth: Dp = 0.dp,
    maxWidth: Dp = Dp.Infinity,
    modifier: Modifier = Modifier,
    fallback: @Composable () -> Unit = { UnsupportedSizeMessage() },
    content: @Composable BoxWithConstraintsScope.() -> Unit,
) {
    BoxWithConstraints(modifier = modifier) {
        when {
            this.maxWidth < minWidth -> fallback()
            minWidth == 0.dp && maxWidth == Dp.Infinity -> content()
            this.maxWidth > maxWidth -> {
                // Center-constrain the content to maxWidth
                Box(Modifier.fillMaxWidth(), contentAlignment = Alignment.Center) {
                    BoxWithConstraints(Modifier.fillMaxSize()) { content() }
                }
            }
            else -> content()
        }
    }
}

/**
 * Wraps [content] in a vertically scrollable Column when the available height
 * drops below [scrollThreshold].
 *
 * Use on screens with many fields (settings, forms) that must not clip on
 * compact-height windows (phones in landscape).
 */
@Composable
fun ScrollableColumnGuard(
    scrollThreshold: Dp = 400.dp,
    modifier: Modifier = Modifier,
    content: @Composable () -> Unit,
) {
    BoxWithConstraints(modifier = modifier) {
        val needsScroll = maxHeight < scrollThreshold
        if (needsScroll) {
            Column(
                modifier = Modifier
                    .fillMaxSize()
                    .verticalScroll(rememberScrollState()),
            ) {
                content()
            }
        } else {
            Column(modifier = Modifier.fillMaxSize()) {
                content()
            }
        }
    }
}

@Composable
private fun UnsupportedSizeMessage() {
    Box(Modifier.fillMaxSize(), contentAlignment = Alignment.Center) {
        Text("This view requires a larger screen area.")
    }
}
