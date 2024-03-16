'''
Entry to the state monitor, run manage.py on the master node to start the state monitor.

Loggically, the state monitor's implementation is playing the role of state monitor, state
scheduler and consistency manager.
'''
from flask import Flask, request, jsonify

from .app import StateMonitor

app = Flask(__name__)
SM = StateMonitor()

@app.route('/state_search/<function_name>',methods=['GET'])
def state_search(function_name):
    """Search the master state replica of the specific function_name."""
    return jsonify(SM.state_search(function_name)),200

@app.route('/state_search_all/<function_name>',methods=['GET'])
def state_search_all(function_name):
    """Search all master and slave state replicas of the specific function_name."""
    return jsonify(SM.state_search_all(function_name)),200
    
@app.route('/state_change/<change_type>/<function_name>',methods=['POST'])
def state_change(change_type,function_name):
    """Update the monitor dict about the state replicas information in state monitor."""
    return jsonify(SM.state_change(request.remote_addr,change_type,function_name)),200

@app.route('/activity_change/<function_name>/<activity>',methods=['POST'])
def activity_schange(activity,function_name):
    """Update the monitor dict about the state replica's data temperature information in state monitor."""
    return jsonify(SM.activity_schange(request.remote_addr,activity,function_name)),200

@app.route('/function_infomation_acquisition/<function_name>',methods=['POST'])
def function_infomation_acquisition(function_name):
    """Get all messages stored in state monitor about specific function"""
    return jsonify(SM.function_infomation_acquisition(function_name)),200

@app.route('/state_migration/<function_name>',methods=['POST'])
def state_migration(function_name):
    """Migrate a state replica from one worker VM to anoter one."""
    return jsonify(SM.state_migration(request.get_json(),function_name)),200

@app.route('/primary_state_search/<function_name>',methods=['GET'])
def primary_state_search(function_name):
    """Search the primary position of the specific function_name"""
    return jsonify(SM.settings[function_name]["primary"]),200

if __name__ == '__main__':
    SM.messages = SM.so.state_messages_init() # initial the state monitoring dict
    SM.so.run_thread(SM.state_remove_from_nodes)  # run the thread to manage cold state replicas
    app.run(port=8053) # run flask app