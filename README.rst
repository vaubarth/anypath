=======
AnyPath
=======
AnyPath makes it trivial to fetch remote resources and work with them locally.
It provides a normalized interface over different resources so that handling them is always consistent.

.. code-block:: python

    with AnyPath('sftp://jane@host:/home/jane') as path:
        path.joinpath('somefile.txt').open().read()

Here AnyPath will copy the directory `/home/jane` from a remote host via ssh to a local temporary directory.
It is then possible to work with the files locally. After we are done the temporary files are deleted.
Therefore AnyPath is useful if you want to fetch e.g. some config files or a small project directory from a remote location and work with it locally.

- `Installation`_

  - `Dependencies`_

- `Basic Usage`_

  - `Persistance`_
  - `Providers and options`_

    - `Http`_
    - `Sftp`_
    - `Git`_
    - `Mercurial`_
    - `Local`_

  - `Checking for dependencies`_
  - `Limitations`_

- `Contributing`_

  - `Writing a new PathProvider`_

    - `Decorators`_
    - `The fetch method`_

- `License`_


Installation
============
To install simply do::

    pip install anypath

Dependencies
------------
By default AnyPath does not install the dependencies for the different providers. You should install them as needed:

    +-----------+---------------------------------+
    | Provider  | Dependencies                    |
    +===========+=================================+
    | git       | local git installation          |
    +-----------+---------------------------------+
    | mercurial | local mercurial installation    |
    +-----------+---------------------------------+
    | http      | `pip install requests`          |
    +-----------+---------------------------------+
    | sftp      | `pip install paramiko`          |
    +-----------+---------------------------------+
    | local     | None                            |
    +-----------+---------------------------------+


Basic Usage
===========
AnyPath uses :code:`pathproviders` to handle different remote resources. The resources are then fetched to a new temporary directory where you can work with them.
The newly fetched ressources are wrapped in a :code:`pathlib.Path`.

.. code-block:: python

   from anypath.anypath import AnyPath, path_provider
   from anypath.pathprovider.http import HttpPath

   path_provider.add(HttpPath)

   with AnyPath('http://example.org') as path:
       path.open().read()

First you register all the providers that you want to use (note: remember to install the dependencies per provider).
Now you can open any uri that has a scheme known to one of the registered providers.

    +-----------+-----------------------------------------+
    | Provider  | Schemes                                 |
    +===========+=========================================+
    | git       | - `git+http://`                         |
    |           | - `git+https://`                        |
    |           | - `git://`                              |
    +-----------+-----------------------------------------+
    | mercurial | - `hg+http://`                          |
    |           | - `hg+https://`                         |
    +-----------+-----------------------------------------+
    | http      | - `http://`                             |
    |           | - `https://`                            |
    +-----------+-----------------------------------------+
    | sftp      | - `sftp://`                             |
    |           | - `ssh://`                              |
    +-----------+-----------------------------------------+
    | local     | - `file://`                             |
    |           | - `/`                                   |
    |           | - `./`                                  |
    +-----------+-----------------------------------------+

You can use AnyPath either as a contextmanager (:code:`with AnyPath ...`) or directly by calling :code:`fetch()`.
Beware that you will have to call :code:`close()` manually when not using the contextmanager to cleanup the temporary files.

.. code-block:: python

   path_provider.add(HttpPath)
   ap = AnyPath('http://example.org')
   path = ap.fetch() # type: Path
   path.open().read()
   ap.close()

Persistance
-----------
The example so far was useful if you are only interested in the content of a fetched resource. They are created in a temporary folder, where you can work with them, and are deleted afterwards.
Sometimes however you may want to persist the remote resource outside of a temporary location.

.. code-block:: python

   path_provider.add(HttpPath)

   with AnyPath('http://example.org', persist_dir='/your/local/path') as path:
       path.open().read()

Instead of copying the files manually you can specify a :code:`persist_dir` when creating the AnyPath. The temporary resources will then be copied to that location.
As a result you will get the :code:`persist_dir` wrapped as an :code:`pathlib.Path` instead of the temporary location and you can directly work with it.

Providers and options
---------------------
While the defaults for fetching resources might be fine for many use cases there are many situations where you might want to pass some options to a provider.
You might for example want to do a POST with an HttpPath or pass credentials to a GitPath.

Options are always passed as keyword arguments. Following you will find all providers and their available options.

Http
^^^^
The options are passed to a requests.Request object, they behave the same and are named accordingly.

.. code-block:: python

   AnyPath('http://example.org', method='GET', data=None, headers=None, params=None)

=========   ============================================================
Option      Description
=========   ============================================================
method      Default: 'GET'

            Specifies the HTTP method to be used as a string.

            E.g. POST, DELETE, PUT


data        Default: None

            The body to attach to the request.

            If a dictionary is provided, form-encoding will take place.


