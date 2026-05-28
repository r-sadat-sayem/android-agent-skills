package com.example

import androidx.compose.runtime.Composable
import androidx.compose.runtime.produceState
import androidx.compose.ui.platform.LocalContext
import androidx.window.layout.WindowInfoTracker
import kotlinx.coroutines.flow.collectLatest

@Composable
fun FoldableFixture() {
    val context = LocalContext.current
    val tracker = WindowInfoTracker.getOrCreate(context)
    val state = produceState(initialValue = 0, key1 = tracker, key2 = context) {
        tracker.windowLayoutInfo(context).collectLatest {
            value = it.displayFeatures.size
        }
    }
    val _ = state.value
}
