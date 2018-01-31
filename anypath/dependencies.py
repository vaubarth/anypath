import importlib
import shutil


class NotInstalledError(BaseException):
    pass


def check_dependency(exec):
    if shutil.which(exec) is None:
        raise NotInstalledError(f'{exec} is not installed or not on the path.')


def do_import(module):
    try:
        return importlib.import_module(module)
    except ModuleNotFoundError:
        raise NotInstalledError(f'Python module {module} is not installed.')
