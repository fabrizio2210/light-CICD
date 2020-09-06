# API

## Frontend API

### /web/login

Login web page, it is necessary to retrieve a security token 

### /web/settings (secured)

Page where manipulate the overall settings

### /web/projects (secured)

Page of all projects

### /web/projects/<id_project>/ (secured)

Page of the project identified by id_project

### /web/projects/<id_project>/settings (secured)

Page where change the settings of the id_project project



## Backend API


### /api/v1/settings/ (secured)

List of all settings

### /api/v1/settings/<name_setting> GET/PUT (secured)

Get or update name_setting general setting

### /api/v1/projects/ (secured)

List of all projects for the current user

### /api/v1/new_project/<name> POST (secured)

Create new project

### /api/v1/project/<id_project>/ GET (secured)

All details of the project identified by id_project

### /api/v1/project/<id_project>/settings/<id_setting> GET/POST (secured)

Retrieve and set a setting of the id_project project

### /api/v1/project/<id_project>/environments GET (secured)

Get all environments of the id_project project

### /api/v1/project/<id_project>/new_environment POST (secured)

Create a new environment the id_project project

### /api/v1/project/<id_project>/environment/<id_environment> GET/PUT/DELETE (secured)

Retrieve and update an setting of the id_project project

### /api/v1/project/<id_project>/executions (secured)

All the builds of the id_project project

### /api/v1/project/<id_project>/build POST (secured)

Trigger a build of the project id_project
