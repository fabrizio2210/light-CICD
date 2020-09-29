import unittest
import logging
import json
import sys
from os import path
sys.path.append( path.dirname( path.dirname( path.abspath(__file__) ) ) )
import app
from utils.data import bootstrap

admin_user = "fabrizio"
admin_password = "pwd"

normal_user = "fabrizio2"
normal_password = "pwd2"

second_user = "fabrizio3"
second_password = "pwd2"

def initialize_test():
  bootstrap()
#########
# General without authentication

class TestAPI_without_auth(unittest.TestCase):

  def setUp(self):
    app.app.testing = True
    self.app = app.app.test_client()
    initialize_test()

  def test_010_root(self):
    rv = self.app.get('/')
    self.assertEqual(rv.status, '404 NOT FOUND')

  def test_020_get_token(self):
    logins = [ {"cred": { "username": admin_user, "password": admin_password}, "res": "200 OK"},
               { "cred": { "username": normal_user, "password": normal_password}, "res": "200 OK"},
               { "cred": { "username": "not_exist_s345ffsdg", "password": "not_exist"}, "res": "401 UNAUTHORIZED"},
               { "cred": { "username": admin_user, "password": "not_exist"}, "res": "401 UNAUTHORIZED"} ]
    for login in logins:
      rv = self.app.post('/auth', json = login['cred'])
      self.assertEqual(rv.status, login['res'])


##############
# Main Setting

class TestAPI_MainSettingAsAdmin(unittest.TestCase):

  def setUp(self):
    app.app.testing = True
    self.app = app.app.test_client()
    initialize_test()
    rv = self.app.post('/auth', json = { "username": admin_user, "password": admin_password})
    self.headers = {'Content-Type': 'application/json', 'Authorization': "JWT " + json.loads(rv.data.decode("utf-8"))['access_token']}

  def test_020_get_settings(self):
    rv = self.app.get('/api/v1/settings', headers = self.headers)
    self.assertEqual(rv.status, '200 OK')

  def test_021_get_setting(self):
    rv = self.app.get('/api/v1/setting/max_project_run_number', headers = self.headers)
    self.assertEqual(rv.status, '200 OK')
    self.assertEqual(json.loads(rv.data.decode("utf-8")), {"id": 1,
      "name": "max_project_run_number",
      "description": "Number of executions per project that are stored",
      "value": None,
      "default_value": 20})

  def test_027_put_setting(self):
    rv = self.app.put('/api/v1/setting/max_project_run_number', json = {"value": 10}, headers = self.headers)
    self.assertEqual(rv.status, '200 OK')
    rv = self.app.get('/api/v1/setting/max_project_run_number', headers = self.headers)
    self.assertEqual(rv.status, '200 OK')
    self.assertEqual(json.loads(rv.data.decode("utf-8")), {"id": 1,
      "name": "max_project_run_number",
      "description": "Number of executions per project that are stored",
      "value": 10,
      "default_value": 20})


class TestAPI_MainSettingasUser(unittest.TestCase):

  def setUp(self):
    app.app.testing = True
    self.app = app.app.test_client()
    initialize_test()
    rv = self.app.post('/auth', json = { "username": normal_user, "password": normal_password})
    self.headers = {'Content-Type': 'application/json', 'Authorization': "JWT " + json.loads(rv.data.decode("utf-8"))['access_token']}

  def test_020_get_settings(self):
    rv = self.app.get('/api/v1/settings', headers = self.headers)
    self.assertEqual(rv.status, '200 OK')

  def test_021_get_setting(self):
    rv = self.app.get('/api/v1/setting/max_project_run_number', headers = self.headers)
    self.assertEqual(rv.status, '200 OK')
    self.assertEqual(json.loads(rv.data.decode("utf-8")), {"id": 1,
      "name": "max_project_run_number",
      "description": "Number of executions per project that are stored",
      "value": None,
      "default_value": 20})

  def test_025_put_setting_forbidden(self):
    rv = self.app.put('/api/v1/setting/max_project_run_number', json = {"value": 1}, headers = self.headers)
    self.assertEqual(rv.status, '403 FORBIDDEN')
    rv = self.app.get('/api/v1/setting/max_project_run_number', headers = self.headers)
    self.assertEqual(rv.status, '200 OK')
    self.assertEqual(json.loads(rv.data.decode("utf-8")), {"id": 1,
      "name": "max_project_run_number",
      "description": "Number of executions per project that are stored",
      "value": None,
      "default_value": 20})


