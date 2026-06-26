package events

import (
	"encoding/json"
	"testing"
	"time"
)

func makeEvent(overrides map[string]interface{}) []byte {
	base := map[string]interface{}{
		"event_key":      "key-1",
		"event_type":     "legal_signal.published",
		"aggregate_type": "legal_signal",
		"aggregate_id":   "uuid-1",
		"country_slug":   "argentina",
		"payload":        map[string]interface{}{},
		"created_at":     time.Now().UTC(),
	}
	for k, v := range overrides {
		base[k] = v
	}
	b, _ := json.Marshal(base)
	return b
}

func TestParseValidEvent(t *testing.T) {
	data := makeEvent(nil)
	e, err := Parse(data)
	if err != nil {
		t.Fatalf("unexpected error: %v", err)
	}
	if e.EventKey != "key-1" {
		t.Errorf("want key-1 got %s", e.EventKey)
	}
}

func TestMissingEventKeyReturnsError(t *testing.T) {
	data := makeEvent(map[string]interface{}{"event_key": ""})
	_, err := Parse(data)
	if err == nil {
		t.Error("expected error for empty event_key")
	}
}

func TestMissingEventTypeReturnsError(t *testing.T) {
	data := makeEvent(map[string]interface{}{"event_type": ""})
	_, err := Parse(data)
	if err == nil {
		t.Error("expected error for empty event_type")
	}
}

func TestMissingAggregateTypeReturnsError(t *testing.T) {
	data := makeEvent(map[string]interface{}{"aggregate_type": ""})
	_, err := Parse(data)
	if err == nil {
		t.Error("expected error for empty aggregate_type")
	}
}

func TestMissingAggregateIDReturnsError(t *testing.T) {
	data := makeEvent(map[string]interface{}{"aggregate_id": ""})
	_, err := Parse(data)
	if err == nil {
		t.Error("expected error for empty aggregate_id")
	}
}

func TestTitleFromPayload(t *testing.T) {
	data := makeEvent(map[string]interface{}{"payload": map[string]interface{}{"title": "Law XYZ"}})
	e, _ := Parse(data)
	if e.Title() != "Law XYZ" {
		t.Errorf("want 'Law XYZ' got %s", e.Title())
	}
}

func TestTitleFallsBackToEventType(t *testing.T) {
	data := makeEvent(nil)
	e, _ := Parse(data)
	if e.Title() != "legal_signal.published" {
		t.Errorf("want event_type fallback got %s", e.Title())
	}
}
