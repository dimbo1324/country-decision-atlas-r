package telegram

type TelegramUpdate struct {
	UpdateID int64            `json:"update_id"`
	Message  *TelegramMessage `json:"message"`
}

type TelegramMessage struct {
	Text string        `json:"text"`
	Chat TelegramChat  `json:"chat"`
	From *TelegramUser `json:"from"`
}

type TelegramChat struct {
	ID int64 `json:"id"`
}

type TelegramUser struct {
	ID       int64  `json:"id"`
	Username string `json:"username"`
	// LanguageCode is the client-reported IETF language tag (e.g. "en",
	// "es-MX") Telegram sends on every message's `from` -- the source for
	// per-recipient notification locale (internal/locale.Resolve).
	LanguageCode string `json:"language_code"`
}
