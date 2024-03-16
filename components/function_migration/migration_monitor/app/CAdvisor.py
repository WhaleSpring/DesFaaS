"""CAdvisor() class to provide the query ability to access cadvisor in kubernetes.

Typical usage example:

    cadvisor = CAdvisor()
    time = cadvisor.get_function_invocated_times(function_name,end) 
"""
from app import PromQL


# 对应cadvisor服务,监控容器级别的指标
class CAdvisor:
    """Communicate with CAdvisor of kubernetes.
    
    In DesFaaS, we just use it to get the number of invacations of the function.

    Attributes:
        promQL: promethues API
    """
    def __init__(self, prom: PromQL):
        """Initial MigrationMonitor class."""
        self.promQL = prom

    def get_function_invocated_times(self, function_name: str, end: float):
        """Get the invocated time of appointed funtion.
        
        Args:
            function_name (string): name of function searched
            end (int):  Difference between the monitored start time and the current time (s)

        Returns:
            An int number that pointing the invacation time "function_name" invocated in "end" seconds.
        
        """
        query = 'sum by(function_name)(gateway_function_invocation_total{{function_name=~"^{function_name}.*"}})'.format(function_name=function_name)
        response = self.promQL.queryRange(query, end)['data'][0]['values']
        return [[record[0], float(record[1])] for record in response]
