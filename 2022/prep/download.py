#!env python3

import gitlab
import subprocess
import os

gl = gitlab.Gitlab('https://clc-gitlab.cs.uiowa.edu:2443')

def clone_group(name,dir):
    """clone the group named name in directory dir"""
    group = gl.groups.get(name)
    projects = group.projects.list(all=True)
    os.makedirs(dir,exist_ok=True)
    n=0
    for project in projects:
        n=n+1
        print(project.name,str(n)+"/"+str(len(projects)))
        if project.name in ["QF_BV_legacy","Sage2_legacy"]:
            print(project.name,"skipped")
            continue
        oldpath=os.path.join(dir,project.path)
        path=os.path.join(dir,project.name)
        if oldpath != path and os.path.exists(oldpath):
            print("rename",oldpath,"to",path)
            os.rename(oldpath,path)
        if os.path.exists(path):
            subprocess.run(["git", "-C", path, "pull", "--depth=1"])
        else:
            subprocess.run(["git", "clone", "--depth=1", project.http_url_to_repo, path])


clone_group("SMT-LIB-benchmarks","non-incremental")
clone_group("SMT-LIB-benchmarks-inc","incremental")
