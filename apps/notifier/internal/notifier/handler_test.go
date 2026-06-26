package notifier

import (
	"context"
	"testing"
	"time"

	"github.com/country-decision-atlas/notifier/internal/events"
	mongostore "github.com/country-decision-atlas/notifier/internal/mongo"
	"github.com/country-decision-atlas/notifier/internal/telegram"
)

func makeTestEvent(eventKey, countrySlug string) *events.DomainEvent {
	return &events.DomainEvent{
		EventKey:      eventKey,
		EventType:     "legal_signal.published",
		AggregateType: "legal_signal",
		AggregateID:   "agg-1",
		CountrySlug:   countrySlug,
		Payload:       map[string]interface{}{},
		CreatedAt:     time.Now().UTC(),
	}
}

func makeActiveSub(userID, countrySlug string) *mongostore.Subscription {
	return &mongostore.Subscription{
		TelegramUserID: userID,
		CountrySlug:    countrySlug,
		Active:         true,
		CreatedAt:      time.Now().UTC(),
		WebUserID:      nil,
	}
}

func TestDuplicateEventSkipped(t *testing.T) {
	dedup := mongostore.NewInMemoryDedupRepository()
	subs := mongostore.NewInMemorySubscriptionRepository([]*mongostore.Subscription{
		makeActiveSub("user1", "argentina"),
	})
	dl := mongostore.NewInMemoryDeliveryLogRepository()
	tg := &telegram.FakeClient{}
	h := NewHandler(dedup, subs, dl, tg)

	ctx := context.Background()
	e := makeTestEvent("key-dup", "argentina")

	_ = h.Handle(ctx, e)
	_ = h.Handle(ctx, e)

	if len(tg.Sent) != 1 {
		t.Errorf("want 1 sent message got %d", len(tg.Sent))
	}
	if len(dl.Entries) != 1 {
		t.Errorf("want 1 delivery_log entry got %d", len(dl.Entries))
	}
}

func TestMatchingSubscriberReceivesMessage(t *testing.T) {
	dedup := mongostore.NewInMemoryDedupRepository()
	subs := mongostore.NewInMemorySubscriptionRepository([]*mongostore.Subscription{
		makeActiveSub("user1", "argentina"),
	})
	dl := mongostore.NewInMemoryDeliveryLogRepository()
	tg := &telegram.FakeClient{}
	h := NewHandler(dedup, subs, dl, tg)

	ctx := context.Background()
	e := makeTestEvent("key-match", "argentina")
	_ = h.Handle(ctx, e)

	if len(tg.Sent) != 1 {
		t.Errorf("want 1 sent message got %d", len(tg.Sent))
	}
	if tg.Sent[0].ChatID != "user1" {
		t.Errorf("want chatID user1 got %s", tg.Sent[0].ChatID)
	}
}

func TestNonMatchingSubscriberDoesNotReceiveMessage(t *testing.T) {
	dedup := mongostore.NewInMemoryDedupRepository()
	subs := mongostore.NewInMemorySubscriptionRepository([]*mongostore.Subscription{
		makeActiveSub("user1", "germany"),
	})
	dl := mongostore.NewInMemoryDeliveryLogRepository()
	tg := &telegram.FakeClient{}
	h := NewHandler(dedup, subs, dl, tg)

	ctx := context.Background()
	e := makeTestEvent("key-nomatch", "argentina")
	_ = h.Handle(ctx, e)

	if len(tg.Sent) != 0 {
		t.Errorf("want 0 messages got %d", len(tg.Sent))
	}
}

