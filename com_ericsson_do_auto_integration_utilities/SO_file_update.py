# pylint: disable=C0302,C0103,C0301,C0412,C0411,W0611,W0212,W0703,R1714,W0613,R0914,W0105,R0913,E0401,W0705,W0612
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
import copy
from packaging import version
from com_ericsson_do_auto_integration_utilities.Logger import Logger
from com_ericsson_do_auto_integration_utilities.Report_file import Report_file
from com_ericsson_do_auto_integration_utilities.Json_file_handler import Json_file_handler
from com_ericsson_do_auto_integration_initilization.SIT_initialization import SIT_initialization
from com_ericsson_do_auto_integration_initilization.Initialization_script import Initialization_script
from com_ericsson_do_auto_integration_utilities.Common_utilities import Common_utilities
from com_ericsson_do_auto_integration_initilization.ECM_PI_initialization import ECM_PI_Initialization
#from com_ericsson_do_auto_integration_scripts.SO_NODE_DEPLOYMENT import fetch_external_subnet_id
from com_ericsson_do_auto_integration_utilities.Server_details import Server_details
from com_ericsson_do_auto_integration_utilities.ServerConnection import ServerConnection


log = Logger.get_logger('SO_file_update.py')


def update_nsd_template_file(file_name, node_name, so_version):
    log.info('Start to update %s', file_name)
    Report_file.add_line('Start to update ' + file_name)
    try:
        sit_data = SIT_initialization.get_model_objects(SIT_initialization, 'SIT')
        attribute_list = ['topology_template', 'node_templates', 'vnf1', 'properties']
        ipam_attribute_list = ['topology_template', 'node_templates', 'networkVNF_mme', 'properties']

        vnfManagers_id = sit_data._SIT__vnfManagers

        vimzone_name = sit_data._SIT__vimzone_name

        if node_name == 'MME':
            vnfd_id = sit_data._SIT__mme_packageId
            name = sit_data._SIT__mme_package_name
            ipam_vnfd_id = sit_data._SIT__vnf_packageId
            Json_file_handler.update_nested_dict_yaml(Json_file_handler, file_name, ipam_attribute_list, 'vimZoneName',
                                                      vimzone_name)
            Json_file_handler.update_nested_dict_yaml(Json_file_handler, file_name, ipam_attribute_list, 'vnfdId',
                                                      ipam_vnfd_id)


        else:
            vnfd_id = sit_data._SIT__vnf_packageId
            name = sit_data._SIT__name

        if node_name == 'Dummy':
            block_attr = sit_data.block_data
            block_data = copy.deepcopy(block_attr)
            block_data['updateOss'] = "false"
            block_data['retry'] = "true"
            block_data['retryTimes'] = "5"
            ip_version = block_data['ip_version']
            block_data['ip_version'] = str(ip_version)
            services_vm_count = block_data['services_vm_count']
            block_data['services_vm_count'] = str(services_vm_count)

            attr = 'deploymentParams'
            Json_file_handler.update_nested_dict_yaml(Json_file_handler, file_name, attribute_list, attr, block_data)

        if so_version <= version.parse('2.0.0-69'):
            Json_file_handler.update_nested_dict_yaml(Json_file_handler, file_name, attribute_list, 'name', name)
            Json_file_handler.update_nested_dict_yaml(Json_file_handler, file_name, attribute_list, 'vimZoneName',
                                                      vimzone_name)
            Json_file_handler.update_nested_dict_yaml(Json_file_handler, file_name, attribute_list, 'vnfdId', vnfd_id)
            Json_file_handler.update_nested_dict_yaml(Json_file_handler, file_name, attribute_list, 'vnfmId',
                                                      vnfManagers_id)
        log.info('Finished to update %s', file_name)
        Report_file.add_line('Finished to update ' + file_name)

    except Exception as e:
        log.error('Error while updating ' + file_name + 'with error ' + str(e))
        Report_file.add_line('Error while updating ' + file_name + ',check logs for more details')


    except Exception as e:
        log.error('Error while updating ' + file_name + 'with error ' + str(e))
        Report_file.add_line('Error while updating ' + file_name + ',check logs for more details')


def update_service_template(file_name, nsd_id, node_name):
    log.info('Start to update %s', file_name)
    Report_file.add_line('Start to update ' + file_name)
    try:
        log.info('updating NSD id in Service template ')
        Report_file.add_line('updating NSD id in Service template')

        if node_name == 'Dummy':
            attribute_list = ['topology_template', 'node_templates', 'mmeTargetVnfNS', 'properties']
            attr = 'nsdId'
        elif node_name == 'MME':
            attribute_list = ['topology_template', 'node_templates', 'mmeTargetVnfNS', 'properties']
            attr = 'nsdId'
        else:
            # attribute_list = ['topology_template', 'node_templates', 'targetVNF_NS', 'properties'] only updating the default section in ST
            attribute_list = ['topology_template', 'inputs', 'nsdId']
            attr = 'default'

        Json_file_handler.update_nested_dict_yaml(Json_file_handler,
                                                  r'com_ericsson_do_auto_integration_files/' + file_name,
                                                  attribute_list, attr, nsd_id)
        log.info('Finished to update %s', file_name)
        Report_file.add_line('Finished to update ' + file_name)

    except Exception as e:

        log.error('Error while updating ' + file_name + 'with error ' + str(e))
        Report_file.add_line('Error while updating ' + file_name + ',check logs for more details')



