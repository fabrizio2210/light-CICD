package main

import (
	"context"
	"fmt"
	"io"
	"log"
	"os"
	"os/exec"
	"time"

	epb "github.com/fabrizio2210/light-CICD/src/go/internal/proto/executor"
	"github.com/fabrizio2210/light-CICD/src/go/internal/rediswrapper"
	"google.golang.org/protobuf/encoding/prototext"
)

var execCommand = exec.Command

type Executor interface {
	Run(*epb.Execution, io.Writer, Writer) (*exec.Cmd, error)
	ProjectDir(*epb.Execution) string
	ProjectRepoDir(*epb.Execution) string
	CentralRepoDir() string
	ExecDir(*epb.Execution) string
	Output(*epb.Execution) (io.Writer, error)
}

type Docker struct {
	projects_dir           string
	projects_volume_string string
}

func (d *Docker) ProjectDir(e *epb.Execution) string {
	return fmt.Sprintf("%s/%s", d.projects_dir, e.GetProjectId())
}

func (d *Docker) ProjectRepoDir(e *epb.Execution) string {
	return fmt.Sprintf("%s/repo", d.ProjectDir(e))
}

func (d *Docker) CentralRepoDir() string {
	return fmt.Sprintf("%s/repo", d.projects_dir)
}

func (d *Docker) ExecDir(e *epb.Execution) string {
	return fmt.Sprintf("%s/%s", d.ProjectDir(e), e.GetId())
}

func (d *Docker) Output(e *epb.Execution) (io.Writer, error) {
	f, err := os.Create(d.ExecDir(e) + "/output")
	if err != nil {
		return nil, err
	}
	return f, nil
}

func (d *Docker) Run(e *epb.Execution, output io.Writer, file Writer) (*exec.Cmd, error) {
	command_array := []string{"run"}

	// Build the command line
	if e.GetManual() {
		command_array = append(command_array, "--env", "MANUAL_TRIGGER=1")
	}
	command_array = append(command_array, "--env", "PROJECT_REPOSITORY="+d.ProjectRepoDir(e))
	command_array = append(command_array, "--env", "REPOSITORY="+d.CentralRepoDir())
	command_array = append(command_array, "--env", "PROJECTS_VOLUME_STRING="+d.projects_volume_string)
	for _, v := range e.GetEnvironmentVariable() {
		command_array = append(command_array, "--env", v.GetName()+"="+v.GetValue())
	}
	command_array = append(command_array, "--pull", "always")
	if d.projects_volume_string != "" {
		command_array = append(command_array, "-v", d.projects_volume_string)
	}
	if e.GetImageUseDocker() {
		command_array = append(command_array, "-v", "/var/run/docker.sock:/var/run/docker.sock")
	}
	for _, c := range e.GetDockerCapability() {
		command_array = append(command_array, "--cap-add", c)
	}
	command_array = append(command_array, e.GetDockerImage())
	command_array = append(command_array,
		"bash", "-c",
		fmt.Sprintf("cd $(mktemp -d); git clone --recurse-submodules %s ; cd * ; ./CICD.sh", e.GetScmUrl()),
	)
	// End of build of the command line
	cmd := execCommand("docker", command_array...)
	log.Printf("Command about be executed: %v\n", cmd)
	err := file.Write(d.ExecDir(e)+"/start_time", fmt.Sprint(time.Now().Unix()))
	if err != nil {
		return nil, err
	}
	err = file.Write(d.ExecDir(e)+"/commandline", cmd.String())
	if err != nil {
		return nil, err
	}
	cmd.Stdout = output
	cmd.Stderr = output
	err = cmd.Start()
	file.Write(d.ExecDir(e)+"/hostname", os.Getenv("HOSTNAME"))
	file.Write(d.ExecDir(e)+"/parameters", e.String())
	return cmd, err
}

func WaitForJob(ctx context.Context, executor Executor, fs Writer) error {
	e, err := rediswrapper.WaitFor(ctx, "executions")
	if err != nil {
		log.Fatalf("Error: %v\n", err)
	}
	log.Printf("Execution: %v\n", e)
	execution := &epb.Execution{}
	err = prototext.Unmarshal([]byte(e), execution)
	if err != nil {
		return err
	}
	log.Printf("Execution: %v", execution.String())
	log.Printf("ProjectDir: %v", executor.ProjectDir(execution))
	err = fs.CreateDir(executor.ProjectDir(execution))
	if err != nil {
		return err
	}
	err = fs.CreateDir(executor.ExecDir(execution))
	if err != nil {
		return err
	}
	err = fs.CreateDir(executor.ProjectRepoDir(execution))
	if err != nil {
		return err
	}
	err = fs.CreateDir(executor.CentralRepoDir())
	if err != nil {
		return err
	}
	output, err := executor.Output(execution)
	if err != nil {
		return err
	}
	cmd, err := executor.Run(execution, output, fs)
	if err != nil {
		return err
	}
	go WaitForExecution(cmd, execution, executor, fs)
	return nil
}

type Writer interface {
	Write(string, string) error
	CreateDir(string) error
}

type Filesystem struct {
}

func (o Filesystem) Write(path string, content string) error {
	f, err := os.Create(path)
	if err != nil {
		return fmt.Errorf("impossible to create %s: %v", path, err)
	}
	defer f.Close()
	_, err = f.WriteString(content)
	if err != nil {
		return fmt.Errorf("impossible to write %s: %v", path, err)
	}
	return nil
}

func (o Filesystem) CreateDir(path string) error {
	return os.MkdirAll(path, 0o755)
}

func WaitForExecution(cmd *exec.Cmd, e *epb.Execution, executor Executor, file Writer) {
	err := file.Write(executor.ExecDir(e)+"/pid", fmt.Sprint(cmd.Process.Pid))
	if err != nil {
		log.Fatalln(err.Error())
	}
	if err := cmd.Wait(); err != nil {
		if exiterr, ok := err.(*exec.ExitError); ok {
			log.Printf("Exit Status: %d", exiterr.ExitCode())
			err := file.Write(executor.ExecDir(e)+"/rc", fmt.Sprint(exiterr.ExitCode()))
			if err != nil {
				log.Fatalln(err.Error())
			}
		} else {
			log.Fatalf("cmd.Wait for %v: %v", e, err)
		}
	}
	err = file.Write(executor.ExecDir(e)+"/stop_time", fmt.Sprint(time.Now().Unix()))
	if err != nil {
		log.Fatalln(err.Error())
	}
	// if no errors, it must be a return code == 0.
	log.Printf("Exit Status: %d", 0)
	err = file.Write(executor.ExecDir(e)+"/rc", fmt.Sprint(0))
	if err != nil {
		log.Fatalln(err.Error())
	}
}

func main() {
	log.Println("This is an executor")
	rediswrapper.RedisClient = rediswrapper.ConnectRedis("redis:6379")
	log.Printf("Redis client: %+v\n", rediswrapper.RedisClient)
	docker := &Docker{}
	docker.projects_dir = os.Getenv("PROJECTS_PATH")
	docker.projects_volume_string = os.Getenv("PROJECTS_VOLUME_STRING")
	ctx := context.Background()
	fs := &Filesystem{}
	for {
		err := WaitForJob(ctx, docker, fs)
		if err != nil {
			log.Fatalln(err.Error())
		}
	}
}
