//import config from 'config';
import { authHeader } from "../helpers";
import { userService } from "./user.service";
var config = {};
config.apiUrl = window.location.origin;

export const executionoutputService = {
  get
};

function get(project_id, execution_id, f_byte, l_byte) {
  var url = new URL(
    `/api/v1/project/${project_id}/execution/${execution_id}/output`,
    config.apiUrl
  );
  const params = {
    first_requested_byte: f_byte,
    last_requested_byte: l_byte
  };
  const requestOptions = {
    method: "GET",
    headers: authHeader()
  };
  url.search = new URLSearchParams(params).toString();
  return fetch(url, requestOptions).then(handleResponse);
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
