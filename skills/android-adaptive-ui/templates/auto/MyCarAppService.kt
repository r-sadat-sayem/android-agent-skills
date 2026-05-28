package com.example.auto

import androidx.car.app.CarAppService
import androidx.car.app.Screen
import androidx.car.app.Session
import androidx.car.app.validation.HostValidator

/**
 * Entry point for the Android Auto integration.
 *
 * Android Auto uses a projection model: your app runs on the phone and its UI
 * is projected to the car head unit. The Car App Library provides a
 * template-based rendering model — you describe WHAT to show using Template
 * objects; the host (the car) decides HOW to render it.
 *
 * CRITICAL: There is NO Compose, NO custom View, NO setContent{} anywhere in
 * this module. Any Compose in a Screen subclass will produce a blank screen.
 *
 * AndroidManifest.xml required entries:
 * ┌──────────────────────────────────────────────────────────┐
 * │ <service                                                  │
 * │     android:name=".MyCarAppService"                      │
 * │     android:exported="true">                             │
 * │   <intent-filter>                                        │
 * │     <action android:name="androidx.car.app.CarAppService" />
 * │   </intent-filter>                                       │
 * │   <meta-data                                             │
 * │     android:name="androidx.car.app.minCarApiLevel"       │
 * │     android:value="1" />                                 │
 * │   <!-- Choose the correct category for your app: -->     │
 * │   <!-- IOT / NAVIGATION / PARKING / CHARGING / POI / MESSAGING / CALLING -->
 * │   <meta-data                                             │
 * │     android:name="androidx.car.app.category"            │
 * │     android:value="androidx.car.app.category.IOT" />    │
 * │ </service>                                               │
 * └──────────────────────────────────────────────────────────┘
 *
 * Gradle dependency (pick ONE):
 *   implementation("androidx.car.app:app-projected:1.7.0")   // Android Auto
 *   implementation("androidx.car.app:app-automotive:1.7.0")  // Automotive OS
 */
class MyCarAppService : CarAppService() {

    override fun createHostValidator(): HostValidator {
        // ALLOW_ALL_HOSTS is safe for development but not for production.
        // For production, replace with a validator that restricts to known host signatures:
        //   return HostValidator.Builder(applicationContext)
        //       .addAllowedHosts(R.array.hosts_allowlist)
        //       .build()
        return HostValidator.ALLOW_ALL_HOSTS_VALIDATOR
    }

    override fun onCreateSession(): Session = MySession()
}

class MySession : Session() {
    override fun onCreateScreen(intent: android.content.Intent): Screen {
        return MainScreen(carContext)
    }
}
