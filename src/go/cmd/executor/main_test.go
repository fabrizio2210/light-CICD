package main

import (
	"fmt"
	"os"
	"os/exec"
	"testing"

	"github.com/fabrizio2210/light-CICD/src/go/internal/proto/executor"
	"github.com/fabrizio2210/light-CICD/src/go/internal/rediswrapper"
	"github.com/go-redis/redismock/v8"
)

func fakeExecCommand(command string, args ...string) *exec.Cmd {
	cs := []string{"-test.run=TestHelperProcess", "--", command}
	cs = append(cs, args...)
	cmd := exec.Command(os.Args[0], cs...)
	cmd.Env = []string{"GO_WANT_HELPER_PROCESS=1"}
	return cmd
}

const dockerRunResult = "foo!"

func TestRunDocker(t *testing.T) {
	execCommand = fakeExecCommand
	defer func() { execCommand = exec.Command }()
	var input executor.Execution
	out, err := RunDocker(&input)
	if err != nil {
		t.Errorf("Expected nil error, got %#v", err)
	}
	if string(out) != dockerRunResult {
		t.Errorf("Expected %q, got %q", dockerRunResult, out)
	}
}

func TestHelperProcess(t *testing.T) {
	if os.Getenv("GO_WANT_HELPER_PROCESS") != "1" {
		return
	}
	// some code here to check arguments perhaps?
	fmt.Fprintf(os.Stdout, dockerRunResult)
	os.Exit(0)
}

func TestWaitForJob(t *testing.T) {
	var redisMock redismock.ClientMock
	rediswrapper.RedisClient, redisMock = redismock.NewClientMock()
	redisMock.ExpectBLPop(0, "executions").SetVal([]string{"test_execution"})
	WaitForJob()
}
