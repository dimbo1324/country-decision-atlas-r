package channels

import (
	"context"
	"errors"
	"testing"

	"github.com/country-decision-atlas/notifier/internal/telegram"
)

func TestRegistryReturnsRegisteredTelegramChannel(t *testing.T) {
	registry := NewRegistry()
	channel := NewTelegramChannel(&telegram.FakeClient{})
	registry.Register(channel)

	got, ok := registry.Get(ChannelTelegram)
	if !ok {
		t.Fatal("expected telegram channel to be registered")
	}
	if got.Type() != ChannelTelegram {
		t.Errorf("want telegram got %s", got.Type())
	}
}

func TestRegistryUnsupportedChannelNotRegistered(t *testing.T) {
	registry := NewRegistry()

	if _, ok := registry.Get(ChannelEmail); ok {
		t.Fatal("email channel must stay reserved, not registered")
	}
}

func TestTelegramChannelFakeDelivery(t *testing.T) {
	client := &telegram.FakeClient{}
	channel := NewTelegramChannel(client)

	result := channel.Deliver(context.Background(), Recipient{
		ChannelType:    ChannelTelegram,
		TelegramUserID: "user1",
	}, NotificationMessage{CountrySlug: "argentina", EventType: "legal_signal.published", Title: "Title"})

	if result.Error != nil {
		t.Fatalf("unexpected delivery error: %v", result.Error)
	}
	if result.Status != "sent" {
		t.Errorf("want sent got %s", result.Status)
	}
	if len(client.Sent) != 1 {
		t.Fatalf("want 1 sent message got %d", len(client.Sent))
	}
}

func TestTelegramChannelInvalidRecipient(t *testing.T) {
	channel := NewTelegramChannel(&telegram.FakeClient{})

	result := channel.Deliver(context.Background(), Recipient{ChannelType: ChannelTelegram}, NotificationMessage{})

	if !errors.Is(result.Error, ErrInvalidRecipient) {
		t.Fatalf("want ErrInvalidRecipient got %v", result.Error)
	}
	if result.Status != "failed" {
		t.Errorf("want failed got %s", result.Status)
	}
}
