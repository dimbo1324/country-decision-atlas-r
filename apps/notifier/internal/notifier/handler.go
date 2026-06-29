package notifier

import (
	"context"
	"errors"

	"github.com/country-decision-atlas/notifier/internal/channels"
	"github.com/country-decision-atlas/notifier/internal/dlq"
	"github.com/country-decision-atlas/notifier/internal/events"
	"github.com/country-decision-atlas/notifier/internal/metrics"
	mongostore "github.com/country-decision-atlas/notifier/internal/mongo"
	"github.com/country-decision-atlas/notifier/internal/telegram"
)

var ErrDeliveryIncomplete = errors.New("delivery incomplete")

type Handler struct {
	dedup       mongostore.DedupRepository
	subs        mongostore.SubscriptionRepository
	deliveryLog mongostore.DeliveryLogRepository
	deadLetters mongostore.DeadLetterRepository
	registry    *channels.ChannelRegistry
	metrics     *metrics.Metrics
}

func NewHandler(
	dedup mongostore.DedupRepository,
	subs mongostore.SubscriptionRepository,
	deliveryLog mongostore.DeliveryLogRepository,
	deadLetters mongostore.DeadLetterRepository,
	registry *channels.ChannelRegistry,
	metricsCollector *metrics.Metrics,
) *Handler {
	if metricsCollector == nil {
		metricsCollector = metrics.New()
	}
	if registry == nil {
		registry = channels.NewRegistry()
	}
	return &Handler{
		dedup:       dedup,
		subs:        subs,
		deliveryLog: deliveryLog,
		deadLetters: deadLetters,
		registry:    registry,
		metrics:     metricsCollector,
	}
}

func NewTelegramHandler(
	dedup mongostore.DedupRepository,
	subs mongostore.SubscriptionRepository,
	deliveryLog mongostore.DeliveryLogRepository,
	tg telegram.Client,
) *Handler {
	registry := channels.NewRegistry()
	registry.Register(channels.NewTelegramChannel(tg))
	return NewHandler(
		dedup,
		subs,
		deliveryLog,
		mongostore.NewInMemoryDeadLetterRepository(),
		registry,
		metrics.New(),
	)
}

func (h *Handler) Handle(ctx context.Context, e *events.DomainEvent) error {
	processed, err := h.dedup.Exists(ctx, e.EventKey)
	if err != nil {
		h.metrics.IncMongoErrors()
		return err
	}
	if processed {
		h.metrics.IncEventsDeduplicated()
		return nil
	}

	subscribers, err := h.subs.FindActiveByCountry(ctx, e.CountrySlug)
	if err != nil {
		h.metrics.IncMongoErrors()
		return err
	}
	h.metrics.IncEventsProcessed()
	h.metrics.AddSubscriptionsMatched(len(subscribers))

	text := telegram.FormatMessage(e.CountrySlug, e.EventType, e.Title())
	message := channels.NotificationMessage{
		EventKey:    e.EventKey,
		EventType:   e.EventType,
		CountrySlug: e.CountrySlug,
		Title:       e.Title(),
		Body:        text,
	}

	for _, sub := range subscribers {
		recipient := recipientFromSubscription(sub)
		already, err := h.alreadyDelivered(ctx, e.EventKey, recipient)
		if err != nil {
			h.metrics.IncMongoErrors()
			return err
		}
		if already {
			h.metrics.IncEventsSkipped()
			continue
		}

		channel, ok := h.registry.Get(recipient.ChannelType)
		if !ok {
			h.metrics.IncUnsupportedChannelTotal()
			h.metrics.IncDeliveriesFailed()
			h.metrics.IncDeliveriesDLQ()
			if err := h.insertDeliveryFailure(ctx, e, recipient, dlq.ReasonUnsupportedChannel); err != nil {
				h.metrics.IncMongoErrors()
				return err
			}
			if err := h.writeDeliveryDLQ(ctx, e, recipient, dlq.ReasonUnsupportedChannel, "unsupported notification channel", false); err != nil {
				h.metrics.IncMongoErrors()
				return err
			}
			continue
		}

		h.metrics.IncDeliveriesAttempted()
		if recipient.ChannelType == channels.ChannelTelegram {
			h.metrics.IncTelegramAttempted()
		}
		result := channel.Deliver(ctx, recipient, message)
		entry := &mongostore.DeliveryLogEntry{
			EventKey:       e.EventKey,
			TelegramUserID: recipient.TelegramUserID,
			ChannelType:    string(recipient.ChannelType),
			RecipientID:    recipient.RecipientID,
			CountrySlug:    e.CountrySlug,
			Status:         result.Status,
		}
		if result.Error != nil {
			errStr := result.Error.Error()
			entry.Error = &errStr
			h.metrics.IncDeliveriesFailed()
			if recipient.ChannelType == channels.ChannelTelegram {
				h.metrics.IncTelegramFailed()
				h.metrics.IncTelegramErrors()
			}
		} else {
			h.metrics.IncDeliveriesSucceeded()
			if recipient.ChannelType == channels.ChannelTelegram {
				h.metrics.IncTelegramSucceeded()
			}
		}
		if err := h.deliveryLog.Insert(ctx, entry); err != nil {
			h.metrics.IncMongoErrors()
			return err
		}

		if result.Error != nil {
			h.metrics.IncDeliveriesDLQ()
			if err := h.writeDeliveryDLQ(ctx, e, recipient, dlq.ReasonTelegramPermanentFailure, result.Error.Error(), false); err != nil {
				h.metrics.IncMongoErrors()
				return err
			}
		}
	}

	if _, err := h.dedup.TryInsert(ctx, e.EventKey); err != nil {
		h.metrics.IncMongoErrors()
		return err
	}
	return nil
}

