"""MigrationScheduler() class will be used to build checkpoint image and run management threads.

Typical usage example:

    ms = MigrationScheduler(msg)
    
"""
from kubernetes import client, config
import threading

# config.py
CLUSTER_CONFIG = {}
NAMESPACE = "openfaas-fn"

class MigrationScheduler:
    """The concrete implementation of some operations about miragtion scheduling."""

    def __init__(self):
        """Initial MigrationScheduler class."""
        pass

    def checkpoint_info_build(self,msg):
        """Build checkpoint decision information acording the requests from migration decision.

        Args:
            msg: target_ip, source_ip, migrate_method, pod_name, migrate_method

        Returen:
            a dict containing all messages to support a migration process.
        """
        # Get target node name and container name
        target_node_name = CLUSTER_CONFIG[msg["target_ip"]]
        config.load_kube_config()
        api = client.CoreV1Api()
        container_name = api.read_namespaced_pod(msg['pod_name'], NAMESPACE).spec.containers[0].name
        
        # construct the checkpoint information
        checkpoint_info = {
            'source_ip': msg['source_ip'],
            'target_ip': msg['target_ip'],
            'pod_name': msg['pod_name'],
            'migrate_method': msg['migrate_method'],
            'container_name': container_name,
            'target_node_name': target_node_name
        }
        return checkpoint_info

    def run_thread(self,thread_function):
        """Run a thread to process the messages in checkpoint and restore queues."""
        thread = threading.Thread(target=thread_function)
        thread.daemon = True
        thread.start()
