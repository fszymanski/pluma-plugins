# SPDX-License-Identifier: GPL-3.0-or-later
# Copyright (c) 2021-2023 Filip Szymański <fszymanski.pl@gmail.com>

import subprocess


def do_shell(cmd, dirname):
    proc = subprocess.run(cmd,
                          stdout=subprocess.PIPE,
                          stderr=subprocess.DEVNULL,
                          shell=True,
                          cwd=dirname)
    return proc.stdout.decode("utf-8").strip()


def is_git_dir(dirname):
    try:
        subprocess.run("git rev-parse --is-inside-work-tree",
                       stdout=subprocess.DEVNULL,
                       stderr=subprocess.DEVNULL,
                       shell=True,
                       cwd=dirname,
                       check=True)

        return True
    except:
        return False


def get_current_git_branch(dirname):
    if (branch := do_shell("git branch --show-current", dirname)):
        return branch

    return do_shell("git rev-parse HEAD", dirname)
