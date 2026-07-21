package bot

import (
	"context"
	"errors"
	"strings"
	"testing"
	"time"

	mongostore "github.com/country-decision-atlas/notifier/internal/mongo"
	"github.com/country-decision-atlas/notifier/internal/subscriptions"
	"github.com/country-decision-atlas/notifier/internal/telegram"
)

func makeHandler() (*Handler, *telegram.FakeClient) {
	h, tg, _ := makeHandlerWithLinkCodes()
	return h, tg
}

func makeHandlerWithLinkCodes() (*Handler, *telegram.FakeClient, *mongostore.InMemoryTelegramLinkCodeRepository) {
	subsRepo := mongostore.NewInMemorySubscriptionRepository(nil)
	identities := mongostore.NewInMemoryTelegramIdentityRepository()
	svc := subscriptions.New(subsRepo, identities)
	tg := &telegram.FakeClient{}
	linkCodes := mongostore.NewInMemoryTelegramLinkCodeRepository()
	h := New(svc, tg, linkCodes, 10*time.Minute)
	return h, tg, linkCodes
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

func extractLinkCode(t *testing.T, reply string) string {
	t.Helper()
	for _, word := range strings.Fields(reply) {
		if len(word) == 6 {
			allDigits := true
			for _, r := range word {
				if r < '0' || r > '9' {
					allDigits = false
					break
				}
			}
			if allDigits {
				return word
			}
		}
	}
	t.Fatalf("no 6-digit code found in reply: %s", reply)
	return ""
}

func TestHandleWebLinkRepliesWithSixDigitCode(t *testing.T) {
	h, tg := makeHandler()
	_ = h.Handle(context.Background(), makeUpdate("/web_link", 100, "dima"))
	if len(tg.Sent) != 1 {
		t.Fatalf("want 1 message got %d", len(tg.Sent))
	}
	code := extractLinkCode(t, tg.Sent[0].Text)
	if len(code) != 6 {
		t.Errorf("want 6-digit code got %q", code)
	}
	if !strings.Contains(tg.Sent[0].Text, disclaimer) {
		t.Error("expected disclaimer in web_link reply")
	}
}

func TestHandleWebLinkGeneratesConsumableCode(t *testing.T) {
	h, tg, linkCodes := makeHandlerWithLinkCodes()
	_ = h.Handle(context.Background(), makeUpdate("/web_link", 200, "dima"))
	code := extractLinkCode(t, tg.Sent[0].Text)

	telegramUserID, err := linkCodes.Consume(context.Background(), mongostore.HashLinkCode(code))
	if err != nil {
		t.Fatalf("unexpected error consuming generated code: %v", err)
	}
	if telegramUserID != "200" {
		t.Errorf("want telegram user id 200 got %s", telegramUserID)
	}
}

func TestHandleWebLinkCodeConsumedOnceOnly(t *testing.T) {
	h, tg, linkCodes := makeHandlerWithLinkCodes()
	_ = h.Handle(context.Background(), makeUpdate("/web_link", 300, "dima"))
	code := extractLinkCode(t, tg.Sent[0].Text)
	hash := mongostore.HashLinkCode(code)

	if _, err := linkCodes.Consume(context.Background(), hash); err != nil {
		t.Fatalf("first consume: %v", err)
	}
	if _, err := linkCodes.Consume(context.Background(), hash); !errors.Is(err, mongostore.ErrLinkCodeConsumed) {
		t.Errorf("want ErrLinkCodeConsumed on second consume got %v", err)
	}
}

func TestHandleWebLinkMentionsExpiryMinutes(t *testing.T) {
	h, tg := makeHandler()
	_ = h.Handle(context.Background(), makeUpdate("/web_link", 100, "dima"))
	if !strings.Contains(tg.Sent[0].Text, "10 минут") {
		t.Errorf("expected reply to mention 10 minute expiry, got: %s", tg.Sent[0].Text)
	}
}

func makeUpdateWithLocale(text string, userID int64, username string, languageCode string) *telegram.TelegramUpdate {
	return &telegram.TelegramUpdate{
		UpdateID: 1,
		Message: &telegram.TelegramMessage{
			Text: text,
			Chat: telegram.TelegramChat{ID: userID},
			From: &telegram.TelegramUser{ID: userID, Username: username, LanguageCode: languageCode},
		},
	}
}

func TestHandleSubscribeRepliesInEnglishForEnglishLanguageCode(t *testing.T) {
	h, tg := makeHandler()
	_ = h.Handle(context.Background(), makeUpdateWithLocale("/subscribe argentina", 100, "dima", "en-US"))
	if !strings.Contains(tg.Sent[0].Text, "You are now subscribed") {
		t.Errorf("expected English reply, got: %s", tg.Sent[0].Text)
	}
	if !strings.Contains(tg.Sent[0].Text, "This is not legal advice.") {
		t.Errorf("expected English disclaimer, got: %s", tg.Sent[0].Text)
	}
}

func TestHandleSubscribeRepliesInSpanishForSpanishLanguageCode(t *testing.T) {
	h, tg := makeHandler()
	_ = h.Handle(context.Background(), makeUpdateWithLocale("/subscribe argentina", 100, "dima", "es"))
	if !strings.Contains(tg.Sent[0].Text, "Te has suscrito") {
		t.Errorf("expected Spanish reply, got: %s", tg.Sent[0].Text)
	}
}

func TestHandleUnknownLanguageCodeFallsBackToRussian(t *testing.T) {
	h, tg := makeHandler()
	_ = h.Handle(context.Background(), makeUpdateWithLocale("/subscribe argentina", 100, "dima", "fr-FR"))
	if !strings.Contains(tg.Sent[0].Text, disclaimer) {
		t.Errorf("expected Russian (default) disclaimer for unrecognized language, got: %s", tg.Sent[0].Text)
	}
}

func TestSetTelegramLocalePersistsAcrossInteractions(t *testing.T) {
	subsRepo := mongostore.NewInMemorySubscriptionRepository(nil)
	identities := mongostore.NewInMemoryTelegramIdentityRepository()
	svc := subscriptions.New(subsRepo, identities)
	tg := &telegram.FakeClient{}
	linkCodes := mongostore.NewInMemoryTelegramLinkCodeRepository()
	h := New(svc, tg, linkCodes, 10*time.Minute)

	ctx := context.Background()
	_ = h.Handle(ctx, makeUpdateWithLocale("/help", 100, "dima", "en"))

	got, err := svc.TelegramLocale(ctx, "100")
	if err != nil {
		t.Fatalf("unexpected error: %v", err)
	}
	if got != "en" {
		t.Errorf("want stored locale %q got %q", "en", got)
	}
}
