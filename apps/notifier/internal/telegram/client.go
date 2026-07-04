package telegram

import (
	"bytes"
	"context"
	"encoding/json"
	"fmt"
	"net/http"
	"time"
)

const Disclaimer = "Это не юридическая консультация."

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

func FormatMessage(countrySlug string, eventType string, title string) string {
	if eventType == "trip_reminder_due" {
		return fmt.Sprintf(
			"Напоминание по плану переезда\n\n%s\nСтрана: %s\n\n%s",
			title,
			countrySlug,
			Disclaimer,
		)
	}
	return fmt.Sprintf(
		"Новое правовое событие по стране: %s\n\nТип события: %s\nЗаголовок: %s\n\n%s",
		countrySlug,
		eventType,
		title,
		Disclaimer,
	)
}
