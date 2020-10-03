# API

## Frontend API

### /web/login

Login web page, it is necessary to retrieve a security token 

### /web/settings 

Page where manipulate the overall settings

### /web/projects 

Page of all projects

### /web/projects/<id_project>/ 

Page of the project identified by id_project

### /web/projects/<id_project>/settings 

Page where change the settings of the id_project project



## Backend API

## Main Setting

### /api/v1/settings/ (secured)

List of all settings

### /api/v1/setting/<name_setting> GET/PUT (secured)

Get or update id_setting general setting


## Project

### /api/v1/projects/ (secured)

List of all projects for the current user

### /api/v1/new_project/<name> POST (secured)

Create new project

### /api/v1/project/<id_project>/ GET (secured)

All details of the project identified by id_project


## Project Settings

### /api/v1/project/<id_project>/settings GET (secured)

Retrieve all the settings of the id_project project

### /api/v1/project/<id_project>/setting/<name_setting> GET/PUT (secured)

Retrieve and set a setting of the id_project project


## Environment 

### /api/v1/project/<id_project>/environments GET (secured)

Get all environments of the id_project project

### /api/v1/project/<id_project>/new_environment POST (secured)

Create a new environment the id_project project

### /api/v1/project/environment/<id_environment> GET/PUT/DELETE (secured)

Retrieve and update the id_environment environment of a project


## Executions

### /api/v1/project/<id_project>/executions GET (secured)

All the builds of the id_project project

### /api/v1/project/<id_project>/execution/<id_execution> GET (secured)

All the details of the id_execution execution

### /api/v1/project/<id_project>/execution/<id_execution>/out/stdout|stderr GET (secured)

Get the stderr or stdout of the id_execution execution

### /api/v1/project/<id_project>/new_execution POST (secured)

Trigger a build of the project id_project


## External Integration

### /api/v1/external/github_trigger POST

It accepts a POST from GITHUB in order to trigger a build
