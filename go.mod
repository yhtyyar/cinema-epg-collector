module cinema-epg-collector

go 1.21

require (
	github.com/gin-gonic/gin v1.9.1
	github.com/lib/pq v1.10.9
	github.com/go-redis/redis/v8 v8.11.5
	github.com/golang-jwt/jwt/v5 v5.0.0
	github.com/robfig/cron/v3 v3.0.1
	github.com/spf13/viper v1.16.0
	github.com/sirupsen/logrus v1.9.3
	gorm.io/gorm v1.25.4
	gorm.io/driver/postgres v1.5.2
)
