'''
Created on 10 feb 2018

@author: eshetra

'''

from com_ericsson_do_auto_integration_utilities.Logger import Logger
from com_ericsson_do_auto_integration_utilities.Report_file import Report_file
from com_ericsson_do_auto_integration_initilization.ECM_PI_initialization import ECM_PI_Initialization
from com_ericsson_do_auto_integration_utilities.ServerConnection import ServerConnection
from com_ericsson_do_auto_integration_utilities.EPIS_files_update import *
from com_ericsson_do_auto_integration_utilities.Shell_handler import ShellHandler
import ast
from com_ericsson_do_auto_integration_scripts.EPG_ECM_DEPLOYMENT import *
from com_ericsson_do_auto_integration_initilization.Initialization_script import Initialization_script
from com_ericsson_do_auto_integration_scripts.ECM_POST_INSTALLATION import *
from com_ericsson_do_auto_integration_scripts.CEE_Cleanup import *
from com_ericsson_do_auto_integration_utilities.Json_file_handler import Json_file_handler
from com_ericsson_do_auto_integration_utilities.SIT_files_update import *
from com_ericsson_do_auto_integration_initilization.SIT_initialization import SIT_initialization
from com_ericsson_do_auto_integration_scripts.VERIFY_NODE_DEPLOYMENT import *
from com_ericsson_do_auto_integration_utilities.ExecuteCurlCommand import *
import time
from com_ericsson_do_auto_integration_utilities.Common_utilities import *

log = Logger.get_logger('VCISCO_DEPLOY')

ovf_id = ''
ovf_package_name = ''
security_group_id = ''


def disable_port():
    try:
        EPIS_data = ECM_PI_Initialization.get_model_objects(ECM_PI_Initialization, 'EPIS')
        cloud_type = EPIS_data._EPIS__cloudManagerType

        if cloud_type == 'OPENSTACK':
            EPIS_data = ECM_PI_Initialization.get_model_objects(ECM_PI_Initialization, 'EPIS')
            openstack_ip = EPIS_data._EPIS__openstack_ip
            username = EPIS_data._EPIS__openstack_username
            password = EPIS_data._EPIS__openstack_password
            openrc_filename = EPIS_data._EPIS__openrc_filename

            ecm_host_data = ECM_PI_Initialization.get_model_objects(ECM_PI_Initialization, 'ECMPI')
            ecm_server_ip = ecm_host_data._Ecm_PI__ECM_Host_Blade_IP
            ecm_username = ecm_host_data._Ecm_PI__ECM_Host_Blade_username
            ecm_password = ecm_host_data._Ecm_PI__ECM_Host_Blade_Password
            connection = ServerConnection.get_connection(ecm_server_ip, ecm_username, ecm_password)

            file_name = 'ASR_VM_DEPLOY_RHOS.json'
            package_dir = '/var/tmp/deployvcisco'
            ServerConnection.get_file_sftp(connection, package_dir + '/' + file_name,
                                            r'com_ericsson_do_auto_integration_files/' + file_name)

            file_data = Json_file_handler.get_json_data(Json_file_handler,
                                                        r'com_ericsson_do_auto_integration_files/ASR_VM_DEPLOY_RHOS.json')
            port_name1 = file_data['orderItems'][4]['createVmVnic']['name']
            port_name2 = file_data['orderItems'][5]['createVmVnic']['name']

            ShellHandler.__init__(ShellHandler, openstack_ip, username, password)
            command = 'source {}'.format(openrc_filename)
            stdin, stdout, stderr = ShellHandler.execute(ShellHandler, command)
            command = '''openstack port list | grep -i '{}{}'''.format(port_name1, "'")
            stdin, stdout, stderr = ShellHandler.execute(ShellHandler, command)
            if not stdout:

                log.info('nothing returned from the port list command ' + command)
                Report_file.add_line('nothing returned from the port list command ' + command)

            else:
                log.info('Port exists in port list command ' + command)
                Report_file.add_line('Port exists in port list command ' + command)

            for line in stdout:
                network_data = line.split('|')
                port_number1 = network_data[1].strip()
                command = '''neutron port-update {} --no-security-groups --no-allowed-address-pairs --port_security_enabled=false'''.format(
                    port_number1)
                log.info('Updating the port using the command: ' + command)
                Report_file.add_line('Updating the port using the command: ' + command)
                stdin, stdout, stderr = ShellHandler.execute(ShellHandler, command)
                time.sleep(4)
                Report_file.add_line('command output ' + str(stdout))
                if 'Updated port' in str(stdout):
                    log.info('Port updated succesfully for: ' + port_number1)
                    Report_file.add_line('Port updated succesfully for: ' + port_number1)
                else:
                    log.info('Port update failed for: ' + port_number1)
                    Report_file.add_line('Port updated failed for: ' + port_number1)

            command = 'source {}'.format(openrc_filename)
            stdin, stdout, stderr = ShellHandler.execute(ShellHandler, command)
            command = '''openstack port list | grep -i '{}{}'''.format(port_name2, "'")
            stdin, stdout, stderr = ShellHandler.execute(ShellHandler, command)
            if not stdout:

                log.info('nothing returned from the port list command ' + command)
                Report_file.add_line('nothing returned from the port list command ' + command)

            else:
                log.info('Port exists in port list command ' + command)
                Report_file.add_line('Port exists in port list command ' + command)

            for line in stdout:
                network_data = line.split('|')
                port_number2 = network_data[1].strip()
                command = '''neutron port-update {} --no-security-groups --no-allowed-address-pairs --port_security_enabled=false'''.format(
                    port_number2)
                log.info('Updating the port using the command: ' + command)
                Report_file.add_line('Updating the port using the command: ' + command)
                stdin, stdout, stderr = ShellHandler.execute(ShellHandler, command)
                time.sleep(4)
                Report_file.add_line('command output ' + str(stdout))
                if 'Updated port' in str(stdout):
                    log.info('Port updated succesfully for: ' + port_number2)
                    Report_file.add_line('Port updated succesfully for: ' + port_number2)
                else:
                    log.info('Port update failed for: ' + port_number2)
                    Report_file.add_line('Port updated failed for: ' + port_number2)

            ShellHandler.__del__(ShellHandler)
        else:
            log.info('Port Update not required for cloud type : ' + cloud_type)
            Report_file.add_line('Port update not required for cloud type : ' + cloud_type)

    except Exception as e:
        log.error('Exception while updating the  port. ERROR: ' + str(e))
        ShellHandler.__del__(ShellHandler)
        assert False


