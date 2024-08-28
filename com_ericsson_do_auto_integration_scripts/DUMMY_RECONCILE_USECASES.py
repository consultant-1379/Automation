from com_ericsson_do_auto_integration_utilities.Report_file import Report_file
from com_ericsson_do_auto_integration_utilities.Logger import Logger
from com_ericsson_do_auto_integration_scripts.ECM_NODE_DEPLOYMENT import *
from com_ericsson_do_auto_integration_utilities.SIT_files_update import *
from com_ericsson_do_auto_integration_scripts.VERIFY_NODE_DEPLOYMENT import *
from com_ericsson_do_auto_integration_initilization.SIT_initialization import SIT_initialization

from com_ericsson_do_auto_integration_utilities.Common_utilities import Common_utilities
from com_ericsson_do_auto_integration_scripts.CEE_Cleanup import *
from com_ericsson_do_auto_integration_utilities.EPIS_files_update import *
from com_ericsson_do_auto_integration_scripts.VERIFY_RECONCILE_USECASES import *
from com_ericsson_do_auto_integration_scripts.ECM_POST_INSTALLATION import *
from com_ericsson_do_auto_integration_utilities.Shell_handler import ShellHandler
from com_ericsson_do_auto_integration_utilities.ExecuteCurlCommand import *


import time


log = Logger.get_logger('DUMMY_RECONCILE_USECASES.py')


def delete_reconcile_volumes():
    volume_list = list_all_volumes_in_EO_CM()
    delete_volumes(volume_list, "Reconcile_bsv")


def get_vol_ids(output, pattern):
    for k, v in output.items():
        if isinstance(v, dict):
            if k == 'data':
                len_of_dict = len(v['bsvs'])
                for i in range(len_of_dict ):
                    name = v['bsvs'][i]['name']
                    if pattern in name:
                        yield v['bsvs'][i]['id']


def delete_volumes(volume_list, match_this):
    """
    Deletes volumes from the list which names contain the string "match_this"
    Empty string pattern will match and delete all volumes
    :param volume_list: list of volumes in json format
    :param match_this: string to match in a volume name to be deleted
    """
    str_to_match = match_this
    try:
        log.info('Start deletion of Reconsile_bsv block storage volumes')
        Report_file.add_line('Block storage volumes deletion begins...')

        ecm_host_data = ECM_PI_Initialization.get_model_objects(ECM_PI_Initialization, 'ECMPI')

        ecm_server_ip = ecm_host_data._Ecm_PI__ECM_Host_Blade_IP
        ecm_username = ecm_host_data._Ecm_PI__ECM_Host_Blade_username
        ecm_password = ecm_host_data._Ecm_PI__ECM_Host_Blade_Password
        core_vm_ip = ecm_host_data._Ecm_PI__CORE_VM_IP
        core_vm_hostname = ecm_host_data._Ecm_PI__core_vm_hostname

        

        connection = ServerConnection.get_connection(ecm_server_ip, ecm_username, ecm_password)

        token = Common_utilities.authToken(Common_utilities, connection, core_vm_hostname)

        volume_ids = [vol for vol in get_vol_ids(volume_list, str_to_match) if vol]

        if volume_ids:
            for vol_id in volume_ids:
                command = '''curl --insecure "https://{}/ecm_service/bsvs/{}" -X DELETE -H "Accept: application/json" -H "AuthToken: {}"'''.format(core_vm_hostname, vol_id, token)

                log.info('Deleting block storage volume id: {} '.format(vol_id))
                Report_file.add_line('Deleting block storage volume id: {}'.format(vol_id))
                Report_file.add_line('Deleting block storage curl command: {}'.format(command))

                command_output = ExecuteCurlCommand.get_json_output(connection, command)

                Report_file.add_line('Deleting block storage volume output ' + command_output)

                command_out = ExecuteCurlCommand.get_sliced_command_output(command_output)
                command_out_dict = ast.literal_eval(command_out)
                requestStatus = command_out_dict['status']['reqStatus']

                if 'SUCCESS' in requestStatus:
                    order_id = command_out_dict['data']['order']['id']
                    order_status, order_output = Common_utilities.orderReqStatus(Common_utilities, connection,
                                                                                 token, core_vm_hostname, order_id, 30)

                    if order_status:
                        log.info('Order status is Completed')
                        Report_file.add_line('Order status is Completed')
                        log.info('Block storage volume deleted successfully')
                        Report_file.add_line('Executed the curl command for deleting block storage volumes : ' + command)
                        Report_file.add_line('Block storage volume id {} deleted successfully'.format(vol_id))
                        Report_file.add_line('Order status is {}'.format(order_id))

                    else:
                        log.error('Order status is Failed ')
                        assert False

                elif 'ERROR' in requestStatus:
                    command_error = command_out_dict['status']['msgs'][0]['msgText']
                    log.error('Error executing curl command for deleting Block storage volume id {} '.format(vol_id) + command_error)
                    Report_file.add_line(command_error)
                    Report_file.add_line('Error executing curl command for deleting block storage volume' + command)
                    Report_file.add_line('Error executing curl command for deleting block storage volume id ' + vol_id)
                    assert False

                else:
                    log.error('Error parsing curl command output ' + command)

        else:
            Report_file.add_line("No volumes with provided criteria were found")

    except Exception as e:
        log.info('Error deliting block storage volumes ' + str(e))
        Report_file.add_line('Error deleting block storage volumes ' + str(e))
        assert False
    finally:
        connection.close()


