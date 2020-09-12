from db import db


class ProjectEnvironmentMap(db.Model):
  project_id = db.Field(_type = "integer")
  environment_id = db.Field(_type = "integer")
  __tablename__ = "project_environment_map"

  def __init__(self, project_id, environment_id ):
    self.project_id = project_id
    self.environment_id = environment_id

  def save_to_db(self):
    self.save()

  def delete_from_db(self):
    self.delete()

  @classmethod
  def find_environment_ids_by_project_id(cls, project_id):
    return cls.find(project_id=project_id)

  @classmethod
  def find_project_id_by_environment_id(cls, environment_id):
    return cls.find(environment_id=environment_id)
