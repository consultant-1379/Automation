# pylint: disable=C0302,C0103,C0301,C0412,E0602,W0621,W0601,W0401,C0411,R0915,E0602,W0611,W0212,W0703,R1714,W0613,R0914,W0105,R0913,E0401,W0705,W0612,C0116
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
Created on 22 Oct 2018

@author: emaidns
'''
import copy
import ipaddress
import time

import yaml

from com_ericsson_do_auto_integration_initilization.ECM_PI_initialization import ECM_PI_Initialization
from com_ericsson_do_auto_integration_initilization.Initialization_script import Initialization_script
from com_ericsson_do_auto_integration_initilization.SIT_initialization import SIT_initialization
from com_ericsson_do_auto_integration_model.Ecm_core import Ecm_core
from com_ericsson_do_auto_integration_model.SIT import SIT
from com_ericsson_do_auto_integration_utilities.ExecuteCurlCommand import ExecuteCurlCommand
from com_ericsson_do_auto_integration_utilities.Json_file_handler import Json_file_handler
from com_ericsson_do_auto_integration_utilities.Logger import Logger
from com_ericsson_do_auto_integration_utilities.Report_file import Report_file
from com_ericsson_do_auto_integration_utilities.ServerConnection import ServerConnection
from com_ericsson_do_auto_integration_utilities.Shell_handler import ShellHandler

log = Logger.get_logger('SIT_files_update')


def update_nfvo_config_file(file_name, dynamic_vnflcm=False):
    """
    This method is only used in case of remove and add nfvo (not part of integration job between ECM and VNF-LCM)
    @param file_name:
    @param dynamic_vnflcm:
    @return:
    """
    log.info('Start to update nfvoConfig.json')
    Report_file.add_line('start to update nfvoConfig.json ')

    try:

        ecm_host_data = Initialization_script.get_model_objects(Initialization_script, 'ECM_CORE')
        nfvo_data = Initialization_script.get_model_objects(Initialization_script, 'NFVO')
        sit_data = SIT_initialization.get_model_objects(SIT_initialization, 'SIT')

        vnf_lcm_ip = ecm_host_data._Ecm_core__VNF_LCM_Servicedb_IP

        subscription_id = sit_data._SIT__vnfManagers
        vdc_id = sit_data._SIT__vdc_id

        nfvo_data._Nfvo__subscriptionId = subscription_id
        nfvo_data._Nfvo__vdcId = vdc_id

        if dynamic_vnflcm:
            nfvo_data._Nfvo__enmHostName = vnf_lcm_ip

        Json_file_handler.update_json_file(Json_file_handler, file_name, nfvo_data.json_file_data)

        log.info('Finished to update nfvoConfig.json')
        Report_file.add_line('Finished to update nfvoConfig.json')

    except Exception as e:

        log.error('Error to update nfvoConfig.json %s', str(e))
        Report_file.add_line('Error to update nfvoConfig.json ,check logs for more detail')
        assert False


def update_flavour(file_name, flavour):
    try:
        log.info('start updating flavor in hot yaml file')
        with open(file_name, "r") as yaml_file:
            data = yaml.load(yaml_file)
            attr = data['parameters']['services_flavor']['constraints'][0]['allowed_values']

            if flavour in attr:
                log.info('flavour already exists in vnflaf_cee.yaml %s', flavour)
            else:
                attr.append(flavour)
                log.info('flavour added successfully in vnflaf_cee.yaml %s', flavour)

        with open(file_name, "w") as yaml_file:

            yaml.dump(data, yaml_file, indent=4)
            log.info('flavour updated successfully in vnflaf_cee.yaml %s', flavour)

    except ValueError as v:

        log.error('Error while updating the yaml file: %s \nERROR: %s', file_name, str(v))
        log.error('Script terminated due to error printed above ')
        Report_file.add_line('Script terminated due to error in Json_file_handler')
        exit(-1)

    except FileNotFoundError:
        log.error('File Not Found Error : Wrong file or file path: %s', file_name)
        log.error('Script terminated due to error printed above ')
        Report_file.add_line('Script terminated due to error in Json_file_handler')
        exit(-1)


def update_runtime_env_file(attribute, value):
    """this method is used to store runtime data in a file placed on blade server
    @param attribute:  attribute to be modified
    @param value: value of attribute
    """

    log.info(f' Updating run time file attribute %s with value %s', attribute, value)
    ecm_host_data = Initialization_script.get_model_objects(Initialization_script, 'ECM_CORE')
    server_ip = ecm_host_data._Ecm_core__ECM_Host_Blade_IP
    username = ecm_host_data._Ecm_core__ECM_Host_Blade_username
    password = ecm_host_data._Ecm_core__ECM_Host_Blade_Password
    enviornment = ecm_host_data._Ecm_core__enviornment
    data_file = r'com_ericsson_do_auto_integration_files/run_time_' + enviornment + '.json'
    dest = r'/root/' + 'run_time_' + enviornment + '.json'
    runtime_file_connection = ServerConnection.get_connection(server_ip, username, password)
    lock_file = 'run_time_' + enviornment + '.lock'
    timeout = 60

    # lock mechanism introduced because there were issues when multiple job accessing the same file at the same time
    try:
        while timeout != 0:
            command = f'file {lock_file}'
            command_output = ExecuteCurlCommand.get_json_output(runtime_file_connection,
                                                                command, base_folder="/root")

            if 'No such file or directory' in command_output:
                log.info('Run time file is ready to use , aquiring lock ')
                try:
                    command = f'touch {lock_file}'
                    cm_out = ExecuteCurlCommand.get_json_output(runtime_file_connection,
                                                                command, base_folder="/root")
                except Exception as e:
                    log.info('Conflict while taking lock on run time %s', str(e))
                    log.info('retry after 1 second')
                    time.sleep(1)
                    timeout = timeout - 1
                    continue

                ServerConnection.get_file_sftp(runtime_file_connection, dest, data_file)
                Json_file_handler.modify_attribute(Json_file_handler, data_file, attribute, value)
                ServerConnection.put_file_sftp(runtime_file_connection, data_file, dest)

                log.info('releasing lock on runtime file ')
                command = f'rm -f {lock_file}'
                cm_out = ExecuteCurlCommand.get_json_output(runtime_file_connection,
                                                            command, base_folder="/root")

                break
            else:
                log.info('Some other process has a lock on runtime file')
                log.info('retry after 1 second')
                time.sleep(1)
                timeout = timeout - 1

        if timeout == 0:
            log.error('Process timed out while upadting runtime file , please check the logs ')
            assert False

    except Exception as e:
        log.error('Error while updating run time file attribute: %s ', str(e))
        assert False
    finally:
        log.info('Making sure lock file is cleaned up')
        command = f'ls {lock_file} && rm -f {lock_file}'
        cm_out = ExecuteCurlCommand.get_json_output(runtime_file_connection, command, base_folder="/root")
        runtime_file_connection.close()


def update_reconcile_onboard_file(file_name, file_data, package_name):
    log.info('Start to update ' + file_name)
    Report_file.add_line('Start to update ' + file_name)
    sit_data = SIT_initialization.get_model_objects(SIT_initialization, 'SIT')
    try:

        attribute_value_dict = {"tenantName": sit_data._SIT__tenantName, "name": package_name,
                                "softwareVersion": sit_data._SIT__softwareVersion, "isPublic": sit_data._SIT__isPublic,
                                "userDefinedData": file_data}
        vnfManagers_id = sit_data._SIT__vnfManagers
        Json_file_handler.modify_list_of_attributes(Json_file_handler, file_name, attribute_value_dict)
        Json_file_handler.update_any_json_attr(Json_file_handler, file_name, ["vnfManagers", 0], 'id', vnfManagers_id)

    except Exception as e:

        log.error('Error while updating %s, %s', file_name, str(e))
        Report_file.add_line('Error while updating ' + file_name + ' ERROR: ' + str(e))
        assert False
    log.info('Finished to update  %s', file_name)
    Report_file.add_line('Finished to update  ' + file_name)


def update_dummy_onboard_file(package_name):
    log.info('Start to update onboard.json file ')
    Report_file.add_line('Start to update onboard.json file')
    try:

        file_name = 'com_ericsson_do_auto_integration_files/on_board.json'
        sit_data = SIT_initialization.get_model_objects(SIT_initialization, 'SIT')

        sit_data._SIT__name = package_name

        log.info('package_name: %s', package_name)

        update_runtime_env_file('ONBOARD_PACKAGE', sit_data._SIT__name)

        block_attr = sit_data.block_data
        block_data = copy.deepcopy(block_attr)
        external_ip_for_services_vm = block_data['external_ip_for_services_vm']
        attribute_value_dict = {"tenantName": sit_data._SIT__tenantName, "name": sit_data._SIT__name,
                                "softwareVersion": sit_data._SIT__softwareVersion, "isPublic": sit_data._SIT__isPublic}
        vnfManagers_id = sit_data._SIT__vnfManagers
        vnfSoftwareVersion = sit_data._SIT__vnfSoftwareVersion
        Json_file_handler.modify_list_of_attributes(Json_file_handler, file_name, attribute_value_dict)
        Json_file_handler.modify_second_level_attr(Json_file_handler, file_name, 'vnfManagers', 0, 'id', vnfManagers_id)
        Json_file_handler.modify_nested_dict(Json_file_handler, file_name, 'userDefinedData', 'dataVNFDSpecific',
                                             'vnfSoftwareVersion', vnfSoftwareVersion)
        Json_file_handler.modify_first_level_attr(Json_file_handler, file_name, "userDefinedData",
                                                  "instantiateVnfOpConfig", block_data)
        Json_file_handler.modify_first_level_attr(Json_file_handler, file_name, "userDefinedData",
                                                  "terminateVnfOpConfig", block_data)

        ip_add_scaleVnfOpConfig = ipaddress.ip_address(external_ip_for_services_vm) + 1
        block_data['external_ip_for_services_vm'] = str(ip_add_scaleVnfOpConfig)
        Json_file_handler.modify_first_level_attr(Json_file_handler, file_name, "userDefinedData", "scaleVnfOpConfig",
                                                  block_data)
    except Exception as e:

        log.error('Error while updating onboarding.json file %s', str(e))
        Report_file.add_line('Error while updating onboarding.json file ,check logs for more details')
        assert False

    log.info('Finished to update onboard.json file ')
    Report_file.add_line('Finished to update onboard.json file')


def update_injest_file(file_name, VDC_ID, VNFM_ID, STACK_ID, STACK_NAME, VNFPACKGE_ID, VNF_NAME, VIMZONE_NAME):
    log.info('Start to update %s', file_name)
    Report_file.add_line('Start to update ' + file_name)
    ecm_host_data = Initialization_script.get_model_objects(Initialization_script, 'ECM_CORE')
    enm_data = Initialization_script.get_model_objects(Initialization_script, 'VNFM')
    ecm_hostname = ecm_host_data._Ecm_core__core_vm_hostname
    enm_hostname = ecm_host_data._Ecm_core__enm_hostname

    try:
        Json_file_handler.update_any_json_attr(Json_file_handler,
                                               r'com_ericsson_do_auto_integration_files/' + file_name,
                                               ['stackInfoList', 0], 'vdcId', VDC_ID)
        Json_file_handler.update_any_json_attr(Json_file_handler,
                                               r'com_ericsson_do_auto_integration_files/' + file_name,
                                               ['stackInfoList', 0], 'vnfmId', VNFM_ID)
        Json_file_handler.update_any_json_attr(Json_file_handler,
                                               r'com_ericsson_do_auto_integration_files/' + file_name,
                                               ['stackInfoList', 0], 'stackId', STACK_ID)
        Json_file_handler.update_any_json_attr(Json_file_handler,
                                               r'com_ericsson_do_auto_integration_files/' + file_name,
                                               ['stackInfoList', 0], 'stackName', STACK_NAME)
        Json_file_handler.update_any_json_attr(Json_file_handler,
                                               r'com_ericsson_do_auto_integration_files/' + file_name,
                                               ['stackInfoList', 0], 'vnfPackageId', VNFPACKGE_ID)
        Json_file_handler.update_any_json_attr(Json_file_handler,
                                               r'com_ericsson_do_auto_integration_files/' + file_name,
                                               ['stackInfoList', 0], 'vnfName', VNF_NAME)
        Json_file_handler.modify_attribute(Json_file_handler, r'com_ericsson_do_auto_integration_files/' + file_name,
                                           "vimZoneName", VIMZONE_NAME)

        log.info('Finished to update %s', file_name)
        Report_file.add_line('Finished to update ' + file_name)

    except Exception as e:

        log.error('Error while updating %s:  %s', file_name, str(e))
        Report_file.add_line('Error while updating ' + file_name + ',check logs for more details')
        assert False


def update_deploy_file(file_name='com_ericsson_do_auto_integration_files/deploy.json'):
    log.info('Start to update deploy.json file ')
    Report_file.add_line('Start to update deploy.json file')
    try:

        sit_data = SIT_initialization.get_model_objects(SIT_initialization, 'SIT')
        block_attr = sit_data.block_data
        block_data = copy.deepcopy(block_attr)
        attribute_value_dict = {"tenantName": sit_data._SIT__tenantName, "vimZoneName": sit_data._SIT__vimzone_name}
        Json_file_handler.modify_list_of_attributes(Json_file_handler, file_name, attribute_value_dict)

        vapp_name = sit_data._SIT__name
        log.info('Vapp Name : %s', vapp_name)
        vnfManagers_id = sit_data._SIT__vnfManagers
        vdc_id = sit_data._SIT__vdc_id
        Json_file_handler.modify_first_level_attr(Json_file_handler, file_name, "vapp", "name", vapp_name)
        Json_file_handler.modify_first_level_attr(Json_file_handler, file_name, "vapp", "deploymentParameters",
                                                  block_data)
        Json_file_handler.modify_first_level_attr(Json_file_handler, file_name, "vdc", "id", vdc_id)
        Json_file_handler.modify_first_level_attr(Json_file_handler, file_name, "vnfm", "id", vnfManagers_id)

    except Exception as e:

        log.error('Error while updating deploy.json file %s', str(e))
        Report_file.add_line('Error while updating deploy.json file ,check logs for more details')
        assert False
    log.info('Finished to update deploy.json file ')
    Report_file.add_line('Finished to update deploy.json file')


def update_terminate_file():
    log.info('Start to update terminate.json file ')
    Report_file.add_line('Start to update terminate.json file')
    try:
        file_name = 'com_ericsson_do_auto_integration_files/terminate.json'
        sit_data = SIT_initialization.get_model_objects(SIT_initialization, 'SIT')
        block_data = sit_data.block_data
        Json_file_handler.modify_attribute(Json_file_handler, file_name, "additionalParams", block_data)

    except Exception as e:

        log.error('Error while updating terminate.json file %s', str(e))
        Report_file.add_line('Error while updating terminate.json file ,check logs for more details')
        assert False
    log.info('Finished to update terminate.json file ')
    Report_file.add_line('Finished to update terminate.json file')


def update_vnflaf_yaml(
        file_name='com_ericsson_do_auto_integration_files/vnflaf/Resources/EnvironmentFiles/vnflaf_cee-env.yaml'):
    log.info('Start to update vnflaf_cee-env.yaml file ')
    Report_file.add_line('Start to update vnflaf_cee-env.yaml file')
    try:

        sit_data = SIT_initialization.get_model_objects(SIT_initialization, 'SIT')
        block_data = sit_data.block_data
        Json_file_handler.update_yaml(Json_file_handler, file_name, 'parameters', block_data)
        log.info('Finished to update vnflaf_cee-env.yaml file ')
    except Exception as e:

        log.error('Error while updating terminate.json file %s', str(e))
        Report_file.add_line('Error while updating vnflaf_cee-env.yaml file ,check logs for more details')
        assert False
    log.info('Finished to update vnflaf_cee-env.yaml file ')
    Report_file.add_line('Finished to update vnflaf_cee-env.yaml file')


def update_VNFD_wrapper(
        file_name=r'com_ericsson_do_auto_integration_files/vnflaf/Resources/VnfdWrapperFiles/VNFD_Wrapper_VNFLAF.json'):
    log.info('Start to update VNFD_Wrapper_VNFLAF.json file ')
    Report_file.add_line('Start to update VNFD_Wrapper_VNFLAF.json file')
    try:

        sit_data = SIT_initialization.get_model_objects(SIT_initialization, 'SIT')
        vnfSoftwareVersion = sit_data._SIT__vnfSoftwareVersion
        Json_file_handler.modify_first_level_attr(Json_file_handler, file_name, 'dataVNFDSpecific',
                                                  'vnfSoftwareVersion', vnfSoftwareVersion)
        block_attr = sit_data.block_data
        block_data = copy.deepcopy(block_attr)
        external_ip_for_services_vm = block_data['external_ip_for_services_vm']
        Json_file_handler.modify_nested_list_of_attributes(Json_file_handler, file_name, 'instantiateVnfOpConfig',
                                                           block_data)
        Json_file_handler.modify_nested_list_of_attributes(Json_file_handler, file_name, 'terminateVnfOpConfig',
                                                           block_data)
        ip_add_scaleVnfOpConfig = ipaddress.ip_address(external_ip_for_services_vm) + 1
        block_data['external_ip_for_services_vm'] = str(ip_add_scaleVnfOpConfig)
        Json_file_handler.modify_nested_list_of_attributes(Json_file_handler, file_name, 'scaleVnfOpConfig', block_data)


    except Exception as e:

        log.error('Error while updating VNFD_Wrapper_VNFLAF.json file %s', str(e))
        Report_file.add_line('Error while updating VNFD_Wrapper_VNFLAF.json file ,check logs for more details')
        assert False
    log.info('Finished to update VNFD_Wrapper_VNFLAF.json file ')
    Report_file.add_line('Finished to update VNFD_Wrapper_VNFLAF.json file')


def update_VNFD_wrapper_SCALE_OUT(file_name):
    log.info('Start to update VNFD_Wrapper_VNFLAF.json file for SCALE_OUT ')
    Report_file.add_line('Start to update VNFD_Wrapper_VNFLAF.json file for SCALE_OUT')
    try:

        sit_data = SIT_initialization.get_model_objects(SIT_initialization, 'SIT')
        vnfSoftwareVersion = sit_data._SIT__vnfSoftwareVersion
        external_ip_for_services_vm_to_scale = sit_data._SIT__externalIpForServicesVmToScale

        Json_file_handler.modify_first_level_attr(Json_file_handler,
                                                  r'com_ericsson_do_auto_integration_files/vnflaf/Resources/VnfdWrapperFiles/' + file_name,
                                                  'dataVNFDSpecific',
                                                  'vnfSoftwareVersion', vnfSoftwareVersion)
        block_attr = sit_data.block_data
        block_data = copy.deepcopy(block_attr)

        servicesImage_scaleout = block_data['servicesImage'] + ',' + block_data['servicesImage']
        block_data['servicesImage'] = servicesImage_scaleout
        block_data['services_vm_count'] = 2

        external_ip_for_services_vm = block_data[
                                          'external_ip_for_services_vm'] + ',' + external_ip_for_services_vm_to_scale
        block_data['external_ip_for_services_vm'] = external_ip_for_services_vm
        Json_file_handler.modify_nested_list_of_attributes(Json_file_handler,
                                                           r'com_ericsson_do_auto_integration_files/vnflaf/Resources/VnfdWrapperFiles/' + file_name,
                                                           'scaleVnfOpConfig',
                                                           block_data)


    except Exception as e:

        log.error('Error while updating VNFD_Wrapper_VNFLAF.json file  for scale out %s', str(e))
        Report_file.add_line(
            'Error while updating VNFD_Wrapper_VNFLAF.json file for scale out ,check logs for more details')
        assert False
    log.info('Finished to update VNFD_Wrapper_VNFLAF.json file for scale out')
    Report_file.add_line('Finished to update VNFD_Wrapper_VNFLAF.json file for scale out')


def update_VNFD_wrapper_SCALE_IN(file_name):
    log.info('Start to update VNFD_Wrapper_VNFLAF.json file for SCALE_IN')
    Report_file.add_line('Start to update VNFD_Wrapper_VNFLAF.json file for SCALE_IN')
    try:

        sit_data = SIT_initialization.get_model_objects(SIT_initialization, 'SIT')

        block_attr = sit_data.block_data
        block_data = copy.deepcopy(block_attr)

        Json_file_handler.modify_nested_list_of_attributes(Json_file_handler,
                                                           r'com_ericsson_do_auto_integration_files/vnflaf/Resources/VnfdWrapperFiles/' + file_name,
                                                           'scaleVnfOpConfig',
                                                           block_data)

    except Exception as e:

        log.error('Error while updating VNFD_Wrapper_VNFLAF.json file for ScaleIn %s', str(e))
        Report_file.add_line(
            'Error while updating VNFD_Wrapper_VNFLAF.json file for ScaleIn ,check logs for more details')
        assert False
    log.info('Finished to update VNFD_Wrapper_VNFLAF.json file for ScaleIn ')
    Report_file.add_line('Finished to update VNFD_Wrapper_VNFLAF.json file for ScaleIn')


def update_VNFD_wrapper_HEAL(file_name):
    log.info('Start to update VNFD_Wrapper_VNFLAF.json file for HEAL')
    Report_file.add_line('Start to update VNFD_Wrapper_VNFLAF.json file for HEAL')
    try:

        sit_data = SIT_initialization.get_model_objects(SIT_initialization, 'SIT')

        block_attr = sit_data.block_data
        block_data = copy.deepcopy(block_attr)

        Json_file_handler.modify_nested_list_of_attributes(Json_file_handler,
                                                           r'com_ericsson_do_auto_integration_files/vnflaf/Resources/VnfdWrapperFiles/' + file_name,
                                                           'healVnfOpConfig',
                                                           block_data)

    except Exception as e:

        log.error('Error while updating VNFD_Wrapper_VNFLAF.json file for HEAL %s', str(e))
        Report_file.add_line('Error while updating VNFD_Wrapper_VNFLAF.json file for HEAL ,check logs for more details')
        assert False
    log.info('Finished to update VNFD_Wrapper_VNFLAF.json file for HEAL ')
    Report_file.add_line('Finished to update VNFD_Wrapper_VNFLAF.json file for HEAL')


def update_epg_onboard_file(file_name, file_data, package_name):
    log.info('Start to update %s', file_name)
    Report_file.add_line('Start to update ' + file_name)
    sit_data = SIT_initialization.get_model_objects(SIT_initialization, 'SIT')
    try:
        update_runtime_env_file('ONBOARD_EPG_PACKAGE', package_name)
        attribute_value_dict = {"tenantName": sit_data._SIT__tenantName, "name": package_name,
                                "softwareVersion": sit_data._SIT__softwareVersion, "isPublic": sit_data._SIT__isPublic,
                                "userDefinedData": file_data}
        vnfManagers_id = sit_data._SIT__vnfManagers
        Json_file_handler.modify_list_of_attributes(Json_file_handler, file_name, attribute_value_dict)
        Json_file_handler.update_any_json_attr(Json_file_handler, file_name, ["vnfManagers", 0], 'id', vnfManagers_id)

    except Exception as e:

        log.error('Error while updating %s:  %s', file_name, str(e))
        Report_file.add_line('Error while updating ' + file_name + ' ERROR: ' + str(e))
        assert False
    log.info('Finished to update  %s', file_name)
    Report_file.add_line('Finished to update  ' + file_name)


def update_mme_node_onboard_file(file_name, file_data, package_name):
    log.info('Start to update %s', file_name)
    Report_file.add_line('Start to update ' + file_name)
    sit_data = SIT_initialization.get_model_objects(SIT_initialization, 'SIT')
    try:
        update_runtime_env_file('ONBOARD_MME_PACKAGE', package_name)
        attribute_value_dict = {"tenantName": sit_data._SIT__tenantName, "name": package_name,
                                "softwareVersion": sit_data._SIT__softwareVersion, "isPublic": sit_data._SIT__isPublic,
                                "userDefinedData": file_data}
        vnfManagers_id = sit_data._SIT__vnfManagers
        Json_file_handler.modify_list_of_attributes(Json_file_handler, file_name, attribute_value_dict)
        Json_file_handler.update_any_json_attr(Json_file_handler, file_name, ["vnfManagers", 0], 'id', vnfManagers_id)

    except Exception as e:

        log.error('Error while updating %s: %s ', file_name, str(e))
        Report_file.add_line('Error while updating ' + file_name + ' ERROR: ' + str(e))
        assert False
    log.info('Finished to update  %s', file_name)
    Report_file.add_line('Finished to update  ' + file_name)


def update_bgf_onboard_file(file_name, file_data, package_name):
    log.info('Start to update %s', file_name)
    Report_file.add_line('Start to update ' + file_name)
    sit_data = SIT_initialization.get_model_objects(SIT_initialization, 'SIT')
    try:

        attribute_value_dict = {"tenantName": sit_data._SIT__tenantName, "name": package_name,
                                "softwareVersion": sit_data._SIT__softwareVersion, "isPublic": sit_data._SIT__isPublic,
                                "userDefinedData": file_data}
        vnfManagers_id = sit_data._SIT__vnfManagers
        Json_file_handler.modify_list_of_attributes(Json_file_handler, file_name, attribute_value_dict)
        Json_file_handler.update_any_json_attr(Json_file_handler, file_name, ["vnfManagers", 0], 'id', vnfManagers_id)

    except Exception as e:

        log.error('Error while updating %s: %s', file_name, str(e))
        Report_file.add_line('Error while updating ' + file_name + ' ERROR: ' + str(e))
        assert False
    log.info('Finished to update  ', file_name)
    Report_file.add_line('Finished to update  ' + file_name)


def update_sbg_onboard_file(file_name, file_data, package_name):
    log.info('Start to update %s', file_name)
    Report_file.add_line('Start to update ' + file_name)
    sit_data = SIT_initialization.get_model_objects(SIT_initialization, 'SIT')
    try:

        attribute_value_dict = {"tenantName": sit_data._SIT__tenantName, "name": package_name,
                                "softwareVersion": sit_data._SIT__softwareVersion, "isPublic": sit_data._SIT__isPublic,
                                "userDefinedData": file_data}
        vnfManagers_id = sit_data._SIT__vnfManagers
        Json_file_handler.modify_list_of_attributes(Json_file_handler, file_name, attribute_value_dict)
        Json_file_handler.update_any_json_attr(Json_file_handler, file_name, ["vnfManagers", 0], 'id', vnfManagers_id)

    except Exception as e:

        log.error('Error while updating %s: %s', file_name, str(e))
        Report_file.add_line('Error while updating ' + file_name + ' ERROR: ' + str(e))
        assert False
    log.info('Finished to update  %s', file_name)
    Report_file.add_line('Finished to update  ' + file_name)


def update_mtas_onboard_file(file_name, file_data, package_name):
    log.info('Start to update %s', file_name)
    Report_file.add_line('Start to update ' + file_name)
    sit_data = SIT_initialization.get_model_objects(SIT_initialization, 'SIT')
    try:

        attribute_value_dict = {"tenantName": sit_data._SIT__tenantName, "name": package_name,
                                "softwareVersion": sit_data._SIT__softwareVersion, "isPublic": sit_data._SIT__isPublic,
                                "userDefinedData": file_data}
        vnfManagers_id = sit_data._SIT__vnfManagers
        Json_file_handler.modify_list_of_attributes(Json_file_handler, file_name, attribute_value_dict)
        Json_file_handler.update_any_json_attr(Json_file_handler, file_name, ["vnfManagers", 0], 'id', vnfManagers_id)

    except Exception as e:

        log.error('Error while updating %s: %s', file_name, str(e))
        Report_file.add_line('Error while updating ' + file_name + ' ERROR: ' + str(e))
        assert False
    log.info('Finished to update  %s', file_name)
    Report_file.add_line('Finished to update  ' + file_name)


def update_cscf_onboard_file(file_name, file_data, package_name):
    log.info('Start to update %s', file_name)
    Report_file.add_line('Start to update ' + file_name)
    sit_data = SIT_initialization.get_model_objects(SIT_initialization, 'SIT')
    try:

        attribute_value_dict = {"tenantName": sit_data._SIT__tenantName, "name": package_name,
                                "softwareVersion": sit_data._SIT__softwareVersion, "isPublic": sit_data._SIT__isPublic,
                                "userDefinedData": file_data}
        vnfManagers_id = sit_data._SIT__vnfManagers
        Json_file_handler.modify_list_of_attributes(Json_file_handler, file_name, attribute_value_dict)
        Json_file_handler.update_any_json_attr(Json_file_handler, file_name, ["vnfManagers", 0], 'id', vnfManagers_id)

    except Exception as e:

        log.error('Error while updating %s: %s', file_name, str(e))
        Report_file.add_line('Error while updating ' + file_name + ' ERROR: ' + str(e))
        assert False
    log.info('Finished to update  %s', file_name)
    Report_file.add_line('Finished to update  ' + file_name)


def update_epg_deploy_file(file_name, file_data, vapp_name):
    log.info('Start to update %s', file_name)
    Report_file.add_line('Start to update ' + file_name)
    try:
        sit_data = SIT_initialization.get_model_objects(SIT_initialization, 'SIT')

        attribute_value_dict = {"tenantName": sit_data._SIT__tenantName, "vimZoneName": sit_data._SIT__vimzone_name}
        Json_file_handler.modify_list_of_attributes(Json_file_handler, file_name, attribute_value_dict)
        deployment_params = file_data['instantiateVnfOpConfig']

        log.info('EPG node  Name : %s', vapp_name)
        vnfManagers_id = sit_data._SIT__vnfManagers
        vdc_id = sit_data._SIT__vdc_id
        Json_file_handler.modify_first_level_attr(Json_file_handler, file_name, "vapp", "name", vapp_name)
        Json_file_handler.modify_first_level_attr(Json_file_handler, file_name, "vapp", "deploymentParameters",
                                                  deployment_params)
        Json_file_handler.modify_first_level_attr(Json_file_handler, file_name, "vdc", "id", vdc_id)
        Json_file_handler.modify_first_level_attr(Json_file_handler, file_name, "vnfm", "id", vnfManagers_id)

    except Exception as e:

        log.error('Error while updating %s: %s', file_name, str(e))
        Report_file.add_line('Error while updating ' + file_name + ' file ,check logs for more details')
        assert False
    log.info('Finished to update %s', file_name)
    Report_file.add_line('Finished to update ' + file_name)


def update_mme_deploy_file(file_name, file_data, vapp_name):
    log.info('Start to update %s', file_name)
    Report_file.add_line('Start to update ' + file_name)
    try:
        sit_data = SIT_initialization.get_model_objects(SIT_initialization, 'SIT')

        attribute_value_dict = {"tenantName": sit_data._SIT__tenantName, "vimZoneName": sit_data._SIT__vimzone_name}
        Json_file_handler.modify_list_of_attributes(Json_file_handler, file_name, attribute_value_dict)
        deployment_params = file_data['instantiateVnfOpConfig']

        log.info('MME node  Name : %s', vapp_name)
        vnfManagers_id = sit_data._SIT__vnfManagers
        vdc_id = sit_data._SIT__vdc_id
        Json_file_handler.modify_first_level_attr(Json_file_handler, file_name, "vapp", "name", vapp_name)
        Json_file_handler.modify_first_level_attr(Json_file_handler, file_name, "vapp", "deploymentParameters",
                                                  deployment_params)
        Json_file_handler.modify_first_level_attr(Json_file_handler, file_name, "vdc", "id", vdc_id)
        Json_file_handler.modify_first_level_attr(Json_file_handler, file_name, "vnfm", "id", vnfManagers_id)

    except Exception as e:

        log.error('Error while updating %s: %s', file_name, str(e))
        Report_file.add_line('Error while updating ' + file_name + ' file ,check logs for more details')
        assert False
    log.info('Finished to update %s', file_name)
    Report_file.add_line('Finished to update ' + file_name)


def update_dummy_mme_deploy_file(name, package_name, flavor_name, image_id):
    file_name = r'com_ericsson_do_auto_integration_files/' + name
    log.info('Start to update %s', file_name)
    Report_file.add_line('Start to update ' + file_name)

    try:
        sit_data = SIT_initialization.get_model_objects(SIT_initialization, 'SIT')
        attribute_value_dict = {"tenantName": sit_data._SIT__tenantName, "vimZoneName": sit_data._SIT__vimzone_name}
        Json_file_handler.modify_list_of_attributes(Json_file_handler, file_name, attribute_value_dict)
        vdc_id = sit_data._SIT__vdc_id
        Json_file_handler.modify_first_level_attr(Json_file_handler, file_name, "vdc", "id", vdc_id)
        Json_file_handler.update_any_json_attr(Json_file_handler, file_name, ["hotPackage", "vapp"], "name",
                                               package_name)
        Json_file_handler.update_any_json_attr(Json_file_handler, file_name, ["hotPackage", "vapp", "configData", 0],
                                               "value", flavor_name)
        Json_file_handler.update_any_json_attr(Json_file_handler, file_name, ["hotPackage", "vapp", "configData", 1],
                                               "value", image_id)

    except Exception as e:

        log.error('Error while updating %s: %s', file_name, str(e))
        Report_file.add_line('Error while updating ' + file_name + ' file ,check logs for more details')
        assert False
    log.info('Finished to update %s', file_name)
    Report_file.add_line('Finished to update ' + file_name)


def update_sol_bgf_deploy_file(name, package_name, external_network_id, sub_network_id):
    file_name = r'com_ericsson_do_auto_integration_files/' + name
    log.info('Start to update %s', file_name)
    Report_file.add_line('Start to update ' + file_name)

    try:
        sit_data = SIT_initialization.get_model_objects(SIT_initialization, 'SIT')
        attribute_value_dict = {"tenantName": sit_data._SIT__tenantName, "vimZoneName": sit_data._SIT__vimzone_name}
        Json_file_handler.modify_list_of_attributes(Json_file_handler, file_name, attribute_value_dict)
        vdc_id = sit_data._SIT__vdc_id

        tosca_bgf_ip = sit_data._SIT__bgf_tosca_ip
        Json_file_handler.modify_first_level_attr(Json_file_handler, file_name, "vdc", "id", vdc_id)
        Json_file_handler.update_any_json_attr(Json_file_handler, file_name, ["hotPackage", "vapp"], "name",
                                               package_name)
        Json_file_handler.update_any_json_attr(Json_file_handler, file_name, ["hotPackage", "vapp", "configData", 0],
                                               "value", sub_network_id)
        Json_file_handler.update_any_json_attr(Json_file_handler, file_name, ["hotPackage", "vapp", "configData", 1],
                                               "value", external_network_id)
        Json_file_handler.update_any_json_attr(Json_file_handler, file_name, ["hotPackage", "vapp", "configData", 3],
                                               "value", tosca_bgf_ip)

    except Exception as e:

        log.error('Error while updating %s: %s', file_name, str(e))
        Report_file.add_line('Error while updating ' + file_name + ' file ,check logs for more details')
        assert False
    log.info('Finished to update %s', file_name)
    Report_file.add_line('Finished to update ' + file_name)


def update_nsd_create_package_file(filename, packageName):
    log.info('Start to update %s file to create NSD package', filename)
    Report_file.add_line('Start to update ' + filename + ' file to create NSD package')
    try:
        Json_file_handler.update_any_json_attr(Json_file_handler, r'com_ericsson_do_auto_integration_files/' + filename,
                                               ['ericssonNfvoData'], 'packageName', packageName)

    except Exception as e:
        log.error('Error while updating NSD %s: %s', filename, str(e))
        Report_file.add_line('Error while updating NSD ' + filename + ' ' + str(e))
        assert False


def update_onboard_sol_bgf_file(file_name, package_name, name):
    log.info('Start to update %s', file_name)

    Report_file.add_line('Start to update ' + file_name)

    sit_data = SIT_initialization.get_model_objects(SIT_initialization, 'SIT')

    file_path = r'com_ericsson_do_auto_integration_files/' + file_name

    try:

        vnfManagers_id = sit_data._SIT__vnfManagers

        Json_file_handler.update_any_json_attr(Json_file_handler, file_path, [], 'fileName', package_name)

        Json_file_handler.update_any_json_attr(Json_file_handler, file_path, [], 'name', name)

        Json_file_handler.update_any_json_attr(Json_file_handler, file_path, ["vnfManagers", 0], 'id', vnfManagers_id)

    except Exception as e:

        log.error('Error while updating %s: %s', file_name, str(e))

        Report_file.add_line('Error while updating ' + file_name + ' file ,check logs for more details')
        assert False
    log.info('Finished to update file %s', file_name)

    Report_file.add_line('Finished to update ' + file_name + ' file')


def update_bgf_deploy_file(file_name, file_data, vapp_name):
    log.info('Start to update %s', file_name)
    Report_file.add_line('Start to update ' + file_name)
    try:
        sit_data = SIT_initialization.get_model_objects(SIT_initialization, 'SIT')

        attribute_value_dict = {"tenantName": sit_data._SIT__tenantName, "vimZoneName": sit_data._SIT__vimzone_name}
        Json_file_handler.modify_list_of_attributes(Json_file_handler, file_name, attribute_value_dict)
        deployment_params = file_data['instantiateVnfOpConfig']

        log.info('BGF node  Name : %s', vapp_name)
        vnfManagers_id = sit_data._SIT__vnfManagers
        vdc_id = sit_data._SIT__vdc_id
        Json_file_handler.modify_first_level_attr(Json_file_handler, file_name, "vapp", "name", vapp_name)
        Json_file_handler.modify_first_level_attr(Json_file_handler, file_name, "vapp", "deploymentParameters",
                                                  deployment_params)
        Json_file_handler.modify_first_level_attr(Json_file_handler, file_name, "vdc", "id", vdc_id)
        Json_file_handler.modify_first_level_attr(Json_file_handler, file_name, "vnfm", "id", vnfManagers_id)

    except Exception as e:

        log.error('Error while updating %s: %s', file_name, str(e))
        Report_file.add_line('Error while updating ' + file_name + ' file ,check logs for more details')

    log.info('Finished to update %s', file_name)
    Report_file.add_line('Finished to update ' + file_name)


def update_sbg_deploy_file(file_name, file_data, vapp_name):
    log.info('Start to update %s', file_name)
    Report_file.add_line('Start to update ' + file_name)
    try:
        sit_data = SIT_initialization.get_model_objects(SIT_initialization, 'SIT')

        attribute_value_dict = {"tenantName": sit_data._SIT__tenantName, "vimZoneName": sit_data._SIT__vimzone_name}
        Json_file_handler.modify_list_of_attributes(Json_file_handler, file_name, attribute_value_dict)
        deployment_params = file_data['instantiateVnfOpConfig']

        log.info('SBG node  Name : %s', vapp_name)
        vnfManagers_id = sit_data._SIT__vnfManagers
        vdc_id = sit_data._SIT__vdc_id
        Json_file_handler.modify_first_level_attr(Json_file_handler, file_name, "vapp", "name", vapp_name)
        Json_file_handler.modify_first_level_attr(Json_file_handler, file_name, "vapp", "deploymentParameters",
                                                  deployment_params)
        Json_file_handler.modify_first_level_attr(Json_file_handler, file_name, "vdc", "id", vdc_id)
        Json_file_handler.modify_first_level_attr(Json_file_handler, file_name, "vnfm", "id", vnfManagers_id)

    except Exception as e:

        log.error('Error while updating %s: %s', file_name, str(e))
        Report_file.add_line('Error while updating ' + file_name + ' file ,check logs for more details')

    log.info('Finished to update %s', file_name)
    Report_file.add_line('Finished to update ' + file_name)


def update_mtas_deploy_file(file_name, file_data, vapp_name):
    log.info('Start to update %s', file_name)
    Report_file.add_line('Start to update ' + file_name)
    try:
        sit_data = SIT_initialization.get_model_objects(SIT_initialization, 'SIT')

        attribute_value_dict = {"tenantName": sit_data._SIT__tenantName, "vimZoneName": sit_data._SIT__vimzone_name}
        Json_file_handler.modify_list_of_attributes(Json_file_handler, file_name, attribute_value_dict)
        deployment_params = file_data['instantiateVnfOpConfig']

        log.info('MTAS node  Name : %s', vapp_name)
        vnfManagers_id = sit_data._SIT__vnfManagers
        vdc_id = sit_data._SIT__vdc_id
        Json_file_handler.modify_first_level_attr(Json_file_handler, file_name, "vapp", "name", vapp_name)
        Json_file_handler.modify_first_level_attr(Json_file_handler, file_name, "vapp", "deploymentParameters",
                                                  deployment_params)
        Json_file_handler.modify_first_level_attr(Json_file_handler, file_name, "vdc", "id", vdc_id)
        Json_file_handler.modify_first_level_attr(Json_file_handler, file_name, "vnfm", "id", vnfManagers_id)

    except Exception as e:

        log.error('Error while updating %s: %s', file_name, str(e))
        Report_file.add_line('Error while updating ' + file_name + ' file ,check logs for more details')

    log.info('Finished to update %s', file_name)
    Report_file.add_line('Finished to update ' + file_name)


def update_cscf_deploy_file(file_name, file_data, vapp_name):
    log.info('Start to update %s', file_name)
    Report_file.add_line('Start to update ' + file_name)
    try:
        sit_data = SIT_initialization.get_model_objects(SIT_initialization, 'SIT')

        attribute_value_dict = {"tenantName": sit_data._SIT__tenantName, "vimZoneName": sit_data._SIT__vimzone_name}
        Json_file_handler.modify_list_of_attributes(Json_file_handler, file_name, attribute_value_dict)
        deployment_params = file_data['instantiateVnfOpConfig']

        log.info('CSCF node  Name : %s', vapp_name)
        vnfManagers_id = sit_data._SIT__vnfManagers
        vdc_id = sit_data._SIT__vdc_id
        Json_file_handler.modify_first_level_attr(Json_file_handler, file_name, "vapp", "name", vapp_name)
        Json_file_handler.modify_first_level_attr(Json_file_handler, file_name, "vapp", "deploymentParameters",
                                                  deployment_params)
        Json_file_handler.modify_first_level_attr(Json_file_handler, file_name, "vdc", "id", vdc_id)
        Json_file_handler.modify_first_level_attr(Json_file_handler, file_name, "vnfm", "id", vnfManagers_id)

    except Exception as e:

        log.error('Error while updating %s: %s', file_name, str(e))
        Report_file.add_line('Error while updating ' + file_name + ' file ,check logs for more details')

    log.info('Finished to update %s', file_name)
    Report_file.add_line('Finished to update ' + file_name)


def update_ovf_deploy_file(file_name):
    log.info('Start to update deploy_ovf.json file ')
    Report_file.add_line('Start to update deploy_ovf.json file')
    try:

        sit_data = SIT_initialization.get_model_objects(SIT_initialization, 'SIT')
        attribute_value_dict = {"tenantName": sit_data._SIT__tenantName, "vimZoneName": sit_data._SIT__vimzone_name}
        Json_file_handler.modify_list_of_attributes(Json_file_handler,
                                                    r'com_ericsson_do_auto_integration_files/' + file_name,
                                                    attribute_value_dict)
        vdc_id = sit_data._SIT__vdc_id
        Json_file_handler.modify_first_level_attr(Json_file_handler,
                                                  r'com_ericsson_do_auto_integration_files/' + file_name, "vdc", "id",
                                                  vdc_id)


    except Exception as e:

        log.error('Error while updating deploy_ovf.json file %s', str(e))
        Report_file.add_line('Error while updating deploy_ovf.json file ,check logs for more details')

    log.info('Finished to update deploy_ovf.json file ')
    Report_file.add_line('Finished to update deploy_ovf.json file')


def update_create_device_file(file_name):
    try:
        log.info('Start to update createdevice.json file ')
        Report_file.add_line('Start to update createdevice.json file')
        file_name = 'com_ericsson_do_auto_integration_files/createdevice.json'

        ecm_host_data = ECM_PI_Initialization.get_model_objects(ECM_PI_Initialization, 'ECMPI')
        vcisco_management_ip = ecm_host_data._Ecm_PI__vCisco_Management_ip
        vcisco_management_username = ecm_host_data._Ecm_PI__vCisco_Management_username
        vcisco_management_password = ecm_host_data._Ecm_PI__vCisco_Management_Password
        asr_device_name = ecm_host_data._Ecm_PI__asr_device_name
        management_ip_port = vcisco_management_ip + ':22'

        Json_file_handler.update_any_json_attr(Json_file_handler, file_name, [], 'masterIdentifier', asr_device_name)
        Json_file_handler.update_any_json_attr(Json_file_handler, file_name, ['accessPoints', 0, 'credentials'],
                                               'username', vcisco_management_username)
        Json_file_handler.update_any_json_attr(Json_file_handler, file_name, ['accessPoints', 0, 'credentials'],
                                               'password', vcisco_management_password)
        Json_file_handler.update_any_json_attr(Json_file_handler, file_name, ['accessPoints', 0], 'address',
                                               management_ip_port)


    except Exception as e:

        log.error('Error while updating create_device.json file %s', str(e))
        Report_file.add_line('Error while updating create_device.json file ,check logs for more details')

    log.info('Finished to update create_device.json file ')
    Report_file.add_line('Finished to update create_device.json file')


def update_transfer_securitygroup(file_name):
    log.info('Start to update transferSecurityGroup.json file ')
    Report_file.add_line('Start to transferSecurityGroup.json file')
    try:
        sit_data = SIT_initialization.get_model_objects(SIT_initialization, 'SIT')
        vimzone_id = sit_data._SIT__vimzone_id
        Json_file_handler.modify_second_level_attr(Json_file_handler,
                                                   'com_ericsson_do_auto_integration_files/' + file_name, 'vimZones', 0,
                                                   'id', vimzone_id)
    except Exception as e:
        log.error('Error while updating transferSecurityGroup.json file %s', str(e))
        Report_file.add_line('Error while updating transferSecurityGroup.json file ,check logs for more details')
    log.info('Finished to update transferSecurityGroup.json file ')
    Report_file.add_line('Finished to update transferSecurityGroup.json file')


def update_vcisco_deploy_file(file_name):
    try:
        log.info('Start to update ASR_VM_DEPLOY.json file ')
        Report_file.add_line('Start to update ASR_VM_DEPLOY.json file')
        file_name1 = 'com_ericsson_do_auto_integration_files/' + file_name
        EPIS_data = ECM_PI_Initialization.get_model_objects(ECM_PI_Initialization, 'EPIS')
        sit_data = SIT_initialization.get_model_objects(SIT_initialization, 'SIT')
        ecm_host_data = ECM_PI_Initialization.get_model_objects(ECM_PI_Initialization, 'ECMPI')

        vdc_id = sit_data._SIT__vdc_id
        vCisco_image_name = sit_data._SIT__vcisco_image_name
        vCisco_flavor = sit_data._SIT__vcisco_flavour_name
        vcisco_name = vCisco_flavor[3:]
        vimzone_name = sit_data._SIT__vimzone_name
        vcisco_management_ip = ecm_host_data._Ecm_PI__vCisco_Management_ip

        tenant_name = EPIS_data._EPIS__tenant_name
        Json_file_handler.update_any_json_attr(Json_file_handler, file_name1, [], 'tenantName', tenant_name)

        Json_file_handler.update_any_json_attr(Json_file_handler, file_name1,
                                               ['orderItems', 0, 'createVm', 'bootSource'], 'imageName',
                                               vCisco_image_name)
        Json_file_handler.update_any_json_attr(Json_file_handler, file_name1, ['orderItems', 0, 'createVm'], 'vmhdName',
                                               vcisco_name)
        Json_file_handler.update_any_json_attr(Json_file_handler, file_name1, ['orderItems', 0, 'createVm', 'vdc'],
                                               'id', vdc_id)
        Json_file_handler.update_any_json_attr(Json_file_handler, file_name1, ['orderItems', 0, 'createVm'],
                                               'vimZoneName', vimzone_name)
        Json_file_handler.update_any_json_attr(Json_file_handler, file_name1, ['orderItems', 1, 'createVmVnic'],
                                               'internalIpAddress', [vcisco_management_ip])


    except Exception as e:

        log.error('Error while updating ASR_VM_DEPLOY.json file %s', str(e))
        Report_file.add_line('Error while updating ASR_VM_DEPLOY.json file ,check logs for more details')

    log.info('Finished to update ASR_VM_DEPLOY.json file ')
    Report_file.add_line('Finished to update ASR_VM_DEPLOY.json file')


def update_activation_gui_password(file_name):
    try:
        log.info('Start to update activation_gui_password.json file ')
        Report_file.add_line('Start to update activation_gui_password.json file')
        file_name = 'com_ericsson_do_auto_integration_files/activation_gui_password.json'
        ecm_host_data = ECM_PI_Initialization.get_model_objects(ECM_PI_Initialization, 'ECMPI')
        act_gui_username = ecm_host_data._Ecm_PI__activation_gui_username
        act_gui_password = ecm_host_data._Ecm_PI__activation_gui_password
        Json_file_handler.update_any_json_attr(Json_file_handler, file_name, [], 'username', act_gui_username)
        Json_file_handler.update_any_json_attr(Json_file_handler, file_name, [], 'new_password', act_gui_password)

    except Exception as e:

        log.error('Error while updating activation_gui_password.json file %s', str(e))
        Report_file.add_line('Error while updating activation_gui_password.json file ,check logs for more details')

    log.info('Finished to update activation_gui_password.json file ')
    Report_file.add_line('Finished to update activation_gui_password.json file')


def update_reconcile_stack_file(file_name, flavour, volume_id, image_id, usecase_name):
    try:
        log.info('Start updating and  transferring reconcile-stack file to openstack ')
        Report_file.add_line('Start updating and  transferring reconcile-stack file to openstack ')

        EPIS_data = ECM_PI_Initialization.get_model_objects(ECM_PI_Initialization, 'EPIS')
        sit_data = SIT_initialization.get_model_objects(SIT_initialization, 'SIT')
        openstack_ip = EPIS_data._EPIS__openstack_ip
        username = EPIS_data._EPIS__openstack_username
        password = EPIS_data._EPIS__openstack_password
        openrc_filename = EPIS_data._EPIS__openrc_filename
        package_name = sit_data._SIT__name

        file_path = 'com_ericsson_do_auto_integration_files/' + file_name
        if usecase_name == '3':
            attribute_list1 = ['resources', 'Server_2', 'properties']
            attribute_list2 = ['resources', 'volume_attachment_2', 'properties']

        else:
            attribute_list1 = ['resources', 'Server_1', 'properties']
            attribute_list2 = ['resources', 'volume_attachment_1', 'properties']

        Json_file_handler.update_nested_dict_yaml(Json_file_handler, file_path, attribute_list1, 'flavor',
                                                  flavour)
        Json_file_handler.update_nested_dict_yaml(Json_file_handler, file_path, attribute_list1, 'image', image_id)

        Json_file_handler.update_nested_dict_yaml(Json_file_handler, file_path, attribute_list2, 'volume_id',
                                                  volume_id)

        connection = ServerConnection.get_connection(openstack_ip, username, password)

        ServerConnection.put_file_sftp(connection, file_path, r'/root/' + file_name)

        log.info('Connecting with open stack to run stack update command  %s', openstack_ip)
        ShellHandler.__init__(ShellHandler, openstack_ip, username, password)
        command = 'source {}'.format(openrc_filename)
        stdin, stdout, stderr = ShellHandler.execute(ShellHandler, command)
        command = 'openstack stack update --template {} {} --wait'.format(file_name, package_name)
        stdin, stdout, stderr = ShellHandler.execute(ShellHandler, command)
        output = str(stdout)

        Report_file.add_line('command output ' + output)
        Report_file.add_line('command output error ' + str(stderr))

        if 'UPDATE_COMPLETE' in output:

            log.info('Finished updating and  transferring reconcile-stack file to open stack ')
            Report_file.add_line('Finished updating and  transferring reconcile-stack file to open stack ')
            ShellHandler.__del__(ShellHandler)


        else:
            log.error('Error updating and transferring reconcile-stack file to open stack ')
            Report_file.add_line('Error updating and transferring reconcile-stack file to open stack ')
            ShellHandler.__del__(ShellHandler)
            assert False


    except Exception as e:

        log.error('Error updating and transferring reconcile-stack file to open stack %s', str(e))
        Report_file.add_line('Error updating and transferring reconcile-stack file to open stack ' + str(e))
        assert False

    finally:
        connection.close()


def update_tosca_security_group_files(security_group):
    try:
        log.info('Start updating tosca security group files ')
        Report_file.add_line('Start updating tosca security group files ')
        file_name = r'com_ericsson_do_auto_integration_files/create_node_security_group.json'
        log.info('Start to update create_node_security_group.json and transfer_security_group.json file ')
        Report_file.add_line('Start to update create_node_security_group.json and transfer_security_group.json file ')
        sit_data = SIT_initialization.get_model_objects(SIT_initialization, 'SIT')

        tenant_name = sit_data._SIT__tenantName
        vimzone_id = sit_data._SIT__vimzone_id

        Json_file_handler.update_any_json_attr(Json_file_handler, file_name, ['securityGroup'], 'name', security_group)
        Json_file_handler.update_any_json_attr(Json_file_handler, file_name, [], 'tenantName', tenant_name)

        file_name = r'com_ericsson_do_auto_integration_files/transfer_node_security_group.json'

        Json_file_handler.update_any_json_attr(Json_file_handler, file_name, ['vimZones', 0], 'id', vimzone_id)

        log.info('Finished to update create_node_security_group.json and transfer_security_group.json file ')
        Report_file.add_line('Finished to update create_node_security_group.json and transfer_security_group.json file')


    except Exception as e:

        log.error('Error while updating activation_gui_password.json file %s', str(e))
        Report_file.add_line('Error while updating activation_gui_password.json file ,check logs for more details')
        assert False


def update_tosca_node_onboard_file(package_name):
    try:
        log.info('Start updating tosca node onboard file %s', package_name)
        Report_file.add_line('Start updating tosca node onboard file ' + package_name)

        sit_data = SIT_initialization.get_model_objects(SIT_initialization, 'SIT')

        tenant_name = sit_data._SIT__tenantName
        vnfManager_id = sit_data._SIT__vnfManagers
        file_zip_name = sit_data._SIT__ims_vnfd_id + '.zip'

        update_runtime_env_file('ONBOARD_PACKAGE', package_name)

        file_name = r'com_ericsson_do_auto_integration_files/onboard_tosca.json'
        data = {'fileName': file_zip_name, 'name': package_name, 'tenantName': tenant_name}

        Json_file_handler.modify_list_of_attributes(Json_file_handler, file_name, data)
        Json_file_handler.update_any_json_attr(Json_file_handler, file_name, ['vnfManagers', 0], 'id', vnfManager_id)


    except Exception as e:
        log.error('Error while updating tosca node onboard file %s', str(e))
        Report_file.add_line('Error while updating tosca node onboard file')


def update_transfer_image_file():
    try:
        log.info('Start updating transfer image file ')
        Report_file.add_line('Start updating transfer image file ')

        sit_data = SIT_initialization.get_model_objects(SIT_initialization, 'SIT')

        vimzone_name = sit_data._SIT__vimzone_name

        file_name = r'com_ericsson_do_auto_integration_files/transfer_image.json'

        Json_file_handler.update_any_json_attr(Json_file_handler, file_name, ['vimZones', 0], 'name', vimzone_name)


    except Exception as e:
        log.error('Error while updating image transfer file %s', str(e))
        Report_file.add_line('Error while updating image transfer file ')
        assert False


def update_tosca_node_deploy_file(file_name, vapp_name, flavor, auth_key, network_list, net_subnet_data):
    try:
        log.info('Start updating tosca node deploy file %s', file_name)
        Report_file.add_line('Start updating tosca node deploy file ' + file_name)

        sit_data = SIT_initialization.get_model_objects(SIT_initialization, 'SIT')
        EPIS_data = ECM_PI_Initialization.get_model_objects(ECM_PI_Initialization, 'EPIS')
        ecm_host_data = ECM_PI_Initialization.get_model_objects(ECM_PI_Initialization, 'ECMPI')

        ecm_environment = ecm_host_data._Ecm_PI__ECM_Host_Name
        cloud_type = EPIS_data._EPIS__cloudManagerType
        ipv4_range = EPIS_data._EPIS__network_ipv4_range

        ip = ipv4_range[:-3]
        start_ip = str(ipaddress.ip_address(ip) + 1)

        allocation_pools_ip = ecm_host_data._Ecm_PI__allocation_pools_ip
        end_ip = allocation_pools_ip.split('-')[1]

        provider_network = 'P3_' + cloud_type + '01_' + ecm_environment + '_PROV'

        file_path = r'com_ericsson_do_auto_integration_files/' + file_name
        attribute_value_dict = {"tenantName": sit_data._SIT__tenantName, "vimZoneName": sit_data._SIT__vimzone_name}
        Json_file_handler.modify_list_of_attributes(Json_file_handler, file_path, attribute_value_dict)

        vnfManager_id = sit_data._SIT__vnfManagers
        vdc_id = sit_data._SIT__vdc_id

        node_ip = sit_data._SIT__bgf_tosca_ip

        Json_file_handler.update_any_json_attr(Json_file_handler, file_path, ['vnfm'], 'id', vnfManager_id)
        Json_file_handler.update_any_json_attr(Json_file_handler, file_path, ['vdc'], 'id', vdc_id)
        Json_file_handler.update_any_json_attr(Json_file_handler, file_path, ['vapp'], 'name', vapp_name)
        Json_file_handler.update_any_json_attr(Json_file_handler, file_path, ['vapp'], 'flavor', flavor)

        Json_file_handler.update_any_json_attr(Json_file_handler, file_path, ['vapp', 'deploymentParameters'],
                                               'OM_ip_address', node_ip)
        Json_file_handler.update_any_json_attr(Json_file_handler, file_path, ['vapp', 'deploymentParameters'],
                                               'admin_authorized_key', auth_key)
        Json_file_handler.update_any_json_attr(Json_file_handler, file_path, ['vapp', 'deploymentParameters'],
                                               'external_net_name', network_list[1])
        Json_file_handler.update_any_json_attr(Json_file_handler, file_path, ['vapp', 'deploymentParameters'],
                                               'workflow_nodeIpAddress', node_ip)

        for i in range(0, 6):
            network_name = network_list[i]
            id_list = net_subnet_data[network_name]
            if provider_network in network_name:
                Json_file_handler.update_any_json_attr(Json_file_handler, file_path,
                                                       ['vapp', 'extVirtualLinks', i, 'extCps', 0, 'cpConfig', 0,
                                                        'cpProtocolData', 0, 'ipOverEthernet', 'ipAddresses', 0,
                                                        'addressRange'], 'minAddress', start_ip)
                Json_file_handler.update_any_json_attr(Json_file_handler, file_path,
                                                       ['vapp', 'extVirtualLinks', i, 'extCps', 0, 'cpConfig', 0,
                                                        'cpProtocolData', 0, 'ipOverEthernet', 'ipAddresses', 0,
                                                        'addressRange'], 'maxAddress', end_ip)

            Json_file_handler.update_any_json_attr(Json_file_handler, file_path, ['vapp', 'extVirtualLinks', i], 'id',
                                                   id_list[0])
            Json_file_handler.update_any_json_attr(Json_file_handler, file_path,
                                                   ['vapp', 'extVirtualLinks', i, 'extCps', 0, 'cpConfig', 0,
                                                    'cpProtocolData', 0, 'ipOverEthernet', 'ipAddresses', 0],
                                                   'nfvoSubnetId', id_list[1])


    except Exception as e:
        log.error('Error while updating tosca node onboard file %s', str(e))
        Report_file.add_line('Error while updating tosca node onboard file')
        assert False


def update_dummy_tosca_deploy_file(file_name, vapp_name, tosca_dummy_depl_flavor, image_vimobjectId):
    try:
        log.info('Start updating etsi tosca dummy deploy file %s', file_name)
        Report_file.add_line('Start updating etsi tosca dummy deploy file' + file_name)

        sit_data = SIT_initialization.get_model_objects(SIT_initialization, 'SIT')
        EPIS_data = ECM_PI_Initialization.get_model_objects(ECM_PI_Initialization, 'EPIS')
        ecm_host_data = ECM_PI_Initialization.get_model_objects(ECM_PI_Initialization, 'ECMPI')

        file_path = r'com_ericsson_do_auto_integration_files/' + file_name
        tenant_name = EPIS_data._EPIS__tenant_name
        vimzone_name = sit_data._SIT__vimzone_name
        vnfManager_id = sit_data._SIT__vnfManagers
        vdc_id = sit_data._SIT__vdc_id

        attribute_value_dict = {"tenantName": tenant_name, "vimZoneName": vimzone_name}
        Json_file_handler.modify_list_of_attributes(Json_file_handler, file_path, attribute_value_dict)

        Json_file_handler.update_any_json_attr(Json_file_handler, file_path, ['vnfm'], 'id', vnfManager_id)
        Json_file_handler.update_any_json_attr(Json_file_handler, file_path, ['vdc'], 'id', vdc_id)
        Json_file_handler.update_any_json_attr(Json_file_handler, file_path, ['vapp'], 'name', vapp_name)

        block_attr = sit_data.block_data
        block_data = copy.deepcopy(block_attr)

        block_data['services_flavor'] = tosca_dummy_depl_flavor
        block_data['servicesImage'] = image_vimobjectId
        block_data['isToscaVnfd'] = True
        block_data['ip_version'] = "4"
        block_data.pop('retry')
        block_data.pop('retryTimes')

        Json_file_handler.update_any_json_attr(Json_file_handler, file_path, ['vapp'], 'deploymentParameters',
                                               block_data)


    except Exception as e:
        log.error('Error while updating dummy deploy etsi tosca node file %s', str(e))
        Report_file.add_line('Error while updating dummy deploy etsi tosca file')
        assert False


def update_ns_create_package_file(file_name, nsdId, nsName):
    log.info('Start to update %s file to create NS Instantiate', file_name)
    Report_file.add_line('Start to update ' + file_name + ' file to create NS Instantiate')
    try:
        filename = r'com_ericsson_do_auto_integration_files/' + file_name
        Json_file_handler.update_any_json_attr(Json_file_handler, filename, [], 'nsdId', nsdId)
        Json_file_handler.update_any_json_attr(Json_file_handler, filename, [], 'nsName', nsName)

    except Exception as e:
        log.error('Error while updating %s: %s', file_name, str(e))
        Report_file.add_line('Error while updating ' + file_name + '' + str(e))
        assert False


def update_cnf_instanatiate_file(file_name, servicename):
    try:
        log.info('Start to update file to create CNF NS Instantiate %s', file_name)

        sit_data = SIT_initialization.get_model_objects(SIT_initialization, 'SIT')
        default_vdc_id = sit_data._SIT__vdc_id
        cnf_vnfm_id = sit_data._SIT__cnf_vnfm_id
        cismName = 'kubernetes'
        vnfInstanceName1 = '' + servicename + '-cnfb1'
        vnfInstanceName2 = '' + servicename + '-cnfa1'
        vnfInstanceName3 = '' + servicename + '-cnfa2'

        filename = r'com_ericsson_do_auto_integration_files/' + file_name
        Json_file_handler.update_any_json_attr(Json_file_handler, filename, ['additionalParamsForNs', 'nsParams'],
                                               'targetVdc', default_vdc_id)

        Json_file_handler.update_any_json_attr(Json_file_handler, filename, ['additionalParamsForNs', 'vnfParams', 0],
                                               'vnfInstanceName', vnfInstanceName1)
        Json_file_handler.update_any_json_attr(Json_file_handler, filename, ['additionalParamsForNs', 'vnfParams', 0],
                                               'cismName', cismName)
        Json_file_handler.update_any_json_attr(Json_file_handler, filename, ['additionalParamsForNs', 'vnfParams', 0],
                                               'vnfmId', cnf_vnfm_id)

        Json_file_handler.update_any_json_attr(Json_file_handler, filename, ['additionalParamsForVnf', 0],
                                               'vnfInstanceName', vnfInstanceName1)

        Json_file_handler.update_any_json_attr(Json_file_handler, filename, ['additionalParamsForNs', 'vnfParams', 1],
                                               'vnfInstanceName', vnfInstanceName2)
        Json_file_handler.update_any_json_attr(Json_file_handler, filename, ['additionalParamsForNs', 'vnfParams', 1],
                                               'cismName', cismName)
        Json_file_handler.update_any_json_attr(Json_file_handler, filename, ['additionalParamsForNs', 'vnfParams', 1],
                                               'vnfmId', cnf_vnfm_id)
        Json_file_handler.update_any_json_attr(Json_file_handler, filename, ['additionalParamsForVnf', 1],
                                               'vnfInstanceName', vnfInstanceName2)

        is_cloudnative = Ecm_core.get_is_cloudnative(Ecm_core)
        if is_cloudnative:
            Json_file_handler.update_any_json_attr(Json_file_handler, filename, ['additionalParamsForNs', 'vnfParams', 2],
                                                   'vnfInstanceName', vnfInstanceName3)
            Json_file_handler.update_any_json_attr(Json_file_handler, filename, ['additionalParamsForNs', 'vnfParams', 2],
                                                   'cismName', cismName)
            Json_file_handler.update_any_json_attr(Json_file_handler, filename, ['additionalParamsForNs', 'vnfParams', 2],
                                                   'vnfmId', cnf_vnfm_id)
            Json_file_handler.update_any_json_attr(Json_file_handler, filename, ['additionalParamsForVnf', 2],
                                               'vnfInstanceName', vnfInstanceName3)

    except Exception as e:
        log.error('Error While doing CNF NS Instantiate %s', str(e))
        assert False


def update_tosca_epg_instantiate_file(file_name, vapp_name, external_network_system_id, sub_network_system_id):
    try:
        log.info('Start to update file to create TOSCA EPG NS Instantiate %s', file_name)
        filename = r'com_ericsson_do_auto_integration_files/' + file_name

        vnf_param_file = r'com_ericsson_do_auto_integration_files/vnfAdditionalParamTEPG.json'
        cp_config_ip1 = Json_file_handler.get_json_attr_value(Json_file_handler, vnf_param_file,
                                                              "ossTopology.nodeIpAddress")

        cp_config_ip2 = str(ipaddress.ip_address(cp_config_ip1) + 1)

        vdc_id = SIT.get_vdc_id(SIT)
        vnfm_id = SIT.get_vnf_managers(SIT)
        vimzone_name = SIT.get_vimzone_name(SIT)

        additional_params = Json_file_handler.get_json_data(Json_file_handler, vnf_param_file)

        additional_params.pop("vnfProfileId", None)

        Json_file_handler.update_any_json_attr(Json_file_handler, filename,
                                               ['additionalParamsForNs', 'accessPointParams', 'exposedVnfCpParams', 0],
                                               'vnfInstanceName', vapp_name)
        Json_file_handler.update_any_json_attr(Json_file_handler, filename,
                                               ['additionalParamsForNs', 'accessPointParams', 'exposedVnfCpParams', 0],
                                               'connectedVn', external_network_system_id)
        Json_file_handler.update_any_json_attr(Json_file_handler, filename,
                                               ['additionalParamsForNs', 'accessPointParams', 'exposedVnfCpParams', 0,
                                                'cpConfig', 0, 'cpProtocolData', 0, 'ipOverEthernet', 'ipAddresses', 0],
                                               'fixedAddresses', [cp_config_ip1])

        Json_file_handler.update_any_json_attr(Json_file_handler, filename,
                                               ['additionalParamsForNs', 'accessPointParams', 'exposedVnfCpParams', 0,
                                                'cpConfig', 0, 'cpProtocolData', 0, 'ipOverEthernet', 'ipAddresses', 0],
                                               'subnetResourceIdRef', sub_network_system_id)

        Json_file_handler.update_any_json_attr(Json_file_handler, filename,
                                               ['additionalParamsForNs', 'accessPointParams', 'exposedVnfCpParams', 0,
                                                'cpConfig', 0, 'cpProtocolData', 0, 'ipOverEthernet', 'ipAddresses', 0],
                                               'subnetId', sub_network_system_id)

        Json_file_handler.update_any_json_attr(Json_file_handler, filename,
                                               ['additionalParamsForNs', 'accessPointParams', 'exposedVnfCpParams', 0,
                                                'cpConfig', 1, 'cpProtocolData', 0, 'ipOverEthernet', 'ipAddresses', 0],
                                               'fixedAddresses', [cp_config_ip2])

        Json_file_handler.update_any_json_attr(Json_file_handler, filename,
                                               ['additionalParamsForNs', 'accessPointParams', 'exposedVnfCpParams', 0,
                                                'cpConfig', 1, 'cpProtocolData', 0, 'ipOverEthernet', 'ipAddresses', 0],
                                               'subnetResourceIdRef', sub_network_system_id)

        Json_file_handler.update_any_json_attr(Json_file_handler, filename,
                                               ['additionalParamsForNs', 'accessPointParams', 'exposedVnfCpParams', 0,
                                                'cpConfig', 1, 'cpProtocolData', 0, 'ipOverEthernet', 'ipAddresses', 0],
                                               'subnetId', sub_network_system_id)

        Json_file_handler.update_any_json_attr(Json_file_handler, filename,
                                               ['additionalParamsForNs', 'nsParams', ],
                                               'targetVdc', vdc_id)

        Json_file_handler.update_any_json_attr(Json_file_handler, filename,
                                               ['additionalParamsForNs', 'vnfParams', 0],
                                               'vnfInstanceName', vapp_name)

        Json_file_handler.update_any_json_attr(Json_file_handler, filename,
                                               ['additionalParamsForNs', 'vnfParams', 0],
                                               'vnfmId', vnfm_id)

        Json_file_handler.update_any_json_attr(Json_file_handler, filename,
                                               ['additionalParamsForNs', 'vnfParams', 0],
                                               'vimZoneName', vimzone_name)

        Json_file_handler.update_any_json_attr(Json_file_handler, filename,
                                               ['additionalParamsForVnf', 0],
                                               'vnfInstanceName', vapp_name)

        Json_file_handler.update_any_json_attr(Json_file_handler, filename,
                                               ['additionalParamsForVnf', 0],
                                               'additionalParams', additional_params)

    except Exception as e:
        log.error('Error While updating TOSCA EPG NS Instantiate file  %s', str(e))
        assert False


def update_vnflaf_yaml_scalefiles(file_path, file_name, servicesImage, tosca_dummy_depl_flavor, option, node_name=''):
    log.info('Start to update %s file for SCALE_OUT ', file_name)
    Report_file.add_line('Start to update ' + file_name + ' file for SCALE_OUT')
    try:

        sit_data = SIT_initialization.get_model_objects(SIT_initialization, 'SIT')

        file_path = file_path + file_name

        external_ip_for_services_vm_to_scale = sit_data._SIT__externalIpForServicesVmToScale

        block_attr = sit_data.block_data
        block_data = copy.deepcopy(block_attr)

        if option == 'Scale-Out':
            block_data['services_flavor'] = tosca_dummy_depl_flavor
            servicesImage_scaleout = servicesImage + ',' + servicesImage
            block_data['servicesImage'] = servicesImage_scaleout
            block_data['services_vm_count'] = 2
            external_ip_for_services_vm = block_data[
                                              'external_ip_for_services_vm'] + ',' + external_ip_for_services_vm_to_scale
            block_data['external_ip_for_services_vm'] = external_ip_for_services_vm
            block_data['ossUserName'] = "root"

        elif option == 'SO-DUUMY-SCALE':
            if node_name == 'SO-DUMMY-HEAL':
                servicesImage = "ECM_TOSCA_Image_EO_Staging_9mb"
                block_data['servicesImage'] = servicesImage
                external_ip_for_services_vm = block_data[
                    'external_ip_for_services_vm']
                block_data['external_ip_for_services_vm'] = external_ip_for_services_vm
            else:
                servicesImage = "ECM_TOSCA_Image_EO_Staging_9mb,ECM_TOSCA_Image_EO_Staging_9mb"
                block_data['servicesImage'] = servicesImage
                external_ip_for_services_vm = block_data[
                                                  'external_ip_for_services_vm'] + ',' + external_ip_for_services_vm_to_scale
                block_data['external_ip_for_services_vm'] = external_ip_for_services_vm

            cloudManagerType = "ECM"
            block_data['cloudManagerType'] = cloudManagerType
            ossType = "OSSRC"
            block_data['ossType'] = ossType
            ossMasterHostName = "masterservice"
            block_data['ossMasterHostName'] = ossMasterHostName
            ossMasterHostIP = "10.32.135.64"
            block_data['ossMasterHostIP'] = ossMasterHostIP
            ossNotificationServiceHost = "notificationservice"
            block_data['ossNotificationServiceHost'] = ossNotificationServiceHost
            ossNotificationServiceIP = "10.32.135.65"
            block_data['ossNotificationServiceIP'] = ossNotificationServiceIP
            ossUserName = "nmsadm"
            block_data['ossUserName'] = ossUserName

            services_flavor = "CM-sol005_flavor_dummy"
            block_data['services_flavor'] = services_flavor
            ip_version = "IPV4"
            block_data['ip_version'] = ip_version
            isToscaVnfd = True
            block_data['isToscaVnfd'] = isToscaVnfd

            external_net_id = sit_data._SIT__external_net_id
            block_data['external_net_id'] = external_net_id

            external_subnet_cidr = sit_data._SIT__external_subnet_cidr
            block_data['external_subnet_cidr'] = external_subnet_cidr
            external_subnet_gateway = sit_data._SIT__external_subnet_gateway
            block_data['external_subnet_gateway'] = external_subnet_gateway


        else:
            block_data['services_flavor'] = tosca_dummy_depl_flavor
            block_data['servicesImage'] = servicesImage
            block_data['services_vm_count'] = 1
            block_data['ossUserName'] = "root"

        block_data.pop('retry')
        block_data.pop('retryTimes')

        Json_file_handler.update_yaml(Json_file_handler, file_path, 'parameters', block_data)

    except Exception as e:
        log.error('Error while updating %s: %s', file_name, str(e))
        Report_file.add_line('Error while updating ' + file_name + ' file ,check logs for more details')

    log.info('Finished to update %s file ', file_name)
    Report_file.add_line('Finished to update ' + file_name + ' file')


def update_cnf_create_package_file(filename, pkg_name, name):
    log.info('Start to update %s file to create CNF package', filename)
    try:
        sit_data = SIT_initialization.get_model_objects(SIT_initialization, 'SIT')
        CNF_VNFM_ID = sit_data._SIT__cnf_vnfm_id
        file_path = r'com_ericsson_do_auto_integration_files/' + filename
        Json_file_handler.update_any_json_attr(Json_file_handler, file_path, [], 'fileName', name)
        Json_file_handler.update_any_json_attr(Json_file_handler, file_path, [], 'name', pkg_name)
        Json_file_handler.update_any_json_attr(Json_file_handler, file_path, ['vnfManagers', 0], 'id', CNF_VNFM_ID)
    except Exception as error:
        log.error('Error while updating %s: %s', filename, str(error))
        assert False


def update_adding_vfc_to_vf_comp_json_files(file_name, key_value_to_update):
    try:
        log.info(f'start to update %s file', file_name)
        Report_file.add_line(f'start to update {file_name} file')
        Json_file_handler.modify_attribute(Json_file_handler,
                                           r'com_ericsson_do_auto_integration_files/UDS_files/' + file_name,
                                           'componentUid', key_value_to_update)


    except Exception as e:
        log.error('Error While updating the %s: %s', file_name, str(e))
        Report_file.add_line(f'Error While updating the {file_name} file' + str(e))
        assert False


def update_create_VF_file_UDS(file_name, vf_name):
    try:
        log.info('start to update %s file', file_name)
        Report_file.add_line(f'start to update {file_name} file')
        Json_file_handler.modify_attribute(Json_file_handler,
                                           r'com_ericsson_do_auto_integration_files/UDS_files/' + file_name,
                                           'name', vf_name)
        data = [vf_name]
        Json_file_handler.modify_attribute(Json_file_handler,
                                           r'com_ericsson_do_auto_integration_files/UDS_files/' + file_name,
                                           'tags', data)
        Json_file_handler.modify_attribute(Json_file_handler,
                                           r'com_ericsson_do_auto_integration_files/UDS_files/' + file_name,
                                           'description', vf_name)

    except Exception as e:
        log.error('Error while updating %s: %s', file_name, str(e))
        Report_file.add_line(f'Error While updating the {file_name} file' + str(e))
        assert False


def update_associate_epg_to_ns_json_file(file_name, epg_comp_id, ns_comp_id, capabilities_id, requirements_id,
                                         requirement_owner_id):
    try:
        log.info('start to update %s file', file_name)
        Report_file.add_line(f'start to update {file_name} file')
        Json_file_handler.modify_attribute(Json_file_handler,
                                           r'com_ericsson_do_auto_integration_files/UDS_files/' + file_name, 'fromNode',
                                           epg_comp_id)
        Json_file_handler.modify_attribute(Json_file_handler,
                                           r'com_ericsson_do_auto_integration_files/UDS_files/' + file_name, 'toNode',
                                           ns_comp_id)
        # Json_file_handler.modify_second_level_attr(Json_file_handler,'com_ericsson_do_auto_integration_files/UDS_files/'+file_name, 'relationships', 0, 'capabilityOwnerId', 'Default')
        Json_file_handler.update_any_json_attr(Json_file_handler,
                                               'com_ericsson_do_auto_integration_files/UDS_files/' + file_name,
                                               ['relationships', 0, 'relation'], 'capabilityOwnerId', ns_comp_id)
        Json_file_handler.update_any_json_attr(Json_file_handler,
                                               'com_ericsson_do_auto_integration_files/UDS_files/' + file_name,
                                               ['relationships', 0, 'relation'], 'capabilityUid', capabilities_id)

        Json_file_handler.update_any_json_attr(Json_file_handler,
                                               'com_ericsson_do_auto_integration_files/UDS_files/' + file_name,
                                               ['relationships', 0, 'relation'], 'requirementOwnerId',
                                               requirement_owner_id)
        Json_file_handler.update_any_json_attr(Json_file_handler,
                                               'com_ericsson_do_auto_integration_files/UDS_files/' + file_name,
                                               ['relationships', 0, 'relation'], 'requirementUid', requirements_id)


    except Exception as e:
        log.error('Error while updating %s: %s', file_name, str(e))
        Report_file.add_line(f'Error While updating the {file_name} file' + str(e))
        assert False


def update_add_epg_properties_json_file(file_name, epg_vfc_id, network_function_vfc_id):
    try:
        # Json_file_handler.update_any_json_attr(Json_file_handler,'com_ericsson_do_auto_integration_files/UDS_files/'+ file_name, [0], 'name', 'admin')
        log.info(f'start to update %s file', file_name)
        Report_file.add_line(f'start to update {file_name} file')
        epg_vfc_unique_id = '' + epg_vfc_id + '.vnfUniqueId'
        epg_vfc_unique_id_for_cusotm = '' + epg_vfc_id + '.customTemplates'
        Json_file_handler.update_any_json_attr(Json_file_handler,
                                               'com_ericsson_do_auto_integration_files/UDS_files/' + file_name, [0],
                                               'uniqueId', epg_vfc_unique_id)
        Json_file_handler.update_any_json_attr(Json_file_handler,
                                               'com_ericsson_do_auto_integration_files/UDS_files/' + file_name, [1],
                                               'parentUniqueId', network_function_vfc_id)
        Json_file_handler.update_any_json_attr(Json_file_handler,
                                               'com_ericsson_do_auto_integration_files/UDS_files/' + file_name, [1],
                                               'uniqueId', epg_vfc_unique_id_for_cusotm)
        Json_file_handler.update_any_json_attr(Json_file_handler,
                                               'com_ericsson_do_auto_integration_files/UDS_files/' + file_name,
                                               [1, 'toscaPresentation'], 'ownerId', network_function_vfc_id)

    except Exception as e:
        log.error('Error while updating %s: %s', file_name, str(e))
        Report_file.add_line(f'Error While updating the {file_name} file' + str(e))
        assert False


def update_add_ns_properties_json_file(file_name, resource_vfc_id, network_service_vfc_id):
    try:
        log.info(f'start to update %s file', file_name)
        Report_file.add_line(f'start to update {file_name} file')
        ns_unique_id = '' + network_service_vfc_id + '.customTemplates'
        Json_file_handler.update_any_json_attr(Json_file_handler,
                                               'com_ericsson_do_auto_integration_files/UDS_files/' + file_name, [0],
                                               'parentUniqueId', resource_vfc_id)
        Json_file_handler.update_any_json_attr(Json_file_handler,
                                               'com_ericsson_do_auto_integration_files/UDS_files/' + file_name, [0],
                                               'uniqueId', ns_unique_id)
        Json_file_handler.update_any_json_attr(Json_file_handler,
                                               'com_ericsson_do_auto_integration_files/UDS_files/' + file_name,
                                               [0, 'toscaPresentation'], 'ownerId', resource_vfc_id)

    except Exception as e:
        log.error(f'Error While updating the %s file', str(e))
        Report_file.add_line(f'Error While updating the {file_name} file' + str(e))
        assert False


def update_add_vf_to_service_json_file(file_name, certify_vf_id):
    try:
        log.info('Start to update add_vf_to_service json file')
        Report_file.add_line('Start to update add_vf_to_service json file')
        file_path = r'com_ericsson_do_auto_integration_files/UDS_files/' + file_name
        Json_file_handler.modify_attribute(Json_file_handler, file_path, 'componentUid', certify_vf_id)

    except Exception as e:
        log.error('Error while updating the add_vf_to_service json file %s ', str(e))
        Report_file.add_line('Error while updating the add_vf_to_service json fil ' + str(e))
        assert False


def update_epg_inputs_json_file(file_name, unique_epg_comp_id, epg_vfc_id, nf_vfc_id):
    try:
        log.info(f'start to update %s file', file_name)
        Report_file.add_line(f'start to update {file_name} file')

        epg_vfc_unique_id_alias = '' + epg_vfc_id + '.alias'
        epf_vfc_unique_id_serv = '' + epg_vfc_id + '.vEPG_service_ip'
        epf_vfc_unique_id_vim = '' + epg_vfc_id + '.vimZoneName'
        epf_vfc_unique_id_vnf = '' + epg_vfc_id + '.vnfdId_epg'
        epf_vfc_unique_id_vnfm = '' + epg_vfc_id + '.vnfm_Id'

        data = {
            unique_epg_comp_id: [
                {
                    "constraints": None,
                    "defaultValue": None,
                    "description": None,
                    "name": "alias",
                    "origName": "alias",
                    "parentUniqueId": None,
                    "password": False,
                    "required": False,
                    "schema": {
                        "property": {}
                    },
                    "schemaType": None,
                    "type": "string",
                    "uniqueId": epg_vfc_unique_id_alias,
                    "value": None,
                    "definition": False,
                    "getInputValues": None,
                    "parentPropertyType": None,
                    "subPropertyInputPath": None,
                    "getPolicyValues": None,
                    "inputPath": None
                },
                {
                    "constraints": None,
                    "defaultValue": None,
                    "description": None,
                    "name": "vEPG_service_ip",
                    "origName": "vEPG_service_ip",
                    "parentUniqueId": None,
                    "password": False,
                    "required": False,
                    "schema": {
                        "property": {}
                    },
                    "schemaType": None,
                    "type": "string",
                    "uniqueId": epf_vfc_unique_id_serv,
                    "value": None,
                    "definition": False,
                    "getInputValues": None,
                    "parentPropertyType": None,
                    "subPropertyInputPath": None,
                    "getPolicyValues": None,
                    "inputPath": None
                },
                {
                    "constraints": None,
                    "defaultValue": None,
                    "description": None,
                    "name": "vimZoneName",
                    "origName": "vimZoneName",
                    "parentUniqueId": nf_vfc_id,
                    "password": False,
                    "required": False,
                    "schema": {
                        "property": {}
                    },
                    "schemaType": None,
                    "type": "string",
                    "uniqueId": epf_vfc_unique_id_vim,
                    "value": None,
                    "definition": False,
                    "getInputValues": None,
                    "parentPropertyType": None,
                    "subPropertyInputPath": None,
                    "getPolicyValues": None,
                    "inputPath": None
                },
                {
                    "constraints": None,
                    "defaultValue": None,
                    "description": None,
                    "name": "vnfdId_epg",
                    "origName": "vnfdId_epg",
                    "parentUniqueId": None,
                    "password": False,
                    "required": False,
                    "schema": {
                        "property": {}
                    },
                    "schemaType": None,
                    "type": "string",
                    "uniqueId": epf_vfc_unique_id_vnf,
                    "value": None,
                    "definition": False,
                    "getInputValues": None,
                    "parentPropertyType": None,
                    "subPropertyInputPath": None,
                    "getPolicyValues": None,
                    "inputPath": None
                },
                {
                    "constraints": None,
                    "defaultValue": None,
                    "description": None,
                    "name": "vnfm_Id",
                    "origName": "vnfm_Id",
                    "parentUniqueId": None,
                    "password": False,
                    "required": False,
                    "schema": {
                        "property": {}
                    },
                    "schemaType": None,
                    "type": "string",
                    "uniqueId": epf_vfc_unique_id_vnfm,
                    "value": None,
                    "definition": False,
                    "getInputValues": None,
                    "parentPropertyType": None,
                    "subPropertyInputPath": None,
                    "getPolicyValues": None,
                    "inputPath": None
                }
            ]
        }

        file_path = r'com_ericsson_do_auto_integration_files/UDS_files/' + file_name
        Json_file_handler.update_any_json_attr(Json_file_handler, file_path, [], 'componentInstanceProperties', data)

    except Exception as e:
        log.error('Error while updating the add_vf_to_service json file%s ', str(e))
        Report_file.add_line('Error while updating the add_vf_to_service json fil ' + str(e))
        assert False


def update_ns_input_json_file(file_name, ns_comp_unique_id, network_service_vfc_id):
    try:
        log.info(f'start to update %s file', file_name)
        Report_file.add_line(f'start to update {file_name} file')

        ns_vfc_id_conn = '' + network_service_vfc_id + '.connectionName'
        ns_vfc_id_desc = '' + network_service_vfc_id + '.nsDescription'
        ns_vfc_id_nsname = '' + network_service_vfc_id + '.nsName'
        ns_vfc_id_nsdid = '' + network_service_vfc_id + '.nsdId'
        ns_vfc_id_sub = '' + network_service_vfc_id + '.subsystemName'
        ns_vfc_id_ten = '' + network_service_vfc_id + '.tenant'

        data = {
            ns_comp_unique_id: [
                {
                    "constraints": None,
                    "defaultValue": None,
                    "description": None,
                    "name": "connectionName",
                    "origName": "connectionName",
                    "parentUniqueId": None,
                    "password": False,
                    "required": False,
                    "schema": {
                        "property": {}
                    },
                    "schemaType": None,
                    "type": "string",
                    "uniqueId": ns_vfc_id_conn,
                    "value": None,
                    "definition": False,
                    "getInputValues": None,
                    "parentPropertyType": None,
                    "subPropertyInputPath": None,
                    "getPolicyValues": None,
                    "inputPath": None
                },
                {
                    "constraints": None,
                    "defaultValue": None,
                    "description": None,
                    "name": "nsDescription",
                    "origName": "nsDescription",
                    "parentUniqueId": None,
                    "password": False,
                    "required": False,
                    "schema": {
                        "property": {}
                    },
                    "schemaType": None,
                    "type": "string",
                    "uniqueId": ns_vfc_id_desc,
                    "value": None,
                    "definition": False,
                    "getInputValues": None,
                    "parentPropertyType": None,
                    "subPropertyInputPath": None,
                    "getPolicyValues": None,
                    "inputPath": None
                },
                {
                    "constraints": None,
                    "defaultValue": None,
                    "description": None,
                    "name": "nsName",
                    "origName": "nsName",
                    "parentUniqueId": None,
                    "password": False,
                    "required": False,
                    "schema": {
                        "property": {}
                    },
                    "schemaType": None,
                    "type": "string",
                    "uniqueId": ns_vfc_id_nsname,
                    "value": None,
                    "definition": False,
                    "getInputValues": None,
                    "parentPropertyType": None,
                    "subPropertyInputPath": None,
                    "getPolicyValues": None,
                    "inputPath": None
                },
                {
                    "constraints": None,
                    "defaultValue": None,
                    "description": None,
                    "name": "nsdId",
                    "origName": "nsdId",
                    "parentUniqueId": None,
                    "password": False,
                    "required": False,
                    "schema": {
                        "property": {}
                    },
                    "schemaType": None,
                    "type": "string",
                    "uniqueId": ns_vfc_id_nsdid,
                    "value": None,
                    "definition": False,
                    "getInputValues": None,
                    "parentPropertyType": None,
                    "subPropertyInputPath": None,
                    "getPolicyValues": None,
                    "inputPath": None
                },
                {
                    "constraints": None,
                    "defaultValue": None,
                    "description": None,
                    "name": "subsystemName",
                    "origName": "subsystemName",
                    "parentUniqueId": None,
                    "password": False,
                    "required": False,
                    "schema": {
                        "property": {}
                    },
                    "schemaType": None,
                    "type": "string",
                    "uniqueId": ns_vfc_id_sub,
                    "value": None,
                    "definition": False,
                    "getInputValues": None,
                    "parentPropertyType": None,
                    "subPropertyInputPath": None,
                    "getPolicyValues": None,
                    "inputPath": None
                },
                {
                    "constraints": None,
                    "defaultValue": None,
                    "description": None,
                    "name": "tenant",
                    "origName": "tenant",
                    "parentUniqueId": None,
                    "password": False,
                    "required": False,
                    "schema": {
                        "property": {}
                    },
                    "schemaType": None,
                    "type": "string",
                    "uniqueId": ns_vfc_id_ten,
                    "value": None,
                    "definition": False,
                    "getInputValues": None,
                    "parentPropertyType": None,
                    "subPropertyInputPath": None,
                    "getPolicyValues": None,
                    "inputPath": None
                }
            ]
        }
        file_path = r'com_ericsson_do_auto_integration_files/UDS_files/' + file_name
        Json_file_handler.update_any_json_attr(Json_file_handler, file_path, [], 'componentInstanceProperties', data)
    except Exception as e:
        log.error('Error while updating %s: %s', file_name, str(e))
        Report_file.add_line(f'Error While updating the {file_name} file' + str(e))
        assert False


def update_epg_heal_json_file(file_name, epg_vapp_name):
    try:
        log.info(f'start to update %s file', file_name)
        Report_file.add_line(f'start to update {file_name} file')

        file_name = r'com_ericsson_do_auto_integration_files/' + file_name
        Json_file_handler.update_any_json_attr(Json_file_handler, file_name, ["additionalParams"], 'resourceName',
                                               epg_vapp_name)

    except Exception as e:
        log.error('Error while updating %s: %s', file_name, str(e))
        Report_file.add_line(f'Error While updating the {file_name} file' + str(e))
        assert False


def update_tosca_epg_heal_json_file(file_name, tosca_epg_vapp_name):
    try:
        log.info(f'start to update %s file', file_name)
        Report_file.add_line(f'start to update {file_name} file')

        file_name = r'com_ericsson_do_auto_integration_files/' + file_name
        Json_file_handler.update_any_json_attr(Json_file_handler, file_name, ["additionalParams"], 'resourceName',
                                               tosca_epg_vapp_name)

    except Exception as e:
        log.error('Error while updating %s: %s', file_name, str(e))
        Report_file.add_line(f'Error While updating the {file_name} file' + str(e))
        assert False


def update_import_vsp_as_vf_json_file(file_name, item_id, version_id, vendorName, vspName):
    try:
        log.info(f'start to update {file_name} file')
        Report_file.add_line(f'start to update {file_name} file')

        file_path = r'com_ericsson_do_auto_integration_files/UDS_files/' + file_name
        Json_file_handler.modify_attribute(Json_file_handler, file_path, 'csarUUID', item_id)
        Json_file_handler.modify_attribute(Json_file_handler, file_path, 'name', vspName)
        Json_file_handler.modify_attribute(Json_file_handler, file_path, 'tags', vspName)
        Json_file_handler.modify_attribute(Json_file_handler, file_path, 'vendorName', vendorName)

    except Exception as e:
        log.error(f'Error While updating the {file_name} file' + str(e))
        Report_file.add_line(f'Error While updating the {file_name} file' + str(e))
        assert False


def update_create_vnf_service_json_file(file_name, vspName):
    try:
        log.info(f'start to update {file_name} file')
        Report_file.add_line(f'start to update {file_name} file')

        file_path = r'com_ericsson_do_auto_integration_files/UDS_files/' + file_name
        Json_file_handler.modify_attribute(Json_file_handler, file_path, 'name', vspName)
        Json_file_handler.modify_attribute(Json_file_handler, file_path, 'tags', vspName)

    except Exception as e:
        log.error(f'Error While updating the {file_name} file' + str(e))
        Report_file.add_line(f'Error While updating the {file_name} file' + str(e))
        assert False


def update_add_vf_to_vnf_service_json_file(file_name, certify_vf_unique_id):
    try:
        log.info(f'start to update {file_name} file')
        Report_file.add_line(f'start to update {file_name} file')

        file_path = r'com_ericsson_do_auto_integration_files/UDS_files/' + file_name
        Json_file_handler.modify_attribute(Json_file_handler, file_path, 'uniqueId', certify_vf_unique_id)
        Json_file_handler.modify_attribute(Json_file_handler, file_path, 'componentUid', certify_vf_unique_id)

    except Exception as e:
        log.error(f'Error While updating the {file_name} file' + str(e))
        Report_file.add_line(f'Error While updating the {file_name} file' + str(e))
        assert False


def update_create_vlm_json_file(file_name, vendorName):
    try:
        log.info(f'start to update {file_name} file')
        Report_file.add_line(f'start to update {file_name} file')

        file_path = r'com_ericsson_do_auto_integration_files/UDS_files/' + file_name
        Json_file_handler.modify_attribute(Json_file_handler, file_path, 'vendorName', vendorName)

    except Exception as e:
        log.error(f'Error While updating the {file_name} file' + str(e))
        Report_file.add_line(f'Error While updating the {file_name} file' + str(e))
        assert False


def update_create_vsp_json_file(file_name, vendorName, vspName, vlm_item_id):
    try:
        log.info(f'start to update {file_name} file')
        Report_file.add_line(f'start to update {file_name} file')

        file_path = r'com_ericsson_do_auto_integration_files/UDS_files/' + file_name
        Json_file_handler.modify_attribute(Json_file_handler, file_path, 'vendorName', vendorName)
        Json_file_handler.modify_attribute(Json_file_handler, file_path, 'name', vspName)
        Json_file_handler.modify_attribute(Json_file_handler, file_path, 'vendorId', vlm_item_id)

    except Exception as e:
        log.error(f'Error While updating the {file_name} file' + str(e))
        Report_file.add_line(f'Error While updating the {file_name} file' + str(e))
        assert False


def update_ns_cnf_remove(file_name, cnf_vapp_instance_id):
    try:
        log.info('Start to update file to remove CNF NS Instantiate %s', file_name)

        file_path = r'com_ericsson_do_auto_integration_files/' + file_name
        Json_file_handler.update_any_json_attr(Json_file_handler, file_path, [],
                                               'removeVnfInstanceId', [cnf_vapp_instance_id])
        Json_file_handler.update_any_json_attr(Json_file_handler, file_path, ['terminateVnfData', 0],
                                               'vnfInstanceId', cnf_vapp_instance_id)

    except Exception as e:
        log.error('Error While doing CNF NS Instantiate %s', str(e))
        assert False


def update_ns_cnf_add(file_name, cnf_vapp_instance_name):
    try:
        log.info('Start to update file to remove CNF NS Instantiate %s', file_name)
        cnf_vnfm_id = SIT.get_cnf_vnfm_id(SIT)

        file_path = r'com_ericsson_do_auto_integration_files/' + file_name
        Json_file_handler.update_any_json_attr(Json_file_handler, file_path, ['instantiateVnfData', 0],
                                               'vnfInstanceName', cnf_vapp_instance_name)
        Json_file_handler.update_any_json_attr(Json_file_handler, file_path, ['additionalParamsForNs', 'vnfParams', 0],
                                               'vnfInstanceName', cnf_vapp_instance_name)
        Json_file_handler.update_any_json_attr(Json_file_handler, file_path, ['additionalParamsForNs', 'vnfParams', 0],
                                               'vnfmId', cnf_vnfm_id)

    except Exception as e:
        log.error('Error While doing CNF NS Instantiate %s', str(e))
        assert False


def update_ns_cnf_scale(file_name, operation_type, number_of_steps, cnf_vapp_mgt_id):
    try:
        log.info('Start to update file %s to %s NS CNF vapp ', file_name, operation_type)

        file_path = r'com_ericsson_do_auto_integration_files/' + file_name
        Json_file_handler.update_any_json_attr(Json_file_handler, file_path, ['scaleVnfData', 0],
                                               'vnfInstanceid', cnf_vapp_mgt_id)
        Json_file_handler.update_any_json_attr(Json_file_handler, file_path, ['scaleVnfData', 0],
                                               'scaleVnfType', operation_type)
        Json_file_handler.update_any_json_attr(Json_file_handler, file_path, ['scaleVnfData', 0, 'scaleByStepData'],
                                               'numberOfSteps', number_of_steps)

    except Exception as e:
        log.error('Error while updating scale file', str(e))
        assert False


def update_etsi_tepg_instanatiate_file(file_name, servicename, file_data):
    try:
        log.info("Start to update file %s", file_name)
        file = f'com_ericsson_do_auto_integration_files/{file_name}'
        vimzone_name = SIT.get_vimzone_name(SIT)
        vdc_id = SIT.get_vdc_id(SIT)
        vnfm_id = SIT.get_vnf_managers(SIT)
        data = file_data["instantiateVnfOpConfig"]
        data['updateOss'] = True
        # Removing the extra parameters for additionalParams from the payload data
        all(data.pop(item) for item in ["BP_net_id", "MATE_net_id", "VFAB_net_id"] if item in data)
        Json_file_handler.update_any_json_attr(Json_file_handler, file, ['additionalParamsForVnf', 0],
                                               "additionalParams", data)
        Json_file_handler.update_any_json_attr(Json_file_handler, file, ['additionalParamsForNs', 'nsParams'],
                                               'targetVdc', vdc_id)
        Json_file_handler.update_any_json_attr(Json_file_handler, file, ['additionalParamsForNs', 'vnfParams', 0],
                                               'vnfmId', vnfm_id)
        Json_file_handler.update_any_json_attr(Json_file_handler, file, ['additionalParamsForNs', 'vnfParams', 0],
                                               'vimZoneName', vimzone_name)
        Json_file_handler.update_any_json_attr(Json_file_handler, file, ['additionalParamsForNs', 'vnfParams', 0],
                                               'vnfInstanceName', servicename)
        Json_file_handler.update_any_json_attr(Json_file_handler, file, ['additionalParamsForVnf', 0],
                                               'vnfInstanceName', servicename)
        Json_file_handler.update_any_json_attr(Json_file_handler, file, ['additionalParamsForVnf', 0],
                                               'vnfProfileId', "epg-vnf")
        log.info("Successfully updated file %s", file_name)
    except Exception as error:
        log.error("Failed to update file %s: %s", file_name, str(error))
        assert False


def update_vapp_cmdb_del_file(file_name, vapp_name):
    try:
        log.info('Start to update file %s', file_name)
        tenant_name = SIT.get_tenant_name(SIT)
        vdc_name = SIT.get_vdc_name(SIT)

        file_path = r'com_ericsson_do_auto_integration_files/' + file_name
        Json_file_handler.update_any_json_attr(Json_file_handler, file_path, [], 'objectNames', [vdc_name, vapp_name])
        Json_file_handler.update_any_json_attr(Json_file_handler, file_path, [], 'tenant', tenant_name)

    except Exception as e:
        log.error('Error while updating cmdb vapp delete file', str(e))
        assert False
