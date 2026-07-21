package subscriptions

import (
	"context"
	"errors"
	"strings"

	mongostore "github.com/country-decision-atlas/notifier/internal/mongo"
)

var ErrUnknownCountry = errors.New("unknown country")

type Service struct {
	subs       mongostore.SubscriptionManager
	identities mongostore.TelegramIdentityRepository
}

// New no longer takes a static allow-list of country slugs (P2-13,
// Аудит-эпизод 5): the API already validates country slugs against the
// database when a subscription is created there, and the notifier has no
// way to keep an env-var list in sync with countries added later without a
// restart. A subscription to an unknown slug is inert — it simply never
// matches a future domain event — so there is no correctness or security
// reason to reject it here.
func New(
	subs mongostore.SubscriptionManager,
	identities mongostore.TelegramIdentityRepository,
) *Service {
	return &Service{subs: subs, identities: identities}
}

func normalizeSlug(slug string) string {
	return strings.ToLower(strings.TrimSpace(slug))
}

func (s *Service) resolveCountry(slug string) (string, error) {
	normalized := normalizeSlug(slug)
	if normalized == "" {
		return "", ErrUnknownCountry
	}
	return normalized, nil
}

func (s *Service) CreateSubscription(ctx context.Context, telegramUserID string, username string, countrySlug string) (*mongostore.Subscription, error) {
	slug, err := s.resolveCountry(countrySlug)
	if err != nil {
		return nil, err
	}
	if err := s.identities.Upsert(ctx, telegramUserID, username); err != nil {
		return nil, err
	}
	return s.subs.CreateOrReactivate(ctx, telegramUserID, slug)
}

func (s *Service) DeleteSubscription(ctx context.Context, telegramUserID string, countrySlug string) (*mongostore.Subscription, error) {
	slug, err := s.resolveCountry(countrySlug)
	if err != nil {
		return nil, err
	}
	return s.subs.Deactivate(ctx, telegramUserID, slug)
}

func (s *Service) ListSubscriptions(ctx context.Context, telegramUserID string) ([]*mongostore.Subscription, error) {
	return s.subs.ListActive(ctx, telegramUserID)
}

// SetTelegramLocale persists the notification locale resolved from a live
// bot interaction's `language_code` (internal/telegram/bot.Handler calls
// this on every incoming update). Deliberately separate from
// CreateSubscription: subscriptions can also be created via gRPC on behalf
// of a web user, which has no Telegram update -- and therefore no
// language_code -- to resolve a locale from at all.
func (s *Service) SetTelegramLocale(ctx context.Context, telegramUserID string, resolvedLocale string) error {
	return s.identities.SetLocale(ctx, telegramUserID, resolvedLocale)
}

// TelegramLocale returns the recipient's stored notification locale
// (locale.Default if never captured).
func (s *Service) TelegramLocale(ctx context.Context, telegramUserID string) (string, error) {
	return s.identities.GetLocale(ctx, telegramUserID)
}
