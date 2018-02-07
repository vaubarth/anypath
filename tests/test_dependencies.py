import unittest

from anypath.anypath import path_provider
from anypath.pathprovider.git import GitPath
from anypath.pathprovider.http import HttpPath
from anypath.pathprovider.local import LocalPath
from anypath.pathprovider.mercurial import HgPath
from anypath.pathprovider.sftp import SftpPath


class TestExecutables(unittest.TestCase):

    def test_git_executables(self):
        self.assertEqual(['git'], GitPath.executables)

    def test_mercurial_executables(self):
        self.assertEqual(['hg'], HgPath.executables)

    def test_local_executables(self):
        self.assertEqual([], LocalPath.executables)


class TestDependencies(unittest.TestCase):

    def test_http_dependencies(self):
        self.assertEqual(['requests'], HttpPath.dependencies)

    def test_sftp_dependencies(self):
        self.assertEqual(['paramiko'], SftpPath.dependencies)

    def test_local_dependencies(self):
        self.assertEqual([], LocalPath.dependencies)


class TestProviderRequirements(unittest.TestCase):

    def setUp(self):
        path_provider.add(GitPath, HgPath, HttpPath, SftpPath, LocalPath)

    def test_get_requirements_modules(self):
        requirements = path_provider.get_requirements()
        self.assertEqual(['requests', 'paramiko'].sort(), requirements['modules'].sort())

    def test_get_requirements_executables(self):
        requirements = path_provider.get_requirements()
        self.assertEqual(['git', 'hg'].sort(), requirements['executables'].sort())
