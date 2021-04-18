import subprocess
import os
import logging
import random
import signal
import json
import shutil
from pathlib import Path, PurePath
from datetime import datetime
from models.project_environment_map import ProjectEnvironmentMap
from models.project_setting_map import ProjectSettingMap
from models.main_setting import MainSettingModel
from models.environment import EnvironmentModel
from models.setting import SettingModel
from shlex import quote

def preexec_function():
  # Protect the the external execution from SIGHUP
  signal.signal(signal.SIGHUP, signal.SIG_IGN)

class ExecutionOutputModel():
  def __init__(self, first_transmitted_byte = None, last_transmitted_byte = None, file_bytes = None, data = None):
    self.first_transmitted_byte = first_transmitted_byte
    self.last_transmitted_byte = last_transmitted_byte
    self.file_bytes = file_bytes
    self.data = data

  def json(self):
    return {'first_transmitted_byte': self.first_transmitted_byte,
            'last_transmitted_byte': self.last_transmitted_byte,
            'file_bytes': self.file_bytes, 
            'data': self.data
           }

class ExecutionModel():
  id = None
  start_time = None
  rc = None
  stop_time = None
  settings = None
  commandline = None
  project_id = None
  project_dir_format = "{root_dir}/{prj}"
  project_repo_dir_format = "{root_dir}/{prj}/repo"
  central_repo_dir_format = "{root_dir}/repo"
  exec_dir_format    = "{root_dir}/{prj}/{exc:0>20}"

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
    exec_dir = self.exec_dir_format.format(root_dir=projects_dir.value,
                  prj=self.project_id,
                  exc=self.id)
    project_repo_dir = self.project_repo_dir_format.format(root_dir=projects_dir.value,
                  prj=self.project_id)
    central_repo_dir = self.central_repo_dir_format.format(root_dir=projects_dir.value)

    # Creation of the environment
    envs = ProjectEnvironmentMap.get_environments_by_project_id(self.project_id)
    if manual:
      envs.append(EnvironmentModel(id=None, name="MANUAL_TRIGGER", value="1"))
    envs.append(EnvironmentModel(id=None, name="PROJECT_REPOSITORY", value=project_repo_dir))
    envs.append(EnvironmentModel(id=None, name="REPOSITORY", value=central_repo_dir))
    d_envs = []
    for env in envs:
      d_envs.append("--env")
      d_envs.append(quote("{}={}".format(env.name, env.value)))

    if image_use_docker.value:
      d_envs.append("-v")
      d_envs.append("/var/run/docker.sock:/var/run/docker.sock")

    # Creation of the directory structure
    Path(exec_dir).mkdir(parents=True, exist_ok=True)
    Path(project_repo_dir).mkdir(parents=True, exist_ok=True)
    Path(central_repo_dir).mkdir(parents=True, exist_ok=True)

    # Creation of the output file
    stdout_fh = open(exec_dir + "/output" , "w")

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
              "; echo $?  > " + exec_dir + "/rc " + \
              "; date +%s > " + exec_dir + "/stop_time"

    # Storing the execution information
    with open(exec_dir + "/start_time", "w") as f:
      f.write(str(self.start_time))
    with open(exec_dir + "/settings", "w") as f:
      json.dump({ self.settings[s].name: 
                  self.settings[s].json() for s in self.settings }, f, indent = 6)
    with open(exec_dir + "/commandline", "w") as f:
      f.write(str(self.commandline))

    # Execution
    logging.info("Command executed: {}".format(repr(self.commandline)))
    process = subprocess.Popen(self.commandline,
                      shell = True,
                      preexec_fn = preexec_function,
                      stdout = stdout_fh,
                      stderr = stdout_fh)

    # Saving the PID
    with open(exec_dir + "/pid", "w") as f:
      f.write(str(process.pid))

  @classmethod
  def find_executions_by_project_id(cls, project_id):
    #TODO implement a limit of executions
    executions = []
    projects_dirs = MainSettingModel.get_setting_by_name("projects_dir")
    project_dir = Path(cls.project_dir_format.format(root_dir=projects_dirs[0].value,
                  prj=project_id))
    if project_dir.is_dir():
      for item in project_dir.iterdir():
        if item.is_dir():
          potential_executions = cls.find_by_id_and_project_id(PurePath(item).name, project_id)
          if potential_executions:
            executions.append(potential_executions[0])
      
    return executions

  @classmethod
  def find_by_id_and_project_id(cls, id, project_id):
    executions = []
    projects_dirs = MainSettingModel.get_setting_by_name("projects_dir")
    exec_dir = cls.exec_dir_format.format(root_dir=projects_dirs[0].value,
                  prj=project_id,
                  exc=id)
    if Path(exec_dir).is_dir():
      try:
        rc = int(cls.readAttribute(exec_dir, "rc"))
      except:
        rc = None
      start_time = int(cls.readAttribute(exec_dir, "start_time"))
      try:
        stop_time = int(cls.readAttribute(exec_dir, "stop_time"))
      except:
        stop_time = None
      j_settings = json.loads(cls.readAttribute(exec_dir, "settings"))
      settings = {}
      for s in j_settings:
        settings[s] = SettingModel(**j_settings[s])
        
      commandline = cls.readAttribute(exec_dir, "commandline")
      execution = ExecutionModel(project_id = project_id, 
              id = id,
              rc = rc,
              start_time = start_time,
              stop_time = stop_time,
              settings = settings,
              commandline = commandline)
      executions.append(execution)
    return executions
  
  @classmethod
  def delete_by_id_and_project_id(cls, id, project_id):
    projects_dirs = MainSettingModel.get_setting_by_name("projects_dir")
    exec_dir = cls.exec_dir_format.format(root_dir=projects_dirs[0].value,
                  prj=project_id,
                  exc=id)
    if Path(exec_dir).is_dir():
      try:
        shutil.rmtree(Path(exec_dir))
      except:
        logging.error("Impossible to delete {}".format(exec_dir))
        raise ValueError("Impossible to delete {}".format(exec_dir))
      return True
    return False

  @classmethod
  def readAttribute(cls, exec_dir, attr):
      if Path(exec_dir + "/" + attr).is_file():
        with open(exec_dir + "/" + attr, "r") as f:
          return f.read().rstrip()
      return None
    
  @classmethod
  def get_output(cls, id, project_id, first_byte, last_byte):
    projects_dirs = MainSettingModel.get_setting_by_name("projects_dir")
    exec_dir = cls.exec_dir_format.format(root_dir=projects_dirs[0].value,
                  prj=project_id,
                  exc=id)
    file_to_read = exec_dir + "/output"
    file_to_read_path = Path(file_to_read)
    if file_to_read_path.is_file():
      size = file_to_read_path.stat().st_size
      if last_byte == -1:
        last_byte = size
      with open(file_to_read, "r") as f:
        buffer_len = last_byte - first_byte
        first_byte = f.seek(first_byte)
        data = f.read(buffer_len)
        return ExecutionOutputModel(first_byte, first_byte + buffer_len, size, data)
    return None

  @classmethod
  def cleanup(cls):
    projects_dirs = MainSettingModel.get_setting_by_name("projects_dir")
    if Path(projects_dirs[0].value).is_dir():
      shutil.rmtree(projects_dirs[0].value)

  @classmethod
  def getUniqueID(cls, project_id):
    #TODO do a more robust approach
    return int("{}{:0>6}".format(int(datetime.now().timestamp()), random.randrange(100000)))


