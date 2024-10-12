package main

import (
  "context"
  "fmt"
  "log"

  "github.com/fabrizio2210/light-CICD/src/go/internal/rediswrapper"
  )

func main() {
	fmt.Println("This is an executor")
  rediswrapper.RedisClient = rediswrapper.ConnectRedis("redis:6379")
  fmt.Printf("Redis client: %+v\n", rediswrapper.RedisClient)

  ctx := context.Background()
  e, err := rediswrapper.WaitFor(ctx, "executions")
  if err != nil {
    log.Printf("Error: %v\n", err)
  }
  fmt.Printf("Execution: %v\n", e)
  err = rediswrapper.Publish(ctx, "topic", []byte{})
  if err != nil {
    log.Printf("Error: %v\n", err)
  }
}
