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
	})
	return err
}

func ensureDeliveryLogIndexes(ctx context.Context, store *Store) error {
	coll := store.DeliveryLog()
	_, err := coll.Indexes().CreateMany(ctx, []mongodriver.IndexModel{
		{Keys: bson.D{{Key: "event_key", Value: 1}}},
		{Keys: bson.D{{Key: "telegram_user_id", Value: 1}}},
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