def update_service_template_catalog(file_name, nsd_id, node_name, day1Config_file, ecm_template_file, so_version,
                                    subsystem_name, tenant_name):
    log.info('Start to update %s', file_name)
    Report_file.add_line('Start to update ' + file_name)
    try:
        log.info('updating NSD id in Service template ')
        Report_file.add_line('updating NSD id in Service template')
        sit_data = SIT_initialization.get_model_objects(SIT_initialization, 'SIT')
        epis_data = ECM_PI_Initialization.get_model_objects(ECM_PI_Initialization, 'EPIS')
        update_properties = []
        if node_name == 'Dummy':
            # Update site name
            site_name = epis_data._EPIS__site_name
            attribute_list = ['topology_template', 'node_templates', 'geoSite', 'node_filter']
            attr = 'properties'
            prop_value = [{'name': {'equal': site_name}}]
            update_properties.append({'attr_list': attribute_list, "attribute": attr, "value": prop_value})

            attribute_list = ['topology_template', 'node_templates', 'geoSite', 'properties']
            attr = 'name'
            prop_value = site_name
            update_properties.append({'attr_list': attribute_list, "attribute": attr, "value": prop_value})

            # Update nsSubsystem properties
            attribute_list = ['topology_template', 'node_templates', 'nsSubsystem', 'node_filter']
            attr = 'properties'
            prop_value = [{'name': {'equal': subsystem_name}}]
            update_properties.append({'attr_list': attribute_list, "attribute": attr, "value": prop_value})

            attribute_list = ['topology_template', 'node_templates', 'nsSubsystem','properties']
            attr = 'name'
            prop_value = subsystem_name
            update_properties.append({'attr_list': attribute_list, "attribute": attr, "value": prop_value})

            attribute_list = ['topology_template', 'node_templates', 'nsSubsystem', 'properties']
            attr = 'accessId'
            prop_value = tenant_name
            update_properties.append({'attr_list': attribute_list, "attribute": attr, "value": prop_value})

            # Update NSD Id
            attribute_list = ['topology_template', 'node_templates', 'mmeTargetVnfNS', 'properties']
            attr = 'SO_NS::nsdId'
            prop_value = nsd_id
            update_properties.append({'attr_list': attribute_list, "attribute": attr, "value": prop_value})

            # Update Vimzone values
            vimzone_name = sit_data._SIT__vimzone_name
            attribute_list = ['topology_template', 'node_templates', 'vimZone', 'node_filter']
            attr = 'properties'
            prop_value = [{'name': {'equal': vimzone_name}}]
            update_properties.append({'attr_list': attribute_list, "attribute": attr, "value": prop_value})

            attribute_list = ['topology_template', 'node_templates', 'vimZone', 'properties']
            attr = 'name'
            prop_value = vimzone_name
            update_properties.append({'attr_list': attribute_list, "attribute": attr, "value": prop_value})

            # Update MME values
            vnfd_id_mme = sit_data._SIT__vnf_packageId
            vnfm_id = sit_data._SIT__vnfManagers
            vapp_name = sit_data._SIT__name

            attribute_list = ['topology_template', 'node_templates', 'mme', 'properties']
            attr = 'name'
            prop_value = vapp_name
            update_properties.append({'attr_list': attribute_list, "attribute": attr, "value": prop_value})

            attribute_list = ['topology_template', 'node_templates', 'mme', 'properties']
            attr = 'CUSTOM_VNF::vnfdId_mme'
            prop_value = vnfd_id_mme
            update_properties.append({'attr_list': attribute_list, "attribute": attr, "value": prop_value})

            attribute_list = ['topology_template', 'node_templates', 'mme', 'properties']
            attr = 'CUSTOM_VNF::vnfm_Id'
            prop_value = vnfm_id
            update_properties.append({'attr_list': attribute_list, "attribute": attr, "value": prop_value})

            # Update Default values
            attribute_list = ['topology_template', 'inputs', 'connectionName']
            update_properties.append({'attr_list': attribute_list, "attribute": 'default', "value": tenant_name})

            attribute_list = ['topology_template', 'inputs', 'subsystemName']
            update_properties.append({'attr_list': attribute_list, "attribute": 'default', "value": subsystem_name})

            attribute_list = ['topology_template', 'inputs', 'vimZoneName']
            vimzone_name = sit_data._SIT__vimzone_name
            update_properties.append({'attr_list': attribute_list, "attribute": 'default', "value": vimzone_name})

            attribute_list = ['topology_template', 'inputs', 'site']
            site_name = epis_data._EPIS__site_name
            update_properties.append({'attr_list': attribute_list, "attribute": 'default', "value": site_name})

            Json_file_handler.update_st_package(Json_file_handler,
                                                r'com_ericsson_do_auto_integration_files/' + file_name,
                                                update_properties)

        else:
            if node_name == 'MME':
                attribute_list = ['topology_template', 'node_templates', 'mmeTargetVnfNS', 'properties']
                attr = 'nsdId'
                attribute_list1 = ['topology_template', 'node_templates', 'so_mme', 'properties', 'customTemplates', 0]
                Json_file_handler.update_nested_dict_yaml(Json_file_handler,
                                                          r'com_ericsson_do_auto_integration_files/' + file_name,
                                                          attribute_list1, 'catalogRef', day1Config_file)
                attribute_list2 = ['topology_template', 'node_templates', 'mmeTargetVnfNS', 'properties', 'customTemplates',
                                   0]
                Json_file_handler.update_nested_dict_yaml(Json_file_handler,
                                                          r'com_ericsson_do_auto_integration_files/' + file_name,
                                                          attribute_list2, 'catalogRef', ecm_template_file)

            elif node_name == 'EPG':
                attribute_list = ['topology_template', 'inputs', 'nsdId']
                attr = 'default'
                attribute_list1 = ['topology_template', 'node_templates', 'so_epg', 'properties', 'customTemplates', 0]
                Json_file_handler.update_nested_dict_yaml(Json_file_handler,
                                                          r'com_ericsson_do_auto_integration_files/' + file_name,
                                                          attribute_list1, 'catalogRef', day1Config_file)
                attribute_list2 = ['topology_template', 'node_templates', 'targetVNF_NS', 'properties', 'customTemplates',
                                   0]
                Json_file_handler.update_nested_dict_yaml(Json_file_handler,
                                                          r'com_ericsson_do_auto_integration_files/' + file_name,
                                                          attribute_list2, 'catalogRef', ecm_template_file)

            else:
                # attribute_list = ['topology_template', 'node_templates', 'targetVNF_NS', 'properties'] only updating the default section in ST
                attribute_list = ['topology_template', 'inputs', 'nsdId']
                attr = 'default'

            Json_file_handler.update_nested_dict_yaml(Json_file_handler,
                                                      r'com_ericsson_do_auto_integration_files/' + file_name,
                                                      attribute_list, attr, nsd_id)

            if so_version >= version.parse('2.0.0-70'):
                new_attribute_list1 = ['topology_template', 'inputs', 'connectionName']
                Json_file_handler.update_nested_dict_yaml(Json_file_handler,
                                                          r'com_ericsson_do_auto_integration_files/' + file_name,
                                                          new_attribute_list1, 'default', tenant_name)
                new_attribute_list2 = ['topology_template', 'inputs', 'subsystemName']
                Json_file_handler.update_nested_dict_yaml(Json_file_handler,
                                                          r'com_ericsson_do_auto_integration_files/' + file_name,
                                                          new_attribute_list2, 'default', subsystem_name)

        log.info('Finished to update %s', file_name)
        Report_file.add_line('Finished to update ' + file_name)

    except Exception as e:
        log.error('Error while updating %s with error %s', file_name, str(e))
        Report_file.add_line('Error while updating ' + file_name + ',check logs for more details')
        assert False


def update_network_service_file(file_name, so_version):
    log.info('Start to update %s', file_name)
    Report_file.add_line('Start to update ' + file_name)
    try:

        sit_data = SIT_initialization.get_model_objects(SIT_initialization, 'SIT')
        service_model_id = sit_data._SIT__service_model_id
        vimzone_name = sit_data._SIT__vimzone_name
        tenant_name = sit_data._SIT__tenantName
        subsystem_name = sit_data._SIT__subsystem_name
        vnfd_id = sit_data._SIT__vnf_packageId
        name = sit_data._SIT__name
        vnfManagers_id = sit_data._SIT__vnfManagers

        if so_version >= version.parse('2.11.0-118'):

            action_data = {
                "description": "",
                "category": "",
                "@type": "ServiceOrder",
                "serviceOrderItem": [
                    {
                        "action": "add",
                        "id": "1",
                        "@type": "ServiceOrderItem",
                        "service": {
                            "name": name,
                            "description": "",
                            "type": "RFS",
                            "serviceSpecification": {
                                "name": "create",
                                "description": "Dummy VNF creation",
                                "serviceModelId": service_model_id,
                                "id": sit_data._SIT__invariant_uuid,
                                "version": "1.0"
                            },
                            "serviceCharacteristic": [
                                {
                                    "name": "vimZoneName",
                                    "value": vimzone_name
                                },
                                {
                                    "name": "serviceName",
                                    "value": "enterprise_service"
                                },
                                {
                                    "name": "subsystemName",
                                    "value": subsystem_name
                                },
                                {
                                    "name": "connectionName",
                                    "value": tenant_name
                                },
                                {
                                    "name": "vnfName_mme",
                                    "value": name
                                },
                                {
                                    "name": "vnfdId_mme",
                                    "value": vnfd_id
                                },
                                {
                                    "name": "vnfm_Id",
                                    "value": vnfManagers_id
                                }
                            ]
                        }
                    }
                ]
            }

        else:
            action_data = {
                "name": name,
                "serviceModelId": service_model_id,
                "description": "VNF creation",
                "inputs": [
                    {
                        "name": "vimZoneName",
                        "value": vimzone_name
                    },
                    {
                        "name": "serviceName",
                        "value": "enterprise_service"
                    },
                    {
                        "name": "subsystemName",
                        "value": subsystem_name
                    },
                    {
                        "name": "connectionName",
                        "value": tenant_name
                    },
                    {
                        "name": "vnfName_mme",
                        "value": name
                    },
                    {
                        "name": "vnfdId_mme",
                        "value": vnfd_id
                    },
                    {
                        "name": "vnfm_Id",
                        "value": vnfManagers_id
                    }
                ]
            }

        Json_file_handler.update_json_file(Json_file_handler, r'com_ericsson_do_auto_integration_files/' + file_name,
                                           action_data)
        log.info('Finished to update %s', file_name)
        Report_file.add_line('Finished to update ' + file_name)
    except Exception as e:

        log.error('Error while updating %s with error %s', file_name, str(e))
        Report_file.add_line('Error while updating ' + file_name + ',check logs for more details')


