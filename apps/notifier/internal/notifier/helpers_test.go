package notifier

import (
	"context"
	"errors"
)

type errorClient struct{}

func (e *errorClient) SendMessage(_ context.Context, _ string, _ string) error {
	return errors.New("telegram send failed")
}
