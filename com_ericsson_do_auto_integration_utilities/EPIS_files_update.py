import random
import ipaddress
from com_ericsson_do_auto_integration_model.EPIS import EPIS
from com_ericsson_do_auto_integration_model.SIT import SIT
from com_ericsson_do_auto_integration_model.Ecm_PI import Ecm_PI
from com_ericsson_do_auto_integration_model.Ecm_core import Ecm_core
from com_ericsson_do_auto_integration_utilities.Logger import Logger
from com_ericsson_do_auto_integration_utilities.Report_file import Report_file
from com_ericsson_do_auto_integration_utilities.Json_file_handler import Json_file_handler
from com_ericsson_do_auto_integration_initilization.ECM_PI_initialization import ECM_PI_Initialization

log = Logger.get_logger('EPIS_files_update.py')


def update_any_flavor_file(flavor_name, cpu, memory, disk_size, tenant_name, ephemeral_disk=False,
                           ephemeral_disk_size=0):
    filename = r'com_ericsson_do_auto_integration_files/flavour.json'
    log.info('Start to update flavour.json file for ' + flavor_name)
    Report_file.add_line('start to update flavour.json file for ' + flavor_name)
    EPIS_data = ECM_PI_Initialization.get_model_objects(ECM_PI_Initialization, 'EPIS')
    cloud_type = EPIS_data._EPIS__cloudManagerType

    try:

        if cloud_type == 'CEE' and flavor_name != 'EOST-valid9m_flavor':

            log.info('Updating flavour file for the cloud ' + cloud_type)

            data = {
                "name": flavor_name,
                "ram": memory,
                "numberOfCpu": cpu,
                "diskSize": disk_size,
                "extraSpecs": [
                    {
                        "key": "hw:mem_page_size",
                        "value": "1048576"
                    },
                    {
                        "key": "hw:cpu_policy",
                        "value": "dedicated"
                    }
                ]
            }

        else:

            log.info('Updating flavour file for the cloud  ' + cloud_type)

            data = {
                "name": flavor_name,
                "ram": memory,
                "numberOfCpu": cpu,
                "diskSize": disk_size
            }

        Json_file_handler.update_any_json_attr(Json_file_handler, filename, [], 'tenantName', tenant_name)
        Json_file_handler.update_any_json_attr(Json_file_handler, filename, [], 'srt', data)
        if ephemeral_disk:
            Json_file_handler.update_any_json_attr(Json_file_handler, filename, ['srt'], 'ephemeralDiskSize',
                                                   ephemeral_disk_size)

        log.info('Finished to update flavour.json file ')
        Report_file.add_line('Finished to update flavour.json file')
    except Exception as e:

        log.error('Error while updating flavour.json file ' + str(e))
        Report_file.add_line('Error while updating flavour.json file ,check logs for more details')


def update_flavour_file():
    filename = r'com_ericsson_do_auto_integration_files/flavour.json'
    log.info('Start to update flavour.json file ')
    Report_file.add_line('Start to update flavour.json file')
    EPIS_data = ECM_PI_Initialization.get_model_objects(ECM_PI_Initialization, 'EPIS')
    try:

        tenant_name = EPIS_data._EPIS__tenant_name
        flavour_name = EPIS_data._EPIS__flavour_name
        name = flavour_name[3:]
        update_any_flavor_file(name, 2, 6144, 20, tenant_name)
        log.info('Finished to update flavour.json file ')
        Report_file.add_line('Finished to update flavour.json file')

    except Exception as e:

        log.error('Error while updating flavour.json file ' + str(e))
        Report_file.add_line('Error while updating flavour.json file ,check logs for more details')


def update_transfer_flavour_file():
    filename = r'com_ericsson_do_auto_integration_files/flavour_transfer.json'
    log.info('Start to update flavour_transfer.json file ')
    Report_file.add_line('Start to update flavour_transfer.json file')
    EPIS_data = ECM_PI_Initialization.get_model_objects(ECM_PI_Initialization, 'EPIS')

    try:
        cloud_type = EPIS_data._EPIS__cloudManagerType
        vimzone_name = EPIS_data._EPIS__vimzone_name

        data = [
            {
                "name": vimzone_name,
                "type": cloud_type
            }
        ]

        Json_file_handler.update_any_json_attr(Json_file_handler, filename, [], 'vimZones', data)

        log.info('Finished to update flavour_transfer.json file ')
        Report_file.add_line('Finished to update flavour_transfer.json file')

    except Exception as e:

        log.error('Error while updating flavour_transfer.json file ' + str(e))
        Report_file.add_line('Error while updating flavour_transfer.json file ,check logs for more details')


