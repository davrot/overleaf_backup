import argh  # type: ignore
import shutil
import os
import subprocess
import glob
from download_files import download_files


def clean(username: str, project_list: list[str]):

    keep_dirs: list[str] = [
        "bin",
        "dev",
        "etc",
        "lib",
        "lib64",
        "usr",
        "sshkey.git",
        ".ssh",
        "projects.git",
    ]

    keep_list = []
    for project_id in project_list:
        keep_list.append(
            os.path.join("/downloads/", f"{username}", project_id + ".git")
        )

    for keep_dir in keep_dirs:
        keep_list.append(os.path.join("/downloads/", f"{username}", keep_dir))

    for entry in glob.glob(os.path.join("/downloads/", f"{username}", "*")):
        if os.path.isdir(entry):
            if not (entry in keep_list):
                try:
                    shutil.rmtree(entry)
                except OSError as e:
                    print(f"Error deleting directory: {e}")


def main(username: str, project_id: str) -> None:

    if len(username) == 0:
        return

    if len(project_id) == 0:
        return

    project_list = download_files(username=username, project_id=project_id)
    clean(username=username, project_list=project_list)

    path: str = f"/downloads/{username}/{project_id}.git"
    filename: str = f"{username}_{project_id}.zip"

    os.makedirs(f"{path}", mode=0o700, exist_ok=True)

    shutil.move(
        f"{filename}",
        f"{path}/{filename}",
    )

    subprocess.run(
        [
            f"/usr/bin/unzip -qq -o {filename} "
        ],
        shell=True, cwd=path
    )

    subprocess.run(
        [f"rm -f {path}/{filename}"], shell=True
    )

    subprocess.run(
        [f"chmod -R 0755 {path} "],
        shell=True,
    )

    if not os.path.isdir(f"{path}/.git"):

        subprocess.run(
            [f"/usr/bin/git init -q "],
            shell=True, cwd=path
        )

    subprocess.run(
        [f"/usr/bin/git add --all "],
        shell=True, cwd=path
    )


    subprocess.run(
        [
            f"/usr/bin/git commit -q -m 'by ShareLatex' "
        ],
        shell=True, cwd=path
    )


    return


if __name__ == "__main__":
    argh.dispatch_command(main)
