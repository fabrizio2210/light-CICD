import subprocess
import logging
import random
import signal
import json
from pathlib import Path
from datetime import datetime
from models.project_environment_map import ProjectEnvironmentMap
from models.project_setting_map import ProjectSettingMap
from models.main_setting import MainSettingModel
from models.environment import EnvironmentModel
from shlex import quote

def preexec_function():
  # Ignore sighup signal
  signal.signal(signal.SIGHUP, signal.SIG_IGN)

class ExecutionModel():
  id = None
  start_time = None
  rc = None
  stop_time = None
  settings = None
  commandline = None
  project_id = None
  project_dir_format = "{root_dir}/{prj}/{exc}"

  def __init__(self, project_id, id = None, commandline = None, start_time = None, rc = None, stop_time = None, settings = None):
    if settings is None:
      settings = {}
    self.id = id
    self.project_id = project_id
    self.start_time = start_time
    self.rc = rc
    self.stop_time = stop_time
    self.settings = settings
    self.commandline = commandline


  def readFromFS(self):
    pass

  def json(self):
    return { 'id': self.id, 
            'project_id': self.project_id, 
            'settings': list(map(lambda x: self.settings[x].json(), self.settings)), 
            'commandline': self.commandline, 
            'rc': self.rc, 
            'start_time': self.start_time, 
            'stop_time': self.stop_time}

  # Execute a run: creation of the environment, git clone, execution of CICD.sh(in container), make the output available
  def exec(self, manual = None):
    # Get Main Settings and Project Settings
    main_settings = MainSettingModel.get_all_settings()
    project_settings = ProjectSettingMap.get_settings_by_project_id(self.project_id)
    self.settings = { s.name: s for s in main_settings + project_settings }

    # Checking informations
    scm_url = self.settings.get("scm_url")
    if scm_url.value is None:
      logging.error("URL of the project not set")
      raise ValueError("URL of the project not set")

    image_use_docker = self.settings.get("image_use_docker")

    docker_image = self.settings.get("name_default_container_image", None)
    if docker_image.value is None:
      logging.error("Docker image is Null")
      raise ValueError("Docker Image not set")

    projects_dir = self.settings.get("projects_dir", None)
    if projects_dir.value is None:
      logging.error("The path where the projects are store is Null")
      raise ValueError("Projects directory not set")

    # Initialization of the Execution
    if self.id is not None:
      logging.error("The ID is already populated")
      raise ValueError("Not possible to rexecute the same execution")
    self.id = ExecutionModel.getUniqueID(self.project_id)
    self.start_time = int(datetime.now().timestamp())
    project_dir = self.project_dir_format.format(root_dir=projects_dir.value,
                  prj=self.project_id,
                  exc=self.id)

    # Creation of the environment
    envs = ProjectEnvironmentMap.get_environments_by_project_id(self.project_id)
    if manual:
      envs.append(EnvironmentModel(id=None, name="MANUAL_TRIGGER", value="1"))
    d_envs = []
    for env in envs:
      d_envs.append("--env")
      d_envs.append(quote("{}={}".format(env.name, env.value)))

    if image_use_docker.value:
      d_envs.append("-v")
      d_envs.append("/var/run/docker.sock:/var/run/docker.sock")

    # Creation of the directory structure
    Path(projects_dir.value + "/" + str(self.project_id) + "/" + str(self.id)).mkdir(parents=True, exist_ok=True)

    # Creation of the output file
    stdout_fh = open(project_dir + "/output" , "w")

    # Creation of the internal command
    d_command = quote("cd $(mktemp -d); git clone {} ; cd * ; ./CICD.sh".format(quote(scm_url.value)))
    command_array = ["docker", 
                      "run", 
                      *d_envs,
                      docker_image.value, 
                      "bash", 
                      "-c",
                      d_command]
    self.commandline = " ".join(command_array) + \
              "; echo $?  > " + project_dir + "/rc " + \
              "; date +%s > " + project_dir + "/stop_time"

    # Storing the execution information
    with open(project_dir + "/start_time", "w") as f:
      f.write(str(self.start_time))
    with open(project_dir + "/settings", "w") as f:
      json.dump(list(map(lambda x: self.settings[x].json(), self.settings)), f, indent = 6)
    with open(project_dir + "/commandline", "w") as f:
      f.write(str(self.commandline))

    # Execution
    logging.info("Command executed: {}".format(repr(self.commandline)))
    process = subprocess.Popen(self.commandline,
                      shell = True,
                      preexec_fn = preexec_function,
                      stdout = stdout_fh,
                      stderr = stdout_fh)

    # Saving the PID
    with open(project_dir + "/pid", "w") as f:
      f.write(str(process.pid))

  @classmethod
  def find_executions_by_project_id(cls, project_id):
    return []

  @classmethod
  def find_by_id_and_project_id(cls, id, project_id):
    executions = []
    project_dir = self.project_dir_format.format(root_dir=projects_dir.value,
                  prj=self.project_id,
                  exc=self.id)
    if Path(project_dir).is_dir():
      execution = ExecutionModel(project_id = project_id, 
              id = id,
              rc = int(cls.readAttribute("rc")),
              start_time = int(cls.readAttribute("start_time")),
              stop_time = int(cls.readAttribute("stop_time")),
              settings = json.loads(cls.readAttribute("settings")),
              commandline = json.loads(cls.readAttribute("commandline"))
        )
      executions.append(execution)
    return executions

  @classmethod
  def readAttribute(project_dir, attr):
      if Path(project_dir + "/" + attr).is_file():
        with open(project_dir + "/" + attr, "r"):
          return f.read().rstrip()
      return None
    
  @classmethod
  def getUniqueID(cls, project_id):
    #TODO implement unique ID
    return random.randrange(100000)


