import logging
import shutil
from abc import ABCMeta, abstractmethod
from pathlib import Path
from tempfile import mkdtemp

from anypath.dependencies import check_executable
from anypath.dependencies import do_import

LOG = logging.getLogger('anypath.anypath')


class BasePath(metaclass=ABCMeta):
    """The base class for all PathProviders.
    Defines common methods and class variables. It provides enter and exit methods so that all PathProviders can be used
    as context manaers.
    :param protocol: Represents the protocol for the PathProvider, e.g. 'ssh://'
    :param path: The remote path to be fetched
    :param persist_dir: If specified, the directory to which the remote resource(s) should be copied to. It is used for
    further Path manipulations instead of the default temp directory.
    :param options: Additional options for the PathProviders if they require/allow them
    """
    # List of required modules to be importer per Pathrovider
    dependencies = []
    # List of executables that must be accessible for calling per PathProvider
    executables = []

    def __init__(self, protocol: str, path: str, persist_dir: str = None, **options: dict):
        self.persist_dir = persist_dir
        self.protocol = protocol
        self.path = path
        # Temporary directory path
        self.td = None
        # Path that will be used after the resources are fetched
        self.out_path = None

    @staticmethod
    def wrapped(func, *args, **kwargs):
        """This decorator must be used on the fetch method as an entry point.
        Before the decorated method is called the following things happen:
        - Dependencies and executables are checked
        - The temporary directory is created
        After the decorated method is called the following things happen:
        - The files are persisted if the persist_dir parameter is set
        - The out_path is returned, which is either the temp dir or persist_dir
        """

        def decorator(self):
            modules = self._check_dependencies()
            self._make_temp()
            # TODO: Check ordering of dependencies vs. args
            func(self, *modules)
            self._persist()
            return self.out_path

        return decorator

    def _check_dependencies(self):
        LOG.debug('Checking for dependencies of PathProvider %s', self.__class__)
        # Import all declared dependencies
        modules = [do_import(dependency) for dependency in self.dependencies]
        # Check required executables
        for executable in self.executables:
            check_executable(executable)
        return modules

    @abstractmethod
    def fetch(self, *dependencies):
        """Must be implemented by all PathProviders, this method is called on __enter__
        :param dependencies: The dependencies that the PathProvider needs are injected to the method as parameters
        """
        pass

    def _make_temp(self):
        LOG.debug('Creating temporary directory')
        self.td = mkdtemp()
        self.out_path = Path(self.td).joinpath('out')
        LOG.debug('Out path is set to %s', self.out_path)

    def _persist(self):
        """If persist_dir is set all files from the temporary directory are copied to it.
        The out_path will be set to persist_dir if it is set.
        """
        if not self.persist_dir:
            return self
        LOG.debug('Persisting files to %s', self.persist_dir)
        try:
            shutil.copytree(str(self.out_path.resolve()), self.persist_dir)
        except NotADirectoryError:
            shutil.copy(str(self.out_path.resolve()), self.persist_dir)
        self.out_path = Path(self.persist_dir).resolve()

    def close(self):
        try:
            shutil.rmtree(self.td)
        except PermissionError as e:
            LOG.debug('Could not delete temporary files %s', e.strerror)

    def __enter__(self):
        return self.fetch()

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()
        if exc_type:
            raise exc_type
        else:
            return True


# noinspection PyMissingConstructor
class AnyPath(BasePath):
    """This class represents the public API for anypath, it is called to instantiate a new PathProvider.
    Usage example: AnyPath('ssh://path')
    This class is never instantiated itself, it returns an instance of a PathProvider immediately in the __new__ method
    :param path: The remote path to be fetched
    :param persist_dir: If specified, the directory to which the remote resource(s) should be copied to. It is used for
    further Path manipulations instead of the default temp directory.
    :param options: Additional options for the PathProviders if they require/allow them
    """

    def __new__(cls, path: str, persist_dir: str = None, **options: dict):
        for protocol, provider in path_provider.registry.items():
            if path.startswith(protocol):
                LOG.debug('Protocol is %s', protocol)
                path = path.replace(protocol, '', 1)
                # Get the appropriate PathProvider from the provider-registry and instantiate it
                fetcher = path_provider.registry[protocol]
                LOG.debug('Using PathProvider %s', fetcher)
                fetcher = fetcher(protocol, path, persist_dir, **options)
                fetcher.dependencies = provider.dependencies
                fetcher.executables = provider.executables
                return fetcher
        else:
            raise UnknownProtocol(f'Unknown protocol in {path} - Registered providers: {path_provider.registry}')

    # Init is not used, the signature is provided to help with autocomplete etc. in IDEs
    def __init__(self, path, persist_dir=None, **options):
        pass

    def fetch(self):
        pass


def pattern(*patterns):
    """Decorator that registers a protocol on a PathProvider
    Usage example: @pattern('http://', 'https://')
    :param patterns: The patterns to be used as protocols
    """

    def cls_decorator(cls):
        cls.patterns = [patt for patt in patterns]
        return cls

    return cls_decorator


class _Provider:
    """Holds references to all registered providers and links there protocol-patterns to them.
    Additionally handles the dependencies of all registered providers
    """

    def __init__(self):
        self.providers = set()
        self.registry = {}

    def add(self, *providers):
        for provider in providers:
            self.providers.add(provider)
            for patt in provider.patterns:
                self.registry[patt] = provider

    def check_requirements(self):
        LOG.debug('Checking requirements for registered PathProviders %s', self.providers)
        for provider in self.providers:
            [do_import(dependency) for dependency in provider.dependencies]
            [check_executable(executable) for executable in provider.executables]

    def get_requirements(self):
        requirements = {'modules': [], 'executables': []}
        for provider in self.providers:
            requirements['modules'] += provider.dependencies
            requirements['executables'] += provider.executables
        LOG.debug('Requirements for registered PathProviders %s are %s', self.providers, requirements)
        return requirements


class UnknownProtocol(LookupError):
    pass


path_provider = _Provider()