def list_all_volumes_in_EO_CM():

    try:
        Report_file.add_line('Block storage volumes listing begins...')

        ecm_host_data = ECM_PI_Initialization.get_model_objects(ECM_PI_Initialization, 'ECMPI')

        ecm_server_ip = ecm_host_data._Ecm_PI__ECM_Host_Blade_IP
        ecm_username = ecm_host_data._Ecm_PI__ECM_Host_Blade_username
        ecm_password = ecm_host_data._Ecm_PI__ECM_Host_Blade_Password
        core_vm_ip = ecm_host_data._Ecm_PI__CORE_VM_IP
        core_vm_hostname = ecm_host_data._Ecm_PI__core_vm_hostname


        connection = ServerConnection.get_connection(ecm_server_ip, ecm_username, ecm_password)

        token = Common_utilities.authToken(Common_utilities, connection, core_vm_hostname)

        log.info('listing block storage volumes using the token for authentication ')

        command = '''curl --insecure "https://{}/ecm_service/bsvs" -H "Accept: application/json" -H "AuthToken: {}"'''.format(core_vm_hostname, token)

        Report_file.add_line('Block storage volumes list command ' + command)

        command_output = ExecuteCurlCommand.get_json_output(connection, command)

        command_out = ExecuteCurlCommand.get_sliced_command_output(command_output)
        Report_file.add_line('Block storage volumes list command completed' + command_out)
        command_out_dict = ast.literal_eval(command_out)

        requestStatus = command_out_dict['status']['reqStatus']

        if 'SUCCESS' in requestStatus:
            log.info('Block storage volumes listed successfully')
            Report_file.add_line('Executed the curl command for listing block storage volumes : ' + command)
            Report_file.add_line('Block storage volumes listed successfully')
            return command_out_dict

        elif 'ERROR' in requestStatus:
            log.error('Error executing curl command for listing Block storage volumes ' + command)
            Report_file.add_line('Error executing curl command for listing block storage volumes' + command)
            assert False

        else:
            log.error('Error parsing curl command output ' + command)
            assert False

    except Exception as e:
        log.info('Error listing block storage volumes ' + str(e))
        Report_file.add_line('Error listing block storage volumes ' + str(e))
        assert False

    finally:
        connection.close()


def fetch_allocated_quota_before():
    global before_quota_list

    before_quota_list = fetch_reconcile_allocated_quota()


def fetch_VM_Vapp_details_before():
    global before_VM_vapp_details

    before_VM_vapp_details = fetch_vapp_vm_details()


def create_reconcile_srt():
    try:
        log.info('start creating reconcile srt')
        Report_file.add_line('start creating reconcile srt')

        EPIS_data = ECM_PI_Initialization.get_model_objects(ECM_PI_Initialization, 'EPIS')
        openstack_ip = EPIS_data._EPIS__openstack_ip
        username = EPIS_data._EPIS__openstack_username
        password = EPIS_data._EPIS__openstack_password
        openrc_filename = EPIS_data._EPIS__openrc_filename
        sit_data = SIT_initialization.get_model_objects(SIT_initialization, 'SIT')
        tenant_name = sit_data._SIT__tenantName
        flavor_name = 'CM-Reconcile_SRT'

        flavor_exists = check_flavor_exists(openrc_filename, openstack_ip, username, password, flavor_name)
        if flavor_exists:
            log.info('Flavor with name ' + flavor_name + ' already exists in cloud')
            Report_file.add_line('Flavor with name ' + flavor_name + ' already exists in cloud')
        else:
            log.info('Flavor with name ' + flavor_name + ' does not  exists in cloud')
            Report_file.add_line('Flavor with name ' + flavor_name + ' does not  exists in CEE')
            name = flavor_name[3:]

            update_any_flavor_file(name, 1, 1024, 1, tenant_name)
            update_transfer_flavour_file()
            create_flavour('flavour.json', 'flavour_transfer.json', name)

        log.info('Finished creating dummy mme flavor')
        Report_file.add_line('Finished creating dummy mme flavor')

    except Exception as e:
        log.error('Error creating dummy mme flavor ' + str(e))
        Report_file.add_line('Error creating dummy mme flavor ' + str(e))
        assert False


