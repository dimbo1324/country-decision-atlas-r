package config

import (
	"errors"
	"os"
	"strconv"
)

type Config struct {
	KafkaBrokers              string
	KafkaTopic                string
	KafkaConsumerGroup        string
	MongoURL                  string
	MongoDatabase             string
	TelegramBotToken          string
	TelegramMode              string
	NotifyAfter               string
	NotifierHTTPAddr          string
	GRPCAddr                  string
	GRPCAuthToken             string
	TelegramWebLinkCodeTTLMin int
}

func Load() (*Config, error) {
	c := &Config{
		KafkaBrokers:              getEnv("KAFKA_BROKERS", "localhost:9092"),
		KafkaTopic:                getEnv("KAFKA_TOPIC", "cda.domain-events"),
		KafkaConsumerGroup:        getEnv("KAFKA_CONSUMER_GROUP", "signal-notifier"),
		MongoURL:                  getEnv("MONGO_URL", "mongodb://localhost:27017"),
		MongoDatabase:             getEnv("MONGO_DATABASE", "country_decision_alerts"),
		TelegramBotToken:          getEnv("TELEGRAM_BOT_TOKEN", ""),
		TelegramMode:              getEnv("TELEGRAM_MODE", "fake"),
		NotifyAfter:               getEnv("NOTIFY_AFTER", "2026-01-01T00:00:00Z"),
		NotifierHTTPAddr:          getEnv("NOTIFIER_HTTP_ADDR", ":8081"),
		GRPCAddr:                  getEnv("GRPC_ADDR", ":9090"),
		GRPCAuthToken:             getEnv("GRPC_AUTH_TOKEN", ""),
		TelegramWebLinkCodeTTLMin: getEnvInt("TELEGRAM_WEB_LINK_CODE_TTL_MINUTES", 10),
	}
	if err := c.validate(); err != nil {
		return nil, err
	}
	return c, nil
}

func (c *Config) validate() error {
	if c.TelegramMode == "real" && c.TelegramBotToken == "" {
		return errors.New("TELEGRAM_BOT_TOKEN is required when TELEGRAM_MODE=real")
	}
	return nil
}

func getEnv(key, defaultVal string) string {
	if v := os.Getenv(key); v != "" {
		return v
	}
	return defaultVal
}

func getEnvInt(key string, defaultVal int) int {
	v := os.Getenv(key)
	if v == "" {
		return defaultVal
	}
	parsed, err := strconv.Atoi(v)
	if err != nil {
		return defaultVal
	}
	return parsed
}
