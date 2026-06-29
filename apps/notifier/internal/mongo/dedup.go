package mongo

import (
	"context"
	"sync"
	"time"

	"go.mongodb.org/mongo-driver/bson"
	"go.mongodb.org/mongo-driver/mongo"
	"go.mongodb.org/mongo-driver/mongo/options"
)

type DedupKey struct {
	EventKey    string    `bson:"event_key"`
	ProcessedAt time.Time `bson:"processed_at"`
}

type DedupRepository interface {
	TryInsert(ctx context.Context, eventKey string) (inserted bool, err error)
	Exists(ctx context.Context, eventKey string) (bool, error)
}

type MongoDedupRepository struct {
	store *Store
}

func NewDedupRepository(store *Store) *MongoDedupRepository {
	return &MongoDedupRepository{store: store}
}

func (r *MongoDedupRepository) TryInsert(ctx context.Context, eventKey string) (bool, error) {
	doc := DedupKey{EventKey: eventKey, ProcessedAt: time.Now().UTC()}
	_, err := r.store.DedupKeys().InsertOne(ctx, doc)
	if err != nil {
		if mongo.IsDuplicateKeyError(err) {
			return false, nil
		}
		return false, err
	}
	return true, nil
}

func (r *MongoDedupRepository) Exists(ctx context.Context, eventKey string) (bool, error) {
	count, err := r.store.DedupKeys().CountDocuments(
		ctx,
		bson.M{"event_key": eventKey},
		options.Count().SetLimit(1),
	)
	if err != nil {
		return false, err
	}
	return count > 0, nil
}

type InMemoryDedupRepository struct {
	mu   sync.Mutex
	seen map[string]bool
}

func NewInMemoryDedupRepository() *InMemoryDedupRepository {
	return &InMemoryDedupRepository{seen: make(map[string]bool)}
}

func (r *InMemoryDedupRepository) TryInsert(_ context.Context, eventKey string) (bool, error) {
	r.mu.Lock()
	defer r.mu.Unlock()
	if r.seen[eventKey] {
		return false, nil
	}
	r.seen[eventKey] = true
	return true, nil
}

func (r *InMemoryDedupRepository) Exists(_ context.Context, eventKey string) (bool, error) {
	r.mu.Lock()
	defer r.mu.Unlock()
	return r.seen[eventKey], nil
}

var _ DedupRepository = (*MongoDedupRepository)(nil)
var _ DedupRepository = (*InMemoryDedupRepository)(nil)
