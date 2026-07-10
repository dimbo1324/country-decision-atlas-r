package grpcserver

import (
	"context"
	"net"
	"testing"
	"time"

	pb "github.com/country-decision-atlas/notifier/internal/grpc/pb"
	"github.com/country-decision-atlas/notifier/internal/metrics"
	mongostore "github.com/country-decision-atlas/notifier/internal/mongo"
	"github.com/country-decision-atlas/notifier/internal/subscriptions"
	"google.golang.org/grpc"
	"google.golang.org/grpc/credentials/insecure"
	"google.golang.org/grpc/metadata"
)

func startTestServer(t *testing.T) (
	pb.SubscriptionServiceClient,
	*mongostore.InMemorySubscriptionRepository,
	*mongostore.InMemoryDeliveryLogRepository,
	*mongostore.InMemoryTelegramIdentityRepository,
	*mongostore.InMemoryTelegramLinkCodeRepository,
) {
	t.Helper()
	subsRepo := mongostore.NewInMemorySubscriptionRepository(nil)
	identities := mongostore.NewInMemoryTelegramIdentityRepository()
	linkCodes := mongostore.NewInMemoryTelegramLinkCodeRepository()
	dl := mongostore.NewInMemoryDeliveryLogRepository()
	svc := subscriptions.New(subsRepo, identities)

	srv := New(svc, dl, identities, linkCodes)

	lis, err := net.Listen("tcp", "127.0.0.1:0")
	if err != nil {
		t.Fatalf("failed to listen: %v", err)
	}
	gs := grpc.NewServer()
	pb.RegisterSubscriptionServiceServer(gs, srv)

	go func() { _ = gs.Serve(lis) }()
	t.Cleanup(gs.Stop)

	conn, err := grpc.NewClient(lis.Addr().String(), grpc.WithTransportCredentials(insecure.NewCredentials()))
	if err != nil {
		t.Fatalf("failed to dial: %v", err)
	}
	t.Cleanup(func() { _ = conn.Close() })

	return pb.NewSubscriptionServiceClient(conn), subsRepo, dl, identities, linkCodes
}

func TestGRPCServerStarts(t *testing.T) {
	client, _, _, _, _ := startTestServer(t)
	if client == nil {
		t.Fatal("expected non-nil client")
	}
}

func TestGRPCCreateSubscription(t *testing.T) {
	client, _, _, _, _ := startTestServer(t)
	ctx := context.Background()
	resp, err := client.CreateSubscription(ctx, &pb.CreateSubscriptionRequest{
		TelegramUserId: "user1",
		Username:       "dima",
		CountrySlug:    "argentina",
	})
	if err != nil {
		t.Fatalf("unexpected error: %v", err)
	}
	if resp.Error != "" {
		t.Errorf("unexpected error in response: %s", resp.Error)
	}
	if resp.Subscription == nil {
		t.Fatal("expected subscription in response")
	}
	if resp.Subscription.CountrySlug != "argentina" {
		t.Errorf("want argentina got %s", resp.Subscription.CountrySlug)
	}
	if !resp.Subscription.Active {
		t.Error("want active subscription")
	}
}

func TestGRPCCreateSubscriptionReactivates(t *testing.T) {
	client, _, _, _, _ := startTestServer(t)
	ctx := context.Background()
	_, _ = client.CreateSubscription(ctx, &pb.CreateSubscriptionRequest{
		TelegramUserId: "user1", Username: "dima", CountrySlug: "argentina",
	})
	_, _ = client.DeleteSubscription(ctx, &pb.DeleteSubscriptionRequest{
		TelegramUserId: "user1", CountrySlug: "argentina",
	})
	resp, err := client.CreateSubscription(ctx, &pb.CreateSubscriptionRequest{
		TelegramUserId: "user1", Username: "dima", CountrySlug: "argentina",
	})
	if err != nil {
		t.Fatalf("unexpected error: %v", err)
	}
	if !resp.Subscription.Active {
		t.Error("want reactivated subscription")
	}
}

func TestGRPCDeleteSubscription(t *testing.T) {
	client, _, _, _, _ := startTestServer(t)
	ctx := context.Background()
	_, _ = client.CreateSubscription(ctx, &pb.CreateSubscriptionRequest{
		TelegramUserId: "user1", Username: "dima", CountrySlug: "argentina",
	})
	resp, err := client.DeleteSubscription(ctx, &pb.DeleteSubscriptionRequest{
		TelegramUserId: "user1", CountrySlug: "argentina",
	})
	if err != nil {
		t.Fatalf("unexpected error: %v", err)
	}
	if resp.Subscription.Active {
		t.Error("want inactive after delete")
	}
}

