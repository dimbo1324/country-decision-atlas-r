package channels

import (
	"context"

	"github.com/country-decision-atlas/notifier/internal/locale"
	"github.com/country-decision-atlas/notifier/internal/telegram"
)

type ChannelType string

const (
	ChannelTelegram ChannelType = "telegram"
	ChannelEmail    ChannelType = "email"
	ChannelRSS      ChannelType = "rss"
	ChannelWebhook  ChannelType = "webhook"
)

type Recipient struct {
	ChannelType    ChannelType
	RecipientID    string
	TelegramUserID string
	CountrySlug    string
}

type NotificationMessage struct {
	EventKey    string
	EventType   string
	CountrySlug string
	Title       string
	Body        string
}

type DeliveryResult struct {
	Status string
	Error  error
}

type DeliveryChannel interface {
	Type() ChannelType
	Deliver(ctx context.Context, recipient Recipient, message NotificationMessage) DeliveryResult
}

type ChannelRegistry struct {
	channels map[ChannelType]DeliveryChannel
}

func NewRegistry() *ChannelRegistry {
	return &ChannelRegistry{channels: map[ChannelType]DeliveryChannel{}}
}

func (r *ChannelRegistry) Register(channel DeliveryChannel) {
	if channel == nil {
		return
	}
	r.channels[channel.Type()] = channel
}

func (r *ChannelRegistry) Get(channelType ChannelType) (DeliveryChannel, bool) {
	if r == nil {
		return nil, false
	}
	ch, ok := r.channels[channelType]
	return ch, ok
}

type TelegramChannel struct {
	client telegram.Client
}

func NewTelegramChannel(client telegram.Client) *TelegramChannel {
	return &TelegramChannel{client: client}
}

func (c *TelegramChannel) Type() ChannelType {
	return ChannelTelegram
}

func (c *TelegramChannel) Deliver(ctx context.Context, recipient Recipient, message NotificationMessage) DeliveryResult {
	chatID := recipient.TelegramUserID
	if chatID == "" {
		chatID = recipient.RecipientID
	}
	if chatID == "" {
		return DeliveryResult{Status: "failed", Error: ErrInvalidRecipient}
	}
	text := message.Body
	if text == "" {
		// Defensive fallback for a NotificationMessage built without a
		// pre-formatted Body -- the real delivery path (notifier/handler.go)
		// always formats Body per-recipient with the recipient's own
		// locale before calling Deliver, so this has no per-recipient
		// locale to use and falls back to locale.Default.
		text = telegram.FormatMessage(message.CountrySlug, message.EventType, message.Title, locale.Default)
	}
	if err := c.client.SendMessage(ctx, chatID, text); err != nil {
		return DeliveryResult{Status: "failed", Error: err}
	}
	return DeliveryResult{Status: "sent"}
}
