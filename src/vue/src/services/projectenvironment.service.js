//import config from 'config';
import { authHeader } from "../helpers";
import { userService } from "./user.service";
var config = {};
config.apiUrl = "";

export const projectenvironmentService = {
  create,
  update,
  getAll
};

function getAll(project_id) {
  const requestOptions = {
    method: "GET",
    headers: authHeader()
  };

  return fetch(`${config.apiUrl}/api/v1/project/${project_id}/environments`, requestOptions).then(
    handleResponse
  );
}

function update(envid, envname, envvalue, envdescription) {
  const requestOptions = {
    method: "PUT",
    headers: authHeader(),
    body: JSON.stringify({ 
      'value': envvalue,
      'name': envname,
      'description': envdescription })
  };

  return fetch(`${config.apiUrl}/api/v1/project/environment/${envid}`, requestOptions).then(
    handleResponse
  );
}

function create(project_id, newenvname) {
  const requestOptions = {
    method: "POST",
    headers: authHeader(),
    body: JSON.stringify({ 'name': newenvname })
  };

  return fetch(`${config.apiUrl}/api/v1/project/${project_id}/new_environment`, requestOptions).then(
    handleResponse
  );
}

function handleResponse(response) {
  return response.text().then(text => {
    const data = text && JSON.parse(text);
    if (!response.ok) {
      if (response.status === 401) {
        // auto logout if 401 response returned from api
        userService.logout();
        location.reload(true);
      }

      const error = (data && data.message) || response.statusText;
      return Promise.reject(error);
    }

    return data;
  });
}
