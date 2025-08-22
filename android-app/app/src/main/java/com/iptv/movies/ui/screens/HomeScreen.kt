package com.iptv.movies.ui.screens

import androidx.compose.foundation.layout.*
import androidx.compose.foundation.lazy.grid.GridCells
import androidx.compose.foundation.lazy.grid.LazyVerticalGrid
import androidx.compose.foundation.lazy.grid.items
import androidx.compose.foundation.rememberScrollState
import androidx.compose.foundation.verticalScroll
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.DarkMode
import androidx.compose.material.icons.filled.LightMode
import androidx.compose.material3.*
import androidx.compose.material3.ExperimentalMaterial3Api
import androidx.compose.runtime.*
import androidx.compose.runtime.saveable.rememberSaveable
import androidx.compose.ui.Modifier
import androidx.compose.ui.unit.dp
import androidx.lifecycle.ViewModel
import androidx.lifecycle.viewModelScope
import androidx.lifecycle.viewmodel.compose.viewModel
import com.iptv.movies.data.ApiService
import com.iptv.movies.data.Movie
import com.iptv.movies.ui.components.LoadingIndicator
import com.iptv.movies.ui.components.MovieCard
import kotlinx.coroutines.launch
import java.time.LocalDate
import java.time.format.DateTimeFormatter
import java.time.temporal.ChronoUnit
import java.util.Locale

class HomeViewModel(private val api: ApiService) : ViewModel() {
    var isLoading by mutableStateOf(false)
        private set
    var isLoadingMore by mutableStateOf(false)
        private set
    var movies by mutableStateOf<List<Movie>>(emptyList())
        private set
    var error by mutableStateOf<String?>(null)
        private set
    var page by mutableStateOf(1)
        private set
    var pages by mutableStateOf(1)
        private set
    var total by mutableStateOf(0)
        private set
    private var lastQuery: String? = null

    fun refresh(q: String? = null) {
        viewModelScope.launch {
            try {
                isLoading = true
                error = null
                lastQuery = q
                page = 1
                pages = 1
                total = 0
                movies = emptyList()
                val resp = api.listMovies(page = 1, perPage = 20, query = q)
                movies = resp.movies
                page = 1
                pages = resp.pagination.pages
                total = resp.pagination.total
            } catch (e: Exception) {
                error = e.message
            } finally {
                isLoading = false
            }
        }
    }

    fun loadMore() {
        if (isLoading || isLoadingMore) return
        if (page >= pages) return
        viewModelScope.launch {
            try {
                isLoadingMore = true
                error = null
                val next = page + 1
                val resp = api.listMovies(page = next, perPage = 20, query = lastQuery)
                movies = movies + resp.movies
                page = resp.pagination.page
                pages = resp.pagination.pages
                total = resp.pagination.total
            } catch (e: Exception) {
                error = e.message
            } finally {
                isLoadingMore = false
            }
        }
    }

    fun loadAll() {
        if (isLoading || isLoadingMore) return
        if (page >= pages) return
        viewModelScope.launch {
            try {
                isLoadingMore = true
                error = null
                var current = page
                while (current < pages) {
                    val next = current + 1
                    val resp = api.listMovies(page = next, perPage = 20, query = lastQuery)
                    movies = movies + resp.movies
                    current = resp.pagination.page
                    page = current
                    pages = resp.pagination.pages
                    total = resp.pagination.total
                }
            } catch (e: Exception) {
                error = e.message
            } finally {
                isLoadingMore = false
            }
        }
    }
}

