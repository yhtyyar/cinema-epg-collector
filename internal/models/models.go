package models

import (
	"time"
	"gorm.io/gorm"
)

// Channel represents a TV channel
type Channel struct {
	ID          uint      `json:"id" gorm:"primaryKey"`
	ExternalID  string    `json:"external_id" gorm:"uniqueIndex;not null"`
	Name        string    `json:"name" gorm:"not null"`
	IconURL     string    `json:"icon_url"`
	StreamURLs  []StreamURL `json:"stream_urls" gorm:"foreignKey:ChannelID"`
	Category    string    `json:"category"`
	CreatedAt   time.Time `json:"created_at"`
	UpdatedAt   time.Time `json:"updated_at"`
}

// StreamURL represents streaming URLs for a channel
type StreamURL struct {
	ID        uint   `json:"id" gorm:"primaryKey"`
	ChannelID uint   `json:"channel_id"`
	URL       string `json:"url" gorm:"not null"`
	Quality   string `json:"quality"`
	Type      string `json:"type"` // hls, dash, etc.
}

// EPGProgram represents an EPG program entry
type EPGProgram struct {
	ID          uint      `json:"id" gorm:"primaryKey"`
	ChannelID   uint      `json:"channel_id"`
	Channel     Channel   `json:"channel" gorm:"foreignKey:ChannelID"`
	ExternalID  string    `json:"external_id"`
	Title       string    `json:"title" gorm:"not null"`
	Description string    `json:"description"`
	StartTime   time.Time `json:"start_time" gorm:"index"`
	EndTime     time.Time `json:"end_time" gorm:"index"`
	Duration    int       `json:"duration"` // in minutes
	Category    string    `json:"category"`
	Genre       string    `json:"genre"`
	AgeRating   string    `json:"age_rating"`
	Year        int       `json:"year"`
	Rating      float32   `json:"rating"`
	PosterURL   string    `json:"poster_url"`
	CreatedAt   time.Time `json:"created_at"`
	UpdatedAt   time.Time `json:"updated_at"`
}

// User represents a system user
type User struct {
	ID           uint      `json:"id" gorm:"primaryKey"`
	Username     string    `json:"username" gorm:"uniqueIndex;not null"`
	Email        string    `json:"email" gorm:"uniqueIndex;not null"`
	PasswordHash string    `json:"-" gorm:"not null"`
	Role         string    `json:"role" gorm:"default:user"` // admin, moderator, user
	CreatedAt    time.Time `json:"created_at"`
	UpdatedAt    time.Time `json:"updated_at"`
	DeletedAt    gorm.DeletedAt `json:"-" gorm:"index"`
}

// PlaylistResponse represents the API response structure for playlist
type PlaylistResponse struct {
	Status   string    `json:"status"`
	Channels []ChannelData `json:"channels"`
}

// ChannelData represents channel data from playlist API
type ChannelData struct {
	ID       string   `json:"id"`
	Name     string   `json:"name"`
	Icon     string   `json:"icon"`
	Category string   `json:"category"`
	URLs     []string `json:"urls"`
}

// EPGResponse represents the API response structure for EPG
type EPGResponse struct {
	Status   string        `json:"status"`
	Programs []ProgramData `json:"programs"`
}

// ProgramData represents program data from EPG API
type ProgramData struct {
	ID          string `json:"id"`
	Title       string `json:"title"`
	Description string `json:"description"`
	StartTime   int64  `json:"start_time"`
	EndTime     int64  `json:"end_time"`
	Category    string `json:"category"`
	Genre       string `json:"genre"`
	AgeRating   string `json:"age_rating"`
	Year        int    `json:"year"`
	Rating      float32 `json:"rating"`
	PosterURL   string `json:"poster_url"`
}
