import subprocess
import logging
import random
from models.project_environment_map import ProjectEnvironmentMap
from models.project_setting_map import ProjectSettingMap
from models.main_setting import MainSettingModel
from models.environment import EnvironmentModel


class ExecutionModel():
  id = None
  stderr_url = None
  stdout_url = None
  start_time = None
  rc = None
  stop_time = None
  settings = None
  project_id = None

  def __init__(self, project_id, id = None, stderr_url = None, stdout_url = None, start_time = None, rc = None, stop_time = None, settings = None):
    if id is None:
      id = ExecutionModel.getUniqueID()
    self.id = id
    self.project_id = project_id
    self.stderr_url = stderr_url
    self.stdout_url = stdout_url
    self.start_time = start_time
    self.rc = rc
    self.stop_time = stop_time
    self.settings = settings

  def json(self):
    return {'stderr_url': self.stderr_url,
            'stdout_url': self.stdout_url, 
            'id': self.id, 
            'project_id': self.project_id, 
            'settings': self.settings, 
            'rc': self.rc, 
            'start_time': self.start_time, 
            'stop_time': self.stop_time}

  # Execute a run: creation of the environment, git clone, execution of CICD.sh(in container), make the output available
  def exec(self):
    # Get information about the project
    scm_url = ProjectSettingMap.get_project_setting_by_name(self.project_id, "scm_url")
    if scm_url.value is None:
      logging.warning("URL of the project not set")
      return "URL of the project not set"
    docker_images = MainSettingModel.get_setting_by_name("name_default_container")

    # Creation of the environment
    envs = ProjectEnvironmentMap.get_environments_by_project_id(self.project_id)
    envs.append(EnvironmentModel(id=None, name="MANUAL_TRIGGER", value="1"))
    d_envs = []
    for env in envs:
      d_envs.append("--env")
      d_envs.append("{}={}".format(env.name, env.value))

    # Creation of the output file
    stdout_fh = open("stdout.out", "w")
    stderr_fh = open("stderr.out", "w")
    #TODO close in the end

    # Creation of the internal command
    d_command = "cd $(mktemp -d); git clone {} ; cd * ; ./CICD.sh".format(scm_url.value)
    command = ["docker", 
                      "run", 
                      *d_envs,
                      docker_images[0].value, 
                      "bash", 
                      "-c",
                      d_command]
    logging.info("Command executed: {}".format(repr(command)))
    subprocess.Popen(command,
                      stdout = stdout_fh,
                      stderr = stderr_fh)

  @classmethod
  def find_executions_by_project_id(cls, project_id):
    return None

  @classmethod
  def find_by_id_and_project_id(cls, id, project_id):
    return None

  @classmethod
  def getUniqueID(cls):
    #TODO implement unique ID
    return random.randrange(100000)

