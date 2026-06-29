package bot

import (
	"context"
	"strings"
	"testing"

	mongostore "github.com/country-decision-atlas/notifier/internal/mongo"
	"github.com/country-decision-atlas/notifier/internal/subscriptions"
	"github.com/country-decision-atlas/notifier/internal/telegram"
)

func makeHandler() (*Handler, *telegram.FakeClient) {
	subsRepo := mongostore.NewInMemorySubscriptionRepository(nil)
	identities := mongostore.NewInMemoryTelegramIdentityRepository()
	svc := subscriptions.New(subsRepo, identities, []string{"argentina", "russia", "uruguay"})
	tg := &telegram.FakeClient{}
	h := New(svc, tg)
	return h, tg
}

func makeUpdate(text string, userID int64, username string) *telegram.TelegramUpdate {
	return &telegram.TelegramUpdate{
		UpdateID: 1,
		Message: &telegram.TelegramMessage{
			Text: text,
			Chat: telegram.TelegramChat{ID: userID},
			From: &telegram.TelegramUser{ID: userID, Username: username},
		},
	}
}

func TestHandleSubscribe(t *testing.T) {
	h, tg := makeHandler()
	err := h.Handle(context.Background(), makeUpdate("/subscribe argentina", 100, "dima"))
	if err != nil {
		t.Fatalf("unexpected error: %v", err)
	}
	if len(tg.Sent) != 1 {
		t.Fatalf("want 1 message got %d", len(tg.Sent))
	}
	if !strings.Contains(tg.Sent[0].Text, "argentina") {
		t.Error("expected argentina in reply")
	}
	if !strings.Contains(tg.Sent[0].Text, disclaimer) {
		t.Errorf("expected disclaimer in reply, got: %s", tg.Sent[0].Text)
	}
}

func TestHandleSubscribeIdempotent(t *testing.T) {
	h, tg := makeHandler()
	ctx := context.Background()
	_ = h.Handle(ctx, makeUpdate("/subscribe argentina", 100, "dima"))
	_ = h.Handle(ctx, makeUpdate("/subscribe argentina", 100, "dima"))
	if len(tg.Sent) != 2 {
		t.Fatalf("want 2 replies got %d", len(tg.Sent))
	}
	if strings.Contains(tg.Sent[1].Text, "Ошибка") {
		t.Error("second subscribe should not error")
	}
}

func TestHandleSubscribeInvalidCountry(t *testing.T) {
	h, tg := makeHandler()
	_ = h.Handle(context.Background(), makeUpdate("/subscribe germany", 100, "dima"))
	if len(tg.Sent) != 1 {
		t.Fatalf("want 1 message got %d", len(tg.Sent))
	}
	if !strings.Contains(tg.Sent[0].Text, disclaimer) {
		t.Error("expected disclaimer")
	}
}

func TestHandleSubscribeMissingCountry(t *testing.T) {
	h, tg := makeHandler()
	_ = h.Handle(context.Background(), makeUpdate("/subscribe", 100, "dima"))
	if len(tg.Sent) != 1 {
		t.Fatalf("want 1 message got %d", len(tg.Sent))
	}
	if !strings.Contains(tg.Sent[0].Text, disclaimer) {
		t.Error("expected disclaimer")
	}
}

func TestHandleUnsubscribe(t *testing.T) {
	h, tg := makeHandler()
	ctx := context.Background()
	_ = h.Handle(ctx, makeUpdate("/subscribe argentina", 100, "dima"))
	tg.Sent = nil
	_ = h.Handle(ctx, makeUpdate("/unsubscribe argentina", 100, "dima"))
	if len(tg.Sent) != 1 {
		t.Fatalf("want 1 message got %d", len(tg.Sent))
	}
	if !strings.Contains(tg.Sent[0].Text, disclaimer) {
		t.Error("expected disclaimer")
	}
}

func TestHandleUnsubscribeMissing(t *testing.T) {
	h, tg := makeHandler()
	_ = h.Handle(context.Background(), makeUpdate("/unsubscribe argentina", 100, "dima"))
	if len(tg.Sent) != 1 {
		t.Fatalf("want 1 message got %d", len(tg.Sent))
	}
	if strings.Contains(tg.Sent[0].Text, "Ошибка") {
		t.Error("missing unsubscribe should be controlled message, not error")
	}
	if !strings.Contains(tg.Sent[0].Text, disclaimer) {
		t.Error("expected disclaimer")
	}
}

func TestHandleList(t *testing.T) {
	h, tg := makeHandler()
	ctx := context.Background()
	_ = h.Handle(ctx, makeUpdate("/subscribe argentina", 100, "dima"))
	_ = h.Handle(ctx, makeUpdate("/subscribe russia", 100, "dima"))
	tg.Sent = nil
	_ = h.Handle(ctx, makeUpdate("/list", 100, "dima"))
	if len(tg.Sent) != 1 {
		t.Fatalf("want 1 message got %d", len(tg.Sent))
	}
	if !strings.Contains(tg.Sent[0].Text, "argentina") {
		t.Error("expected argentina in list")
	}
	if !strings.Contains(tg.Sent[0].Text, disclaimer) {
		t.Error("expected disclaimer")
	}
}

func TestHandleListEmpty(t *testing.T) {
	h, tg := makeHandler()
	_ = h.Handle(context.Background(), makeUpdate("/list", 100, "dima"))
	if len(tg.Sent) != 1 {
		t.Fatalf("want 1 message got %d", len(tg.Sent))
	}
	if !strings.Contains(tg.Sent[0].Text, disclaimer) {
		t.Error("expected disclaimer")
	}
}

func TestHandleHelp(t *testing.T) {
	h, tg := makeHandler()
	_ = h.Handle(context.Background(), makeUpdate("/help", 100, "dima"))
	if len(tg.Sent) != 1 {
		t.Fatalf("want 1 message got %d", len(tg.Sent))
	}
	if !strings.Contains(tg.Sent[0].Text, disclaimer) {
		t.Error("expected disclaimer in help")
	}
}

func TestHandleUnknownCommand(t *testing.T) {
	h, tg := makeHandler()
	_ = h.Handle(context.Background(), makeUpdate("/unknown", 100, "dima"))
	if len(tg.Sent) != 1 {
		t.Fatalf("want 1 message got %d", len(tg.Sent))
	}
	if !strings.Contains(tg.Sent[0].Text, disclaimer) {
		t.Error("expected disclaimer in unknown command reply")
	}
}

func TestHandleNilMessage(t *testing.T) {
	h, tg := makeHandler()
	err := h.Handle(context.Background(), &telegram.TelegramUpdate{UpdateID: 1})
	if err != nil {
		t.Errorf("nil message should not error, got: %v", err)
	}
	if len(tg.Sent) != 0 {
		t.Error("nil message should not send")
	}
}

func TestDisclaimerInSubscribeReply(t *testing.T) {
	h, tg := makeHandler()
	_ = h.Handle(context.Background(), makeUpdate("/subscribe argentina", 100, "dima"))
	if !strings.Contains(tg.Sent[0].Text, "Это не юридическая консультация.") {
		t.Error("exact disclaimer missing from subscribe reply")
	}
}