def update_mme_network_service_file(file_name, so_version):
    log.info('Start to update %s', file_name)
    Report_file.add_line('Start to update ' + file_name)
    try:

        sit_data = SIT_initialization.get_model_objects(SIT_initialization, 'SIT')
        service_model_id = sit_data._SIT__service_model_id
        vimzone_name = sit_data._SIT__vimzone_name
        tenant_name = sit_data._SIT__tenantName
        subsystem_name = sit_data._SIT__subsystem_name
        vnfd_id = sit_data._SIT__mme_packageId
        vnfManagers_id = sit_data._SIT__vnfManagers
        ipam_vnfd_id = sit_data._SIT__vnf_packageId

        if so_version >= version.parse('2.11.0-118'):

            action_data = {
                "description": "",
                "category": "",
                "@type": "ServiceOrder",
                "serviceOrderItem": [
                    {
                        "action": "add",
                        "id": "1",
                        "@type": "ServiceOrderItem",
                        "service": {
                            "name": sit_data._SIT__mme_package_name,
                            "description": "",
                            "type": "RFS",
                            "serviceSpecification": {
                                "name": "create",
                                "description": "mme VNF creation",
                                "serviceModelId": service_model_id,
                                "id": sit_data._SIT__invariant_uuid,
                                "version": "1.0"
                            },
                            "serviceCharacteristic": [
                                {
                                    "name": "vimZoneName",
                                    "value": vimzone_name
                                },
                                {
                                    "name": "serviceName",
                                    "value": "demo_so"
                                },
                                {
                                    "name": "subsystemName",
                                    "value": subsystem_name
                                },
                                {
                                    "name": "connectionName",
                                    "value": tenant_name
                                },
                                {
                                    "name": "networkVNF_vnfdId",
                                    "value": ipam_vnfd_id
                                },
                                {
                                    "name": "vnfName_mme",
                                    "value": sit_data._SIT__mme_package_name
                                },
                                {
                                    "name": "vnfdId_mme",
                                    "value": vnfd_id
                                },
                                {
                                    "name": "vnfm_Id",
                                    "value": vnfManagers_id
                                }
                            ]
                        }
                    }
                ]
            }

        else:
            action_data = {
                "name": sit_data._SIT__mme_package_name,
                "serviceModelId": service_model_id,
                "description": " mme VNF creation",
                "inputs": [
                    {
                        "name": "vimZoneName",
                        "value": vimzone_name
                    },
                    {
                        "name": "serviceName",
                        "value": "demo_so"
                    },
                    {
                        "name": "subsystemName",
                        "value": subsystem_name
                    },
                    {
                        "name": "connectionName",
                        "value": tenant_name
                    },
                    {
                        "name": "networkVNF_vnfdId",
                        "value": ipam_vnfd_id
                    },
                    {
                        "name": "vnfName_mme",
                        "value": sit_data._SIT__mme_package_name
                    },
                    {
                        "name": "vnfdId_mme",
                        "value": vnfd_id
                    },
                    {
                        "name": "vnfm_Id",
                        "value": vnfManagers_id
                    }
                ]
            }

        Json_file_handler.update_json_file(Json_file_handler, r'com_ericsson_do_auto_integration_files/' + file_name,
                                           action_data)
        log.info('Finished to update %s', file_name)
        Report_file.add_line('Finished to update ' + file_name)
    except Exception as e:

        log.error('Error while updating %s with error %s', file_name, str(e))
        Report_file.add_line('Error while updating ' + file_name + ',check logs for more details')


def update_epg_uds_so_network_service_file(file_name, so_version):
    log.info('Start to update %s', file_name)
    Report_file.add_line('Start to update ' + file_name)
    try:
        sit_data = SIT_initialization.get_model_objects(SIT_initialization, 'SIT')
        service_model_id = sit_data._SIT__service_model_id
        nsd_id = sit_data._SIT__nsd_id
        vimzone_name = sit_data._SIT__vimzone_name
        tenant_name = sit_data._SIT__tenantName
        subsystem_name = sit_data._SIT__subsystem_name
        vnfd_id = sit_data._SIT__vnf_packageId
        vnfManagers_id = sit_data._SIT__vnfManagers

        file_data = Json_file_handler.get_json_data(Json_file_handler,
                                                    r'com_ericsson_do_auto_integration_files/VNFD_Wrapper_EPG.json')
        ip_address = file_data['instantiateVnfOpConfig']['vnfIpAddress']

        if so_version >= version.parse('2.11.0-118'):
            data = {
                "description": "",
                "category": "",
                "@type": "ServiceOrder",
                "serviceOrderItem": [
                    {
                        "action": "add",
                        "id": "1",
                        "@type": "ServiceOrderItem",
                        "service": {
                            "name": sit_data._SIT__name,
                            "description": "",
                            "type": "RFS",
                            "serviceSpecification": {
                                "name": "create",
                                "description": "VNF creation using UDS template",
                                "serviceModelId": service_model_id,
                                "id": sit_data._SIT__invariant_uuid,
                                "version": "1.0"
                            },
                            "serviceCharacteristic": [
                                {
                                    "name": "so_networkservice_nsName",
                                    "value": sit_data._SIT__name
                                },
                                {
                                    "name": "so_networkservice_nsDescription",
                                    "value": "EPG Deployment using template created by UDS"
                                },
                                {
                                    "name": "so_epg_vimZoneName",
                                    "value": vimzone_name
                                },
                                {
                                    "name": "so_epg_vnfm_Id",
                                    "value": vnfManagers_id
                                },
                                {
                                    "name": "so_networkservice_nsdId",
                                    "value": nsd_id
                                },
                                {
                                    "name": "so_networkservice_tenant",
                                    "value": tenant_name
                                },
                                {
                                    "name": "so_epg_vnfdId_epg",
                                    "value": vnfd_id
                                },
                                {
                                    "name": "so_epg_alias",
                                    "value": sit_data._SIT__name
                                },
                                {
                                    "name": "so_networkservice_connectionName",
                                    "value": "ECM"
                                },
                                {
                                    "name": "so_networkservice_subsystemName",
                                    "value": subsystem_name
                                },
                                {
                                    "name": "so_epg_vEPG_service_ip",
                                    "value": ip_address
                                }
                            ]
                        }
                    }
                ]
            }

        else:

            data = {
                "name": sit_data._SIT__name,
                "serviceModelId": service_model_id,
                "description": "VNF creation using UDS template",
                "inputs": [
                    {
                        "name": "so_networkservice_nsName",
                        "value": sit_data._SIT__name
                    },
                    {
                        "name": "so_networkservice_nsDescription",
                        "value": "EPG Deployment using template created by UDS"
                    },
                    {
                        "name": "so_epg_vimZoneName",
                        "value": vimzone_name
                    },
                    {
                        "name": "so_epg_vnfm_Id",
                        "value": vnfManagers_id
                    },
                    {
                        "name": "so_networkservice_nsdId",
                        "value": nsd_id
                    },
                    {
                        "name": "so_networkservice_tenant",
                        "value": tenant_name
                    },
                    {
                        "name": "so_epg_vnfdId_epg",
                        "value": vnfd_id
                    },
                    {
                        "name": "so_epg_alias",
                        "value": sit_data._SIT__name
                    },
                    {
                        "name": "so_networkservice_connectionName",
                        "value": "ECM"
                    },
                    {
                        "name": "so_networkservice_subsystemName",
                        "value": subsystem_name
                    },
                    {
                        "name": "so_epg_vEPG_service_ip",
                        "value": ip_address
                    }
                ]
            }
        Json_file_handler.update_json_file(Json_file_handler, r'com_ericsson_do_auto_integration_files/' + file_name,
                                           data)
        log.info('Finished to update %s', file_name)
        Report_file.add_line('Finished to update ' + file_name)

    except Exception as e:

        log.error('Error while updating %s with error %s', file_name, str(e))
        Report_file.add_line('Error while updating ' + file_name + ',check logs for more details')


