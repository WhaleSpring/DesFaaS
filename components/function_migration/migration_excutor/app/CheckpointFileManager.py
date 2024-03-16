"""CheckpointFIleManager() class to manage the checkpoint file and checkpoint image in migration process.

Typical usage example:

    cfm = CheckpointFileManager(host)
"""
import paramiko
import subprocess

# config.py
WORKER_NODES_USERNAME = ""
WORKER_NODES_PASSWORD = ""
WORKER_NODES_PORT = ""
EXTERNAL_IMAGE_STORAGE = ""

class CheckpointFileManager:
    """The related operation about the file and image opration when migrating in worker nodes.

    Attributes:
        host: the ip address of remote connecting target VM.
    """

    def __init__(self,host):
        """Initial CheckpointFileManager class and complete the remote target VM (if exsists)."""
        if not host == "" :
            self.ssh = paramiko.SSHClient()
            self.ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            self.ssh.connect(host, WORKER_NODES_PORT, WORKER_NODES_USERNAME, WORKER_NODES_PASSWORD)

    def close(self):
        """Close ssh connect"""
        self.ssh.close()
    
    def file_send(self,local_path,target_path):
        """Send a file from local path to remote target path.

        Args:
            local_path (string): local file path
            target_path (string): target file path
        """
        sftp = self.ssh.open_sftp()
        sftp.put(local_path, target_path)

    def file_pull(self,remote_path,local_path):
        """Pull a file from remote taget path to local path.

        Args:
            local_path (string): local file path
            remote_path (string): remote file path
        """
        sftp = self.ssh.open_sftp()
        sftp.get(remote_path,local_path)

    def image_build(self,file_path,image_name):
        """Build the checkpoint image according to the checkpoint file

        Args:
            file_path (string): the checkpoint file path
            image (string): the image name build by checkpoint file
        """
        cmd = f"""
            newcontainer=$(buildah from scratch) && \
            buildah add $newcontainer {file_path} / && \
            buildah config --annotation=io.kubernetes.cri-o.annotations.checkpoint.name={image_name} $newcontainer && \
            buildah commit $newcontainer {image_name}:latest && \
            buildah rm $newcontainer
        """
        subprocess.run(cmd, shell=True, stdout=subprocess.PIPE, text=True, check=True)

    def image_push(self,image_name):
        """Push checkpoint image from local image storage to external image repository.

        Args:
            image (string): the image which will be push to external storage
        """
        cmd = f"buildah push localhost/{image_name}:latest {EXTERNAL_IMAGE_STORAGE}/{image_name}:latest"
        subprocess.run(cmd, shell=True, stdout=subprocess.PIPE, text=True, check=True)

    def image_pull(self,image_name):
        """Pull checkpoint image from external image repository to local storage.

        Args:
            image (string): the pulled image
        """
        cmd = f"buildah pull {EXTERNAL_IMAGE_STORAGE}/{image_name}:latest"
        subprocess.run(cmd, shell=True, stdout=subprocess.PIPE, text=True, check=True)