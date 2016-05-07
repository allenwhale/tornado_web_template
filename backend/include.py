import fnmatch
import importlib
import inspect
import os
import re

class T:
    pass

def include(cls, dir="./", ignore=[], isobject=False):
    files = []
    if dir[-1] != "/":
        dir += "/"
    for root, dirnames, filenames in os.walk(dir):
        for filename in fnmatch.filter(filenames, '*.py'):
            if filename in ignore:
                continue
            files.append(os.path.join(root, filename))
    for file in files:
        packagepath = file[:-3]
        if packagepath[:2] == "./":
            packagepath = packagepath[2:]
        packagepath = packagepath.replace("/", ".")
        file = file[len(dir):]
        path = file.split("/")
        now = cls
        print(file)
        for d in path:
            if d != path[-1]:
                if not hasattr(cls, d):
                    setattr(now, d, T())
                now = getattr(now, d)
            else:
                package = importlib.import_module(packagepath)
                modules = inspect.getmembers(package, inspect.isclass)
                reg_exp = "^.*" + packagepath + "\..*$"
                for x in modules:
                    if re.match(reg_exp, str(x[1])):
                        if isobject:
                            setattr(now, x[0], getattr(package, x[0])())
                        else:
                            setattr(now, x[0], getattr(package, x[0]))
