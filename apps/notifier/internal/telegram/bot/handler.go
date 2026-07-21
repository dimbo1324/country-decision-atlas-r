package bot

import (
	"context"
	"crypto/rand"
	"errors"
	"log"
	"strconv"
	"strings"
	"time"

	"github.com/country-decision-atlas/notifier/internal/locale"
	mongostore "github.com/country-decision-atlas/notifier/internal/mongo"
	"github.com/country-decision-atlas/notifier/internal/subscriptions"
	"github.com/country-decision-atlas/notifier/internal/telegram"
	"github.com/country-decision-atlas/notifier/internal/telegram/commands"
)

// disclaimer is the pre-i18n Russian-only constant, kept for backward
// compatibility with existing references (including this package's own
// tests); reply text now goes through withDisclaimer(loc, ...) instead.
const disclaimer = telegram.Disclaimer

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
	var languageCode string
	if update.Message.From != nil {
		telegramUserID = strconv.FormatInt(update.Message.From.ID, 10)
		username = update.Message.From.Username
		languageCode = update.Message.From.LanguageCode
	}
	if telegramUserID == "" {
		telegramUserID = chatID
	}

	// Every live interaction is the only place a real language_code is
	// available (gRPC-created subscriptions have no Telegram update at
	// all) -- persisted so future event notifications can use it too. A
	// failure here shouldn't block replying to the user, but isn't
	// swallowed silently either.
	resolvedLocale := locale.Resolve(languageCode)
	if err := h.svc.SetTelegramLocale(ctx, telegramUserID, resolvedLocale); err != nil {
		log.Printf("set telegram locale error user=%s: %v", telegramUserID, err)
	}

	cmd := commands.Parse(text)
	reply := h.dispatch(ctx, cmd, telegramUserID, username, resolvedLocale)
	return h.tg.SendMessage(ctx, chatID, reply)
}

func (h *Handler) dispatch(ctx context.Context, cmd commands.ParsedCommand, telegramUserID string, username string, loc string) string {
	msgs := messagesFor(loc)
	switch cmd.Type {
	case commands.CmdSubscribe:
		return h.handleSubscribe(ctx, cmd, telegramUserID, username, loc, msgs)
	case commands.CmdUnsubscribe:
		return h.handleUnsubscribe(ctx, cmd, telegramUserID, loc, msgs)
	case commands.CmdList:
		return h.handleList(ctx, telegramUserID, loc, msgs)
	case commands.CmdWebLink:
		return h.handleWebLink(ctx, telegramUserID, loc, msgs)
	case commands.CmdHelp, commands.CmdUnknown:
		return msgs.help
	default:
		return msgs.help
	}
}

func (h *Handler) handleSubscribe(ctx context.Context, cmd commands.ParsedCommand, telegramUserID string, username string, loc string, msgs messages) string {
	if cmd.Error != "" {
		return withDisclaimer(loc, msgs.subscribeUsage)
	}
	_, err := h.svc.CreateSubscription(ctx, telegramUserID, username, cmd.CountrySlug)
	if err != nil {
		if errors.Is(err, subscriptions.ErrUnknownCountry) {
			return withDisclaimer(loc, msgs.unknownCountry(cmd.CountrySlug))
		}
		return withDisclaimer(loc, msgs.subscribeFailed)
	}
	return withDisclaimer(loc, msgs.subscribed(cmd.CountrySlug))
}

func (h *Handler) handleUnsubscribe(ctx context.Context, cmd commands.ParsedCommand, telegramUserID string, loc string, msgs messages) string {
	if cmd.Error != "" {
		return withDisclaimer(loc, msgs.unsubscribeUsage)
	}
	sub, err := h.svc.DeleteSubscription(ctx, telegramUserID, cmd.CountrySlug)
	if err != nil {
		if errors.Is(err, subscriptions.ErrUnknownCountry) {
			return withDisclaimer(loc, msgs.unknownCountry(cmd.CountrySlug))
		}
		return withDisclaimer(loc, msgs.unsubscribeFailed)
	}
	if sub == nil {
		return withDisclaimer(loc, msgs.notSubscribed(cmd.CountrySlug))
	}
	return withDisclaimer(loc, msgs.unsubscribed(cmd.CountrySlug))
}

func (h *Handler) handleList(ctx context.Context, telegramUserID string, loc string, msgs messages) string {
	subs, err := h.svc.ListSubscriptions(ctx, telegramUserID)
	if err != nil {
		return withDisclaimer(loc, msgs.listFailed)
	}
	if len(subs) == 0 {
		return withDisclaimer(loc, msgs.noSubscriptions)
	}
	slugs := make([]string, len(subs))
	for i, s := range subs {
		slugs[i] = s.CountrySlug
	}
	return withDisclaimer(loc, msgs.subscriptionsList(strings.Join(slugs, "\n")))
}

func (h *Handler) handleWebLink(ctx context.Context, telegramUserID string, loc string, msgs messages) string {
	code, err := generateLinkCode()
	if err != nil {
		return withDisclaimer(loc, msgs.webLinkFailed)
	}
	codeHash := mongostore.HashLinkCode(code)
	if err := h.linkCodes.Create(ctx, telegramUserID, codeHash, h.linkCodeTTL); err != nil {
		return withDisclaimer(loc, msgs.webLinkFailed)
	}
	minutes := int(h.linkCodeTTL / time.Minute)
	return withDisclaimer(loc, msgs.webLinkInstructions(code, minutes))
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
