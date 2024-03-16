"""PromQL() class to access the API of prometheus directly.

Typical usage example:

    promQL = PromQL(ip)
    data = promQL.queryRange(query, end)
"""
import requests
import json

class PromQL:
    """Communicate with APIs of prometheus directly.

    Attributes:
        ip: ip address of prometheus
        apiQuery: the query order to search corresponding single message
        apiQueryRange: the query order to search corresponding messages' sequence
    """

    def __init__(self, ip: str):
        """Initial PromQL class."""
        self.ip = ip
        self.apiQuery = 'http://' + ip + '/api/v1/query'
        self.apiQueryRange = 'http://' + ip + '/api/v1/query_range'

    def query(self, query: str):
        """Query the instantaneous value or certain information"""
        # Get information
        res = {
            'status': 'error',
            'data': '',
        }
        response = requests.get(self.apiQuery, {'query': query})

        # Check results
        if response.status_code == 200:
            response_json = json.loads(response.text)
            res['status'] = response_json['status']
            res['data'] = response_json['data']['result']
        else:
            print('Request error with error code' + str(response.status_code))

        return res

    def queryRange(self, query: str, end: float, ahead: int = 60, step: int = 1):
        """Query continuous information"""
        # Get information
        start = end - ahead
        res = {
            'status': 'error',
            'data': '',
        }
        response = requests.get(self.apiQueryRange, {'query': query, 'start': start, 'end': end, 'step': step})
        
        # Check results
        if response.status_code == 200:
            response_json = json.loads(response.text)
            res['status'] = response_json['status']
            res['data'] = response_json['data']['result']
        else:
            print('Request error with error code' + str(response.status_code))

        return res

