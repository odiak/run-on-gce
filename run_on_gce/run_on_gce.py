#!/usr/bin/env python3

import sys
import os

if len(sys.argv) <= 1 or sys.argv[1] != "--really":
    os.execvp(
        "poetry", ("poetry", "run", "python", sys.argv[0], "--really", *sys.argv[1:])
    )

from subprocess import CalledProcessError, check_call, check_output
from typing import Collection, Tuple
from time import sleep


def run_on_gce(
    project: str,
    instance: str,
    location: str,
    project_dir: str,
    filter_rules: Collection[str],
    args: Collection[str],
) -> None:
    gcloud_compute = ("gcloud", f"--project={project}", "compute")
    ssh_host = f"{instance}.{location}.{project}"

    python = "~/.pyenv/shims/python"
    pip = "~/.pyenv/shims/pip"
    poetry = "~/.pyenv/shims/poetry"

    check_call((*gcloud_compute, "instances", "start", instance))
    check_call((*gcloud_compute, "config-ssh"))

    # wait for boot
    for _ in range(5):
        try:
            check_output((*gcloud_compute, "ssh", instance, "--", "echo", "0"))
            break
        except CalledProcessError:
            sleep(4)

    check_call(
        (
            *gcloud_compute,
            "ssh",
            instance,
            "--",
            *(
                *("mkdir", "-p", project_dir),
                "&&",
                *("cd", project_dir),
                "&&",
                *(pip, "-q", "install", "-U", "poetry"),
                "&&",
                *("sudo", "apt", "install", "-yq", "rsync", ""),
            ),
        )
    )
    check_call(
        (
            "rsync",
            "-a",
            "--delete",
            "--prune-empty-dirs",
            *(f"--filter={f}" for f in filter_rules),
            "./",
            f"{ssh_host}:{project_dir}",
        )
    )
    check_call(
        (
            *gcloud_compute,
            "ssh",
            instance,
            "--",
            *(
                *("cd", project_dir),
                "&&",
                *(*("[", "-d", ".venv", "]"), "||", *(python, "-m", "venv", ".venv")),
                "&&",
                *(".venv/bin/pip", "-q", "install", "-U", "pip"),
                "&&",
                *(poetry, "install"),
                "&&",
                *args,
            ),
        )
    )