func TestGRPCDeleteSubscriptionIdempotent(t *testing.T) {
	client, _, _, _, _ := startTestServer(t)
	ctx := context.Background()
	resp, err := client.DeleteSubscription(ctx, &pb.DeleteSubscriptionRequest{
		TelegramUserId: "user1", CountrySlug: "argentina",
	})
	if err != nil {
		t.Fatalf("unexpected error on missing: %v", err)
	}
	if resp.Error != "" {
		t.Errorf("unexpected error: %s", resp.Error)
	}
}

func TestGRPCListSubscriptionsActiveOnly(t *testing.T) {
	client, _, _, _, _ := startTestServer(t)
	ctx := context.Background()
	_, _ = client.CreateSubscription(ctx, &pb.CreateSubscriptionRequest{
		TelegramUserId: "user1", Username: "dima", CountrySlug: "argentina",
	})
	_, _ = client.CreateSubscription(ctx, &pb.CreateSubscriptionRequest{
		TelegramUserId: "user1", Username: "dima", CountrySlug: "russia",
	})
	_, _ = client.DeleteSubscription(ctx, &pb.DeleteSubscriptionRequest{
		TelegramUserId: "user1", CountrySlug: "russia",
	})

	resp, err := client.ListSubscriptions(ctx, &pb.ListSubscriptionsRequest{TelegramUserId: "user1"})
	if err != nil {
		t.Fatalf("unexpected error: %v", err)
	}
	if len(resp.Subscriptions) != 1 {
		t.Errorf("want 1 active subscription got %d", len(resp.Subscriptions))
	}
}

func TestGRPCGetDeliveryStatus(t *testing.T) {
	client, _, dl, _, _ := startTestServer(t)
	ctx := context.Background()
	errStr := "test error"
	_ = dl.Insert(ctx, &mongostore.DeliveryLogEntry{
		EventKey:       "key-1",
		TelegramUserID: "user1",
		CountrySlug:    "argentina",
		Status:         "sent",
		SentAt:         time.Now().UTC(),
	})
	_ = dl.Insert(ctx, &mongostore.DeliveryLogEntry{
		EventKey:       "key-2",
		TelegramUserID: "user1",
		CountrySlug:    "russia",
		Status:         "failed",
		SentAt:         time.Now().UTC(),
		Error:          &errStr,
	})

	resp, err := client.GetDeliveryStatus(ctx, &pb.GetDeliveryStatusRequest{
		TelegramUserId: "user1",
		Limit:          10,
	})
	if err != nil {
		t.Fatalf("unexpected error: %v", err)
	}
	if len(resp.Entries) != 2 {
		t.Errorf("want 2 entries got %d", len(resp.Entries))
	}
}

func TestGRPCGetDeliveryStatusFilterByEventKey(t *testing.T) {
	client, _, dl, _, _ := startTestServer(t)
	ctx := context.Background()
	_ = dl.Insert(ctx, &mongostore.DeliveryLogEntry{
		EventKey: "key-1", TelegramUserID: "user1", CountrySlug: "argentina", Status: "sent", SentAt: time.Now().UTC(),
	})
	_ = dl.Insert(ctx, &mongostore.DeliveryLogEntry{
		EventKey: "key-2", TelegramUserID: "user1", CountrySlug: "argentina", Status: "sent", SentAt: time.Now().UTC(),
	})

	resp, err := client.GetDeliveryStatus(ctx, &pb.GetDeliveryStatusRequest{
		TelegramUserId: "user1",
		EventKey:       "key-1",
		Limit:          10,
	})
	if err != nil {
		t.Fatalf("unexpected error: %v", err)
	}
	if len(resp.Entries) != 1 {
		t.Errorf("want 1 entry got %d", len(resp.Entries))
	}
}

func TestGRPCGetDeliveryStatusFilterByCountry(t *testing.T) {
	client, _, dl, _, _ := startTestServer(t)
	ctx := context.Background()
	_ = dl.Insert(ctx, &mongostore.DeliveryLogEntry{
		EventKey: "key-1", TelegramUserID: "user1", CountrySlug: "argentina", Status: "sent", SentAt: time.Now().UTC(),
	})
	_ = dl.Insert(ctx, &mongostore.DeliveryLogEntry{
		EventKey: "key-2", TelegramUserID: "user1", CountrySlug: "russia", Status: "sent", SentAt: time.Now().UTC(),
	})

	resp, err := client.GetDeliveryStatus(ctx, &pb.GetDeliveryStatusRequest{
		TelegramUserId: "user1",
		CountrySlug:    "russia",
		Limit:          10,
	})
	if err != nil {
		t.Fatalf("unexpected error: %v", err)
	}
	if len(resp.Entries) != 1 {
		t.Errorf("want 1 entry got %d", len(resp.Entries))
	}
}

