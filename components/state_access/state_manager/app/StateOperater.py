"""StateOperater() class aims to provide ability to help StateManager to manage states.

Typical usage example:

    sm = StateOperater()
    sm.get_node_ip()
"""
import json
import threading
import requests
import psutil

from app import StateFileManager

# config.py
WORKER_STATE_DISK_PATH = ""
MASTER_IP = ""
PORT = 22
EXTERNAL_STATE_SERVER_IP = ""
EXTERNAL_STATE_SERVER_USERNAME = ""
EXTERNAL_STATE_SERVER_PASSWORD = ""
EXTERNAL_STATE_SERVER_STORAGE_PATH = ""
WORKER_STATE_DISK_PATH = ""

class StateOperater:
    """Help StateManager to manage states.
    
    Atributes:
        node_ip: local ip address
    """

    def __init__(self):
        """Initial the StateOperater class."""
        self.node_ip = self.get_node_ip()
    
    def get_node_ip(self):
        """Get local ip address.
        
        Returns:
            node_ip(string)
        """
        interfaces = psutil.net_if_addrs()
        interface_name = "enp0s8" 
        interface = interfaces.get(interface_name)
        node_ip = interface[0][1] 
        return node_ip

    def save_dict_to_file(self,function_name, state_data):
        """Save specific state replica from memory to local disk.

        Args:
            function_name: state which will be saved to disk.
        """
        filename = f"{WORKER_STATE_DISK_PATH}/{function_name}.json"
        with open(filename, 'w') as file:
            json.dump(state_data, file)

    def run_thread(self,thread_function):
        """Run a thread to help management."""
        thread = threading.Thread(target=thread_function)
        thread.daemon = True
        thread.start()

    def state_new_tell_monitor(self,function_name):
        """Tell monitor when creating a new state replica in state manager.
        
        Args:
            function_name: state newly created.
        """
        url = f'http://{MASTER_IP}:8053/state_change/add/{function_name}'
        res = requests.post(url)

    def activity_update_tell(self,function_name,activity_temp):
        """Tell monitor to update the temperate of states.
        
        Args:
            function_name: state whose temperature is changed
            activity_temp: new temperature
        """
        url = f"http://{MASTER_IP}:8053/activity_change/{function_name}/{activity_temp}"
        res = requests.post(url) 

    def state_lock_of_other_nodes(self,function_name):
        """Tell other nodes to lock their state with pointed state name.
        
        Args:
            function_name: state locked
        """
        # Search all replicas' locations
        url = f"http://{MASTER_IP}:8053/state_search_all/{function_name}"
        res = requests.get(url) 
        nodes_list = res.json()

        # Send lock requests to other nodes
        data = {"locked": 1 , "identity": 0 }
        for node_ip in nodes_list:
            if (not node_ip == self.node_ip) and (not node_ip == "externalstorage") :
                url = f"http://{node_ip}:8054/state_read/{function_name}"
                requests.get(url,json=data)

    def state_unlock_of_other_nodes(self,function_name,state_data):
        """Tell other nodes to update and unlock their state with pointed state name.
        
        Args:
            function_name: state locked
            state_data: the new updated value of state data 
        """
        # Search all replicas' locations
        url = f"http://{MASTER_IP}:8053/state_search_all/{function_name}"
        res = requests.get(url) 
        nodes_list = res.json()

        # Send requests to other nodes
        data = {"state_data" : state_data,"identity": 0 }
        for node_ip in nodes_list:
            if (not node_ip == self.node_ip) and (not node_ip == "externalstorage") : # 筛去自己和外部存储
                url = f"http://{node_ip}:8054/state_write/{function_name}"
                requests.post(url,json=data)

    def state_move_to_external_storage(self,function_name,state_data):
        """Move state from memory to external storage.
        
        Args:
            function_name: the state name which will be moved.
            state_data: the moved data value
        """
        self.save_dict_to_file(function_name, state_data)
        sfm = StateFileManager(EXTERNAL_STATE_SERVER_IP,EXTERNAL_STATE_SERVER_USERNAME,EXTERNAL_STATE_SERVER_PASSWORD)
        sfm.file_send(f"{WORKER_STATE_DISK_PATH}/{function_name}.json",f"{EXTERNAL_STATE_SERVER_STORAGE_PATH }/{function_name}.json")
        sfm.close()

    def state_move_to_external_storage_from_disk(self,function_name):
        """Move state from local disk to external storage.
        
        Args:
            function_name: the state name which will be moved.
        """
        sfm = StateFileManager(EXTERNAL_STATE_SERVER_IP,EXTERNAL_STATE_SERVER_USERNAME,EXTERNAL_STATE_SERVER_PASSWORD)
        sfm.file_send(f"{WORKER_STATE_DISK_PATH}/{function_name}.json",f"{EXTERNAL_STATE_SERVER_STORAGE_PATH}/{function_name}.json")
        sfm.close()

    def state_delete_tell_monitor(self,function_name):
        """Tell monitor that the removing operation has been completed ."""
        url = f'http://{MASTER_IP}:8053/state_change/delete/{function_name}'
        res = requests.post(url)
    
    def state_pull_from_other_nodes(self,function_name):
        """Pull a state from other nodes or external storage.
        
        Args:
            function name: the state name which will be pulled.

        Returns:
            state data pulled from other locations.
        """
        # Search master state location or external storage
        url = f"http://{MASTER_IP}:8053/state_search/{function_name}"
        res = requests.get(url) 
        node_ip = res.json()

        # State in external storage
        if node_ip == "externalstorage":
            # Pull state
            sfm = StateFileManager(EXTERNAL_STATE_SERVER_IP,EXTERNAL_STATE_SERVER_USERNAME,EXTERNAL_STATE_SERVER_PASSWORD)
            sfm.file_pull(EXTERNAL_STATE_SERVER_STORAGE_PATH,WORKER_STATE_DISK_PATH) 
            sfm.close()
            state_data = self.state_load_from_local_disk(function_name) 

            # Remove state in external storage
            self.state_externalstorage_delete(function_name)

        # State in other worker nodes
        else:
            # Send a request to state manager which managing state we want.
            data = {
                "locked": 0 ,
                "identity": 0 
            }
            url = f"http://{node_ip}:8054/state_read/{function_name}"
            state_data = requests.get(url,json=data)

        return state_data.json()

    def state_load_from_local_disk(function_name):
        """Load state from local disk to local memory.
        
        Args:
            function_name: the state name which will be loaded.
        """
        with open(f"{WORKER_STATE_DISK_PATH}/{function_name}.json", 'r') as json_file:
            return json.load(json_file)

    def get_memory_utilization():
        """Acquire the local memory utilization.
        
        Rertun:
            a float number to describe the memory utilization.
        """
        memory_info = psutil.virtual_memory()
        memory_percent = memory_info.percent
        return memory_percent

    def state_externalstorage_delete(function_name):
        """Remove a state replica in external storage

        Args:
            function_name: the removed state's name
        """
        sfm = StateFileManager(EXTERNAL_STATE_SERVER_IP,EXTERNAL_STATE_SERVER_USERNAME,EXTERNAL_STATE_SERVER_PASSWORD)
        delete_command = f"rm  -rf {EXTERNAL_STATE_SERVER_STORAGE_PATH}/{function_name}.json"
        stdin, stdout, stderr = sfm.ssh.exec_command(delete_command)
        sfm.close()