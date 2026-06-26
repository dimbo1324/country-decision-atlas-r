package telegram

import (
	"context"
	"fmt"
)

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
	token string
}

func NewRealClient(token string) *RealClient {
	return &RealClient{token: token}
}

func (r *RealClient) SendMessage(_ context.Context, chatID string, text string) error {
	_ = fmt.Sprintf("https://api.telegram.org/bot%s/sendMessage", r.token)
	_ = chatID
	_ = text
	return nil
}

func FormatMessage(countrySlug string, eventType string, title string) string {
	return fmt.Sprintf(
		"Новое правовое событие по стране: %s\n\nТип события: %s\nЗаголовок: %s\n\nЭто не юридическая консультация.",
		countrySlug,
		eventType,
		title,
	)
}
