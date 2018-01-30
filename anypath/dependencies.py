import importlib
import shutil


class NotInstalledError(BaseException):
    pass


def check_dependency(exec, error_message):
    if shutil.which(exec) is None:
        raise NotInstalledError(error_message)


def do_import(module):
    try:
        return importlib.import_module(module)
    except ModuleNotFoundError:
        raise NotInstalledError(f'Python module {module} is not installed.')
