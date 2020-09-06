from db import db

class UserModel(db.Model):
  id = db.Field(_type = "integer", primary_key =  True)
  username = db.Field(_type = "string")
  password = db.Field(_type = "string")
  admin = db.Field(_type = "integer")
  __tablename__ = "users"
  
  def __init__(self, id, username, password, admin):
    self.id = id
    self.username = username
    self.password = password
    self.admin = admin

  def save_to_db(self):
    self.save(self)

  @classmethod
  def get_all(cls):
    return cls.find()

  @classmethod
  def find_by_username(cls, username):
    return cls.find(username=username)

  @classmethod
  def find_by_id(cls, _id):
    return cls.find(id=_id)
