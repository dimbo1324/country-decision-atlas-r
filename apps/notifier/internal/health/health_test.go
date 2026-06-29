package health

import (
	"encoding/json"
	"net/http"
	"net/http/httptest"
	"testing"

	"github.com/country-decision-atlas/notifier/internal/metrics"
)

func TestHealthEndpointStatus200(t *testing.T) {
	req := httptest.NewRequest(http.MethodGet, "/health", nil)
	w := httptest.NewRecorder()
	Handler(metrics.New()).ServeHTTP(w, req)
	if w.Code != http.StatusOK {
		t.Errorf("want 200 got %d", w.Code)
	}
}

func TestHealthResponseIncludesStatusOk(t *testing.T) {
	req := httptest.NewRequest(http.MethodGet, "/health", nil)
	w := httptest.NewRecorder()
	Handler(metrics.New()).ServeHTTP(w, req)

	var body map[string]string
	if err := json.NewDecoder(w.Body).Decode(&body); err != nil {
		t.Fatalf("decode error: %v", err)
	}
	if body["status"] != "ok" {
		t.Errorf("want status=ok got %s", body["status"])
	}
}

func TestHealthResponseIncludesServiceName(t *testing.T) {
	req := httptest.NewRequest(http.MethodGet, "/health", nil)
	w := httptest.NewRecorder()
	Handler(metrics.New()).ServeHTTP(w, req)

	var body map[string]string
	if err := json.NewDecoder(w.Body).Decode(&body); err != nil {
		t.Fatalf("decode error: %v", err)
	}
	if body["service"] != "signal-notifier" {
		t.Errorf("want service=signal-notifier got %s", body["service"])
	}
}

func TestMetricsEndpointStatus200(t *testing.T) {
	req := httptest.NewRequest(http.MethodGet, "/metrics", nil)
	w := httptest.NewRecorder()
	m := metrics.New()
	m.IncKafkaMessagesConsumed()

	Handler(m).ServeHTTP(w, req)

	if w.Code != http.StatusOK {
		t.Errorf("want 200 got %d", w.Code)
	}
	var body map[string]interface{}
	if err := json.NewDecoder(w.Body).Decode(&body); err != nil {
		t.Fatalf("decode error: %v", err)
	}
	if body["kafka_messages_consumed"].(float64) != 1 {
		t.Errorf("want kafka_messages_consumed=1 got %v", body["kafka_messages_consumed"])
	}
}
