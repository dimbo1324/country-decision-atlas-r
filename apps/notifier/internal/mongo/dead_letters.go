package mongo

import (
	"context"
	"crypto/sha256"
	"encoding/hex"
	"sync"
	"time"

	"github.com/country-decision-atlas/notifier/internal/dlq"
	"go.mongodb.org/mongo-driver/bson"
	"go.mongodb.org/mongo-driver/mongo/options"
)

type DeadLetter struct {
	ID             string                 `bson:"_id,omitempty"`
	EventKey       string                 `bson:"event_key"`
	Stage          string                 `bson:"stage"`
	ReasonCode     string                 `bson:"reason_code"`
	Error          string                 `bson:"error"`
	EventType      string                 `bson:"event_type,omitempty"`
	CountrySlug    string                 `bson:"country_slug,omitempty"`
	ChannelType    string                 `bson:"channel_type,omitempty"`
	RecipientID    string                 `bson:"recipient_id,omitempty"`
	TelegramUserID string                 `bson:"telegram_user_id,omitempty"`
	Payload        map[string]interface{} `bson:"payload,omitempty"`
	Retryable      bool                   `bson:"retryable"`
	Status         string                 `bson:"status"`
	CreatedAt      time.Time              `bson:"created_at"`
	LastSeenAt     time.Time              `bson:"last_seen_at"`
	Attempts       int                    `bson:"attempts"`
}

type DeadLetterRepository interface {
	Upsert(ctx context.Context, entry *DeadLetter) error
}

type MongoDeadLetterRepository struct {
	store *Store
}

func NewDeadLetterRepository(store *Store) *MongoDeadLetterRepository {
	return &MongoDeadLetterRepository{store: store}
}

func (r *MongoDeadLetterRepository) Upsert(ctx context.Context, entry *DeadLetter) error {
	normalizeDeadLetter(entry)
	filter := bson.M{"_id": entry.ID}
	update := bson.M{
		"$set": bson.M{
			"event_key":        entry.EventKey,
			"stage":            entry.Stage,
			"reason_code":      entry.ReasonCode,
			"error":            entry.Error,
			"event_type":       entry.EventType,
			"country_slug":     entry.CountrySlug,
			"channel_type":     entry.ChannelType,
			"recipient_id":     entry.RecipientID,
			"telegram_user_id": entry.TelegramUserID,
			"payload":          entry.Payload,
			"retryable":        entry.Retryable,
			"status":           entry.Status,
			"last_seen_at":     entry.LastSeenAt,
		},
		"$setOnInsert": bson.M{
			"_id":        entry.ID,
			"created_at": entry.CreatedAt,
		},
		"$inc": bson.M{"attempts": 1},
	}
	_, err := r.store.DeadLetters().UpdateOne(ctx, filter, update, options.Update().SetUpsert(true))
	return err
}

type InMemoryDeadLetterRepository struct {
	mu      sync.Mutex
	Entries map[string]*DeadLetter
}

func NewInMemoryDeadLetterRepository() *InMemoryDeadLetterRepository {
	return &InMemoryDeadLetterRepository{Entries: map[string]*DeadLetter{}}
}

func (r *InMemoryDeadLetterRepository) Upsert(_ context.Context, entry *DeadLetter) error {
	r.mu.Lock()
	defer r.mu.Unlock()
	normalizeDeadLetter(entry)
	existing, ok := r.Entries[entry.ID]
	if ok {
		existing.LastSeenAt = entry.LastSeenAt
		existing.ReasonCode = entry.ReasonCode
		existing.Error = entry.Error
		existing.Status = entry.Status
		existing.Attempts++
		return nil
	}
	copyEntry := *entry
	copyEntry.Attempts = 1
	r.Entries[entry.ID] = &copyEntry
	return nil
}

func StableMalformedEventKey(raw []byte) string {
	sum := sha256.Sum256(raw)
	return "malformed:" + hex.EncodeToString(sum[:])
}

func normalizeDeadLetter(entry *DeadLetter) {
	now := time.Now().UTC()
	if entry.EventKey == "" {
		entry.EventKey = StableMalformedEventKey([]byte(entry.Error))
	}
	if entry.Stage == "" {
		entry.Stage = dlq.StageEventProcessing
	}
	if entry.Status == "" {
		entry.Status = dlq.StatusOpen
	}
	if entry.CreatedAt.IsZero() {
		entry.CreatedAt = now
	}
	entry.LastSeenAt = now
	if entry.ID == "" {
		entry.ID = deadLetterID(entry)
	}
}

func deadLetterID(entry *DeadLetter) string {
	key := entry.EventKey
	if key == "" {
		key = StableMalformedEventKey([]byte(entry.Error))
	}
	recipient := entry.RecipientID
	if recipient == "" {
		recipient = entry.TelegramUserID
	}
	sum := sha256.Sum256([]byte(key + "|" + entry.Stage + "|" + entry.ChannelType + "|" + recipient))
	return hex.EncodeToString(sum[:])
}

var _ DeadLetterRepository = (*MongoDeadLetterRepository)(nil)
var _ DeadLetterRepository = (*InMemoryDeadLetterRepository)(nil)
