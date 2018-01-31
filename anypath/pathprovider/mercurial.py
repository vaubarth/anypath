import shutil
import subprocess

from anypath.anypath import BasePath, pattern
from anypath.dependencies import check_dependency


@pattern('hg+http://', 'hg+https://')
class HgPath(BasePath):
    def __init__(self, protocol, path, persist_dir):
        super().__init__(protocol, path, persist_dir)
        self.protocol = protocol.replace('hg+', '', 1)

    @BasePath.wrapped
    def fetch(self):
        check_dependency('hg')
        git_process = subprocess.Popen(['hg', 'clone', self.protocol + self.path, self.out_path])
        git_process.wait()
