package mongo

import (
	"context"
	"sync"
	"time"

	"go.mongodb.org/mongo-driver/bson"
	"go.mongodb.org/mongo-driver/mongo/options"
)

type TelegramIdentity struct {
	TelegramUserID string    `bson:"telegram_user_id"`
	Username       string    `bson:"username"`
	CreatedAt      time.Time `bson:"created_at"`
	UpdatedAt      time.Time `bson:"updated_at"`
	WebUserID      *string   `bson:"web_user_id"`
}

type TelegramIdentityRepository interface {
	Upsert(ctx context.Context, telegramUserID string, username string) error
}

type MongoTelegramIdentityRepository struct {
	store *Store
}

func NewTelegramIdentityRepository(store *Store) *MongoTelegramIdentityRepository {
	return &MongoTelegramIdentityRepository{store: store}
}

func (r *MongoTelegramIdentityRepository) Upsert(ctx context.Context, telegramUserID string, username string) error {
	now := time.Now().UTC()
	filter := bson.M{"telegram_user_id": telegramUserID}
	update := bson.M{
		"$set": bson.M{
			"username":   username,
			"updated_at": now,
		},
		"$setOnInsert": bson.M{
			"telegram_user_id": telegramUserID,
			"created_at":       now,
			"web_user_id":      nil,
		},
	}
	opts := options.Update().SetUpsert(true)
	_, err := r.store.TelegramIdentities().UpdateOne(ctx, filter, update, opts)
	return err
}

type InMemoryTelegramIdentityRepository struct {
	mu         sync.Mutex
	identities map[string]*TelegramIdentity
}

func NewInMemoryTelegramIdentityRepository() *InMemoryTelegramIdentityRepository {
	return &InMemoryTelegramIdentityRepository{identities: make(map[string]*TelegramIdentity)}
}

func (r *InMemoryTelegramIdentityRepository) Upsert(_ context.Context, telegramUserID string, username string) error {
	r.mu.Lock()
	defer r.mu.Unlock()
	now := time.Now().UTC()
	if existing, ok := r.identities[telegramUserID]; ok {
		existing.Username = username
		existing.UpdatedAt = now
		return nil
	}
	r.identities[telegramUserID] = &TelegramIdentity{
		TelegramUserID: telegramUserID,
		Username:       username,
		CreatedAt:      now,
		UpdatedAt:      now,
		WebUserID:      nil,
	}
	return nil
}

func (r *InMemoryTelegramIdentityRepository) Get(telegramUserID string) *TelegramIdentity {
	r.mu.Lock()
	defer r.mu.Unlock()
	return r.identities[telegramUserID]
}

var _ TelegramIdentityRepository = (*MongoTelegramIdentityRepository)(nil)
var _ TelegramIdentityRepository = (*InMemoryTelegramIdentityRepository)(nil)
