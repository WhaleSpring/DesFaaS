'''
Entry to the state manager, run manage.py on every worker node to start the state managers.

The state manager takes charge in the local state management among 3 storage layers, and communicate
with global state monitor and state managers in other worker nodes to achieve the state scheduling.
'''
from flask import Flask, request, jsonify

from .app import StateManager

app = Flask(__name__)
SM = StateManager()

@app.route('/state_memory_get',methods=['GET'])
def state_memory_get():
    """The interface to get all the state replicas in memory locally managed by the state manager."""
    return jsonify(SM.memory_state_storage)

@app.route('/state_lock_get',methods=['GET'])
def state_lock_get():
    """The interface to get all the state locks  locally managed by the state manager."""
    return jsonify(SM.state_lock_get()),200

@app.route('/state_access_time_get',methods=['GET'])
def state_access_time_get():
    """The interface to get all the times of state replicas locally managed by the state manager."""
    return jsonify(SM.state_access_time)

@app.route('/state_create/<function_name>',methods=['POST'])
def state_create(function_name):
    """The interface to create a state replica locally."""
    return jsonify(SM.state_create(function_name,request.get_json()['value'])) , 200

@app.route('/state_monitor_get',methods=['GET'])
def state_monitor_get():
    """The interface for state monitor to get the state list in the state manager"""
    return jsonify(SM.state_monitor_get()),200

@app.route('/state_read/<function_name>',methods=['GET'])
def state_read(function_name):
    """The interface for serverless stateful functions to read a specific state replica."""
    return jsonify(SM.state_read(function_name,request.get_json()['locked'],request.get_json()['identity'])),200

@app.route('/state_write/<function_name>',methods=['POST'])
def state_write(function_name):
    """The interface for serverless stateful functions to write a specific state replica."""
    return jsonify(SM.state_write(function_name,request.get_json()['identity'],request.get_json()['state_data'])),200

@app.route('/state_remove/<function_name>',methods=['POST'])
def state_remove(function_name):
    """The interface to remove a local state."""
    return jsonify(SM.state_remove(function_name,request.get_json()['type'])),200

@app.route('/state_size',methods=['GET'])
def state_size():
    """The interface to acquire the sum storage cost of state replicas in memory"""
    return jsonify(SM.state_size()),200

if __name__ == '__main__': 
    SM.so.run_thread(SM.state_activity_change) # Run temperature management thread 
    SM.so.run_thread(SM.state_semi_activity_manager) # Run warm state daya management thread
    app.run(port=8054) # Run flask app