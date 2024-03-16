"""
Entry to the migration excutor, run manage.py locally on the worker node to 
start the migration decision-maker on that node   
"""

from flask import Flask, request, jsonify

from .app import CheckpointExcutor
from .app import RestoreExcutor

app = Flask(__name__)

@app.route('/checkpoint', methods=['POST'])
def checkpoint():
    '''Complete the sending of function running status checkpoints on the work node in the CHECKPOINT process.'''
    return jsonify(CheckpointExcutor(request.get_json())),200

@app.route('/restore', methods=['POST'])
def restore():
    '''Complete the acquisition of the function running state image on the work node during the RESTORE process.'''
    return jsonify(RestoreExcutor(request.get_json())),200

if __name__ == '__main__':
    app.run(port=8052) # Run flask app
