package commands

import (
	"strings"
)

type CommandType string

const (
	CmdSubscribe   CommandType = "subscribe"
	CmdUnsubscribe CommandType = "unsubscribe"
	CmdList        CommandType = "list"
	CmdHelp        CommandType = "help"
	CmdUnknown     CommandType = "unknown"
)

type ParsedCommand struct {
	Type        CommandType
	CountrySlug string
	Error       string
}

func Parse(text string) ParsedCommand {
	text = strings.TrimSpace(text)
	if text == "" {
		return ParsedCommand{Type: CmdHelp}
	}

	parts := strings.Fields(text)
	raw := strings.ToLower(parts[0])

	if at := strings.Index(raw, "@"); at != -1 {
		raw = raw[:at]
	}

	switch raw {
	case "/subscribe":
		return parseWithCountry(CmdSubscribe, parts)
	case "/unsubscribe":
		return parseWithCountry(CmdUnsubscribe, parts)
	case "/list":
		return ParsedCommand{Type: CmdList}
	case "/help":
		return ParsedCommand{Type: CmdHelp}
	default:
		return ParsedCommand{Type: CmdUnknown}
	}
}

func parseWithCountry(cmd CommandType, parts []string) ParsedCommand {
	if len(parts) < 2 {
		return ParsedCommand{Type: cmd, Error: "country is required"}
	}
	slug := strings.ToLower(strings.TrimSpace(parts[1]))
	if slug == "" {
		return ParsedCommand{Type: cmd, Error: "country is required"}
	}
	return ParsedCommand{Type: cmd, CountrySlug: slug}
}