def check_if_securityGroup_exist(connection, core_vm_hostname, token):
    log.info('Start to check if vCisco SecurityGroup Already Exist.')
    Report_file.add_line('Start to check if vCisco SecurityGroup Already Exist.')

    command = '''curl --insecure "https://{}/ecm_service/v2/securitygroups" -H "Accept: application/json" -H "AuthToken: {}"'''.format(
        core_vm_hostname, token)

    command_output = ExecuteCurlCommand.get_json_output(connection, command)
    command_out = ExecuteCurlCommand.get_sliced_command_output(command_output)
    output = ast.literal_eval(command_out)
    requestStatus = output['status']['reqStatus']

    if 'SUCCESS' in requestStatus:
        if 'securityGroups' in str(output):
            data = output['data']['securityGroups']
            for sec_group in data:
                name = sec_group['name']
                if 'vCisco_Security_Group' == name:
                    log.info('Already created security group for vCisco. name = ' + name)
                    Report_file.add_line('Already created security group for vCisco. name = ' + name)
                    security_group_id = sec_group['id']
                    log.info('Security Group ID - ' + security_group_id)
                    Report_file.add_line('Security Group ID - ' + security_group_id)
                    return "AlreadyExist", security_group_id

            log.info("Security Group does not exist")
            Report_file.add_line("Security Group does not exist")
            return "DoesNotExist", 1

        else:
            log.info("Security Group does not exist")
            Report_file.add_line("Security Group does not exist")
            return "DoesNotExist", 1

    else:
        log.info("Failed to list the created securityGroups.")
        Report_file.add_line('Failed to list the created securityGroups')
        assert False


def create_security_groups():
    try:
        log.info('Start security groups creation')
        Report_file.add_line(' Security group creation begins...')
        EPIS_data = ECM_PI_Initialization.get_model_objects(ECM_PI_Initialization, 'EPIS')
        cloud_type = EPIS_data._EPIS__cloudManagerType
        global security_group_id
        if cloud_type == 'OPENSTACK':
            ecm_host_data = ECM_PI_Initialization.get_model_objects(ECM_PI_Initialization, 'ECMPI')
            ecm_server_ip = ecm_host_data._Ecm_PI__ECM_Host_Blade_IP
            ecm_username = ecm_host_data._Ecm_PI__ECM_Host_Blade_username
            ecm_password = ecm_host_data._Ecm_PI__ECM_Host_Blade_Password
            core_vm_ip = ecm_host_data._Ecm_PI__CORE_VM_IP
            core_vm_hostname = ecm_host_data._Ecm_PI__core_vm_hostname
            sit_data = SIT_initialization.get_model_objects(SIT_initialization, 'SIT')

            connection = ServerConnection.get_connection(ecm_server_ip, ecm_username, ecm_password)
            log.info('Generating token in the host blade server using the  curl command  ')
            token = Common_utilities.authToken(Common_utilities, connection, core_vm_hostname)
            value, securitygroup_id = check_if_securityGroup_exist(connection, core_vm_hostname, token)
            if value == "AlreadyExist":
                security_group_id = securitygroup_id
                return True
            file_name = 'createSecuritygroup_RHOS.json'
            package_dir = '/var/tmp/deployvcisco'
            ServerConnection.get_file_sftp(connection, package_dir + '/' + file_name,
                                            r'com_ericsson_do_auto_integration_files/' + file_name)

            sftp = connection.open_sftp()
            sftp.put(r'com_ericsson_do_auto_integration_files/' + file_name, SIT.get_base_folder(SIT) + file_name)
            sftp.close()
            curl = '''curl --insecure https://{}/ecm_service/securitygroups -H 'Accept: application/json' -H 'Content-Type: application/json' -H 'AuthToken: {}' --data @{}'''.format(
                core_vm_hostname, token, file_name)
            command = curl
            Report_file.add_mesg('Step', 'Executing the curl command to create security groups', command)
            command_output = ExecuteCurlCommand.get_json_output(connection, command)
            output = ast.literal_eval(command_output[2:-1:1])
            requestStatus = output['status']['reqStatus']

            if 'SUCCESS' in requestStatus:
                log.info('Curl command to create security group is successful')
                Report_file.add_line('Curl command to create security group is successful: ' + command_output)

                security_group_id = output['data']['securityGroup']['id']
                log.info('Start transferring security group ')
                token = Common_utilities.authToken(Common_utilities, connection, core_vm_hostname)

                file_name = 'transferSecurityGroup_RHOS.json'
                ServerConnection.get_file_sftp(connection, package_dir + '/' + file_name,
                                                r'com_ericsson_do_auto_integration_files/' + file_name)

                update_transfer_securitygroup(file_name)
                sftp = connection.open_sftp()
                sftp.put(r'com_ericsson_do_auto_integration_files/' + file_name, SIT.get_base_folder(SIT) + file_name)
                sftp.close()
                curl = '''curl --insecure https://{}/ecm_service/securitygroups/{}/transfer -H 'Accept: application/json' -H 'Content-Type: application/json' -H 'AuthToken: {}' --data @{}'''.format(
                    core_vm_hostname, security_group_id, token, file_name)
                command = curl
                Report_file.add_mesg('Step', 'Executing the curl command to transfer security groups',
                                     command)
                command_output = ExecuteCurlCommand.get_json_output(connection, command)
                output = ast.literal_eval(command_output[2:-1:1])
                requestStatus = output['status']['reqStatus']

                if 'SUCCESS' in requestStatus:
                    log.info('Curl command to transfer security group is successful')
                    Report_file.add_line('Curl command to transfer security group is successful: ' + command_output)
                    order_id = output['data']['order']['id']
                    log.info('Order id to transfer the security group  ' + order_id)
                    Report_file.add_line('Order id to transfer the security group ' + order_id)
                    log.info(command_output)

                    order_status, order_output = Common_utilities.orderReqStatus(Common_utilities, connection, token,
                                                                                 core_vm_hostname, order_id, 10)

                    if order_status:
                        log.info('Order Status is completed ' + order_id)
                        Report_file.add_line('Order Status is completed ' + order_id)
                        log.info('Security group transferred successfully :  ' + command_output)
                        Report_file.add_line('Security group transfered successfully' + command_output)
                        log.info('wait 5 seconds to complete the transfer security order for ASR ')
                        time.sleep(5)


                    else:
                        log.info('Order Status is failed with message mentioned above ' + order_id)
                        Report_file.add_line('Order Status is failed with message mentioned above ' + order_id)
                        connection.close()
                        assert False


                elif 'ERROR' in requestStatus:
                    command_error = output['status']['msgs'][0]['msgText']
                    log.error('Error executing curl command for transfer of security group ' + command_error)
                    Report_file.add_line(command_error)
                    Report_file.add_line('Error executing curl command for transfer of security group')
                    connection.close()
                    assert False

            elif 'ERROR' in requestStatus:
                command_error = output['status']['msgs'][0]['msgText']
                log.error('Error executing curl command for creating security groups ' + command_error)
                Report_file.add_line(command_error)
                Report_file.add_line('Error executing curl command while creating security groups')
                connection.close()
                assert False

            connection.close()
            log.info(' Security group creation ends')
            Report_file.add_line('Security group creation ends...')

        else:
            log.info(' Security group creation not required for cloud type : ' + cloud_type)
            Report_file.add_line(' Security group creation not required for cloud type : ' + cloud_type)


    except Exception as e:
        log.error('Error creating security groups ' + str(e))
        Report_file.add_line('Error creating security groups ' + str(e))
        assert False