def register_reconcile_image():
    try:

        log.info('start register reconcile valid 9M image')
        Report_file.add_line('start register reconcile valid 9M image')
        sit_data = SIT_initialization.get_model_objects(SIT_initialization, 'SIT')
        ecm_host_data = Initialization_script.get_model_objects(Initialization_script, 'ECM_CORE')
        ecm_server_ip = ecm_host_data._Ecm_core__ECM_Host_Blade_IP
        ecm_username = ecm_host_data._Ecm_core__ECM_Host_Blade_username
        ecm_password = ecm_host_data._Ecm_core__ECM_Host_Blade_Password
        core_vm_ip = ecm_host_data._Ecm_core__CORE_VM_IP
        vimzone_name = sit_data._SIT__vimzone_name
        core_vm_hostname = ecm_host_data._Ecm_core__core_vm_hostname

        connection = ServerConnection.get_connection(ecm_server_ip, ecm_username, ecm_password)

        image_name = sit_data._SIT__valid9m_image_name
        global image_id
        image_id = sit_data._SIT__valid9m_image_id

        token = Common_utilities.authToken(Common_utilities, connection, core_vm_hostname)
        image_exists = check_image_registered(connection, image_name, token, core_vm_hostname)
        if image_exists:
            Report_file.add_line('Image with name ' + image_name + ' already registered in cloud manager')
        else:
            log.info('Going to register image with name ' + image_name)
            update_image_file('RegisterImage.json', image_name, vimzone_name, image_id)
            image_registration('RegisterImage.json')

        log.info('Finished register dummy mme image')
        Report_file.add_line('Finished register dummy mme image')

    except Exception as e:
        log.error('Error register mme images ' + str(e))
        Report_file.add_line('Error register mme images ' + str(e))
        assert False

    finally:
        connection.close()


def create_reconcile_block_storage():
    log.info('start creation of reconclie block storage')
    Report_file.add_line('Reconcile Block Storage creation begins...')

    ecm_host_data = ECM_PI_Initialization.get_model_objects(ECM_PI_Initialization, 'ECMPI')
    sit_data = SIT_initialization.get_model_objects(SIT_initialization, 'SIT')
    global bsv_name
    bsv_name = Common_utilities.get_name_with_timestamp(Common_utilities, 'Reconcile_bsv_')
    volume = 1
    vdc_id = sit_data._SIT__vdc_id
    global vimobject_id
    cinder_id = create_genric_block_storage(bsv_name, volume, vdc_id)

    ecm_server_ip = ecm_host_data._Ecm_PI__ECM_Host_Blade_IP
    ecm_username = ecm_host_data._Ecm_PI__ECM_Host_Blade_username
    ecm_password = ecm_host_data._Ecm_PI__ECM_Host_Blade_Password
    core_vm_ip = ecm_host_data._Ecm_PI__CORE_VM_IP
    core_vm_hostname = ecm_host_data._Ecm_PI__core_vm_hostname

    connection = ServerConnection.get_connection(ecm_server_ip, ecm_username, ecm_password)

    token = Common_utilities.authToken(Common_utilities, connection, core_vm_hostname)

    try:

        curl = '''curl --insecure --header 'Accept: application/json' --header 'AuthToken:{}' https://{}/ecm_service/bsvs/{}'''.format(
            token, core_vm_hostname, cinder_id)

        command = curl
        Report_file.add_line('Reconcile Block Storage vim object id fetching curl ' + command)

        command_output = ExecuteCurlCommand.get_json_output(connection, command)
        Report_file.add_line('Reconcile Block Storage vim object id fetching curl output  ' + command_output)

        command_out = ExecuteCurlCommand.get_sliced_command_output(command_output)
        output = ast.literal_eval(command_out)
        requestStatus = output['status']['reqStatus']

        if 'SUCCESS' in requestStatus:

            vimobject_id = output['data']['bsv']['vimObjectId']
            log.info('Reconcile Block Storage vim object id is ' + vimobject_id)
            Report_file.add_line('Reconcile Block Storage vim object id is ' + vimobject_id)

        elif 'ERROR' in requestStatus:

            command_error = output['status']['msgs'][0]['msgText']

            log.error(
                'Error executing curl command for fetching reconcile block Storage vim object id ' + command_error)
            Report_file.add_line(command_error)
            Report_file.add_line('Error executing curl command for fetching reconcile block Storage vim object id')

            assert False

    except Exception as e:
        log.error('Error fetching reconcile block storage vim object id' + str(e))
        Report_file.add_line('Error fetching reconcile block storage vim object id ' + str(e))
        assert False

    finally:
        connection.close()


