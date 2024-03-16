"""StateOperater() class aims to help StateMonitor complete detailed operations.

Typical usage example:

    sm = StateOperater()
    sm.state_messages_init()
"""
import requests
import json
import threading

CLUSTER_CONFIG = {}

class StateOperater:
    """Help StateMonitor complete detailed operations about accessing state manager in worker
    VMs and managing the monitoring dicts"""

    def __init__(self):
        """Initial the StateOperater class."""
        pass

    def state_messages_init():
        """Initial the messages dict in state monitor from the state managers in worker VMs.
        
        Returns:
            A dict containing the messages from every worker VM.
        """
        messages_dict = {}
        for node_ip in CLUSTER_CONFIG:
            url = f'http://{node_ip}:8054/state_monitor_get'
            res = requests.get(url)
            messages_dict[node_ip] = json.loads(res.text)
        return messages_dict

    def run_thread(thread_function):
        """Run a threading."""
        thread = threading.Thread(target=thread_function)
        thread.daemon = True
        thread.start()

    def state_remove(function_name,node_name,remove_type):
        """Send a request to a state manager in worker VM in order to remove a specific state 
        replica.
        
        Args:
            function_name(str): the searched state name of corresponding function.
            node_name(str) : the ip address of the state manager in worker VM.
            remove type(int): 0 represents just removing the replica, whiile 1 represents
                    removing the replica after moving it to external storage.
        """
        data = {'type': remove_type}
        url = f'http://{node_name}:8054/state_remove/{function_name}'
        res = requests.post(url, json=data)

    def state_read(function_name,data,ip):
        """Send a request to a state manager in worker VM to read a state.

        Read the state by state monitor for node "ip" to pull the specific state from other
        VM to node "ip".
        
        Args:
            function_name(str): the searched state name of corresponding function.
            ip(str) : the ip address of the state manager in worker VM.
            data(dict): the request messages sent to the state manager in worker VM.
        """
        url = f'http://{ip}:8054/state_read/{function_name}'
        res = requests.get(url, json=data)