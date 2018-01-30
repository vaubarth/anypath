import unittest

from anypath.anypath import AnyPath, path_provider
from anypath.pathprovider.git import GitPath
from anypath.pathprovider.http import HttpPath
from anypath.pathprovider.local import LocalPath
from anypath.pathprovider.mercurial import HgPath
from anypath.pathprovider.sftp import SftpPath


class TestGitSchemes(unittest.TestCase):

    def setUp(self):
        path_provider.add(GitPath)

    def test_http_scheme(self):
        ap = AnyPath('git+http://test')
        self.assertEqual(type(ap), GitPath)

    def test_https_scheme(self):
        ap = AnyPath('git+https://test')
        self.assertEqual(type(ap), GitPath)

    def test_git_scheme(self):
        ap = AnyPath('git://test')
        self.assertEqual(type(ap), GitPath)


class TestHttpSchemes(unittest.TestCase):

    def setUp(self):
        path_provider.add(HttpPath)

    def test_http_scheme(self):
        ap = AnyPath('http://test')
        self.assertEqual(type(ap), HttpPath)

    def test_https_scheme(self):
        ap = AnyPath('https://test')
        self.assertEqual(type(ap), HttpPath)


class TestLocalSchemes(unittest.TestCase):

    def setUp(self):
        path_provider.add(LocalPath)

    def test_file_scheme(self):
        ap = AnyPath('file://test')
        self.assertEqual(type(ap), LocalPath)


class TestHgSchemes(unittest.TestCase):

    def setUp(self):
        path_provider.add(HgPath)

    def test_http_schemes(self):
        ap = AnyPath('hg+https://test')
        self.assertEqual(type(ap), HgPath)

    def test_https_schemes(self):
        ap = AnyPath('hg+https://test')
        self.assertEqual(type(ap), HgPath)


class TestSftpSchemes(unittest.TestCase):

    def setUp(self):
        path_provider.add(SftpPath)

    def test_sftp_scheme(self):
        ap = AnyPath('sftp://root@test:/test')
        self.assertEqual(type(ap), SftpPath)
