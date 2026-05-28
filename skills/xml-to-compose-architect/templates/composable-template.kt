@file:Suppress("UnusedPrivateMember")

package com.example.migration

import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.padding
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.ui.Modifier
import androidx.compose.ui.tooling.preview.Preview
import androidx.compose.ui.unit.dp

data class ExampleUiState(
    val title: String = "Title",
    val subtitle: String = "Subtitle"
)

@Composable
fun ExampleRoute(
    uiState: ExampleUiState,
    onPrimaryAction: () -> Unit,
    modifier: Modifier = Modifier
) {
    ExampleContent(
        uiState = uiState,
        onPrimaryAction = onPrimaryAction,
        modifier = modifier
    )
}

@Composable
fun ExampleContent(
    uiState: ExampleUiState,
    onPrimaryAction: () -> Unit,
    modifier: Modifier = Modifier
) {
    Column(
        modifier = modifier
            .fillMaxSize()
            .padding(16.dp)
    ) {
        Text(
            text = uiState.title,
            style = MaterialTheme.typography.headlineSmall,
            modifier = Modifier.fillMaxWidth()
        )
        Text(
            text = uiState.subtitle,
            style = MaterialTheme.typography.bodyMedium,
            modifier = Modifier.fillMaxWidth()
        )
    }
}

@Preview(showBackground = true, name = "Light")
@Composable
private fun ExampleContentLightPreview() {
    ExampleContent(
        uiState = ExampleUiState(),
        onPrimaryAction = {}
    )
}

