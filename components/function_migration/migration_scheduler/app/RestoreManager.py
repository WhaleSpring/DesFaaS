"""RestoreManager() class to manage the global scheduling for restore process.

Typical usage example:

  RestoreManager(info)
"""
import requests
import json
import subprocess

# config.py
CLUSTER_CONFIG = {}
NAMESPACE = "openfaas-fn"
FUNCTION_CONFIG_PATH = ""

class RestoreManager:
    """The concrete implementation of scheduling in restore process.

    Attributes:
        info: related information including checkpointfile_path, container_name, target_ip, migrate_method.
    """

    def __init__(self,info):
        """Initial RestoreManager class and excute corresponding operations.
        
        Initial info that restore process need, post request to migration excutor in migration target VM
        and  then deploy new funtion to restore the function migrated.
        """      
        self.info = info
        self.restore_post()
        self.deploy_pod()

    def restore_post(self):
        """Send restore post request to migration excutor in migration target VM."""
        data = {
            "checkpointfile_path": self.info['checkpointfile_path'] ,
            "container_name": self.info['container_name'],
            "migrate_method": self.info['migrate_method']
        }
        headers = {
            "Content-Type": "application/json"
        }
        url = f"http://{self.info['target_ip']}:8052/MigrateRestoreSubModule"
        requests.post(url, data=json.dumps(data), headers=headers)


    def deploy_pod(self):
        """Communicate with OpenFaaS gateway to deploy new function in OpenFaaS."""
        cmd = f"faas deploy -f {FUNCTION_CONFIG_PATH}/{self.info['container_name']}.yml -e write_debug=true -e read_timeout=180s -e write_timeout=180s"
        result = subprocess.run(cmd, capture_output=True, text=True)


    