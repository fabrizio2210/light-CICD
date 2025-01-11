import subprocess
import os
import logging
import random
import signal
import json
import psutil
import shutil
from pathlib import Path, PurePath
from datetime import datetime
from models.project_environment_map import ProjectEnvironmentMap
from models.project_setting_map import ProjectSettingMap
from models.main_setting import MainSettingModel
from models.setting import SettingModel
from models.redis import RedisModel
from go.internal.proto.executor import executor_pb2
from google.protobuf import text_format
from shlex import quote

def is_exec_equal(a: executor_pb2.Execution, b: executor_pb2.Execution)-> bool:
  a.id = "0"
  b.id = "0"
  if text_format.MessageToString(a) != text_format.MessageToString(b):
    return False
  return True

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
  projects_dir = None
  projects_volume_string = None
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
  def exec(self, manual = None, supplement_envs = None):
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
    docker_image = self.settings.get("name_container_image")
    docker_capabilities = self.settings.get("docker_capabilities")
    parallel_execs_per_project_host = self.settings.get("parallel_execs_per_project_host", None)

    if not docker_image.value:
      default_docker_image = self.settings.get("name_default_container_image", None)
      if default_docker_image.value is None:
        logging.error("Docker image is Null")
        raise ValueError("Docker Image not set")
      docker_image.value = default_docker_image.value

    # Cleaning old executions
    ExecutionModel.keepLastExecutions(self.project_id)

    # Initialization of the Execution
    if self.id is not None:
      logging.error("The ID is already populated: %s" % self.id)
      raise ValueError("Not possible to rexecute the same execution")
    self.id = ExecutionModel.getUniqueID(self.project_id)
    logging.info(self.id)

    e = executor_pb2.Execution()
    e.id = f"{self.id:0>20}"
    e.project_id = str(self.project_id)
    e.scm_url = scm_url.value
    e.image_use_docker = image_use_docker.value
    e.docker_image = docker_image.value
    for env in ProjectEnvironmentMap.get_environments_by_project_id(self.project_id):
      v = executor_pb2.EnvironmentVariable()
      v.name = env.name
      v.value = env.value
      e.environment_variable.append(v)
    if supplement_envs:
      for env in supplement_envs:
        v = executor_pb2.EnvironmentVariable()
        v.name = env.name
        v.value = env.value
        e.environment_variable.append(v)
    for capability in docker_capabilities.value.split(","):
      if capability != "":
        e.docker_capability.append(capability)
    e.manual = manual == True

    # Deduplicate executions in the queue.
    already_present = False
    in_queue = ExecutionModel.find_protos_in_queue_by_project_id(self.project_id)
    for w in in_queue:
      if is_exec_equal(w, e):
        already_present = True

    if already_present:
      logging.info("A similar execution is already in queue, dropping.")
      raise RuntimeError("A similar execution is already in queue, dropping.")
    RedisModel.enque("executions", text_format.MessageToString(e))

  @classmethod
  def find_executions_by_project_id(cls, project_id):
    #TODO implement a limit of executions
    executions = []
    project_dir = Path(cls.project_dir_format.format(root_dir=cls.projects_dir,
                  prj=project_id))
    if project_dir.is_dir():
      for item in project_dir.iterdir():
        if item.is_dir():
          try:
            exec_id = int(PurePath(item).name)
          except:
            # The directory is not a number, so it cannot be an execution id.
            logging.info("'%s' is not a directory which contains an execution." % PurePath(item).name)
            continue
          potential_executions = cls.find_by_id_and_project_id(exec_id, project_id)
          if potential_executions:
            executions.append(potential_executions[0])
    executions.extend(cls.find_executions_in_queue_by_project_id(project_id))
    return executions

  @classmethod
  def find_executions_in_queue_by_project_id(cls, project_id):
    executions = []
    for msg in RedisModel.peek_queue("executions"):
      e = text_format.Parse(msg, executor_pb2.Execution())
      if e.project_id != str(project_id):
        continue
      execution = ExecutionModel(project_id = project_id, 
                                 id = e.id)
      executions.append(execution)
    return executions
  
  @classmethod
  def find_protos_in_queue_by_project_id(cls, project_id):
    protos = []
    for msg in RedisModel.peek_queue("executions"):
      e = text_format.Parse(msg, executor_pb2.Execution())
      if e.project_id != str(project_id):
        continue
      protos.append(e)
    return protos

  @classmethod
  def find_by_id_and_project_id(cls, id, project_id):
    executions = []
    exec_dir = cls.exec_dir_format.format(root_dir=cls.projects_dir,
                  prj=project_id,
                  exc=id)
    if Path(exec_dir).is_dir():
      try:
        rc = int(cls.readAttribute(exec_dir, "rc"))
      except:
        rc = None
      try:
        start_time = int(cls.readAttribute(exec_dir, "start_time"))
      except:
        start_time = None
      try:
        stop_time = int(cls.readAttribute(exec_dir, "stop_time"))
      except:
        stop_time = None
      try:
        j_settings = json.loads(cls.readAttribute(exec_dir, "settings"))
      except:
        j_settings = []
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
    for e in cls.find_executions_in_queue_by_project_id(project_id):
      if e.id == f"{id:0>20}":
        executions.append(e)
    return executions
  
  @classmethod
  def delete_by_id_and_project_id(cls, id, project_id):
    exec_dir = cls.exec_dir_format.format(root_dir=cls.projects_dir,
                  prj=project_id,
                  exc=id)
    logging.info("rm -rf %s", exec_dir)
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
    exec_dir = cls.exec_dir_format.format(root_dir=cls.projects_dir,
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
    if Path(cls.projects_dir).is_dir():
      shutil.rmtree(cls.projects_dir)

  @classmethod
  def keepLastExecutions(cls, project_id):
    executions = cls.find_executions_by_project_id(project_id)
    real_executions = [i for i in executions if i.start_time is not None]
    real_executions.sort(key=lambda e: e.start_time, reverse=True)

    number_of_executions_to_keep = ProjectSettingMap.get_project_setting_by_name(project_id,
                                                                                 "number_of_executions_to_keep")
    if number_of_executions_to_keep is None:
      number_of_executions_to_keep = MainSettingModel.get_setting_by_name("number_of_executions_to_keep")

    if number_of_executions_to_keep:
      for e in real_executions[number_of_executions_to_keep[0].value-1:]:
        logging.info("Deleting %d execution of %d.", e.id, project_id)
        cls.delete_by_id_and_project_id(e.id, project_id)

  @classmethod
  def set_projects_dir(cls, projects_dir):
    cls.projects_dir = projects_dir

  @classmethod
  def set_projects_volume_string(cls, projects_volume_string):
    cls.projects_volume_string = projects_volume_string

  @classmethod
  def getUniqueID(cls, project_id):
    #TODO do a more robust approach
    return int("{}{:0>6}".format(int(datetime.now().timestamp()), random.randrange(100000)))



