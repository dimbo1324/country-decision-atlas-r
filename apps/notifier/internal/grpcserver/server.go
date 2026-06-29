package grpcserver

import (
	"context"
	"crypto/subtle"
	"errors"
	"net"
	"time"

	pb "github.com/country-decision-atlas/notifier/internal/grpc/pb"
	mongostore "github.com/country-decision-atlas/notifier/internal/mongo"
	"github.com/country-decision-atlas/notifier/internal/subscriptions"
	"google.golang.org/grpc"
	"google.golang.org/grpc/codes"
	"google.golang.org/grpc/metadata"
	"google.golang.org/grpc/status"
)

type Server struct {
	pb.UnimplementedSubscriptionServiceServer
	svc         *subscriptions.Service
	deliveryLog mongostore.DeliveryLogRepository
}

func New(svc *subscriptions.Service, deliveryLog mongostore.DeliveryLogRepository) *Server {
	return &Server{svc: svc, deliveryLog: deliveryLog}
}

func (s *Server) CreateSubscription(ctx context.Context, req *pb.CreateSubscriptionRequest) (*pb.SubscriptionResponse, error) {
	sub, err := s.svc.CreateSubscription(ctx, req.TelegramUserId, req.Username, req.CountrySlug)
	if err != nil {
		if errors.Is(err, subscriptions.ErrUnknownCountry) {
			return &pb.SubscriptionResponse{Error: "unknown country"}, nil
		}
		return nil, status.Error(codes.Internal, "internal error")
	}
	return &pb.SubscriptionResponse{Subscription: toProtoSub(sub)}, nil
}

func (s *Server) DeleteSubscription(ctx context.Context, req *pb.DeleteSubscriptionRequest) (*pb.SubscriptionResponse, error) {
	sub, err := s.svc.DeleteSubscription(ctx, req.TelegramUserId, req.CountrySlug)
	if err != nil {
		if errors.Is(err, subscriptions.ErrUnknownCountry) {
			return &pb.SubscriptionResponse{Error: "unknown country"}, nil
		}
		return nil, status.Error(codes.Internal, "internal error")
	}
	if sub == nil {
		return &pb.SubscriptionResponse{
			Subscription: &pb.Subscription{
				TelegramUserId: req.TelegramUserId,
				CountrySlug:    req.CountrySlug,
				Active:         false,
			},
		}, nil
	}
	return &pb.SubscriptionResponse{Subscription: toProtoSub(sub)}, nil
}

func (s *Server) ListSubscriptions(ctx context.Context, req *pb.ListSubscriptionsRequest) (*pb.ListSubscriptionsResponse, error) {
	subs, err := s.svc.ListSubscriptions(ctx, req.TelegramUserId)
	if err != nil {
		return nil, status.Error(codes.Internal, "internal error")
	}
	pbSubs := make([]*pb.Subscription, len(subs))
	for i, sub := range subs {
		pbSubs[i] = toProtoSub(sub)
	}
	return &pb.ListSubscriptionsResponse{Subscriptions: pbSubs}, nil
}

func (s *Server) GetDeliveryStatus(ctx context.Context, req *pb.GetDeliveryStatusRequest) (*pb.GetDeliveryStatusResponse, error) {
	entries, err := s.deliveryLog.FindByUser(ctx, mongostore.DeliveryLogQuery{
		TelegramUserID: req.TelegramUserId,
		EventKey:       req.EventKey,
		CountrySlug:    req.CountrySlug,
		Limit:          req.Limit,
	})
	if err != nil {
		return nil, status.Error(codes.Internal, "internal error")
	}
	pbEntries := make([]*pb.DeliveryStatus, len(entries))
	for i, e := range entries {
		ds := &pb.DeliveryStatus{
			EventKey:       e.EventKey,
			TelegramUserId: e.TelegramUserID,
			CountrySlug:    e.CountrySlug,
			Status:         e.Status,
			SentAt:         e.SentAt.UTC().Format(time.RFC3339),
		}
		if e.Error != nil {
			ds.Error = *e.Error
		}
		pbEntries[i] = ds
	}
	return &pb.GetDeliveryStatusResponse{Entries: pbEntries}, nil
}

func toProtoSub(sub *mongostore.Subscription) *pb.Subscription {
	return &pb.Subscription{
		TelegramUserId: sub.TelegramUserID,
		CountrySlug:    sub.CountrySlug,
		Active:         sub.Active,
	}
}

func tokenAuthInterceptor(token string) grpc.UnaryServerInterceptor {
	expected := []byte("Bearer " + token)
	return func(ctx context.Context, req any, _ *grpc.UnaryServerInfo, handler grpc.UnaryHandler) (any, error) {
		if token == "" {
			return nil, status.Error(codes.Unauthenticated, "grpc auth is not configured")
		}
		md, ok := metadata.FromIncomingContext(ctx)
		if !ok {
			return nil, status.Error(codes.Unauthenticated, "missing metadata")
		}
		values := md.Get("authorization")
		if len(values) == 0 || subtle.ConstantTimeCompare([]byte(values[0]), expected) != 1 {
			return nil, status.Error(codes.Unauthenticated, "invalid token")
		}
		return handler(ctx, req)
	}
}

func Serve(ctx context.Context, addr string, authToken string, srv *Server) error {
	lis, err := net.Listen("tcp", addr)
	if err != nil {
		return err
	}
	gs := grpc.NewServer(grpc.UnaryInterceptor(tokenAuthInterceptor(authToken)))
	pb.RegisterSubscriptionServiceServer(gs, srv)
	go func() {
		<-ctx.Done()
		gs.GracefulStop()
	}()
	return gs.Serve(lis)
}