def update_new_vimzone_file(file, end_points_data):
    file_name = r'com_ericsson_do_auto_integration_files/' + file
    EPIS_data = ECM_PI_Initialization.get_model_objects(ECM_PI_Initialization, 'EPIS')
    cloud_type = EPIS_data._EPIS__synccloudManagerType
    vim_zone_name = EPIS_data._EPIS__sync_vimzone_name
    site_name = EPIS_data._EPIS__site_name
    static_project_name = EPIS_data._EPIS__existing_project_name
    static_project_username = EPIS_data._EPIS__existing_project_admin_username
    static_project_password = EPIS_data._EPIS__existing_project_admin_password

    data = {
        "name": static_project_name,
        "adminUserName": static_project_username,
        "adminPassword": static_project_password
    }

    Json_file_handler.modify_attribute(Json_file_handler, file_name, 'name', vim_zone_name)
    Json_file_handler.modify_attribute(Json_file_handler, file_name, 'siteName', site_name)
    Json_file_handler.modify_attribute(Json_file_handler, file_name, 'type', cloud_type)
    Json_file_handler.update_any_json_attr(Json_file_handler, file_name, [], 'credentials', data)
    Json_file_handler.update_any_json_attr(Json_file_handler, file_name, [], 'endPoints', end_points_data)


def update_create_new_project_file(test_hotel, default_user_role):
    file_name = r'com_ericsson_do_auto_integration_files/createnewProject.json'
    try:
        log.info('start updating file %s', file_name)
        tenant_type = EPIS.get_sync_tenant_type(EPIS)
        cloud_type = EPIS.get_cloud_manager_type(EPIS)
        tenant = EPIS.get_tenant_name(EPIS)
        is_cloudnative = Ecm_core.get_is_cloudnative(Ecm_core)

        if test_hotel and is_cloudnative:
            project_name = EPIS.get_existing_project_name(EPIS)
            admin_user_name = EPIS.get_existing_project_admin_username(EPIS)
            admin_password = EPIS.get_existing_project_admin_password(EPIS)
            user_name = EPIS.get_existing_project_user_username(EPIS)
            user_password = EPIS.get_existing_project_user_password(EPIS)

        else:

            project_name = EPIS.get_project_name(EPIS)
            admin_user_name = project_name + '_admin'
            admin_password = project_name.capitalize() + '.laf'
            user_name = project_name + '_user'
            user_password = project_name.capitalize() + '.laf'

        admin_data = {
            "adminUserName": admin_user_name,
            "adminPassword": admin_password,
            "grantedRoles": [{
                "roleName": "admin"
            }]
        }

        user_data = {
            "userName": user_name,
            "userPassword": user_password,
            "grantedRoles": [{
                "roleName": default_user_role
            }]
        }

        data = {'name': project_name, 'type': tenant_type, 'adminUserCredentials': admin_data,
                'userCredentials': user_data}
        Json_file_handler.modify_list_of_attributes(Json_file_handler, file_name, data)
        Json_file_handler.update_any_json_attr(Json_file_handler, file_name, ['tenants', 0],
                                               'tenantName', tenant)

        if cloud_type == 'CEE' and not test_hotel:
            Json_file_handler.modify_attribute(Json_file_handler, file_name, "domainName", cloud_type)
        else:
            Json_file_handler.modify_attribute(Json_file_handler, file_name, "domainName", "Default")
        log.info('updating of file %s completed', file_name)

    except Exception as error:
        log.error("Failed to update file %s: %s", file_name, str(error))
        assert False


