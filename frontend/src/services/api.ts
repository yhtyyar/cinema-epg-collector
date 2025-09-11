import axios, { AxiosError, AxiosRequestConfig } from 'axios';
import {
  Genre,
  Movie,
  PagedResponse,
  MovieDTO,
  MoviesResponseDTO,
  TMDBData,
  EPGData
} from '../types/movie';
import { API_ENDPOINTS, DEFAULTS } from '../lib/constants';
import { ApiError, NetworkError } from '../lib/errors';

// Базовый URL для API запросов
const baseURL = import.meta.env.VITE_API_BASE_URL ?? '/api';

// Создаем экземпляр axios с базовой конфигурацией
export const api = axios.create({
  baseURL,
  timeout: 15000, // Увеличили таймаут для медленных запросов
  headers: {
    'Accept': 'application/json',
    'Content-Type': 'application/json'
  }
});

// Перехватчик ответов: нормализация ошибок и логирование
api.interceptors.response.use(
  (response) => {
    // Логируем успешные запросы в режиме разработки
    if (import.meta.env.DEV) {
      console.log(`✅ API ${response.config.method?.toUpperCase()} ${response.config.url}:`, response.status);
    }
    return response;
  },
  (error: AxiosError) => {
    // Извлекаем информацию об ошибке
    const status = error?.response?.status ?? 0;
    const message = (error?.response?.data as any)?.detail ||
      (error?.response?.data as any)?.message ||
      error?.message ||
      'Ошибка сети';
    const details = error?.response?.data;

    // Логируем ошибки в режиме разработки
    if (import.meta.env.DEV) {
      console.error(`❌ API Error ${status}:`, message, details);
    }

    // Создаем расширенный объект ошибки
    return Promise.reject(new ApiError(message, status, details));
  }
);

/**
 * Адаптер для преобразования данных фильма из формата бэкенда в формат фронтенда
 * Правильно обрабатывает структуру epg_data и tmdb_data
 */
function adaptMovie(dto: MovieDTO): Movie {
  // Извлекаем данные из правильных полей бэкенда
  const tmdb: TMDBData = dto?.tmdb_data ?? {};
  const epg: EPGData = dto?.epg_data ?? {};

  // Приоритет названия: TMDB -> EPG -> fallback
  const title = tmdb.title || epg.title || 'Без названия';

  // Приоритет описания: TMDB -> EPG -> пустая строка
  const overview = tmdb.description || epg.description || '';

  // Приоритет постера: TMDB -> EPG preview -> пустая строка
  const poster_url = tmdb.poster_url || epg.preview_image || '';

  // Извлекаем остальные поля из TMDB данных
  const year = tmdb.year ?? undefined;
  const rating = tmdb.rating ?? undefined;
  const duration = tmdb.duration ?? undefined;
  const original_title = tmdb.original_title ?? undefined;

  // Преобразуем жанры из массива строк в массив объектов Genre
  const genresSrc: string[] = Array.isArray(tmdb.genres) ? tmdb.genres : [];
  const genres: Genre[] = genresSrc.map((name, idx) => ({
    id: idx + 1,
    name
  }));

  // Извлекаем метаданные
  const source: string | undefined = dto?.metadata?.source || undefined;
  const broadcast_time: string | undefined = epg?.broadcast_time || undefined;

  // Определяем возрастной рейтинг на основе рейтинга фильма
  const getAgeRating = (rating?: number): string => {
    if (!rating) return '18+';
    if (rating >= 8) return '6+';
    if (rating >= 7) return '12+';
    if (rating >= 5) return '16+';
    return '18+';
  };

  return {
    id: String(dto?.id ?? ''),
    title,
    original_title,
    overview,
    year,
    rating,
    duration,
    genres,
    poster_url,
    source,
    broadcast_time,
    age_rating: getAgeRating(rating),
  };
}

interface FetchMoviesParams {
  page?: number;
  size?: number;
  genre?: number | string;
  year?: number | string;
  rating?: number | string;
  q?: string;
}

/**
 * Получение списка фильмов с сервера с поддержкой фильтрации и поиска
 * Правильно обрабатывает структуру ответа бэкенда MoviesResponseDTO
 */
export async function fetchMovies(
  params: FetchMoviesParams,
  signal?: AbortSignal
): Promise<PagedResponse<Movie>> {
  const { page = 1, size = DEFAULTS.PAGE_SIZE, genre, year, rating, q } = params;

  // Выбираем правильный эндпоинт в зависимости от наличия поискового запроса
  const path = q ? API_ENDPOINTS.MOVIE_SEARCH : API_ENDPOINTS.MOVIES;

  // Формируем параметры запроса согласно API бэкенда
  const requestParams = q
    ? { q, page, per_page: size }
    : {
      page,
      per_page: size,
      ...(genre && { genre }),
      ...(year && { year }),
      ...(rating && { rating_gte: rating })
    };

  try {
    // Выполняем запрос с типизированным ответом
    const { data } = await api.get<MoviesResponseDTO>(path, {
      params: requestParams,
      signal
    });

    // Проверяем структуру ответа и адаптируем данные
    const movies = Array.isArray(data?.movies) ? data.movies.map(adaptMovie) : [];
    const pagination = data?.pagination || {
      total: movies.length,
      page,
      per_page: size,
      pages: 1
    };

    // Преобразуем в формат фронтенда
    const mapped: PagedResponse<Movie> = {
      items: movies,
      total: Number(pagination.total ?? movies.length),
      page: Number(pagination.page ?? page),
      size: Number(pagination.per_page ?? size),
    };

    return mapped;
  } catch (error) {
    // Логируем ошибку и пробрасываем дальше
    console.error('Ошибка при получении списка фильмов:', error);
    throw error;
  }
}

/**
 * Получение детальной информации о фильме по ID
 */
export async function fetchMovie(id: string | number, signal?: AbortSignal): Promise<Movie> {
  try {
    const { data } = await api.get<MovieDTO>(API_ENDPOINTS.MOVIE_DETAIL(id), { signal });
    return adaptMovie(data);
  } catch (error) {
    console.error(`Ошибка при получении фильма ${id}:`, error);
    throw error;
  }
}

/**
 * Получение списка всех доступных жанров
 * Собирает жанры из первых 200 фильмов для формирования списка фильтров
 */
export async function fetchGenres(signal?: AbortSignal): Promise<Genre[]> {
  try {
    // Получаем расширенную первую страницу для сбора жанров
    const { data } = await api.get<MoviesResponseDTO>(API_ENDPOINTS.MOVIES, {
      params: { page: 1, per_page: DEFAULTS.MOVIE_PAGE_SIZE },
      signal
    });

    const movies: MovieDTO[] = Array.isArray(data?.movies) ? data.movies : [];
    const genresSet = new Set<string>();

    // Собираем уникальные жанры из TMDB данных
    for (const movie of movies) {
      const tmdbGenres: string[] = movie?.tmdb_data?.genres || [];
      tmdbGenres.forEach((genre) => {
        if (genre && genre.trim()) {
          genresSet.add(genre.trim());
        }
      });
    }

    // Преобразуем в массив объектов Genre и сортируем по алфавиту
    const result: Genre[] = Array.from(genresSet)
      .sort((a, b) => a.localeCompare(b, 'ru'))
      .map((name, idx) => ({ id: idx + 1, name }));

    return result;
  } catch (error) {
    console.error('Ошибка при получении жанров:', error);
    // Возвращаем пустой массив в случае ошибки
    return [];
  }
}