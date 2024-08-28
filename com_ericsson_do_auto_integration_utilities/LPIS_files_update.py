# ********************************************************************
# Ericsson LMI                                    SCRIPT
# ********************************************************************
#
# (c) Ericsson LMI 2021
#
# The copyright to the computer program(s) herein is the property of
# Ericsson LMI. The programs may be used and/or copied only  with the
# written permission from Ericsson LMI or in accordance with the terms
# and conditions stipulated in the agreement/contract under which the
# program(s) have been supplied.
#
# ********************************************************************
'''
Created on 16 April 2020


@author: eiaavij
'''

from com_ericsson_do_auto_integration_utilities.Logger import Logger
from com_ericsson_do_auto_integration_utilities.Report_file import Report_file
from com_ericsson_do_auto_integration_utilities.Json_file_handler import Json_file_handler
from com_ericsson_do_auto_integration_initilization.Initialization_script import Initialization_script
from com_ericsson_do_auto_integration_initilization.ECM_PI_initialization import ECM_PI_Initialization
from com_ericsson_do_auto_integration_initilization.SIT_initialization import SIT_initialization
from com_ericsson_do_auto_integration_model.Ecm_core import Ecm_core
from com_ericsson_do_auto_integration_model.EPIS import EPIS

log = Logger.get_logger('LPIS_files_update.py')


def update_register_vm_vnfm(file, name, option=''):
    try:
        log.info('updating vm_vnfm_register.json file')
        file_name = r'com_ericsson_do_auto_integration_files/vm_vnfm/' + file

        ecm_host_data = Initialization_script.get_model_objects(Initialization_script, 'ECM_CORE')
        is_cloudnative = Ecm_core.get_is_cloudnative(Ecm_core)
        site_name = EPIS.get_site_name(EPIS)

        evnfm_hostname = ecm_host_data._Ecm_core__evnfm_hostname

        evnfm_username = ecm_host_data._Ecm_core__evnfm_auth_username
        evnfm_password = ecm_host_data._Ecm_core__evnfm_auth_password

        Json_file_handler.update_any_json_attr(Json_file_handler, file_name, [], 'name', name)
        Json_file_handler.update_any_json_attr(Json_file_handler, file_name, ['endpoints', 0], 'ipAddress',
                                               evnfm_hostname)
        Json_file_handler.update_any_json_attr(Json_file_handler, file_name, [], 'authIpAddress',
                                               evnfm_hostname)
        Json_file_handler.update_any_json_attr(Json_file_handler, file_name, [], 'authUserName',
                                               evnfm_username)
        Json_file_handler.update_any_json_attr(Json_file_handler, file_name, [], 'authPassword',
                                               evnfm_password)
        Json_file_handler.update_any_json_attr(Json_file_handler, file_name, ['endpoints', 0], 'testUri',
                                               "/vnflcm")
        Json_file_handler.update_any_json_attr(Json_file_handler, file_name, [], 'siteName', site_name)

        if option == 'CNS-INST' or option == 'TEST-HOTEL-VM-VNFM-INTE':
            Json_file_handler.update_any_json_attr(Json_file_handler, file_name, [], 'cnfCapable', "true")
            Json_file_handler.update_any_json_attr(Json_file_handler, file_name, ['endpoints', 0], 'testUri',
                                                   "/")
        else:
            Json_file_handler.update_any_json_attr(Json_file_handler, file_name, [], 'cnfCapable', "false")
        log.info('end updating vm_vnfm_register.json file')
    except Exception as e:

        log.error('Error while updating vm_vnfm_register.json file %s', str(e))
        Report_file.add_line('Error while updating vm_vnfm_register.json file')


