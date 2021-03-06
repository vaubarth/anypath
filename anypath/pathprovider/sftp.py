import os
from pathlib import Path
from stat import S_ISDIR

from anypath.anypath import BasePath, pattern
from anypath.dependencies import dependencies


@pattern('sftp://', 'ssh://')
@dependencies('paramiko')
class SftpPath(BasePath):
    def __init__(self, protocol, path, persist_dir, password=None, private_key=None, port=22):
        super().__init__(protocol, path, persist_dir)
        self.password = password
        self.port = port
        self.private_key = private_key
        # We expect self.path to be in the format user@host:/path/on/host
        self.username, host_and_path = str(self.path).split('@', 1)
        self.host, self.path = host_and_path.split(':', 1)

        self.sftp = None
        self.path = Path(self.path)

    @BasePath.wrapped
    def fetch(self, paramiko):
        self.sftp = paramiko.SFTPClient.from_transport(self._connect(paramiko))
        self.sftp.chdir(str(self.path.parent))
        self._walk(self.path)

    def _connect(self, paramiko):
        """Connects to the host via ssh
        :param paramiko: The paramiko module
        :return: The transport connection
        """
        if self.private_key is not None:
            with open(self.private_key) as key_file:
                key = paramiko.RSAKey.from_private_key(key_file, self.password)
        else:
            key = None
        self._check_host(paramiko)
        transport = paramiko.Transport((self.host, self.port))
        transport.connect(None, self.username, self.password, key)
        return transport

    def _check_host(self, paramiko):
        """Checks if the host is in known_hosts
        :param paramiko: The paramiko module
        """
        hostkeys = paramiko.hostkeys.HostKeys()
        hostkeys.load(Path('~').expanduser().joinpath('.ssh', 'known_hosts'))
        if len(hostkeys.items()) == 0:
            raise Exception('No Host Keys Found')
        if hostkeys.lookup(self.host) is None:
            raise Exception(f'No hostkey for host {self.host} found.')

    # TODO: something nicer than replace first /
    def _walk(self, path):
        """Recursively walks through the remote path and fetches all found files
        :param paramiko: The paramiko module
        """
        os.makedirs(self.out_path.joinpath(str(path).replace('/', '', 1)), exist_ok=True)
        for entry in self.sftp.listdir_attr(str(path)):
            if S_ISDIR(entry.st_mode):
                # Go a level deeper in the folder hierarchy
                self._walk(path.joinpath(entry.filename))
            else:
                # If the element is a file, fetch it
                self.get(path.joinpath(entry.filename))

    def get(self, remote_path):
        self.sftp.get(str(remote_path), self.out_path.joinpath(str(remote_path).replace('/', '', 1)))
