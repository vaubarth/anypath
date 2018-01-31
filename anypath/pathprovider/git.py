import subprocess

from anypath.anypath import BasePath, pattern
from anypath.dependencies import check_dependency


@pattern('git+http://', 'git+https://', 'git://')
class GitPath(BasePath):
    def __init__(self, protocol, path, persist_dir):
        super().__init__(protocol, path, persist_dir)
        self.protocol = protocol.replace('git+', '', 1)

    @BasePath.wrapped
    def fetch(self):
        check_dependency('git')
        git_process = subprocess.Popen(['git', 'clone', self.protocol + self.path, self.out_path])
        git_process.wait()