headers     Default: None

            A dictionary of headers to send in the request.


params      Default: None

            A dictionary of URL parameters to append to the URL.
=========   ============================================================

Sftp
^^^^
The path for Sftp is expected to be in the format :code:`sftp://user@host:/path/on/host`, additional options can be set via arguments.

.. code-block:: python

   AnyPath('sftp://user@localhost:/path/on/host', password=None, private_key=None, port=22)

============    ============================================================
Option          Description
============    ============================================================
password        Default: None

                The password for the user.

                Also used if private_key is given,
                and the key requires a password


private_key     Default: None

                The path to the local private_key (as a string)
                if it is used to login


port            Default: 22

                The ssh port to be used.
============    ============================================================

Git
^^^
None

Mercurial
^^^^^^^^^
None

Local
^^^^^
None

Checking for dependencies
-------------------------
By default dependencies are only checked right before the appropriate PathProvider is called, i.e., at the moment the remote resources should be fetched.
It is possible to check for dependencies as soon as all PathProviders are registered. There are two methods to do that, :code:`get_requirements()` and :code:`check_requirements()`.
:code:`get_requirements()` only returns a dictionary of all dependencies (modules and executables) that would be needed, while :code:`check_requirements()` fully checks for all dependencies to be present and would raise an exception if they are not:

.. code-block:: python

    >>> path_provider.add(HttpPath, SftpPath, GitPath)
    >>> path_provider.get_requirements()
    {'modules': ['requests', 'paramiko'], 'executables': ['git']}

If the requirements for HttpPath (the requests module) would not be met calling :code:`check_requirements()` would raise an exception:

.. code-block:: python

    >>> path_provider.add(HttpPath)
    >>> path_provider.check_requirements()
    ...anypath.dependencies.NotInstalledError: Python module requests is not installed.


Limitations
-----------
You might not want to use AnyPath if you are working with a huge remote resource.
Everything is fetched to your local machine, which might take some time and cost a lot of space if you try to work with a whole filesystemn of a remote host for example.
It is also not intended do do updates to the remote resource since there is no mechanism to write changes back to the remote.

Contributing
============
You can contribute in any of the following areas, no matter if it is your first OSS contribution or your thousandths.
Contributions are welcome for example:

- If you find any issue or bug when using AnyPath
- If you want to add to the documentation or fix incorrect or missing documentation.
- If you want to add features or work on the codebase in general

Just file an issue in the tracker first describing what you would like to do and then create a pull-request.

Writing a new PathProvider
--------------------------
Creating a new PathProvider requires writing a new class; using it requires registering it via :code:`path_provider.add()`

The basic structure of a PathProvider looks like this:

.. code-block:: python

    @pattern('protocol://')
    @required_executables('some_executable')
    @dependencies('some_py_module')
    class MyPath(BasePath):
        def __init__(self, protocol, path, persist_dir, some_option='default'):
            super().__init__(protocol, path, persist_dir)
            ...

        @BasePath.wrapped
        def fetch(self):
            ...

Here a PathProvider MyPath is created, it registers a protocol that it can handle, declares some requirements and has a fetch method which does the actual work.
The PathProvider must always inherit from :code:`anypath.BasePath`.

Decorators
^^^^^^^^^^
There are three class decorators available for a PathProvider:

:code:`pattern('')`

This decorator is required. It lists all patterns a path can start with on which the PathProvider can act. In the example MyPath registers the pattern :code:`protocol://`,
meaning whenever a path start with :code:`protocol://` MyPath will be called.

A PathProvider can register more than one pattern, each pattern is passed as a single argument to the pattern decorator.
The HttpPath for example registers :code:`http://` and :code:`https://` using :code:`@pattern('http://', 'https://')`.


:code:`required_executables('')`

This decorator is optional. It lists all required executables which must be available on the system to perform the tasks of the PathProvider.
In the example MyPath specifies, that :code:`some_executable` must exists and be callable from within the program.

AnyPath checks for the existence via checking :code:`shutil.which(executable) is None` where :code:`executable` is the exectuable specified in :code:`required_executables()`.


:code:`dependencies('')`

This decorator is optional. It lists all required python modules which must be available to be imported to perform the tasks of the PathProvider.
In the example MyPath specifies, that :code:`some_py_module` must exists and be importable.

AnyPath will import the module via :code:`importlib.import_module(module)` where :code:`module` is the module specified in :code:`dependencies()`.

The fetch method
^^^^^^^^^^^^^^^^
The class must include a :code:`fetch` method which will be called to fetch the remote resources.
The fetch method must have the method decorator :code:`@BasePath.wrapped`. Its main purpose is to call pre and post actions to fetching the resources.
Those actions are creating a temporary directory and persisting the temporary files if needed.

License
=======
AnyPath is licensed under "Mozilla Public License Version 2.0". See LICENSE.txt for the full license.