def update_createvdc_file(file_name):
    log.info('Start to update createvdc.json file ')
    Report_file.add_line('Start to update createvdc.json file')
    EPIS_data = ECM_PI_Initialization.get_model_objects(ECM_PI_Initialization, 'EPIS')

    try:
        tenant = EPIS_data._EPIS__tenant_name
        vdc_name = 'vdc_' + str(random.randint(0, 999))
        log.info('Going  to create vdc with name  ' + vdc_name)
        Report_file.add_line('Going  to create vdc with name  ' + vdc_name)
        vimzone_name = EPIS_data._EPIS__vimzone_name

        vdc_data = {
            "name": vdc_name,
            "vimZones": [
                vimzone_name
            ],
            "description": "Datacenter for demo"
        }

        data = {'tenantName': tenant, 'vdc': vdc_data}
        Json_file_handler.modify_list_of_attributes(Json_file_handler,
                                                    r'com_ericsson_do_auto_integration_files/' + file_name,
                                                    data)
        log.info('Finished to update createvdc.json file ')
        Report_file.add_line('Finished to update createvdc.json file')

    except Exception as e:

        log.error('Error while updating createvdc.json file ' + str(e))
        Report_file.add_line('Error while updating createvdc.json file ,check logs for more details')


def update_image_file(file_name, image_name, vimzone_name, image_id):
    log.info('Start to update registerImage.json file ' + image_name)
    Report_file.add_line('Start to update registerImage.json file ' + image_name)
    EPIS_data = ECM_PI_Initialization.get_model_objects(ECM_PI_Initialization, 'EPIS')
    cloud_type = EPIS_data._EPIS__cloudManagerType
    tenant = EPIS_data._EPIS__tenant_name

    try:

        if 'ECM' != tenant:
            Json_file_handler.modify_first_level_attr(Json_file_handler,
                                                      r'com_ericsson_do_auto_integration_files/' + file_name,
                                                      'image', 'isPublic', False)

        data = [
            {
                "vimZoneName": vimzone_name,
                "vimZoneType": cloud_type,
                "vimImageObjectId": image_id
            }
        ]

        Json_file_handler.modify_first_level_attr(Json_file_handler,
                                                  r'com_ericsson_do_auto_integration_files/' + file_name,
                                                  'image', 'name', image_name)
        Json_file_handler.modify_first_level_attr(Json_file_handler,
                                                  r'com_ericsson_do_auto_integration_files/' + file_name,
                                                  'image', 'vimImages', data)
        log.info('Finished to update registerImage.json file ')
        Report_file.add_line('Finished to update registerImage.json file')
    except Exception as e:

        log.error('Error while updating registerImage.json file ' + str(e))
        Report_file.add_line('Error while updating registerImage.json file ,check logs for more details')


def update_registerImage_file(file_name):
    EPIS_data = ECM_PI_Initialization.get_model_objects(ECM_PI_Initialization, 'EPIS')

    image_name = EPIS_data._EPIS__image_name
    image_id = EPIS_data._EPIS__image_id
    vimzone_name = EPIS_data._EPIS__vimzone_name

    update_image_file(file_name, image_name, vimzone_name, image_id)


def update_blockStorage_file(file_name, ecm_environment, bsv_name, volume, vdc_id):
    log.info('Start to update BlockStorage.json file ')
    Report_file.add_line('Start to update BlockStrage.json file')
    EPIS_data = ECM_PI_Initialization.get_model_objects(ECM_PI_Initialization, 'EPIS')

    try:
        tenant_name = EPIS_data._EPIS__tenant_name
        diskSize = volume
        vimzone_name = EPIS_data._EPIS__vimzone_name

        data = {

            "name": bsv_name,
            "diskSize": diskSize,
            "vdc": {"id": vdc_id},
            "vimZoneName": vimzone_name
        }

        Json_file_handler.modify_attribute(Json_file_handler,
                                           r'com_ericsson_do_auto_integration_files/' + file_name,
                                           'tenantName', tenant_name)
        Json_file_handler.modify_attribute(Json_file_handler,
                                           r'com_ericsson_do_auto_integration_files/' + file_name, 'bsv',
                                           data)

    except Exception as e:

        log.error('Error while updating BlockStorage.json file ' + str(e))
        Report_file.add_line('Error while updating BlockStorage.json file ,check logs for more details')


def update_create_site_file():
    log.info('Start to update createSite.yaml file ')
    Report_file.add_line('Start to update createSite.yaml file')
    EPIS_data = ECM_PI_Initialization.get_model_objects(ECM_PI_Initialization, 'EPIS')

    file_name = r'com_ericsson_do_auto_integration_files/CreateSite.yaml'
    site_name = EPIS_data._EPIS__site_name
    id = site_name.replace(' ', '')
    Json_file_handler.update_third_attr_yaml(Json_file_handler, file_name, 'create', 'sites', 'id', id)
    Json_file_handler.update_third_attr_yaml(Json_file_handler, file_name, 'create', 'sites', 'name',
                                             site_name)
    log.info('Updated createSite.yaml file ')
    Report_file.add_line('updated createSite.yaml file')