def stack_update_uc1():
    try:
        log.info(' UC-1 start updating and running stack update file  ' )
        Report_file.add_line('UC-1 start updating and running stack update file ')
        
        stack_file_name = 'update_reconcile_stack.yaml'
        
        update_reconcile_stack_file(stack_file_name,'CM-Reconcile_SRT',vimobject_id,image_id,usecase_name = '1')

    except Exception as e:

        log.error('Error UC-1 start updating and running stack update file ' + str(e))
        Report_file.add_line('Error UC-1 start updating and running stack update file ' + str(e))
        assert False
   


def reconcile_vapp():
    try:
        log.info('Start reconcile vapp on ECM ')
        Report_file.add_line('Start reconcile vapp on ECM ')

        EPIS_data = ECM_PI_Initialization.get_model_objects(ECM_PI_Initialization, 'EPIS')
        sit_data = SIT_initialization.get_model_objects(SIT_initialization, 'SIT')

        tenant_id = EPIS_data._EPIS__tenant_name
        ecm_host_data = Initialization_script.get_model_objects(Initialization_script, 'ECM_CORE')
        ecm_server_ip = ecm_host_data._Ecm_core__ECM_Host_Blade_IP
        ecm_username = ecm_host_data._Ecm_core__ECM_Host_Blade_username
        ecm_password = ecm_host_data._Ecm_core__ECM_Host_Blade_Password
        core_vm_ip = ecm_host_data._Ecm_core__CORE_VM_IP
        core_vm_hostname = ecm_host_data._Ecm_core__core_vm_hostname

        node_id = sit_data._SIT__vapp_Id

        file_name = 'reconcile_vapp.json'

        Json_file_handler.update_any_json_attr(Json_file_handler,
                                               r'com_ericsson_do_auto_integration_files/' + file_name, ['vapps', 0],
                                               'id', node_id)

        connection = ServerConnection.get_connection(ecm_server_ip, ecm_username, ecm_password)

        ServerConnection.put_file_sftp(connection,
                                        r'com_ericsson_do_auto_integration_files/' + file_name, SIT.get_base_folder(SIT) + file_name)

        token = Common_utilities.authToken(Common_utilities, connection, core_vm_hostname)

        log.info('performing reconcile use case on ECM ')
        Report_file.add_line('performing reconcile use case on ECM  ')

        curl = '''curl -X POST --insecure --header 'Content-Type: application/json' --header 'Accept: application/json' --header 'AuthToken:{}' --header 'tenantid:{}' --data @{} https://{}/ecm_service/vapps/reconcilevnfs'''.format(
            token, tenant_id, file_name, core_vm_hostname)
        command = curl
        Report_file.add_line('reconcile curl command  ' + command)

        command_output = ExecuteCurlCommand.get_json_output(connection, command)
        output = ast.literal_eval(command_output[2:-1:1])
        requestStatus = output['status']['reqStatus']

        if 'SUCCESS' in requestStatus:

            order_id = output['data']['order']['id']

            order_status, order_output = Common_utilities.orderReqStatus(Common_utilities, connection, token,
                                                                         core_vm_hostname,
                                                                         order_id, 10)

            if order_status:

                log.info('Order Status is completed ' + order_id)
                Report_file.add_line('Order Status is completed ' + order_id)

            else:

                log.info(order_output)
                log.info('Order Status is failed with message mentioned above ' + order_id)
                Report_file.add_line('Order Status is failed with message mentioned above ' + order_id)
                connection.close()
                assert False


        elif 'ERROR' in requestStatus:

            command_error = output['status']['msgs'][0]['msgText']
            log.error('Error executing curl command for reconcile ' + command_error)
            Report_file.add_line(command_error)
            Report_file.add_line('Error executing curl command for reconcile ')
            connection.close()
            assert False

            log.info('Finished reconcile on ECM ')
            Report_file.add_line('Finished reconcile on ECM ')

    except Exception as e:

        log.info('Error reconcile on ECM ' + str(e))
        Report_file.add_line('Error reconcile on ECM ' + str(e))
        assert False
    finally:
        connection.close()


def fetch_allocated_quota_usecase1():
    global usecase1_quota_list

    usecase1_quota_list = fetch_reconcile_allocated_quota()


