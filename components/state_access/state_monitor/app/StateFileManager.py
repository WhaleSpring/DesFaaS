"""StateFileManager() class aims to help StateMonitor access the remote file in external storage.

Typical usage example:

    sfm = StateFileManager()
    date = sfm.external_states_get()
"""
import paramiko
import os

# config.py
PORT = 22
EXTERNAL_STATE_SERVER_IP = ""
EXTERNAL_STATE_SERVER_USERNAME = ""
EXTERNAL_STATE_SERVER_PASSWORD = ""
EXTERNAL_STATE_SERVER_STORAGE_PATH = ""

class StateFileManager:
    """Connect the external storage server to get the state information in external storage.

    Attributes:
        ssh: connect the server where contains external storage.
    """

    def __init__(self):
        """Initial the StateFileManager class and connect the server."""
        self.ssh = paramiko.SSHClient()
        self.ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        self.ssh.connect(EXTERNAL_STATE_SERVER_IP, PORT, EXTERNAL_STATE_SERVER_USERNAME, EXTERNAL_STATE_SERVER_PASSWORD)

    def close(self):
        """Close the connection."""
        self.ssh.close()
    
    def external_states_get(self):
        """Aquire the list of state in external storage.
        
        Returns:
            A list containing all state names in external storage.
        """
        # Get the storage JSON file list
        cmd = f"ls {EXTERNAL_STATE_SERVER_STORAGE_PATH}/*.json"
        stdout = self.ssh.exec_command(cmd)
        json_files = stdout.read().decode().splitlines()
        function_names = []

        # Process the file list to get the state name list.
        for json_file in json_files:
            file_name = os.path.basename(json_file)
            function_names.append(os.path.splitext(file_name)[0])
        return function_names