def update_dev_stack_vimzone_file(file):
    file_name = r'com_ericsson_do_auto_integration_files/' + file
    EPIS_data = ECM_PI_Initialization.get_model_objects(ECM_PI_Initialization, 'EPIS')
    cloud_type = EPIS_data._EPIS__cloudManagerType
    vim_zone_name = EPIS_data._EPIS__vimzone_name
    site_name = EPIS_data._EPIS__site_name
    static_project_name = EPIS_data._EPIS__static_project
    static_project_username = EPIS_data._EPIS__static_project_username
    static_project_password = EPIS_data._EPIS__static_project_password
    vim_url = EPIS_data._EPIS__vim_url
    ip = vim_url[7:-9:]

    data = {
        "name": static_project_name,
        "adminUserName": static_project_username,
        "adminPassword": static_project_password
    }

    Json_file_handler.modify_attribute(Json_file_handler, file_name, 'name', vim_zone_name)
    Json_file_handler.modify_attribute(Json_file_handler, file_name, 'siteName', site_name)
    Json_file_handler.modify_attribute(Json_file_handler, file_name, 'type', cloud_type)
    Json_file_handler.update_any_json_attr(Json_file_handler, file_name, [], 'credentials', data)
    Json_file_handler.update_any_json_attr(Json_file_handler, file_name, ['endPoints', 0], 'ipAddress', ip)
    Json_file_handler.update_any_json_attr(Json_file_handler, file_name, ['endPoints', 1], 'ipAddress', ip)
    Json_file_handler.update_any_json_attr(Json_file_handler, file_name, ['endPoints', 2], 'ipAddress', ip)
    Json_file_handler.update_any_json_attr(Json_file_handler, file_name, ['endPoints', 3], 'ipAddress', ip)
    Json_file_handler.update_any_json_attr(Json_file_handler, file_name, ['endPoints', 4], 'ipAddress', ip)
    Json_file_handler.update_any_json_attr(Json_file_handler, file_name, ['endPoints', 5], 'ipAddress', ip)


def update_vimzone_file(file, end_points_data):
    file_name = r'com_ericsson_do_auto_integration_files/' + file
    EPIS_data = ECM_PI_Initialization.get_model_objects(ECM_PI_Initialization, 'EPIS')
    cloud_type = EPIS_data._EPIS__cloudManagerType
    vim_zone_name = EPIS_data._EPIS__vimzone_name
    site_name = EPIS_data._EPIS__site_name
    static_project_name = EPIS_data._EPIS__static_project
    static_project_username = EPIS_data._EPIS__static_project_username
    static_project_password = EPIS_data._EPIS__static_project_password

    data = {
        "name": static_project_name,
        "adminUserName": static_project_username,
        "adminPassword": static_project_password
    }

    Json_file_handler.modify_attribute(Json_file_handler, file_name, 'name', vim_zone_name)
    Json_file_handler.modify_attribute(Json_file_handler, file_name, 'siteName', site_name)
    Json_file_handler.modify_attribute(Json_file_handler, file_name, 'type', cloud_type)
    Json_file_handler.update_any_json_attr(Json_file_handler, file_name, [], 'credentials', data)
    Json_file_handler.update_any_json_attr(Json_file_handler, file_name, [], 'endPoints', end_points_data)
    if cloud_type == 'CEE':
        Json_file_handler.modify_attribute(Json_file_handler, file_name, 'keystoneDefaultDomain', cloud_type)
    else:
        Json_file_handler.modify_attribute(Json_file_handler, file_name, 'keystoneDefaultDomain', 'Default')


