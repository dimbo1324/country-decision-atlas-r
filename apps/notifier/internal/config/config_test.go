package config

import (
	"os"
	"testing"
)

func TestLoadDefaults(t *testing.T) {
	unset := []string{
		"KAFKA_BROKERS", "KAFKA_TOPIC", "KAFKA_CONSUMER_GROUP",
		"MONGO_URL", "MONGO_DATABASE", "TELEGRAM_BOT_TOKEN",
		"TELEGRAM_MODE", "NOTIFY_AFTER", "NOTIFIER_HTTP_ADDR",
		"NOTIFIER_ALLOWED_COUNTRIES", "GRPC_ADDR", "GRPC_AUTH_TOKEN",
	}
	for _, k := range unset {
		os.Unsetenv(k)
	}

	cfg, err := Load()
	if err != nil {
		t.Fatalf("unexpected error: %v", err)
	}
	if cfg.KafkaBrokers != "localhost:9092" {
		t.Errorf("KafkaBrokers want localhost:9092 got %s", cfg.KafkaBrokers)
	}
	if cfg.KafkaTopic != "cda.domain-events" {
		t.Errorf("KafkaTopic want cda.domain-events got %s", cfg.KafkaTopic)
	}
	if cfg.KafkaConsumerGroup != "signal-notifier" {
		t.Errorf("KafkaConsumerGroup want signal-notifier got %s", cfg.KafkaConsumerGroup)
	}
	if cfg.MongoURL != "mongodb://localhost:27017" {
		t.Errorf("MongoURL want mongodb://localhost:27017 got %s", cfg.MongoURL)
	}
	if cfg.MongoDatabase != "country_decision_alerts" {
		t.Errorf("MongoDatabase want country_decision_alerts got %s", cfg.MongoDatabase)
	}
	if cfg.TelegramMode != "fake" {
		t.Errorf("TelegramMode want fake got %s", cfg.TelegramMode)
	}
	if cfg.NotifierHTTPAddr != ":8081" {
		t.Errorf("NotifierHTTPAddr want :8081 got %s", cfg.NotifierHTTPAddr)
	}
}

func TestLoadEnvOverrides(t *testing.T) {
	os.Setenv("KAFKA_BROKERS", "broker1:9092,broker2:9092")
	os.Setenv("KAFKA_TOPIC", "test.topic")
	os.Setenv("TELEGRAM_MODE", "fake")
	defer func() {
		os.Unsetenv("KAFKA_BROKERS")
		os.Unsetenv("KAFKA_TOPIC")
		os.Unsetenv("TELEGRAM_MODE")
	}()

	cfg, err := Load()
	if err != nil {
		t.Fatalf("unexpected error: %v", err)
	}
	if cfg.KafkaBrokers != "broker1:9092,broker2:9092" {
		t.Errorf("KafkaBrokers want override got %s", cfg.KafkaBrokers)
	}
	if cfg.KafkaTopic != "test.topic" {
		t.Errorf("KafkaTopic want override got %s", cfg.KafkaTopic)
	}
}

func TestFakeModeNoTokenRequired(t *testing.T) {
	os.Unsetenv("TELEGRAM_BOT_TOKEN")
	os.Setenv("TELEGRAM_MODE", "fake")
	defer os.Unsetenv("TELEGRAM_MODE")

	_, err := Load()
	if err != nil {
		t.Errorf("fake mode should not require token, got error: %v", err)
	}
}

func TestRealModeRequiresToken(t *testing.T) {
	os.Unsetenv("TELEGRAM_BOT_TOKEN")
	os.Setenv("TELEGRAM_MODE", "real")
	defer func() {
		os.Unsetenv("TELEGRAM_MODE")
	}()

	_, err := Load()
	if err == nil {
		t.Error("real mode without token should return error")
	}
}