func TestGRPCGetDeliveryStatusAppliesLimit(t *testing.T) {
	client, _, dl, _, _ := startTestServer(t)
	ctx := context.Background()
	for i := 0; i < 5; i++ {
		_ = dl.Insert(ctx, &mongostore.DeliveryLogEntry{
			EventKey: "key", TelegramUserID: "user1", CountrySlug: "argentina", Status: "sent", SentAt: time.Now().UTC(),
		})
	}

	resp, err := client.GetDeliveryStatus(ctx, &pb.GetDeliveryStatusRequest{
		TelegramUserId: "user1",
		Limit:          2,
	})
	if err != nil {
		t.Fatalf("unexpected error: %v", err)
	}
	if len(resp.Entries) != 2 {
		t.Errorf("want 2 entries (limit) got %d", len(resp.Entries))
	}
}

func TestGRPCCountryNotInAnyStaticListIsAccepted(t *testing.T) {
	// P2-13, Аудит-эпизод 5: no hardcoded allow-list on the notifier side
	// anymore, so a country slug it has never seen before must succeed.
	client, _, _, _, _ := startTestServer(t)
	ctx := context.Background()
	resp, err := client.CreateSubscription(ctx, &pb.CreateSubscriptionRequest{
		TelegramUserId: "user1", Username: "dima", CountrySlug: "germany",
	})
	if err != nil {
		t.Fatalf("unexpected transport error: %v", err)
	}
	if resp.Error != "" {
		t.Errorf("want no error got %s", resp.Error)
	}
}

func TestGRPCEmptyCountryRejected(t *testing.T) {
	client, _, _, _, _ := startTestServer(t)
	ctx := context.Background()
	resp, err := client.CreateSubscription(ctx, &pb.CreateSubscriptionRequest{
		TelegramUserId: "user1", Username: "dima", CountrySlug: "   ",
	})
	if err != nil {
		t.Fatalf("unexpected transport error: %v", err)
	}
	if resp.Error == "" {
		t.Error("want error for empty country slug")
	}
}

func TestGRPCWebUserIDRemainsNull(t *testing.T) {
	client, _, _, _, _ := startTestServer(t)
	resp, _ := client.CreateSubscription(context.Background(), &pb.CreateSubscriptionRequest{
		TelegramUserId: "user1", Username: "dima", CountrySlug: "argentina",
	})
	if resp.Subscription.WebUserId != "" {
		t.Errorf("want empty WebUserId got %s", resp.Subscription.WebUserId)
	}
}

func TestGRPCConsumeTelegramWebLinkCodeSuccess(t *testing.T) {
	client, _, _, identities, linkCodes := startTestServer(t)
	ctx := context.Background()
	if err := linkCodes.Create(ctx, "telegram-user-1", mongostore.HashLinkCode("123456"), 10*time.Minute); err != nil {
		t.Fatalf("seed link code: %v", err)
	}

	resp, err := client.ConsumeTelegramWebLinkCode(ctx, &pb.ConsumeTelegramWebLinkCodeRequest{
		Code:      "123456",
		WebUserId: "web-user-1",
	})
	if err != nil {
		t.Fatalf("unexpected error: %v", err)
	}
	if !resp.Ok {
		t.Fatalf("want ok=true got error=%s", resp.Error)
	}
	if resp.TelegramUserId != "telegram-user-1" {
		t.Errorf("want telegram-user-1 got %s", resp.TelegramUserId)
	}

	linked, webUserID, err := identities.GetLinkStatus(ctx, "telegram-user-1")
	if err != nil {
		t.Fatalf("unexpected error: %v", err)
	}
	if !linked {
		t.Error("want identity linked after consume")
	}
	if webUserID != "web-user-1" {
		t.Errorf("want web-user-1 got %s", webUserID)
	}
}

func TestGRPCConsumeTelegramWebLinkCodeInvalidCode(t *testing.T) {
	client, _, _, _, _ := startTestServer(t)
	resp, err := client.ConsumeTelegramWebLinkCode(context.Background(), &pb.ConsumeTelegramWebLinkCodeRequest{
		Code:      "000000",
		WebUserId: "web-user-1",
	})
	if err != nil {
		t.Fatalf("unexpected transport error: %v", err)
	}
	if resp.Ok {
		t.Fatal("want ok=false for unknown code")
	}
	if resp.Error != "invalid_code" {
		t.Errorf("want invalid_code got %s", resp.Error)
	}
}

