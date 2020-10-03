from db import db


class EnvironmentModel(db.Model):
  id = db.Field(_type = "integer", primary_key =  True)
  name = db.Field(_type = "string")
  description = db.Field(_type = "string")
  value = db.Field(_type = "string")
  __tablename__ = "environments"

  def __init__(self, id, name, value = None, description = None):
    self.name = name
    self.value = value
    self.description = description
    self.id = id

  def json(self):
    return {'name': self.name, 'id': self.id, 'description': self.description, 'value': self.value}

  def save_to_db(self):
    self.save()

  def delete_from_db(self):
    self.delete()

  @classmethod
  def find_by_id(cls, id):
    return cls.find(id=id)

  @classmethod
  def find_by_name(cls, name):
    return cls.find(name=name)
