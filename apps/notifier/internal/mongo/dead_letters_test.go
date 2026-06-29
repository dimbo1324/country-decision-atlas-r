package mongo

import (
	"context"
	"testing"

	"github.com/country-decision-atlas/notifier/internal/dlq"
)

func TestDeadLetterUpsertIsIdempotent(t *testing.T) {
	repo := NewInMemoryDeadLetterRepository()
	entry := &DeadLetter{
		EventKey:    "event-1",
		Stage:       dlq.StageDelivery,
		ReasonCode:  dlq.ReasonUnsupportedChannel,
		Error:       "unsupported notification channel",
		ChannelType: "email",
		RecipientID: "user1",
		Status:      dlq.StatusOpen,
	}

	if err := repo.Upsert(context.Background(), entry); err != nil {
		t.Fatalf("first upsert: %v", err)
	}
	if err := repo.Upsert(context.Background(), entry); err != nil {
		t.Fatalf("second upsert: %v", err)
	}

	if len(repo.Entries) != 1 {
		t.Fatalf("want one dead letter got %d", len(repo.Entries))
	}
	for _, dl := range repo.Entries {
		if dl.Attempts != 2 {
			t.Errorf("want attempts=2 got %d", dl.Attempts)
		}
	}
}

func TestStableMalformedEventKey(t *testing.T) {
	first := StableMalformedEventKey([]byte("{bad"))
	second := StableMalformedEventKey([]byte("{bad"))
	if first != second {
		t.Fatal("malformed event key must be stable")
	}
	if first == StableMalformedEventKey([]byte("{other")) {
		t.Fatal("different raw payloads should produce different malformed keys")
	}
}
