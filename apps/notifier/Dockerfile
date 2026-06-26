FROM golang:1.23-alpine AS builder
WORKDIR /build
COPY apps/notifier/go.mod apps/notifier/go.sum ./
RUN go mod download
COPY apps/notifier/ ./
RUN CGO_ENABLED=0 GOOS=linux go build -o notifier ./cmd/notifier

FROM alpine:3.20
RUN apk add --no-cache ca-certificates tzdata
WORKDIR /app
COPY --from=builder /build/notifier ./notifier
EXPOSE 8081
ENTRYPOINT ["./notifier"]