func (h *Handler) alreadyDelivered(ctx context.Context, eventKey string, recipient channels.Recipient) (bool, error) {
	entries, err := h.deliveryLog.FindByUser(ctx, mongostore.DeliveryLogQuery{
		TelegramUserID: recipient.TelegramUserID,
		ChannelType:    string(recipient.ChannelType),
		RecipientID:    recipient.RecipientID,
		EventKey:       eventKey,
	})
	if err != nil {
		return false, err
	}
	for _, entry := range entries {
		if entry.Status == "sent" {
			return true, nil
		}
	}
	return false, nil
}

func (h *Handler) insertDeliveryFailure(ctx context.Context, e *events.DomainEvent, recipient channels.Recipient, errText string) error {
	return h.deliveryLog.Insert(ctx, &mongostore.DeliveryLogEntry{
		EventKey:       e.EventKey,
		TelegramUserID: recipient.TelegramUserID,
		ChannelType:    string(recipient.ChannelType),
		RecipientID:    recipient.RecipientID,
		CountrySlug:    e.CountrySlug,
		Status:         "failed",
		Error:          &errText,
	})
}

func (h *Handler) writeDeliveryDLQ(
	ctx context.Context,
	e *events.DomainEvent,
	recipient channels.Recipient,
	reason string,
	errText string,
	retryable bool,
) error {
	if h.deadLetters == nil {
		return nil
	}
	return h.deadLetters.Upsert(ctx, &mongostore.DeadLetter{
		EventKey:       e.EventKey,
		Stage:          dlq.StageDelivery,
		ReasonCode:     reason,
		Error:          errText,
		EventType:      e.EventType,
		CountrySlug:    e.CountrySlug,
		ChannelType:    string(recipient.ChannelType),
		RecipientID:    recipient.RecipientID,
		TelegramUserID: recipient.TelegramUserID,
		Payload:        e.Payload,
		Retryable:      retryable,
		Status:         dlq.StatusOpen,
	})
}

func recipientFromSubscription(sub *mongostore.Subscription) channels.Recipient {
	channelType := channels.ChannelType(sub.ChannelType)
	if channelType == "" {
		channelType = channels.ChannelTelegram
	}
	recipientID := sub.RecipientID
	if recipientID == "" {
		recipientID = sub.TelegramUserID
	}
	return channels.Recipient{
		ChannelType:    channelType,
		RecipientID:    recipientID,
		TelegramUserID: sub.TelegramUserID,
		CountrySlug:    sub.CountrySlug,
	}
}
