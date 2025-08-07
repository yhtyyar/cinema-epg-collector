package epg

import (
	"fmt"
	"time"
	"cinema-epg-collector/internal/config"
	"cinema-epg-collector/internal/models"
	"cinema-epg-collector/internal/storage/postgres"
	"cinema-epg-collector/pkg/httpclient"
	"cinema-epg-collector/pkg/logger"
)

type Collector struct {
	client   *httpclient.Client
	db       *postgres.Database
	config   *config.APIConfig
}

func NewCollector(cfg *config.APIConfig, db *postgres.Database) *Collector {
	client := httpclient.NewClient(
		time.Duration(cfg.Timeout)*time.Second,
		cfg.Headers,
	)

	return &Collector{
		client: client,
		db:     db,
		config: cfg,
	}
}

func (c *Collector) CollectEPGForChannel(channelID string, timezone int) error {
	logger.Infof("Collecting EPG for channel ID: %s", channelID)

	// Build EPG URL with parameters
	epgURL := fmt.Sprintf("%s?id=%s&tz=%d&epg_from=0&epg_limit=100&grouping=1&region=77&lang=ru",
		c.config.EPGURL, channelID, timezone)

	var response models.EPGResponse
	err := c.client.GetJSON(epgURL, &response)
	if err != nil {
		return fmt.Errorf("failed to fetch EPG for channel %s: %w", channelID, err)
	}

	logger.Infof("Received %d programs for channel %s", len(response.Programs), channelID)

	// Get channel from database
	channel, err := c.db.GetChannelByExternalID(channelID)
	if err != nil {
		return fmt.Errorf("channel %s not found in database: %w", channelID, err)
	}

	for _, programData := range response.Programs {
		err := c.processProgram(channel.ID, programData)
		if err != nil {
			logger.Errorf("Failed to process program %s: %v", programData.Title, err)
			continue
		}
	}

	logger.Infof("EPG collection completed for channel %s", channelID)
	return nil
}

func (c *Collector) CollectEPGForAllChannels(timezone int) error {
	logger.Info("Starting EPG collection for all channels...")

	channels, err := c.db.GetAllChannels()
	if err != nil {
		return fmt.Errorf("failed to get channels: %w", err)
	}

	logger.Infof("Found %d channels to collect EPG for", len(channels))

	successCount := 0
	errorCount := 0

	for _, channel := range channels {
		err := c.CollectEPGForChannel(channel.ExternalID, timezone)
		if err != nil {
			logger.Errorf("Failed to collect EPG for channel %s: %v", channel.Name, err)
			errorCount++
		} else {
			successCount++
		}

		// Add small delay to avoid overwhelming the API
		time.Sleep(100 * time.Millisecond)
	}

	logger.Infof("EPG collection completed. Success: %d, Errors: %d", successCount, errorCount)
	return nil
}

func (c *Collector) processProgram(channelID uint, programData models.ProgramData) error {
	// Convert Unix timestamps to time.Time
	startTime := time.Unix(programData.StartTime, 0)
	endTime := time.Unix(programData.EndTime, 0)

	// Calculate duration in minutes
	duration := int(endTime.Sub(startTime).Minutes())

	program := &models.EPGProgram{
		ChannelID:   channelID,
		ExternalID:  programData.ID,
		Title:       programData.Title,
		Description: programData.Description,
		StartTime:   startTime,
		EndTime:     endTime,
		Duration:    duration,
		Category:    programData.Category,
		Genre:       programData.Genre,
		AgeRating:   programData.AgeRating,
		Year:        programData.Year,
		Rating:      programData.Rating,
		PosterURL:   programData.PosterURL,
		CreatedAt:   time.Now(),
		UpdatedAt:   time.Now(),
	}

	err := c.db.CreateEPGProgram(program)
	if err != nil {
		return fmt.Errorf("failed to create EPG program: %w", err)
	}

	logger.Debugf("Created EPG program: %s (Channel ID: %d)", program.Title, channelID)
	return nil
}

func (c *Collector) GetProgramCount() (int64, error) {
	var count int64
	err := c.db.DB.Model(&models.EPGProgram{}).Count(&count).Error
	return count, err
}

func (c *Collector) GetProgramsByTimeRange(channelID uint, startTime, endTime time.Time) ([]models.EPGProgram, error) {
	var programs []models.EPGProgram
	err := c.db.DB.Where("channel_id = ? AND start_time >= ? AND end_time <= ?", 
		channelID, startTime, endTime).
		Order("start_time ASC").
		Find(&programs).Error
	return programs, err
}
