package mongo

import (
	"context"
	"crypto/sha256"
	"encoding/hex"
	"errors"
	"sync"
	"time"

	"go.mongodb.org/mongo-driver/bson"
	"go.mongodb.org/mongo-driver/mongo"
)

type TelegramLinkCode struct {
	TelegramUserID string     `bson:"telegram_user_id"`
	CodeHash       string     `bson:"code_hash"`
	CreatedAt      time.Time  `bson:"created_at"`
	ExpiresAt      time.Time  `bson:"expires_at"`
	ConsumedAt     *time.Time `bson:"consumed_at"`
}

var ErrLinkCodeNotFound = errors.New("link code not found")
var ErrLinkCodeExpired = errors.New("link code expired")
var ErrLinkCodeConsumed = errors.New("link code already consumed")

func HashLinkCode(code string) string {
	sum := sha256.Sum256([]byte(code))
	return hex.EncodeToString(sum[:])
}

type TelegramLinkCodeRepository interface {
	Create(ctx context.Context, telegramUserID string, codeHash string, ttl time.Duration) error
	Consume(ctx context.Context, codeHash string) (telegramUserID string, err error)
}

type MongoTelegramLinkCodeRepository struct {
	store *Store
}

func NewTelegramLinkCodeRepository(store *Store) *MongoTelegramLinkCodeRepository {
	return &MongoTelegramLinkCodeRepository{store: store}
}

func (r *MongoTelegramLinkCodeRepository) Create(ctx context.Context, telegramUserID string, codeHash string, ttl time.Duration) error {
	now := time.Now().UTC()
	_, err := r.store.TelegramLinkCodes().InsertOne(ctx, TelegramLinkCode{
		TelegramUserID: telegramUserID,
		CodeHash:       codeHash,
		CreatedAt:      now,
		ExpiresAt:      now.Add(ttl),
		ConsumedAt:     nil,
	})
	return err
}

func (r *MongoTelegramLinkCodeRepository) Consume(ctx context.Context, codeHash string) (string, error) {
	var code TelegramLinkCode
	err := r.store.TelegramLinkCodes().FindOne(ctx, bson.M{"code_hash": codeHash}).Decode(&code)
	if err != nil {
		if errors.Is(err, mongo.ErrNoDocuments) {
			return "", ErrLinkCodeNotFound
		}
		return "", err
	}
	if code.ConsumedAt != nil {
		return "", ErrLinkCodeConsumed
	}
	if time.Now().UTC().After(code.ExpiresAt) {
		return "", ErrLinkCodeExpired
	}
	now := time.Now().UTC()
	_, err = r.store.TelegramLinkCodes().UpdateOne(
		ctx,
		bson.M{"code_hash": codeHash, "consumed_at": nil},
		bson.M{"$set": bson.M{"consumed_at": now}},
	)
	if err != nil {
		return "", err
	}
	return code.TelegramUserID, nil
}

type InMemoryTelegramLinkCodeRepository struct {
	mu    sync.Mutex
	codes map[string]*TelegramLinkCode
}

func NewInMemoryTelegramLinkCodeRepository() *InMemoryTelegramLinkCodeRepository {
	return &InMemoryTelegramLinkCodeRepository{codes: make(map[string]*TelegramLinkCode)}
}

func (r *InMemoryTelegramLinkCodeRepository) Create(_ context.Context, telegramUserID string, codeHash string, ttl time.Duration) error {
	r.mu.Lock()
	defer r.mu.Unlock()
	now := time.Now().UTC()
	r.codes[codeHash] = &TelegramLinkCode{
		TelegramUserID: telegramUserID,
		CodeHash:       codeHash,
		CreatedAt:      now,
		ExpiresAt:      now.Add(ttl),
		ConsumedAt:     nil,
	}
	return nil
}

func (r *InMemoryTelegramLinkCodeRepository) Consume(_ context.Context, codeHash string) (string, error) {
	r.mu.Lock()
	defer r.mu.Unlock()
	code, ok := r.codes[codeHash]
	if !ok {
		return "", ErrLinkCodeNotFound
	}
	if code.ConsumedAt != nil {
		return "", ErrLinkCodeConsumed
	}
	if time.Now().UTC().After(code.ExpiresAt) {
		return "", ErrLinkCodeExpired
	}
	now := time.Now().UTC()
	code.ConsumedAt = &now
	return code.TelegramUserID, nil
}

var _ TelegramLinkCodeRepository = (*MongoTelegramLinkCodeRepository)(nil)
var _ TelegramLinkCodeRepository = (*InMemoryTelegramLinkCodeRepository)(nil)
