from pathlib import Path

from anypath.anypath import BasePath, pattern


@pattern('file://')
class LocalPath(BasePath):
    def __init__(self, protocol, path, persist_dir):
        super().__init__(protocol, path, persist_dir)
        self.path = Path(self.path)
        self.out_path = self.path

    @BasePath.wrapped
    def fetch(self):
        pass

    def _make_temp(self):
        pass

    def close(self):
        pass
