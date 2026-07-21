package telegram

import (
	"bytes"
	"context"
	"encoding/json"
	"fmt"
	"net/http"
	"time"

	"github.com/country-decision-atlas/notifier/internal/locale"
)

// Disclaimer is the pre-i18n Russian-only text, kept for callers (and
// tests) that referenced it directly before locale support existed;
// DisclaimerFor(loc) is the locale-aware replacement.
const Disclaimer = "Это не юридическая консультация."

var disclaimerByLocale = map[string]string{
	locale.RU: Disclaimer,
	locale.EN: "This is not legal advice.",
	locale.ES: "Esto no es asesoramiento legal.",
}

// DisclaimerFor returns the disclaimer text for a resolved locale, falling
// back to locale.Default for anything not in the catalog.
func DisclaimerFor(loc string) string {
	if text, ok := disclaimerByLocale[loc]; ok {
		return text
	}
	return disclaimerByLocale[locale.Default]
}

type Client interface {
	SendMessage(ctx context.Context, chatID string, text string) error
}

type FakeClient struct {
	Sent []SentMessage
}

type SentMessage struct {
	ChatID string
	Text   string
}

func (f *FakeClient) SendMessage(_ context.Context, chatID string, text string) error {
	f.Sent = append(f.Sent, SentMessage{ChatID: chatID, Text: text})
	return nil
}

type RealClient struct {
	token  string
	client *http.Client
}

func NewRealClient(token string) *RealClient {
	return &RealClient{token: token, client: &http.Client{Timeout: 10 * time.Second}}
}

func (r *RealClient) SendMessage(ctx context.Context, chatID string, text string) error {
	payload, err := json.Marshal(map[string]string{"chat_id": chatID, "text": text})
	if err != nil {
		return err
	}
	url := fmt.Sprintf("https://api.telegram.org/bot%s/sendMessage", r.token)
	req, err := http.NewRequestWithContext(ctx, http.MethodPost, url, bytes.NewReader(payload))
	if err != nil {
		return err
	}
	req.Header.Set("Content-Type", "application/json")
	resp, err := r.client.Do(req)
	if err != nil {
		return err
	}
	defer func() { _ = resp.Body.Close() }()
	if resp.StatusCode < 200 || resp.StatusCode >= 300 {
		return fmt.Errorf("telegram api returned status %d", resp.StatusCode)
	}
	return nil
}

// FormatMessage renders an event-notification body in the given resolved
// locale (see internal/locale.Resolve), falling back to locale.Default for
// anything unrecognized.
func FormatMessage(countrySlug string, eventType string, title string, loc string) string {
	disclaimer := DisclaimerFor(loc)
	if eventType == "trip_reminder_due" {
		switch loc {
		case locale.EN:
			return fmt.Sprintf(
				"Relocation plan reminder\n\n%s\nCountry: %s\n\n%s",
				title, countrySlug, disclaimer,
			)
		case locale.ES:
			return fmt.Sprintf(
				"Recordatorio del plan de mudanza\n\n%s\nPaís: %s\n\n%s",
				title, countrySlug, disclaimer,
			)
		default:
			return fmt.Sprintf(
				"Напоминание по плану переезда\n\n%s\nСтрана: %s\n\n%s",
				title, countrySlug, disclaimer,
			)
		}
	}
	switch loc {
	case locale.EN:
		return fmt.Sprintf(
			"New legal signal for country: %s\n\nEvent type: %s\nTitle: %s\n\n%s",
			countrySlug, eventType, title, disclaimer,
		)
	case locale.ES:
		return fmt.Sprintf(
			"Nueva señal legal para el país: %s\n\nTipo de evento: %s\nTítulo: %s\n\n%s",
			countrySlug, eventType, title, disclaimer,
		)
	default:
		return fmt.Sprintf(
			"Новое правовое событие по стране: %s\n\nТип события: %s\nЗаголовок: %s\n\n%s",
			countrySlug, eventType, title, disclaimer,
		)
	}
}
