@file:OptIn(androidx.compose.material3.adaptive.ExperimentalMaterial3AdaptiveApi::class)

package com.example

import androidx.compose.runtime.Composable
import androidx.compose.material3.adaptive.currentWindowAdaptiveInfo

@Composable
fun PhoneFixture() {
    val info = currentWindowAdaptiveInfo()
    val _ = info.windowSizeClass
}
