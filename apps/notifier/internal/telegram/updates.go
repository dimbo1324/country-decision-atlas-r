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
}
