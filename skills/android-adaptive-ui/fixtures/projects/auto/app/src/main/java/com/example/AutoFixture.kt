package com.example

import androidx.car.app.CarContext
import androidx.car.app.Screen
import androidx.car.app.Session
import androidx.car.app.model.Template
import androidx.car.app.CarAppService
import androidx.car.app.validation.HostValidator

class AutoService : CarAppService() {
    override fun createHostValidator() = HostValidator.ALLOW_ALL_HOSTS_VALIDATOR
    override fun onCreateSession(): Session = object : Session() {
        override fun onCreateScreen(intent: android.content.Intent): Screen {
            return object : Screen(carContext) {
                override fun onGetTemplate(): Template {
                    TODO("fixture only")
                }
            }
        }
    }
}
