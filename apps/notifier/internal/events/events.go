package events

import (
	"encoding/json"
	"errors"
	"fmt"
	"time"

	"github.com/country-decision-atlas/notifier/internal/dlq"
)

type DomainEvent struct {
	EventKey      string                 `json:"event_key"`
	EventType     string                 `json:"event_type"`
	AggregateType string                 `json:"aggregate_type"`
	AggregateID   string                 `json:"aggregate_id"`
	CountrySlug   string                 `json:"country_slug"`
	Payload       map[string]interface{} `json:"payload"`
	CreatedAt     time.Time              `json:"created_at"`
}

var (
	ErrInvalidJSON          = errors.New("invalid json")
	ErrMissingEventKey      = errors.New("event_key is required")
	ErrMissingEventType     = errors.New("event_type is required")
	ErrMissingAggregateType = errors.New("aggregate_type is required")
	ErrMissingAggregateID   = errors.New("aggregate_id is required")
	ErrMissingCountrySlug   = errors.New("country_slug is required")
	ErrUnsupportedEventType = errors.New("unsupported event_type")
	ErrInvalidCreatedAt     = errors.New("created_at is required")
)

var supportedEventTypes = map[string]struct{}{
	"legal_signal.published":       {},
	"legal_signal_event.published": {},
	"route.published":              {},
}

func Parse(data []byte) (*DomainEvent, error) {
	var e DomainEvent
	if err := json.Unmarshal(data, &e); err != nil {
		return nil, fmt.Errorf("%w: %v", ErrInvalidJSON, err)
	}
	if err := e.validate(); err != nil {
		return nil, err
	}
	return &e, nil
}

func (e *DomainEvent) validate() error {
	if e.EventKey == "" {
		return ErrMissingEventKey
	}
	if e.EventType == "" {
		return ErrMissingEventType
	}
	if _, ok := supportedEventTypes[e.EventType]; !ok {
		return fmt.Errorf("%w: %s", ErrUnsupportedEventType, e.EventType)
	}
	if e.AggregateType == "" {
		return ErrMissingAggregateType
	}
	if e.AggregateID == "" {
		return ErrMissingAggregateID
	}
	if e.CountrySlug == "" {
		return ErrMissingCountrySlug
	}
	if e.CreatedAt.IsZero() {
		return ErrInvalidCreatedAt
	}
	return nil
}

func ReasonForError(err error) string {
	switch {
	case errors.Is(err, ErrInvalidJSON):
		return dlq.ReasonInvalidJSON
	case errors.Is(err, ErrMissingEventKey):
		return dlq.ReasonMissingEventKey
	case errors.Is(err, ErrMissingCountrySlug):
		return dlq.ReasonMissingCountrySlug
	case errors.Is(err, ErrUnsupportedEventType):
		return dlq.ReasonUnsupportedEventType
	default:
		return dlq.ReasonUnknownProcessingError
	}
}

func (e *DomainEvent) Title() string {
	if e.Payload == nil {
		return e.EventType
	}
	if t, ok := e.Payload["title"]; ok {
		if s, ok := t.(string); ok && s != "" {
			return s
		}
	}
	return e.EventType
}
