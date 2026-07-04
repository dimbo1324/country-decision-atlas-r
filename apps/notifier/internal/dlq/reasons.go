package dlq

const (
	StageEventProcessing = "event_processing"
	StageDelivery        = "delivery"

	StatusOpen = "open"

	ReasonInvalidJSON              = "invalid_json"
	ReasonMissingEventKey          = "missing_event_key"
	ReasonMissingCountrySlug       = "missing_country_slug"
	ReasonUnsupportedEventType     = "unsupported_event_type"
	ReasonUnsupportedChannel       = "unsupported_channel"
	ReasonTelegramPermanentFailure = "telegram_permanent_failure"
	ReasonDeliveryRetriesExhausted = "delivery_retries_exhausted"
	ReasonNotifyAfterSkipped       = "notify_after_skipped"
	ReasonUnknownProcessingError   = "unknown_processing_error"
	ReasonMissingRecipient         = "missing_recipient"
	ReasonTelegramNotLinked        = "telegram_not_linked"
)
