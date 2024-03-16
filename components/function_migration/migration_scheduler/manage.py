'''
Entry to the migration scheduler, run manage.py on the master node to 
start the migration scheduler.
'''
from flask import Flask, request, jsonify
import queue
import time

from .app import CheckpointManager
from .app import RestoreManager
from .app import MigrationScheduler

# Initialize the global dependency
app = Flask(__name__)
MS = MigrationScheduler()
PENDING_CHECKPOINTS = queue.Queue()
PENDING_RESTORES = queue.Queue()

def process_checkpoint():
    """Checkpoint procedure processing thread"""
    while True:
        try:
            # Get a checkpoint decision
            checkpoint_operation = PENDING_CHECKPOINTS.get()
            
            # Process the decision
            restore_info = CheckpointManager(checkpoint_operation)
            
            # Put the decision into restore queue
            PENDING_RESTORES.put(restore_info)
        except Exception as e:
            print(f"Thread error: {e}") # Error handling
        time.sleep(0.5)

def process_restore():
    """Restore procedure processing thread"""
    while True:
        try:
            # Get a restore decision
            restore_operation = PENDING_RESTORES.get()
            
            # Process the decision
            RestoreManager(restore_operation)
        except Exception as e:
            print(f"Thread error: {e}") # Error handling
        time.sleep(0.5)

@app.route('/descision_request', methods=['POST'])
def descision_request():
    """Receive function migration decision from migration decision-maker and put it 
    into PENDING_CHECKPOINTS queue waiting for excuting."""
    return jsonify(PENDING_CHECKPOINTS.put(MS.checkpoint_info_build(request.get_json()))),200

if __name__ == '__main__':
    # Run 2 prcessing threadings.
    MS.run_thread(process_checkpoint)
    MS.run_thread(process_restore)
    
    # Run flask app.
    app.run(port=8051)
