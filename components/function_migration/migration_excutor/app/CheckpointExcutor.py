"""CheckpointExcutor() class to excute migration operation while checkpoint process in worker nodes.

Typical usage example:

  CheckpointExcutor(msg)
"""
import shutil

from app import CheckpointFileManager


WORKER_CHECKPOINT_DISK_PATH = ""
WORKER_SHARED_DISK_PATH = ""

class CheckpointExcutor:
    """The related operation about the excution of migration in worker nodes.

    Attributes:
        checkpointfile_path: the location of checkpoint file
        transfer_method: the transfer medium of this migration
        target_ip: ip address of the migration target VM
        targetfile_path: the target file path in target VM
        container_name: the container name of migrated function 
    """

    def __init__(self,msg):
        """Initial CheckpointExcutor class and complete the checkpoint send.
        
        Args:
            msg: all messages the checkpoint operation requiring

        Returen:
            the response of checkpoint send operation
        """
        self.checkpointfile_path = msg['checkpointfile_path']
        self.transfer_method = msg['migrate_method']
        self.target_ip = msg['target_ip']
        self.targetfile_path = msg['targetfile_path']
        self.container_name = msg['container_name']
        
        res = self.checkpoint_file_send()

        return res

    def checkpoint_file_send(self):
        """Select a transfer method to excute the corresponding operation."""
        if self.transfer_method == 0 : # Network
            self.network_transfer()
        elif self.transfer_method == 1 : # External Storage
            self.externalstorage_transfer()
        elif self.transfer_method == 2 : # Shared Disk
            self.shareddisk_transfer()

    def network_transfer(self):
        """Transfer checkpoint file by network.
        
        Send checkpoint file from local path to the target path in migration target VM.
        """
        fs = CheckpointFileManager(self.target_ip)
        fs.file_send(self.checkpintfile_path,WORKER_CHECKPOINT_DISK_PATH)
        fs.close()

    def shareddisk_transfer(local_file_path):
        """Transfer checkpoint file by shared disk.
        
        Send checkpoint file from local path to the shared disk between local VM and migration target VM.
        """
        shutil.copy(local_file_path, WORKER_SHARED_DISK_PATH)

    def externalstorage_transfer(self):
        """Transfer checkpoint file by external storage.
        
        Build the checkpoint image about checkpoint file and push the image to external image repository.
        """
        fs = CheckpointFileManager(self.target_ip)
        fs.image_build(self.checkpointfile_path,self.container_name)
        fs.image_push(self.container_name)
        fs.close()