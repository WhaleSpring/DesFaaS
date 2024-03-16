"""StateFileManager() class aims to send file to external storage.

Typical usage example:

    sfm = StateFileManager()
    sfm.file_send(local_file_path,target_file_path)
"""
import paramiko

# config
PORT = 22

class StateFileManager:
    """Connect the external storage server to send file to it.

    Attributes:
        ssh: connect the server where contains external storage.
    """
    def __init__(self,ip,username,password):
        """Initial the StateFileManager class and connect the server."""
        self.ssh = paramiko.SSHClient()
        self.ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        self.ssh.connect(ip, PORT, username, password)

    def close(self):
        """Close the connection."""
        self.ssh.close()

    def file_send(self,local_file_path,target_file_path):
        """Send state JSON file from local to another server.
        
        Args:
            local_file_path
            target_file_path
        """
        sftp = self.ssh.open_sftp()
        sftp.put(local_file_path, target_file_path)
        sftp.close()

    def file_pull(self,remote_file_path,local_file_path):
        """Pull state JSON file from remote server to local path.
        
        Args:
            local_file_path
            remote_file_path
        """
        sftp = self.ssh.open_sftp()
        sftp.get(remote_file_path,local_file_path)
        sftp.close()
