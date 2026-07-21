package mongo

import (
	"context"
	"errors"
	"sync"
	"time"

	"go.mongodb.org/mongo-driver/bson"
	"go.mongodb.org/mongo-driver/mongo"
	"go.mongodb.org/mongo-driver/mongo/options"

	"github.com/country-decision-atlas/notifier/internal/locale"
)

type TelegramIdentity struct {
	TelegramUserID string    `bson:"telegram_user_id"`
	Username       string    `bson:"username"`
	Locale         string    `bson:"locale,omitempty"`
	CreatedAt      time.Time `bson:"created_at"`
	UpdatedAt      time.Time `bson:"updated_at"`
	WebUserID      *string   `bson:"web_user_id"`
}

type TelegramIdentityRepository interface {
	Upsert(ctx context.Context, telegramUserID string, username string) error
	SetWebUserID(ctx context.Context, telegramUserID string, webUserID string) error
	ClearWebUserID(ctx context.Context, telegramUserID string) error
	GetLinkStatus(ctx context.Context, telegramUserID string) (linked bool, webUserID string, err error)
	FindByWebUserID(ctx context.Context, webUserID string) (linked bool, telegramUserID string, err error)
	// SetLocale persists the resolved notification locale for a Telegram
	// user -- called on every bot interaction (internal/telegram/bot),
	// since that's the only place a real `language_code` is available.
	SetLocale(ctx context.Context, telegramUserID string, resolvedLocale string) error
	// GetLocale returns the stored locale, or locale.Default if the
	// identity doesn't exist yet or has never sent a message the bot
	// could capture a language_code from (e.g. created only via the
	// gRPC CreateSubscription path, which has no Telegram update at all).
	GetLocale(ctx context.Context, telegramUserID string) (string, error)
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

func (r *MongoTelegramIdentityRepository) SetWebUserID(ctx context.Context, telegramUserID string, webUserID string) error {
	now := time.Now().UTC()
	filter := bson.M{"telegram_user_id": telegramUserID}
	update := bson.M{
		"$set": bson.M{
			"web_user_id": webUserID,
			"updated_at":  now,
		},
		"$setOnInsert": bson.M{
			"telegram_user_id": telegramUserID,
			"created_at":       now,
		},
	}
	opts := options.Update().SetUpsert(true)
	_, err := r.store.TelegramIdentities().UpdateOne(ctx, filter, update, opts)
	return err
}

func (r *MongoTelegramIdentityRepository) ClearWebUserID(ctx context.Context, telegramUserID string) error {
	filter := bson.M{"telegram_user_id": telegramUserID}
	update := bson.M{
		"$set": bson.M{
			"web_user_id": nil,
			"updated_at":  time.Now().UTC(),
		},
	}
	_, err := r.store.TelegramIdentities().UpdateOne(ctx, filter, update)
	return err
}

func (r *MongoTelegramIdentityRepository) SetLocale(ctx context.Context, telegramUserID string, resolvedLocale string) error {
	now := time.Now().UTC()
	filter := bson.M{"telegram_user_id": telegramUserID}
	update := bson.M{
		"$set": bson.M{
			"locale":     resolvedLocale,
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

func (r *MongoTelegramIdentityRepository) GetLocale(ctx context.Context, telegramUserID string) (string, error) {
	var identity TelegramIdentity
	err := r.store.TelegramIdentities().
		FindOne(ctx, bson.M{"telegram_user_id": telegramUserID}).
		Decode(&identity)
	if err != nil {
		if errors.Is(err, mongo.ErrNoDocuments) {
			return locale.Default, nil
		}
		return "", err
	}
	if identity.Locale == "" {
		return locale.Default, nil
	}
	return identity.Locale, nil
}

func (r *MongoTelegramIdentityRepository) GetLinkStatus(ctx context.Context, telegramUserID string) (bool, string, error) {
	var identity TelegramIdentity
	err := r.store.TelegramIdentities().
		FindOne(ctx, bson.M{"telegram_user_id": telegramUserID}).
		Decode(&identity)
	if err != nil {
		if errors.Is(err, mongo.ErrNoDocuments) {
			return false, "", nil
		}
		return false, "", err
	}
	if identity.WebUserID == nil {
		return false, "", nil
	}
	return true, *identity.WebUserID, nil
}

func (r *MongoTelegramIdentityRepository) FindByWebUserID(ctx context.Context, webUserID string) (bool, string, error) {
	var identity TelegramIdentity
	err := r.store.TelegramIdentities().
		FindOne(ctx, bson.M{"web_user_id": webUserID}).
		Decode(&identity)
	if err != nil {
		if errors.Is(err, mongo.ErrNoDocuments) {
			return false, "", nil
		}
		return false, "", err
	}
	return true, identity.TelegramUserID, nil
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

func (r *InMemoryTelegramIdentityRepository) SetWebUserID(_ context.Context, telegramUserID string, webUserID string) error {
	r.mu.Lock()
	defer r.mu.Unlock()
	now := time.Now().UTC()
	webUserIDCopy := webUserID
	if existing, ok := r.identities[telegramUserID]; ok {
		existing.WebUserID = &webUserIDCopy
		existing.UpdatedAt = now
		return nil
	}
	r.identities[telegramUserID] = &TelegramIdentity{
		TelegramUserID: telegramUserID,
		CreatedAt:      now,
		UpdatedAt:      now,
		WebUserID:      &webUserIDCopy,
	}
	return nil
}

func (r *InMemoryTelegramIdentityRepository) ClearWebUserID(_ context.Context, telegramUserID string) error {
	r.mu.Lock()
	defer r.mu.Unlock()
	if existing, ok := r.identities[telegramUserID]; ok {
		existing.WebUserID = nil
		existing.UpdatedAt = time.Now().UTC()
	}
	return nil
}

func (r *InMemoryTelegramIdentityRepository) SetLocale(_ context.Context, telegramUserID string, resolvedLocale string) error {
	r.mu.Lock()
	defer r.mu.Unlock()
	now := time.Now().UTC()
	if existing, ok := r.identities[telegramUserID]; ok {
		existing.Locale = resolvedLocale
		existing.UpdatedAt = now
		return nil
	}
	r.identities[telegramUserID] = &TelegramIdentity{
		TelegramUserID: telegramUserID,
		Locale:         resolvedLocale,
		CreatedAt:      now,
		UpdatedAt:      now,
		WebUserID:      nil,
	}
	return nil
}

func (r *InMemoryTelegramIdentityRepository) GetLocale(_ context.Context, telegramUserID string) (string, error) {
	r.mu.Lock()
	defer r.mu.Unlock()
	existing, ok := r.identities[telegramUserID]
	if !ok || existing.Locale == "" {
		return locale.Default, nil
	}
	return existing.Locale, nil
}

func (r *InMemoryTelegramIdentityRepository) GetLinkStatus(_ context.Context, telegramUserID string) (bool, string, error) {
	r.mu.Lock()
	defer r.mu.Unlock()
	existing, ok := r.identities[telegramUserID]
	if !ok || existing.WebUserID == nil {
		return false, "", nil
	}
	return true, *existing.WebUserID, nil
}

func (r *InMemoryTelegramIdentityRepository) FindByWebUserID(_ context.Context, webUserID string) (bool, string, error) {
	r.mu.Lock()
	defer r.mu.Unlock()
	for _, identity := range r.identities {
		if identity.WebUserID != nil && *identity.WebUserID == webUserID {
			return true, identity.TelegramUserID, nil
		}
	}
	return false, "", nil
}

var _ TelegramIdentityRepository = (*MongoTelegramIdentityRepository)(nil)
var _ TelegramIdentityRepository = (*InMemoryTelegramIdentityRepository)(nil)