def fetch_VM_Vapp_details_usecase1():
    log.info('wait 20 seconds for reconcile to finish')
    time.sleep(20)
    global usecase1_VM_vapp_details

    usecase1_VM_vapp_details = fetch_vapp_vm_details()


def verification_reconcile_usecase1():

    verify_reconcile_usecase1(before_quota_list,before_VM_vapp_details,usecase1_quota_list,usecase1_VM_vapp_details)


def delete_resource():

    try:

        log.info(' Use Case 2 - Start deleting BSV resource from open stack' )
        Report_file.add_line('Use Case 2 - Start deleting BSV resource from open stack ')

        EPIS_data = ECM_PI_Initialization.get_model_objects(ECM_PI_Initialization, 'EPIS')
        sit_data = SIT_initialization.get_model_objects(SIT_initialization, 'SIT')
        openstack_ip = EPIS_data._EPIS__openstack_ip
        username = EPIS_data._EPIS__openstack_username
        password = EPIS_data._EPIS__openstack_password
        openrc_filename = EPIS_data._EPIS__openrc_filename


        log.info('Connecting with open stack to run remove volume command  ' +openstack_ip )
        ShellHandler.__init__(ShellHandler, openstack_ip, username, password)
        command = 'source {}'.format(openrc_filename)
        stdin, stdout, stderr = ShellHandler.execute(ShellHandler, command)

        command = 'openstack volume list | grep -i {}'.format(bsv_name)
        Report_file.add_line('command to fetch BSV system id and attached server name ' + command)
        stdin, stdout, stderr = ShellHandler.execute(ShellHandler, command)
        Report_file.add_line('BSV system id and attached server name fetch command output ' + str(stdout))

        for line in stdout:
            list_data = line.split('|')
            bsv_id = list_data[1].strip()
            server_name = list_data[5].strip().split('Attached to')[1].split('on /dev/vdb')[0].strip()

        log.info('BSV id : '+bsv_id + ' server name : '+server_name)
        Report_file.add_line('BSV system id is ' + bsv_id + ' and ' + 'attached server name is ' + server_name)

        command = 'openstack server list | grep -i {}'.format(server_name)
        Report_file.add_line('command to fetch server id using server name ' + command)
        stdin, stdout, stderr = ShellHandler.execute(ShellHandler, command)
        Report_file.add_line(' fetch server id command output ' + str(stdout))

        for line in stdout:
            list_data = line.split('|')
            server_id = list_data[1].strip()
            network_name = list_data[4].strip().split('=')[0]

        log.info('server id is ' + server_id)
        log.info('network name is ' + network_name)
        Report_file.add_line('server id is ' + server_id)
        Report_file.add_line('network name is ' + network_name)


        command = 'openstack server remove volume {} {}'.format(server_id,bsv_id)
        Report_file.add_line('command to remove volume ' + command)
        stdin, stdout, stderr = ShellHandler.execute(ShellHandler, command)
        Report_file.add_line(' remove volume command output ' + str(stdout))

        time.sleep(5)

        command = 'openstack port list --network {} | grep -i reconcile'.format(network_name)
        Report_file.add_line('command to list port using network name ' + network_name + ' + , command is ' + command)
        stdin, stdout, stderr = ShellHandler.execute(ShellHandler, command)

        Report_file.add_line('port list command output ' + str(stdout))

        for line in stdout:
            port_id = line.split('|')[1].strip()
            log.info('port id : '+port_id)

        command = 'openstack port delete {}'.format(port_id)
        Report_file.add_line('command to delete port ' + command)
        stdin, stdout, stderr = ShellHandler.execute(ShellHandler, command)
        Report_file.add_line(' delete port command output ' + str(stdout))

        time.sleep(5)
        
        log.info(' Use Case 2 - Finished deleting BSV resource from open stack' )
        Report_file.add_line('Use Case 2 - Finished deleting BSV resource from open stack ')
        ShellHandler.__del__(ShellHandler)

    except Exception as e:

        log.error('Use Case 2 - Error deleting BSV resource from open stack'  + str(e))
        Report_file.add_line('Use Case 2 - Error deleting BSV resource from open stack' + str(e))
        ShellHandler.__del__(ShellHandler)
        assert False


def fetch_VM_Vapp_details_usecase2():
    log.info('wait 20 seconds for reconcile to finish')
    time.sleep(20)
    global usecase2_VM_vapp_details

    usecase2_VM_vapp_details = fetch_vapp_vm_details()


def verification_reconcile_usecase2():

    verify_reconcile_usecase2(usecase2_VM_vapp_details,usecase1_VM_vapp_details)
    
    
