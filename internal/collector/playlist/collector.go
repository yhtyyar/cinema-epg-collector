package playlist

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

func (c *Collector) CollectPlaylist() error {
	logger.Info("Starting playlist collection...")

	var response models.PlaylistResponse
	err := c.client.GetJSON(c.config.PlaylistURL, &response)
	if err != nil {
		return fmt.Errorf("failed to fetch playlist: %w", err)
	}

	logger.Infof("Received %d channels from playlist API", len(response.Channels))

	for _, channelData := range response.Channels {
		err := c.processChannel(channelData)
		if err != nil {
			logger.Errorf("Failed to process channel %s: %v", channelData.Name, err)
			continue
		}
	}

	logger.Info("Playlist collection completed successfully")
	return nil
}

func (c *Collector) processChannel(channelData models.ChannelData) error {
	// Check if channel already exists
	existingChannel, err := c.db.GetChannelByExternalID(channelData.ID)
	if err == nil {
		// Channel exists, update it
		return c.updateChannel(existingChannel, channelData)
	}

	// Channel doesn't exist, create new one
	return c.createChannel(channelData)
}

func (c *Collector) createChannel(channelData models.ChannelData) error {
	channel := &models.Channel{
		ExternalID: channelData.ID,
		Name:       channelData.Name,
		IconURL:    channelData.Icon,
		Category:   channelData.Category,
		CreatedAt:  time.Now(),
		UpdatedAt:  time.Now(),
	}

	err := c.db.CreateChannel(channel)
	if err != nil {
		return fmt.Errorf("failed to create channel: %w", err)
	}

	// Create stream URLs
	for i, url := range channelData.URLs {
		streamURL := &models.StreamURL{
			ChannelID: channel.ID,
			URL:       url,
			Quality:   fmt.Sprintf("stream_%d", i+1),
			Type:      "hls", // Assuming HLS for now
		}

		err := c.db.CreateStreamURL(streamURL)
		if err != nil {
			logger.Errorf("Failed to create stream URL for channel %s: %v", channel.Name, err)
		}
	}

	logger.Debugf("Created new channel: %s (ID: %s)", channel.Name, channel.ExternalID)
	return nil
}

func (c *Collector) updateChannel(existingChannel *models.Channel, channelData models.ChannelData) error {
	// Update channel info
	existingChannel.Name = channelData.Name
	existingChannel.IconURL = channelData.Icon
	existingChannel.Category = channelData.Category
	existingChannel.UpdatedAt = time.Now()

	err := c.db.UpdateChannel(existingChannel)
	if err != nil {
		return fmt.Errorf("failed to update channel: %w", err)
	}

	// Delete existing stream URLs and create new ones
	err = c.db.DeleteStreamURLsByChannelID(existingChannel.ID)
	if err != nil {
		logger.Errorf("Failed to delete old stream URLs for channel %s: %v", existingChannel.Name, err)
	}

	// Create new stream URLs
	for i, url := range channelData.URLs {
		streamURL := &models.StreamURL{
			ChannelID: existingChannel.ID,
			URL:       url,
			Quality:   fmt.Sprintf("stream_%d", i+1),
			Type:      "hls", // Assuming HLS for now
		}

		err := c.db.CreateStreamURL(streamURL)
		if err != nil {
			logger.Errorf("Failed to create stream URL for channel %s: %v", existingChannel.Name, err)
		}
	}

	logger.Debugf("Updated channel: %s (ID: %s)", existingChannel.Name, existingChannel.ExternalID)
	return nil
}

func (c *Collector) GetChannelCount() (int64, error) {
	var count int64
	err := c.db.DB.Model(&models.Channel{}).Count(&count).Error
	return count, err
}
