'''
Created on 15 July 2021

@author: eiaavij
'''
from com_ericsson_do_auto_integration_utilities.Report_file import Report_file
from com_ericsson_do_auto_integration_utilities.Logger import Logger
from com_ericsson_do_auto_integration_scripts.MODIFY_TOSCA_PARAMS import *
from com_ericsson_do_auto_integration_initilization.SIT_initialization import SIT_initialization

log = Logger.get_logger('MODIFY_TOSCA_EPG_PARAMS.py')


def modify_configurable_prop_tosca_epg():
    """Modifying parameters of tosca epg."""
    try:
        vapp_name = SIT.get_tosca_epg_vapp(SIT)
        file_name = 'modifyConfigurableProperties_tosca_epg.json'
        result = '{"isAutoHealingEnabled":"false","isAutoScaleEnabled":"false"}'

        modify_configurable_prop_tosca('TOSCA_EPG', vapp_name, file_name, result)

    except Exception as e:
        log.error('Error modifying configurable properties for TOSCA epg %s', str(e))
        Report_file.add_line('Error modifying configurable properties for TOSCA epg ' + str(e))
        assert False


def modify_metadata_tosca_epg():
    """Modifying metadata of tosca epg."""
    try:
        file_name = 'modifyMetadata_tosca_epg.json'
        result = '{"meta1":"value1"}'
        modify_metadata_tosca('TOSCA_EPG', file_name, result)

    except Exception as e:
        log.error('Error  modifying meta data for TOSCA epg %s', str(e))
        Report_file.add_line('Error  modifying meta data for TOSCA epg ' + str(e))
        assert False


def modify_extension_tosca_epg():
    """Modifying extension of tosca epg."""
    try:
        file_name = 'modifyExtensions_tosca_epg.json'
        result = '"waitTimeBeforeAutoheal":2'

        modify_extension_tosca('TOSCA_EPG', file_name, result)

    except Exception as e:
        log.error('Error modifying extension parameter for TOSCA epg %s', str(e))
        Report_file.add_line('Error modifying extension parameter for TOSCA epg ' + str(e))
        assert False
