package mongo

import (
	"context"

	"go.mongodb.org/mongo-driver/bson"
	mongodriver "go.mongodb.org/mongo-driver/mongo"
	"go.mongodb.org/mongo-driver/mongo/options"
)

func EnsureIndexes(ctx context.Context, store *Store) error {
	if err := ensureDedupIndexes(ctx, store); err != nil {
		return err
	}
	if err := ensureSubscriptionIndexes(ctx, store); err != nil {
		return err
	}
	if err := ensureDeliveryLogIndexes(ctx, store); err != nil {
		return err
	}
	if err := ensureTelegramIdentityIndexes(ctx, store); err != nil {
		return err
	}
	if err := ensureDeadLetterIndexes(ctx, store); err != nil {
		return err
	}
	if err := ensureTelegramLinkCodeIndexes(ctx, store); err != nil {
		return err
	}
	return nil
}

func ensureDedupIndexes(ctx context.Context, store *Store) error {
	_, err := store.DedupKeys().Indexes().CreateOne(ctx, mongodriver.IndexModel{
		Keys:    bson.D{{Key: "event_key", Value: 1}},
		Options: options.Index().SetUnique(true),
	})
	return err
}

func ensureSubscriptionIndexes(ctx context.Context, store *Store) error {
	coll := store.Subscriptions()
	_, err := coll.Indexes().CreateMany(ctx, []mongodriver.IndexModel{
		{
			Keys:    bson.D{{Key: "telegram_user_id", Value: 1}, {Key: "country_slug", Value: 1}},
			Options: options.Index().SetUnique(true),
		},
		{
			Keys: bson.D{{Key: "country_slug", Value: 1}},
		},
		{
			Keys: bson.D{{Key: "channel_type", Value: 1}, {Key: "recipient_id", Value: 1}},
		},
	})
	return err
}

func ensureDeliveryLogIndexes(ctx context.Context, store *Store) error {
	coll := store.DeliveryLog()
	_, err := coll.Indexes().CreateMany(ctx, []mongodriver.IndexModel{
		{Keys: bson.D{{Key: "event_key", Value: 1}}},
		{Keys: bson.D{{Key: "telegram_user_id", Value: 1}}},
		{Keys: bson.D{{Key: "channel_type", Value: 1}, {Key: "recipient_id", Value: 1}}},
	})
	return err
}

func ensureTelegramIdentityIndexes(ctx context.Context, store *Store) error {
	_, err := store.TelegramIdentities().Indexes().CreateOne(ctx, mongodriver.IndexModel{
		Keys:    bson.D{{Key: "telegram_user_id", Value: 1}},
		Options: options.Index().SetUnique(true),
	})
	return err
}

func ensureTelegramLinkCodeIndexes(ctx context.Context, store *Store) error {
	coll := store.TelegramLinkCodes()
	_, err := coll.Indexes().CreateMany(ctx, []mongodriver.IndexModel{
		{Keys: bson.D{{Key: "code_hash", Value: 1}}},
		{
			Keys:    bson.D{{Key: "expires_at", Value: 1}},
			Options: options.Index().SetExpireAfterSeconds(0),
		},
	})
	return err
}

func ensureDeadLetterIndexes(ctx context.Context, store *Store) error {
	coll := store.DeadLetters()
	_, err := coll.Indexes().CreateMany(ctx, []mongodriver.IndexModel{
		{Keys: bson.D{{Key: "event_key", Value: 1}}},
		{Keys: bson.D{{Key: "stage", Value: 1}}},
		{Keys: bson.D{{Key: "status", Value: 1}}},
		{Keys: bson.D{{Key: "created_at", Value: -1}}},
		{Keys: bson.D{{Key: "country_slug", Value: 1}}},
		{
			Keys: bson.D{
				{Key: "event_key", Value: 1},
				{Key: "stage", Value: 1},
				{Key: "channel_type", Value: 1},
				{Key: "recipient_id", Value: 1},
			},
			Options: options.Index().SetUnique(true),
		},
	})
	return err
}
