package mongo

import (
	"context"
	"sync"
	"time"

	"go.mongodb.org/mongo-driver/bson"
	"go.mongodb.org/mongo-driver/mongo/options"
)

type DeliveryLogEntry struct {
	EventKey       string    `bson:"event_key"`
	TelegramUserID string    `bson:"telegram_user_id"`
	CountrySlug    string    `bson:"country_slug"`
	Status         string    `bson:"status"`
	SentAt         time.Time `bson:"sent_at"`
	Error          *string   `bson:"error"`
}

type DeliveryLogQuery struct {
	TelegramUserID string
	EventKey       string
	CountrySlug    string
	Limit          int32
}

type DeliveryLogRepository interface {
	Insert(ctx context.Context, entry *DeliveryLogEntry) error
	FindByUser(ctx context.Context, q DeliveryLogQuery) ([]*DeliveryLogEntry, error)
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

func (r *MongoDeliveryLogRepository) FindByUser(ctx context.Context, q DeliveryLogQuery) ([]*DeliveryLogEntry, error) {
	filter := bson.M{"telegram_user_id": q.TelegramUserID}
	if q.EventKey != "" {
		filter["event_key"] = q.EventKey
	}
	if q.CountrySlug != "" {
		filter["country_slug"] = q.CountrySlug
	}
	limit := int64(q.Limit)
	if limit <= 0 {
		limit = 50
	}
	if limit > 100 {
		limit = 100
	}
	opts := options.Find().SetLimit(limit).SetSort(bson.D{{Key: "sent_at", Value: -1}})
	cur, err := r.store.DeliveryLog().Find(ctx, filter, opts)
	if err != nil {
		return nil, err
	}
	defer cur.Close(ctx)
	var results []*DeliveryLogEntry
	if err := cur.All(ctx, &results); err != nil {
		return nil, err
	}
	return results, nil
}

type InMemoryDeliveryLogRepository struct {
	mu      sync.Mutex
	Entries []*DeliveryLogEntry
}

func NewInMemoryDeliveryLogRepository() *InMemoryDeliveryLogRepository {
	return &InMemoryDeliveryLogRepository{}
}

func (r *InMemoryDeliveryLogRepository) Insert(_ context.Context, entry *DeliveryLogEntry) error {
	r.mu.Lock()
	defer r.mu.Unlock()
	if entry.SentAt.IsZero() {
		entry.SentAt = time.Now().UTC()
	}
	r.Entries = append(r.Entries, entry)
	return nil
}

func (r *InMemoryDeliveryLogRepository) FindByUser(_ context.Context, q DeliveryLogQuery) ([]*DeliveryLogEntry, error) {
	r.mu.Lock()
	defer r.mu.Unlock()
	limit := int(q.Limit)
	if limit <= 0 {
		limit = 50
	}
	if limit > 100 {
		limit = 100
	}
	var results []*DeliveryLogEntry
	for i := len(r.Entries) - 1; i >= 0 && len(results) < limit; i-- {
		e := r.Entries[i]
		if e.TelegramUserID != q.TelegramUserID {
			continue
		}
		if q.EventKey != "" && e.EventKey != q.EventKey {
			continue
		}
		if q.CountrySlug != "" && e.CountrySlug != q.CountrySlug {
			continue
		}
		results = append(results, e)
	}
	return results, nil
}

var _ DeliveryLogRepository = (*MongoDeliveryLogRepository)(nil)
var _ DeliveryLogRepository = (*InMemoryDeliveryLogRepository)(nil)
