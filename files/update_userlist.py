import docker  # type: ignore
import json
from download_files import get_container
import pwd
import subprocess

container_name: str = "/sharelatex"
our_container: None | docker.models.containers.Container = get_container(container_name)

if our_container is None:
    exit(1)

result: tuple[int, str] = our_container.exec_run(
    (
        "/bin/bash -c '"
        "cd /overleaf/services/web && "
        "node modules/server-ce-scripts/scripts/get_user_list.js "
        "'"
    )
)

temp_json = "{}"
if result[1].endswith(b"} #-#-#\n") and (result[0] == 0):  # type: ignore
    temp_json = result[1].split(b"#-#-#")[-2].decode("ascii")  # type: ignore
json_list = json.loads(temp_json)

if not ("userlist" in json_list.keys()):
    exit(1)
user_json_list = json_list["userlist"]

user_list: list[str] = []
for element in user_json_list:
    if "email" in element.keys():
        user_list.append(element["email"])

for username in user_list:

    create_new_user: bool = False
    try:
        pwd.getpwnam(username)
        create_new_user = False
    except KeyError:
        create_new_user = True

    if create_new_user:
        subprocess.run([f"sh /update_user_jail.sh {username}"], shell=True)
