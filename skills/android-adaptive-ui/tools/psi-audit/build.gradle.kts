plugins {
    kotlin("jvm") version "2.0.21"
    application
}

repositories {
    mavenCentral()
}

dependencies {
    implementation("org.jetbrains.kotlin:kotlin-compiler-embeddable:2.0.21")
}

application {
    mainClass.set("dev.adaptive.PsiAuditMainKt")
}

kotlin {
    jvmToolchain(17)
}