def update_create_project_file(default_user_role):
    try:
        file_name = r'com_ericsson_do_auto_integration_files/createProject.json'
        log.info('start updating file %s', file_name)
        cloud_type = EPIS.get_cloud_manager_type(EPIS)
        project_name = EPIS.get_project_name(EPIS)
        tenant = EPIS.get_tenant_name(EPIS)
        admin_user_name = project_name + '_admin'
        admin_password = project_name.capitalize() + '.laf'
        user_name = project_name + '_user'
        user_password = project_name.capitalize() + '.laf'

        admin_data = {
            "adminUserName": admin_user_name,
            "adminPassword": admin_password,
            "grantedRoles": [{
                "roleName": "admin"
            }]
        }
        user_data = {
            "userName": user_name,
            "userPassword": user_password,
            "grantedRoles": [{
                "roleName": default_user_role
            }]
        }

        data = {'name': project_name, 'adminUserCredentials': admin_data, 'userCredentials': user_data}
        Json_file_handler.modify_list_of_attributes(Json_file_handler, file_name, data)
        Json_file_handler.update_any_json_attr(Json_file_handler, file_name, ['tenants', 0], 'tenantName', tenant)

        if cloud_type == 'CEE':
            Json_file_handler.modify_attribute(Json_file_handler, file_name, "domainName", cloud_type)
        else:
            Json_file_handler.modify_attribute(Json_file_handler, file_name, "domainName", "Default")
        log.info('Updating of file %s completed', file_name)

    except Exception as error:
        log.error("Failed to update file %s: %s", file_name, str(error))
        assert False


def get_network_details(cloud_type, ecm_environment):
    if 'ORCH_Staging_C7a_dynamic' == ecm_environment:

        network_name = 'P9_' + cloud_type + '01_' + ecm_environment + '_PROV'
        ipv4_network_name = 'P9_' + ecm_environment + '_IPv4'
        ipv6_network_name = 'P9_' + ecm_environment + '_IPv6'

    elif 'EO_Maintrack_C11AF01' == ecm_environment:

        network_name = 'P0_' + cloud_type + '01_' + ecm_environment + '_PROV'
        ipv4_network_name = 'P0_' + ecm_environment + '_IPv4'
        ipv6_network_name = 'P0_' + ecm_environment + '_IPv6'

    else:

        network_name = 'P3_' + cloud_type + '01_' + ecm_environment + '_PROV'
        ipv4_network_name = 'P3_' + ecm_environment + '_IPv4'
        ipv6_network_name = 'P3_' + ecm_environment + '_IPv6'

    return network_name, ipv4_network_name, ipv6_network_name


