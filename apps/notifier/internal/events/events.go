package events

import (
	"encoding/json"
	"errors"
	"time"
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

func Parse(data []byte) (*DomainEvent, error) {
	var e DomainEvent
	if err := json.Unmarshal(data, &e); err != nil {
		return nil, err
	}
	if err := e.validate(); err != nil {
		return nil, err
	}
	return &e, nil
}

func (e *DomainEvent) validate() error {
	if e.EventKey == "" {
		return errors.New("event_key is required")
	}
	if e.EventType == "" {
		return errors.New("event_type is required")
	}
	if e.AggregateType == "" {
		return errors.New("aggregate_type is required")
	}
	if e.AggregateID == "" {
		return errors.New("aggregate_id is required")
	}
	return nil
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
