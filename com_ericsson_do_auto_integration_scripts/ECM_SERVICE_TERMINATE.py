import re
from com_ericsson_do_auto_integration_initilization.Initialization_script import Initialization_script
from com_ericsson_do_auto_integration_model.Ecm_core import Ecm_core
from com_ericsson_do_auto_integration_model.SIT import SIT
from com_ericsson_do_auto_integration_utilities.Common_utilities import Common_utilities
from com_ericsson_do_auto_integration_utilities.Logger import Logger
from com_ericsson_do_auto_integration_utilities.Report_file import Report_file
from com_ericsson_do_auto_integration_utilities.ServerConnection import ServerConnection
from com_ericsson_do_auto_integration_utilities.Server_details import Server_details
from com_ericsson_do_auto_integration_utilities.ExecuteCurlCommand import ExecuteCurlCommand
from com_ericsson_do_auto_integration_scripts.ECM_NODE_DELETION import get_vapp_list_from_eocm

log = Logger.get_logger('ECM_SERVICE_TERMINATE.py')


def get_ns_instance_id(connection, token, core_vm_hostname):
    try:
        log.info("Start to fecth Network Service Id")
        Report_file.add_line('Start to Fetch Network Service Id ')
        count = 0
        vapp_list = get_vapp_list_from_eocm(connection, token, core_vm_hostname, "ALL")
        for vapp_dict in vapp_list:
            if 'networkServices' in vapp_dict:
                networkservcies = vapp_dict['networkServices']
                for line in networkservcies:
                    name = line['name']
                    if name == 'nsd-cnf':
                        id = line['id']
                        log.info('Fetching ns_instance_id from vapp_list %s  %s', name, id)
                        count = count + 1
                        return id

        if count == 0:
            log.info("There is no networkservices in the vapp list")
            Report_file.add_line("There is no networkservices in the vapp list")
            return "NO_NETSERV"


    except Exception as e:

        log.error('Error Fetching Network Service Id %s', str(e))
        assert False


def terminate_ns_instantiate():
    log.info("Start terminating of ecm network services")
    instance_id_dict = fetch_ns_instance_ids()
    if instance_id_dict:
        vnf_type = SIT.get_vnf_type(SIT)
        if vnf_type.lower() == 'all':
            for ns_name, ns_id in instance_id_dict.items():
                terminate_ns(ns_id, vnf_type)
        else:
            for ns_name, ns_id in instance_id_dict.items():
                if ns_name.startswith(vnf_type.lower()):
                    terminate_ns(ns_id, vnf_type)
            else:
                log.info("No network services present in EOCM for vnf type %s", vnf_type)
    else:
        log.info("No network services present in EOCM")
    log.info("Terminating of ecm network services completed")


def fetch_ns_instance_ids():
    try:
        log.info('Start to collect network service instances from EOCM')
        ecm_server_ip, ecm_username, ecm_password = Server_details.ecm_host_blade_details(Server_details)
        connection = ServerConnection.get_connection(ecm_server_ip, ecm_username, ecm_password)
        core_vm_hostname = Ecm_core.get_core_vm_hostname(Ecm_core)
        token = Common_utilities.authToken(Common_utilities, connection, core_vm_hostname)
        command = f"curl -X GET --insecure --header 'Content-Type: application/json' --header 'Accept: "\
                  f"application/json' --header 'AuthToken:{token}' 'https://{core_vm_hostname}/ecm_service/" \
                  f"SOL005/nslcm/v1/ns_instances?$filter=tenantName%253D%27ECM%27&$data=%7B%22ericssonNfvoData%" \
                  f"22%253Atrue%7D&exclude_default'"
        output = Common_utilities.execute_curl_command(Common_utilities, connection, command)
        instance_dict = {}
        if output:
            for item in output:
                instance_dict[item["nsInstanceName"]] = item["id"]
        log.info("Collected ns instances data from EOCM %s", instance_dict)
        return instance_dict
    except Exception as error:
        log.error("Failed to fetch service instances id from EOCM, %s", str(error))
        assert False
    finally:
        connection.close()


def delete_instantiate_ns(connection, ns_instances_id):
    try:
        log.info('Terminating of NS Instantiate has been failed, Hence deleting the NS ')

        core_vm_ip = Server_details.ecm_host_blade_corevmip(Server_details)
        token = Common_utilities.authToken(Common_utilities, connection, core_vm_ip)
        ecm_host_data = Initialization_script.get_model_objects(Initialization_script, 'ECM_CORE')
        core_vm_hostname = ecm_host_data._Ecm_core__core_vm_hostname
        command = '''curl --insecure "https://{}/ecm_service/SOL005/nslcm/v1/ns_instances/{}"  -X "DELETE"   -H "AuthToken: {}"'''.format(
            core_vm_hostname, ns_instances_id, token)

        command_output = ExecuteCurlCommand.get_json_output(connection, command)

        if '204 No Content' in command_output:
            log.info('NS Instantiate Deleted Successfully')
        else:
            log.error('NS Instantiate Deletion failed ')
            assert False

    except Exception as error:
        log.error('Error while deleting NS Instantiate  %s', str(error))
        Report_file.add_line('Error while deleting NS Instantiate' + str(error))
        assert False


def terminate_ns(ns_instances_id, vnf_type):
    connection = None
    try:
        log.info('Start to terminate Instantiate NS, vnf_type %s', vnf_type)
        ecm_server_ip, ecm_username, ecm_password = Server_details.ecm_host_blade_details(Server_details)
        connection = ServerConnection.get_connection(ecm_server_ip, ecm_username, ecm_password)
        ecm_host_data = Initialization_script.get_model_objects(Initialization_script, 'ECM_CORE')
        core_vm_hostname = ecm_host_data._Ecm_core__core_vm_hostname
        token = Common_utilities.authToken(Common_utilities, connection, core_vm_hostname)

        file_name = "terminate_NS.json"
        ServerConnection.put_file_sftp(connection, r'com_ericsson_do_auto_integration_files/' + file_name,
                                       SIT.get_base_folder(SIT) + file_name)

        command = '''curl --insecure -i -X POST "https://{}/ecm_service/SOL005/nslcm/v1/ns_instances/{}/terminate" -H "AuthToken: {}" -H "Content-Type: application/json"  --data @{}'''.format(
            core_vm_hostname, ns_instances_id, token, file_name)

        output = ExecuteCurlCommand.get_json_output(connection, command)

        if '202 Accepted' in output:
            order_id = re.findall('NS.*', output)[0].split('\\r\\n')[0].strip()
            log.info('terminate NS Order Id - %s', order_id)

            token = Common_utilities.authToken(Common_utilities, connection, core_vm_hostname)

            order_status, order_output = Common_utilities.NSorderReqStatus(Common_utilities, connection, token,
                                                                           core_vm_hostname, order_id, 10)
            if order_status:
                log.info("Successfully Terminated Instantiation of NS")
            else:
                log.info("Failed to terminate NS. Hence deleting the NS")
                delete_instantiate_ns(connection, ns_instances_id)

        else:
            log.error('Error While deleting Instantiation of NS')
            assert False

    except Exception as e:
        log.error('Error while terminate Instantiate NS %s', str(e))
        assert False

    finally:
        if connection:
            connection.close()
            