// Package locale resolves a raw Telegram `language_code` (BCP-47, e.g.
// "en-US", "es", "") to one of the three locales this app's notification
// text is translated into, matching apps/web's SUPPORTED_LOCALES.
package locale

import "strings"

const (
	EN = "en"
	RU = "ru"
	ES = "es"
	// Default matches the notifier's pre-i18n hardcoded behavior, so a
	// visitor with no or an unrecognized language_code sees the same text
	// as before this package existed.
	Default = RU
)

var supported = map[string]bool{EN: true, RU: true, ES: true}

// Resolve maps a raw `language_code` to one of EN/RU/ES, defaulting to
// Default when it's empty or not one of the three.
func Resolve(rawCode string) string {
	code := strings.ToLower(strings.TrimSpace(rawCode))
	if code == "" {
		return Default
	}
	if idx := strings.IndexByte(code, '-'); idx != -1 {
		code = code[:idx]
	}
	if supported[code] {
		return code
	}
	return Default
}
