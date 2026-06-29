package main

import (
	"context"
	"log"
	"net/http"
	"os"
	"os/signal"
	"syscall"

	"github.com/country-decision-atlas/notifier/internal/config"
	"github.com/country-decision-atlas/notifier/internal/events"
	"github.com/country-decision-atlas/notifier/internal/grpcserver"
	"github.com/country-decision-atlas/notifier/internal/health"
	kafkaconsumer "github.com/country-decision-atlas/notifier/internal/kafka"
	mongostore "github.com/country-decision-atlas/notifier/internal/mongo"
	"github.com/country-decision-atlas/notifier/internal/notifier"
	"github.com/country-decision-atlas/notifier/internal/subscriptions"
	"github.com/country-decision-atlas/notifier/internal/telegram"
)

func main() {
	cfg, err := config.Load()
	if err != nil {
		log.Fatalf("config error: %v", err)
	}

	ctx, stop := signal.NotifyContext(context.Background(), os.Interrupt, syscall.SIGTERM)
	defer stop()

	store, err := mongostore.Connect(ctx, cfg.MongoURL, cfg.MongoDatabase)
	if err != nil {
		log.Fatalf("mongo connect error: %v", err)
	}
	defer func() { _ = store.Disconnect(context.Background()) }()

	if err := mongostore.EnsureIndexes(ctx, store); err != nil {
		log.Fatalf("mongo index error: %v", err)
	}

	var tgClient telegram.Client
	if cfg.TelegramMode == "fake" {
		tgClient = &telegram.FakeClient{}
	} else {
		tgClient = telegram.NewRealClient(cfg.TelegramBotToken)
	}

	subRepo := mongostore.NewSubscriptionRepository(store)
	identityRepo := mongostore.NewTelegramIdentityRepository(store)
	dl := mongostore.NewDeliveryLogRepository(store)
	dedup := mongostore.NewDedupRepository(store)

	svc := subscriptions.New(subRepo, identityRepo, cfg.AllowedCountries)

	h := notifier.NewHandler(dedup, subRepo, dl, tgClient)

	grpcSrv := grpcserver.New(svc, dl)

	consumer := kafkaconsumer.NewKafkaConsumer(cfg.KafkaBrokers, cfg.KafkaTopic, cfg.KafkaConsumerGroup)
	defer func() { _ = consumer.Close() }()

	go func() {
		srv := &http.Server{Addr: cfg.NotifierHTTPAddr, Handler: health.Handler()}
		if err := srv.ListenAndServe(); err != nil && err != http.ErrServerClosed {
			log.Printf("health server error: %v", err)
		}
	}()

	go func() {
		log.Printf("gRPC server starting addr=%s", cfg.GRPCAddr)
		if err := grpcserver.Listen(cfg.GRPCAddr, grpcSrv); err != nil {
			log.Printf("gRPC server error: %v", err)
		}
	}()

	log.Printf("notifier started, addr=%s grpc=%s kafka=%s topic=%s", cfg.NotifierHTTPAddr, cfg.GRPCAddr, cfg.KafkaBrokers, cfg.KafkaTopic)

	for {
		msg, err := consumer.ReadMessage(ctx)
		if err != nil {
			if ctx.Err() != nil {
				break
			}
			log.Printf("kafka read error: %v", err)
			continue
		}
		e, err := events.Parse(msg.Value)
		if err != nil {
			log.Printf("parse error: %v", err)
			continue
		}
		if err := h.Handle(ctx, e); err != nil {
			log.Printf("handle error event_key=%s: %v", e.EventKey, err)
		}
	}

	log.Println("notifier stopped")
}
