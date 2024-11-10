package main

import (
	"fmt"
	"io"
	"os"
	"os/exec"
	"testing"

	epb "github.com/fabrizio2210/light-CICD/src/go/internal/proto/executor"
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
	cmd.Stderr = os.Stderr
	cmd.Stdout = os.Stdout
	return cmd
}

type fakeWriter struct{}

func (f *fakeWriter) Write(path string, vlaue string) error {
	return nil
}

func TestRunDocker(t *testing.T) {
	execCommand = fakeExecCommand
	defer func() { execCommand = exec.Command }()
	input := &epb.Execution{
		Id:        proto.String("123"),
		ProjectId: proto.String("222"),
		ScmUrl:    proto.String("https://github.com/example"),
		EnvironmentVariable: []*epb.EnvironmentVariable{
			{
				Name:  proto.String("VAR"),
				Value: proto.String("value"),
			},
		},
		DockerCapability: []string{*proto.String("CAPABILITY")},
		DockerImage:      proto.String("fabrizio2210/docker_light-default_container"),
		ImageUseDocker:   proto.Bool(true),
		Manual:           proto.Bool(true),
	}
	runner := &Docker{}
	runner.projects_dir = "/opt/data/projects"
	runner.projects_volume_string = "temp_projects_dir:/opt/data"
	fs := &fakeWriter{}
	cmd, err := runner.Run(input, os.Stdout, fs)
	if err != nil {
		t.Errorf("Expected nil error, got %#v", err)
		t.FailNow()
	}
	err = cmd.Wait()
	if err != nil {
		t.Errorf("Expected nil error after execution, got %v", err)
	}
}

func TestHelperProcess(t *testing.T) {
	if os.Getenv("GO_WANT_HELPER_PROCESS") != "1" {
		return
	}

	// Checking arguments.
	want := []string{
		"docker",
		"run",
		"--env", "MANUAL_TRIGGER=1",
		"--env", "PROJECT_REPOSITORY=/opt/data/projects/222/repo",
		"--env", "REPOSITORY=/opt/data/projects/repo",
		"--env", "PROJECTS_VOLUME_STRING=temp_projects_dir:/opt/data",
		"--env", "VAR=value",
		"--pull", "always",
		"-v", "temp_projects_dir:/opt/data",
		"-v", "/var/run/docker.sock:/var/run/docker.sock",
		"--cap-add", "CAPABILITY",
		"fabrizio2210/docker_light-default_container",
		"bash", "-c",
		"'cd $(mktemp -d); git clone --recurse-submodules https://github.com/example ; cd * ; ./CICD.sh'",
	}
	diff := cmp.Diff(want, os.Args[3:])
	if diff != "" {
		fmt.Fprintf(os.Stderr, "Error, the arguments are different: %v", diff)
		os.Exit(2)
	}

	// some code to emulate output?
	// fmt.Fprintf(os.Stdout, dockerRunResult)

	os.Exit(0)
}

type fakeDocker struct {
	arg *epb.Execution
}

func (d *fakeDocker) ProjectDir(e *epb.Execution) string {
	return ""
}

func (d *fakeDocker) ProjectRepoDir(e *epb.Execution) string {
	return ""
}

func (d *fakeDocker) CentralRepoDir() string {
	return ""
}

func (d *fakeDocker) ExecDir(e *epb.Execution) string {
	return ""
}

func (d *fakeDocker) Output(e *epb.Execution) (io.Writer, error) {
	return os.Stdout, nil
}

func (d *fakeDocker) Run(e *epb.Execution, out io.Writer, fs Writer) (*exec.Cmd, error) {
	d.arg = e
	cmd := exec.Command("echo")
	cmd.Start()
	return cmd, nil
}

func TestWaitForJob(t *testing.T) {
	inputExecution := &epb.Execution{
		Id:        proto.String("123"),
		ProjectId: proto.String("222"),
		EnvironmentVariable: []*epb.EnvironmentVariable{
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