def update_epg_network_service_file(file_name, so_version):
    log.info('Start to update %s', file_name)
    Report_file.add_line('Start to update ' + file_name)
    try:

        sit_data = SIT_initialization.get_model_objects(SIT_initialization, 'SIT')
        service_model_id = sit_data._SIT__service_model_id
        nsd_id = sit_data._SIT__nsd_id
        vimzone_name = sit_data._SIT__vimzone_name
        tenant_name = sit_data._SIT__tenantName
        subsystem_name = sit_data._SIT__subsystem_name
        vnfd_id = sit_data._SIT__vnf_packageId
        vnfManagers_id = sit_data._SIT__vnfManagers

        file_data = Json_file_handler.get_json_data(Json_file_handler,
                                                    r'com_ericsson_do_auto_integration_files/VNFD_Wrapper_EPG.json')
        ip_address = file_data['instantiateVnfOpConfig']['vnfIpAddress']

        if so_version >= version.parse('2.11.0-118'):

            data = {
                "description": "",
                "category": "",
                "@type": "ServiceOrder",
                "serviceOrderItem": [
                    {
                        "action": "add",
                        "id": "1",
                        "@type": "ServiceOrderItem",
                        "service": {
                            "name": sit_data._SIT__name,
                            "description": "",
                            "type": "RFS",
                            "serviceSpecification": {
                                "name": "create",
                                "description": "VNF creation",
                                "serviceModelId": service_model_id,
                                "id": sit_data._SIT__invariant_uuid,
                                "version": "1.0"
                            },
                            "serviceCharacteristic": [
                                {
                                    "name": "vEPG_service_ip",
                                    "value": ip_address
                                },
                                {
                                    "name": "VimZone",
                                    "value": vimzone_name
                                },
                                {
                                    "name": "serviceName",
                                    "value": "EPG_service"
                                },
                                {
                                    "name": "subsystemName",
                                    "value": subsystem_name
                                },
                                {
                                    "name": "connectionName",
                                    "value": tenant_name
                                },
                                {
                                    "name": "vnfName_epg",
                                    "value": sit_data._SIT__name
                                },
                                {
                                    "name": "vnfdId_epg",
                                    "value": vnfd_id
                                },
                                {
                                    "name": "vnfm_Id",
                                    "value": vnfManagers_id
                                }
                            ]
                        }
                    }
                ]
            }
        else:
            data = {
                "name": sit_data._SIT__name,
                "serviceModelId": service_model_id,
                "description": "VNF creation",
                "inputs": [
                    {
                        "name": "vEPG_service_ip",
                        "value": ip_address
                    },
                    {
                        "name": "VimZone",
                        "value": vimzone_name
                    },
                    {
                        "name": "serviceName",
                        "value": "EPG_service"
                    },
                    {
                        "name": "subsystemName",
                        "value": subsystem_name
                    },
                    {
                        "name": "connectionName",
                        "value": tenant_name
                    },
                    {
                        "name": "vnfName_epg",
                        "value": sit_data._SIT__name
                    },
                    {
                        "name": "vnfdId_epg",
                        "value": vnfd_id
                    },
                    {
                        "name": "vnfm_Id",
                        "value": vnfManagers_id
                    }
                ]
            }

        Json_file_handler.update_json_file(Json_file_handler, r'com_ericsson_do_auto_integration_files/' + file_name,
                                           data)
        log.info('Finished to update %s', file_name)
        Report_file.add_line('Finished to update ' + file_name)
    except Exception as e:

        log.error('Error while updating %s with error %s', file_name, str(e))
        Report_file.add_line('Error while updating ' + file_name + ',check logs for more details')


def update_subsystem_file(file_name, subsystem_name, tenant_name):
    log.info('Start to update %s', file_name)
    Report_file.add_line('Start to update ' + file_name)
    ecm_host_data = Initialization_script.get_model_objects(Initialization_script, 'ECM_CORE')
    enm_data = Initialization_script.get_model_objects(Initialization_script, 'VNFM')
    ecm_hostname = ecm_host_data._Ecm_core__core_vm_hostname
    enm_hostname = ecm_host_data._Ecm_core__enm_hostname
    multi_enm_hostname = ecm_host_data._Ecm_core__multi_enm_hostname

    try:

        Json_file_handler.modify_attribute(Json_file_handler, r'com_ericsson_do_auto_integration_files/' + file_name,
                                           "name", subsystem_name)

        if 'ECM' in subsystem_name or 'SOL005_EOCM' in subsystem_name:

            Json_file_handler.update_any_json_attr(Json_file_handler,
                                                   r'com_ericsson_do_auto_integration_files/' + file_name,
                                                   ['connectionProperties', 0], 'tenant', tenant_name)

            url = 'https://' + ecm_hostname + ':443'
            user_name = ecm_host_data._Ecm_core__ecm_gui_username
            password = ecm_host_data._Ecm_core__ecm_gui_password

        elif 'MULTI_ENM' in subsystem_name:
            url = 'https://' + multi_enm_hostname
            user_name = enm_data._Vnfm__authUserName
            password = enm_data._Vnfm__authPassword

        elif 'ENM' in subsystem_name:
            url = 'https://' + enm_hostname
            user_name = enm_data._Vnfm__authUserName
            password = enm_data._Vnfm__authPassword

        Json_file_handler.modify_attribute(Json_file_handler, r'com_ericsson_do_auto_integration_files/' + file_name,
                                           "url", url)
        Json_file_handler.update_any_json_attr(Json_file_handler,
                                               r'com_ericsson_do_auto_integration_files/' + file_name,
                                               ['connectionProperties', 0], 'username', user_name)
        Json_file_handler.update_any_json_attr(Json_file_handler,
                                               r'com_ericsson_do_auto_integration_files/' + file_name,
                                               ['connectionProperties', 0], 'password', password)

        log.info('Finished to update %s', file_name)
        Report_file.add_line('Finished to update ' + file_name)

    except Exception as e:

        log.error('Error while updating %s with error %s', file_name, str(e))
        Report_file.add_line('Error while updating ' + file_name + ',check logs for more details')
        assert False


def update_day1Config_file(file_name, package_name, node_name):
    log.info('Start to update %s', file_name)
    Report_file.add_line('Start to update ' + file_name)
    try:
        Json_file_handler.modify_xml_attr(Json_file_handler, r'com_ericsson_do_auto_integration_files/' + file_name,
                                          'xn:MeContext', 'id', package_name)

        if 'MME' in node_name:
            Json_file_handler.modify_xml_attr(Json_file_handler, r'com_ericsson_do_auto_integration_files/' + file_name,
                                              'xn:VsDataContainer', 'id', package_name)
        else:
            Json_file_handler.modify_xml_attr(Json_file_handler, r'com_ericsson_do_auto_integration_files/' + file_name,
                                              'xn:ManagedElement', 'id', package_name)


    except Exception as e:

        log.error('Error while updating %s with error %s', file_name, str(e))
        Report_file.add_line('Error while updating ' + file_name + ',check logs for more details')


def update_tenant_mapping_file(file_name, tenant, subsystem_id, connection_prop_id):
    log.info('Start to update %s', file_name)
    Report_file.add_line('Start to update ' + file_name)
    try:

        Json_file_handler.modify_attribute(Json_file_handler, r'com_ericsson_do_auto_integration_files/' + file_name,
                                           "tenantName", tenant)
        Json_file_handler.modify_attribute(Json_file_handler, r'com_ericsson_do_auto_integration_files/' + file_name,
                                           "subsystemId", int(subsystem_id))
        Json_file_handler.modify_attribute(Json_file_handler, r'com_ericsson_do_auto_integration_files/' + file_name,
                                           "connectionProperties", [int(connection_prop_id)])

    except Exception as e:

        log.error('Error while updating %s with error %s', file_name, str(e))
        Report_file.add_line('Error while updating ' + file_name + ',check logs for more details')


def update_vnf_param_file(file_name, key):
    log.info('Start to update %s', file_name)
    Report_file.add_line('Start to update ' + file_name)
    try:

        Json_file_handler.modify_attribute(Json_file_handler, r'com_ericsson_do_auto_integration_files/' + file_name,
                                           "admin_authorized_key", key)


    except Exception as e:

        log.error('Error while updating %s with error %s', file_name, str(e))
        Report_file.add_line('Error while updating ' + file_name + ',check logs for more details')


