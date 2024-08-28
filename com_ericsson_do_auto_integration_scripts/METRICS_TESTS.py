'''
Created on jul 17, 2020

@author: zsyapra
'''
import os
from com_ericsson_do_auto_integration_utilities.Report_file import Report_file
from com_ericsson_do_auto_integration_utilities.Logger import Logger
from com_ericsson_do_auto_integration_utilities.Server_details import Server_details



log = Logger.get_logger('METRICS_TESTS.py')


def collect_metrics_tests():
    try:
        log.info("Start to fetch codeploy metrics tests")
        Report_file.add_line('Start to fetch codeploy metrics tests')
        url, app = Server_details.get_metrics_details(Server_details)
        command = 'python -m pytest --rootdir=common_service_tests/metrics/ common_service_tests/metrics/tests/pm-server.py -s --url {} -m {}'.format(url,app)
        log.info('command: %s', command)
        res = os.system(command)
        log.info('response: %s', str(res))
        if res != 0:
            log.info('Metric not found')
            Report_file.add_line('Metric not found')
            assert False
        else:
            log.info('Metrics has been collected successfully')
            Report_file.add_line('Metrics has been collected successfully')
            
    
    except Exception as err:
        log.info('Error in Metrics Tests'+str(err))
        Report_file.add_line('Error in Metrics Tests ' + str(err))
        assert False
    