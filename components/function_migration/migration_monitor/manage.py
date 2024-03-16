'''
Entry to the migration monitor, run manage.py on the master node to 
start the migration monitor.
'''
from flask import Flask, request, jsonify

from .app import MigrationMonitor

# init flask app and MonitorMonitor class
app = Flask(__name__)
MM = MigrationMonitor()

@app.route('/node_pods_utilization',methods=['GET'])
def node_pod_cpu_utilization():
    """Interface to search the glabal cpu and memory usage of functions in one worker node"""
    return jsonify(MM.node_pod_cpu_utilization(request.remote_addr)),200

@app.route('/nodes_utilization',methods=['GET'])
def global_cpu_utilization():
    """Interface to search the glabal cpu and memory usage of all worker nodes in cluster"""
    return jsonify(MM.global_cpu_utilization()),200

@app.route('/node_pod_num',methods=['GET'])
def node_pod_num():
    """Interface to search the number of functions in one worker node"""
    return jsonify(MM.node_pod_num(request.remote_addr)),200

@app.route('/global_node_pod_num',methods=['GET'])
def global_node_pod_num():
    """Interface to search the number of functions in all worker nodes"""
    return jsonify(MM.global_node_pod_num()),200

@app.route('/function_recent_call_times/<function_name>',methods=['GET'])
def function_recent_call_times(function_name):
    """Interface to search the call times of one function"""
    return jsonify(MM.function_recent_call_times(function_name)),200   

if __name__ == '__main__': 
    app.run(port=8055) # run flask app
