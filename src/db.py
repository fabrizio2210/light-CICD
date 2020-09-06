import sqlite3
import inspect

class db:
  db_file = "/tmp/data.db"

  @classmethod
  def create_tables(cls):
    pass
  
  class Field():
    def __init__(self, _type = None, primary_key = None):
      if primary_key == None:
          primary_key = False
      if _type == None:
        _type = "string"
      self.primary_key = primary_key
      if _type == "string":
        self._type = "text"
      if _type == "integer":
        _type = "INTEGER"
      self._type = _type

  class Model():
    def __init__(self):
      pass

    @classmethod
    def get_class_attrs(cls):
      attributes = inspect.getmembers(cls, lambda a:not(inspect.isroutine(a))) 
      return [a for a in attributes if not(a[0].startswith('__') and a[0].endswith('__'))]

    def get_attrs(self):
      attributes = inspect.getmembers(self, lambda a:not(inspect.isroutine(a))) 
      return [a for a in attributes if not(a[0].startswith('__') and a[0].endswith('__'))]

    def __repr__(self):
      ans = ""
      for attr in self.get_attrs():
        ans += '%s => "%s"\n' % (str(attr[0]), str(attr[1]))
      return ans

    @classmethod
    def create_table(cls):
      attrs = cls.get_class_attrs()
      attrs.sort()
      ph = "("
      for col in attrs:
        ph += "{name} {_type} ".format(name=col[0],_type=col[1]._type)
        if col[1].primary_key:
          ph += " PRIMARY KEY"
        ph += ","
      ph = ph.rstrip(',')
      ph += ")"
      create_table = "CREATE TABLE IF NOT EXISTS {table} {placeholder}".format(table=cls.__tablename__, placeholder=ph)
      print("====== Start Query ======")
      print(create_table) 
      print("======== End Query ======")
      connection = sqlite3.connect(db.db_file)
      cursor = connection.cursor()
      cursor.execute(create_table)
      connection.commit()
      connection.close()

    @classmethod
    def find(cls, **kwargs):
      list_args = []
      where_args = ""
      query = "SELECT * FROM {table} ".format(table=cls.__tablename__)
      query += "WHERE "
      for arg in kwargs:
        query += " %s=? AND " % arg
        list_args.append(kwargs[arg])
      query += "1 = 1"
      print("====== Start Query ======")
      print(query)
      print(list_args)
      print("======== End Query ======")
      connection = sqlite3.connect(db.db_file)
      cursor = connection.cursor()
      result = cursor.execute(query, (*list_args,))
      rows = result.fetchall()
      connection.close()
      attrs = cls.get_class_attrs()
      attrs.sort()
      res = []
      if len(rows)>0:
        for row in rows:
          # mapping correctly 
          res.append(cls(**dict(zip([a[0] for a in attrs],[*row]))))
      return res

    def save(self):
      attrs = self.get_attrs()
      attrs.sort()
      ph = "(" + ",".join(['?']*len(attrs)) + ")"
      row = (*[a[1] for a in attrs],)
      create_obj = "INSERT INTO {table} VALUES {placeholder}".format(table=self.__tablename__, placeholder=ph)
      print("====== Start Query ======")
      print(create_obj)
      print(row)
      connection = sqlite3.connect(db.db_file)
      cursor = connection.cursor()
      cursor.execute(create_obj, row)
      connection.commit()
      connection.close()

      # Update instance with new ID
      class_attrs = self.__class__.get_class_attrs()
      for col in class_attrs:
        if col[1].primary_key and col[1]._type == "INTEGER":
          setattr(self, col[0], cursor.lastrowid)
          self.id = cursor.lastrowid
          print("rowid: %d" % self.id)
      print("======== End Query ======")

    def delete(self):
      attrs = self.get_attrs()
      list_args = []
      where_args = ""
      query = "DELETE FROM {table} ".format(table=self.__tablename__)
      query += "WHERE "
      if len(attrs) == 0:
        print("Error: trying to drop table")
        return

      # Check if an ID exists
      use_id = False
      class_attrs = self.__class__.get_class_attrs()
      for col in class_attrs:
        if col[1].primary_key and col[1]._type == "INTEGER":
          list_args.append(getattr(self, col[0]))
          query += " %s=? " % col[0]
          use_id = True

      if not use_id:
        print(attrs)
        for arg in attrs:
          print(arg)
          query += " %s=? AND " % arg[0]
          list_args.append(arg[1])
        query += "1 = 1"

      print("====== Start Query ======")
      print(query)
      print(list_args)
      print("======== End Query ======")
      connection = sqlite3.connect(db.db_file)
      cursor = connection.cursor()
      cursor.execute(query, (*list_args,))
      connection.commit()
      connection.close()