def update_sol005_bgf_network_service_file(file_name, external_network_system_id, sub_network_system_id, nsd_id,
                                           so_version):
    log.info('Start to update %s', file_name)
    Report_file.add_line('Start to update ' + file_name)
    try:

        sit_data = SIT_initialization.get_model_objects(SIT_initialization, 'SIT')
        service_model_id = sit_data._SIT__service_model_id
        vimzone_name = sit_data._SIT__vimzone_name
        subsystem_name = sit_data._SIT__subsystem_name
        vnfManagers_id = sit_data._SIT__vnfManagers
        vdc = sit_data._SIT__vdc_id
        tosca_bgf_ip = sit_data._SIT__bgf_tosca_ip
        name = Common_utilities.get_name_with_timestamp(Common_utilities, 'Test_Sol005_vBGF')

        if so_version >= version.parse('2.11.0-118'):
            action_data = {
                "description": "",
                "category": "",
                "@type": "ServiceOrder",
                "serviceOrderItem": [
                    {
                        "action": "add",
                        "id": "1",
                        "@type": "ServiceOrderItem",
                        "service": {
                            "name": name,
                            "description": "",
                            "type": "RFS",
                            "serviceSpecification": {
                                "name": "create",
                                "description": "vBGF creation",
                                "serviceModelId": service_model_id,
                                "id": sit_data._SIT__invariant_uuid,
                                "version": "1.0"
                            },
                            "serviceCharacteristic": [
                                {
                                    "name": "vnfInstanceName",
                                    "value": name
                                },
                                {
                                    "name": "networkServiceDescription",
                                    "value": "Instantiate_vBGF_sol005"
                                },
                                {
                                    "name": "targetVdc",
                                    "value": vdc
                                },
                                {
                                    "name": "networkServiceName",
                                    "value": name
                                },
                                {
                                    "name": "external_subnet_v4_resource_ref_id",
                                    "value": sub_network_system_id
                                },
                                {
                                    "name": "mip_port_public_ip_addr",
                                    "value": tosca_bgf_ip
                                },
                                {
                                    "name": "connected_virtual_network_ext",
                                    "value": external_network_system_id
                                },
                                {
                                    "name": "subsystemName",
                                    "value": subsystem_name
                                },
                                {
                                    "name": "external_subnet_v4_id",
                                    "value": sub_network_system_id
                                },
                                {
                                    "name": "networkServiceDescriptorId",
                                    "value": nsd_id
                                },
                                {
                                    "name": "vimZoneName",
                                    "value": vimzone_name
                                },
                                {
                                    "name": "mip_port_ip_addr",
                                    "value": tosca_bgf_ip
                                },
                                {
                                    "name": "connectionName",
                                    "value": "ECM_Sol005"
                                },
                                {
                                    "name": "pl_active_flavor",
                                    "value": "CM-TOSCA_SOL_BGF_FLAVOR"
                                },
                                {
                                    "name": "vnfmId",
                                    "value": vnfManagers_id
                                }
                            ]
                        }
                    }
                ]
            }


        else:

            action_data = {
                "name": name,
                "serviceModelId": service_model_id,
                "description": "VNF creation",
                "inputs": [
                    {
                        "name": "vnfInstanceName",
                        "value": name
                    },
                    {
                        "name": "networkServiceDescription",
                        "value": "Instantiate_vBGF_sol005"
                    },
                    {
                        "name": "targetVdc",
                        "value": vdc
                    },
                    {
                        "name": "networkServiceName",
                        "value": name
                    },
                    {
                        "name": "external_subnet_v4_resource_ref_id",
                        "value": sub_network_system_id
                    },
                    {
                        "name": "mip_port_public_ip_addr",
                        "value": tosca_bgf_ip
                    },
                    {
                        "name": "connected_virtual_network_ext",
                        "value": external_network_system_id
                    },
                    {
                        "name": "subsystemName",
                        "value": subsystem_name
                    },
                    {
                        "name": "external_subnet_v4_id",
                        "value": sub_network_system_id
                    },
                    {
                        "name": "networkServiceDescriptorId",
                        "value": nsd_id
                    },
                    {
                        "name": "vimZoneName",
                        "value": vimzone_name
                    },
                    {
                        "name": "mip_port_ip_addr",
                        "value": tosca_bgf_ip
                    },
                    {
                        "name": "connectionName",
                        "value": "ECM_Sol005"
                    },
                    {
                        "name": "pl_active_flavor",
                        "value": "CM-TOSCA_SOL_BGF_FLAVOR"
                    },
                    {
                        "name": "vnfmId",
                        "value": vnfManagers_id
                    }
                ]
            }

        Json_file_handler.update_json_file(Json_file_handler, r'com_ericsson_do_auto_integration_files/' + file_name,
                                           action_data)

        log.info('Finished to update %s', file_name)
        Report_file.add_line('Finished to update ' + file_name)

    except Exception as e:

        log.error('Error while updating %s with error %s', file_name, str(e))
        Report_file.add_line('Error while updating ' + file_name + ',check logs for more details')


def update_sol_dummy_network_service_file(file_name, external_network_system_id, nsd_id, onboard_package_name,
                                          so_version):
    log.info('Start to update %s', file_name)
    Report_file.add_line('Start to update ' + file_name)
    try:

        sit_data = SIT_initialization.get_model_objects(SIT_initialization, 'SIT')
        service_model_id = sit_data._SIT__service_model_id
        vimzone_name = sit_data._SIT__vimzone_name
        subsystem_name = sit_data._SIT__subsystem_name
        vnfManagers_id = sit_data._SIT__vnfManagers
        vdc = sit_data._SIT__vdc_id
        external_subnet_cidr = sit_data._SIT__external_subnet_cidr
        external_subnet_gateway = sit_data._SIT__external_subnet_gateway
        external_ip_for_services_vm = sit_data._SIT__external_ip_for_services_vm

        if so_version >= version.parse('2.11.0-118'):

            service_data = {
                "description": "",
                "category": "",
                "@type": "ServiceOrder",
                "serviceOrderItem": [
                    {
                        "action": "add",
                        "id": "1",
                        "@type": "ServiceOrderItem",
                        "service": {
                            "name": onboard_package_name,
                            "description": "",
                            "type": "RFS",
                            "serviceSpecification": {
                                "name": "create",
                                "description": "Scalable dummy node",
                                "serviceModelId": service_model_id,
                                "id": sit_data._SIT__invariant_uuid,
                                "version": "1.0"
                            },
                            "serviceCharacteristic": [
                                {
                                    "name": "networkId",
                                    "value": external_network_system_id
                                },
                                {
                                    "name": "vnfInstanceName",
                                    "value": onboard_package_name
                                },
                                {
                                    "name": "networkServiceDescription",
                                    "value": "sol005-scale-ns-instance NS"
                                },
                                {
                                    "name": "external_subnet_cidr",
                                    "value": external_subnet_cidr
                                },
                                {
                                    "name": "targetVdc",
                                    "value": vdc
                                },
                                {
                                    "name": "networkServiceName",
                                    "value": "vnflaf_service"
                                },
                                {
                                    "name": "networkServiceDescriptorId",
                                    "value": nsd_id
                                },
                                {
                                    "name": "subsystemName",
                                    "value": subsystem_name
                                },
                                {
                                    "name": "vimZoneName",
                                    "value": vimzone_name
                                },
                                {
                                    "name": "enmNodeIp",
                                    "value": "11.11.11.11"
                                },
                                {
                                    "name": "connectionName",
                                    "value": "ECM_Sol005"
                                },
                                {
                                    "name": "vnfmId",
                                    "value": vnfManagers_id
                                },
                                {
                                    "name": "external_subnet_gateway",
                                    "value": external_subnet_gateway
                                },
                                {
                                    "name": "external_ip_for_services_vm",
                                    "value": external_ip_for_services_vm
                                }
                            ]
                        }
                    }
                ]
            }


        else:

            service_data = {
                "name": onboard_package_name,
                "serviceModelId": service_model_id,
                "description": 'Scalable dummy node',
                "inputs": [
                    {
                        "name": "networkId",
                        "value": external_network_system_id
                    },
                    {
                        "name": "vnfInstanceName",
                        "value": onboard_package_name
                    },
                    {
                        "name": "networkServiceDescription",
                        "value": "sol005-scale-ns-instance NS"
                    },
                    {
                        "name": "external_subnet_cidr",
                        "value": external_subnet_cidr
                    },
                    {
                        "name": "targetVdc",
                        "value": vdc
                    },
                    {
                        "name": "networkServiceName",
                        "value": "vnflaf_service"
                    },
                    {
                        "name": "networkServiceDescriptorId",
                        "value": nsd_id
                    },
                    {
                        "name": "subsystemName",
                        "value": subsystem_name
                    },
                    {
                        "name": "vimZoneName",
                        "value": vimzone_name
                    },
                    {
                        "name": "enmNodeIp",
                        "value": "11.11.11.11"
                    },
                    {
                        "name": "connectionName",
                        "value": "ECM_Sol005"
                    },
                    {
                        "name": "vnfmId",
                        "value": vnfManagers_id
                    },
                    {
                        "name": "external_subnet_gateway",
                        "value": external_subnet_gateway
                    },
                    {
                        "name": "external_ip_for_services_vm",
                        "value": external_ip_for_services_vm
                    }
                ]}

        Json_file_handler.update_json_file(Json_file_handler, r'com_ericsson_do_auto_integration_files/' + file_name,
                                           service_data)

        log.info('Finished to update %s', file_name)
        Report_file.add_line('Finished to update ' + file_name)

    except Exception as e:

        log.error('Error while updating %s with error %s', file_name, str(e))
        Report_file.add_line('Error while updating ' + file_name + ',check logs for more details')


