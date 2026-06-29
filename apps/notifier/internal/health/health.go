package health

import (
	"encoding/json"
	"net/http"

	"github.com/country-decision-atlas/notifier/internal/metrics"
)

type response struct {
	Status  string `json:"status"`
	Service string `json:"service"`
}

func Handler(metricsCollector *metrics.Metrics) http.Handler {
	mux := http.NewServeMux()
	mux.HandleFunc("/health", func(w http.ResponseWriter, _ *http.Request) {
		w.Header().Set("Content-Type", "application/json")
		w.WriteHeader(http.StatusOK)
		_ = json.NewEncoder(w).Encode(response{Status: "ok", Service: "signal-notifier"})
	})
	mux.HandleFunc("/metrics", func(w http.ResponseWriter, _ *http.Request) {
		w.Header().Set("Content-Type", "application/json")
		w.WriteHeader(http.StatusOK)
		_ = json.NewEncoder(w).Encode(metricsCollector.Snapshot())
	})
	return mux
}
