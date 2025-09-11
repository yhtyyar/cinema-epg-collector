/**
 * Application constants
 */

// API endpoints
export const API_ENDPOINTS = {
    MOVIES: '/movies',
    MOVIE_SEARCH: '/movies/search',
    MOVIE_DETAIL: (id: string | number) => `/movies/${id}`,
    GENRES: '/genres'
} as const;

// Query keys for React Query
export const QUERY_KEYS = {
    MOVIES: 'movies',
    MOVIE: 'movie',
    GENRES: 'genres'
} as const;

// Local storage keys
export const STORAGE_KEYS = {
    THEME: 'theme',
    SEARCH_HISTORY: 'searchHistory'
} as const;

// Default values
export const DEFAULTS = {
    PAGE_SIZE: 20,
    MOVIE_PAGE_SIZE: 200,
    CACHE_TIMES: {
        MOVIES: 5 * 60 * 1000, // 5 minutes
        MOVIE: 10 * 60 * 1000, // 10 minutes
        GENRES: 30 * 60 * 1000 // 30 minutes
    }
} as const;

// Rating thresholds
export const RATING_THRESHOLDS = {
    HIGH: 7,
    MEDIUM: 5
} as const;

// Age ratings
export const AGE_RATINGS = {
    ALL: '0+',
    CHILDREN: '6+',
    TEEN: '12+',
    YOUNG_ADULT: '16+',
    ADULT: '18+'
} as const;