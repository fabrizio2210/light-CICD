package main

import (
	"context"
	"fmt"
	"log"
	"os/exec"

	epb "github.com/fabrizio2210/light-CICD/src/go/internal/proto/executor"
	"github.com/fabrizio2210/light-CICD/src/go/internal/rediswrapper"
	"google.golang.org/protobuf/encoding/prototext"
)

var execCommand = exec.Command

type Executor interface {
	Run(*epb.Execution) error
}

type Docker struct {
}

func (d *Docker) Run(execution *epb.Execution) error {
	cmd := execCommand("docker", "run", "-d", "  ")
	_, err := cmd.CombinedOutput()
	return err
}

func WaitForJob(executor Executor) error {
	ctx := context.Background()
	e, err := rediswrapper.WaitFor(ctx, "executions")
	if err != nil {
		log.Printf("Error: %v\n", err)
	}
	fmt.Printf("Execution: %v\n", e)
	execution := &epb.Execution{}
	prototext.Unmarshal([]byte(e), execution)
	return executor.Run(execution)
}

func main() {
	fmt.Println("This is an executor")
	rediswrapper.RedisClient = rediswrapper.ConnectRedis("redis:6379")
	fmt.Printf("Redis client: %+v\n", rediswrapper.RedisClient)
	docker := &Docker{}
	WaitForJob(docker)
}