def create_vcisco_bgw_ports():
    try:
        EPIS_data = ECM_PI_Initialization.get_model_objects(ECM_PI_Initialization, 'EPIS')
        cloud_type = EPIS_data._EPIS__cloudManagerType

        if cloud_type == 'CEE':
            log.info('Start vCisco BGW ports creation')
            Report_file.add_line(' vCisco BGW ports creation begins...')
            EPIS_data = ECM_PI_Initialization.get_model_objects(ECM_PI_Initialization, 'EPIS')
            sit_data = SIT_initialization.get_model_objects(SIT_initialization, 'SIT')

            ecm_host_data = ECM_PI_Initialization.get_model_objects(ECM_PI_Initialization, 'ECMPI')
            openstack_ip = EPIS_data._EPIS__openstack_ip
            username = EPIS_data._EPIS__openstack_username
            password = EPIS_data._EPIS__openstack_password
            vCisco_gatway_ip = sit_data._SIT__vcisco_gateway_ip
            openrc_filename = EPIS_data._EPIS__openrc_filename

            ecm_environment = ecm_host_data._Ecm_PI__ECM_Host_Name

            ShellHandler.__init__(ShellHandler, openstack_ip, username, password)
            command = 'source {}'.format(openrc_filename)
            stdin, stdout, stderr = ShellHandler.execute(ShellHandler, command)
            vcisco_network_name = 'P3-CEE01-' + ecm_environment + '-vMME-OM_CN'

            command = 'openstack port list --network {} | grep -i ACTIVE '.format(vcisco_network_name)
            stdin, stdout, stderr = ShellHandler.execute(ShellHandler, command)

            existing_ips = []
            for line in stdout:
                port_data = line.split('|')
                fixed_ip_address = port_data[4].strip()
                ip_data = fixed_ip_address.split(',')
                ip_address = ip_data[0].strip()
                ip_num = ip_address.split('=')
                ip = ip_num[1].strip()
                existing_ips.append(ip[1:-1:])

            avail_ip_list = []
            i = 1
            while avail_ip_list.__len__() != 2:
                ip_add = str(ipaddress.ip_address(vCisco_gatway_ip) + i)

                if ip_add in existing_ips:
                    log.info('IP {} for bgw port create already exists , searching for new IP address '.format(ip_add))
                else:
                    log.info('IP {} is available for bgw port creation  '.format(ip_add))
                    avail_ip_list.append(ip_add)

                i = i + 1

            for i in range(1, 3):
                port_name = vcisco_network_name + '_bgw_' + str(i)
                subnet_id = vcisco_network_name + '_Sub'

                ip_add = avail_ip_list[i - 1]
                command = 'neutron port-create --name {} --fixed-ip subnet_id={},ip_address={} --device_owner=baremetal:BGW-{} --binding:host_id=BGW-{} {}'.format(
                    port_name, subnet_id, ip_add, i, i, vcisco_network_name)

                stdin, stdout, stderr = ShellHandler.execute(ShellHandler, command)
                log.info('waiting 30 seconds to create BGW Port')
                time.sleep(30)

            log.info(' vCisco BGW ports creation ends')
            Report_file.add_line('vCisco BGW ports creation ends...')
        else:
            log.info(' vCisco BGW ports creation not required for cloud type : ' + cloud_type)
            Report_file.add_line(' vCisco BGW ports creation not required for cloud type : ' + cloud_type)

    except Exception as e:
        log.error('Error vCisco BGW ports creation ' + str(e))
        Report_file.add_line('Error vCisco BGW ports creation ' + str(e))
        assert False


def create_vCisco_flavours():
    try:
        log.info('start creating vCisco flavors')
        Report_file.add_line('start creating vCisco flavors')
        EPIS_data = ECM_PI_Initialization.get_model_objects(ECM_PI_Initialization, 'EPIS')
        openstack_ip = EPIS_data._EPIS__openstack_ip
        username = EPIS_data._EPIS__openstack_username
        password = EPIS_data._EPIS__openstack_password
        openrc_filename = EPIS_data._EPIS__openrc_filename
        sit_data = SIT_initialization.get_model_objects(SIT_initialization, 'SIT')
        tenant_name = EPIS_data._EPIS__tenant_name

        vCisco_flavor = sit_data._SIT__vcisco_flavour_name
        # Valid9m_flavor = sit_data._SIT__valid9m_flavour_name
        # Need to verify this with
        flavors_list = [vCisco_flavor]
        for flavor_name in flavors_list:

            flavor_exists = check_flavor_exists(openrc_filename, openstack_ip, username, password, flavor_name)
            if flavor_exists:
                log.info('Flavor with name ' + flavor_name + ' already exists in CEE')
                Report_file.add_line('Flavor with name ' + flavor_name + ' already exists in CEE')
            else:
                log.info('Flavor with name ' + flavor_name + ' does not  exists in CEE')
                Report_file.add_line('Flavor with name ' + flavor_name + ' does not  exists in CEE')
                name = flavor_name[3:]
                if 'vCisco' in name:
                    update_any_flavor_file(name, 4, 20480, 45, tenant_name)
                    update_transfer_flavour_file()
                else:
                    log.info('This is valid9m flavour')

                create_flavour('flavour.json', 'flavour_transfer.json', name)

        log.info('Finished creating vCisco flavor')
        Report_file.add_line('Finished creating vCisco flavor')

    except Exception as e:
        log.error('Error creating vCisco flavors ' + str(e))
        Report_file.add_line('Error creating vCisco flavors ' + str(e))
        assert False


