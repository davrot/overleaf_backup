import docker  # type: ignore
import json
import tarfile
import os


def get_container(container_name: str) -> None | docker.models.containers.Container:

    client = docker.from_env()

    # Find our overleaf container (name is defined in config.json)
    running_containers = client.containers.list()
    locate_containers = []
    for running_container in running_containers:
        if running_container.attrs["Name"] == container_name:
            locate_containers.append(running_container)

    if len(locate_containers) != 1:
        return None

    return locate_containers[0]


def _create_file(
    our_container: None | docker.models.containers.Container,
    username: str,
    project_id: str,
    path: str = "/var/lib/overleaf/",
) -> tuple[bool, str, str]:
    filename: str = username + "_" + project_id + ".zip"

    fullpath: str = path + filename
    if our_container is None:
        return False, "", ""

    result: tuple[int, str] = our_container.exec_run(
        (
            "/bin/bash -c '"
            "cd /overleaf/services/web && "
            "node modules/server-ce-scripts/scripts/download_zip.js "
            f"{project_id} "
            f"{fullpath} "
            "'"
        )
    )

    if result[1].endswith(b"\nDone.\n") and (result[0] == 0):  # type: ignore
        return True, filename, fullpath
    else:
        return False, "", ""


def _delete_file(
    our_container: None | docker.models.containers.Container,
    username: str,
    project_id: str,
    path: str = "/var/lib/overleaf/",
) -> None:
    filename: str = username + "_" + project_id + ".zip"

    fullpath: str = path + filename
    if our_container is None:
        return

    our_container.exec_run(("/bin/bash -c '" f"rm -f {fullpath} " "'"))


def process_file(
    our_container: None | docker.models.containers.Container,
    username: str,
    project_id: str,
    path: str = "/var/lib/overleaf/",
):

    if our_container is None:
        return

    status, filename, fullpath = _create_file(
        our_container=our_container, username=username, project_id=project_id, path=path
    )

    if status:
        with open(filename + ".tar", "wb") as file:
            bits, _ = our_container.get_archive(fullpath)

            for chunk in bits:
                file.write(chunk)

        _delete_file(
            our_container=our_container,
            username=username,
            project_id=project_id,
            path=path,
        )

        # Extract from tar
        with tarfile.open(filename + ".tar") as tar:
            member = tar.next()
            with tar.extractfile(member) as content, open(filename, "wb") as output_file:  # type: ignore
                for chunk in content:
                    output_file.write(chunk)

        # Clean up tar file
        os.remove(filename + ".tar")


def download_projectlist(
    our_container: None | docker.models.containers.Container,
    username: str,
    userid: str,
    path: str = "/var/lib/overleaf/",
) -> list[str]:

    if our_container is None:
        return []

    filename: str = username + "_project_list.json"

    fullpath: str = path + filename

    result: tuple[int, str] = our_container.exec_run(
        (
            "/bin/bash -c '"
            "cd /overleaf/services/web && "
            "node modules/server-ce-scripts/scripts/export_project_list_of_user.js "
            f"{userid} "
            f"{fullpath} "
            "'"
        )
    )

    status: bool = False
    if result[1].endswith(b"\nDone.\n") and (result[0] == 0):  # type: ignore
        status = True

    if status:
        with open(filename + ".tar", "wb") as file:
            bits, _ = our_container.get_archive(fullpath)

            for chunk in bits:
                file.write(chunk)

        our_container.exec_run(("/bin/bash -c '" f"rm -f {fullpath} " "'"))

        # Extract from tar
        with tarfile.open(filename + ".tar") as tar:
            member = tar.next()
            with tar.extractfile(member) as content, open(filename, "wb") as output_file:  # type: ignore
                for chunk in content:
                    output_file.write(chunk)

        # Clean up tar file
        os.remove(filename + ".tar")

        with open(filename, "r") as file:
            return_json = json.load(file)

        os.remove(filename)

        data_found = "projects" in return_json.keys()

        projects: list[str] = []
        if data_found:
            for project in return_json["projects"]:
                projects.append(project["_id"])

        return projects
    else:
        return []


def get_user_id(
    our_container: None | docker.models.containers.Container, username: str
) -> str:

    if our_container is None:
        return ""

    result: tuple[int, str] = our_container.exec_run(
        (
            "/bin/bash -c '"
            "cd /overleaf/services/web && "
            "node modules/server-ce-scripts/scripts/id_user.js "
            f"{username} "
            "'"
        )
    )

    if result[1].endswith(b"') #-#-#\n") and (result[0] == 0):  # type: ignore
        return result[1].split(b"#-#-#")[-2].split(b"'")[-2].decode("ascii")  # type: ignore
    else:
        return ""


def download_files(
    username: str,
    project_id: str,
    container_name: str = "/sharelatex",
    path: str = "/var/lib/overleaf/",
) -> list[str]:
    our_container: None | docker.models.containers.Container = get_container(
        container_name
    )

    if our_container is None:
        return []

    userid = get_user_id(our_container=our_container, username=username)

    if len(userid) == 0:
        return []

    project_list = download_projectlist(
        our_container=our_container, username=username, userid=userid, path=path
    )

    if project_id in project_list:
        process_file(
            our_container=our_container,
            username=username,
            project_id=project_id,
            path=path,
        )
    return project_list
