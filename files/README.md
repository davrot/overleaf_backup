* auth_against_docker.py
  
  If given a username and password, the tool talks to the overleaf container and checks the credentials against the overleaf userdata base 

* build_jail.sh
  
  Collects the files for the sshd jail into the /master_jail directory.
    
* download_files.py
  
  Include file that organizes the retrivel of the files from the overleaf container given a username
  
* get_projects.py
  
  Given a username, it performs the update of the local project git folders under /downloads/[USERNAME].
   
* pam_sshd
  
  The pam settings for the sshd
  
* process_user_auth.sh
  
  Script that performs the user authentification for PAM
  
* sshd_config
  
  sshd config file

* update_user_jail.sh
  
  Prepares the individual user jails, derived from the /master_jail.
  
* update_userlist.py
  
  Updates the local user ensembale (i.e. creates missing users) based on the user list from the overleaf user database

* pre-rush.sh

  Is called by sshd and organizes the pre-git processes and the jail
  
* rush.rc

  Config file for the restricted user shell (rush)
  
* update_project_list.py

  Acquires the project list from the overleaf docker for a given user
