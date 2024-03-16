"""RestoreExcutor() class to excute migration operation while restore process in worker nodes.

Typical usage example:

  RestoreExcutor(msg)
"""
from app import CheckpointFileManager

class RestoreExcutor:
    """The related operation about the excution of migration in worker nodes.

    Attributes:
        checkpointfile_path: the location of checkpoint file
        migrate_method: the transfer medium of this migration
        container_name: the container name of migrated function 
    """

    def __init__(self,msg):
        """Initial RestoreExcutor class and complete the checkpoint image-get.
        
        Args:
            msg: all messages the restore operation requiring

        Returen:
            the response of  checkpoint image-get operation
        """
        self.checkpointfile_path = msg['checkpointfile_path']
        self.container_name = msg['container_name']
        self.migrate_method = msg['migrate_method']

        res = self.checkpoint_image_get()
        
        return res
    
    def checkpoint_image_get(self):
        """Get the checkpoint image to restore the function in target VM"""
        if self.migrate_method == 1: # external storage
            fs = CheckpointFileManager("")
            fs.image_build(self.checkpointfile_path,self.container_name)
        else: # network or shared disk
            fs = CheckpointFileManager("")
            fs.image_pull(self.container_name)