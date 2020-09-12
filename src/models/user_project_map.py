from db import db


class UserProjectMap(db.Model):
  project_id = db.Field(_type = "integer")
  user_id = db.Field(_type = "integer")
  __tablename__ = "user_project_map"

  def __init__(self, project_id, user_id ):
    self.project_id = project_id
    self.user_id = user_id

  def save_to_db(self):
    self.save()

  def delete_from_db(self):
    self.delete()

  @classmethod
  def find_project_ids_by_user_id(cls, user_id):
    return cls.find(user_id=user_id)

  @classmethod
  def find_user_id_by_project_id(cls, project_id):
    return cls.find(project_id=project_id)
