'''
Created on 30 Apr 2020

@author: zsyapra
'''
from com_ericsson_do_auto_integration_utilities.Report_file import Report_file
from com_ericsson_do_auto_integration_utilities.Logger import Logger
from com_ericsson_do_auto_integration_utilities.Common_utilities import Common_utilities
from com_ericsson_do_auto_integration_scripts.SCALE_HEAL import *
from com_ericsson_do_auto_integration_scripts.DUMMY_TOSCA_PRETOSCA_WORKFLOW import *

log = Logger.get_logger('ETSI_DUMMY_TOSCA_SCALE_HEAL')


def etsi_dummy_tosca_depl_scaleout():
    try:
        log.info('Start Dummy Tosca ScaleOut ')
        Report_file.add_line('Start Dummy Tosca ScaleOut')
        start_scale_out("TOSCA_DUMMY")
    
    except Exception as e:
        log.error('Error During Dummy Tosca ScaleOut ' + str(e))
        Report_file.add_line('Error During Dummy Tosca Scaleout ' + str(e))
        assert False


def etsi_dummy_tosca_depl_scalein():
    try:
        log.info('Start Dummy Tosca SCALE-IN ')
        Report_file.add_line('Start Dummy Tosca SCALE-IN')
        start_scale_in("TOSCA_DUMMY")
     
    except Exception as e:
        log.error('Error During Dummy Tosca ScaleIn ' + str(e))
        Report_file.add_line('Error During Dummy Tosca Scalein ' + str(e))
        assert False  
        
def etsi_dummy_tosca_depl_heal():
    try:
        
        log.info('Start Dummy Tosca deployment HEAL ')
        Report_file.add_line('Start Dummy Tosca deployment HEAL')
        start_heal("TOSCA_DUMMY")
        
        
    except Exception as e:
        log.error('Error During Dummy Tosca ScaleHeal ' + str(e))
        Report_file.add_line('Error During Dummy Tosca ScaleHeal ' + str(e))
        assert False


def verify_etsi_tosca_dummyheal_workflow_verison():
    attribute_name = 'ONBOARD_PACKAGE' 
    node_name = Common_utilities.fetch_attribute_from_runtimefile(Common_utilities,attribute_name)
    verify_worklow_version(node_name)
    
    