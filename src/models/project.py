from db import db
from models.user_project_map import UserProjectMap


class ProjectModel(db.Model):
  id = db.Field(_type = "integer", primary_key =  True)
  name = db.Field(_type = "string")
  disabled = db.Field(_type = "string")
  __tablename__ = "projects"

  def __init__(self, id, name , disabled = None):
    if disabled == None:
      disabled = 0
    self.name = name
    self.disabled = disabled
    self.id = id

  def json(self):
    return {'name': self.name, 'id': self.id}

  def save_to_db(self):
    self.save()

  def delete_from_db(self):
    self.delete()

  @classmethod
  def get_projects_by_user_id(cls, user_id):
    res = []
    prj_ids = UserProjectMap.find_project_ids_by_user_id(user_id)
    for prj_id in prj_ids:
      res.append(cls.find_by_id(prj_id.project_id)[0])
    return res

  @classmethod
  def find_by_id(cls, id):
    return cls.find(id=id)

  @classmethod
  def find_by_name(cls, name):
    return cls.find(name=name)
