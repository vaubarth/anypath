import importlib
import shutil


class NotInstalledError(BaseException):
    pass


def dependencies(*modules):
    def cls_decorator(cls):
        cls.dependencies = [module for module in modules]
        return cls
    return cls_decorator


def do_import(module):
    try:
        return importlib.import_module(module)
    except ModuleNotFoundError:
        raise NotInstalledError(f'Python module {module} is not installed.')


def required_executables(*executables):
    def cls_decorator(cls):
        cls.executables = [executable for executable in executables]
        return cls
    return cls_decorator


def check_executable(exec):
    if shutil.which(exec) is None:
        raise NotInstalledError(f'{exec} is not installed or not on the path.')
    return exec