def create_openstack_srt():
    
    try:

        log.info(' Use Case 3 - Start creating SRT resource from open stack' )
        Report_file.add_line('Use Case 3 - Start creating SRT resource from open stack ')

        EPIS_data = ECM_PI_Initialization.get_model_objects(ECM_PI_Initialization, 'EPIS')        
        openstack_ip = EPIS_data._EPIS__openstack_ip
        username = EPIS_data._EPIS__openstack_username
        password = EPIS_data._EPIS__openstack_password
        openrc_filename = EPIS_data._EPIS__openrc_filename
                
        global openstack_flavor_name
        openstack_flavor_name = 'CM-Reconcile_SRT_OS'
        
        flavor_exists = check_flavor_exists(openrc_filename, openstack_ip, username, password, openstack_flavor_name)
        if flavor_exists:
            log.info('Flavor with name ' + openstack_flavor_name + ' already exists in cloud')
            Report_file.add_line('Flavor with name ' + openstack_flavor_name + ' already exists in cloud')
            command = 'openstack flavor list --all | grep -i {}'.format(openstack_flavor_name)
        else:
            command = 'openstack flavor create {} --ram 6144 --disk 20 --vcpus 2 --public -c id | grep -i id'.format(openstack_flavor_name)
        
        log.info('Connecting with open stack to create SRT ' +openstack_ip )
        ShellHandler.__init__(ShellHandler, openstack_ip, username, password)
        command_1 = 'source {}'.format(openrc_filename)
        stdin, stdout, stderr = ShellHandler.execute(ShellHandler, command_1)
    
        
        Report_file.add_line('command on openstack  ' + command)
        stdin, stdout, stderr = ShellHandler.execute(ShellHandler, command)
        Report_file.add_line('  openstack command output ' + str(stdout))

        for line in stdout:
            list_data = line.split('|')
            global openstack_srt_id
            if flavor_exists:
                openstack_srt_id = list_data[1].strip()
            else:   
                openstack_srt_id = list_data[2].strip()

        log.info('openstack srt id is ' + openstack_srt_id)        
        Report_file.add_line('openstack srt id is ' + openstack_srt_id)
        ShellHandler.__del__(ShellHandler)

        log.info(' Use Case 3 - Finished creating  SRT resource from open stack' )
        Report_file.add_line('Use Case 3 - Finished creatingSRT resource from open stack ')
        

    except Exception as e:

        log.error('Use Case 3 - Error creating SRT resource from open stack'  + str(e))
        Report_file.add_line('Use Case 3 - Error Creating SRT resource from open stack' + str(e))
        ShellHandler.__del__(ShellHandler)
        assert False
    

def create_openstack_block_storage():
    
    try:

        log.info(' Use Case 3 - Start creating BSV resource from open stack' )
        Report_file.add_line('Use Case 3 - Start creating BSV resource from open stack ')

        EPIS_data = ECM_PI_Initialization.get_model_objects(ECM_PI_Initialization, 'EPIS')
        
        openstack_ip = EPIS_data._EPIS__openstack_ip
        username = EPIS_data._EPIS__openstack_username
        password = EPIS_data._EPIS__openstack_password
        openrc_filename = EPIS_data._EPIS__openrc_filename
        global openstack_bsv_name
        openstack_bsv_name = Common_utilities.get_name_with_timestamp(Common_utilities, 'Reconcile_bsv_')

        log.info('Connecting with open stack to create volume ' +openstack_ip )
        ShellHandler.__init__(ShellHandler, openstack_ip, username, password)
        command = 'source {}'.format(openrc_filename)
        stdin, stdout, stderr = ShellHandler.execute(ShellHandler, command)

        command = 'openstack volume create {} --size 4 -c id | grep -i id'.format(openstack_bsv_name)
        Report_file.add_line('command to create open stack BSV  ' + command)
        stdin, stdout, stderr = ShellHandler.execute(ShellHandler, command)
        Report_file.add_line('BSV system id command output ' + str(stdout))

        for line in stdout:
            list_data = line.split('|')
            global openstack_bsv_id
            openstack_bsv_id = list_data[2].strip()        
            

        log.info('Openstack BSV id : '+openstack_bsv_id )
        Report_file.add_line('Openstack BSV system id is ' + openstack_bsv_id)

        log.info('Start verification of BSV status ')
        timeout = 180
        log.info("timeout for verification is 180 seconds , Note : it won't fail after 180 seconds ")
        command = 'openstack volume show {} -c status | grep -i status'.format(openstack_bsv_id)
        Report_file.add_line('command to verify open stack BSV  ' + command)

        while timeout !=0:
            stdin, stdout, stderr = ShellHandler.execute(ShellHandler, command)
            Report_file.add_line('command output ' + str(stdout))
            status_output = []
            for output in stdout:
                status_output = output.split('|')
                status = status_output[2].strip()

            if 'available' == status:
                log.info('Openstack BSV status is available ')
                Report_file.add_line('Openstack BSV status is available ')
                break
            else:
                log.info('Openstack BSV status is '+status)
                log.info('waiting for 10 seconds to retry ')
                timeout = timeout -10
                time.sleep(10)
        else:
            log.warning('Openstack BSV status is not available after 180 seconds , ********Usecase may Fail******* ')

        log.info(' Use Case 3 - Finished creating BSV resource from open stack' )
        Report_file.add_line('Use Case 3 - Finished creating BSV resource from open stack ')
        ShellHandler.__del__(ShellHandler)

    except Exception as e:

        log.error('Use Case 3 - Error creating BSV resource from open stack'  + str(e))
        Report_file.add_line('Use Case 3 - Error Creating BSV resource from open stack' + str(e))
        ShellHandler.__del__(ShellHandler)
        assert False
    