##############################
# Project and Project Settings

class TestAPI_ProjectAsUser(unittest.TestCase):

  def setUp(self):
    self.verificationErrors = []
    app.app.testing = True
    self.app = app.app.test_client()
    initialize_test()
    rv = self.app.post('/auth', json = { "username": normal_user, "password": normal_password})
    self.headers = {'Content-Type': 'application/json', 'Authorization': "JWT " + json.loads(rv.data.decode("utf-8"))['access_token']}

  def tearDown(self):
    self.assertEqual([], self.verificationErrors)

      # GET  /api/v1/project/1
      # GET  /api/v1/projects
      # POST /api/v1/new_project
  def test_030_project(self):
    prj_name = "my_prj_name"
    prj_name2 = "my_prj_name2"
    # Try to get project
    rv = self.app.get("/api/v1/project/1", headers = self.headers)
    try: self.assertEqual(rv.status, '404 NOT FOUND')
    except AssertionError as e: self.verificationErrors.append(str(e) + "Line: " + str(sys.exc_info()[2].tb_lineno)) 
    # Create project
    rv = self.app.post("/api/v1/new_project/{}".format(prj_name), json = {}, headers = self.headers)
    try: self.assertEqual(rv.status, '201 CREATED')
    except AssertionError as e: self.verificationErrors.append(str(e) + "Line: " + str(sys.exc_info()[2].tb_lineno)) 
    try: self.assertEqual(json.loads(rv.data.decode("utf-8")), { "name": prj_name, "id": 1})
    except AssertionError as e: self.verificationErrors.append(str(e) + "Line: " + str(sys.exc_info()[2].tb_lineno)) 
    # Get project
    rv = self.app.get("/api/v1/project/1", json = {}, headers = self.headers)
    try: self.assertEqual(rv.status, '200 OK')
    except AssertionError as e: self.verificationErrors.append(str(e) + "Line: " + str(sys.exc_info()[2].tb_lineno)) 
    try: self.assertEqual(json.loads(rv.data.decode("utf-8")), { "name": prj_name, "id": 1 })
    except AssertionError as e: self.verificationErrors.append(str(e) + "Line: " + str(sys.exc_info()[2].tb_lineno)) 
    # Create second project as second user
    rv = self.app.post('/auth', json = { "username": second_user, "password": second_password})
    self.headers = {'Content-Type': 'application/json', 'Authorization': "JWT " + json.loads(rv.data.decode("utf-8"))['access_token']}
    rv = self.app.post("/api/v1/new_project/{}".format(prj_name2), json = {}, headers = self.headers)
    try: self.assertEqual(rv.status, '201 CREATED')
    except AssertionError as e: self.verificationErrors.append(str(e) + "Line: " + str(sys.exc_info()[2].tb_lineno)) 
    try: self.assertEqual(json.loads(rv.data.decode("utf-8")), { "name": prj_name2, "id": 2})
    except AssertionError as e: self.verificationErrors.append(str(e) + "Line: " + str(sys.exc_info()[2].tb_lineno)) 
    # Get all project of the second user
    rv = self.app.get("/api/v1/projects", json = {}, headers = self.headers)
    try: self.assertEqual(rv.status, '200 OK')
    except AssertionError as e: self.verificationErrors.append(str(e) + "Line: " + str(sys.exc_info()[2].tb_lineno)) 
    try: self.assertEqual(json.loads(rv.data.decode("utf-8")), { "projects": [ { "name": prj_name2, "id": 2 } ] })
    except AssertionError as e: self.verificationErrors.append(str(e) + "Line: " + str(sys.exc_info()[2].tb_lineno)) 

      # GET/PUT /api/v1/project/1/setting/scm_url
  def test_050_get_setting_project(self):
    prj_name = "my_prj_name"
    prj_name2 = "my_prj_name2"
    value = "http://github.com/fdfdsfsd/dfsddf.git"
    value2 = "http://github.com/fdfd/dff.git"
    # Try to get setting of a non-existant project
    rv = self.app.get('/api/v1/project/1/setting/scm_url', headers = self.headers)
    try: self.assertEqual(rv.status, '404 NOT FOUND')
    except AssertionError as e: self.verificationErrors.append(str(e) + "Line: " + str(sys.exc_info()[2].tb_lineno)) 
    # Create first project
    rv = self.app.post("/api/v1/new_project/{}".format(prj_name), json = {}, headers = self.headers)
    try: self.assertEqual(rv.status, '201 CREATED')
    except AssertionError as e: self.verificationErrors.append(str(e) + "Line: " + str(sys.exc_info()[2].tb_lineno)) 
    try: self.assertEqual(json.loads(rv.data.decode("utf-8")), { "name": prj_name, "id": 1})
    except AssertionError as e: self.verificationErrors.append(str(e)) 
    # Get setting of first project
    rv = self.app.get('/api/v1/project/1/setting/scm_url', headers = self.headers)
    try: self.assertEqual(rv.status, '200 OK')
    except AssertionError as e: self.verificationErrors.append(str(e) + "Line: " + str(sys.exc_info()[2].tb_lineno)) 
    try: self.assertEqual(json.loads(rv.data.decode("utf-8")), { "name": "scm_url", 
      "id": None, 
      "description": "Source Control Manager URL of the project",
      "value": None,
      "default_value": None })
    except AssertionError as e: self.verificationErrors.append(str(e) + "Line: " + str(sys.exc_info()[2].tb_lineno)) 
    # Put setting of first project
    payload = { "value": value }
    rv = self.app.put('/api/v1/project/1/setting/scm_url', json = payload, headers = self.headers)
    try: self.assertEqual(rv.status, '200 OK')
    except AssertionError as e: self.verificationErrors.append(str(e) + "Line: " + str(sys.exc_info()[2].tb_lineno)) 
    try: self.assertEqual(json.loads(rv.data.decode("utf-8")), { "name": "scm_url", 
      "id": 4, 
      "description": "Source Control Manager URL of the project",
      "value": value,
      "default_value": None })
    except AssertionError as e: self.verificationErrors.append(str(e) + "Line: " + str(sys.exc_info()[2].tb_lineno)) 
    # Create second project as second user
    rv = self.app.post('/auth', json = { "username": second_user, "password": second_password})
    self.headers = {'Content-Type': 'application/json', 'Authorization': "JWT " + json.loads(rv.data.decode("utf-8"))['access_token']}
    rv = self.app.post("/api/v1/new_project/{}".format(prj_name2), json = {}, headers = self.headers)
    try: self.assertEqual(rv.status, '201 CREATED')
    except AssertionError as e: self.verificationErrors.append(str(e) + "Line: " + str(sys.exc_info()[2].tb_lineno)) 
    try: self.assertEqual(json.loads(rv.data.decode("utf-8")), { "name": prj_name2, "id": 2})
    except AssertionError as e: self.verificationErrors.append(str(e) + "Line: " + str(sys.exc_info()[2].tb_lineno)) 
    # Try to get setting of the first as second user
    rv = self.app.get('/api/v1/project/1/setting/scm_url', headers = self.headers)
    try: self.assertEqual(rv.status, '403 FORBIDDEN')
    except AssertionError as e: self.verificationErrors.append(str(e) + "Line: " + str(sys.exc_info()[2].tb_lineno)) 
    # Try to modify as second user
    rv = self.app.post('/auth', json = { "username": second_user, "password": second_password})
    self.headers = {'Content-Type': 'application/json', 'Authorization': "JWT " + json.loads(rv.data.decode("utf-8"))['access_token']}
    payload = { "value": value2 }
    rv = self.app.put('/api/v1/project/1/setting/scm_url', json = payload, headers = self.headers)
    try: self.assertEqual(rv.status, '403 FORBIDDEN')
    except AssertionError as e: self.verificationErrors.append(str(e) + "Line: " + str(sys.exc_info()[2].tb_lineno)) 
    # Put non existantsetting of second project as second user
    payload = { "value": value }
    rv = self.app.put('/api/v1/project/2/setting/non_existent_setting_Dfdsfs', json = payload, headers = self.headers)
    try: self.assertEqual(rv.status, '404 NOT FOUND')
    except AssertionError as e: self.verificationErrors.append(str(e) + "Line: " + str(sys.exc_info()[2].tb_lineno)) 
    # Try to get setting of the second as second user
    rv = self.app.get('/api/v1/project/2/setting/non_existent_setting_Dfdsfs', headers = self.headers)
    try: self.assertEqual(rv.status, '404 NOT FOUND')
    except AssertionError as e: self.verificationErrors.append(str(e) + "Line: " + str(sys.exc_info()[2].tb_lineno)) 

      # PUT /api/v1/project/1/setting/scm_url
  def test_035_put_project_setting(self):
    prj_name = "my_prj_name"
    value = "http://github.com/fdfdsfsd/dfsddf.git"
    value2 = "http://github.com/fdfd/dff.git"
    # Create project
    rv = self.app.post("/api/v1/new_project/{}".format(prj_name), json = {}, headers = self.headers)
    try: self.assertEqual(rv.status, '201 CREATED')
    except AssertionError as e: self.verificationErrors.append(str(e) + "Line: " + str(sys.exc_info()[2].tb_lineno)) 
    try: self.assertEqual(json.loads(rv.data.decode("utf-8")), { "name": prj_name, "id": 1})
    except AssertionError as e: self.verificationErrors.append(str(e) + "Line: " + str(sys.exc_info()[2].tb_lineno)) 
    # Put setting
    payload = { "value": value }
    rv = self.app.put('/api/v1/project/1/setting/scm_url', json = payload, headers = self.headers)
    try: self.assertEqual(rv.status, '200 OK')
    except AssertionError as e: self.verificationErrors.append(str(e) + "Line: " + str(sys.exc_info()[2].tb_lineno)) 
    try: self.assertEqual(json.loads(rv.data.decode("utf-8")), { "name": "scm_url", 
      "id": 4, 
      "description": "Source Control Manager URL of the project",
      "value": value,
      "default_value": None })
    except AssertionError as e: self.verificationErrors.append(str(e) + "Line: " + str(sys.exc_info()[2].tb_lineno)) 
    # Try to modify as second user
    rv = self.app.post('/auth', json = { "username": second_user, "password": second_password})
    self.headers = {'Content-Type': 'application/json', 'Authorization': "JWT " + json.loads(rv.data.decode("utf-8"))['access_token']}
    payload = { "value": value2 }
    rv = self.app.put('/api/v1/project/1/setting/scm_url', json = payload, headers = self.headers)
    try: self.assertEqual(rv.status, '403 FORBIDDEN')
    except AssertionError as e: self.verificationErrors.append(str(e) + "Line: " + str(sys.exc_info()[2].tb_lineno)) 
    # Get setting as first user
    rv = self.app.post('/auth', json = { "username": normal_user, "password": normal_password})
    self.headers = {'Content-Type': 'application/json', 'Authorization': "JWT " + json.loads(rv.data.decode("utf-8"))['access_token']}
    rv = self.app.get('/api/v1/project/1/setting/scm_url', headers = self.headers)
    try: self.assertEqual(rv.status, '200 OK')
    except AssertionError as e: self.verificationErrors.append(str(e) + "Line: " + str(sys.exc_info()[2].tb_lineno)) 
    try: self.assertEqual(json.loads(rv.data.decode("utf-8")), { "name": "scm_url", 
      "id": 4, 
      "description": "Source Control Manager URL of the project",
      "value": value,
      "default_value": None })
    except AssertionError as e: self.verificationErrors.append(str(e) + "Line: " + str(sys.exc_info()[2].tb_lineno)) 

