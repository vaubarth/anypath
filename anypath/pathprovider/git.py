import subprocess

from anypath.anypath import BasePath, pattern
from anypath.dependencies import required_executables


@pattern('git+http://', 'git+https://', 'git://')
@required_executables('git')
class GitPath(BasePath):
    def __init__(self, protocol, path, persist_dir, *args):
        super().__init__(protocol, path, persist_dir)
        self.protocol = protocol.replace('git+', '', 1)

    @BasePath.wrapped
    def fetch(self):
        git_process = subprocess.Popen(['git', 'clone', self.protocol + self.path, self.out_path])
        git_process.wait()
