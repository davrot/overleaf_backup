If the user logs in via git (in the moment on port 993, please don't forget to allow port 993 via ufw allow 993), the projects for that user are automatically updated.

Every 5 minutes, cron checks the userdata base of overleaf and new user from the database are created. 

## Get the ssh keys for a user

```
git clone ssh://[USERNAME]@[FQDN]:[PORT]/sshkey.git
```

e.g.

```
git clone ssh://davrot@uni-bremen.de@psintern.neuro.uni-bremen.de:993/sshkey.git
```
## Get the project list for a user

```
git clone ssh://[USERNAME]@[FQDN]:[PORT]/projects.git
```

e.g.

```
git clone ssh://davrot@uni-bremen.de@psintern.neuro.uni-bremen.de:993/projects.git
```

## Get a project

```
git clone ssh://[USERNAME]@[FQDN]:[PORT]/[PROJECT_ID].git
```

e.g.


```
git clone ssh://davrot@uni-bremen.de@psintern.neuro.uni-bremen.de:993/6759fdf66ca7b8bc5b81b184.git
```

On the one side this backup container communicates with the user via git and with the overleaf server via docker socket. 

# Port 993

If you don't like port 993 you can change the compose.yaml
```    
    ports:
      - 993:22
```
accordingly. But don't forget you firewall:

```    
ufw allow 993
```

## Change the name of the overleaf server container: 

Default is "/sharelatex"

If your installation is different then change in the files download_files.py, auth_against_docker.py and update_userlist.py as well install.sh in the other directory modifiy the line accordingly:

```
container_name: str = "/sharelatex",
```

# Files

* Dockerfile
  
  Dockerfile for creating the container image 

* compose.yaml
  
  Compose file to start the container 

* crontab_host.txt
  
  This needs to be placed into the crontab of the host
  
* down.sh
  
  For stoping the container
  
* exec.sh
  
  For entering the container for an interactive session

* init.sh
  
  Init script that is ran during starting the container. The make_image.sh places it into the container. 
  
* logs.sh
  
  Shows the logs of the running container
  
* make_image.sh
  
  Needs to be run for generating the container image
  
* run_update_userlist.sh
  
  Is run by the cron to update the user basis in the container based on the overleaf user database

* up.sh
  
  Starts the container 
