from pathlib import Path

from anypath.anypath import BasePath, pattern


@pattern('file://', '/', './')
class LocalPath(BasePath):
    def __init__(self, protocol, path, persist_dir):
        super().__init__(protocol, path, persist_dir)
        # In case we use 'file://' as protocol do not use it to construct the path
        if self.protocol == 'file://':
            protocol = ''
        else:
            protocol = self.protocol
        self.path = Path(f'{protocol}{path}')
        self.out_path = self.path

    @BasePath.wrapped
    def fetch(self):
        pass

    def _make_temp(self):
        pass

    def close(self):
        pass
