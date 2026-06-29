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

func startTestServer(t *testing.T) (pb.SubscriptionServiceClient, *mongostore.InMemorySubscriptionRepository, *mongostore.InMemoryDeliveryLogRepository) {
	t.Helper()
	subsRepo := mongostore.NewInMemorySubscriptionRepository(nil)
	identities := mongostore.NewInMemoryTelegramIdentityRepository()
	dl := mongostore.NewInMemoryDeliveryLogRepository()
	svc := subscriptions.New(subsRepo, identities, []string{"argentina", "russia", "uruguay"})

	srv := New(svc, dl)

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

	return pb.NewSubscriptionServiceClient(conn), subsRepo, dl
}

func TestGRPCServerStarts(t *testing.T) {
	client, _, _ := startTestServer(t)
	if client == nil {
		t.Fatal("expected non-nil client")
	}
}

func TestGRPCCreateSubscription(t *testing.T) {
	client, _, _ := startTestServer(t)
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
	client, _, _ := startTestServer(t)
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
	client, _, _ := startTestServer(t)
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
	client, _, _ := startTestServer(t)
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
	client, _, _ := startTestServer(t)
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
	client, _, dl := startTestServer(t)
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
	client, _, dl := startTestServer(t)
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
	client, _, dl := startTestServer(t)
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
	client, _, dl := startTestServer(t)
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

func TestGRPCInvalidCountryRejected(t *testing.T) {
	client, _, _ := startTestServer(t)
	ctx := context.Background()
	resp, err := client.CreateSubscription(ctx, &pb.CreateSubscriptionRequest{
		TelegramUserId: "user1", Username: "dima", CountrySlug: "germany",
	})
	if err != nil {
		t.Fatalf("unexpected transport error: %v", err)
	}
	if resp.Error == "" {
		t.Error("want error for unknown country")
	}
}

func TestGRPCWebUserIDRemainsNull(t *testing.T) {
	client, _, _ := startTestServer(t)
	resp, _ := client.CreateSubscription(context.Background(), &pb.CreateSubscriptionRequest{
		TelegramUserId: "user1", Username: "dima", CountrySlug: "argentina",
	})
	if resp.Subscription.WebUserId != "" {
		t.Errorf("want empty WebUserId got %s", resp.Subscription.WebUserId)
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
