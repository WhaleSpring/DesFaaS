"""CheckpointManager() class to manage the global scheduling for checkpoint process.

Typical usage example:

  CheckpointManager(info).checkpoint_post()
"""
import subprocess
import json
import yaml
import os
import requests

# config.py
CLUSTER_CONFIG = {}
NAMESPACE = "openfaas-fn"
FUNCTION_CONFIG_PATH = ""
WORKER_CHECKPOINT_DISK_PATH = ""
WORKER_SHARED_DISK_PATH = ""

class CheckpointManager:
    """The concrete implementation of scheduling in checkpoint process.

    Attributes:
        info: related information including checkpointfile_path, container_name, pod_name, target_path,
            migrate_method, source_ip.
    """

    def __init__(self,info):
        """Initial CheckpointManager class and excute corresponding operations.
        
        Initial info that checkpint process need, remove old pod and modify config yaml file of function.
        """        
        self.info = info
        self.info['checkpointfile_path'] = self.checkpoint_post()
        self.remove_pod()
        self.modify_yaml()
        return self.info

    def checkpoint_post(self):
        """Complete a time of checkpoint operation.

        At first, send checkpoint post request to kubelet checkpoint API in migration source VM. Then transfer
        the checkpoint file by specific migration medium.

        Returns:
            A string to describe the checkpoint's path in migration target VM with its file name (if exists,
            else return empty string) .
        """
        checkpointfile_source_path = self.post_kubelet()
        checkpointfile_path = self.checkpoint_transfer(checkpointfile_source_path)
        return checkpointfile_path
        

    def remove_pod(self):
        """Remove the old function.

        Communicate with OpenFaaS gateway to remove the old function config in OpenFaaS, and then delete the
        old container by force to avoid the influence about deploying new function (while restoring).
        """
        # Remove old function config.
        cmd1 = f'faas remove -f {FUNCTION_CONFIG_PATH}/{self.info["container_name"]}.yml'
        subprocess.run(cmd1, shell=True, stdout=subprocess.PIPE, text=True, check=True)
        
        # Delete old container by force.
        cmd2 = f"kubectl delete pod -n openfaas-fn {self.info['pod_name']}   --grace-period=0 --force"
        subprocess.run(cmd2, shell=True, stdout=subprocess.PIPE, text=True, check=True)

    def modify_yaml(self):
        """Modify the new function config by changing the OpenFaaS yaml file."""
        # Open corresponding config file
        with open(f'{FUNCTION_CONFIG_PATH}/{self.info["container_name"]}.yml', 'r') as file:
            data = yaml.load(file, Loader=yaml.FullLoader)
        
        # Get address ip of target VM by target VM name
        for key, value in CLUSTER_CONFIG.items():
            if value == self.info['target_node_name']:
                target_ip = key
                
        # Modify related information.
        data['functions'][self.info["container_name"]]['environment']['NodeIP'] = target_ip
        data['functions'][self.info["container_name"]]['constraints'] = [ f'{self.info["target_node_name"]}=1' ]
        
        # Save the config file
        with open(f'{FUNCTION_CONFIG_PATH}/{self.info["container_name"]}.yml', 'w') as file:
            yaml.dump(data, file, default_flow_style=False, sort_keys=False)

    def post_kubelet(self):
        """Construct request and post it to kubelet API to get the checkpoint file with function runtime state.
        
        Returns:
            A string about file path containing the path of checkpoint file and file name in the source VM.
        """
        # Send request
        cmd = f'''curl -sk -X POST "https://{ self.info['source_ip'] }:10250/checkpoint/{NAMESPACE}/{self.info['pod_name']}/{self.info['container_name']}" --key /etc/kubernetes/pki/apiserver-kubelet-client.key --cacert /etc/kubernetes/pki/ca.crt --cert /etc/kubernetes/pki/apiserver-kubelet-client.crt'''
        res = subprocess.run(cmd, shell=True, stdout=subprocess.PIPE, text=True, check=True)
        
        # Read and return file path
        checkpointfile_path = json.loads(res.stdout).get("items")[0]    
        return checkpointfile_path

    def checkpoint_transfer(self,checkpointfile_source_path):
        """Transfer checkpoint from source to target location according to the migration method.

        Returns:
            A string about file path containing the path of checkpoint file and file name in the target VM.
        """
        # Choose the target path
        checkpointfile_name = os.path.basename(checkpointfile_source_path)
        if self.info['migrate_method'] == 0: # disk of tagret VM
            target_path = f"{WORKER_CHECKPOINT_DISK_PATH}/{checkpointfile_name}"
        elif self.info['migrate_method'] == 2: # shared disk between target and source VMs
            target_path = f"{WORKER_SHARED_DISK_PATH}/{checkpointfile_name}"
        else: # external storage image repositary
            target_path = ""

        # Send request to migration excutor in migration source worker nodes
        data = {
            "checkpointfile_path": checkpointfile_source_path,
            "migrate_method": self.info['migrate_method'],
            "target_ip": self.info['target_ip'],
            "targetfile_path": self.info['target_path'],
            "container_name": self.info['container_name']
        }
        headers = {
            "Content-Type": "application/json"
        }
        url = f"http://{self.info['source_ip']}:8052/checkpoint"
        res = requests.post(url, data=json.dumps(data), headers=headers)

        return target_path 