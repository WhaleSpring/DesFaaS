"""StateRW is aims to help user access the state stored by DesFaaS.

Typical usage example:

  srw = StateRW()
  data = srw.read()
  srw.write(data)
"""
import requests
import os

class StateRW:
    """Help user access the state stored by DesFaaS.

    Attributes:
        function_name(str): the state name stored in DesFaaS
        read_url(str): the url to read state  
        wirte_url: the url to wriet state
    """

    def __init__(self, function_name):
        """Initial the StateRW class and constuct the url to read and wirte"""
        self.function_name = function_name
        self.read_url = f"http://{os.getenv('NodeIP')}:8054/state_read/{self.function_name}"
        self.write_url = f"http://{self.state_primary_check()}:8054/state_write/{self.function_name}"

    def state_primary_check(self):
        """Search the master replica location of the funtion.
        
        Returns:
            A string of the ip address where the master replica is located.
        """
        url = f"http://100.64.214.11:8053/primary_state_search/{self.function_name}"
        return requests.get(url).text.strip().strip("\"")

    def state_read(self):
        """Read state data.
        
        Returns:
            state data
        """
        data = {
            'locked':  0,
            'identity': 1
        }
        res = requests.get(self.read_url, json=data)
        return res.json()

    def state_write(self, state_data):
        """Write state data.
        
        Args:
            state_data
        """
        data = {
            'state_data':  state_data,
            'identity': 1
        }
        requests.post(self.write_url, json=data)