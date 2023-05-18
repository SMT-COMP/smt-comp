#!env python3

import gitlab
import subprocess
import os,sys

gl = gitlab.Gitlab('https://clc-gitlab.cs.uiowa.edu:2443')

def clone_group(name,dir):
    """clone the group named name in directory dir"""
    group = gl.groups.get(name)
    projects = group.projects.list(all=True)
    os.makedirs(dir,exist_ok=True)
    deprecated = [f for f in os.listdir(dir) if not os.path.isfile(os.path.join(dir, f))]
    n=0
    for project in projects:
        n=n+1
        print(project.name,str(n)+"/"+str(len(projects)))
        if project.name in deprecated: deprecated.remove(project.name)
        if project.name in ["QF_BV_legacy","Sage2_legacy"]:
            print(project.name,"skipped")
            continue
        oldpath=os.path.join(dir,project.path)
        path=os.path.join(dir,project.name)
        if os.path.exists(path):
            subprocess.run(["git", "-C", path, "fetch", "--depth=1"])
            subprocess.run(["git", "-C", path, "reset", "--hard", "origin/"+project.default_branch])
        else:
            subprocess.run(["git", "clone", "--depth=1", project.http_url_to_repo, path])
    #remove deprecated projects
    for project_name in deprecated:
            subprocess.run(["rm", "-rf", os.path.join(dir,project_name)])

def run():
    if len(sys.argv)<2:
        print("download.py <DIR>")
        exit(1)

    dst=sys.argv[1]
    clone_group("SMT-LIB-benchmarks",os.path.join(dst,"non-incremental"))
    clone_group("SMT-LIB-benchmarks-inc",os.path.join(dst,"incremental"))

if __name__ == '__main__':
    run()
