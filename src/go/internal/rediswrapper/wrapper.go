package rediswrapper

import (
	"context"
	"log"

	"github.com/go-redis/redis/v8"
)

var RedisClient *redis.Client

func ConnectRedis(address string) *redis.Client {
	log.Printf("Connecting to \"%s\" for Redis", address)
	return redis.NewClient(&redis.Options{
		Addr: address,
	})
}

func Publish(ctx context.Context, topic string, json []byte) error {
	if err := RedisClient.Publish(ctx, topic, json).Err(); err != nil {
		return err
	}
	return nil
}

func WaitFor(ctx context.Context, queue string) (string, error) {
	msg, err := RedisClient.BLPop(ctx, 0, queue).Result()
	if err != nil {
		return "", err
	}
	return msg[1], nil
}
