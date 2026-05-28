package com.example.auto

import androidx.car.app.CarContext
import androidx.car.app.Screen
import androidx.car.app.model.Action
import androidx.car.app.model.ItemList
import androidx.car.app.model.ListTemplate
import androidx.car.app.model.Row
import androidx.car.app.model.Template

/**
 * First screen shown when the driver opens the app in Android Auto.
 *
 * ── Driver Distraction Rules ──────────────────────────────────────────────────
 * 1. NO custom Views. Everything is expressed as a Template object.
 * 2. NO Compose. setContent{} must never appear in any Screen subclass.
 * 3. NO arbitrary animations — only those provided by the host template system.
 * 4. NO direct touch input — use Row.Builder().setOnClickListener() only.
 * 5. Item limits:
 *      minCarApiLevel 1-2: maximum 6 items per ListTemplate
 *      minCarApiLevel 3+:  configurable via CarAppApiLevels
 *    Exceeding the limit causes the host to silently truncate or throw.
 * 6. Text must be glanceable — 1-2 words for titles, brief metadata for subtitles.
 * 7. Color palette must meet WCAG 2.1 AA contrast ratios (the host may override colors).
 * ─────────────────────────────────────────────────────────────────────────────
 */
class MainScreen(carContext: CarContext) : Screen(carContext) {

    override fun onGetTemplate(): Template {
        val itemListBuilder = ItemList.Builder()

        SAMPLE_DESTINATIONS.take(6).forEach { destination ->
            itemListBuilder.addItem(
                Row.Builder()
                    .setTitle(destination.title)
                    .addText(destination.subtitle)
                    .setOnClickListener {
                        // Navigate to a new screen or perform an action
                        screenManager.push(DetailScreen(carContext, destination))
                    }
                    .build()
            )
        }

        return ListTemplate.Builder()
            .setHeaderAction(Action.APP_ICON)
            .setTitle("My App")
            .setSingleList(itemListBuilder.build())
            .build()
    }
}

// ─── Detail screen example ────────────────────────────────────────────────────

class DetailScreen(
    carContext: CarContext,
    private val destination: Destination,
) : Screen(carContext) {

    override fun onGetTemplate(): Template {
        return ListTemplate.Builder()
            .setHeaderAction(Action.BACK)
            .setTitle(destination.title)
            .setSingleList(
                ItemList.Builder()
                    .addItem(
                        Row.Builder()
                            .setTitle(destination.subtitle)
                            .build()
                    )
                    .build()
            )
            .build()
    }
}

// ─── Data model ───────────────────────────────────────────────────────────────

data class Destination(val title: String, val subtitle: String)

private val SAMPLE_DESTINATIONS = listOf(
    Destination("Home", "123 Main St"),
    Destination("Work", "456 Office Blvd"),
    Destination("Gym", "789 Fitness Ave"),
    Destination("Coffee", "321 Brew Lane"),
    Destination("Park", "Gateway Park"),
    Destination("Airport", "Terminal B"),
)
