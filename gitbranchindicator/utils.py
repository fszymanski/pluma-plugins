# Copyright (C) 2021 Filip Szymański <fszymanski.pl@gmail.com>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program. If not, see <https://www.gnu.org/licenses/>.
#

__all__ = ['get_current_git_branch', 'is_git_dir']

import subprocess


def do_shell(cmd, path):
    proc = subprocess.run(cmd,
                          stdout=subprocess.PIPE,
                          stderr=subprocess.DEVNULL,
                          shell=True,
                          cwd=path)
    return proc.stdout.decode('utf-8').strip()


def is_git_dir(path):
    try:
        subprocess.run('git rev-parse --is-inside-work-tree',
                       stdout=subprocess.DEVNULL,
                       stderr=subprocess.DEVNULL,
                       shell=True,
                       cwd=path,
                       check=True)

        return True
    except:
        return False


def get_current_git_branch(path):
    branch = do_shell('git branch --show-current', path)
    if branch:
        return branch

    return do_shell('git symbolic-ref --short HEAD', path)

# vim: ft=python3 ts=4 et
