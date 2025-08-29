# IPTV Movies (Android MVP)

Минимальное Android-приложение (Kotlin + Jetpack Compose) для показа фильмов из локального API `cinema-epg-collector`.

## Стек
- Single-Activity + Navigation Compose
- ViewModel (androidx.lifecycle)
- Retrofit + Moshi
- Coil для изображений
- Material 3, темная тема по умолчанию с переключателем

## Локальный запуск
1. Запустите API:
   - В корне репо:
     ```bash
     uvicorn epg_collector.api.app:app --host 0.0.0.0 --port 8000 --reload
     ```
     Эндпоинты:
     - GET `http://localhost:8000/api/movies?page=1&per_page=20&q=...`
     - GET `http://localhost:8000/api/movies/{id}`
2. Откройте папку `android-app/` в Android Studio.
3. Дождитесь синхронизации Gradle и запустите на эмуляторе.
   - Эмулятор обращается к локальному хосту по адресу `http://10.0.2.2:8000/` (уже настроено в коде).

## Структура
```
android-app/
  ├─ settings.gradle.kts
  ├─ build.gradle.kts
  └─ app/
     ├─ build.gradle.kts
     ├─ src/main/AndroidManifest.xml
     ├─ src/main/res/values/strings.xml
     └─ src/main/java/com/iptv/movies/
        ├─ MainActivity.kt
        ├─ data/
        │  ├─ ApiService.kt
        │  └─ Models.kt
        ├─ navigation/Navigation.kt
        └─ ui/
           ├─ theme/{Theme.kt, Color.kt}
           ├─ components/{MovieCard.kt, LoadingIndicator.kt}
           └─ screens/{HomeScreen.kt, DetailScreen.kt}
```

## Примечания
- Пагинации, избранного и кэша нет — MVP.
- Для постеров используется `kinopoisk_data.poster_url`, либо `epg_data.preview_image`. Если путь относительный (например, `/static/...`), он преобразуется к `http://10.0.2.2:8000/...`.
