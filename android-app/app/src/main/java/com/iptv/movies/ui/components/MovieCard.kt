package com.iptv.movies.ui.components

import androidx.compose.foundation.clickable
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.height
import androidx.compose.foundation.layout.padding
import androidx.compose.material3.Card
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.runtime.remember
import androidx.compose.ui.Modifier
import androidx.compose.ui.text.style.TextOverflow
import androidx.compose.ui.unit.dp
import coil.compose.AsyncImage
import com.iptv.movies.data.Movie
import com.iptv.movies.data.buildPosterUrl
import java.time.LocalDateTime
import java.time.OffsetDateTime
import java.time.ZoneId
import java.time.format.DateTimeFormatter

@Composable
fun MovieCard(movie: Movie, onClick: (Movie) -> Unit) {
    Card(
        modifier = Modifier
            .fillMaxWidth()
            .clickable { onClick(movie) }
    ) {
        val poster = buildPosterUrl(movie.kinopoisk_data?.poster_url ?: movie.epg_data?.preview_image)
        AsyncImage(
            model = poster,
            contentDescription = movie.kinopoisk_data?.title ?: movie.epg_data?.title,
            modifier = Modifier
                .fillMaxWidth()
                .height(180.dp)
        )
        Column(Modifier.padding(8.dp)) {
            Text(
                text = movie.kinopoisk_data?.title ?: movie.epg_data?.title ?: "",
                style = MaterialTheme.typography.titleMedium,
                maxLines = 1,
                overflow = TextOverflow.Ellipsis
            )

            val timeText = remember(movie.epg_data?.broadcast_time) {
                formatBroadcastTimeMsk(movie.epg_data?.broadcast_time)
            }
            if (timeText != null) {
                Text(text = "$timeText МСК", style = MaterialTheme.typography.bodySmall)
            }
            val rating = movie.kinopoisk_data?.rating
            if (rating != null) {
                Text(text = "★ %.1f".format(rating))
            }
        }
    }
}

private fun formatBroadcastTimeMsk(raw: String?): String? {
    if (raw.isNullOrBlank()) return null
    // Попытка 1: c временной зоной/смещением
    runCatching {
        val odt = OffsetDateTime.parse(raw)
        val zdt = odt.atZoneSameInstant(ZoneId.of("Europe/Moscow"))
        return DateTimeFormatter.ofPattern("HH:mm").format(zdt)
    }
    // Попытка 2: ISO_LOCAL_DATE_TIME ("yyyy-MM-dd'T'HH:mm[:ss]")
    runCatching {
        val norm = raw.replace(' ', 'T')
        val ldt = LocalDateTime.parse(norm)
        return DateTimeFormatter.ofPattern("HH:mm").format(ldt)
    }
    // Попытка 3: "yyyy-MM-dd HH:mm:ss"
    runCatching {
        val fmt = DateTimeFormatter.ofPattern("yyyy-MM-dd HH:mm:ss")
        val ldt = LocalDateTime.parse(raw, fmt)
        return DateTimeFormatter.ofPattern("HH:mm").format(ldt)
    }
    // Попытка 4: "yyyy-MM-dd'T'HH:mm:ss"
    runCatching {
        val fmt = DateTimeFormatter.ofPattern("yyyy-MM-dd'T'HH:mm:ss")
        val ldt = LocalDateTime.parse(raw, fmt)
        return DateTimeFormatter.ofPattern("HH:mm").format(ldt)
    }
    // Попытка 5: "yyyy-MM-dd'T'HH:mm"
    runCatching {
        val fmt = DateTimeFormatter.ofPattern("yyyy-MM-dd'T'HH:mm")
        val ldt = LocalDateTime.parse(raw, fmt)
        return DateTimeFormatter.ofPattern("HH:mm").format(ldt)
    }
    // Попытка 6: "yyyy-MM-dd HH:mm"
    runCatching {
        val fmt = DateTimeFormatter.ofPattern("yyyy-MM-dd HH:mm")
        val ldt = LocalDateTime.parse(raw, fmt)
        return DateTimeFormatter.ofPattern("HH:mm").format(ldt)
    }
    return null
}
