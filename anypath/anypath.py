from pathlib import Path
import shutil
from abc import ABCMeta, abstractmethod
from tempfile import mkdtemp

from anypath.dependencies import check_executable
from build.lib.anypath.dependencies import do_import


class BasePath(metaclass=ABCMeta):
    dependencies = []
    executables = []
    def __init__(self, protocol, path, persist_dir=None, **options):
        self.persist_dir = persist_dir
        self.protocol = protocol
        self.path = path
        self.td = None
        self.out_path = None

    @staticmethod
    def wrapped(func, *args, **kwargs):
        def decorator(self):
            # Import all declared dependencies
            modules = [do_import(dependency) for dependency in self.dependencies]
            # Check required executables
            for executable in self.executables:
                check_executable(executable)

            self._make_temp()
            # TODO: Check ordering of dependecies vs. args
            func(self, *modules)
            self._persist()
            return self.out_path
        return decorator

    @abstractmethod
    def fetch(self, *dependencies):
        pass

    def _make_temp(self):
        self.td = mkdtemp()
        self.out_path = Path(self.td).joinpath('out')

    def _persist(self):
        if not self.persist_dir:
            return self
        try:
            shutil.copytree(str(self.out_path.resolve()), self.persist_dir)
        except NotADirectoryError:
            shutil.copy(str(self.out_path.resolve()), self.persist_dir)
        self.out_path = Path(self.persist_dir).resolve()

    def close(self):
        shutil.rmtree(self.td)

    def __enter__(self):
        return self.fetch()

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()
        if exc_type:
            return exc_type
        else:
            return True


# noinspection PyMissingConstructor
class AnyPath(BasePath):
    def __new__(cls, path, persist_dir=None, **options):
        for protocol, provider in path_provider.registry.items():
            if path.startswith(protocol):
                path = path.replace(protocol, '', 1)
                fetcher = path_provider.registry[protocol](protocol, path, persist_dir, **options)
                fetcher.dependencies = cls.dependencies
                fetcher.executables = cls.executables
                return fetcher
        else:
            raise UnknownProtocol(f'Unknown protocol in {path} - Registered providers: {path_provider.registry}')

    def __init__(self, path, persist_dir=None, **options):
        pass

    def fetch(self):
        pass


def pattern(*patterns):
    def cls_decorator(cls):
        cls.patterns = [patt for patt in patterns]
        return cls

    return cls_decorator


class _Provider:
    def __init__(self):
        self.providers = set()
        self.registry = {}

    def add(self, *providers):
        for provider in providers:
            self.providers.add(provider)
            for patt in provider.patterns:
                self.registry[patt] = provider

    def check_requirements(self):
        for provider in self.providers:
            [do_import(dependency) for dependency in provider.dependencies]
            [check_executable(executable) for executable in provider.executables]

    def get_requirements(self):
        requirements = {'modules': [], 'executables': []}
        for provider in self.providers:
            requirements['modules'] += (provider.dependencies)
            requirements['executables'] += (provider.executables)
        return requirements

class UnknownProtocol(LookupError):
    pass


path_provider = _Provider()