def create_valid9m_flavours():
    try:
        log.info('start creating valid9m flavors')
        Report_file.add_line('start creating valid9m flavors')
        EPIS_data = ECM_PI_Initialization.get_model_objects(ECM_PI_Initialization, 'EPIS')
        openstack_ip = EPIS_data._EPIS__openstack_ip
        username = EPIS_data._EPIS__openstack_username
        password = EPIS_data._EPIS__openstack_password
        openrc_filename = EPIS_data._EPIS__openrc_filename
        sit_data = SIT_initialization.get_model_objects(SIT_initialization, 'SIT')
        tenant_name = EPIS_data._EPIS__tenant_name

        # vCisco_flavor = sit_data._SIT__vcisco_flavour_name
        Valid9m_flavor = sit_data._SIT__valid9m_flavour_name
        # Need to verify this with
        flavors_list = [Valid9m_flavor]
        for flavor_name in flavors_list:

            flavor_exists = check_flavor_exists(openrc_filename, openstack_ip, username, password, flavor_name)
            if flavor_exists:
                log.info('Flavor with name ' + flavor_name + ' already exists in CEE')
                Report_file.add_line('Flavor with name ' + flavor_name + ' already exists in CEE')
            else:
                log.info('Flavor with name ' + flavor_name + ' does not  exists in CEE')
                Report_file.add_line('Flavor with name ' + flavor_name + ' does not  exists in CEE')
                name = flavor_name[3:]
                if 'valid' in name:
                    update_any_flavor_file(name, 1, 1024, 1, tenant_name)
                    update_transfer_flavour_file()
                else:
                    log.info('This is valid9m flavour')

                create_flavour('valid9m_flavour.json', 'flavour_transfer.json', name)

        log.info('Finished creating valid9m flavor')
        Report_file.add_line('Finished creating valid9m flavor')

    except Exception as e:
        log.error('Error creating valid9m flavors ' + str(e))
        Report_file.add_line('Error creating valid9m flavors ' + str(e))
        assert False


def register_vCisco_images():
    try:
        log.info('start register vCisco images')
        Report_file.add_line('start register vCisco images')
        sit_data = SIT_initialization.get_model_objects(SIT_initialization, 'SIT')
        EPIS_data = ECM_PI_Initialization.get_model_objects(ECM_PI_Initialization, 'EPIS')
        ecm_host_data = Initialization_script.get_model_objects(Initialization_script, 'ECM_CORE')
        ecm_server_ip = ecm_host_data._Ecm_core__ECM_Host_Blade_IP
        ecm_username = ecm_host_data._Ecm_core__ECM_Host_Blade_username
        ecm_password = ecm_host_data._Ecm_core__ECM_Host_Blade_Password
        core_vm_ip = ecm_host_data._Ecm_core__CORE_VM_IP
        core_vm_hostname = ecm_host_data._Ecm_core__core_vm_hostname
        vimzone_name = sit_data._SIT__vimzone_name
        vCisco_image_name = sit_data._SIT__vcisco_image_name
        Valid9m_image_name = sit_data._SIT__valid9m_image_name
        vCisco_image_id = sit_data._SIT__vcisco_image_id
        Valid9m_image_id = sit_data._SIT__valid9m_image_id
        image_names = [vCisco_image_name, Valid9m_image_name]
        image_ids = [vCisco_image_id, Valid9m_image_id]

        for image_name, image_id in zip(image_names, image_ids):
            connection = ServerConnection.get_connection(ecm_server_ip, ecm_username, ecm_password)
            token = Common_utilities.authToken(Common_utilities, connection, core_vm_hostname)

            print('going in for loop')
            image_exists = check_image_registered(connection, image_name, token, core_vm_hostname)
            print(image_exists)
            if image_exists:
                Report_file.add_line('Image with name ' + image_name + ' already registered in cloud manager')
            else:
                log.info('Going to register image with name ' + image_name)
                update_image_file('RegisterImage.json', image_name, vimzone_name, image_id)
                image_registration('RegisterImage.json')

        log.info('Finished register vCisco images')
        Report_file.add_line('Finished register vCisco images')
    except Exception as e:
        log.error('Error register vCisco images ' + str(e))
        Report_file.add_line('Error register vCisco images ' + str(e))
        assert False


def onboard_generic_ovf_package(ovf_package, package_dir):
    try:
        log.info('Start Onboarding of OVF ' + ovf_package)
        Report_file.add_line('Start Onboarding the OVF for ' + ovf_package)
        ecm_host_data = ECM_PI_Initialization.get_model_objects(ECM_PI_Initialization, 'ECMPI')

        ecm_server_ip = ecm_host_data._Ecm_PI__ECM_Host_Blade_IP
        ecm_username = ecm_host_data._Ecm_PI__ECM_Host_Blade_username
        ecm_password = ecm_host_data._Ecm_PI__ECM_Host_Blade_Password
        core_vm_ip = ecm_host_data._Ecm_PI__CORE_VM_IP
        core_vm_hostname = ecm_host_data._Ecm_PI__core_vm_hostname
        sit_data = SIT_initialization.get_model_objects(SIT_initialization, 'SIT')
        connection = ServerConnection.get_connection(ecm_server_ip, ecm_username, ecm_password)
        log.info('Generating token in the host blade server using the  curl command  ')
        token = Common_utilities.authToken(Common_utilities, connection, core_vm_hostname)

        try:
            log.info('Getting the ovf file')
            Report_file.add_line('Getting the ovf file from blade server')
            ServerConnection.get_file_sftp(connection, package_dir + '/' + ovf_package,
                                            r'com_ericsson_do_auto_integration_files/' + ovf_package)
            ServerConnection.put_file_sftp(connection,
                                            r'com_ericsson_do_auto_integration_files/' + ovf_package,
                                            SIT.get_base_folder(SIT) + ovf_package)

        except Exception as e:
            log.error('Error while getting the ASR_Networks.ovf from server ' + str(e))

        file_checksum = Common_utilities.crc(Common_utilities, r'com_ericsson_do_auto_integration_files/' + ovf_package)
        chunk_Size = "$(wc -c < {})".format(ovf_package)
        chunk_Data = "$(base64 {})".format(ovf_package)
        tenant_name = sit_data._SIT__tenantName
        global ovf_package_name
        ovf_package_name = Common_utilities.get_name_with_timestamp(Common_utilities, ovf_package[:-4:])

        data_file = '"{\\"tenantName\\":\\"' + tenant_name + '\\",\\"ovfPackage\\":{\\"name\\":\\"' + ovf_package_name + '\\",\\"description\\":\\"VNF with OVF VNFD\\",\\"fileChecksum\\":\\"' + file_checksum + '\\",\\"fileName\\":\\"' + ovf_package + '\\",\\"isPublic\\":false,\\"chunkSize\\":\\"' + chunk_Size + '\\",\\"chunkData\\":\\"' + chunk_Data + '\\" }}"'

        command = f'cd {SIT.get_base_folder(SIT)}; echo {data_file} > file_onboard_ovf_input.base64.req.body'
        log.info('command to create file_onboard_ovf_input.base64.req.body file ' + command)
        stdin, stdout, stderr = connection.exec_command(command)
        command = 'wc -c < {}'.format(ovf_package)
        stdin, stdout, stderr = connection.exec_command(command)
        command_output = str(stdout.read())
        content_range = command_output[2:-3:1]

        curl = '''curl --insecure -X POST  https://{}/ecm_service/ovfpackages -H 'Content-Range: bytes 0-'''.format(
            core_vm_hostname) + str(int(
            content_range) - 1) + '/' + content_range + '''{} -H 'AuthToken: {}' -H 'Content-Type: application/json' --data @file_onboard_ovf_input.base64.req.body'''.format(
            "'", token)

        command = curl
        Report_file.add_mesg('Step', 'Executing the curl command to onboard the ovf  ', command)
        command_output = ExecuteCurlCommand.get_json_output(connection, command)
        output = ast.literal_eval(command_output[2:-1:1])
        requestStatus = output['status']['reqStatus']

        if 'SUCCESS' in requestStatus:
            global ovf_id
            ovf_id = output['data']['ovfPackage']['id']
            log.info(command_output)
            Report_file.add_line('Executed the curl command to onboard ovf: ' + command_output)
            log.info('Onboarded ovf package id is' + ovf_id)
            Report_file.add_line('Onboarded ovf package id is ' + ovf_id)

            Report_file.add_line('OVF for vcisco is now onboarded')

        elif 'ERROR' in requestStatus:

            command_error = output['status']['msgs'][0]['msgText']

            log.error('Error executing curl command for onboarding OVF ' + command_error)
            Report_file.add_line(command_error)
            Report_file.add_line('Error executing curl command while onboarding OVF')
            connection.close()
            assert False

        connection.close()
        log.info('onboarding ovf for vcisco ends')
        Report_file.add_line('Onboarding ovf for vcisco ends')

    except Exception as e:
        log.error('Error Onboarding of OVF for vCisco ' + str(e))
        Report_file.add_line('Error Onboarding of OVF for vCisco ' + str(e))
        assert False