def update_epg_tosca_service_json_file(file_name, external_network_system_id, sub_network_system_id,
                                       onboard_package_name, so_version):
    log.info('Start to update %s', file_name)
    Report_file.add_line('Start to update ' + file_name)
    try:

        sit_data = SIT_initialization.get_model_objects(SIT_initialization, 'SIT')
        service_model_id = sit_data._SIT__service_model_id
        subsystem_name = sit_data._SIT__subsystem_name
        vnfManagers_id = sit_data._SIT__vnfManagers
        vdc = sit_data._SIT__vdc_id

        if so_version >= version.parse('2.11.0-118'):

            service_data = {
                "description": "",
                "category": "",
                "@type": "ServiceOrder",
                "serviceOrderItem": [
                    {
                        "action": "add",
                        "id": "1",
                        "@type": "ServiceOrderItem",
                        "service": {
                            "name": onboard_package_name,
                            "description": "",
                            "type": "RFS",
                            "serviceSpecification": {
                                "name": "create",
                                "description": "Tosca EPG creation",
                                "serviceModelId": service_model_id,
                                "id": sit_data._SIT__invariant_uuid,
                                "version": "1.0"
                            },
                            "serviceCharacteristic": [
                                {
                                    "name": "vnfInstanceName",
                                    "value": onboard_package_name
                                },

                                {
                                    "name": "targetVdc",
                                    "value": vdc
                                }
                                ,
                                {
                                    "name": "connectedVn",
                                    "value": external_network_system_id
                                }
                                ,
                                {
                                    "name": "subsystemName",
                                    "value": subsystem_name
                                },

                                {
                                    "name": "connectionName",
                                    "value": "ECM_Sol005"
                                },
                                {
                                    "name": "vnfmId",
                                    "value": vnfManagers_id
                                },
                                {
                                    "name": "subnetId",
                                    "value": sub_network_system_id
                                }
                            ]
                        }
                    }
                ]
            }

        else:
            service_data = {
                "name": onboard_package_name,
                "serviceModelId": service_model_id,
                "description": 'Scalable dummy node',
                "inputs": [
                    {
                        "name": "vnfInstanceName",
                        "value": onboard_package_name
                    },

                    {
                        "name": "targetVdc",
                        "value": vdc
                    }
                    ,
                    {
                        "name": "connectedVn",
                        "value": external_network_system_id
                    }
                    ,
                    {
                        "name": "subsystemName",
                        "value": subsystem_name
                    },

                    {
                        "name": "connectionName",
                        "value": "ECM_Sol005"
                    },
                    {
                        "name": "vnfmId",
                        "value": vnfManagers_id
                    },
                    {
                        "name": "subnetId",
                        "value": sub_network_system_id
                    }
                ]}

        Json_file_handler.update_json_file(Json_file_handler, r'com_ericsson_do_auto_integration_files/' + file_name,
                                           service_data)

        log.info('Finished to update %s', file_name)
        Report_file.add_line('Finished to update ' + file_name)

    except Exception as e:

        log.error('Error while updating %s with error %s', file_name, str(e))
        Report_file.add_line('Error while updating ' + file_name + ',check logs for more details')


def update_etsi_tosca_network_service_file(file_name, external_network_system_id, nsd_id, onboard_package_name,
                                           so_version):
    log.info('Start to update %s', file_name)
    Report_file.add_line('Start to update ' + file_name)
    try:

        sit_data = SIT_initialization.get_model_objects(SIT_initialization, 'SIT')
        service_model_id = sit_data._SIT__service_model_id
        vimzone_name = sit_data._SIT__vimzone_name
        subsystem_name = sit_data._SIT__subsystem_name
        vnfManagers_id = sit_data._SIT__vnfManagers
        vdc = sit_data._SIT__vdc_id

        if so_version >= version.parse('2.11.0-118'):

            service_data = {
                "description": "",
                "category": "",
                "@type": "ServiceOrder",
                "serviceOrderItem": [
                    {
                        "action": "add",
                        "id": "1",
                        "@type": "ServiceOrderItem",
                        "service": {
                            "name": onboard_package_name,
                            "description": "",
                            "type": "RFS",
                            "serviceSpecification": {
                                "name": "create",
                                "description": "Unclassified EPG package deploy over sol005",
                                "serviceModelId": service_model_id,
                                "id": sit_data._SIT__invariant_uuid,
                                "version": "1.0"
                            },
                            "serviceCharacteristic": [
                                {
                                    "name": "vnfInstanceName",
                                    "value": onboard_package_name
                                },
                                {
                                    "name": "networkServiceDescription",
                                    "value": "Instantiate_EPG_sol005"
                                },
                                {
                                    "name": "targetVdc",
                                    "value": vdc
                                },
                                {
                                    "name": "networkServiceName",
                                    "value": "epg_sol005"
                                },
                                {
                                    "name": "networkServiceDescriptorId",
                                    "value": nsd_id
                                },
                                {
                                    "name": "subsystemName",
                                    "value": subsystem_name
                                },
                                {
                                    "name": "vimZoneName",
                                    "value": vimzone_name
                                },
                                {
                                    "name": "connectionName",
                                    "value": "ECM_Sol005"
                                },
                                {
                                    "name": "vnfmId",
                                    "value": vnfManagers_id
                                }
                            ]
                        }
                    }
                ]
            }


        else:

            service_data = {
                "name": onboard_package_name,
                "serviceModelId": service_model_id,
                "description": 'Scalable dummy node',
                "inputs": [
                    {
                        "name": "vnfInstanceName",
                        "value": onboard_package_name
                    },
                    {
                        "name": "networkServiceDescription",
                        "value": "Instantiate_EPG_sol005"
                    },
                    {
                        "name": "targetVdc",
                        "value": vdc
                    },
                    {
                        "name": "networkServiceName",
                        "value": "epg_sol005"
                    },
                    {
                        "name": "networkServiceDescriptorId",
                        "value": nsd_id
                    },
                    {
                        "name": "subsystemName",
                        "value": subsystem_name
                    },
                    {
                        "name": "vimZoneName",
                        "value": vimzone_name
                    },
                    {
                        "name": "connectionName",
                        "value": "ECM_Sol005"
                    },
                    {
                        "name": "vnfmId",
                        "value": vnfManagers_id
                    }
                ]}

        Json_file_handler.update_json_file(Json_file_handler, r'com_ericsson_do_auto_integration_files/' + file_name,
                                           service_data)

        log.info('Finished to update %s', file_name)
        Report_file.add_line('Finished to update ' + file_name)

    except Exception as e:

        log.error('Error while updating %s with error %s', file_name, str(e))
        Report_file.add_line('Error while updating ' + file_name + ',check logs for more details')

