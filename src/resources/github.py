
import json
import logging
from flask_restful import Resource, reqparse
from models.execution import ExecutionModel
from models.project import ProjectModel
from models.project_setting_map import ProjectSettingMap
from models.setting import SettingModel


class GithubReceiver(Resource):
  parser = reqparse.RequestParser()
  parser.add_argument('repository',
                      type=dict,
                      required=True)
  parser.add_argument('hook',
                      type=dict,
                      required=True)
  parser.add_argument('X-Hub-Signature',
                      location='headers')


  def post(self):
    data = GithubReceiver.parser.parse_args()
    hook = data['hook']
    repository = data['repository']
    logging.info('Github webhook for: %s', repository['clone_url'])
    
    if not 'push' in hook.get('events', []):
      return {'message': 'Not handling events different than "push"'}, 400

    settings = SettingModel.find_by_name('scm_url')
    for setting in settings:
      if setting.value == repository['clone_url']:
        project_ids = ProjectSettingMap.find_project_id_by_setting_id(setting.id)
        if not project_ids:
          return {'message': 'Setting is not associate to any project'}, 500
        execution = ExecutionModel(project_id=project_ids[0].project_id)
        try:
          execution.exec()
        except Exception as e:
          logging.error(repr(e))
          return {"message": "An error occurred running the item."}, 500
        return { 'execution': execution.json()}, 201
    return {'message': 'Repository URL not found.'}, 404
        