def onboard_ovf():
    # ovf_package = 'ASR_Networks.ovf'
    package_dir = '/var/tmp/deployvcisco'

    EPIS_data = ECM_PI_Initialization.get_model_objects(ECM_PI_Initialization, 'EPIS')
    cloud_type = EPIS_data._EPIS__cloudManagerType

    if cloud_type == 'OPENSTACK':
        ovf_package = r'ASR_Networks_RHOS.ovf'
    else:
        ovf_package = r'ASR_Networks_CEE.ovf'

    onboard_generic_ovf_package(ovf_package, package_dir)


def deploy_generic_ovf_package(file_name):
    try:

        log.info('Start Deployment of OVF for ' + file_name)
        Report_file.add_line('Start Deployment of OVF begins... ' + file_name)

        ecm_host_data = ECM_PI_Initialization.get_model_objects(ECM_PI_Initialization, 'ECMPI')

        ecm_server_ip = ecm_host_data._Ecm_PI__ECM_Host_Blade_IP
        ecm_username = ecm_host_data._Ecm_PI__ECM_Host_Blade_username
        ecm_password = ecm_host_data._Ecm_PI__ECM_Host_Blade_Password
        core_vm_ip = ecm_host_data._Ecm_PI__CORE_VM_IP
        core_vm_hostname = ecm_host_data._Ecm_PI__core_vm_hostname
        connection = ServerConnection.get_connection(ecm_server_ip, ecm_username, ecm_password)

        log.info('Generating token in the host blade server using the  curl command  ')
        token = Common_utilities.authToken(Common_utilities, connection, core_vm_hostname)
        log.info('Deploying of ovf using the token for authentication ')

        Report_file.add_line('Start Deployment of OVF  using the token for authentication ')
        update_ovf_deploy_file(file_name)

        sftp = connection.open_sftp()
        sftp.put(r'com_ericsson_do_auto_integration_files/' + file_name, SIT.get_base_folder(SIT) + file_name)
        sftp.close()

        curl = '''curl --insecure https://{}/ecm_service/ovfpackages/{}/deploy -H 'AuthToken: {}' -H 'Accept: application/json' -H 'Content-Type: application/json' --data @{}'''.format(
            core_vm_hostname, ovf_id, token, file_name)
        command = curl
        Report_file.add_mesg('Step', 'Executing the curl command to deploy the ovf  ', command)
        command_output = ExecuteCurlCommand.get_json_output(connection, command)
        output = ast.literal_eval(command_output[2:-1:1])
        requestStatus = output['status']['reqStatus']

        if 'SUCCESS' in requestStatus:
            log.info('Curl command for OVF deployment is successful')
            Report_file.add_line('Order status of OVF  deployment is successful: ' + command_output)

            order_status, order_output = Common_utilities.ovforderReqStatus(Common_utilities, connection, token,
                                                                            core_vm_hostname, ovf_package_name, 20)

            if order_status:
                log.info('Order Status of curl command  for OVF deployment is completed ' + ovf_package_name)
                Report_file.add_line('Order Status  for OVF deployment is completed ' + ovf_package_name)
            else:
                log.info(order_output)
                log.info(
                    'Order Status of curl command for OVF deployment is failed with message mentioned above ' + ovf_package_name)
                Report_file.add_line('Order Status for OVF deployment failed with message mentioned above ' + ovf_package_name)
                connection.close()
                assert False

        elif 'ERROR' in requestStatus:

            command_error = output['status']['msgs'][0]['msgText']

            log.error('Error executing curl command for deploying OVF ' + command_error)
            Report_file.add_line(command_error)
            Report_file.add_line('Error executing curl command while deploying OVF')
            connection.close()
            assert False

        connection.close()
        log.info('deploying ovf ends')
        Report_file.add_line('deploying ovf  ends')

    except Exception as e:
        log.error('Error Deployment of OVF  ' + str(e))
        Report_file.add_line('Error Deployment of OVF  ' + str(e))
        assert False


def deploy_ovf():
    ecm_host_data = ECM_PI_Initialization.get_model_objects(ECM_PI_Initialization, 'ECMPI')

    ecm_server_ip = ecm_host_data._Ecm_PI__ECM_Host_Blade_IP
    ecm_username = ecm_host_data._Ecm_PI__ECM_Host_Blade_username
    ecm_password = ecm_host_data._Ecm_PI__ECM_Host_Blade_Password

    connection = ServerConnection.get_connection(ecm_server_ip, ecm_username, ecm_password)
    package_dir = '/var/tmp/deployvcisco'
    EPIS_data = ECM_PI_Initialization.get_model_objects(ECM_PI_Initialization, 'EPIS')
    cloud_type = EPIS_data._EPIS__cloudManagerType

    if cloud_type == 'OPENSTACK':
        file_name = r'deploy_ovf_RHOS.json'
    else:
        file_name = r'deploy_ovf_CEE.json'
    ServerConnection.get_file_sftp(connection, package_dir + '/' + file_name,
                                    r'com_ericsson_do_auto_integration_files/' + file_name)

    deploy_generic_ovf_package(file_name)

    connection.close()


