package main

import (
	"os"
	"os/exec"
	"testing"

	"github.com/fabrizio2210/light-CICD/src/go/internal/proto/executor"
	"github.com/fabrizio2210/light-CICD/src/go/internal/rediswrapper"
	"github.com/go-redis/redismock/v8"
	"github.com/google/go-cmp/cmp"
	"google.golang.org/protobuf/encoding/prototext"
	"google.golang.org/protobuf/proto"
	"google.golang.org/protobuf/testing/protocmp"
)

func fakeExecCommand(command string, args ...string) *exec.Cmd {
	cs := []string{"-test.run=TestHelperProcess", "--", command}
	cs = append(cs, args...)
	cmd := exec.Command(os.Args[0], cs...)
	cmd.Env = []string{"GO_WANT_HELPER_PROCESS=1"}
	return cmd
}

func TestRunDocker(t *testing.T) {
	execCommand = fakeExecCommand
	defer func() { execCommand = exec.Command }()
	var input executor.Execution
	runner := &Docker{}
	err := runner.Run(&input)
	if err != nil {
		t.Errorf("Expected nil error, got %#v", err)
	}
}

func TestHelperProcess(t *testing.T) {
	if os.Getenv("GO_WANT_HELPER_PROCESS") != "1" {
		return
	}
	// some code here to check arguments perhaps?

	// some code to emaulate output?
	// fmt.Fprintf(os.Stdout, dockerRunResult)

	os.Exit(0)
}

type fakeDocker struct {
	arg *executor.Execution
}

func (f *fakeDocker) Run(e *executor.Execution) error {
	f.arg = e
	return nil
}

func TestWaitForJob(t *testing.T) {
	inputExecution := &executor.Execution{
		Id:        proto.String("123"),
		ProjectId: proto.String("222"),
		EnvironmentVariable: []*executor.EnvironmentVariable{
			{
				Name:  proto.String("key"),
				Value: proto.String("value_of_env"),
			},
		},
	}
	var redisMock redismock.ClientMock
	rediswrapper.RedisClient, redisMock = redismock.NewClientMock()
	text, err := prototext.Marshal(inputExecution)
	if err != nil {
		t.Errorf("Error during proto conversion: %v", err)
	}
	redisMock.ExpectBLPop(0, "executions").SetVal([]string{"executions", string(text)})
	fakeInterface := &fakeDocker{}
	WaitForJob(fakeInterface)
	diff := cmp.Diff(fakeInterface.arg, inputExecution, protocmp.Transform())
	if diff != "" {
		t.Errorf("Argument passed to WaitForJob is different: %v", diff)
	}
}
