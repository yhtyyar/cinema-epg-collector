from __future__ import annotations

from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, Field


class EPGData(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    broadcast_time: Optional[str] = None  # ISO8601
    preview_image: Optional[str] = None


class KinoData(BaseModel):
    title: Optional[str] = None
    original_title: Optional[str] = None
    year: Optional[int] = None
    rating: Optional[float] = None
    description: Optional[str] = None
    poster_url: Optional[str] = None
    genres: Optional[List[str]] = None
    duration: Optional[int] = None


class Metadata(BaseModel):
    created_at: Optional[str] = None
    updated_at: Optional[str] = None
    source: Optional[str] = None


class Movie(BaseModel):
    id: str = Field(..., description="Уникальный идентификатор")
    epg_data: EPGData
    kinopoisk_data: Optional[KinoData] = None
    metadata: Metadata


class Pagination(BaseModel):
    page: int
    per_page: int
    total: int
    pages: int


class MoviesResponse(BaseModel):
    movies: List[Movie]
    pagination: Pagination


class ErrorResponse(BaseModel):
    detail: str
