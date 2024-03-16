"""K8S() class to provide API to aquire k8s merics messages.

Typical usage example:

  k8s = K8S()
  node_metrics = k8s.get_node_metrics()
  pod_list = k8s.get_pod_list()
"""
from kubernetes import client, config

# config.py
NAMESPACE = "openfaas-fn"

class K8S:
    """The concrete implementation to access kubernetes metrics API."""

    def __init__(self):
        """Initial K8S class and load the config file of kubernetes."""
        config.load_kube_config()

    def get_node_metrics(self):
        """Get the node metrics from kubernetes metrics API.

        Returns:
            A dict containing all nodes messages.
        """
        api_instance = client.CustomObjectsApi()
        group = "metrics.k8s.io"
        version = "v1beta1"
        resource = "nodes"
        nodes_metrics = api_instance.list_cluster_custom_object(group, version, resource)
        return nodes_metrics

    def get_pod_list(self):
        """Get the pods metrics from kubernetes metrics API.

        Returns:
            A dict containing all pods messages.
        """
        # Load all messages.
        config.load_kube_config()
        api = client.CoreV1Api()
        pod_list = api.list_namespaced_pod(namespace=NAMESPACE, watch=False)
        
        # Format the messages we need.
        formatted_pod_list = {}
        for pod in pod_list.items:
            pod_name = pod.metadata.name
            node_name = pod.spec.node_name
            formatted_pod_list[pod_name]=node_name
        return formatted_pod_list