package com.example

import androidx.compose.runtime.Composable
import androidx.compose.ui.platform.LocalConfiguration
import androidx.wear.compose.material3.Text

@Composable
fun WearFixture() {
    val round = LocalConfiguration.current.isScreenRound
    Text(if (round) "Round" else "Square")
}
