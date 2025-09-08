// types/movie-new.ts
export interface EPGData {
  title: string;
  description: string;
  broadcast_time: string;
  preview_image: string;
}

export interface TMDBData {
  title: string;
  original_title?: string;
  year?: number;
  rating?: number;
  description?: string;
  poster_url?: string;
  genres?: string[];
  duration?: number;
}

export interface MovieMetadata {
  created_at?: string;
  updated_at?: string;
  source: string;
}

export interface Movie {
  id: string;
  epg_data: EPGData;
  tmdb_data?: TMDBData;
  metadata: MovieMetadata;
}

export interface MoviesResponse {
  movies: Movie[];
  pagination: {
    page: number;
    per_page: number;
    total: number;
    pages: number;
  };
}

export interface MoviesByDate {
  [date: string]: Movie[];
}

export interface DateOption {
  date: string;
  displayDate: string;
  isToday: boolean;
  count: number;
}