#    def test_get_device(self):
#        name = "televisore"
#        body = televisore
#        rv = self.app.get('/device/{}'.format(name))
#        self.assertEqual(rv.status, '200 OK')
#        self.maxDiff = None
#        dict_received = json.loads(rv.data.decode("utf-8"))
#        self.assertEqual(dict_received['device']['name'], name)
#        pairs = zip(dict_received['device']['keys'],body['keys'])
#        same = any(x != y for x, y in pairs)
#        self.assertEqual(same, True)
#
#    def test_get_remote_control(self):
#        name = 'piano5'
#        rv = self.app.get('/remote_control')
#        self.assertEqual(rv.status, '200 OK')
#        dict_received = json.loads(rv.data.decode("utf-8"))
#        devices = ('televisore', 'stereo', 'proiettore')
#        notfound = {}
#        for device in devices:
#          notfound[device] = True
#        for x in dict_received['devices']:
#          for device in devices:
#            if x['name'] == device:
#              notfound[device] = False
#        self.assertEqual(any(notfound.values()), False)
#
#    def test_get_inexistent_item(self):
#        name = 'piano6'
#        rv = self.app.get('/item/{}'.format(name))
#        self.assertEqual(rv.status, '404 NOT FOUND')

if __name__ == '__main__':
  logging.basicConfig(level=logging.CRITICAL)
  unittest.main()
