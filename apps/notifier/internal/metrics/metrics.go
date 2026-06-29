package metrics

import (
	"sync/atomic"
	"time"
)

type Metrics struct {
	startedAt time.Time

	kafkaMessagesConsumed  atomic.Uint64
	kafkaMessagesCommitted atomic.Uint64
	kafkaMessagesFailed    atomic.Uint64

	eventsProcessed    atomic.Uint64
	eventsSkipped      atomic.Uint64
	eventsDeduplicated atomic.Uint64
	eventsDLQ          atomic.Uint64

	subscriptionsMatched atomic.Uint64

	deliveriesAttempted atomic.Uint64
	deliveriesSucceeded atomic.Uint64
	deliveriesFailed    atomic.Uint64
	deliveriesDLQ       atomic.Uint64

	telegramAttempted atomic.Uint64
	telegramSucceeded atomic.Uint64
	telegramFailed    atomic.Uint64

	grpcRequests   atomic.Uint64
	grpcAuthFailed atomic.Uint64

	mongoErrors             atomic.Uint64
	telegramErrors          atomic.Uint64
	unsupportedChannelTotal atomic.Uint64
}

type ChannelCounters struct {
	Attempted uint64 `json:"attempted"`
	Succeeded uint64 `json:"succeeded"`
	Failed    uint64 `json:"failed"`
}

type ChannelsSnapshot struct {
	Telegram ChannelCounters `json:"telegram"`
}

type Snapshot struct {
	StartedAt     string `json:"started_at"`
	UptimeSeconds int64  `json:"uptime_seconds"`

	KafkaMessagesConsumed  uint64 `json:"kafka_messages_consumed"`
	KafkaMessagesCommitted uint64 `json:"kafka_messages_committed"`
	KafkaMessagesFailed    uint64 `json:"kafka_messages_failed"`

	EventsProcessed    uint64 `json:"events_processed"`
	EventsSkipped      uint64 `json:"events_skipped"`
	EventsDeduplicated uint64 `json:"events_deduplicated"`
	EventsDLQ          uint64 `json:"events_dlq"`

	SubscriptionsMatched uint64 `json:"subscriptions_matched"`

	DeliveriesAttempted uint64 `json:"deliveries_attempted"`
	DeliveriesSucceeded uint64 `json:"deliveries_succeeded"`
	DeliveriesFailed    uint64 `json:"deliveries_failed"`
	DeliveriesDLQ       uint64 `json:"deliveries_dlq"`

	Channels ChannelsSnapshot `json:"channels"`

	GRPCRequests   uint64 `json:"grpc_requests"`
	GRPCAuthFailed uint64 `json:"grpc_auth_failed"`

	MongoErrors             uint64 `json:"mongo_errors"`
	TelegramErrors          uint64 `json:"telegram_errors"`
	UnsupportedChannelTotal uint64 `json:"unsupported_channel_total"`
}

func New() *Metrics {
	return &Metrics{startedAt: time.Now().UTC()}
}

func (m *Metrics) Snapshot() Snapshot {
	if m == nil {
		m = New()
	}
	now := time.Now().UTC()
	return Snapshot{
		StartedAt:     m.startedAt.Format(time.RFC3339),
		UptimeSeconds: int64(now.Sub(m.startedAt).Seconds()),

		KafkaMessagesConsumed:  m.kafkaMessagesConsumed.Load(),
		KafkaMessagesCommitted: m.kafkaMessagesCommitted.Load(),
		KafkaMessagesFailed:    m.kafkaMessagesFailed.Load(),

		EventsProcessed:    m.eventsProcessed.Load(),
		EventsSkipped:      m.eventsSkipped.Load(),
		EventsDeduplicated: m.eventsDeduplicated.Load(),
		EventsDLQ:          m.eventsDLQ.Load(),

		SubscriptionsMatched: m.subscriptionsMatched.Load(),

		DeliveriesAttempted: m.deliveriesAttempted.Load(),
		DeliveriesSucceeded: m.deliveriesSucceeded.Load(),
		DeliveriesFailed:    m.deliveriesFailed.Load(),
		DeliveriesDLQ:       m.deliveriesDLQ.Load(),

		Channels: ChannelsSnapshot{
			Telegram: ChannelCounters{
				Attempted: m.telegramAttempted.Load(),
				Succeeded: m.telegramSucceeded.Load(),
				Failed:    m.telegramFailed.Load(),
			},
		},

		GRPCRequests:   m.grpcRequests.Load(),
		GRPCAuthFailed: m.grpcAuthFailed.Load(),

		MongoErrors:             m.mongoErrors.Load(),
		TelegramErrors:          m.telegramErrors.Load(),
		UnsupportedChannelTotal: m.unsupportedChannelTotal.Load(),
	}
}

func (m *Metrics) IncKafkaMessagesConsumed()  { m.kafkaMessagesConsumed.Add(1) }
func (m *Metrics) IncKafkaMessagesCommitted() { m.kafkaMessagesCommitted.Add(1) }
func (m *Metrics) IncKafkaMessagesFailed()    { m.kafkaMessagesFailed.Add(1) }
func (m *Metrics) IncEventsProcessed()        { m.eventsProcessed.Add(1) }
func (m *Metrics) IncEventsSkipped()          { m.eventsSkipped.Add(1) }
func (m *Metrics) IncEventsDeduplicated()     { m.eventsDeduplicated.Add(1) }
func (m *Metrics) IncEventsDLQ()              { m.eventsDLQ.Add(1) }
func (m *Metrics) AddSubscriptionsMatched(n int) {
	if n > 0 {
		m.subscriptionsMatched.Add(uint64(n))
	}
}
func (m *Metrics) IncDeliveriesAttempted()     { m.deliveriesAttempted.Add(1) }
func (m *Metrics) IncDeliveriesSucceeded()     { m.deliveriesSucceeded.Add(1) }
func (m *Metrics) IncDeliveriesFailed()        { m.deliveriesFailed.Add(1) }
func (m *Metrics) IncDeliveriesDLQ()           { m.deliveriesDLQ.Add(1) }
func (m *Metrics) IncTelegramAttempted()       { m.telegramAttempted.Add(1) }
func (m *Metrics) IncTelegramSucceeded()       { m.telegramSucceeded.Add(1) }
func (m *Metrics) IncTelegramFailed()          { m.telegramFailed.Add(1) }
func (m *Metrics) IncGRPCRequests()            { m.grpcRequests.Add(1) }
func (m *Metrics) IncGRPCAuthFailed()          { m.grpcAuthFailed.Add(1) }
func (m *Metrics) IncMongoErrors()             { m.mongoErrors.Add(1) }
func (m *Metrics) IncTelegramErrors()          { m.telegramErrors.Add(1) }
func (m *Metrics) IncUnsupportedChannelTotal() { m.unsupportedChannelTotal.Add(1) }
