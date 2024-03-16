'''
Entry to the migration decision-maker, run manage.py locally on the worker node to 
start the migration decision-maker on that node
'''
from .app import MigrationDecision

if __name__ == '__main__': 
    # run the migration decision algorithm。
    md = MigrationDecision()
    md.migration_decision_algorithm_cpu_utilization()