def update_external_network_creation_file(file_name):
    log.info('Start to update providernetwork.json file ')
    Report_file.add_line('Start to update providernetwork.json file')
    EPIS_data = ECM_PI_Initialization.get_model_objects(ECM_PI_Initialization, 'EPIS')
    ecm_host_data = ECM_PI_Initialization.get_model_objects(ECM_PI_Initialization, 'ECMPI')

    try:
        ecm_environment = ecm_host_data._Ecm_PI__ECM_Host_Name
        cloud_type = EPIS_data._EPIS__cloudManagerType
        tenant_name = EPIS_data._EPIS__tenant_name
        vimzone_name = EPIS_data._EPIS__vimzone_name
        ipv4_range = EPIS_data._EPIS__network_ipv4_range
        ip = ipv4_range[:-3]

        gatway_ipv4 = str(ipaddress.ip_address(ip) + 1)
        EPIS_data._EPIS__network_gatway_ip = gatway_ipv4
        ipv6_range = EPIS_data._EPIS__network_ipv6_range
        ip = ipv6_range[:-3]
        gatway_ipv6 = ip + '1'
        segmentation_id = EPIS_data._EPIS__segmentation_id

        network_details = get_network_details(cloud_type, ecm_environment)

        network_name = network_details[0]
        ipv4_network_name = network_details[1]
        ipv6_network_name = network_details[2]

        allocation_pools_ip = ecm_host_data._Ecm_PI__allocation_pools_ip

        # ip_list = allocation_pools_ip.split(',')
        pool_1_ips = allocation_pools_ip.split('-')
        # pool_2_ips = ip_list[1].split('-')

        ipV4_subnet = {
            "name": ipv4_network_name,
            "ipVersion": "IPv4",
            "ipAddressRange": ipv4_range,
            "allocationPools": [
                {
                    "start": pool_1_ips[0],
                    "end": pool_1_ips[1]
                }

            ],
            "dhcpEnabled": True,
            "gatewayIpAddress": gatway_ipv4
        }

        ipV6_subnet = {
            "name": ipv6_network_name,
            "ipVersion": "IPv6",
            "ipAddressRange": ipv6_range,
            "dhcpEnabled": False,
            "gatewayIpAddress": gatway_ipv6
        }

        if cloud_type == 'OPENSTACK':

            log.info(
                'Cloud Type is ' + cloud_type + 'updating External Network file with attribute physicalNetworkName')
            Json_file_handler.update_any_json_attr(Json_file_handler,
                                                   r'com_ericsson_do_auto_integration_files/' + file_name,
                                                   ['vn', 'segments', 0], 'physicalNetworkName', 'datacentre')

        else:
            data = {
                "name": "exampleSegment1",
                "networkType": "VXLAN",
                "isPrimary": True
            }
            log.info(
                'Cloud Type is ' + cloud_type + 'updating External Network file with attribute physicalNetworkName')
            Json_file_handler.update_any_json_attr(Json_file_handler,
                                                   r'com_ericsson_do_auto_integration_files/' + file_name,
                                                   ['vn', 'segments'], 0, data)

        Json_file_handler.modify_attribute(Json_file_handler, r'com_ericsson_do_auto_integration_files/' + file_name,

                                           'tenantName', tenant_name)
        Json_file_handler.modify_first_level_attr(Json_file_handler,
                                                  r'com_ericsson_do_auto_integration_files/' + file_name,
                                                  'vn',
                                                  'name', network_name)
        Json_file_handler.modify_third_level_attr(Json_file_handler,
                                                  r'com_ericsson_do_auto_integration_files/' + file_name,
                                                  'vn', 'segments', 0, 'segmentationId', segmentation_id)
        Json_file_handler.modify_first_level_attr(Json_file_handler,
                                                  r'com_ericsson_do_auto_integration_files/' + file_name,
                                                  'vn',
                                                  'vimZoneName', vimzone_name)
        Json_file_handler.update_any_json_attr(Json_file_handler,
                                               r'com_ericsson_do_auto_integration_files/' + file_name,
                                               ['vn', 'segments', 0], 'segmentationId', segmentation_id)

        Json_file_handler.update_any_json_attr(Json_file_handler,
                                               r'com_ericsson_do_auto_integration_files/' + file_name,
                                               ['vn', 'subnets'], 0, ipV4_subnet)
        Json_file_handler.update_any_json_attr(Json_file_handler,
                                               r'com_ericsson_do_auto_integration_files/' + file_name,
                                               ['vn', 'subnets'], 1, ipV6_subnet)

        log.info('Finished to update providernetwork.json file ')
        Report_file.add_line('Finished to update providernetwork.json file')

    except Exception as e:

        log.error('Error while updating providernetwork.json file ' + str(e))
        Report_file.add_line('Error while updating providernetwork.json file ,check logs for more details')


def update_internal_network_creation_file(file_name):
    """ update file internalnetwork.json """
    try:
        log.info('Start to update %s file', file_name)
        ecm_environment = Ecm_PI.get_ecm_host_name(Ecm_PI)
        tenant_name = EPIS.get_tenant_name(EPIS)
        vimzone_name = EPIS.get_vimzone_name(EPIS)
        vdc_id = EPIS.get_vdc_id(EPIS)
        cloud_type = EPIS.get_cloud_manager_type(EPIS)
        vim_url = EPIS.get_vim_url(EPIS)
        network_name = 'Dualstack_Internal_Network_' + ecm_environment

        if cloud_type == 'OPENSTACK':
            if any(env in vim_url for env in
                   ['cloud4a', 'cloud7a', 'cloud11a', 'cloud12a', 'cloud13a', 'cloud14a', 'cloud7b']):
                log.info('Cloud Type is %s updating Internal Network file', cloud_type)
                data = {
                    "name": "exampleSegment_cloud13a",
                    "networkType": "VXLAN",
                    "isPrimary": True
                }

                Json_file_handler.update_any_json_attr(Json_file_handler,
                                                       r'com_ericsson_do_auto_integration_files/' + file_name,
                                                       ['vn', 'segments'], 0, data)
            else:
                log.info('Cloud Type is %s updating Internal Network file with attribute physicalNetworkName',
                         cloud_type)
                Json_file_handler.update_any_json_attr(Json_file_handler,
                                                       r'com_ericsson_do_auto_integration_files/' + file_name,
                                                       ['vn', 'segments', 0], 'physicalNetworkName',
                                                       'datacentre')
        else:
            data = {
                "name": "exampleSegment1",
                "networkType": "VXLAN",
                "isPrimary": True
            }
            log.info('Cloud Type is %s updating Internal Network file with attribute physicalNetworkName',
                     cloud_type)
            Json_file_handler.update_any_json_attr(Json_file_handler, r'com_ericsson_do_auto_integration_files/'
                                                   + file_name, ['vn', 'segments'], 0, data)

        Json_file_handler.modify_first_level_attr(Json_file_handler,
                                                  r'com_ericsson_do_auto_integration_files/' + file_name,
                                                  'vn', 'name', network_name)
        Json_file_handler.modify_attribute(Json_file_handler,
                                           r'com_ericsson_do_auto_integration_files/' + file_name,
                                           'tenantName', tenant_name)
        Json_file_handler.modify_first_level_attr(Json_file_handler,
                                                  r'com_ericsson_do_auto_integration_files/' + file_name,
                                                  'vn', 'vimZoneName', vimzone_name)
        Json_file_handler.modify_nested_dict(Json_file_handler,
                                             r'com_ericsson_do_auto_integration_files/' + file_name,
                                             "vn", "vdc", "id", vdc_id)
        log.info('Finished to update %s file', file_name)

    except Exception as error:
        log.error('Error while updating %s file: %s', file_name, str(error))


