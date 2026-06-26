package mongo

import (
	"context"
	"time"
)

type DeliveryLogEntry struct {
	EventKey       string    `bson:"event_key"`
	TelegramUserID string    `bson:"telegram_user_id"`
	CountrySlug    string    `bson:"country_slug"`
	Status         string    `bson:"status"`
	SentAt         time.Time `bson:"sent_at"`
	Error          *string   `bson:"error"`
}

type DeliveryLogRepository interface {
	Insert(ctx context.Context, entry *DeliveryLogEntry) error
}

type MongoDeliveryLogRepository struct {
	store *Store
}

func NewDeliveryLogRepository(store *Store) *MongoDeliveryLogRepository {
	return &MongoDeliveryLogRepository{store: store}
}

func (r *MongoDeliveryLogRepository) Insert(ctx context.Context, entry *DeliveryLogEntry) error {
	if entry.SentAt.IsZero() {
		entry.SentAt = time.Now().UTC()
	}
	_, err := r.store.DeliveryLog().InsertOne(ctx, entry)
	return err
}

type InMemoryDeliveryLogRepository struct {
	Entries []*DeliveryLogEntry
}

func NewInMemoryDeliveryLogRepository() *InMemoryDeliveryLogRepository {
	return &InMemoryDeliveryLogRepository{}
}

func (r *InMemoryDeliveryLogRepository) Insert(_ context.Context, entry *DeliveryLogEntry) error {
	if entry.SentAt.IsZero() {
		entry.SentAt = time.Now().UTC()
	}
	r.Entries = append(r.Entries, entry)
	return nil
}

var _ DeliveryLogRepository = (*MongoDeliveryLogRepository)(nil)
var _ DeliveryLogRepository = (*InMemoryDeliveryLogRepository)(nil)
