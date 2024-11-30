#!/bin/bash

function docker-compose {
  docker compose $@
}

# Supposing to deploy on x86_64 architecture
docker build -t fabrizio2210/light_cicd-backend -f docker/x86_64/Dockerfile-backend --build-arg DOCKERARCH=x86_64 .
docker build -t fabrizio2210/light_cicd-frontend -f docker/x86_64/Dockerfile-frontend .
docker build -t fabrizio2210/light_cicd-executor -f docker/x86_64/Dockerfile-executor .
docker-compose -f docker/lib/stack.yml  up
