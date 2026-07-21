package telegram

import (
	"strings"
	"testing"

	"github.com/country-decision-atlas/notifier/internal/locale"
)

func TestDisclaimerFor(t *testing.T) {
	cases := map[string]string{
		locale.RU: "Это не юридическая консультация.",
		locale.EN: "This is not legal advice.",
		locale.ES: "Esto no es asesoramiento legal.",
		"fr":      "Это не юридическая консультация.", // unrecognized -> default
	}
	for loc, want := range cases {
		if got := DisclaimerFor(loc); got != want {
			t.Errorf("DisclaimerFor(%q) = %q, want %q", loc, got, want)
		}
	}
}

func TestFormatMessageLegalSignalPerLocale(t *testing.T) {
	cases := map[string]struct {
		mustContain []string
	}{
		locale.RU: {[]string{"Новое правовое событие", "argentina", "новый закон", "Это не юридическая консультация."}},
		locale.EN: {[]string{"New legal signal", "argentina", "новый закон", "This is not legal advice."}},
		locale.ES: {[]string{"Nueva señal legal", "argentina", "новый закон", "Esto no es asesoramiento legal."}},
	}
	for loc, tc := range cases {
		text := FormatMessage("argentina", "legal_change", "новый закон", loc)
		for _, want := range tc.mustContain {
			if !strings.Contains(text, want) {
				t.Errorf("FormatMessage(loc=%s) = %q, missing %q", loc, text, want)
			}
		}
	}
}

func TestFormatMessageTripReminderPerLocale(t *testing.T) {
	cases := map[string]string{
		locale.RU: "Напоминание по плану переезда",
		locale.EN: "Relocation plan reminder",
		locale.ES: "Recordatorio del plan de mudanza",
	}
	for loc, want := range cases {
		text := FormatMessage("argentina", "trip_reminder_due", "check visa docs", loc)
		if !strings.Contains(text, want) {
			t.Errorf("FormatMessage(trip_reminder_due, loc=%s) = %q, missing %q", loc, text, want)
		}
	}
}

func TestFormatMessageUnrecognizedLocaleFallsBackToDefault(t *testing.T) {
	text := FormatMessage("argentina", "legal_change", "title", "fr")
	if !strings.Contains(text, "Новое правовое событие") {
		t.Errorf("expected default (ru) template for unrecognized locale, got: %s", text)
	}
}
