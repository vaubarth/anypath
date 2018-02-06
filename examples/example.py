from anypath.anypath import AnyPath, path_provider
from anypath.pathprovider.http import HttpPath

path_provider.add(HttpPath)
path_provider.check_requirements()

with AnyPath('http://example.org') as path:
    content = path.read_text()
print(content)
