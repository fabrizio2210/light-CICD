import os
from models.user import UserModel
from models.setting import SettingModel
from models.environment import EnvironmentModel
from models.main_setting import MainSettingModel
from models.init_project_setting import InitProjectSettingModel
from models.project import ProjectModel

from models.user_project_map import UserProjectMap
from models.project_environment_map import ProjectEnvironmentMap
from models.project_setting_map import ProjectSettingMap


def bootstrap():
  if os.path.isfile("/tmp/data.db"):
    os.unlink("/tmp/data.db")

  UserModel.create_table()
  UserProjectMap.create_table()
  ProjectModel.create_table()
  EnvironmentModel.create_table()
  SettingModel.create_table()
  MainSettingModel.create_table()
  InitProjectSettingModel.create_table()
  UserProjectMap.create_table()
  ProjectEnvironmentMap.create_table()
  ProjectSettingMap.create_table()

#######
# Users
  new_user = UserModel(id=None, username="fabrizio", password="pwd", admin=1)
  new_user.save()
  new_user = UserModel(id=None, username="fabrizio2", password="pwd2", admin=0)
  new_user.save()
  new_user = UserModel(id=None, username="fabrizio4", password="pwd2", admin=0)
  new_user.save()
  new_user.username = "fabrizio3"
  new_user.save()

  print(UserModel.find_by_username("jose"))
  print(UserModel.find_by_id(1))
  print(UserModel.find_by_username("fabrizio"))
  print(UserModel.get_all())

##########
# Settings

# Main Settings
  new_setting = SettingModel(id=None, 
                             name="max_project_run_number", 
                             description = "Number of executions per project that are stored",
                             default_value = 20)
  new_setting.save()
  new_main_setting = MainSettingModel("max_project_run_number", new_setting.id)
  new_main_setting.save()

  new_setting = SettingModel(id=None, 
                             name="name_default_container", 
                             description = "Default container to use",
                             default_value = "fabrizio2210/controller")
  new_setting.save()
  new_main_setting = MainSettingModel("name_default_container", new_setting.id)
  new_main_setting.save()

# Initial Project Settings
  new_setting = SettingModel(id=None, 
                             name="scm_url", 
                             description = "Source Control Manager URL of the project")
  new_setting.save()
  new_main_setting = InitProjectSettingModel(new_setting.name, new_setting.id)
  new_main_setting.save()

##############
# Environments

