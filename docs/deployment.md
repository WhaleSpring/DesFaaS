# Infrastructure Config
## Python Enviroment

Python3.10 should be installed to support the running of DesFaaS in master VM and worker VMs, and related dependencies should be installed. In master VM, the dependencies is in [requirements_master.txt](https://github.com/WhaleSpring/DesFaaS/blob/main/components/requirements_master.txt), while worker VMs in [requirements_worker.txt](https://github.com/WhaleSpring/DesFaaS/blob/main/components/requirements_worker.txt)

## Worker VMs

To run DesFaaS, every worker VM needs to meet such conditions:
- CRI-O is deployed as the basic container runtime. 
- The checkpoint/restore(C/R) capacity of CRI-O is active.
- CRI-O version is greater than 1.25 .
- Buildah tool is installed as image build tool.
- Shared disk among VMs of one physical mechines is configured.

## Kubernetes 

To run DesFaaS, kubernetes cluster needs to meet such conditions:
- OpenFaaS is deployed as the basic serverless runtime.
- CAdvisor, Node-exporter, Kube-metrics and Promethues is deployed and configured to monitor cluster information DesFaaS requires.
- The checkpoint capacity of Kubernetes is active.
- Kubernetes version is greater than 1.25 .

## External Infrastructure

Desfaas requires the following external infrastructure:
- Disk of a external server is required as state external storage.
- A external image repository is requied as external storage of funtion runtime image.

# DesFaaS Config

You need to modify the config.py to meet your cluster and other infrastructures which DesFaaS relies. 


| Global Variable Name | Meaning | Type |
|---|---|---|
|MASTRE_IP| The ip address of master node of kubernetes|string|
|CLUSTER_CONFIG|The ip and corresponding server name of worker nodes|dict|
|CLUSTER_SETTINGS|The shared disk config about with CLUSTER_CONFIG|dict|
|NAMESPACE|The kubernetes namespace where the stateful functions is running|string|
| PROMETHEUM | The path of promethues | string |
| FUNCTION_CONFIG_PATH | The path of OpenFaaS stateful function config yaml file | string |
|FUNCTION_CONFIG_PATH|the path to store the OpenFaaS yaml files|string|
|WORKER_NODES_USERNAME|The user name of worker nodes|string|
|WORKER_NODES_PASSWORD|The password of worker nodes|string|
|WORKER_NODES_PORT|The ssh connection port of worker nodes|int|
|WORKER_STATE_DISK_PATH |The shared disk path in worker nodes|string|
|WORKER_CHECKPOINT_DISK_PATH |The path to store checkpoint file in worker nodes|string|
|EXTERNAL_IMAGE_STORAGE| The url of external image storage| string |
|EXTERNAL_STATE_SERVER_IP| The ip of state external storage server|string|  
|EXTERNAL_STATE_SERVER_USERNAME| The username of state external storage server|string|  
|EXTERNAL_STATE_SERVER_PASSWORD|The password of state external storage server|string|  
|PORT|The ssh port of state external storage server|int|  
|EXTERNAL_STATE_SERVER_STORAGE_PATH|The storege path of state external storage server|string|  


# DesFaaS Deployment

After completing the above configuration, DesFaaS can be used. You need to copy the modified source code of DesFaaS to master VM and each worker VM, and run the components of DesFaaS on the corresponding ports in corresponding VM:
|conponent name|port|Introduction|runnning location|
|--|--|--|--|
|state monitor|8053|Monitor and schedule global state messages.|master VM|
|state manager|8054|Manage local state replicas.|worker VM|
|migration monitor|8055|Monitor cluster and function information.|master VM|
|migration decision-maker|/|Make migration decisions for local functions.|worker VM|
|migration scheduler|8051|Coordinate the entire process of migration decisions.|master VM|
|migration excutor|8052|Perform specific migration operations on the worker nodes.|worker VM|