package com.iptv.movies.ui.screens

import androidx.compose.foundation.layout.*
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.runtime.LaunchedEffect
import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.remember
import androidx.compose.runtime.setValue
import androidx.compose.ui.Modifier
import androidx.compose.ui.unit.dp
import androidx.lifecycle.ViewModel
import androidx.lifecycle.viewmodel.compose.viewModel
import androidx.lifecycle.viewModelScope
import coil.compose.AsyncImage
import com.iptv.movies.data.ApiService
import com.iptv.movies.data.Movie
import com.iptv.movies.data.buildPosterUrl
import kotlinx.coroutines.launch

class DetailViewModel(private val api: ApiService) : ViewModel() {
    var movie by mutableStateOf<Movie?>(null)
        private set
    var isLoading by mutableStateOf(false)
        private set
    var error by mutableStateOf<String?>(null)
        private set

    fun load(id: String) {
        viewModelScope.launch {
            try {
                isLoading = true
                error = null
                movie = api.getMovie(id)
            } catch (e: Exception) {
                error = e.message
            } finally {
                isLoading = false
            }
        }
    }
}

@Composable
fun DetailScreen(api: ApiService, id: String, vm: DetailViewModel = viewModel(factory = object : androidx.lifecycle.ViewModelProvider.Factory {
    override fun <T : ViewModel> create(modelClass: Class<T>): T {
        @Suppress("UNCHECKED_CAST")
        return DetailViewModel(api) as T
    }
})) {
    LaunchedEffect(id) { vm.load(id) }

    val m = vm.movie
    if (vm.isLoading) {
        Text("Загрузка...", modifier = Modifier.padding(16.dp))
        return
    }
    if (vm.error != null) {
        Text("Ошибка: ${vm.error}", modifier = Modifier.padding(16.dp))
        return
    }
    if (m == null) return

    val title = m.kinopoisk_data?.title ?: m.epg_data?.title ?: ""
    val rating = m.kinopoisk_data?.rating
    val desc = m.kinopoisk_data?.description ?: m.epg_data?.description ?: ""
    val year = m.kinopoisk_data?.year
    val genres = m.kinopoisk_data?.genres?.joinToString()
    val poster = buildPosterUrl(m.kinopoisk_data?.poster_url ?: m.epg_data?.preview_image)

    Column(Modifier.padding(16.dp)) {
        AsyncImage(model = poster, contentDescription = title, modifier = Modifier.fillMaxWidth().height(300.dp))
        Spacer(Modifier.height(12.dp))
        Text(text = title, style = MaterialTheme.typography.headlineSmall)
        if (rating != null) Text(text = "★ %.1f".format(rating), style = MaterialTheme.typography.titleMedium)
        if (year != null) Text(text = "Год: $year")
        if (!genres.isNullOrBlank()) Text(text = "Жанры: $genres")
        Spacer(Modifier.height(8.dp))
        Text(text = desc)
    }
}
