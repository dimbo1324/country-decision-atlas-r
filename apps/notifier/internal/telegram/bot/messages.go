package bot

import (
	"fmt"

	"github.com/country-decision-atlas/notifier/internal/locale"
	"github.com/country-decision-atlas/notifier/internal/telegram"
)

// messages is the full set of bot-facing strings for one locale. The `ru`
// entry is byte-for-byte the text this package hardcoded before locale
// support existed, so a visitor with no/unrecognized language_code (the
// pre-existing default) sees exactly the same replies as before. The
// disclaimer itself lives in telegram.DisclaimerFor -- shared with the
// event-notification templates in telegram.FormatMessage, so there's a
// single source of truth per locale, not two catalogs that could drift.
type messages struct {
	help                string
	subscribeUsage      string
	unsubscribeUsage    string
	unknownCountry      func(countrySlug string) string
	subscribeFailed     string
	subscribed          func(countrySlug string) string
	unsubscribeFailed   string
	notSubscribed       func(countrySlug string) string
	unsubscribed        func(countrySlug string) string
	listFailed          string
	noSubscriptions     string
	subscriptionsList   func(slugs string) string
	webLinkFailed       string
	webLinkInstructions func(code string, minutes int) string
}

func withDisclaimer(loc string, text string) string {
	return fmt.Sprintf("%s\n\n%s", text, telegram.DisclaimerFor(loc))
}

var catalog = map[string]messages{
	locale.RU: {
		help: "/subscribe <страна> — подписаться на уведомления\n" +
			"/unsubscribe <страна> — отписаться\n" +
			"/list — мои подписки\n" +
			"/web_link — код для привязки web-аккаунта\n" +
			"/help — помощь\n\n" +
			telegram.DisclaimerFor(locale.RU),
		subscribeUsage:   "Укажите страну: /subscribe argentina",
		unsubscribeUsage: "Укажите страну: /unsubscribe argentina",
		unknownCountry: func(slug string) string {
			return fmt.Sprintf("Страна «%s» не поддерживается.", slug)
		},
		subscribeFailed: "Ошибка подписки.",
		subscribed: func(slug string) string {
			return fmt.Sprintf("Вы подписаны на уведомления по стране: %s", slug)
		},
		unsubscribeFailed: "Ошибка отписки.",
		notSubscribed: func(slug string) string {
			return fmt.Sprintf("Подписка на «%s» не найдена.", slug)
		},
		unsubscribed: func(slug string) string {
			return fmt.Sprintf("Вы отписаны от уведомлений по стране: %s", slug)
		},
		listFailed:      "Ошибка получения подписок.",
		noSubscriptions: "У вас нет активных подписок.",
		subscriptionsList: func(slugs string) string {
			return fmt.Sprintf("Ваши подписки:\n%s", slugs)
		},
		webLinkFailed: "Не удалось создать код привязки.",
		webLinkInstructions: func(code string, minutes int) string {
			return fmt.Sprintf(
				"Ваш код для привязки web-аккаунта: %s\nВведите его в личном кабинете в течение %d минут.",
				code, minutes,
			)
		},
	},
	locale.EN: {
		help: "/subscribe <country> — subscribe to notifications\n" +
			"/unsubscribe <country> — unsubscribe\n" +
			"/list — my subscriptions\n" +
			"/web_link — code to link your web account\n" +
			"/help — help\n\n" +
			telegram.DisclaimerFor(locale.EN),
		subscribeUsage:   "Specify a country: /subscribe argentina",
		unsubscribeUsage: "Specify a country: /unsubscribe argentina",
		unknownCountry: func(slug string) string {
			return fmt.Sprintf("Country \"%s\" is not supported.", slug)
		},
		subscribeFailed: "Subscription failed.",
		subscribed: func(slug string) string {
			return fmt.Sprintf("You are now subscribed to notifications for: %s", slug)
		},
		unsubscribeFailed: "Unsubscribe failed.",
		notSubscribed: func(slug string) string {
			return fmt.Sprintf("No subscription found for \"%s\".", slug)
		},
		unsubscribed: func(slug string) string {
			return fmt.Sprintf("You are unsubscribed from notifications for: %s", slug)
		},
		listFailed:      "Could not retrieve your subscriptions.",
		noSubscriptions: "You have no active subscriptions.",
		subscriptionsList: func(slugs string) string {
			return fmt.Sprintf("Your subscriptions:\n%s", slugs)
		},
		webLinkFailed: "Could not create a link code.",
		webLinkInstructions: func(code string, minutes int) string {
			return fmt.Sprintf(
				"Your web account link code: %s\nEnter it in your account within %d minutes.",
				code, minutes,
			)
		},
	},
	locale.ES: {
		help: "/subscribe <país> — suscribirse a notificaciones\n" +
			"/unsubscribe <país> — cancelar suscripción\n" +
			"/list — mis suscripciones\n" +
			"/web_link — código para vincular tu cuenta web\n" +
			"/help — ayuda\n\n" +
			telegram.DisclaimerFor(locale.ES),
		subscribeUsage:   "Indica un país: /subscribe argentina",
		unsubscribeUsage: "Indica un país: /unsubscribe argentina",
		unknownCountry: func(slug string) string {
			return fmt.Sprintf("El país «%s» no está disponible.", slug)
		},
		subscribeFailed: "No se pudo completar la suscripción.",
		subscribed: func(slug string) string {
			return fmt.Sprintf("Te has suscrito a las notificaciones de: %s", slug)
		},
		unsubscribeFailed: "No se pudo cancelar la suscripción.",
		notSubscribed: func(slug string) string {
			return fmt.Sprintf("No se encontró una suscripción para «%s».", slug)
		},
		unsubscribed: func(slug string) string {
			return fmt.Sprintf("Has cancelado la suscripción a: %s", slug)
		},
		listFailed:      "No se pudieron obtener tus suscripciones.",
		noSubscriptions: "No tienes suscripciones activas.",
		subscriptionsList: func(slugs string) string {
			return fmt.Sprintf("Tus suscripciones:\n%s", slugs)
		},
		webLinkFailed: "No se pudo crear el código de vinculación.",
		webLinkInstructions: func(code string, minutes int) string {
			return fmt.Sprintf(
				"Tu código para vincular la cuenta web: %s\nIntrodúcelo en tu cuenta antes de %d minutos.",
				code, minutes,
			)
		},
	},
}

func messagesFor(loc string) messages {
	if m, ok := catalog[loc]; ok {
		return m
	}
	return catalog[locale.Default]
}
