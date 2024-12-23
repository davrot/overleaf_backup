import docker  # type: ignore
from download_files import get_container
import argh  # type: ignore


def main(username: str, password: str, container_name: str = "/sharelatex"):

    if username is None:
        exit(1)

    if password is None:
        exit(1)

    if len(username) == 0:
        exit(1)

    if len(password) == 0:
        exit(1)

    our_container: None | docker.models.containers.Container = get_container(
        container_name
    )

    if our_container is None:
        exit(1)

    result: tuple[int, str] = our_container.exec_run(
        (
            "/bin/bash -c '"
            "cd /overleaf/services/web && "
            "node modules/server-ce-scripts/scripts/auth_check_user.js "
            f"{username} "
            f"{password} "
            "'"
        )
    )

    if result[0] == 0:
        exit(0)
    else:
        exit(1)


if __name__ == "__main__":
    argh.dispatch_command(main)