def update_site_subsystem_vimzone(properties):
    sit_data = SIT_initialization.get_model_objects(SIT_initialization, 'SIT')
    epis_data = ECM_PI_Initialization.get_model_objects(ECM_PI_Initialization, 'EPIS')

    # Update site name
    site_name = epis_data._EPIS__site_name
    attribute_list = ['topology_template', 'node_templates', 'geoSite', 'node_filter']
    attr = 'properties'
    prop_value = [{'name': {'equal': site_name}}]
    properties.append({'attr_list': attribute_list, "attribute": attr, "value": prop_value})

    attribute_list = ['topology_template', 'node_templates', 'geoSite', 'properties']
    attr = 'name'
    prop_value = site_name
    properties.append({'attr_list': attribute_list, "attribute": attr, "value": prop_value})

    # Update Vimzone values
    vimzone_name = sit_data._SIT__vimzone_name
    attribute_list = ['topology_template', 'node_templates', 'vimZone', 'node_filter']
    attr = 'properties'
    prop_value = [{'name': {'equal': vimzone_name}}]
    properties.append({'attr_list': attribute_list, "attribute": attr, "value": prop_value})

    attribute_list = ['topology_template', 'node_templates', 'vimZone', 'properties']
    attr = 'name'
    prop_value = vimzone_name
    properties.append({'attr_list': attribute_list, "attribute": attr, "value": prop_value})

    # Update nsSubsystem properties
    subsystem_name = sit_data._SIT__subsystem_name
    attribute_list = ['topology_template', 'node_templates', 'nsSubsystem', 'node_filter']
    attr = 'properties'
    prop_value = [{'name': {'equal': subsystem_name}}]
    properties.append({'attr_list': attribute_list, "attribute": attr, "value": prop_value})

    attribute_list = ['topology_template', 'node_templates', 'nsSubsystem', 'properties']
    attr = 'name'
    prop_value = subsystem_name
    properties.append({'attr_list': attribute_list, "attribute": attr, "value": prop_value})


def update_sol_service_template(st_file_name, nsparam_form_name, vnfparam_form_name, node_name,
                                day1_template_name=None):

    try:
        log.info('Start to update %s', st_file_name)
        Report_file.add_line('Start to update ' + st_file_name)

        if node_name == "sol005_dummy":
            node = "vnf"
            onboard_package = "ONBOARD_PACKAGE"
        elif node_name == "TEPG":
            node = "EPG"
            onboard_package = "ONBOARD_EPG_TOSCA_PACKAGE"
        elif node_name == "Sol005_EPG":
            node = "EPG"
            onboard_package = "ONBOARD_EPG_PACKAGE"

        # update common parameters
        sit_data = SIT_initialization.get_model_objects(SIT_initialization, 'SIT')
        update_properties = []

        attribute_list = ['topology_template', 'node_templates', 'NS', 'properties', 'SO_RESOURCE::customTemplates',
                          0]
        update_properties.append(
            {'attr_list': attribute_list, "attribute": 'catalogRef', "value": nsparam_form_name})

        attribute_list = ['topology_template', 'node_templates', node, 'properties', 'SO_RESOURCE::customTemplates', 0]
        update_properties.append(
            {'attr_list': attribute_list, "attribute": 'catalogRef', "value": vnfparam_form_name})

        # update nsSubsystem, vimZone name, site name
        update_site_subsystem_vimzone(update_properties)

        targetVdc = sit_data._SIT__vdc_id
        attribute_list = ['topology_template', 'node_templates', 'NS', 'properties']
        attr = 'CUSTOM_NS::targetVdc'
        prop_value = targetVdc
        update_properties.append({'attr_list': attribute_list, "attribute": attr, "value": prop_value})

        vnfmId = sit_data._SIT__vnfManagers
        attribute_list = ['topology_template', 'node_templates', 'NS', 'properties']
        attr = 'CUSTOM_NS::vnfmId'
        prop_value = vnfmId
        update_properties.append({'attr_list': attribute_list, "attribute": attr, "value": prop_value})

        ecm_host_data = ECM_PI_Initialization.get_model_objects(ECM_PI_Initialization, 'ECMPI')
        environment = ecm_host_data._Ecm_PI__ECM_Host_Name
        data_file = r'com_ericsson_do_auto_integration_files/run_time_' + environment + '.json'
        vnf_instance_ame = Json_file_handler.get_json_attr_value(Json_file_handler, data_file,
                                                                onboard_package)
        attribute_list = ['topology_template', 'node_templates', node, 'properties']
        attr = 'name'
        prop_value = vnf_instance_ame
        update_properties.append({'attr_list': attribute_list, "attribute": attr, "value": prop_value})

        if node_name == 'sol005_dummy':
            # Update NS properties
            attribute_list = ['topology_template', 'node_templates', 'NS', 'properties']
            attr = 'name'
            prop_value = 'vnflaf_service'
            update_properties.append({'attr_list': attribute_list, "attribute": attr, "value": prop_value})

            attribute_list = ['topology_template', 'node_templates', 'NS', 'properties']
            attr = 'description'
            prop_value = 'sol005-scale-ns-instance NS'
            update_properties.append({'attr_list': attribute_list, "attribute": attr, "value": prop_value})

            attribute_list = ['topology_template', 'node_templates', 'NS', 'properties']
            attr = 'CUSTOM_NS::enmNodeIp'
            prop_value = '11.11.11.11'
            update_properties.append({'attr_list': attribute_list, "attribute": attr, "value": prop_value})

            external_ip_for_services_vm = sit_data._SIT__external_ip_for_services_vm
            attribute_list = ['topology_template', 'node_templates', 'NS', 'properties']
            attr = 'CUSTOM_NS::external_ip_for_services_vm'
            prop_value = external_ip_for_services_vm
            update_properties.append({'attr_list': attribute_list, "attribute": attr, "value": prop_value})

            external_subnet_cidr = sit_data._SIT__external_subnet_cidr
            attribute_list = ['topology_template', 'node_templates', 'NS', 'properties']
            attr = 'CUSTOM_NS::external_subnet_cidr'
            prop_value = external_subnet_cidr
            update_properties.append({'attr_list': attribute_list, "attribute": attr, "value": prop_value})

            external_subnet_gateway = sit_data._SIT__external_subnet_gateway
            attribute_list = ['topology_template', 'node_templates', 'NS', 'properties']
            attr = 'CUSTOM_NS::external_subnet_gateway'
            prop_value = external_subnet_gateway
            update_properties.append({'attr_list': attribute_list, "attribute": attr, "value": prop_value})

            networkId = sit_data._SIT__external_net_id
            attribute_list = ['topology_template', 'node_templates', 'NS', 'properties']
            attr = 'CUSTOM_NS::networkId'
            prop_value = networkId
            update_properties.append({'attr_list': attribute_list, "attribute": attr, "value": prop_value})

        if node_name in ["TEPG", "Sol005_EPG"]:
            node = "NS" if node_name is "Sol005_EPG" else "EPG"
            attribute_list = ['topology_template', 'node_templates', node, 'properties',
                              'SO_RESOURCE::customTemplates', 1]
            update_properties.append(
                {'attr_list': attribute_list, "attribute": 'catalogRef', "value": day1_template_name})
            nsd_id = sit_data._SIT__nsd_id
            # Update NSD Id
            attribute_list = ['topology_template', 'node_templates', 'NS', 'properties']
            attr = 'SO_NS::nsdId'
            prop_value = nsd_id
            update_properties.append({'attr_list': attribute_list, "attribute": attr, "value": prop_value})

        if node_name == "TEPG":
            sit_data = SIT_initialization.get_model_objects(SIT_initialization, 'SIT')
            external_network_system_id = sit_data._SIT__external_network_system_id
            sub_network_system_id = sit_data._SIT__sub_network_system_id

            attribute_list = ['topology_template', 'node_templates', 'NS', 'properties']
            attr = 'CUSTOM_NS::connectedVn'
            prop_value = external_network_system_id
            update_properties.append({'attr_list': attribute_list, "attribute": attr, "value": prop_value})

            attribute_list = ['topology_template', 'node_templates', 'NS', 'properties']
            attr = 'CUSTOM_NS::subnetId'
            prop_value = sub_network_system_id
            update_properties.append({'attr_list': attribute_list, "attribute": attr, "value": prop_value})

        Report_file.add_line('Start to update ' + str(update_properties))

        Json_file_handler.update_st_package(Json_file_handler,
                                            r'com_ericsson_do_auto_integration_files/' + st_file_name,
                                            update_properties)
    except Exception as e:
        log.error('Error while updating %s with error %s', st_file_name, str(e))
        Report_file.add_line('Error while updating ' + st_file_name + ',check logs for more details')
        assert False


