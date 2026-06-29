package mongo

import (
	"context"
	"time"

	"go.mongodb.org/mongo-driver/bson"
	"go.mongodb.org/mongo-driver/mongo"
	"go.mongodb.org/mongo-driver/mongo/options"
)

type Subscription struct {
	TelegramUserID string    `bson:"telegram_user_id"`
	CountrySlug    string    `bson:"country_slug"`
	Active         bool      `bson:"active"`
	CreatedAt      time.Time `bson:"created_at"`
	UpdatedAt      time.Time `bson:"updated_at"`
	WebUserID      *string   `bson:"web_user_id"`
}

type SubscriptionRepository interface {
	FindActiveByCountry(ctx context.Context, countrySlug string) ([]*Subscription, error)
}

type SubscriptionManager interface {
	SubscriptionRepository
	CreateOrReactivate(ctx context.Context, telegramUserID string, countrySlug string) (*Subscription, error)
	Deactivate(ctx context.Context, telegramUserID string, countrySlug string) (*Subscription, error)
	ListActive(ctx context.Context, telegramUserID string) ([]*Subscription, error)
	Get(ctx context.Context, telegramUserID string, countrySlug string) (*Subscription, error)
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

func (r *MongoSubscriptionRepository) CreateOrReactivate(ctx context.Context, telegramUserID string, countrySlug string) (*Subscription, error) {
	now := time.Now().UTC()
	filter := bson.M{"telegram_user_id": telegramUserID, "country_slug": countrySlug}
	update := bson.M{
		"$set": bson.M{
			"active":     true,
			"updated_at": now,
		},
		"$setOnInsert": bson.M{
			"telegram_user_id": telegramUserID,
			"country_slug":     countrySlug,
			"created_at":       now,
			"web_user_id":      nil,
		},
	}
	opts := options.FindOneAndUpdate().
		SetUpsert(true).
		SetReturnDocument(options.After)
	var sub Subscription
	err := r.store.Subscriptions().FindOneAndUpdate(ctx, filter, update, opts).Decode(&sub)
	if err != nil {
		return nil, err
	}
	return &sub, nil
}

func (r *MongoSubscriptionRepository) Deactivate(ctx context.Context, telegramUserID string, countrySlug string) (*Subscription, error) {
	now := time.Now().UTC()
	filter := bson.M{"telegram_user_id": telegramUserID, "country_slug": countrySlug}
	update := bson.M{
		"$set": bson.M{
			"active":     false,
			"updated_at": now,
		},
	}
	opts := options.FindOneAndUpdate().SetReturnDocument(options.After)
	var sub Subscription
	err := r.store.Subscriptions().FindOneAndUpdate(ctx, filter, update, opts).Decode(&sub)
	if err != nil {
		if err == mongo.ErrNoDocuments {
			return nil, nil
		}
		return nil, err
	}
	return &sub, nil
}

func (r *MongoSubscriptionRepository) ListActive(ctx context.Context, telegramUserID string) ([]*Subscription, error) {
	filter := bson.M{"telegram_user_id": telegramUserID, "active": true}
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

func (r *MongoSubscriptionRepository) Get(ctx context.Context, telegramUserID string, countrySlug string) (*Subscription, error) {
	filter := bson.M{"telegram_user_id": telegramUserID, "country_slug": countrySlug}
	var sub Subscription
	err := r.store.Subscriptions().FindOne(ctx, filter).Decode(&sub)
	if err != nil {
		if err == mongo.ErrNoDocuments {
			return nil, nil
		}
		return nil, err
	}
	return &sub, nil
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

func (r *InMemorySubscriptionRepository) CreateOrReactivate(_ context.Context, telegramUserID string, countrySlug string) (*Subscription, error) {
	now := time.Now().UTC()
	for _, s := range r.subscriptions {
		if s.TelegramUserID == telegramUserID && s.CountrySlug == countrySlug {
			s.Active = true
			s.UpdatedAt = now
			return s, nil
		}
	}
	sub := &Subscription{
		TelegramUserID: telegramUserID,
		CountrySlug:    countrySlug,
		Active:         true,
		CreatedAt:      now,
		UpdatedAt:      now,
		WebUserID:      nil,
	}
	r.subscriptions = append(r.subscriptions, sub)
	return sub, nil
}

func (r *InMemorySubscriptionRepository) Deactivate(_ context.Context, telegramUserID string, countrySlug string) (*Subscription, error) {
	now := time.Now().UTC()
	for _, s := range r.subscriptions {
		if s.TelegramUserID == telegramUserID && s.CountrySlug == countrySlug {
			s.Active = false
			s.UpdatedAt = now
			return s, nil
		}
	}
	return nil, nil
}

func (r *InMemorySubscriptionRepository) ListActive(_ context.Context, telegramUserID string) ([]*Subscription, error) {
	var results []*Subscription
	for _, s := range r.subscriptions {
		if s.TelegramUserID == telegramUserID && s.Active {
			results = append(results, s)
		}
	}
	return results, nil
}

func (r *InMemorySubscriptionRepository) Get(_ context.Context, telegramUserID string, countrySlug string) (*Subscription, error) {
	for _, s := range r.subscriptions {
		if s.TelegramUserID == telegramUserID && s.CountrySlug == countrySlug {
			return s, nil
		}
	}
	return nil, nil
}

var _ SubscriptionManager = (*MongoSubscriptionRepository)(nil)
var _ SubscriptionManager = (*InMemorySubscriptionRepository)(nil)
