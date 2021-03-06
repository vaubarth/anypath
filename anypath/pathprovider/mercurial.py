import subprocess

from anypath.anypath import BasePath, pattern
from anypath.dependencies import required_executables


@pattern('hg+http://', 'hg+https://')
@required_executables('hg')
class HgPath(BasePath):
    def __init__(self, protocol, path, persist_dir):
        super().__init__(protocol, path, persist_dir)
        self.protocol = protocol.replace('hg+', '', 1)

    @BasePath.wrapped
    def fetch(self):
        git_process = subprocess.Popen(['hg', 'clone', self.protocol + str(self.path), str(self.out_path)])
        git_process.wait()