def update_sol_cnf_configmap_st_template(vnf1conf_file, vnf2conf_file, vnf1param_file, vnf2param_file,
                                         cnfparam_file, st_file_name):
    try:
        log.info('Start to update %s', st_file_name)
        sit_data = SIT_initialization.get_model_objects(SIT_initialization, 'SIT')
        update_properties = []
        # update nsSubsystem, vimZone name, site name
        update_site_subsystem_vimzone(update_properties)

        files = {'vnf01': [vnf1param_file, vnf1conf_file], 'vnf02': [vnf2param_file, vnf2conf_file], 'NS': [cnfparam_file]}
        for element, file_names in files.items():
            for i, file in enumerate(file_names):
                attribute_list = ['topology_template', 'node_templates', element, 'properties',
                                  'SO_RESOURCE::customTemplates', i]
                update_properties.append(
                    {'attr_list': attribute_list, "attribute": 'catalogRef', "value": file})

        vnfmId = sit_data._SIT__cnf_vnfm_id
        attribute_list = ['topology_template', 'node_templates', 'NS', 'properties']
        attr = 'CUSTOM_NS::vnfmId'
        prop_value = vnfmId
        update_properties.append({'attr_list': attribute_list, "attribute": attr, "value": prop_value})

        # Update NSD Id
        attribute_list = ['topology_template', 'node_templates', 'NS', 'properties']
        attr = 'SO_NS::nsdId'
        sit_data = SIT_initialization.get_model_objects(SIT_initialization, 'SIT')
        nsd_id = sit_data._SIT__nsd_id
        update_properties.append({'attr_list': attribute_list, "attribute": attr, "value": nsd_id})

        log.info('update properties %s', str(update_properties))
        Json_file_handler.update_st_package(Json_file_handler,
                                            r'com_ericsson_do_auto_integration_files/' + st_file_name,
                                            update_properties)
    except Exception as e:
        log.error('Error while updating %s with error %s', st_file_name, str(e))
        assert False


def update_sol_cnf_configma_netwrok_service_file(file_name, so_version):
    log.info('Start to update %s', file_name)
    Report_file.add_line('Start to update ' + file_name)
    try:

        sit_data = SIT_initialization.get_model_objects(SIT_initialization, 'SIT')
        service_model_id = sit_data._SIT__service_model_id
        subsystem_name = sit_data._SIT__subsystem_name
        vnfManagers_id = sit_data._SIT__cnf_vnfm_id

        name = Common_utilities.get_name_with_timestamp(Common_utilities, 'Test_Sol005_CNF_CONFIGMAP')

        if so_version >= version.parse('2.11.0-118'):

            action_data = {
                "description": "",
                "category": "",
                "@type": "ServiceOrder",
                "serviceOrderItem": [
                    {
                        "action": "add",
                        "id": "1",
                        "@type": "ServiceOrderItem",
                        "service": {
                            "name": name,
                            "description": "",
                            "type": "RFS",
                            "serviceSpecification": {
                                "name": "create",
                                "description": "CNF with configmap feature deployment from SO",
                                "serviceModelId": service_model_id,
                                "id": sit_data._SIT__invariant_uuid,
                                "version": "1.0"
                            },
                            "serviceCharacteristic": [
                                {
                                    "name": "vnf01_vnfInstanceName",
                                    "value": "cnf-configmap-vnf01"
                                },
                                {
                                    "name": "vimZoneName",
                                    "value": "kubernetes"
                                },
                                {
                                    "name": "vnf01_vnfInstanceDescription",
                                    "value": "ETSI NFV SOL 001 vnfd types definitions version 2.5.1"
                                },
                                {
                                    "name": "vnf02_vnfInstanceName",
                                    "value": "cnf-configmap-vnf-02"
                                },
                                {
                                    "name": "subsystemName",
                                    "value": subsystem_name
                                },
                                {
                                    "name": "nsdId",
                                    "value": "nsd-id-3317001212"
                                },
                                {
                                    "name": "networkServiceName",
                                    "value": "CNF_ConfigMap_fromSO"
                                },
                                {
                                    "name": "cismName",
                                    "value": "kubernetes"
                                },
                                {
                                    "name": "connectionName",
                                    "value": "ECM_Sol005"
                                },
                                {
                                    "name": "vnf02_vnfInstanceDescription",
                                    "value": "ETSI NFV SOL 001 vnfd types definitions version 2.5.1"
                                },
                                {
                                    "name": "vnfmId",
                                    "value": vnfManagers_id
                                }
                            ]
                        }
                    }
                ]
            }


        else:

            action_data = {
                "name": name,
                "serviceModelId": service_model_id,
                "description": "CNF with configmap feature deployment from SO",
                "inputs": [
                    {
                        "name": "vnf01_vnfInstanceName",
                        "value": "cnf-configmap-vnf01"
                    },
                    {
                        "name": "vimZoneName",
                        "value": "kubernetes"
                    },
                    {
                        "name": "vnf01_vnfInstanceDescription",
                        "value": "ETSI NFV SOL 001 vnfd types definitions version 2.5.1"
                    },
                    {
                        "name": "vnf02_vnfInstanceName",
                        "value": "cnf-configmap-vnf-02"
                    },
                    {
                        "name": "subsystemName",
                        "value": subsystem_name
                    },
                    {
                        "name": "nsdId",
                        "value": "nsd-id-3317001212"
                    },
                    {
                        "name": "networkServiceName",
                        "value": "CNF_ConfigMap_fromSO"
                    },
                    {
                        "name": "cismName",
                        "value": "kubernetes"
                    },
                    {
                        "name": "connectionName",
                        "value": "ECM_Sol005"
                    },
                    {
                        "name": "vnf02_vnfInstanceDescription",
                        "value": "ETSI NFV SOL 001 vnfd types definitions version 2.5.1"
                    },
                    {
                        "name": "vnfmId",
                        "value": vnfManagers_id
                    }
                ]
            }

        Json_file_handler.update_json_file(Json_file_handler, r'com_ericsson_do_auto_integration_files/' + file_name,
                                           action_data)

        log.info('Finished to update %s', file_name)
        Report_file.add_line('Finished to update ' + file_name)

    except Exception as e:

        log.error('Error while updating %s with error %s', file_name, str(e))
        Report_file.add_line('Error while updating ' + file_name + ',check logs for more details')


def update_service_delete_file(file_name, service_id, service_name):
    try:
        log.info('Updating file %s', file_name)
        Report_file.add_line(f'Updating file {file_name}')

        Json_file_handler.modify_third_level_attr(Json_file_handler, r'com_ericsson_do_auto_integration_files/' + file_name, 'serviceOrderItem',
                                                  0, 'service', 'id', service_id)
        Json_file_handler.modify_third_level_attr(Json_file_handler, r'com_ericsson_do_auto_integration_files/' + file_name, 'serviceOrderItem',
                                                  0, 'service', 'name', service_name)

        log.info('Finished updating file %s', file_name)
        Report_file.add_line(f'Finished updating file {file_name}')

    except Exception as e:
        log.error('Error while updating %s: %s', file_name, str(e))
        Report_file.add_line(f'Error while updating {file_name} check logs for more details')
