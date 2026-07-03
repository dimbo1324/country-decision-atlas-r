package mongo

import (
	"context"
	"errors"
	"testing"
	"time"
)

func TestHashLinkCodeIsDeterministic(t *testing.T) {
	first := HashLinkCode("123456")
	second := HashLinkCode("123456")
	if first != second {
		t.Errorf("want deterministic hash, got %s and %s", first, second)
	}
	if len(first) != 64 {
		t.Errorf("want 64-char hex sha256 digest, got length %d", len(first))
	}
}

func TestHashLinkCodeDiffersForDifferentCodes(t *testing.T) {
	if HashLinkCode("123456") == HashLinkCode("654321") {
		t.Error("want different hashes for different codes")
	}
}

func TestInMemoryLinkCodeRepositoryConsumeReturnsTelegramUserID(t *testing.T) {
	repo := NewInMemoryTelegramLinkCodeRepository()
	ctx := context.Background()
	hash := HashLinkCode("111111")

	if err := repo.Create(ctx, "telegram-user-1", hash, 10*time.Minute); err != nil {
		t.Fatalf("create: %v", err)
	}

	telegramUserID, err := repo.Consume(ctx, hash)
	if err != nil {
		t.Fatalf("unexpected error: %v", err)
	}
	if telegramUserID != "telegram-user-1" {
		t.Errorf("want telegram-user-1 got %s", telegramUserID)
	}
}

func TestInMemoryLinkCodeRepositoryConsumeUnknownCodeReturnsNotFound(t *testing.T) {
	repo := NewInMemoryTelegramLinkCodeRepository()
	_, err := repo.Consume(context.Background(), HashLinkCode("unknown"))
	if !errors.Is(err, ErrLinkCodeNotFound) {
		t.Errorf("want ErrLinkCodeNotFound got %v", err)
	}
}

func TestInMemoryLinkCodeRepositoryConsumeTwiceReturnsConsumedError(t *testing.T) {
	repo := NewInMemoryTelegramLinkCodeRepository()
	ctx := context.Background()
	hash := HashLinkCode("222222")
	if err := repo.Create(ctx, "telegram-user-2", hash, 10*time.Minute); err != nil {
		t.Fatalf("create: %v", err)
	}

	if _, err := repo.Consume(ctx, hash); err != nil {
		t.Fatalf("first consume: %v", err)
	}
	if _, err := repo.Consume(ctx, hash); !errors.Is(err, ErrLinkCodeConsumed) {
		t.Errorf("want ErrLinkCodeConsumed got %v", err)
	}
}

func TestInMemoryLinkCodeRepositoryConsumeExpiredReturnsExpiredError(t *testing.T) {
	repo := NewInMemoryTelegramLinkCodeRepository()
	ctx := context.Background()
	hash := HashLinkCode("333333")
	if err := repo.Create(ctx, "telegram-user-3", hash, -1*time.Minute); err != nil {
		t.Fatalf("create: %v", err)
	}

	if _, err := repo.Consume(ctx, hash); !errors.Is(err, ErrLinkCodeExpired) {
		t.Errorf("want ErrLinkCodeExpired got %v", err)
	}
}

func TestInMemoryTelegramIdentityRepositorySetAndGetLinkStatus(t *testing.T) {
	repo := NewInMemoryTelegramIdentityRepository()
	ctx := context.Background()

	linked, webUserID, err := repo.GetLinkStatus(ctx, "telegram-user-4")
	if err != nil {
		t.Fatalf("unexpected error: %v", err)
	}
	if linked {
		t.Error("want unlinked before any SetWebUserID call")
	}

	if err := repo.SetWebUserID(ctx, "telegram-user-4", "web-user-4"); err != nil {
		t.Fatalf("set web user id: %v", err)
	}

	linked, webUserID, err = repo.GetLinkStatus(ctx, "telegram-user-4")
	if err != nil {
		t.Fatalf("unexpected error: %v", err)
	}
	if !linked {
		t.Fatal("want linked after SetWebUserID")
	}
	if webUserID != "web-user-4" {
		t.Errorf("want web-user-4 got %s", webUserID)
	}
}

func TestInMemoryTelegramIdentityRepositoryClearWebUserID(t *testing.T) {
	repo := NewInMemoryTelegramIdentityRepository()
	ctx := context.Background()

	if err := repo.SetWebUserID(ctx, "telegram-user-5", "web-user-5"); err != nil {
		t.Fatalf("set web user id: %v", err)
	}
	if err := repo.ClearWebUserID(ctx, "telegram-user-5"); err != nil {
		t.Fatalf("clear web user id: %v", err)
	}

	linked, _, err := repo.GetLinkStatus(ctx, "telegram-user-5")
	if err != nil {
		t.Fatalf("unexpected error: %v", err)
	}
	if linked {
		t.Error("want unlinked after ClearWebUserID")
	}
}

func TestInMemoryTelegramIdentityRepositoryClearWebUserIDOnUnknownIdentityIsNoop(t *testing.T) {
	repo := NewInMemoryTelegramIdentityRepository()
	if err := repo.ClearWebUserID(context.Background(), "never-seen"); err != nil {
		t.Fatalf("unexpected error clearing unknown identity: %v", err)
	}
}
