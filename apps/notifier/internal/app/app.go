package app

import (
	"context"
	"encoding/json"
	"log"
	"net/http"
	"os"
	"os/signal"
	"sync"
	"syscall"
	"time"

	"github.com/country-decision-atlas/notifier/internal/channels"
	"github.com/country-decision-atlas/notifier/internal/config"
	"github.com/country-decision-atlas/notifier/internal/dlq"
	"github.com/country-decision-atlas/notifier/internal/events"
	"github.com/country-decision-atlas/notifier/internal/grpcserver"
	"github.com/country-decision-atlas/notifier/internal/health"
	kafkaconsumer "github.com/country-decision-atlas/notifier/internal/kafka"
	"github.com/country-decision-atlas/notifier/internal/metrics"
	mongostore "github.com/country-decision-atlas/notifier/internal/mongo"
	"github.com/country-decision-atlas/notifier/internal/notifier"
	"github.com/country-decision-atlas/notifier/internal/subscriptions"
	"github.com/country-decision-atlas/notifier/internal/telegram"
)

func Run() {
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
	linkCodeRepo := mongostore.NewTelegramLinkCodeRepository(store)
	dl := mongostore.NewDeliveryLogRepository(store)
	dedup := mongostore.NewDedupRepository(store)
	deadLetters := mongostore.NewDeadLetterRepository(store)
	metricsCollector := metrics.New()

	svc := subscriptions.New(subRepo, identityRepo)

	registry := channels.NewRegistry()
	registry.Register(channels.NewTelegramChannel(tgClient))
	h := notifier.NewHandler(dedup, subRepo, identityRepo, dl, deadLetters, registry, metricsCollector)

	grpcSrv := grpcserver.NewWithMetrics(svc, dl, identityRepo, linkCodeRepo, metricsCollector)

	consumer := kafkaconsumer.NewKafkaConsumer(cfg.KafkaBrokers, cfg.KafkaTopic, cfg.KafkaConsumerGroup)
	defer func() { _ = consumer.Close() }()

	httpSrv := &http.Server{
		Addr:              cfg.NotifierHTTPAddr,
		Handler:           health.Handler(metricsCollector),
		ReadHeaderTimeout: 5 * time.Second,
		ReadTimeout:       10 * time.Second,
		WriteTimeout:      10 * time.Second,
		IdleTimeout:       60 * time.Second,
	}
	go func() {
		if err := httpSrv.ListenAndServe(); err != nil && err != http.ErrServerClosed {
			log.Printf("health server error: %v", err)
		}
	}()

	if cfg.GRPCAuthToken == "" {
		log.Printf("warning: GRPC_AUTH_TOKEN is not set, gRPC subscription service will reject all calls")
	}
	var grpcWG sync.WaitGroup
	grpcWG.Add(1)
	go func() {
		defer grpcWG.Done()
		log.Printf("gRPC server starting addr=%s", cfg.GRPCAddr)
		if err := grpcserver.Serve(ctx, cfg.GRPCAddr, cfg.GRPCAuthToken, grpcSrv); err != nil {
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
			metricsCollector.IncKafkaMessagesFailed()
			continue
		}
		metricsCollector.IncKafkaMessagesConsumed()
		e, err := events.Parse(msg.Value)
		if err != nil {
			log.Printf("parse error: %v", err)
			var partial events.DomainEvent
			_ = json.Unmarshal(msg.Value, &partial)
			eventKey := partial.EventKey
			if eventKey == "" {
				eventKey = mongostore.StableMalformedEventKey(msg.Value)
			}
			if dlqErr := deadLetters.Upsert(ctx, &mongostore.DeadLetter{
				EventKey:    eventKey,
				Stage:       dlq.StageEventProcessing,
				ReasonCode:  events.ReasonForError(err),
				Error:       err.Error(),
				EventType:   partial.EventType,
				CountrySlug: partial.CountrySlug,
				Payload:     partial.Payload,
				Retryable:   false,
				Status:      dlq.StatusOpen,
			}); dlqErr != nil {
				log.Printf("dlq write error: %v", dlqErr)
				metricsCollector.IncMongoErrors()
				continue
			}
			metricsCollector.IncEventsDLQ()
			if err := consumer.Commit(ctx, msg); err != nil {
				log.Printf("commit error malformed_event_key=%s: %v", eventKey, err)
				metricsCollector.IncKafkaMessagesFailed()
			} else {
				metricsCollector.IncKafkaMessagesCommitted()
			}
			continue
		}
		if err := h.Handle(ctx, e); err != nil {
			log.Printf("handle error event_key=%s: %v", e.EventKey, err)
			continue
		}
		if err := consumer.Commit(ctx, msg); err != nil {
			log.Printf("commit error event_key=%s: %v", e.EventKey, err)
			metricsCollector.IncKafkaMessagesFailed()
		} else {
			metricsCollector.IncKafkaMessagesCommitted()
		}
	}

	shutdownCtx, cancel := context.WithTimeout(context.Background(), 5*time.Second)
	defer cancel()
	_ = httpSrv.Shutdown(shutdownCtx)
	grpcWG.Wait()

	log.Println("notifier stopped")
}
