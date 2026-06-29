package subscriptions

import (
	"context"
	"errors"

	mongostore "github.com/country-decision-atlas/notifier/internal/mongo"
)

var ErrUnknownCountry = errors.New("unknown country")
var ErrNotSubscribed = errors.New("not subscribed")

type Result struct {
	Subscription *mongostore.Subscription
}

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
		m[c] = struct{}{}
	}
	return &Service{subs: subs, identities: identities, allowed: m}
}

func (s *Service) validateCountry(slug string) error {
	if _, ok := s.allowed[slug]; !ok {
		return ErrUnknownCountry
	}
	return nil
}

func (s *Service) CreateSubscription(ctx context.Context, telegramUserID string, username string, countrySlug string) (*mongostore.Subscription, error) {
	if err := s.validateCountry(countrySlug); err != nil {
		return nil, err
	}
	if err := s.identities.Upsert(ctx, telegramUserID, username); err != nil {
		return nil, err
	}
	return s.subs.CreateOrReactivate(ctx, telegramUserID, countrySlug)
}

func (s *Service) DeleteSubscription(ctx context.Context, telegramUserID string, countrySlug string) (*mongostore.Subscription, error) {
	if err := s.validateCountry(countrySlug); err != nil {
		return nil, err
	}
	sub, err := s.subs.Deactivate(ctx, telegramUserID, countrySlug)
	if err != nil {
		return nil, err
	}
	return sub, nil
}

func (s *Service) ListSubscriptions(ctx context.Context, telegramUserID string) ([]*mongostore.Subscription, error) {
	return s.subs.ListActive(ctx, telegramUserID)
}
