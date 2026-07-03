package bot

import (
	"context"
	"crypto/rand"
	"errors"
	"fmt"
	"strconv"
	"strings"
	"time"

	mongostore "github.com/country-decision-atlas/notifier/internal/mongo"
	"github.com/country-decision-atlas/notifier/internal/subscriptions"
	"github.com/country-decision-atlas/notifier/internal/telegram"
	"github.com/country-decision-atlas/notifier/internal/telegram/commands"
)

const disclaimer = telegram.Disclaimer

const helpText = `/subscribe <страна> — подписаться на уведомления
/unsubscribe <страна> — отписаться
/list — мои подписки
/web_link — код для привязки web-аккаунта
/help — помощь

` + disclaimer

type Handler struct {
	svc         *subscriptions.Service
	tg          telegram.Client
	linkCodes   mongostore.TelegramLinkCodeRepository
	linkCodeTTL time.Duration
}

func New(svc *subscriptions.Service, tg telegram.Client, linkCodes mongostore.TelegramLinkCodeRepository, linkCodeTTL time.Duration) *Handler {
	return &Handler{svc: svc, tg: tg, linkCodes: linkCodes, linkCodeTTL: linkCodeTTL}
}

func (h *Handler) Handle(ctx context.Context, update *telegram.TelegramUpdate) error {
	if update.Message == nil {
		return nil
	}
	chatID := strconv.FormatInt(update.Message.Chat.ID, 10)
	text := update.Message.Text

	var username string
	var telegramUserID string
	if update.Message.From != nil {
		telegramUserID = strconv.FormatInt(update.Message.From.ID, 10)
		username = update.Message.From.Username
	}
	if telegramUserID == "" {
		telegramUserID = chatID
	}

	cmd := commands.Parse(text)
	reply := h.dispatch(ctx, cmd, telegramUserID, username)
	return h.tg.SendMessage(ctx, chatID, reply)
}

func (h *Handler) dispatch(ctx context.Context, cmd commands.ParsedCommand, telegramUserID string, username string) string {
	switch cmd.Type {
	case commands.CmdSubscribe:
		return h.handleSubscribe(ctx, cmd, telegramUserID, username)
	case commands.CmdUnsubscribe:
		return h.handleUnsubscribe(ctx, cmd, telegramUserID)
	case commands.CmdList:
		return h.handleList(ctx, telegramUserID)
	case commands.CmdWebLink:
		return h.handleWebLink(ctx, telegramUserID)
	case commands.CmdHelp, commands.CmdUnknown:
		return helpText
	default:
		return helpText
	}
}

func (h *Handler) handleSubscribe(ctx context.Context, cmd commands.ParsedCommand, telegramUserID string, username string) string {
	if cmd.Error != "" {
		return fmt.Sprintf("Укажите страну: /subscribe argentina\n\n%s", disclaimer)
	}
	_, err := h.svc.CreateSubscription(ctx, telegramUserID, username, cmd.CountrySlug)
	if err != nil {
		if errors.Is(err, subscriptions.ErrUnknownCountry) {
			return fmt.Sprintf("Страна «%s» не поддерживается.\n\n%s", cmd.CountrySlug, disclaimer)
		}
		return fmt.Sprintf("Ошибка подписки.\n\n%s", disclaimer)
	}
	return fmt.Sprintf("Вы подписаны на уведомления по стране: %s\n\n%s", cmd.CountrySlug, disclaimer)
}

func (h *Handler) handleUnsubscribe(ctx context.Context, cmd commands.ParsedCommand, telegramUserID string) string {
	if cmd.Error != "" {
		return fmt.Sprintf("Укажите страну: /unsubscribe argentina\n\n%s", disclaimer)
	}
	sub, err := h.svc.DeleteSubscription(ctx, telegramUserID, cmd.CountrySlug)
	if err != nil {
		if errors.Is(err, subscriptions.ErrUnknownCountry) {
			return fmt.Sprintf("Страна «%s» не поддерживается.\n\n%s", cmd.CountrySlug, disclaimer)
		}
		return fmt.Sprintf("Ошибка отписки.\n\n%s", disclaimer)
	}
	if sub == nil {
		return fmt.Sprintf("Подписка на «%s» не найдена.\n\n%s", cmd.CountrySlug, disclaimer)
	}
	return fmt.Sprintf("Вы отписаны от уведомлений по стране: %s\n\n%s", cmd.CountrySlug, disclaimer)
}

func (h *Handler) handleList(ctx context.Context, telegramUserID string) string {
	subs, err := h.svc.ListSubscriptions(ctx, telegramUserID)
	if err != nil {
		return fmt.Sprintf("Ошибка получения подписок.\n\n%s", disclaimer)
	}
	if len(subs) == 0 {
		return fmt.Sprintf("У вас нет активных подписок.\n\n%s", disclaimer)
	}
	slugs := make([]string, len(subs))
	for i, s := range subs {
		slugs[i] = s.CountrySlug
	}
	return fmt.Sprintf("Ваши подписки:\n%s\n\n%s", strings.Join(slugs, "\n"), disclaimer)
}

func (h *Handler) handleWebLink(ctx context.Context, telegramUserID string) string {
	code, err := generateLinkCode()
	if err != nil {
		return fmt.Sprintf("Не удалось создать код привязки.\n\n%s", disclaimer)
	}
	codeHash := mongostore.HashLinkCode(code)
	if err := h.linkCodes.Create(ctx, telegramUserID, codeHash, h.linkCodeTTL); err != nil {
		return fmt.Sprintf("Не удалось создать код привязки.\n\n%s", disclaimer)
	}
	minutes := int(h.linkCodeTTL / time.Minute)
	return fmt.Sprintf(
		"Ваш код для привязки web-аккаунта: %s\nВведите его в личном кабинете в течение %d минут.\n\n%s",
		code, minutes, disclaimer,
	)
}

func generateLinkCode() (string, error) {
	const digits = "0123456789"
	buf := make([]byte, 6)
	if _, err := rand.Read(buf); err != nil {
		return "", err
	}
	code := make([]byte, len(buf))
	for i, b := range buf {
		code[i] = digits[int(b)%len(digits)]
	}
	return string(code), nil
}
