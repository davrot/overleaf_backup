import argh  # type: ignore
import docker  # type: ignore
from download_files import get_container
import os
import json
import tarfile
import subprocess


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


def download_projectlist(
    our_container: None | docker.models.containers.Container,
    username: str,
    path: str = "/var/lib/overleaf/",
):

    if our_container is None:
        return

    if username is None:
        return

    if len(username) == 0:
        return

    userid: str = get_user_id(our_container=our_container, username=username)

    if userid is None:
        return

    if len(userid) == 0:
        return

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

        if data_found:
            os.makedirs(
                f"/downloads/{username}/projects.git", mode=0o700, exist_ok=True
            )

            with open(
                os.path.join(
                    "/downloads/", f"{username}", "projects.git", "projects.txt"
                ),
                "w",
            ) as file:
                for entry in return_json["projects"]:
                    file.write(f'{entry["_id"]} ; "{entry["name"]}"\n')

            if not os.path.isdir("/downloads/{username}/projects.git/.git"):

                subprocess.run(
                    [f"cd /downloads/{username}/projects.git && /usr/bin/git init -q "],
                    shell=True,
                )

            subprocess.run(
                [f"cd /downloads/{username}/projects.git && /usr/bin/git add --all "],
                shell=True,
            )
            subprocess.run(
                [
                    f"cd /downloads/{username}/projects.git && /usr/bin/git commit -q -m 'by ShareLatex' "
                ],
                shell=True,
            )

            subprocess.run(
                [f"chmod -R 0700 /downloads/{username}/projects.git "],
                shell=True,
            )

        return
    else:
        return


def main(
    username: str,
    container_name: str = "/overleafserver",
    path: str = "/var/lib/overleaf/",
):

    if username is None:
        exit(1)

    if len(username) == 0:
        exit(1)

    our_container: None | docker.models.containers.Container = get_container(
        container_name
    )

    if our_container is None:
        exit(1)

    download_projectlist(
        our_container=our_container,
        username=username,
        path=path,
    )


if __name__ == "__main__":
    argh.dispatch_command(main)
