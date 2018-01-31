from anypath.anypath import BasePath, pattern, path_provider, AnyPath
from anypath.dependencies import do_import


@pattern('http://', 'https://')
class HttpPath(BasePath):
    def __init__(self, protocol, path, persist_dir, method='GET', data=None, headers=None, params=None):
        super().__init__(protocol, path, persist_dir)
        self.method = method
        self.headers = headers
        self.params = params
        self.data = data

    @BasePath.wrapped
    def fetch(self, requests=do_import('requests')):
        request = requests.Request(method=self.method,
                                   url=self.protocol + self.path,
                                   headers=self.headers,
                                   params=self.params,
                                   data=self.data).prepare()
        response = requests.Session().send(request)

        with open(self.out_path, 'w+') as f:
            f.write(response.text)