@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun HomeScreen(
    api: ApiService,
    isDark: Boolean,
    onToggleTheme: () -> Unit,
    onOpenDetails: (String) -> Unit,
    vm: HomeViewModel = viewModel(factory = object : androidx.lifecycle.ViewModelProvider.Factory {
        override fun <T : ViewModel> create(modelClass: Class<T>): T {
            @Suppress("UNCHECKED_CAST")
            return HomeViewModel(api) as T
        }
    })
) {
    var query by remember { mutableStateOf("") }

    LaunchedEffect(Unit) { vm.refresh() }

    Scaffold(
        topBar = {
            TopAppBar(
                title = { Text("IPTV Movies") },
                actions = {
                    IconButton(onClick = onToggleTheme) {
                        Icon(
                            imageVector = if (isDark) Icons.Filled.DarkMode else Icons.Filled.LightMode,
                            contentDescription = "Toggle theme"
                        )
                    }
                }
            )
        }
    ) { padding ->
        Column(Modifier.padding(padding).padding(12.dp)) {
            OutlinedTextField(
                value = query,
                onValueChange = { query = it },
                modifier = Modifier.fillMaxWidth(),
                placeholder = { Text(text = "Поиск по названию") },
                singleLine = true,
                trailingIcon = {
                    TextButton(onClick = { vm.refresh(query.ifBlank { null }) }) {
                        Text("Найти")
                    }
                }
            )

            Spacer(Modifier.height(12.dp))

            when {
                vm.isLoading -> LoadingIndicator()
                vm.error != null -> Text("Ошибка: ${vm.error}")
                else -> {
                    val sections = remember(vm.movies) { groupByDay(vm.movies) }

                    var selectedKey by rememberSaveable { mutableStateOf<String?>(null) }
                    LaunchedEffect(sections) {
                        if (selectedKey == null || sections.none { it.key == selectedKey }) {
                            selectedKey = sections.firstOrNull { it.date == LocalDate.now() }?.key
                                ?: sections.firstOrNull()?.key
                        }
                    }
                    val selectedSection = sections.find { it.key == selectedKey }

                    var showDateDialog by remember { mutableStateOf(false) }

                    // Панель выбора даты и быстрый переход на Сегодня
                    Row(
                        Modifier.fillMaxWidth(),
                        horizontalArrangement = Arrangement.SpaceBetween
                    ) {
                        TextButton(onClick = { showDateDialog = true }) { Text("Выбрать дату") }

                        selectedSection?.let {
                            Text(text = it.label, style = MaterialTheme.typography.titleMedium)
                        }

                        TextButton(onClick = {
                            val today = sections.firstOrNull { it.date == LocalDate.now() }
                            if (today != null) selectedKey = today.key
                        }) { Text("Сегодня") }
                    }

                    Spacer(Modifier.height(8.dp))

                    // Контент выбранной секции
                    if (selectedSection != null) {
                        Text(
                            text = selectedSection.label,
                            style = MaterialTheme.typography.titleMedium
                        )
                        LazyVerticalGrid(
                            columns = GridCells.Adaptive(140.dp),
                            verticalArrangement = Arrangement.spacedBy(8.dp),
                            horizontalArrangement = Arrangement.spacedBy(8.dp),
                        ) {
                            items(selectedSection.items) { movie ->
                                MovieCard(movie) { onOpenDetails(it.id) }
                            }
                        }
                    } else {
                        Text("Нет данных для выбранной даты")
                    }

                    // Диалог выбора даты
                    if (showDateDialog) {
                        AlertDialog(
                            onDismissRequest = { showDateDialog = false },
                            title = { Text("Выберите дату") },
                            text = {
                                Column(
                                    Modifier
                                        .fillMaxWidth()
                                        .heightIn(max = 400.dp)
                                        .verticalScroll(rememberScrollState())
                                ) {
                                    sections.forEach { s ->
                                        TextButton(
                                            onClick = {
                                                selectedKey = s.key
                                                showDateDialog = false
                                            },
                                            modifier = Modifier.fillMaxWidth()
                                        ) {
                                            Text("${s.label} (${s.items.size})")
                                        }
                                    }
                                }
                            },
                            confirmButton = {
                                TextButton(onClick = { showDateDialog = false }) { Text("Закрыть") }
                            }
                        )
                    }

                    Spacer(Modifier.height(12.dp))

                    // Панель пагинации: прогресс и кнопки
                    Row(Modifier.fillMaxWidth(), horizontalArrangement = Arrangement.Center) {
                        val loaded = vm.movies.size
                        val total = vm.total
                        if (total > 0) {
                            Text("Показано $loaded из $total", modifier = Modifier.padding(end = 12.dp))
                        }
                        if (vm.page < vm.pages) {
                            OutlinedButton(onClick = { vm.loadMore() }, enabled = !vm.isLoadingMore) {
                                Text(if (vm.isLoadingMore) "Загрузка..." else "Показать ещё")
                            }
                            Spacer(Modifier.width(8.dp))
                            TextButton(onClick = { vm.loadAll() }, enabled = !vm.isLoadingMore) {
                                Text("Показать все")
                            }
                        }
                    }
                }
            }
        }
    }
}

private data class Section(
    val key: String,
    val label: String,
    val date: LocalDate?,
    val items: List<Movie>
)

private fun groupByDay(movies: List<Movie>, now: LocalDate = LocalDate.now()): List<Section> {
    val map = LinkedHashMap<String, Section>()
    fun parseDate(m: Movie): LocalDate? {
        val s = m.epg_data?.broadcast_time ?: return null
        val part = if (s.length >= 10) s.substring(0, 10) else s
        return try { LocalDate.parse(part) } catch (e: Exception) { null }
    }
    fun labelFor(d: LocalDate?): String {
        if (d == null) return "Без даты"
        val diff = ChronoUnit.DAYS.between(now, d).toInt()
        return when (diff) {
            0 -> "Сегодня"
            1 -> "Завтра"
            -1 -> "Вчера"
            else -> d.format(DateTimeFormatter.ofPattern("dd MMMM", Locale("ru")))
        }
    }
    fun weight(d: LocalDate?): Int {
        if (d == null) return Int.MAX_VALUE
        val diff = ChronoUnit.DAYS.between(now, d).toInt()
        return when {
            diff == 0 -> -1000
            diff == 1 -> -900
            diff > 1 -> diff
            diff == -1 -> 1000
            diff < -1 -> 1000 - diff
            else -> Int.MAX_VALUE
        }
    }

    for (m in movies) {
        val d = parseDate(m)
        val key = d?.toString() ?: "no-date"
        val exist = map[key]
        if (exist == null) {
            map[key] = Section(key = key, label = labelFor(d), date = d, items = mutableListOf(m))
        } else {
            (exist.items as MutableList).add(m)
        }
    }

    return map.values
        .sortedWith(compareBy({ weight(it.date) }, { it.date ?: LocalDate.MAX }))
        .map { s -> s.copy(items = s.items) }
}