def deploy_asr_network():
    try:

        log.info('Start Deployment of network for ASR ')
        Report_file.add_line('Start Deployment of Network begins... ')

        ecm_host_data = ECM_PI_Initialization.get_model_objects(ECM_PI_Initialization, 'ECMPI')

        ecm_server_ip = ecm_host_data._Ecm_PI__ECM_Host_Blade_IP
        ecm_username = ecm_host_data._Ecm_PI__ECM_Host_Blade_username
        ecm_password = ecm_host_data._Ecm_PI__ECM_Host_Blade_Password
        core_vm_ip = ecm_host_data._Ecm_PI__CORE_VM_IP
        core_vm_hostname = ecm_host_data._Ecm_PI__core_vm_hostname
        connection = ServerConnection.get_connection(ecm_server_ip, ecm_username, ecm_password)

        log.info('Generating token in the host blade server using the  curl command  ')
        token = Common_utilities.authToken(Common_utilities, connection, core_vm_hostname)
        log.info('Deploying of network using the token for authentication ')
        package_dir = '/var/tmp/deployvcisco'
        EPIS_data = ECM_PI_Initialization.get_model_objects(ECM_PI_Initialization, 'EPIS')
        cloud_type = EPIS_data._EPIS__cloudManagerType
        if cloud_type == 'OPENSTACK':
            file_name = r'network_RHOS.json'
        else:
            file_name = r'network_CEE.json'

        ServerConnection.get_file_sftp(connection, package_dir + '/' + file_name,
                                        r'com_ericsson_do_auto_integration_files/' + file_name)

        ServerConnection.put_file_sftp(connection, r'com_ericsson_do_auto_integration_files/' + file_name,
                                       SIT.get_base_folder(SIT) + file_name)

        if cloud_type == 'OPENSTACK':
            curl = '''curl --insecure -X POST https://{}/ecm_service/v2/orders -H "AuthToken: {}" -H 'Content-Type: application/json' --data @{}'''.format(
                core_vm_hostname, token, file_name)
        else:
            curl = '''curl --insecure -X POST https://{}/ecm_service/orders -H "AuthToken: {}" -H 'Content-Type: application/json' --data @{}'''.format(
                core_vm_hostname, token, file_name)

        # curl = '''curl --insecure -X POST https://{}/ecm_service/orders -H "AuthToken: {}" -H 'Content-Type: application/json' --data @{}'''.format(core_vm_ip, token, file_name)
        command = curl
        Report_file.add_mesg('Step', 'Executing the curl command to deploy the network for ASR', command)
        command_output = ExecuteCurlCommand.get_json_output(connection, command)
        Report_file.add_line('Internal Network curl output ' + command_output)
        output = ast.literal_eval(command_output[2:-1:1])
        requestStatus = output['status']['reqStatus']

        if 'SUCCESS' in requestStatus:
            order_id = output['data']['order']['id']
            log.info('Order id for network creation for ASR  ' + order_id)
            Report_file.add_line('Order id for ASR network creation  ' + order_id)
            log.info(command_output)

            order_status, order_output = Common_utilities.orderReqStatus(Common_utilities, connection, token,
                                                                         core_vm_hostname, order_id, 10)

            if order_status:
                log.info('Order Status is completed ' + order_id)
                Report_file.add_line('Order Status is completed ' + order_id)
                log.info('Created ASR Network creation successfully :  ' + command_output)
                Report_file.add_line('Created ASR Network creation successfully' + command_output)
                log.info('wait 5 seconds to complete the network creation order for ASR ')
                time.sleep(5)


            else:
                log.info('Order Status is failed with message mentioned above ' + order_id)
                Report_file.add_line('Order Status is failed with message mentioned above ' + order_id)
                connection.close()
                assert False


        elif 'ERROR' in requestStatus:
            command_error = output['status']['msgs'][0]['msgText']
            log.error('Error executing curl command for creation network for ASR ' + command_error)
            Report_file.add_line(command_error)
            Report_file.add_line('Error executing curl command for creating network for ASR')
            connection.close()
            assert False

        connection.close()
        log.info('Network creation for ASR ends')
        Report_file.add_line('Network creation for ASR ends...')
    except Exception as e:
        log.error('Error Network creation for ASR ' + str(e))
        Report_file.add_line('Error Network creation for ASR ' + str(e))
        assert False


def deploy_vcisco():
    try:
        log.info('Start Deployment of vCisco')
        Report_file.add_line('Start Deployment of VCISCO begins...')

        ecm_host_data = ECM_PI_Initialization.get_model_objects(ECM_PI_Initialization, 'ECMPI')

        ecm_server_ip = ecm_host_data._Ecm_PI__ECM_Host_Blade_IP
        ecm_username = ecm_host_data._Ecm_PI__ECM_Host_Blade_username
        ecm_password = ecm_host_data._Ecm_PI__ECM_Host_Blade_Password
        core_vm_ip = ecm_host_data._Ecm_PI__CORE_VM_IP
        core_vm_hostname = ecm_host_data._Ecm_PI__core_vm_hostname
        connection = ServerConnection.get_connection(ecm_server_ip, ecm_username, ecm_password)

        log.info('Generating token in the host blade server using the  curl command  ')
        token = Common_utilities.authToken(Common_utilities, connection, core_vm_hostname)
        log.info('Deploying vCisco using the token generated')

        Report_file.add_line('Start Deployment of vCisco using the token for authentication ')

        package_dir = '/var/tmp/deployvcisco'
        EPIS_data = ECM_PI_Initialization.get_model_objects(ECM_PI_Initialization, 'EPIS')
        cloud_type = EPIS_data._EPIS__cloudManagerType
        if cloud_type == 'OPENSTACK':
            file_name = r'ASR_VM_DEPLOY_RHOS.json'
        else:
            file_name = r'ASR_VM_DEPLOY_CEE.json'

        ServerConnection.get_file_sftp(connection, package_dir + '/' + file_name,
                                        r'com_ericsson_do_auto_integration_files/' + file_name)

        update_vcisco_deploy_file(file_name)

        if cloud_type == 'OPENSTACK':
            file_name = r'ASR_VM_DEPLOY_RHOS.json'
            file_name1 = 'com_ericsson_do_auto_integration_files/' + file_name
            Json_file_handler.update_any_json_attr(Json_file_handler, file_name1,
                                                   ['orderItems', 0, 'createVm', 'securityGroups', 0], 'id',
                                                   security_group_id)

        sftp = connection.open_sftp()
        sftp.put(r'com_ericsson_do_auto_integration_files/' + file_name, SIT.get_base_folder(SIT) + file_name)
        sftp.close()

        curl = '''curl --insecure -X POST https://{}/ecm_service/v2/orders -H 'AuthToken: {}' -H 'Content-Type: application/json' --data @{}'''.format(
            core_vm_hostname, token, file_name)
        command = curl
        Report_file.add_mesg('Step', 'Executing the curl command to deploy the vCisco ', command)
        command_output = ExecuteCurlCommand.get_json_output(connection, command)
        output = ast.literal_eval(command_output[2:-1:1])
        requestStatus = output['status']['reqStatus']

        if 'SUCCESS' in requestStatus:
            order_id = output['data']['order']['id']
            order_status, order_output = Common_utilities.orderReqStatus(Common_utilities, connection, token,
                                                                         core_vm_hostname, order_id, 30)

            if order_status:

                log.info('Order Status of curl command deployment is completed ' + order_id)
                Report_file.add_line('Order Status is completed ' + order_id)
                log.info('Curl command for VCISCO deployment is successful')
                log.info(command_output)
                Report_file.add_line('Order status of vCisco deployment is succesfull: ' + command_output)

            else:

                log.info(order_output)
                log.info('Order Status of curl command deployment is failed with message mentioned above ' + order_id)
                Report_file.add_line('Order Status is failed with message mentioned above ' + order_id)
                connection.close()
                assert False

        elif 'ERROR' in requestStatus:
            command_error = output['status']['msgs'][0]['msgText']
            log.error('Error executing curl command for deploying VCISCO ')
            Report_file.add_line('Error executing curl command while deploying VCISCO')
            connection.close()
            assert False

        connection.close()
        log.info('deployment of  vCisco ends')
        Report_file.add_line('deployment of vCisco ends')
    except Exception as e:
        log.error('Error Deployment of vCisco ' + str(e))
        Report_file.add_line('Error Deployment of vCisco ' + str(e))
        assert False


