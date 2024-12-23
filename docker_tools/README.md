These tools need to be placed inside the overleaf docker container. We do this automatically when this container goes up via the install.sh.

* auth_check_user.js
  
  Is used for checking a user and the password against the overleaf user database

* download_zip.js
  
  Downloads the data for a project id into a file
  
* export_project_list_of_user.js
  
  Given a userid the get a list of the project ids of the user

* get_user_list.js
  
  We get the list of the list of all users in the overleaf user database
  
* id_user.js
  
  We get the userid for a username (==email)

