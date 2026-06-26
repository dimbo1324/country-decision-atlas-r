package notifier

import (
	"context"

	"github.com/country-decision-atlas/notifier/internal/events"
	mongostore "github.com/country-decision-atlas/notifier/internal/mongo"
	"github.com/country-decision-atlas/notifier/internal/telegram"
)

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
	inserted, err := h.dedup.TryInsert(ctx, e.EventKey)
	if err != nil {
		return err
	}
	if !inserted {
		return nil
	}

	subscribers, err := h.subs.FindActiveByCountry(ctx, e.CountrySlug)
	if err != nil {
		return err
	}

	text := telegram.FormatMessage(e.CountrySlug, e.EventType, e.Title())

	for _, sub := range subscribers {
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
		} else {
			entry.Status = "sent"
		}
		_ = h.deliveryLog.Insert(ctx, entry)
	}
	return nil
}