def update_nfvo_vm_vnfm(file, subscription_id):
    try:
        log.info('updating vm_vnfm_nfvo.json file')
        file_name = r'com_ericsson_do_auto_integration_files/vm_vnfm/' + file

        sit_data = SIT_initialization.get_model_objects(SIT_initialization, 'SIT')
        ecm_host_data = Initialization_script.get_model_objects(Initialization_script, 'ECM_CORE')
        nfvo_data = Initialization_script.get_model_objects(Initialization_script, 'NFVO')
        EPIS_data = ECM_PI_Initialization.get_model_objects(ECM_PI_Initialization, 'EPIS')
        tenant_id = EPIS_data._EPIS__tenant_name
        core_vm_hostname = ecm_host_data._Ecm_core__core_vm_hostname
        base_url = f"https://{core_vm_hostname}:443/ecm_service"
        core_host_ip = ecm_host_data._Ecm_core__CORE_VM_IP
        enm_host_name = ecm_host_data._Ecm_core__evnfm_hostname
        ecm_gui_username = ecm_host_data._Ecm_core__ecm_gui_username
        ecm_gui_password = ecm_host_data._Ecm_core__ecm_gui_password
        vdc_id = sit_data._SIT__vdc_id
        sol_version = nfvo_data._Nfvo__orvnfm_version

        Json_file_handler.update_any_json_attr(Json_file_handler, file_name, [], 'baseUrl', base_url)
        Json_file_handler.update_any_json_attr(Json_file_handler, file_name, [], 'hostName', core_vm_hostname)
        Json_file_handler.update_any_json_attr(Json_file_handler, file_name, [], 'hostIpAddress',
                                               core_host_ip)
        Json_file_handler.update_any_json_attr(Json_file_handler, file_name, [], 'orVnfmVersion', sol_version)
        Json_file_handler.update_any_json_attr(Json_file_handler, file_name, [], 'userName', ecm_gui_username)
        Json_file_handler.update_any_json_attr(Json_file_handler, file_name, [], 'password', ecm_gui_password)
        Json_file_handler.update_any_json_attr(Json_file_handler, file_name, [], 'enmHostName', enm_host_name)
        Json_file_handler.update_any_json_attr(Json_file_handler, file_name, [], 'subscriptionId',
                                               subscription_id)
        Json_file_handler.update_any_json_attr(Json_file_handler, file_name, ['tenancyDetails', 0],
                                               'tenantId', tenant_id)
        Json_file_handler.update_any_json_attr(Json_file_handler, file_name,
                                               ['tenancyDetails', 0, 'vdcDetails', 0], 'id', vdc_id)

        log.info('end updating vm_vnfm_nfvo.json file')

    except Exception as e:

        log.error('Error while updating vm_vnfm_nfvo.json file %s', str(e))
        Report_file.add_line('Error while updating vm_vnfm_nfvo.json file')
        assert False


def update_vim_vm_vnfm(file):
    try:
        log.info('updating vm_vnfm_vim_addition.json file')
        file_name = r'com_ericsson_do_auto_integration_files/vm_vnfm/' + file

        sit_data = SIT_initialization.get_model_objects(SIT_initialization, 'SIT')
        cee_data = Initialization_script.get_model_objects(Initialization_script, 'CEE')
        EPIS_data = ECM_PI_Initialization.get_model_objects(ECM_PI_Initialization, 'EPIS')

        host_ip_address = cee_data._Cee__host_ip_address
        cloud_hostname = cee_data._Cee__host_name
        key_stone = EPIS_data._EPIS__key_stone
        project_tenant_id = sit_data._SIT__project_id
        project_name = EPIS_data._EPIS__project_name
        project_username = project_name + '_admin'
        project_password = project_name.capitalize() + '.laf'

        Json_file_handler.update_any_json_attr(Json_file_handler, file_name, ['vims', 0], 'hostIpAddress',
                                               host_ip_address)
        Json_file_handler.update_any_json_attr(Json_file_handler, file_name, ['vims', 0], 'hostName',
                                               cloud_hostname)
        Json_file_handler.update_any_json_attr(Json_file_handler, file_name, ['vims', 0], 'authUrl',
                                               key_stone)
        Json_file_handler.update_any_json_attr(Json_file_handler, file_name,
                                               ['vims', 0, 'domain', 0, 'project', 0], 'name', project_name)
        Json_file_handler.update_any_json_attr(Json_file_handler, file_name,
                                               ['vims', 0, 'domain', 0, 'project', 0], 'id',
                                               project_tenant_id)
        Json_file_handler.update_any_json_attr(Json_file_handler, file_name,
                                               ['vims', 0, 'domain', 0, 'project', 0], 'username',
                                               project_username)
        Json_file_handler.update_any_json_attr(Json_file_handler, file_name,
                                               ['vims', 0, 'domain', 0, 'project', 0], 'password',
                                               project_password)

        log.info('end updating vm_vnfm_vim_addition.json file')

    except Exception as e:

        log.error('Error while updating vm_vnfm_vim_addition.json file %s', str(e))
        Report_file.add_line('Error while updating vm_vnfm_vim_addition.json file')
