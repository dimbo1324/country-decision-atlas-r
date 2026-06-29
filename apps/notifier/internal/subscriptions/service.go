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
	allowed    map[string]struct{}
}

func New(
	subs mongostore.SubscriptionManager,
	identities mongostore.TelegramIdentityRepository,
	allowedCountries []string,
) *Service {
	m := make(map[string]struct{}, len(allowedCountries))
	for _, c := range allowedCountries {
		m[normalizeSlug(c)] = struct{}{}
	}
	return &Service{subs: subs, identities: identities, allowed: m}
}

func normalizeSlug(slug string) string {
	return strings.ToLower(strings.TrimSpace(slug))
}

func (s *Service) resolveCountry(slug string) (string, error) {
	normalized := normalizeSlug(slug)
	if _, ok := s.allowed[normalized]; !ok {
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
