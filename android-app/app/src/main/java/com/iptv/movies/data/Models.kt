package com.iptv.movies.data

// Модели под формат FastAPI

data class EpgData(
    val title: String? = null,
    val description: String? = null,
    val broadcast_time: String? = null,
    val preview_image: String? = null,
)

data class KinoData(
    val title: String? = null,
    val original_title: String? = null,
    val year: Int? = null,
    val rating: Double? = null,
    val description: String? = null,
    val poster_url: String? = null,
    val genres: List<String>? = null,
    val duration: Int? = null,
)

data class Metadata(
    val created_at: String? = null,
    val updated_at: String? = null,
    val source: String? = null,
)

data class Movie(
    val id: String,
    val epg_data: EpgData?,
    val kinopoisk_data: KinoData?,
    val metadata: Metadata,
)

data class Pagination(
    val page: Int,
    val per_page: Int,
    val total: Int,
    val pages: Int,
)

data class MoviesResponse(
    val movies: List<Movie>,
    val pagination: Pagination,
)
