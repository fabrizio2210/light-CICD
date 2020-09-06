from db import db
from models.project_environment_map import ProjectEnvironmentMap


class SettingModel(db.Model):
  id = db.Field(_type = "integer", primary_key =  True)
  name = db.Field(_type = "string")
  description = db.Field(_type = "string")
  value = db.Field(_type = "string")
  __tablename__ = "settings"

  def __init__(self, id, name, value = None, description = None):
    if description == None:
      description ="" 
    self.name = name
    self.description = description
    self.id = id

  def json(self):
    return {'name': self.name, 'id': self.id, 'description': self.description, 'value': self.value}

  def save_to_db(self):
    self.save()

  def delete_from_db(self):
    self.delete()

  @classmethod
  def get_environments_by_project_id(cls, project_id):
    res = []
    env_ids = ProjectEnvironmentMap.find_environment_ids_by_project_id(project_id)
    for env_id in env_ids:
      res.append(cls.find_by_id(env_id.setting_id)[0])
    return res

  @classmethod
  def find_by_id(cls, id):
    return cls.find(id=id)

  @classmethod
  def find_by_name(cls, name):
    return cls.find(name=name)