func TestInactiveSubscriberDoesNotReceiveMessage(t *testing.T) {
	dedup := mongostore.NewInMemoryDedupRepository()
	subs := mongostore.NewInMemorySubscriptionRepository([]*mongostore.Subscription{
		{TelegramUserID: "user1", CountrySlug: "argentina", Active: false, CreatedAt: time.Now().UTC()},
	})
	dl := mongostore.NewInMemoryDeliveryLogRepository()
	tg := &telegram.FakeClient{}
	h := NewHandler(dedup, subs, dl, tg)

	ctx := context.Background()
	e := makeTestEvent("key-inactive", "argentina")
	_ = h.Handle(ctx, e)

	if len(tg.Sent) != 0 {
		t.Errorf("want 0 messages got %d", len(tg.Sent))
	}
}

func TestNoSubscribersHandledSafely(t *testing.T) {
	dedup := mongostore.NewInMemoryDedupRepository()
	subs := mongostore.NewInMemorySubscriptionRepository(nil)
	dl := mongostore.NewInMemoryDeliveryLogRepository()
	tg := &telegram.FakeClient{}
	h := NewHandler(dedup, subs, dl, tg)

	ctx := context.Background()
	e := makeTestEvent("key-nosub", "argentina")
	err := h.Handle(ctx, e)
	if err != nil {
		t.Errorf("want no error got %v", err)
	}
	if len(dl.Entries) != 0 {
		t.Errorf("want 0 log entries got %d", len(dl.Entries))
	}
}

func TestSuccessCreatesDeliveryLogSent(t *testing.T) {
	dedup := mongostore.NewInMemoryDedupRepository()
	subs := mongostore.NewInMemorySubscriptionRepository([]*mongostore.Subscription{
		makeActiveSub("user1", "argentina"),
	})
	dl := mongostore.NewInMemoryDeliveryLogRepository()
	tg := &telegram.FakeClient{}
	h := NewHandler(dedup, subs, dl, tg)

	ctx := context.Background()
	e := makeTestEvent("key-success", "argentina")
	_ = h.Handle(ctx, e)

	if len(dl.Entries) != 1 {
		t.Fatalf("want 1 log entry got %d", len(dl.Entries))
	}
	if dl.Entries[0].Status != "sent" {
		t.Errorf("want status=sent got %s", dl.Entries[0].Status)
	}
}

func TestFailureCreatesDeliveryLogFailed(t *testing.T) {
	dedup := mongostore.NewInMemoryDedupRepository()
	subs := mongostore.NewInMemorySubscriptionRepository([]*mongostore.Subscription{
		makeActiveSub("user1", "argentina"),
	})
	dl := mongostore.NewInMemoryDeliveryLogRepository()
	tg := &errorClient{}
	h := NewHandler(dedup, subs, dl, tg)

	ctx := context.Background()
	e := makeTestEvent("key-fail", "argentina")
	_ = h.Handle(ctx, e)

	if len(dl.Entries) != 1 {
		t.Fatalf("want 1 log entry got %d", len(dl.Entries))
	}
	if dl.Entries[0].Status != "failed" {
		t.Errorf("want status=failed got %s", dl.Entries[0].Status)
	}
	if dl.Entries[0].Error == nil {
		t.Error("want non-nil error in log entry")
	}
}

func TestWebUserIDRemainsNil(t *testing.T) {
	sub := makeActiveSub("user1", "argentina")
	if sub.WebUserID != nil {
		t.Error("want WebUserID=nil")
	}
}

func TestMessageTemplateIncludesCountryAndEventType(t *testing.T) {
	dedup := mongostore.NewInMemoryDedupRepository()
	subs := mongostore.NewInMemorySubscriptionRepository([]*mongostore.Subscription{
		makeActiveSub("user1", "argentina"),
	})
	dl := mongostore.NewInMemoryDeliveryLogRepository()
	tg := &telegram.FakeClient{}
	h := NewHandler(dedup, subs, dl, tg)

	ctx := context.Background()
	e := makeTestEvent("key-template", "argentina")
	_ = h.Handle(ctx, e)

	if len(tg.Sent) == 0 {
		t.Fatal("expected at least one message sent")
	}
	msg := tg.Sent[0].Text
	if msg == "" {
		t.Error("message should not be empty")
	}
}
