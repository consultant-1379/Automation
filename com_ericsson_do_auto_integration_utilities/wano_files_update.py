from com_ericsson_do_auto_integration_utilities.Logger import Logger
from com_ericsson_do_auto_integration_utilities.Report_file import Report_file
from com_ericsson_do_auto_integration_utilities.Json_file_handler import Json_file_handler

log = Logger.get_logger('wano_files_update.py')

def update_wano_service_file(file_name,service_name):
    try:
        log.info('Start to update {} file '.format(file_name))
        Report_file.add_line('Start to update {} file '.format(file_name))

        data  = '{\"ipvpnService\":{\"serviceName\":\"SERVICE_NAME\",\"serviceDefinition\":\"Full Mesh IPVPN\",\"sites\":{\"site\":[{\"siteNetworkAccesses\":{\"siteNetworkAccess\":[{\"providerEdge\":{\"bearer\":{\"vlanBased\":{\"vlan\":{\"vlanId\":63}}},\"routerName\":\"vmx-PE3\",\"interfaceName\":\"vmx-PE3:ge-0/0/8\"},\"ipConnection\":{\"ipv4\":{\"providerAddress\":\"26.53.1.1\",\"mask\":30}},\"routingConfigurations\":{\"ospf\":{\"addressFamily\":\"ipv4\",\"areaId\":\"0.0.0.10\",\"routingProcessId\":\"2\"}},\"serviceAttachment\":{\"role\":\"any-to-any\"}}]}},{\"siteNetworkAccesses\":{\"siteNetworkAccess\":[{\"providerEdge\":{\"bearer\":{\"vlanBased\":{\"vlan\":{\"vlanId\":64}}},\"routerName\":\"vmx-PE4\",\"interfaceName\":\"vmx-PE4:ge-0/0/8\"},\"ipConnection\":{\"ipv4\":{\"providerAddress\":\"26.54.1.1\",\"mask\":30}},\"routingConfigurations\":{\"ospf\":{\"addressFamily\":\"ipv4\",\"areaId\":\"0.0.0.10\",\"routingProcessId\":\"2\"}},\"serviceAttachment\":{\"role\":\"any-to-any\"}}]}}]}}}'
        request_data = data.replace("SERVICE_NAME",service_name)

        Json_file_handler.update_any_json_attr(Json_file_handler,r'com_ericsson_do_auto_integration_files/wano_files/' + file_name, [],'name',service_name)
        Json_file_handler.update_any_json_attr(Json_file_handler,
                                               r'com_ericsson_do_auto_integration_files/wano_files/' + file_name, [],
                                               'requestData', request_data)


    except Exception as e:

        log.error('Error to update {} file with error {}'.format(file_name, str(e)))
        Report_file.add_line('Error to update {} file with error {}'.format(file_name, str(e)))