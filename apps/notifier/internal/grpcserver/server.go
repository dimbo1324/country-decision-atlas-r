package grpcserver

import (
	"context"
	"errors"
	"net"

	pb "github.com/country-decision-atlas/notifier/internal/grpc/pb"
	mongostore "github.com/country-decision-atlas/notifier/internal/mongo"
	"github.com/country-decision-atlas/notifier/internal/subscriptions"
	"google.golang.org/grpc"
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
		return &pb.SubscriptionResponse{Error: err.Error()}, nil
	}
	return &pb.SubscriptionResponse{
		Subscription: toProtoSub(sub),
	}, nil
}

func (s *Server) DeleteSubscription(ctx context.Context, req *pb.DeleteSubscriptionRequest) (*pb.SubscriptionResponse, error) {
	sub, err := s.svc.DeleteSubscription(ctx, req.TelegramUserId, req.CountrySlug)
	if err != nil {
		if errors.Is(err, subscriptions.ErrUnknownCountry) {
			return &pb.SubscriptionResponse{Error: "unknown country"}, nil
		}
		return &pb.SubscriptionResponse{Error: err.Error()}, nil
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
	return &pb.SubscriptionResponse{
		Subscription: toProtoSub(sub),
	}, nil
}

func (s *Server) ListSubscriptions(ctx context.Context, req *pb.ListSubscriptionsRequest) (*pb.ListSubscriptionsResponse, error) {
	subs, err := s.svc.ListSubscriptions(ctx, req.TelegramUserId)
	if err != nil {
		return &pb.ListSubscriptionsResponse{}, err
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
		return &pb.GetDeliveryStatusResponse{}, err
	}
	pbEntries := make([]*pb.DeliveryStatus, len(entries))
	for i, e := range entries {
		ds := &pb.DeliveryStatus{
			EventKey:       e.EventKey,
			TelegramUserId: e.TelegramUserID,
			CountrySlug:    e.CountrySlug,
			Status:         e.Status,
			SentAt:         e.SentAt.Format("2006-01-02T15:04:05Z"),
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

func Listen(addr string, srv *Server) error {
	lis, err := net.Listen("tcp", addr)
	if err != nil {
		return err
	}
	s := grpc.NewServer()
	pb.RegisterSubscriptionServiceServer(s, srv)
	return s.Serve(lis)
}
