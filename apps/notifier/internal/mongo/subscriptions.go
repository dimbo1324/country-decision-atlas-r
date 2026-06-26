package mongo

import (
	"context"
	"time"

	"go.mongodb.org/mongo-driver/bson"
	"go.mongodb.org/mongo-driver/mongo"
)

type Subscription struct {
	TelegramUserID string    `bson:"telegram_user_id"`
	CountrySlug    string    `bson:"country_slug"`
	Active         bool      `bson:"active"`
	CreatedAt      time.Time `bson:"created_at"`
	WebUserID      *string   `bson:"web_user_id"`
}

type SubscriptionRepository interface {
	FindActiveByCountry(ctx context.Context, countrySlug string) ([]*Subscription, error)
}

type MongoSubscriptionRepository struct {
	store *Store
}

func NewSubscriptionRepository(store *Store) *MongoSubscriptionRepository {
	return &MongoSubscriptionRepository{store: store}
}

func (r *MongoSubscriptionRepository) FindActiveByCountry(ctx context.Context, countrySlug string) ([]*Subscription, error) {
	filter := bson.M{"country_slug": countrySlug, "active": true}
	cur, err := r.store.Subscriptions().Find(ctx, filter)
	if err != nil {
		return nil, err
	}
	defer cur.Close(ctx)
	var results []*Subscription
	if err := cur.All(ctx, &results); err != nil {
		return nil, err
	}
	return results, nil
}

type InMemorySubscriptionRepository struct {
	subscriptions []*Subscription
}

func NewInMemorySubscriptionRepository(subs []*Subscription) *InMemorySubscriptionRepository {
	return &InMemorySubscriptionRepository{subscriptions: subs}
}

func (r *InMemorySubscriptionRepository) FindActiveByCountry(_ context.Context, countrySlug string) ([]*Subscription, error) {
	var results []*Subscription
	for _, s := range r.subscriptions {
		if s.CountrySlug == countrySlug && s.Active {
			results = append(results, s)
		}
	}
	return results, nil
}

var _ SubscriptionRepository = (*MongoSubscriptionRepository)(nil)
var _ SubscriptionRepository = (*InMemorySubscriptionRepository)(nil)

func InsertSubscription(ctx context.Context, store *Store, sub *Subscription) error {
	if sub.CreatedAt.IsZero() {
		sub.CreatedAt = time.Now().UTC()
	}
	_, err := store.Subscriptions().InsertOne(ctx, sub)
	if err != nil {
		if mongo.IsDuplicateKeyError(err) {
			return nil
		}
		return err
	}
	return nil
}
