package locale

import "testing"

func TestResolve(t *testing.T) {
	cases := map[string]string{
		"":        Default,
		"ru":      RU,
		"en":      EN,
		"es":      ES,
		"en-US":   EN,
		"es-MX":   ES,
		"RU":      RU,
		" en ":    EN,
		"fr":      Default,
		"fr-FR":   Default,
		"zh-Hans": Default,
	}
	for input, want := range cases {
		if got := Resolve(input); got != want {
			t.Errorf("Resolve(%q) = %q, want %q", input, got, want)
		}
	}
}
