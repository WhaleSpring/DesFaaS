"""StateManager() class aims to provide the interfaces to manage the states in worker VMs.

Typical usage example:

    sm = StateManager()
    sm.state_lock_get()
"""
import time
import threading
import sys
import os
import psutil

from app import StateOperater
from app import StateFileManager

# config.py
WORKER_STATE_DISK_PATH = ""

class StateManager:
    """Manage the state monitor data and provide scheduling ability about the monitored data.

    Attributes:
        memory_state_storage: a dict with state replica's name as keys and the state value as
                values.
        state_access_time: a dict with state name as keys and their access time (int) as values.
        state_access_log: a dict with state name as keys and list of their acces times as values.
        state_lock: a dict with state name as keys and lock object as values.
        state_activity: a dict with state replica name as keys and their temperature as values.
        so: StateOeprater object to excute detailed operations.
    """

    def __init__(self):
        """Initial the StateManager class."""
        self.memory_state_storage = {}
        self.state_access_time = {}
        self.state_access_log = {}
        self.state_lock = {} 
        self.state_activity = {}
        self.so = StateOperater()

    def state_lock_get(self):
        """Serialize the lock objects and return the locks list dict."""
        serializable_locks = {}
        for lock_name, lock_obj in self.state_lock.items():
            serializable_locks[lock_name] = lock_obj.locked()
        return serializable_locks

    def state_create(self,function_name,value):
        """Create a new state replica in the state manager.
        
        Args:
            fucntion_name: the created state name
            value: the value of new state
        """
        # Check whether the state has existed in the state manager.
        if function_name in self.memory_state_storage:
            return f"state of function {function_name} has exists" 

        # Create state's lock and initial its value       
        self.state_lock[function_name] = threading.Lock()
        self.memory_state_storage[function_name] = value
        
        # Record the first access messages
        self.state_access_time[function_name] = time.time()
        self.state_access_log[function_name] = []
        self.state_access_log[function_name].append(time.time())

        # Initial the temperature to be warm
        self.state_activity[function_name] = 1
        
        # Tell the creating messages to state monitor
        self.so.state_new_tell_monitor(function_name)
        self.so.activity_update_tell(function_name,1)

    def state_monitor_get(self):
        """Interface for state monitor to initial the monitor dict."""
        monitor_dict = {}
        for function_name in self.state_lock :
            monitor_dict[function_name]["activity"] = self.state_activity[function_name]
        return monitor_dict

    def state_size(self):
        """Interface for experiments to monitor the memory cost of state manager's memory storage."""
        total_size = 0
        for value in self.memory_state_storage.values():
            total_size += sys.getsizeof(value)
        return total_size

    def state_read(self,function_name,locked,post_identity):
        """Provide the ability to read the states' values and related lock operations.
        
        Args:
            function_name: the read state name
            locked: 1 (lock the state) or 0 (don't lock the state)
            post_identity: 1 (stateful functions) pr 0 (monitor or other manager)
        
        Returns:
            The state value required.
        """
        # Just lock the local state (from other manager locking the state.)
        if locked == 1 and post_identity == 0 :
            self.state_lock[function_name].acquire()
            return 

        # There is not the specific state replica locally, needing to pull from other positions.
        if function_name not in self.state_lock:
            # Initial the lock object
            self.state_lock[function_name] = threading.Lock()

            # Pull the specific state.
            self.memory_state_storage[function_name] = self.so.state_pull_from_other_nodes(function_name) 
            
            # Initial temperature and tell monitor.
            self.state_activity[function_name] = 1
            self.so.activity_update_tell(function_name,1)
            self.so.state_new_tell_monitor(function_name)

        # State juest in local disk.
        elif function_name not in self.memory_state_storage:
            # Load state from local disk to local memory.
            self.memory_state_storage[function_name] = self.so.state_load_from_local_disk(function_name) 

        # Check whether locking the state replica.
        if locked == 1 : # Lock
            self.state_lock[function_name].acquire()
            state_data = self.memory_state_storage[function_name]
            self.so.state_lock_of_other_nodes(function_name)
        else : # Unlock
            self.state_lock[function_name].acquire()
            state_data = self.memory_state_storage[function_name]
            self.state_lock[function_name].release()
        
        # If state is read by stateful function, update the access message logs. 
        if post_identity == 1:
            if function_name not in self.state_access_log:
                self.state_access_log[function_name] = []
            self.state_access_time[function_name] = time.time()
            self.state_access_log[function_name].append(time.time())

        return state_data # Return the value read.

    def state_write(self,function_name,post_identity,state_data):
        """Provide the ability to wirte the states' values and related lock operations.
        
        Args:
            function_name: the write state name
            state data: the value wiil be updated to state manager
            post_identity: 1 (stateful functions) pr 0 (monitor or other manager)
        """
        # Pull state from other nodes if not existing locally
        if function_name not in self.state_lock:
            # Create and initial the related objects.
            self.state_lock[function_name] = threading.Lock()
            self.state_activity[function_name] = 1
            self.so.activity_update_tell(function_name,1)
            self.so.state_new_tell_monitor(function_name)
        
        # Write the state locally in memort.
        self.memory_state_storage[function_name] = state_data
        
        # Release the lock if it was locked. 
        if self.state_lock.get(function_name).locked():
            self.state_lock[function_name].release()
        
        # If state is writen by stateful function, update the access message logs. 
        if post_identity == 1:
            self.state_access_time[function_name] = time.time()
            self.state_access_log[function_name].append(time.time())
            self.so.state_unlock_of_other_nodes(function_name,state_data)   

    def state_remove(self,function_name,type):
        """Provide the ability to remove a state replica in state manager for user and monitor.
        
        Args:
            function_name: the removed state's name
            type: 1 (Remove after move to external storage) or 0 (Directly remove)
        """
        if function_name in self.state_lock:
            # Remove afer move to external storage
            if type == 1 :
                # Move to external from the stored stoarge layer.
                sfm = StateFileManager()
                if function_name in self.memory_state_storage: # Memory
                    sfm.state_move_to_external_storage(function_name,self.memory_state_storage[function_name])
                else: # Disk
                    sfm.state_move_to_external_storage_from_disk(function_name)
                sfm.close()
            
            # Delete local state replica
            del self.state_lock[function_name]
            if function_name in self.memory_state_storage:
                del self.memory_state_storage[function_name]
            if os.path.exists(f"{WORKER_STATE_DISK_PATH}/{function_name}.json"):
                os.remove(f"{WORKER_STATE_DISK_PATH}/{function_name}.json")
            
            # Tell monitor
            self.so.state_delete_tell_monitor(function_name)


    def state_activity_change(self):
        """Manage the active scheduling of state replicas' temperature."""
        while True :
            # Record the current time and local memory utilization.
            current_time = time.time()
            memory_utilization = self.so.get_memory_utilization()
            
            # Check every state replica locally
            for function_name in self.state_lock:
                # Compute the access time in 120 seconds
                f = 0
                for access_time in self.state_access_log[function_name] :
                    if current_time - access_time < 120:
                        f += 1

                # Schedule the temperature according to the messages. 
                if current_time - self.state_access_time[function_name] >= 1000000 :
                    activity_temp = 0 # cold
                elif f >= 10 and memory_utilization < 0.8 : 
                    activity_temp = 2 # hot
                else : 
                    activity_temp = 1 # warm
                
                # Judge by the state size if hot.
                if activity_temp == 2:
                    # Compute size
                    if function_name in self.memory_state_storage:
                        data_size = sys.getsizeof(self.memory_state_storage[function_name])
                    else:
                        data_size = sys.getsizeof(self.so.state_load_from_local_disk(function_name)) 

                    # Judege
                    if data_size > 1024 or  psutil.virtual_memory().percent > 60 :
                        activity_temp = 1 # warm

                # If temperature is not changed
                if activity_temp == self.state_activity[function_name] :
                    continue

                # If temperature is changed
                else:
                    # To hot, we update state to memory.
                    if activity_temp == 2 :
                        if function_name not in self.memory_state_storage : 
                            self.memory_state_storage[function_name] = funcs.state_load_from_local_disk(function_name)
                    
                    # To cold, we delete state in meory first.
                    elif activity_temp == 0 :
                        if function_name in self.memory_state_storage :
                            self.so.save_dict_to_file(function_name,self.memory_state_storage[function_name])
                            del self.memory_state_storage[function_name]

                    # Tell state monitor, and the cold state will be scheduling to external storage by top layer.
                    self.state_activity[function_name] =  activity_temp
                    self.so.activity_update_tell(function_name,activity_temp)
            
            # Schedule once every 5 minitues.
            time.sleep(300)


    def state_semi_activity_manager(self):
        """Manage the warm temperature."""
        while True:
            # Record the current time.
            current_time = time.time()

            # Check every warm state existing in local memory.
            for function_name in self.state_lock:
                if function_name in self.memory_state_storage :
                    
                    # Judge if last access time is greater than 60 seconds from now.
                    if self.state_activity[function_name] == 1 and current_time - self.state_access_time[function_name] > 60 :
                        if function_name in self.memory_state_storage:
                            
                            # Save state to local disk and remove the replica in memorty
                            self.so.save_dict_to_file(function_name,self.memory_state_storage[function_name])
                            del self.memory_state_storage[function_name]

            # Schedule once every 30 seconds.
            time.sleep(30)