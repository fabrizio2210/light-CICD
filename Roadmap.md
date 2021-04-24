# Roadmap

- Insert login
- Use sqlite as a backend DB
- Substitute sqlite with something that can serve several distributed nodes

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
