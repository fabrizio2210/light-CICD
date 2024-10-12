# Roadmap

- Substitute sqlite with MariaDB o MongoDB
- Introduce Redis and workers which will run the execution
 - workers written in Golang, Redis will have a queue and a proto between python and Go will be used
- Introduce API for the script in the container to fan out the load
- Use sidecar executable to upload output (stdout, stderr) to Redis

# Requirements

- Multiple projects
- Output via web
- Secure connection with GitHub
- Triggered by GitHub or manual
- Fast
- Store artifacts
- Able to run on multiple nodes (etcd)

# To deploy

- Put in a container
- Persistant data
- Test a full cycle in development environment

# Decisions

- The environment variables are not shared between projects
  every project has its own set of variables
  - To change this, use a normal MariaDB 
