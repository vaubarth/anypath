import unittest
from unittest.mock import MagicMock, patch

from anypath.anypath import AnyPath, path_provider
from anypath.pathprovider.git import GitPath
from anypath.pathprovider.http import HttpPath
from anypath.pathprovider.local import LocalPath
from anypath.pathprovider.mercurial import HgPath
from anypath.pathprovider.sftp import SftpPath


class TestFetching(unittest.TestCase):

    def setUp(self):
        path_provider.add(LocalPath, HttpPath, SftpPath, GitPath, HgPath)
        self.deps = []

    def mocked_dependencies(self):
        return self.deps

    def test_local(self):
        with AnyPath('./resources/localfile.txt') as path:
            content = path.read_text()
        self.assertEqual(content, 'Content', 'Content was not created')

    def test_http(self):
        HttpPath._check_dependencies = self.mocked_dependencies
        req_mock = MagicMock()
        res_mock = MagicMock()
        res_mock.text = 'Content'
        req_mock.Session().send.return_value = res_mock

        self.deps.append(req_mock)

        with AnyPath('http://example.com') as path:
            content = path.read_text()
        self.assertEqual(content, 'Content', 'Content was not created')

    def test_sftp(self):
        SftpPath._check_dependencies = self.mocked_dependencies
        sftp_mock = MagicMock()
        sftp_mock.hostkeys.HostKeys().items.return_value = {'key': 'value'}

        self.deps.append(sftp_mock)

        with AnyPath('ssh://user@host:example') as path:
            self.assertTrue(path.parent.exists(), 'Path was not created')

    def test_git(self):
        GitPath._check_dependencies = self.mocked_dependencies
        with patch('subprocess.Popen'):
            with AnyPath('git://asdas') as path:
                self.assertTrue(path.parent.exists(), 'Path was not created')

    def test_hg(self):
        HgPath._check_dependencies = self.mocked_dependencies
        with patch('subprocess.Popen'):
            with AnyPath('hg+http://asdas') as path:
                self.assertTrue(path.parent.exists(), 'Path was not created')
