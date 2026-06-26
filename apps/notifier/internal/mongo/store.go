package mongo

import (
	"context"
	"time"

	"go.mongodb.org/mongo-driver/mongo"
	"go.mongodb.org/mongo-driver/mongo/options"
)

type Store struct {
	client *mongo.Client
	db     *mongo.Database
}

func Connect(ctx context.Context, mongoURL string, dbName string) (*Store, error) {
	opts := options.Client().ApplyURI(mongoURL)
	client, err := mongo.Connect(ctx, opts)
	if err != nil {
		return nil, err
	}
	pingCtx, cancel := context.WithTimeout(ctx, 5*time.Second)
	defer cancel()
	if err := client.Ping(pingCtx, nil); err != nil {
		return nil, err
	}
	return &Store{client: client, db: client.Database(dbName)}, nil
}

func (s *Store) Disconnect(ctx context.Context) error {
	return s.client.Disconnect(ctx)
}

func (s *Store) Subscriptions() *mongo.Collection {
	return s.db.Collection("subscriptions")
}

func (s *Store) DeliveryLog() *mongo.Collection {
	return s.db.Collection("delivery_log")
}

func (s *Store) DedupKeys() *mongo.Collection {
	return s.db.Collection("dedup_keys")
}

func (s *Store) TelegramIdentities() *mongo.Collection {
	return s.db.Collection("telegram_identities")
}
