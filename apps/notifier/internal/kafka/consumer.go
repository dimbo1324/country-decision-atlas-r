package kafka

import (
	"context"
	"strings"

	kafkago "github.com/segmentio/kafka-go"
)

type Message struct {
	Key   []byte
	Value []byte
}

type Consumer interface {
	ReadMessage(ctx context.Context) (*Message, error)
	Close() error
}

type KafkaConsumer struct {
	reader *kafkago.Reader
}

func NewKafkaConsumer(brokers string, topic string, groupID string) *KafkaConsumer {
	r := kafkago.NewReader(kafkago.ReaderConfig{
		Brokers: strings.Split(brokers, ","),
		Topic:   topic,
		GroupID: groupID,
	})
	return &KafkaConsumer{reader: r}
}

func (c *KafkaConsumer) ReadMessage(ctx context.Context) (*Message, error) {
	msg, err := c.reader.ReadMessage(ctx)
	if err != nil {
		return nil, err
	}
	return &Message{Key: msg.Key, Value: msg.Value}, nil
}

func (c *KafkaConsumer) Close() error {
	return c.reader.Close()
}

type FakeConsumer struct {
	messages []*Message
	pos      int
}

func NewFakeConsumer(messages []*Message) *FakeConsumer {
	return &FakeConsumer{messages: messages}
}

func (f *FakeConsumer) ReadMessage(ctx context.Context) (*Message, error) {
	if f.pos >= len(f.messages) {
		<-ctx.Done()
		return nil, ctx.Err()
	}
	msg := f.messages[f.pos]
	f.pos++
	return msg, nil
}

func (f *FakeConsumer) Close() error {
	return nil
}

var _ Consumer = (*KafkaConsumer)(nil)
var _ Consumer = (*FakeConsumer)(nil)
