package postgres

import (
	"fmt"
	"cinema-epg-collector/internal/config"
	"cinema-epg-collector/internal/models"
	"cinema-epg-collector/pkg/logger"
	
	"gorm.io/driver/postgres"
	"gorm.io/gorm"
)

type Database struct {
	DB *gorm.DB
}

func NewDatabase(cfg *config.DatabaseConfig) (*Database, error) {
	dsn := fmt.Sprintf("host=%s port=%d user=%s password=%s dbname=%s sslmode=%s",
		cfg.Host, cfg.Port, cfg.User, cfg.Password, cfg.DBName, cfg.SSLMode)

	db, err := gorm.Open(postgres.Open(dsn), &gorm.Config{})
	if err != nil {
		return nil, fmt.Errorf("failed to connect to database: %w", err)
	}

	logger.Info("Connected to PostgreSQL database")

	return &Database{DB: db}, nil
}

func (d *Database) AutoMigrate() error {
	err := d.DB.AutoMigrate(
		&models.Channel{},
		&models.StreamURL{},
		&models.EPGProgram{},
		&models.User{},
	)
	if err != nil {
		return fmt.Errorf("failed to auto-migrate: %w", err)
	}

	logger.Info("Database migration completed successfully")
	return nil
}

func (d *Database) Close() error {
	sqlDB, err := d.DB.DB()
	if err != nil {
		return err
	}
	return sqlDB.Close()
}

// Channel operations
func (d *Database) CreateChannel(channel *models.Channel) error {
	return d.DB.Create(channel).Error
}

func (d *Database) GetChannelByExternalID(externalID string) (*models.Channel, error) {
	var channel models.Channel
	err := d.DB.Preload("StreamURLs").Where("external_id = ?", externalID).First(&channel).Error
	return &channel, err
}

func (d *Database) UpdateChannel(channel *models.Channel) error {
	return d.DB.Save(channel).Error
}

func (d *Database) GetAllChannels() ([]models.Channel, error) {
	var channels []models.Channel
	err := d.DB.Preload("StreamURLs").Find(&channels).Error
	return channels, err
}

// EPG operations
func (d *Database) CreateEPGProgram(program *models.EPGProgram) error {
	return d.DB.Create(program).Error
}

func (d *Database) GetEPGByChannelID(channelID uint, limit int) ([]models.EPGProgram, error) {
	var programs []models.EPGProgram
	err := d.DB.Where("channel_id = ?", channelID).
		Order("start_time ASC").
		Limit(limit).
		Find(&programs).Error
	return programs, err
}

func (d *Database) CreateStreamURL(streamURL *models.StreamURL) error {
	return d.DB.Create(streamURL).Error
}

func (d *Database) DeleteStreamURLsByChannelID(channelID uint) error {
	return d.DB.Where("channel_id = ?", channelID).Delete(&models.StreamURL{}).Error
}
