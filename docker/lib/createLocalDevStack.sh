#!/bin/bash -eu

function docker-compose {
  docker compose $@
}

# Supposing to deploy on x86_64 architecture
docker build -t fabrizio2210/light_cicd-backend-dev -f docker/x86_64/Dockerfile-backend-dev .
docker build -t fabrizio2210/light_cicd-frontend-dev -f docker/x86_64/Dockerfile-frontend-dev .
docker build -t fabrizio2210/light_cicd-executor-dev -f docker/x86_64/Dockerfile-executor-dev .
docker-compose --project-name "light_cicd_dev" -f docker/lib/stack-dev.yml  up
