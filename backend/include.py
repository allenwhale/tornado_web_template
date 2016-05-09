import fnmatch
import importlib
import inspect
import os
import re

class T:
    pass

def include(cls, dir="./", ignore=[], isobject=False):
    ##################################################
    ### Recursive all files under dir              ###
    ##################################################
    files = []
    if dir[-1] != "/":
        dir += "/"
    print(dir)
    for root, dirnames, filenames in os.walk(dir):
        for filename in fnmatch.filter(filenames, '*.py'):
            if filename in ignore:
                continue
            files.append(os.path.join(root, filename))
    print(files)
    for file in files:
        ##################################################
        ### trans normal path to import path           ###
        ### ex: abc/def => abc.def                     ###
        ##################################################
        packagepath = file[:-3]
        if packagepath[:2] == "./":
            packagepath = packagepath[2:]
        packagepath = packagepath.replace("/", ".")
        file = file[len(dir):]
        path = file.split("/")
        now = cls
        for d in path:
            if d != path[-1]:
                ##################################################
                ### build instance for path dir                ###
                ##################################################
                if not hasattr(cls, d):
                    setattr(now, d, T())
                now = getattr(now, d)
            else:
                ###################################################
                ### build instance for all class in target file ###
                ###################################################
                package = importlib.import_module(packagepath)
                modules = inspect.getmembers(package, inspect.isclass)
                reg_exp = "^.*" + packagepath + "\..*$"
                for x in modules:
                    if re.match(reg_exp, str(x[1])):
                        if isobject:
                            setattr(now, x[0], getattr(package, x[0])())
                        else:
                            setattr(now, x[0], getattr(package, x[0]))
