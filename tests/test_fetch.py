import unittest
from unittest.mock import MagicMock

from anypath.anypath import AnyPath, path_provider
from anypath.pathprovider.http import HttpPath
from anypath.pathprovider.local import LocalPath


class MockedRequests:

    def __init__(self):
        self.text = ''

    def Request(self, *args, **kwargs):
        return self

    def prepare(self):
        return self

    def Session(self):
        return self

    def send(self, *args, **kwargs):
        return self


class TestFetching(unittest.TestCase):

    def setUp(self):
        path_provider.add(LocalPath, HttpPath)
        self.deps = []

    def mocked_dependencies(self):
        return self.deps

    def test_local(self):
        with AnyPath('./resources') as path:
            content = path.read_text()
            self.assertEquals(content, 'Content')

    def test_http(self):
        HttpPath._check_dependencies = self.mocked_dependencies
        req_mock = MagicMock()
        res_mock = MagicMock()
        res_mock.text = ''
        req_mock.Session().send.return_value = res_mock
        self.deps.append(req_mock)

        with AnyPath('http://example.com') as path:
            print(path)