func TestGRPCConsumeTelegramWebLinkCodeExpired(t *testing.T) {
	client, _, _, _, linkCodes := startTestServer(t)
	ctx := context.Background()
	if err := linkCodes.Create(ctx, "telegram-user-2", mongostore.HashLinkCode("222222"), -1*time.Minute); err != nil {
		t.Fatalf("seed link code: %v", err)
	}

	resp, err := client.ConsumeTelegramWebLinkCode(ctx, &pb.ConsumeTelegramWebLinkCodeRequest{
		Code:      "222222",
		WebUserId: "web-user-2",
	})
	if err != nil {
		t.Fatalf("unexpected transport error: %v", err)
	}
	if resp.Ok {
		t.Fatal("want ok=false for expired code")
	}
	if resp.Error != "expired_code" {
		t.Errorf("want expired_code got %s", resp.Error)
	}
}

func TestGRPCConsumeTelegramWebLinkCodeAlreadyUsed(t *testing.T) {
	client, _, _, _, linkCodes := startTestServer(t)
	ctx := context.Background()
	if err := linkCodes.Create(ctx, "telegram-user-3", mongostore.HashLinkCode("333333"), 10*time.Minute); err != nil {
		t.Fatalf("seed link code: %v", err)
	}

	req := &pb.ConsumeTelegramWebLinkCodeRequest{Code: "333333", WebUserId: "web-user-3"}
	if _, err := client.ConsumeTelegramWebLinkCode(ctx, req); err != nil {
		t.Fatalf("first consume: %v", err)
	}

	resp, err := client.ConsumeTelegramWebLinkCode(ctx, req)
	if err != nil {
		t.Fatalf("unexpected transport error: %v", err)
	}
	if resp.Ok {
		t.Fatal("want ok=false for already-used code")
	}
	if resp.Error != "already_used" {
		t.Errorf("want already_used got %s", resp.Error)
	}
}

func TestGRPCGetTelegramIdentityLinkStatusLinked(t *testing.T) {
	client, _, _, identities, _ := startTestServer(t)
	ctx := context.Background()
	if err := identities.SetWebUserID(ctx, "telegram-user-4", "web-user-4"); err != nil {
		t.Fatalf("seed identity: %v", err)
	}

	resp, err := client.GetTelegramIdentityLinkStatus(ctx, &pb.GetTelegramIdentityLinkStatusRequest{
		TelegramUserId: "telegram-user-4",
	})
	if err != nil {
		t.Fatalf("unexpected error: %v", err)
	}
	if !resp.Linked {
		t.Fatal("want linked=true")
	}
	if resp.WebUserId != "web-user-4" {
		t.Errorf("want web-user-4 got %s", resp.WebUserId)
	}
}

func TestGRPCGetTelegramIdentityLinkStatusNotLinked(t *testing.T) {
	client, _, _, _, _ := startTestServer(t)
	resp, err := client.GetTelegramIdentityLinkStatus(context.Background(), &pb.GetTelegramIdentityLinkStatusRequest{
		TelegramUserId: "never-linked",
	})
	if err != nil {
		t.Fatalf("unexpected error: %v", err)
	}
	if resp.Linked {
		t.Error("want linked=false for unknown telegram user")
	}
}

func TestGRPCUnlinkTelegramWebUserClearsWebUserID(t *testing.T) {
	client, _, _, identities, _ := startTestServer(t)
	ctx := context.Background()
	if err := identities.SetWebUserID(ctx, "telegram-user-5", "web-user-5"); err != nil {
		t.Fatalf("seed identity: %v", err)
	}

	resp, err := client.UnlinkTelegramWebUser(ctx, &pb.UnlinkTelegramWebUserRequest{
		TelegramUserId: "telegram-user-5",
	})
	if err != nil {
		t.Fatalf("unexpected error: %v", err)
	}
	if !resp.Ok {
		t.Fatal("want ok=true")
	}

	linked, _, err := identities.GetLinkStatus(ctx, "telegram-user-5")
	if err != nil {
		t.Fatalf("unexpected error: %v", err)
	}
	if linked {
		t.Error("want unlinked after UnlinkTelegramWebUser")
	}
}

func TestGRPCAuthFailedMetric(t *testing.T) {
	m := metrics.New()
	interceptor := tokenAuthInterceptor("secret", m)
	ctx := metadata.NewIncomingContext(context.Background(), metadata.Pairs("authorization", "Bearer wrong"))

	_, err := interceptor(ctx, nil, &grpc.UnaryServerInfo{FullMethod: "/test"}, func(context.Context, any) (any, error) {
		t.Fatal("handler should not be called with invalid token")
		return nil, nil
	})

	if err == nil {
		t.Fatal("expected unauthenticated error")
	}
	snapshot := m.Snapshot()
	if snapshot.GRPCRequests != 1 {
		t.Errorf("want grpc_requests=1 got %d", snapshot.GRPCRequests)
	}
	if snapshot.GRPCAuthFailed != 1 {
		t.Errorf("want grpc_auth_failed=1 got %d", snapshot.GRPCAuthFailed)
	}
}
