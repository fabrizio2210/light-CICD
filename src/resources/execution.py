import logging
from flask_restful import Resource, reqparse
from flask_jwt import jwt_required, current_identity
from models.execution import ExecutionModel
from models.project import ProjectModel


class Execution(Resource):

  @jwt_required()
  def get(self, project_id, id):
    if len(ProjectModel.find_by_id(project_id)) == 0:
      return {'message': 'Project not found'}, 404
    executions = ExecutionModel.find_by_id_and_project_id(id, project_id)
    if executions:
      return executions[0].json()
    return {'message': 'Execution not found'}, 404

  @jwt_required()
  def delete(self, id):
    project = ProjectModel.find_by_id(id)
    if project:
      project.delete_from_db()
      return {'message': 'Item deleted.'}
    return {'message': 'Item not found.'}, 404


class ExecutionList(Resource):

  @jwt_required()
  def get(self, project_id):
    if len(ProjectModel.find_by_id(project_id)) == 0:
      return {'message': 'Project not found'}, 404
    return {'executions': 
            list(map(lambda x: x.json(), 
                   ExecutionModel.find_executions_by_project_id(project_id)))}


class NewExecution(Resource):

  @jwt_required()
  def post(self, project_id):
    if not ProjectModel.find_by_id(project_id):
      return {'message': 
              "A project with id '{}' does not exist.".format(project_id)}, 404

    # Create a new execution
    execution = ExecutionModel(project_id=project_id)
    try:
      execution.exec()
    except Exception as e:
      logging.error(repr(e))
      return {"message": "An error occurred running the item."}, 500

    return execution.json(), 201
