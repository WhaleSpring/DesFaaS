# config.py

# IP adrress, mechine name and phisical structure of worker VM's mechines 
MASTRE_IP = "192.168.0.10"
CLUSTER_CONFIG = {
    "192.168.0.11":"worker1",
    "192.168.0.12":"worker2",
    "192.168.0.13":"worker3",
    "192.168.0.14":"worker4",
}
CLUSTER_SETTINGS = {
    '192.168.0.11':['wroker1',1],
    '192.168.0.12':['wroker2',1],
    '192.168.0.13':['wroker3',2],
    '192.168.0.14':['wroker4',2],
}


# cluster interfaces config
NAMESPACE = "openfaas-fn"
PROMETHEUM = "192.168.0.10:31112"

FUNCTION_CONFIG_PATH = ""

WORKER_NODES_USERNAME = ""
WORKER_NODES_PASSWORD = ""
WORKER_NODES_PORT = 22

WORKER_STATE_DISK_PATH = ""
WORKER_CHECKPOINT_DISK_PATH = ""

EXTERNAL_IMAGE_STORAGE = ""

EXTERNAL_STATE_SERVER_IP = ""
EXTERNAL_STATE_SERVER_USERNAME = ""
EXTERNAL_STATE_SERVER_PASSWORD = ""
PORT = 22
EXTERNAL_STATE_SERVER_STORAGE_PATH = ""


# Scheduling Strategy
TOTAL_CPU_N = 8 * 10**9     # CPU quantity in one virtual mechines
TOTAL_MEM_K = 16*1024*1024  # MEM quantity in one virtual mechines