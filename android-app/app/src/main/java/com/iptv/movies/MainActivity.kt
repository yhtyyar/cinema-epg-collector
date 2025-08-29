package com.iptv.movies

import android.os.Bundle
import androidx.activity.ComponentActivity
import androidx.activity.compose.setContent
import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.remember
import androidx.compose.runtime.setValue
import com.iptv.movies.data.ApiClient
import com.iptv.movies.navigation.AppNav
import com.iptv.movies.ui.theme.MoviesTheme

class MainActivity : ComponentActivity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContent {
            var isDark by remember { mutableStateOf(true) }
            MoviesTheme(darkTheme = isDark) {
                AppNav(api = ApiClient.api, isDark = isDark) { isDark = !isDark }
            }
        }
    }
}