def update_test_hotel_network_creation(file_name):
    try:
        log.info('Start to update test_hotel_network.json file ')
        tenant_name = EPIS.get_tenant_name(EPIS)
        network_name = EPIS.get_external_network_name(EPIS)
        vim_object_id = EPIS.get_external_network_vim_id(EPIS)
        vimzone_name = EPIS.get_vimzone_name(EPIS)

        Json_file_handler.update_any_json_attr(Json_file_handler,
                                               r'com_ericsson_do_auto_integration_files/test_hotel/' + file_name,
                                               [], 'tenantName', tenant_name)

        Json_file_handler.update_any_json_attr(Json_file_handler,
                                               r'com_ericsson_do_auto_integration_files/test_hotel/' + file_name,
                                               [], 'name', network_name)

        Json_file_handler.update_any_json_attr(Json_file_handler,
                                               r'com_ericsson_do_auto_integration_files/test_hotel/' + file_name,
                                               [], 'vimObjectId', vim_object_id)

        Json_file_handler.update_any_json_attr(Json_file_handler,
                                               r'com_ericsson_do_auto_integration_files/test_hotel/' + file_name,
                                               [], 'vimZoneName', vimzone_name)

        log.info('Finished to update test_hotel_network.json file ')

    except Exception as e:

        log.error('Error while updating test_hotel_network.json file %s', str(e))


def update_test_hotel_subnet(file_name, network_id):
    try:
        log.info('Start to update test_hotel_subnet.json file ')
        network_name = EPIS.get_external_network_name(EPIS) + '_ipv4'
        subnet_vim_object_id = EPIS.get_network_subnet_vim_id(EPIS)
        ip_address_range = SIT.get_external_subnet_cidr(SIT)
        gateway_ip_address = SIT.get_external_subnet_gateway(SIT)
        vdc_id = SIT.get_vdc_id(SIT)

        Json_file_handler.update_any_json_attr(Json_file_handler,
                                               r'com_ericsson_do_auto_integration_files/test_hotel/' + file_name,
                                               [], 'vimObjectId', subnet_vim_object_id)

        Json_file_handler.update_any_json_attr(Json_file_handler,
                                               r'com_ericsson_do_auto_integration_files/test_hotel/' + file_name,
                                               [], 'name', network_name)

        Json_file_handler.update_any_json_attr(Json_file_handler,
                                               r'com_ericsson_do_auto_integration_files/test_hotel/' + file_name,
                                               [], 'ipAddressRange', ip_address_range)

        Json_file_handler.update_any_json_attr(Json_file_handler,
                                               r'com_ericsson_do_auto_integration_files/test_hotel/' + file_name,
                                               [], 'gatewayIpAddress', gateway_ip_address)

        Json_file_handler.update_any_json_attr(Json_file_handler,
                                               r'com_ericsson_do_auto_integration_files/test_hotel/' + file_name,
                                               ['vdc'], 'id', vdc_id)

        Json_file_handler.update_any_json_attr(Json_file_handler,
                                               r'com_ericsson_do_auto_integration_files/test_hotel/' + file_name,
                                               ['vn'], 'id', network_id)

        log.info('Finished to update test_hotel_subnet.json file ')

    except Exception as e:

        log.error('Error while updating test_hotel_subnet.json file %s', str(e))
