@file:OptIn(androidx.compose.material3.adaptive.ExperimentalMaterial3AdaptiveApi::class)

package com.example

import android.os.Parcelable
import androidx.activity.compose.BackHandler
import androidx.compose.runtime.Composable
import androidx.compose.material3.adaptive.layout.ListDetailPaneScaffoldRole
import androidx.compose.material3.adaptive.navigation.BackNavigationBehavior
import androidx.compose.material3.adaptive.navigation.rememberListDetailPaneScaffoldNavigator
import kotlinx.parcelize.Parcelize

@Parcelize
data class Item(val id: Int) : Parcelable

@Composable
fun LargeScreenFixture() {
    val navigator = rememberListDetailPaneScaffoldNavigator<Item>()
    BackHandler(navigator.canNavigateBack()) {
        navigator.navigateBack(BackNavigationBehavior.PopUntilScaffoldValueChange)
    }
    navigator.navigateTo(ListDetailPaneScaffoldRole.Detail, Item(1))
}
