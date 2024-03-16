"""StateMonitor() class aims to provide the ability about state monitor, state global management.

Typical usage example:

    sm = StateMonitor()
    sm.state_search(function_name)
"""
import copy
import time

from app import StateOperater
from app import StateFileManager

class StateMonitor:
    """Manage the state monitor data and provide scheduling ability about the monitored data.

    Attributes:
        so: the tool class to help complete related operations.
        messages: the situation about the state replica name list in every worker VM including other
                monitoring messages.
        settings: the information about every function, especially including the master state replica's
                locations.
    """

    def __init__(self):
        """Initial the StateMonitor class and related monitoring dict."""
        self.so = StateOperater()
        self.messages = {} 
        self.settings = {}

    def state_search(self,function_name):
        """Search the master state replica of the specific function_name.

        Args:
            function_name(str): the searched state name of corresponding function.

        Returen:
            A string about the ip address of primary(master) state replica location or "externalstorage".
        """
        # Exists master replica in other worker VM.
        return_node = ""
        if self.settings[function_name]:
            if self.settings[function_name]["primary"] :
                return_node = self.settings[function_name]["primary"]
                return return_node

        #  Exists master replica in other worker VM.
        if return_node == "" :
            # Search external storage
            sfm = StateFileManager()
            self.messages["externalstorage"] = self.sfm.external_states_get()
            sfm.close()
            
            # In external storage
            if function_name in self.messages["externalstorage"]:
                return "externalstorage"
        
        # Not in the cluster
        return "" 

    def state_search_all(self,function_name):
        """Search all state replicas of the specific function_name.

        Args:
            function_name(str): the searched state name of corresponding function.

        Returen:
            A string LIST about the ip address of state replica locations in worker nodes
        """
        node_list = []
        for node_ip, funcion_dict in self.messages.items():
            if function_name in funcion_dict:
                node_list.append(node_ip)
        
        return node_list

    def state_change(self,node_ip,change_type,function_name):
        """Update the state monitoring dict about the removing or adding of state replicas. 

        Args:
            function_name(str): the searched state name of corresponding function.
            node_ip(str): the location of adding or removing happened.
            change_type(str): "add" or "delete".
        """
        # State replica adding
        if change_type == "add": 
            # Initial new subdict
            self.messages[node_ip][function_name]={}
            
            # Set the value of monitor dict
            if function_name not in self.settings:
                self.settings[function_name]={}
                self.settings[function_name]["primary"] = node_ip
        
        # State replica removing
        elif change_type == "delete":
            # Delete the removed state replica in monitor dict.
            del self.messages[node_ip][function_name]

            # Change the master replica if the master state replica is removed.
            if not function_name in self.settings:
                del self.settings[function_name]["primary"]
                
                # Select a slave replica randomly as new master replica.
                for node_ip, funcion_dict in self.messages.items():
                    if function_name in funcion_dict:
                        self.settings[function_name]["primary"]=node_ip

    def activity_schange(self,node_ip,activity,function_name):
        """Update the state monitoring dict about the temperature of on state replica. 

        Args:
            function_name(str): the searched state name of corresponding function.
            node_ip(str): the location of temperature changing happened.
            activity: the new temperature from {"cold","warm","hot"}
        """
        self.messages[node_ip][function_name]={}
        self.messages[node_ip][function_name]["activity"] = int(activity)

    def function_infomation_acquisition(self,function_name):
        """Acquire all information about state of the specific function corresponding.

        Args:
            function_name(str): the searched state name of corresponding function.
        
        Returens:
            A dict containing the location list, temperature list, scope and master location.
        """
        return_dict = {}
        return_dict["scope"] = 0
        for node_ip, funcion_dict in self.messages.items():
            if function_name in funcion_dict:
                return_dict["location"][node_ip]["activity"] = funcion_dict[function_name]["activity"]
                return_dict["scope"] += 1
        return_dict["primary"] = self.settings[function_name]
        return return_dict

    def state_migration(self,msg,function_name):
        """The active state migration interface for the coupling problem of state and migration.

        Args:
            function_name(str): the searched state name of corresponding function.
            msg: the related IP messages about the state migration.
        """
        # Create new state in target VM
        self.so.state_read(function_name,{'locked':0, 'identity': 1},msg['target_ip'])
        
        # Remove old state in source VM
        self.so.state_remove(function_name,msg['source_ip'],0)

    def state_remove_from_nodes(self):
        """Manage cold state replicas to remove them."""
        while True :
            # Deepcopy the monitor dicts.
            state_messages = copy.deepcopy(self.messages)
            state_setting = copy.deepcopy(self.settings)
            
            # Check the temperature of every state replica
            for node_name in state_messages :
                pending_remove=[]
                for function_name in state_messages[node_name] :            
                    
                    # Remove the state replica with "cold" temperature.
                    if state_messages[node_name][function_name]["activity"] == 0 :
                        
                        # Judge if there is cold replica
                        count = 0
                        for node_ip, funcion_dict in state_messages.items():
                            if function_name in funcion_dict:
                                count += 1

                        # Remove directly if the removed replica is slave replica.
                        if not state_setting[function_name]["primary"] == node_name :     
                            # If there is only one replica, move it to external storage.
                            if count == 1 :
                                pending_remove.append([function_name,node_name,1])

                            # Remove directly.
                            else:
                                pending_remove.append([function_name,node_name,0])

                        # Else remove the replica and set new master replica.
                        else :
                            # If there is only one replica, move it to external storage.
                            if count ==1 :
                                pending_remove.append([function_name,node_name,1])
                
                # Excute specific remove operations.
                for msg in pending_remove:
                    self.so.state_remove(msg[0],msg[1],msg[2])

            # Update the monitor dicts.
            self.messages = copy.deepcopy(state_messages)
            self.settings = copy.deepcopy(state_setting)
            
            # The algorithm will excute once every 120 seconds.
            time.sleep(120)