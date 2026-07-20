FROM golang:1.25-alpine AS builder
WORKDIR /build
COPY apps/notifier/go.mod apps/notifier/go.sum ./
RUN go mod download
COPY apps/notifier/ ./
RUN CGO_ENABLED=0 GOOS=linux go build -o notifier ./cmd/notifier

FROM alpine:3.20
# Runs unprivileged, matching apps/api/Dockerfile: the notifier only talks to
# Kafka/Mongo/Telegram over the network and writes nothing locally, and its
# listen ports (8081 gRPC, 9090 metrics) are above 1024, so root buys nothing
# and only widens the blast radius if the process is ever compromised.
RUN apk add --no-cache ca-certificates tzdata \
    && addgroup -S app \
    && adduser -S -G app app
WORKDIR /app
COPY --from=builder /build/notifier ./notifier
USER app
EXPOSE 8081
ENTRYPOINT ["./notifier"]
