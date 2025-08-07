package main

import (
	"context"
	"fmt"
	"net/http"
	"os"
	"os/signal"
	"syscall"
	"time"

	"cinema-epg-collector/internal/config"
	"cinema-epg-collector/internal/collector/playlist"
	"cinema-epg-collector/internal/collector/epg"
	"cinema-epg-collector/internal/storage/postgres"
	"cinema-epg-collector/pkg/logger"

	"github.com/gin-gonic/gin"
	"github.com/robfig/cron/v3"
)

func main() {
	// Load configuration
	cfg, err := config.LoadConfig()
	if err != nil {
		fmt.Printf("Failed to load config: %v\n", err)
		os.Exit(1)
	}

	// Initialize logger
	logger.InitLogger(cfg.Logging.Level, cfg.Logging.Format)
	logger.Info("Starting CinemaEPGCollector service...")

	// Initialize database
	db, err := postgres.NewDatabase(&cfg.Database)
	if err != nil {
		logger.Fatalf("Failed to connect to database: %v", err)
	}
	defer db.Close()

	// Run database migrations
	if err := db.AutoMigrate(); err != nil {
		logger.Fatalf("Failed to run database migrations: %v", err)
	}

	// Initialize collectors
	playlistCollector := playlist.NewCollector(&cfg.API, db)
	epgCollector := epg.NewCollector(&cfg.API, db)

	// Setup cron scheduler
	c := cron.New()
	
	// Schedule playlist collection daily at 6:00 AM
	_, err = c.AddFunc("0 6 * * *", func() {
		logger.Info("Running scheduled playlist collection...")
		if err := playlistCollector.CollectPlaylist(); err != nil {
			logger.Errorf("Scheduled playlist collection failed: %v", err)
		}
	})
	if err != nil {
		logger.Errorf("Failed to schedule playlist collection: %v", err)
	}

	// Schedule EPG collection every 2 hours
	_, err = c.AddFunc("0 */2 * * *", func() {
		logger.Info("Running scheduled EPG collection...")
		if err := epgCollector.CollectEPGForAllChannels(3); err != nil { // timezone +3 for Moscow
			logger.Errorf("Scheduled EPG collection failed: %v", err)
		}
	})
	if err != nil {
		logger.Errorf("Failed to schedule EPG collection: %v", err)
	}

	// Start cron scheduler
	c.Start()
	defer c.Stop()

	// Setup HTTP server
	router := setupRoutes(playlistCollector, epgCollector, db)
	
	srv := &http.Server{
		Addr:         fmt.Sprintf("%s:%s", cfg.Server.Host, cfg.Server.Port),
		Handler:      router,
		ReadTimeout:  time.Duration(cfg.Server.ReadTimeout) * time.Second,
		WriteTimeout: time.Duration(cfg.Server.WriteTimeout) * time.Second,
	}

	// Start server in a goroutine
	go func() {
		logger.Infof("Server starting on %s:%s", cfg.Server.Host, cfg.Server.Port)
		if err := srv.ListenAndServe(); err != nil && err != http.ErrServerClosed {
			logger.Fatalf("Failed to start server: %v", err)
		}
	}()

	// Run initial data collection
	go func() {
		logger.Info("Running initial playlist collection...")
		if err := playlistCollector.CollectPlaylist(); err != nil {
			logger.Errorf("Initial playlist collection failed: %v", err)
		} else {
			// After playlist collection, collect EPG
			logger.Info("Running initial EPG collection...")
			if err := epgCollector.CollectEPGForAllChannels(3); err != nil {
				logger.Errorf("Initial EPG collection failed: %v", err)
			}
		}
	}()

	// Wait for interrupt signal to gracefully shutdown the server
	quit := make(chan os.Signal, 1)
	signal.Notify(quit, syscall.SIGINT, syscall.SIGTERM)
	<-quit
	logger.Info("Shutting down server...")

	// Graceful shutdown with timeout
	ctx, cancel := context.WithTimeout(context.Background(), 30*time.Second)
	defer cancel()

	if err := srv.Shutdown(ctx); err != nil {
		logger.Fatalf("Server forced to shutdown: %v", err)
	}

	logger.Info("Server exited")
}

func setupRoutes(playlistCollector *playlist.Collector, epgCollector *epg.Collector, db *postgres.Database) *gin.Engine {
	gin.SetMode(gin.ReleaseMode)
	router := gin.New()
	router.Use(gin.Logger())
	router.Use(gin.Recovery())

	// Health check endpoint
	router.GET("/health", func(c *gin.Context) {
		c.JSON(http.StatusOK, gin.H{
			"status": "healthy",
			"timestamp": time.Now().Unix(),
		})
	})

	// Stats endpoint
	router.GET("/stats", func(c *gin.Context) {
		channelCount, _ := playlistCollector.GetChannelCount()
		programCount, _ := epgCollector.GetProgramCount()
		
		c.JSON(http.StatusOK, gin.H{
			"channels": channelCount,
			"programs": programCount,
			"timestamp": time.Now().Unix(),
		})
	})

	// Manual collection endpoints
	router.POST("/collect/playlist", func(c *gin.Context) {
		logger.Info("Manual playlist collection triggered")
		if err := playlistCollector.CollectPlaylist(); err != nil {
			c.JSON(http.StatusInternalServerError, gin.H{"error": err.Error()})
			return
		}
		c.JSON(http.StatusOK, gin.H{"message": "Playlist collection completed"})
	})

	router.POST("/collect/epg", func(c *gin.Context) {
		timezone := c.DefaultQuery("tz", "3")
		logger.Infof("Manual EPG collection triggered with timezone: %s", timezone)
		
		var tz int = 3 // default to Moscow timezone
		if timezone != "3" {
			// Parse timezone if needed
		}
		
		if err := epgCollector.CollectEPGForAllChannels(tz); err != nil {
			c.JSON(http.StatusInternalServerError, gin.H{"error": err.Error()})
			return
		}
		c.JSON(http.StatusOK, gin.H{"message": "EPG collection completed"})
	})

	// Get channels endpoint
	router.GET("/channels", func(c *gin.Context) {
		channels, err := db.GetAllChannels()
		if err != nil {
			c.JSON(http.StatusInternalServerError, gin.H{"error": err.Error()})
			return
		}
		c.JSON(http.StatusOK, gin.H{"channels": channels})
	})

	// Get EPG for specific channel
	router.GET("/channels/:id/epg", func(c *gin.Context) {
		channelID := c.Param("id")
		
		// Find channel by external ID
		channel, err := db.GetChannelByExternalID(channelID)
		if err != nil {
			c.JSON(http.StatusNotFound, gin.H{"error": "Channel not found"})
			return
		}

		programs, err := db.GetEPGByChannelID(channel.ID, 50)
		if err != nil {
			c.JSON(http.StatusInternalServerError, gin.H{"error": err.Error()})
			return
		}

		c.JSON(http.StatusOK, gin.H{
			"channel": channel,
			"programs": programs,
		})
	})

	return router
}
