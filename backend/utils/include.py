import os
import fnmatch
import tornado.util
import inspect
import regex


class NOP:
    pass


def include(cls, directory, ignore=[], isobject=True):
    files = []
    for root, dirnames, filenames in os.walk(directory):
        files.extend(os.path.join(root, filename)
                     for filename in fnmatch.filter(filenames, '*.py')
                     if filename not in ignore)
    for file in files:
        package_path = file[:-3]
        if package_path[:2] == './':
            package_path = package_path[2:]
        package_path = package_path.replace('/', '.')
        now = cls
        for attr in package_path.split('.')[1:-1]:
            if not hasattr(now, attr):
                setattr(now, attr, NOP())
            now = getattr(now, attr)
        package = tornado.util.import_object(package_path)
        classes = inspect.getmembers(package, inspect.isclass)
        re = regex.compile("<class '%s.*" % package_path)
        for class_name, class_path in classes:
            if re.match(str(class_path)):
                if isobject:
                    setattr(now, class_name, getattr(package, class_name)())
                else:
                    setattr(now, class_name, getattr(package, class_name))
                setattr(getattr(now, class_name),
                        'path', package_path.split('.')[1:-1] + [class_name])
