package notifier

import (
	"context"
	"errors"

	"github.com/country-decision-atlas/notifier/internal/events"
	mongostore "github.com/country-decision-atlas/notifier/internal/mongo"
	"github.com/country-decision-atlas/notifier/internal/telegram"
)

var ErrDeliveryIncomplete = errors.New("delivery incomplete")

type Handler struct {
	dedup       mongostore.DedupRepository
	subs        mongostore.SubscriptionRepository
	deliveryLog mongostore.DeliveryLogRepository
	tg          telegram.Client
}

func NewHandler(
	dedup mongostore.DedupRepository,
	subs mongostore.SubscriptionRepository,
	deliveryLog mongostore.DeliveryLogRepository,
	tg telegram.Client,
) *Handler {
	return &Handler{dedup: dedup, subs: subs, deliveryLog: deliveryLog, tg: tg}
}

func (h *Handler) Handle(ctx context.Context, e *events.DomainEvent) error {
	processed, err := h.dedup.Exists(ctx, e.EventKey)
	if err != nil {
		return err
	}
	if processed {
		return nil
	}

	subscribers, err := h.subs.FindActiveByCountry(ctx, e.CountrySlug)
	if err != nil {
		return err
	}

	text := telegram.FormatMessage(e.CountrySlug, e.EventType, e.Title())

	delivered := true
	for _, sub := range subscribers {
		already, err := h.alreadyDelivered(ctx, e.EventKey, sub.TelegramUserID)
		if err != nil {
			return err
		}
		if already {
			continue
		}

		sendErr := h.tg.SendMessage(ctx, sub.TelegramUserID, text)
		entry := &mongostore.DeliveryLogEntry{
			EventKey:       e.EventKey,
			TelegramUserID: sub.TelegramUserID,
			CountrySlug:    e.CountrySlug,
		}
		if sendErr != nil {
			errStr := sendErr.Error()
			entry.Status = "failed"
			entry.Error = &errStr
			delivered = false
		} else {
			entry.Status = "sent"
		}
		if err := h.deliveryLog.Insert(ctx, entry); err != nil {
			return err
		}
	}

	if !delivered {
		return ErrDeliveryIncomplete
	}

	if _, err := h.dedup.TryInsert(ctx, e.EventKey); err != nil {
		return err
	}
	return nil
}

func (h *Handler) alreadyDelivered(ctx context.Context, eventKey string, telegramUserID string) (bool, error) {
	entries, err := h.deliveryLog.FindByUser(ctx, mongostore.DeliveryLogQuery{
		TelegramUserID: telegramUserID,
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
