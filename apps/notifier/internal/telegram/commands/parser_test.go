package commands

import (
	"testing"
)

func TestParseSubscribe(t *testing.T) {
	cmd := Parse("/subscribe argentina")
	if cmd.Type != CmdSubscribe {
		t.Errorf("want subscribe got %s", cmd.Type)
	}
	if cmd.CountrySlug != "argentina" {
		t.Errorf("want argentina got %s", cmd.CountrySlug)
	}
	if cmd.Error != "" {
		t.Errorf("want no error got %s", cmd.Error)
	}
}

func TestParseUnsubscribe(t *testing.T) {
	cmd := Parse("/unsubscribe argentina")
	if cmd.Type != CmdUnsubscribe {
		t.Errorf("want unsubscribe got %s", cmd.Type)
	}
	if cmd.CountrySlug != "argentina" {
		t.Errorf("want argentina got %s", cmd.CountrySlug)
	}
}

func TestParseList(t *testing.T) {
	cmd := Parse("/list")
	if cmd.Type != CmdList {
		t.Errorf("want list got %s", cmd.Type)
	}
}

func TestParseHelp(t *testing.T) {
	cmd := Parse("/help")
	if cmd.Type != CmdHelp {
		t.Errorf("want help got %s", cmd.Type)
	}
}

func TestParseUnknownCommand(t *testing.T) {
	cmd := Parse("/foobar")
	if cmd.Type != CmdUnknown {
		t.Errorf("want unknown got %s", cmd.Type)
	}
}

func TestParseMissingCountry(t *testing.T) {
	cmd := Parse("/subscribe")
	if cmd.Error == "" {
		t.Error("want error for missing country")
	}
}

func TestParseLowercasesSlug(t *testing.T) {
	cmd := Parse("/subscribe ARGENTINA")
	if cmd.CountrySlug != "argentina" {
		t.Errorf("want lowercase got %s", cmd.CountrySlug)
	}
}

func TestParseTrimSpace(t *testing.T) {
	cmd := Parse("  /subscribe  russia  ")
	if cmd.Type != CmdSubscribe {
		t.Errorf("want subscribe got %s", cmd.Type)
	}
	if cmd.CountrySlug != "russia" {
		t.Errorf("want russia got %s", cmd.CountrySlug)
	}
}

func TestParseBotMention(t *testing.T) {
	cmd := Parse("/subscribe@mybot argentina")
	if cmd.Type != CmdSubscribe {
		t.Errorf("want subscribe got %s", cmd.Type)
	}
	if cmd.CountrySlug != "argentina" {
		t.Errorf("want argentina got %s", cmd.CountrySlug)
	}
}

func TestParseEmptyText(t *testing.T) {
	cmd := Parse("")
	if cmd.Type != CmdHelp {
		t.Errorf("empty text should return help, got %s", cmd.Type)
	}
}
