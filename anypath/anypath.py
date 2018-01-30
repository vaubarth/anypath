from pathlib import Path

import shutil
from abc import ABCMeta, abstractmethod
from tempfile import mkdtemp


class BasePath(metaclass=ABCMeta):
    def __init__(self, protocol, path, persist_dir=None):
        self.persist_dir = persist_dir
        self.protocol = protocol
        self.path = path
        self.td = None
        self.out_path = None

    @staticmethod
    def wrapped(func, *args, **kwargs):
        def decorator(self):
            self._make_temp()
            func(self, *args, **kwargs)
            self._persist()
            return self.out_path
        return decorator

    @abstractmethod
    def fetch(self):
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
        self.registry = {}

    def add(self, *providers):
        for provider in providers:
            for patt in provider.patterns:
                self.registry[patt] = provider


class UnknownProtocol(LookupError):
    pass


path_provider = _Provider()
