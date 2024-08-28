'''
Created on 14 May 2020

@author: emaidns
'''
from com_ericsson_do_auto_integration_utilities.Report_file import Report_file
from com_ericsson_do_auto_integration_utilities.Logger import Logger
from com_ericsson_do_auto_integration_scripts.MODIFY_TOSCA_PARAMS import *
from com_ericsson_do_auto_integration_initilization.SIT_initialization import SIT_initialization

log = Logger.get_logger('MODIFY_TOSCA_DUMMY_PARAMS.py')


def modify_configurable_prop_tosca_dummy():
    """Modifying parameters of tosca dummy."""
    try:
        sit_data = SIT_initialization.get_model_objects(SIT_initialization, 'SIT')
        vapp_name = sit_data._SIT__dummy_package_name
        file_name = 'modifyConfigurableProperties_tosca_dummy.json'
        result = '''"keyValuePairs":{"isAutoHealingEnabled":"false","isAutoScaleEnabled":"false"}'''

        modify_configurable_prop_tosca('TOSCA_DUMMY', vapp_name, file_name, result)

    except Exception as e:
        Report_file.add_line('Error modifying configurable properties for TOSCA dummy ' + str(e))
        assert False


def modify_metadata_tosca_dummy():
    """Modifying metadata of tosca dummy."""
    try:
        file_name = 'modifyMetadata_tosca_dummy.json'
        result = '{"keyValuePairs":{"meta1":"value1"}}'
        modify_metadata_tosca('TOSCA_DUMMY', file_name, result)

    except Exception as e:
        log.error('Error  modifying meta data for TOSCA dummy %s', str(e))
        Report_file.add_line('Error  modifying meta data for TOSCA dummy ' + str(e))
        assert False


def modify_extension_tosca_dummy():
    """Modifying extension of tosca dummy."""
    try:
        file_name = 'modifyExtensions_tosca_dummy.json'
        result = '{"keyValuePairs":{"ext2":"val2"}}'
        modify_extension_tosca('TOSCA_DUMMY', file_name, result)

    except Exception as e:
        log.error('Error modifying extension parameter for TOSCA dummy %s', str(e))
        Report_file.add_line('Error modifying extension parameter for TOSCA dummy ' + str(e))
        assert False
