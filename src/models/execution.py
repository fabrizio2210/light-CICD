import subprocess
import logging
import random
import signal
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
  environments = None
  project_id = None
  project_dir_format = "{root_dir}/{prj}/{exc}"

  def __init__(self, project_id, id = None, environments = None, start_time = None, rc = None, stop_time = None, settings = None):
    if environments is None:
      environments = []
    if settings is None:
      settings = []
    self.id = id
    self.project_id = project_id
    self.start_time = start_time
    self.rc = rc
    self.stop_time = stop_time
    self.settings = settings
    self.environments = environments


  def readFromFS(self):
    pass

  def json(self):
    return { 'id': self.id, 
            'project_id': self.project_id, 
            'settings': self.settings, 
            'environments': self.environments, 
            'rc': self.rc, 
            'start_time': self.start_time, 
            'stop_time': self.stop_time}

  # Execute a run: creation of the environment, git clone, execution of CICD.sh(in container), make the output available
  def exec(self, manual = None):
    # Get information about the project
    scm_url = ProjectSettingMap.get_project_setting_by_name(self.project_id, "scm_url")
    if scm_url.value is None:
      logging.error("URL of the project not set")
      raise ValueError("URL of the project not set")

    image_use_docker = ProjectSettingMap.get_project_setting_by_name(self.project_id, "image_use_docker")

    # Get Main Settings
    docker_images = MainSettingModel.get_setting_by_name("name_default_container_image")
    if docker_images[0].value is None:
      logging.error("Docker image is Null")
      raise ValueError("Docker Image not set")
    docker_image = docker_images[0]

    projects_dirs = MainSettingModel.get_setting_by_name("projects_dir")
    if projects_dirs[0].value is None:
      logging.error("The path where the projects are store is Null")
      raise ValueError("Projects directory not set")
    projects_dir = projects_dirs[0]

    # Initialization of the Execution
    if self.id is not None:
      logging.error("The ID is already populated")
      raise ValueError("Not possible to rexecute the same execution")
    self.id = ExecutionModel.getUniqueID(self.project_id)
    self.start_time = datetime.now().timestamp()

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
    stdout_fh = open(self.project_dir_format.format(root_dir=projects_dir.value,
    prj=self.project_id,
    exc=self.id) + "/output" , "w")
    #TODO close in the end

    # Creation of the internal command
    d_command = quote("cd $(mktemp -d); git clone {} ; cd * ; ./CICD.sh".format(quote(scm_url.value)))
    command_array = ["docker", 
                      "run", 
                      *d_envs,
                      docker_images[0].value, 
                      "bash", 
                      "-c",
                      d_command]
    command = " ".join(command_array) + "; echo $? > " + self.project_dir_format.format(root_dir=projects_dir.value,
    prj=self.project_id,
    exc=self.id) + "/rc"
    logging.info("Command executed: {}".format(repr(command)))
    process = subprocess.Popen(command,
                      shell = True,
                      preexec_fn = preexec_function,
                      stdout = stdout_fh,
                      stderr = stdout_fh)
    with open(self.project_dir_format.format(root_dir=projects_dir.value,
    prj=self.project_id,
    exc=self.id) + "/pid", "w") as f:
      f.write(str(process.pid))

  @classmethod
  def find_executions_by_project_id(cls, project_id):
    return []

  @classmethod
  def find_by_id_and_project_id(cls, id, project_id):
    return None

  @classmethod
  def getUniqueID(cls, project_id):
    #TODO implement unique ID
    return random.randrange(100000)


