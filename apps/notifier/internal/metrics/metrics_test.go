package metrics

import "testing"

func TestMetricsCountersSnapshot(t *testing.T) {
	m := New()
	m.IncKafkaMessagesConsumed()
	m.IncDeliveriesAttempted()
	m.IncTelegramSucceeded()
	m.IncGRPCAuthFailed()

	snapshot := m.Snapshot()
	if snapshot.KafkaMessagesConsumed != 1 {
		t.Errorf("want kafka consumed 1 got %d", snapshot.KafkaMessagesConsumed)
	}
	if snapshot.DeliveriesAttempted != 1 {
		t.Errorf("want deliveries attempted 1 got %d", snapshot.DeliveriesAttempted)
	}
	if snapshot.Channels.Telegram.Succeeded != 1 {
		t.Errorf("want telegram succeeded 1 got %d", snapshot.Channels.Telegram.Succeeded)
	}
	if snapshot.GRPCAuthFailed != 1 {
		t.Errorf("want grpc auth failed 1 got %d", snapshot.GRPCAuthFailed)
	}
}