def verify_vcisco_deployment():
    try:
        log.info('Start verification of vCisco deployment')
        Report_file.add_line('Start verification of vCisco deployment...')
        log.info('waiting 360 seconds to verify vCisco Deployment')
        time.sleep(360)

        ecm_host_data = Initialization_script.get_model_objects(Initialization_script, 'ECM_CORE')
        ecm_server_ip = ecm_host_data._Ecm_core__ECM_Host_Blade_IP
        ecm_username = ecm_host_data._Ecm_core__ECM_Host_Blade_username
        ecm_password = ecm_host_data._Ecm_core__ECM_Host_Blade_Password
        connection = ServerConnection.get_connection(ecm_server_ip, ecm_username, ecm_password)

        EPIS_data = ECM_PI_Initialization.get_model_objects(ECM_PI_Initialization, 'EPIS')
        cloud_type = EPIS_data._EPIS__cloudManagerType

        if cloud_type == 'OPENSTACK':
            file_name = r'ASR_VM_DEPLOY_RHOS.json'
        else:
            file_name = r'ASR_VM_DEPLOY_CEE.json'

        file_data = Json_file_handler.get_json_data(Json_file_handler,
                                                    r'com_ericsson_do_auto_integration_files/' + file_name)
        ip_address = file_data['orderItems'][1]['createVmVnic']['internalIpAddress'][0]
        print(ip_address)
        ping_response = get_ping_response(connection, ip_address)

        if True == ping_response:
            log.info('Ping Successful')
            log.info('Verification of vCisco deployment is success')
            Report_file.add_line('Verification of vCisco deployment is successful')
            connection.close()
        else:
            log.info('Ping Failed.Please check the logs manually ')
            Report_file.add_line('Verification of vCisco deployment failed. Please check the logs manually ')
            connection.close()
            assert False
    except Exception as e:
        log.error('Error verify vCisco Deployment' + str(e))
        Report_file.add_line('Error verify vCisco Deployment ' + str(e))
        assert False


