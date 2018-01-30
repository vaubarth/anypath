import shutil
import subprocess

from anypath.anypath import BasePath, pattern, NotInstalledError


@pattern('hg+http://', 'hg+https://')
class HgPath(BasePath):
    def __init__(self, protocol, path, persist_dir):
        super().__init__(protocol, path, persist_dir)
        self.protocol = protocol.replace('hg+', '', 1)

    @BasePath.wrapped
    def fetch(self):
        if shutil.which('git') is None:
            raise NotInstalledError('Mercurial (hg) is not installed or not on the path.')
        git_process = subprocess.Popen(['hg', 'clone', self.protocol + self.path, self.out_path])
        git_process.wait()
