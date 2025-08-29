package com.iptv.movies.navigation

import androidx.compose.runtime.Composable
import androidx.navigation.NavType
import androidx.navigation.compose.NavHost
import androidx.navigation.compose.composable
import androidx.navigation.compose.rememberNavController
import androidx.navigation.navArgument
import com.iptv.movies.data.ApiService
import com.iptv.movies.ui.screens.DetailScreen
import com.iptv.movies.ui.screens.HomeScreen

sealed class Dest(val route: String) {
    data object Home : Dest("home")
    data object Detail : Dest("detail/{id}") {
        fun route(id: String) = "detail/$id"
    }
}

@Composable
fun AppNav(api: ApiService, isDark: Boolean, onToggleTheme: () -> Unit) {
    val nav = rememberNavController()
    NavHost(navController = nav, startDestination = Dest.Home.route) {
        composable(Dest.Home.route) {
            HomeScreen(
                api = api,
                isDark = isDark,
                onToggleTheme = onToggleTheme,
                onOpenDetails = { id -> nav.navigate(Dest.Detail.route(id)) }
            )
        }
        composable(
            route = Dest.Detail.route,
            arguments = listOf(navArgument("id") { type = NavType.StringType })
        ) { backStackEntry ->
            val id = backStackEntry.arguments?.getString("id") ?: return@composable
            DetailScreen(api = api, id = id)
        }
    }
}
