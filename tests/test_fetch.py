import unittest

from anypath.anypath import AnyPath, path_provider
from anypath.pathprovider.local import LocalPath


class TestFetching(unittest.TestCase):

    def setUp(self):
        path_provider.add(LocalPath)

    def test_local(self):
        with AnyPath('./resources') as path:
            content = path.read_text()
            self.assertEquals(content, 'Content')