def register_vcisco_license():
    try:
        log.info('Start Registering vCisco License')
        Report_file.add_line('Start Registering of vCisco License...')

        ecm_host_data = ECM_PI_Initialization.get_model_objects(ECM_PI_Initialization, 'ECMPI')
        ecm_server_ip = ecm_host_data._Ecm_PI__ECM_Host_Blade_IP
        ecm_username = ecm_host_data._Ecm_PI__ECM_Host_Blade_username
        ecm_password = ecm_host_data._Ecm_PI__ECM_Host_Blade_Password
        vcisco_management_ip = ecm_host_data._Ecm_PI__vCisco_Management_ip
        vcisco_management_username = ecm_host_data._Ecm_PI__vCisco_Management_username
        vcisco_management_password = ecm_host_data._Ecm_PI__vCisco_Management_Password

        connection = ServerConnection.get_connection(ecm_server_ip, ecm_username, ecm_password)
        interact = connection.invoke_shell()
        resp = interact.recv(9999)
        buff = str(resp)
        command = 'ssh ' + vcisco_management_username + '@' + vcisco_management_ip
        log.info('Command: ' + command)

        interact.send(command + '\n')
        time.sleep(2)
        resp = interact.recv(9999)
        buff = str(resp)
        log.info(buff)
        if 'continue connecting' in buff:
            interact.send('yes\n')
            time.sleep(5)
            resp = interact.recv(9999)
            buff = str(resp)

        if 'Password:' in buff:
            interact.send(vcisco_management_password + '\n')
            time.sleep(2)

        command = 'conf t'
        interact.send(command + '\n')
        time.sleep(2)
        resp = interact.recv(9999)
        buff = str(resp)
        log.info('Command: ' + command + 'command output : ' + buff)

        command = 'domain name-server 159.107.173.3'
        interact.send(command + '\n')
        time.sleep(2)
        resp = interact.recv(9999)
        buff = str(resp)
        log.info('Command: ' + command + 'command output : ' + buff)

        command = 'domain name-server 159.107.173.12'
        interact.send(command + '\n')
        time.sleep(2)
        resp = interact.recv(9999)
        buff = str(resp)
        log.info('Command: ' + command + 'command output : ' + buff)

        command = 'domain lookup source-interface MgmtEth0/RP0/CPU0/0'
        interact.send(command + '\n')
        time.sleep(2)
        resp = interact.recv(9999)
        buff = str(resp)
        log.info('Command: ' + command + 'command output : ' + buff)

        command = 'crypto ca trustpoint Trustpool'
        interact.send(command + '\n')
        time.sleep(2)
        resp = interact.recv(9999)
        buff = str(resp)
        log.info('Command: ' + command + 'command output : ' + buff)

        command = 'crl optional'
        interact.send(command + '\n')
        time.sleep(2)
        resp = interact.recv(9999)
        buff = str(resp)
        log.info('Command: ' + command + 'command output : ' + buff)

        command = 'commit'
        interact.send(command + '\n')
        time.sleep(4)
        resp = interact.recv(9999)
        buff = str(resp)
        log.info('Command: ' + command + 'command output : ' + buff)

        command = 'exit'
        interact.send(command + '\n')
        time.sleep(2)
        resp = interact.recv(9999)
        buff = str(resp)
        log.info('Command: ' + command + 'command output : ' + buff)

        command = 'end'
        interact.send(command + '\n')
        time.sleep(2)
        resp = interact.recv(9999)
        buff = str(resp)
        log.info('Command: ' + command + 'command output : ' + buff)

        command = 'conf t'
        interact.send(command + '\n')
        time.sleep(2)
        resp = interact.recv(9999)
        buff = str(resp)
        log.info('Command: ' + command + 'command output : ' + buff)

        command = 'no call-home'
        interact.send(command + '\n')
        time.sleep(2)
        resp = interact.recv(9999)
        buff = str(resp)
        log.info('Command: ' + command + 'command output : ' + buff)

        command = 'call-home'
        interact.send(command + '\n')
        time.sleep(2)
        resp = interact.recv(9999)
        buff = str(resp)
        log.info('Command: ' + command + 'command output : ' + buff)

        command = 'service active'
        interact.send(command + '\n')
        time.sleep(2)
        resp = interact.recv(9999)
        buff = str(resp)
        log.info('Command: ' + command + 'command output : ' + buff)

        command = 'contact smart-licensing'
        interact.send(command + '\n')
        time.sleep(2)
        resp = interact.recv(9999)
        buff = str(resp)
        log.info('Command: ' + command + 'command output : ' + buff)

        command = 'source-interface MgmtEth0/RP0/CPU0/0'
        interact.send(command + '\n')
        time.sleep(2)
        resp = interact.recv(9999)
        buff = str(resp)
        log.info('Command: ' + command + 'command output : ' + buff)

        command = 'profile CiscoTAC-1'
        interact.send(command + '\n')
        time.sleep(2)
        resp = interact.recv(9999)
        buff = str(resp)
        log.info('Command: ' + command + 'command output : ' + buff)

        command = 'active'
        interact.send(command + '\n')
        time.sleep(2)
        resp = interact.recv(9999)
        buff = str(resp)
        log.info('Command: ' + command + 'command output : ' + buff)

        command = 'destination address http http://tools.cisco.com/its/service/oddce/services/DDCEService'
        interact.send(command + '\n')
        time.sleep(2)
        resp = interact.recv(9999)
        buff = str(resp)
        log.info('Command: ' + command + 'command output : ' + buff)

        command = 'destination transport-method http'
        interact.send(command + '\n')
        time.sleep(2)
        resp = interact.recv(9999)
        buff = str(resp)
        log.info('Command: ' + command + 'command output : ' + buff)

        command = 'commit'
        interact.send(command + '\n')
        time.sleep(2)
        resp = interact.recv(9999)
        buff = str(resp)
        log.info('Command: ' + command + 'command output : ' + buff)

        command = 'exit'
        interact.send(command + '\n')
        time.sleep(4)
        resp = interact.recv(9999)
        buff = str(resp)
        log.info('Command: ' + command + 'command output : ' + buff)

        command = 'exit'
        interact.send(command + '\n')
        time.sleep(4)
        resp = interact.recv(9999)
        buff = str(resp)
        log.info('Command: ' + command + 'command output : ' + buff)

        command = 'exit'
        interact.send(command + '\n')
        time.sleep(4)
        resp = interact.recv(9999)
        buff = str(resp)
        log.info('Command: ' + command + 'command output : ' + buff)

        command = 'license smart deregister'
        interact.send(command + '\n')
        time.sleep(15)
        resp = interact.recv(9999)
        buff = str(resp)
        log.info('Command: ' + command + 'command output : ' + buff)

        EPIS_data = ECM_PI_Initialization.get_model_objects(ECM_PI_Initialization, 'EPIS')
        cloud_type = EPIS_data._EPIS__cloudManagerType

        if vcisco_management_ip == '10.232.122.126':
            command = 'license smart register idtoken MGM1OGIxYjYtNTMyNi00NTIzLWE2NmItYjJiOTJiMjY4NWJmLTE2NzcxNDc0%0AMDYzOTB8VCs4ODRXYXAwTjQ4N2ZsRG9uRW1sOFlIbFJKRHBXTXd2QXpid2g2%0ATm51UT0%3D%0A force'
        elif vcisco_management_ip == '10.210.221.62':
            command = 'license smart register idtoken MjZlNmI5ZDgtMWJkNC00YTY3LWIyOWYtN2YyYTM5MWRiZDE5LTE2NjcwNTQw%0AMTc2NTd8cFhaNUUxV1ZleTBkRVhtSENzcE1JTnZhWVZmNCtXYkxaUFRmRG1M%0AMU8xTT0%3D%0A force'
        else:
            log.info('Could not find the license token for the given vcisco management IP: ' + vcisco_management_ip)
            Report_file.add_line('Could not find the license token for the given vcisco management IP: ' + vcisco_management_ip)
            assert False

        interact.send(command + '\n')
        time.sleep(40)
        resp = interact.recv(9999)
        log.info('Command: ' + command)
        count = 0
        while (count != 2):
            command = 'show license status'
            interact.send(command + '\n')
            time.sleep(5)
            resp = interact.recv(9999)
            buff = str(resp)
            log.info('Command: ' + command)
            log.info('command output : ' + buff)

            if 'ENABLED' and 'First Attempt Pending' in buff and count != 1:
                log.info('Output contains First attempt pending  ')
                log.info('waiting 120 seconds to check the status again ')
                count = count + 1
                time.sleep(120)

            elif 'ENABLED' and 'SUCCEEDED' in buff:
                log.info('License command "license smart register " completed successfully.' + buff)
                break
            else:
                log.error('License command "license smart register " Failed' + buff)
                interact.shutdown(2)
                connection.close()
                assert False

        interact.shutdown(2)
        connection.close()

    except Exception as e:
        log.error('Error Registering vCisco License' + str(e))
        Report_file.add_line('Error Registering vCisco License ' + str(e))
        assert False


def main():
    # Getting user inputs and storing it to local cache memory

    log.info('Starting script : VCISCO_DEPLOYMENT')
    log.info('Going to fetch user inputs')
    Report_file.add_line('Starting script : VCISCO_DEPLOYMENT')

    create_vCisco_flavours()
    create_valid9m_flavours()
    register_vCisco_images()
    onboard_ovf()
    deploy_ovf()
    deploy_asr_network()
    create_vcisco_bgw_ports()
    deploy_vcisco()
    verify_vcisco_deployment()
    register_vcisco_license()

    log.info('END script : VCISCO_DEPLOYMENT')
    Report_file.add_line('END script : VCISCO_DEPLOYMENT')
