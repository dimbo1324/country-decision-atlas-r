package notifier

import (
	"context"
	"encoding/json"
	"testing"
	"time"

	"github.com/country-decision-atlas/notifier/internal/events"
	mongostore "github.com/country-decision-atlas/notifier/internal/mongo"
	"github.com/country-decision-atlas/notifier/internal/subscriptions"
	"github.com/country-decision-atlas/notifier/internal/telegram"
)

func makeIntegrationSetup() (
	*Handler,
	*mongostore.InMemorySubscriptionRepository,
	*mongostore.InMemoryDeliveryLogRepository,
	*mongostore.InMemoryDedupRepository,
	*telegram.FakeClient,
	*subscriptions.Service,
) {
	subsRepo := mongostore.NewInMemorySubscriptionRepository(nil)
	identities := mongostore.NewInMemoryTelegramIdentityRepository()
	dl := mongostore.NewInMemoryDeliveryLogRepository()
	dedup := mongostore.NewInMemoryDedupRepository()
	tg := &telegram.FakeClient{}
	svc := subscriptions.New(subsRepo, identities, []string{"argentina", "russia", "uruguay"})
	h := NewTelegramHandler(dedup, subsRepo, dl, tg)
	return h, subsRepo, dl, dedup, tg, svc
}

func makeEvent(key, country string) *events.DomainEvent {
	return &events.DomainEvent{
		EventKey:      key,
		EventType:     "legal_signal.published",
		AggregateType: "legal_signal",
		AggregateID:   "agg-1",
		CountrySlug:   country,
		Payload:       map[string]interface{}{"title": "Test Event"},
		CreatedAt:     time.Now().UTC(),
	}
}

func makeEventFromJSON(key, country string) []byte {
	payload := map[string]interface{}{
		"event_key":      key,
		"event_type":     "legal_signal.published",
		"aggregate_type": "legal_signal",
		"aggregate_id":   "agg-1",
		"country_slug":   country,
		"payload":        map[string]interface{}{"title": "Test Event"},
		"created_at":     time.Now().UTC().Format(time.RFC3339),
	}
	b, _ := json.Marshal(payload)
	return b
}

func TestIntegrationFullFlow(t *testing.T) {
	h, _, dl, _, tg, svc := makeIntegrationSetup()
	ctx := context.Background()

	_, err := svc.CreateSubscription(ctx, "user1", "dima", "argentina")
	if err != nil {
		t.Fatalf("create subscription: %v", err)
	}

	e := makeEvent("key-flow", "argentina")
	if err := h.Handle(ctx, e); err != nil {
		t.Fatalf("handle: %v", err)
	}

	if len(tg.Sent) != 1 {
		t.Fatalf("want 1 fake telegram message got %d", len(tg.Sent))
	}
	if len(dl.Entries) != 1 {
		t.Fatalf("want 1 delivery_log entry got %d", len(dl.Entries))
	}
	if dl.Entries[0].Status != "sent" {
		t.Errorf("want status=sent got %s", dl.Entries[0].Status)
	}
}

func TestIntegrationDuplicateEventKeySkipped(t *testing.T) {
	h, _, dl, _, tg, svc := makeIntegrationSetup()
	ctx := context.Background()

	_, _ = svc.CreateSubscription(ctx, "user1", "dima", "argentina")

	e := makeEvent("key-dup-integ", "argentina")
	_ = h.Handle(ctx, e)
	_ = h.Handle(ctx, e)

	if len(tg.Sent) != 1 {
		t.Errorf("duplicate event_key should skip second, want 1 message got %d", len(tg.Sent))
	}
	if len(dl.Entries) != 1 {
		t.Errorf("want 1 delivery_log entry got %d", len(dl.Entries))
	}
}

func TestIntegrationInactiveSubscriptionSkipped(t *testing.T) {
	h, _, dl, _, tg, svc := makeIntegrationSetup()
	ctx := context.Background()

	_, _ = svc.CreateSubscription(ctx, "user1", "dima", "argentina")
	_, _ = svc.DeleteSubscription(ctx, "user1", "argentina")

	e := makeEvent("key-inactive-integ", "argentina")
	_ = h.Handle(ctx, e)

	if len(tg.Sent) != 0 {
		t.Errorf("inactive subscriber should not receive delivery, got %d messages", len(tg.Sent))
	}
	if len(dl.Entries) != 0 {
		t.Errorf("want 0 delivery_log entries got %d", len(dl.Entries))
	}
}

func TestIntegrationNonMatchingCountrySkipped(t *testing.T) {
	h, _, _, _, tg, svc := makeIntegrationSetup()
	ctx := context.Background()

	_, _ = svc.CreateSubscription(ctx, "user1", "dima", "russia")

	e := makeEvent("key-nomatch-integ", "argentina")
	_ = h.Handle(ctx, e)

	if len(tg.Sent) != 0 {
		t.Errorf("non-matching country should not deliver, got %d messages", len(tg.Sent))
	}
}

func TestIntegrationNoSubscribersNoFail(t *testing.T) {
	h, _, dl, _, tg, _ := makeIntegrationSetup()
	ctx := context.Background()

	e := makeEvent("key-nosub-integ", "argentina")
	err := h.Handle(ctx, e)
	if err != nil {
		t.Errorf("no subscribers should not error: %v", err)
	}
	if len(tg.Sent) != 0 {
		t.Error("want 0 messages")
	}
	if len(dl.Entries) != 0 {
		t.Error("want 0 log entries")
	}
}

func TestIntegrationEventParsedFromJSON(t *testing.T) {
	b := makeEventFromJSON("key-json-integ", "argentina")
	e, err := events.Parse(b)
	if err != nil {
		t.Fatalf("parse error: %v", err)
	}
	if e.EventKey != "key-json-integ" {
		t.Errorf("want key-json-integ got %s", e.EventKey)
	}
	if e.CountrySlug != "argentina" {
		t.Errorf("want argentina got %s", e.CountrySlug)
	}
}

func TestIntegrationDeliveryLogFailedOnTelegramError(t *testing.T) {
	_, subsRepo, dl, dedup, _, svc := makeIntegrationSetup()
	ctx := context.Background()

	_, _ = svc.CreateSubscription(ctx, "user1", "dima", "argentina")

	tg := &errorClient{}
	h := NewTelegramHandler(dedup, subsRepo, dl, tg)

	e := makeEvent("key-fail-integ", "argentina")
	_ = h.Handle(ctx, e)

	if len(dl.Entries) != 1 {
		t.Fatalf("want 1 delivery_log entry got %d", len(dl.Entries))
	}
	if dl.Entries[0].Status != "failed" {
		t.Errorf("want status=failed got %s", dl.Entries[0].Status)
	}
}
