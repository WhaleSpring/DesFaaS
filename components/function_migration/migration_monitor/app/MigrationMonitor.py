"""MigrationMonitor() class to provide messages for making migration decisions.

Typical usage example:

  mm = MigrationMonitor()
"""
import time

from app import K8S
from app import CAdvisor
from app import PromQL

# config.py
WORKER_CHECKPOINT_DISK_PATH = ""
WORKER_SHARED_DISK_PATH = ""
CLUSTER_CONFIG = {}
NAMESPACE = "openfaas-fn"
PROMETHEUS = '100.64.217.134:31119'

class MigrationMonitor:
    """The concrete implementation of migration monitor.

    Attributes:
        k8s: kubernetes cluster API
        promQL: promethues API
    """

    def __init__(self):
        """Initial MigrationMonitor class and create k8s and promQL objects."""
        self.k8s = K8S()
        self.promQL = PromQL(PROMETHEUS)

    def node_pod_cpu_utilization(self,node_ip):
        """Get the cpu and memory usage of all functions in designative worker VM.

        Args:
            node_ip (string): the ip address where request comes from  

        Returns:
            A dict with the above messages. For example:

            {
                "function_1" : [ "CPU" : 999, "MEM" : 999 ]
                "function_2" : [ "CPU" : 999, "MEM" : 999 ]
            }
        """
        # Get detailed information from k8s cluster API
        node_name = CLUSTER_CONFIG[node_ip]
        formatted_data = self.format_pod_metrics(self.k8s.get_pod_metrics(NAMESPACE))
        pod_list = self.k8s.get_pod_list()
        pods_data = [] 

        # Filter information we need
        for pod_msg in formatted_data:
            if pod_list[pod_msg["Pod Name"]] == node_name :
                pods_data.append(pod_msg)
        return pods_data

    def global_cpu_utilization(self):
        """Get the cpu and memory usage of all worker nodes in cluster.

        Returns:
            A dict with the above messages. For example:

            {
                "worker1" : { "CPU" : 999, "MEM" : 999 }
                "worker2" : { "CPU" : 999, "MEM" : 999 }
            }
        """
        return self.format_pod_metrics(self.k8s.get_pod_metrics(NAMESPACE))

    def global_node_pod_num(self):
        """Get the function numbers of all worker nodes.

        Returns:
            An int number list about the function number.
        """
        pod_num_list = []
        for node_ip in CLUSTER_CONFIG.keys():
            pod_num_list.append(self.node_pod_num(node_ip))
        return pod_num_list

    def node_pod_num(self,node_ip):
        """Get the function number of designative worker node.

        Args:
            node_ip (string): the ip address where request comes from  

        Returns:
            An int number about the function number.
        """
        pod_list = self.k8s.get_pod_list(NAMESPACE)
        pod_num = 0
        for pod in pod_list.items:
            if pod.spec.node_name == CLUSTER_CONFIG[node_ip]:
                pod_num += 1
        return pod_num

    def function_recent_call_times(self,function_name):
        """Get the function recent call time of designative function.

        Args:
            function_name (string): the designative function  

        Returns:
            An int number about the function number.
        """
        cadvisor = CAdvisor(self.promQL)
        time_now = cadvisor.get_function_invocated_times(function_name,time.time())
        time_before = cadvisor.get_function_invocated_times(function_name,time.time()-600)

        return time_now[0][1] - time_before[0][1]


    def format_node_metrics(self,metrics_data):
        """Select the data we need from k8s metrics.

        Args:
            metrics_data (dict): nodes information from k8s API

        Returns:
            A dict containing formatted data.
        """
        formatted_data = []
        for node_metrics in metrics_data.get('items', []):
            # Get data we need
            node_name = node_metrics['metadata']['name']
            cpu_usage = node_metrics['usage']['cpu']
            memory_usage = node_metrics['usage']['memory']
            cpu_usage,memory_usage = self.remove_unit(cpu_usage,memory_usage)
            
            # construct formatted data dict
            formatted_data.append({
                'Node Name': node_name,
                'CPU Usage': cpu_usage,
                'Memory Usage': memory_usage
            })
        return formatted_data

    def remove_unit(self,cpu_str, memory_str):
        """Unified the unit of CPU and memory.

        Because the CPU and memory metrics provided by the k8sAPI may have different data units, 
        a uniform unit is required. Here we unify CPU usage in nanoseconds and memory in KiB/s.

        Args:
            cpu_str (str): raw CPU data
            memory_str (str): raw memory data

        Returns:
            cpu_value (int): CPU usage value after process
            memory_value (int): memory usage value after process
        """
        # CPU
        if cpu_str.endswith('n'):
            cpu_value = int(cpu_str[:-1]) #  ns
        elif cpu_str.endswith('u'):
            cpu_value = int(cpu_str[:-1]) * 1000  # Chaneg μs to ns
        elif cpu_str.endswith('m'):
            cpu_value = int(cpu_str[:-1]) * 1000000  # Change ms to ns
        else:
            cpu_value = int(cpu_str) * 1000000000  # Change s to ns
        
        # Memory
        if memory_str.endswith('Ki'):
            memory_value = int(memory_str[:-2]) # KiB
        elif memory_str.endswith('Mi'):
            memory_value = int(memory_str[:-2]) * 1024  # change MiB to KiB
        else:
            memory_value = int(memory_str) # KiB

        return cpu_value, memory_value