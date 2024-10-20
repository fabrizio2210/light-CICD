package main

import (
	"context"
	"fmt"
	"log"
	"os/exec"

	"github.com/fabrizio2210/light-CICD/src/go/internal/proto/executor"
	"github.com/fabrizio2210/light-CICD/src/go/internal/rediswrapper"
)

var execCommand = exec.Command

func RunDocker(execution *executor.Execution) ([]byte, error) {
	cmd := execCommand("docker", "run", "-d", "  ")
	return cmd.CombinedOutput()
}

func WaitForJob() {
	ctx := context.Background()
	e, err := rediswrapper.WaitFor(ctx, "executions")
	if err != nil {
		log.Printf("Error: %v\n", err)
	}
	fmt.Printf("Execution: %v\n", e)

}

func main() {
	fmt.Println("This is an executor")
	rediswrapper.RedisClient = rediswrapper.ConnectRedis("redis:6379")
	fmt.Printf("Redis client: %+v\n", rediswrapper.RedisClient)
	WaitForJob()
}
