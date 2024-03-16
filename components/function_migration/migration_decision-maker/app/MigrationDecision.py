"""MigrationDecision() class to help make migration descision in a worker VM.

Typical usage example:

  md = MigrationDecision()
  md.migration_decision_algorithm_cpu_utilization()
"""

import psutil
import requests
import json
import time

# config.py
MASTER_IP = ""
CLUSTER_SETTING = {}
MASTER_IP = "100.64.217.134"
CLUSTER_SETTINGS = {}
TOTAL_CPU_N = 8 * 10**9  
TOTAL_MEM_K = 16*1024*1024 

# Algorithm parameters
CPU_UTILIZATION_UPPER_THRESHOLD = 0.8   # Threshold to judge resource overhead
CPU_UTILIZATION_LOWER_THRESHOLD = 0.2   # Threshold to judge resource wastage
FUNCTION_CALL_TIMES_THRESHOLD = 30

class MigrationDecision:    
    """The concrete implementation of migration-decision maker.

    Attributes:
        node_ip: Local ip address
    """

    def __init__(self):
        """Initial MigrationDecision class."""
        self.node_ip = self.get_NodeIP() # Record local ip address. 

    def migration_decision_algorithm_cpu_utilization(self):
        """Migration decision algorithm based on CPU utilization."""
        while True:
            # Get global resource information.
            utilizations = self.get_global_utilization()
            local_utilization = self.get_local_utilization(utilizations)
            
            # Judge whether occuring resource wastage or overhead.
            if local_utilization["CPU Usage"]/TOTAL_CPU_N >= CPU_UTILIZATION_UPPER_THRESHOLD :
                
                pods_utilization = self.get_local_pods_list() # Get local pods information.
                
                while local_utilization["CPU Usage"]/TOTAL_CPU_N >= CPU_UTILIZATION_UPPER_THRESHOLD : # Migrate functions until local resource usage to be normal.
                    removed_pod = self.select_removed_pod(pods_utilization) # Select a function to be migrated
                    
                    # Select a VM as migration target.
                    for utilization in utilizations: 
                        if (not utilization['Node Name']==CLUSTER_SETTINGS[self.node_ip][0])and(not utilization['Node Name']=="exp-master") and (utilization["CPU Usage"] + removed_pod["CPU Usage"] < CPU_UTILIZATION_UPPER_THRESHOLD) and (utilization["Memory Usage"] + removed_pod["Memory Usage"] < TOTAL_MEM_K):
                            # Adjust resource config after migration.
                            utilization["CPU Usage"] +=  removed_pod["CPU Usage"]
                            utilization["Memory Usage"] +=  removed_pod["Memory Usage"]
                            local_utilization["CPU Usage"] -=  removed_pod["CPU Usage"]
                            local_utilization["Memory Usage"] -=  removed_pod["Memory Usage"]

                            # Make and send migration decision.
                            target_ip = self.get_target_ip(utilization['Node Name'])
                            migrate_type = self.get_migration_type(target_ip,removed_pod)            
                            self.send_migrate_decision(target_ip,removed_pod,migrate_type)
                            break

                    pods_utilization.remove(removed_pod) # Remove the function migrated.

            elif local_utilization["CPU Usage"]/TOTAL_CPU_N <= CPU_UTILIZATION_UPPER_THRESHOLD  :
                pass
            
            time.sleep(300) # The migration algorithm will run once every 5 minutes.

    def get_NodeIP(self):
        """Get local ip address.

        Aquire local ip according to psutil to read the local network config, andget ip address. It's worth 
        montioning that the network card name should be adjusted dynimically in terms of specific network config. 
        In the paper of DesFaaS, we use "enp0s0" as virtual network card.

        Returns:
            A string to describe local ip address. For example:

            "192.168.0.11"
        """        
        interfaces = psutil.net_if_addrs()
        interface_name = "enp0s8" 
        interface = interfaces.get(interface_name)
        return interface[0][1] 

    def get_global_utilization(self):
        """Get global resource utilization about CPU and memory.

        Aquire CPU and memory utilization of all worker VMs in the cluster. We will send a request to migration 
        monitor of DesFaaS to get the above messages.

        Returns:
            A dict to describe the above messages. For example

            {
                "worker1" : { "CPU" : 999, "MEM" : 999 }
                "worker2" : { "CPU" : 999, "MEM" : 999 }
            }
        """        
        url = f"http://{MASTER_IP}:8055/nodes_utilization" 
        return json.loads(requests.get(url).text)

    def get_local_utilization(self,utilizations):
        """Get local resource utilization about CPU and memory.

        According global resource utilization condition, select local one according to the local ip address.

        Args:
            utilizations: the result dict aquired by MigrationDecision.get_global_utilization()  

        Returns:
            A dict to describe the above messages. For example

            { "CPU" : 999, "MEM" : 999 }
        """        
        local_utilization = {}
        for utilization in utilizations:
            if utilization['Node Name']==CLUSTER_SETTING[self.node_ip][0]:
                local_utilization = utilization
                break
        return local_utilization

    def get_local_pods_list(self):
        """Get local pods list and related resource usage conditions.

        Aquire CPU and memory utilization of all local functions. We will send a request to migration 
        monitor of DesFaaS to get the above messages.    

        Returns:
            A dict to describe the above messages. For example:

            {
                "function_1" : { "CPU" : 999, "MEM" : 999 }
                "function_2" : { "CPU" : 999, "MEM" : 999 }
            }
        """  
        url = f"http://{MASTER_IP}:8055/node_pods_utilization"
        return json.loads(requests.get(url).text)

    def get_removed_pod(self,pods_utilization):
        """Select a function's pod to be migrated. 

        Select a pod with max CPU usage in pods_utilization.

        Args:
            pods_utilization: the result dict aquired by MigrationDecision.get_local_pods_list()

        Returns:
            A subdict to describe the pod selected. For example:

            {} "CPU" : 999, "MEM" : 999 }
        """        
        removed_pod = {"CPU Usage":-1}
        for pod_utilization in pods_utilization:
            if pod_utilization["CPU Usage"]>removed_pod["CPU Usage"]:
                removed_pod = pod_utilization
        return removed_pod

    def get_target_ip(self,node_name):
        """Search the corresponding VM ip address by its name. 

        Args:
            node_name: the node name we want to get its ip.

        Returns:
            A string descrbing the corresponding ip address. For example:

            "192.168.0.11"
        """                
        for key, value in CLUSTER_SETTING.items():
            if value[0] == node_name:
                return key
    
    def get_migration_type(self,target_ip,removed_pod):
        """Decide the migration medium about the selected function.

        We will send a request to migration monitor to get the recent call time for the
        removed funtion. And if the call time is too low, choosing external storage, and
        if existing shared disk between source and target, choosing shared disk.Otherwise,
        network.

        Args:
            target_ip: the target VM in this migration 
            removed_pod: the pod name the selected function corresponding

        Returns:
            A int number to describe the migration type. 0 stands for "network", 1 stands 
            for "external storage", and 2 stands for "shared disk".
        """               
        url = f'http://{MASTER_IP}:8055/function_recent_call_times/{removed_pod["Pod Name"]}'
        recent_call_times = json.loads(requests.get(url).text)

        if recent_call_times < FUNCTION_CALL_TIMES_THRESHOLD : 
            migrate_type = 1
        elif CLUSTER_SETTING[target_ip][1]==CLUSTER_SETTING[self.node_ip]:
            migrate_type = 2
        else :
            migrate_type = 0
        return migrate_type

    def send_migrate_decision(self,target_ip,removed_pod,migrate_type):
        """Generate and send migration decision to migration scheduler.

        Args:
            target_ip: the target VM in this migration 
            removed_pod: the pod name the selected function corresponding
            migrate_type: the migration medium selected
        """       
        url = 'http://100.64.217.134:8051/MigrationDecisionAcquisition'
        data = {
            "source_ip": self.node_ip, # local ip address
            "target_ip": target_ip,
            "pod_name": removed_pod['Pod Name'],
            "migrate_type": migrate_type
        }
        res = requests.post(url, json=data)