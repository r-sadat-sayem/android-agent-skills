plugins {
    id("com.android.application")
    id("org.jetbrains.kotlin.android")
}

android {
    namespace = "com.example.fixture.auto"
    compileSdk = 35

    defaultConfig {
        applicationId = "com.example.fixture.auto"
        minSdk = 26
        targetSdk = 35
        versionCode = 1
        versionName = "1.0"
    }
}

dependencies {
    implementation("androidx.car.app:app-projected:1.7.0")
}
