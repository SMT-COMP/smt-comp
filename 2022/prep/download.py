#!env python3

import gitlab
import subprocess
import os

gl = gitlab.Gitlab('https://clc-gitlab.cs.uiowa.edu:2443')

def clone_group(name,dir):
    """clone the group named name in directory dir"""
    group = gl.groups.get(name)
    projects = group.projects.list(all=True)
    os.mkdir(dir)
    for project in projects:
        subprocess.run(["git", "clone", "--depth=1", project.http_url_to_repo], cwd=dir)


clone_group("SMT-LIB-benchmarks","non-incremental")
clone_group("SMT-LIB-benchmarks-inc","incremental")