def register_srt_block_storage():
    
    try:
        
        log.info(' UC-3 start registering srt and bsv on ECM  ' )
        Report_file.add_line('UC-3 start registering srt and bsv on ECM  ')
    
        sit_data = SIT_initialization.get_model_objects(SIT_initialization, 'SIT')
        EPIS_data = ECM_PI_Initialization.get_model_objects(ECM_PI_Initialization, 'EPIS')
        ecm_host_data = Initialization_script.get_model_objects(Initialization_script, 'ECM_CORE')
        ecm_server_ip = ecm_host_data._Ecm_core__ECM_Host_Blade_IP
        ecm_username = ecm_host_data._Ecm_core__ECM_Host_Blade_username
        ecm_password = ecm_host_data._Ecm_core__ECM_Host_Blade_Password
        tenant_name = sit_data._SIT__tenantName        
        core_vm_ip = ecm_host_data._Ecm_core__CORE_VM_IP
        core_vm_hostname = ecm_host_data._Ecm_core__core_vm_hostname
        ecm_gui_username = ecm_host_data._Ecm_core__ecm_gui_username
        ecm_gui_password = ecm_host_data._Ecm_core__ecm_gui_password     
        vimzone_name = EPIS_data._EPIS__vimzone_name
        vdc_id = sit_data._SIT__vdc_id
        
        auth_basic = base64.b64encode(bytes(ecm_gui_username+':'+ecm_gui_password, encoding='utf-8'))        
        decoded_auth_basic = auth_basic.decode('utf-8')
        
        bsv_file = 'register_bsv.json'
        Json_file_handler.modify_attribute(Json_file_handler,r'com_ericsson_do_auto_integration_files/'+bsv_file, 'vimObjectId', openstack_bsv_id)        
        Json_file_handler.modify_attribute(Json_file_handler,r'com_ericsson_do_auto_integration_files/'+bsv_file, 'name', openstack_bsv_name)
        Json_file_handler.modify_attribute(Json_file_handler,r'com_ericsson_do_auto_integration_files/'+bsv_file, 'vimZoneName', vimzone_name)
        Json_file_handler.update_any_json_attr(Json_file_handler,r'com_ericsson_do_auto_integration_files/'+bsv_file, ['vdc'],'id', vdc_id)      
        
        connection = ServerConnection.get_connection(ecm_server_ip, ecm_username, ecm_password)
        
        log.info('transferring register bsv file to ECM : ' + bsv_file)
        #curl --insecure --request POST 'https://ieatdo9029-om-2.athtem.eei.ericsson.se/ecm_service/cmdb/bsvs' --header 'tenantid: ECM' --header 'Content-Type: application/json' --header 'Authorization: Basic ZWNtYWRtaW46Q2xvdWRBZG1pbjEyMw==' --data@
        ServerConnection.put_file_sftp(connection, r'com_ericsson_do_auto_integration_files/' + bsv_file, SIT.get_base_folder(SIT) + bsv_file)

        command = '''curl -X POST --insecure --header 'Content-Type: application/json' --header 'Accept: application/json' --header 'tenantid: {}' --header 'Authorization: Basic {}' --data @{} 'https://{}/ecm_service/cmdb/bsvs{}'''.format(tenant_name,decoded_auth_basic, bsv_file, core_vm_hostname, "'")
    
        Report_file.add_line('curl command of deployment ' + command)
    
        command_output = ExecuteCurlCommand.get_json_output(connection, command)

        command_out = ExecuteCurlCommand.get_sliced_command_output(command_output)
        output = ast.literal_eval(command_out)
        requestStatus = output['status']['reqStatus']

        if 'SUCCESS' or 'WARNING' in requestStatus:
    
            system_bsv_id = output['data']['bsv']['id']
            log.info('system_bsv_id : ' + system_bsv_id)
            Report_file.add_line('system_bsv_id : ' + system_bsv_id)
            
    
        elif 'ERROR' in requestStatus:
    
            command_error = output['status']['msgs'][0]['msgText']
    
            log.error('Error executing curl command for registering the bsv ' + command_error)
            Report_file.add_line(command_error)
            Report_file.add_line('Error executing curl command for registering the bsv')
            connection.close()
            assert False


        token = Common_utilities.authToken(Common_utilities, connection , core_vm_hostname)

        flavor_check = check_flavor_exists_in_ecm(connection, token, core_vm_hostname, tenant_name, 'Reconcile_SRT_OS')

        if flavor_check:

            log.info('Flavor {} already exists in ECM , skipping registration of SRT  '.format(openstack_flavor_name))
            Report_file.add_line('Flavor {} already exists in ECM , skipping registration of SRT  '.format(openstack_flavor_name))

        else:
            data = [{

                "vimZoneName": vimzone_name,
                "vimObjectId": openstack_srt_id,
                "name": openstack_flavor_name

            }]
            srt_file = 'register_srt.json'
            Json_file_handler.modify_attribute(Json_file_handler, r'com_ericsson_do_auto_integration_files/' + srt_file,
                                               'tenantName', tenant_name)
            Json_file_handler.modify_attribute(Json_file_handler, r'com_ericsson_do_auto_integration_files/' + srt_file,
                                               'name', openstack_flavor_name[3:])
            Json_file_handler.update_any_json_attr(Json_file_handler,
                                                   r'com_ericsson_do_auto_integration_files/' + srt_file, [], 'vimSrts',
                                                   data)

            log.info('transferring register srt file to ECM : ' + srt_file)
            ServerConnection.put_file_sftp(connection,
                                            r'com_ericsson_do_auto_integration_files/' + srt_file, SIT.get_base_folder(SIT) + srt_file)

            command = '''curl -X POST --insecure --header 'Content-Type: application/json' --header 'Accept: application/json' --header 'tenantid: {}' --header 'Authorization: Basic {}' --data @{} 'https://{}/ecm_service/cmdb/srts{}'''.format(
                tenant_name, decoded_auth_basic, srt_file, core_vm_hostname, "'")

            Report_file.add_line('curl command of deployment ' + command)

            command_output = ExecuteCurlCommand.get_json_output(connection, command)

            command_out = ExecuteCurlCommand.get_sliced_command_output(command_output)
            output = ast.literal_eval(command_out)
            requestStatus = output['status']['reqStatus']

            if 'SUCCESS' in requestStatus:

                system_srt_id = output['data']['srt']['id']
                log.info('system_srt_id : ' + system_srt_id)
                Report_file.add_line('system_srt_id : ' + system_srt_id)


            elif 'ERROR' in requestStatus:

                command_error = output['status']['msgs'][0]['msgText']

                log.error('Error executing curl command for registering the srt ' + command_error)
                Report_file.add_line(command_error)
                Report_file.add_line('Error executing curl command for registering the srt')
                connection.close()
                assert False


         
    
    except Exception as e:
        connection.close()
        log.error('Error registering srt and bsv on ECM  ' + str(e))
        Report_file.add_line('Error registering srt and bsv on ECM ' + str(e))
        assert False

    
    

def stack_update_uc3():
    
    try:
        log.info(' UC-3 start updating and running stack update file  ' )
        Report_file.add_line('UC-3 start updating and running stack update file ')
        
        stack_file_name = 'update_reconcile_stack_uc3.yaml'
                
        update_reconcile_stack_file(stack_file_name,'CM-Reconcile_SRT_OS',openstack_bsv_id,image_id,usecase_name= '3')

    
    except Exception as e:
        
        log.error(' UC-3 Error updating and running stack update ' + str(e))
        Report_file.add_line('UC-3 Error updating and running stack update ' + str(e))
        assert False


def fetch_allocated_quota_usecase3():
    global usecase3_quota_list

    usecase3_quota_list = fetch_reconcile_allocated_quota()


def fetch_VM_Vapp_details_usecase3():
    log.info('wait 20 seconds for reconcile to finish')
    time.sleep(20)
    global usecase3_VM_vapp_details

    usecase3_VM_vapp_details = fetch_vapp_vm_details()
    
    
def verification_reconcile_usecase3():
    
    verify_reconcile_usecase3(before_quota_list,usecase3_quota_list,usecase2_VM_vapp_details,usecase3_VM_vapp_details)
        
