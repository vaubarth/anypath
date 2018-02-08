from anypath.anypath import AnyPath, path_provider
from anypath.pathprovider.git import GitPath
from anypath.pathprovider.http import HttpPath

path_provider.add(HttpPath, GitPath)
path_provider.check_requirements()

with AnyPath('http://example.org') as path:
    content = path.read_text()
    print(len(content))

with AnyPath('git+https://github.com/vaubarth/anypath.git') as path:
    content = path.glob('*')
    print(list(content))
