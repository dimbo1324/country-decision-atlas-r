package subscriptions

import (
	"context"
	"errors"
	"testing"

	mongostore "github.com/country-decision-atlas/notifier/internal/mongo"
)

func makeService() (*Service, *mongostore.InMemorySubscriptionRepository, *mongostore.InMemoryTelegramIdentityRepository) {
	subs := mongostore.NewInMemorySubscriptionRepository(nil)
	identities := mongostore.NewInMemoryTelegramIdentityRepository()
	svc := New(subs, identities)
	return svc, subs, identities
}

func TestCreateSubscriptionValid(t *testing.T) {
	svc, _, _ := makeService()
	sub, err := svc.CreateSubscription(context.Background(), "user1", "dima", "argentina")
	if err != nil {
		t.Fatalf("unexpected error: %v", err)
	}
	if sub == nil {
		t.Fatal("expected subscription")
	}
	if sub.CountrySlug != "argentina" {
		t.Errorf("want argentina got %s", sub.CountrySlug)
	}
	if sub.TelegramUserID != "user1" {
		t.Errorf("want user1 got %s", sub.TelegramUserID)
	}
	if !sub.Active {
		t.Error("want active subscription")
	}
	if sub.WebUserID != nil {
		t.Error("want WebUserID=nil")
	}
}

func TestCreateSubscriptionIdempotent(t *testing.T) {
	svc, _, _ := makeService()
	ctx := context.Background()
	_, _ = svc.CreateSubscription(ctx, "user1", "dima", "argentina")
	sub, err := svc.CreateSubscription(ctx, "user1", "dima", "argentina")
	if err != nil {
		t.Fatalf("unexpected error on repeat: %v", err)
	}
	if !sub.Active {
		t.Error("want active on repeat subscribe")
	}
}

func TestCreateSubscriptionReactivates(t *testing.T) {
	svc, subs, _ := makeService()
	ctx := context.Background()
	_, _ = svc.CreateSubscription(ctx, "user1", "dima", "argentina")
	_, _ = svc.DeleteSubscription(ctx, "user1", "argentina")
	sub, err := svc.CreateSubscription(ctx, "user1", "dima", "argentina")
	if err != nil {
		t.Fatalf("unexpected error: %v", err)
	}
	if !sub.Active {
		t.Error("want reactivated subscription")
	}
	_ = subs
}

func TestCreateSubscriptionAcceptsCountryNotInAnyStaticList(t *testing.T) {
	// P2-13, Аудит-эпизод 5: the notifier no longer validates against a
	// hardcoded env-var list of countries, so a slug never seen before
	// (i.e. not one of the three demo countries) must still succeed - the
	// API is the source of truth for which countries actually exist.
	svc, _, _ := makeService()
	sub, err := svc.CreateSubscription(context.Background(), "user1", "dima", "germany")
	if err != nil {
		t.Fatalf("unexpected error: %v", err)
	}
	if sub.CountrySlug != "germany" {
		t.Errorf("want germany got %s", sub.CountrySlug)
	}
}

func TestCreateSubscriptionEmptyCountryIsRejected(t *testing.T) {
	svc, _, _ := makeService()
	_, err := svc.CreateSubscription(context.Background(), "user1", "dima", "   ")
	if !errors.Is(err, ErrUnknownCountry) {
		t.Errorf("want ErrUnknownCountry got %v", err)
	}
}

func TestDeleteSubscriptionDeactivates(t *testing.T) {
	svc, _, _ := makeService()
	ctx := context.Background()
	_, _ = svc.CreateSubscription(ctx, "user1", "dima", "argentina")
	sub, err := svc.DeleteSubscription(ctx, "user1", "argentina")
	if err != nil {
		t.Fatalf("unexpected error: %v", err)
	}
	if sub == nil {
		t.Fatal("expected subscription returned")
	}
	if sub.Active {
		t.Error("want inactive after delete")
	}
}

func TestDeleteSubscriptionIdempotent(t *testing.T) {
	svc, _, _ := makeService()
	ctx := context.Background()
	sub, err := svc.DeleteSubscription(ctx, "user1", "argentina")
	if err != nil {
		t.Fatalf("unexpected error on missing: %v", err)
	}
	if sub != nil {
		t.Error("want nil for missing subscription")
	}
}

func TestDeleteSubscriptionEmptyCountryIsRejected(t *testing.T) {
	svc, _, _ := makeService()
	_, err := svc.DeleteSubscription(context.Background(), "user1", "   ")
	if !errors.Is(err, ErrUnknownCountry) {
		t.Errorf("want ErrUnknownCountry got %v", err)
	}
}

func TestListSubscriptionsReturnsActive(t *testing.T) {
	svc, _, _ := makeService()
	ctx := context.Background()
	_, _ = svc.CreateSubscription(ctx, "user1", "dima", "argentina")
	_, _ = svc.CreateSubscription(ctx, "user1", "dima", "russia")
	_, _ = svc.DeleteSubscription(ctx, "user1", "russia")

	subs, err := svc.ListSubscriptions(ctx, "user1")
	if err != nil {
		t.Fatalf("unexpected error: %v", err)
	}
	if len(subs) != 1 {
		t.Errorf("want 1 active subscription got %d", len(subs))
	}
	if subs[0].CountrySlug != "argentina" {
		t.Errorf("want argentina got %s", subs[0].CountrySlug)
	}
}

func TestIdentityIsUpserted(t *testing.T) {
	svc, _, identities := makeService()
	ctx := context.Background()
	_, _ = svc.CreateSubscription(ctx, "user1", "dima", "argentina")
	identity := identities.Get("user1")
	if identity == nil {
		t.Fatal("expected identity to be upserted")
	}
	if identity.Username != "dima" {
		t.Errorf("want username dima got %s", identity.Username)
	}
	if identity.WebUserID != nil {
		t.Error("want WebUserID=nil")
	}
}

func TestWebUserIDRemainsNil(t *testing.T) {
	svc, _, _ := makeService()
	sub, _ := svc.CreateSubscription(context.Background(), "user1", "dima", "argentina")
	if sub.WebUserID != nil {
		t.Error("want WebUserID=nil")
	}
}
