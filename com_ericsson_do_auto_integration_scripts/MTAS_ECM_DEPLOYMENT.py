
from com_ericsson_do_auto_integration_utilities.Report_file import Report_file
from com_ericsson_do_auto_integration_utilities.Logger import Logger
from com_ericsson_do_auto_integration_scripts.CEE_Cleanup import *
from com_ericsson_do_auto_integration_initilization.ECM_PI_initialization import ECM_PI_Initialization
from com_ericsson_do_auto_integration_utilities.EPIS_files_update import *
from com_ericsson_do_auto_integration_initilization.Initialization_script import Initialization_script
from com_ericsson_do_auto_integration_scripts.ECM_POST_INSTALLATION import *
from com_ericsson_do_auto_integration_scripts.ECM_NODE_DEPLOYMENT import *
from com_ericsson_do_auto_integration_utilities.SIT_files_update import *
from com_ericsson_do_auto_integration_scripts.VERIFY_NODE_DEPLOYMENT import *
from com_ericsson_do_auto_integration_initilization.SIT_initialization import SIT_initialization
from com_ericsson_do_auto_integration_scripts.SO_NODE_DEPLOYMENT import *
import random

log = Logger.get_logger('MTAS_ECM_DEPLOYMENT.py')

package_name =''



def remove_LCM_entry():
    remove_host_lcm_entry()


def admin_heatstack_rights():
    update_admin_heatstack_rights()

def update_lcm_password():
    update_lcm_oss_password()


# method to get folder name that is named upon mtas software folder
def get_vnfd_id_mtas_nodes():    
    get_vnfd_id_ims_nodes('MTAS','deployMTAS')   


# new changes for IMS nodes
def transfer_mtas_software():
    
    transfer_node_software_vnflcm('MTAS','deployMTAS')

#Not in use after auto download from Node ARM Repo
"""def unpack_mtas_software():
    sit_data = SIT_initialization.get_model_objects(SIT_initialization, 'SIT')
    mtas_version = sit_data._SIT__mtas_version
    hot_file = 'mtas_hot.yaml'
    unpack_node_software('MTAS', mtas_version, 'MTAS_Software_complete.tar', 'MTAS_Software_resources.tar', hot_file)

def mtas_workflow_deployment():
    try:
        log.info('start MTAS workflow bundle install on LCM')
        Report_file.add_line(Report_file, 'MTAS Workflow  bundle install on LCM begins...')
        sit_data = SIT_initialization.get_model_objects(SIT_initialization, 'SIT')

        ecm_host_data = Initialization_script.get_model_objects(Initialization_script, 'ECM_CORE')
        server_ip = ecm_host_data._Ecm_core__VNF_LCM_Servicedb_IP
        username = ecm_host_data._Ecm_core__VNF_LCM_Servicedb_Username
        password = ecm_host_data._Ecm_core__VNF_LCM_Servicedb_Password
        mtas_software_path = r'/var/tmp/' + sit_data._SIT__mtas_version

        connection = Server_connection.get_connection(Server_connection, server_ip, username, password)

        command = 'cd ' + mtas_software_path +' ;ls -ltr | grep -i .rpm'
        stdin, stdout, stderr = connection.exec_command(command)
        command_output = str(stdout.read())
        output = command_output.split()
        rpm_name = output[-1][:-3]
        log.info('rpm name :' + rpm_name)
        log.info('command output  : ' + command_output)

        log.info('Starting Install of LCM Workflow using rpm bundle')
        Report_file.add_line(Report_file, 'Starting Install of LCM Workflow using rpm bundle downloaded')

        command = 'sudo -i wfmgr bundle install --package={}/{}'.format(mtas_software_path, rpm_name)
        stdin, stdout, stderr = connection.exec_command(command, get_pty=True)
        command_output = str(stdout.read())
        log.info(command_output)
    
        if 'already installed' in command_output:
            log.info('LCM Workflow already installed')
        
        else:
            log.info('waiting for bundle to install ')
            time.sleep(120)
            log.info('LCM workflow deploy is finished using command:' + command)
            Report_file.add_line(Report_file, 'LCM workflow deploy is completed.')

        connection.close()
    except Exception as e:
        connection.close()
        log.error('Error MTAS workflow bundle install on LCM '+str(e))
        Report_file.add_line(Report_file, 'Error MTAS workflow bundle install on LCM '+str(e))
        assert False

def mtas_so_files_transfer():
    sit_data = SIT_initialization.get_model_objects(SIT_initialization, 'SIT')
    mtas_software_path = sit_data._SIT__mtas_software_path
    so_files_transfer(mtas_software_path)"""

def generate_ssh_key():
    
    try:
        
        ssh_key_generate_on_lcm("")
        
                        
        ecm_host_data = Initialization_script.get_model_objects(Initialization_script, 'ECM_CORE')
        sit_data = SIT_initialization.get_model_objects(SIT_initialization, 'SIT')
        server_ip = ecm_host_data._Ecm_core__VNF_LCM_Servicedb_IP
        username = ecm_host_data._Ecm_core__VNF_LCM_Servicedb_Username
        password = ecm_host_data._Ecm_core__VNF_LCM_Servicedb_Password
        connection = ServerConnection.get_connection(server_ip, username, password)
        vnfd_id = sit_data._SIT__ims_vnfd_id
        ServerConnection.get_file_sftp(connection, r'/vnflcm-ext/current/vnf_package_repo/' + vnfd_id + '/Resources/VnfdWrapperFiles/VNFD_Wrapper.json', r'com_ericsson_do_auto_integration_files/VNFD_Wrapper_MTAS.json')
        file = 'com_ericsson_do_auto_integration_files/VNFD_Wrapper_MTAS.json'        
        workflow_config_dir = Json_file_handler.get_any_json_attr(Json_file_handler,file,['instantiateVnfOpConfig'],'workflow_config_dir')               
        path = workflow_config_dir[7:]
        log.info(path)        
        ssh_key_dir(connection,vnfd_id,path)        
    
    except Exception as e:
        connection.close()
        log.error('Error MTAS ssh-key generation '+str(e))
        Report_file.add_line('Error MTAS ssh-key generation ' + str(e))
        assert False
    

"""def create_mtas_flavours():

    log.info('start creating mtas flavors')
    Report_file.add_line(Report_file, 'start creating mtas flavors')

    EPIS_data = ECM_PI_Initialization.get_model_objects(ECM_PI_Initialization, 'EPIS')
    openstack_ip = EPIS_data._EPIS__openstack_ip
    username = EPIS_data._EPIS__openstack_username
    password = EPIS_data._EPIS__openstack_password
    openrc_filename = EPIS_data._EPIS__openrc_filename
    sit_data = SIT_initialization.get_model_objects(SIT_initialization, 'SIT')
    tenant_name = sit_data._SIT__tenantName
    mtas_flavors = sit_data._SIT__mtas_flavors
    flavors_list = mtas_flavors.split(',')
    for flavor_name in flavors_list:

        flavor_exists = check_flavor_exists(openrc_filename,openstack_ip,username,password,flavor_name)
        if flavor_exists:
            log.info('Flavor with name '+flavor_name+ ' already exists in CEE')
            Report_file.add_line(Report_file, 'Flavor with name '+flavor_name+ ' already exists in CEE')
        else:
            log.info('Flavor with name ' + flavor_name + ' does not  exists in CEE')
            Report_file.add_line(Report_file, 'Flavor with name ' + flavor_name + ' does not  exists in CEE')
            name = flavor_name[3:]
            if '_SC' in name:
                #cpu,memory,disk_size                
                update_any_flavor_file(name,4,29696,0,tenant_name,True,200)           
            elif '_PL' in name:
                update_any_flavor_file(name,4,29696,0,tenant_name)                               
            
            else:
                log.info('Creating Common Flavor with ephemeral_disk_size as 50')
                update_any_flavor_file(name,4,29696,0,tenant_name,True,50)                
            
            update_transfer_flavour_file()
            create_flavour('flavour.json','flavour_transfer.json',name)  
                
    log.info('Finished creating mtas flavors')
    Report_file.add_line(Report_file, 'Finished creating mtas flavors')

def register_mtas_images():
    try:

        log.info('start register mtas images')
        Report_file.add_line(Report_file, 'start register mtas images')
        sit_data = SIT_initialization.get_model_objects(SIT_initialization, 'SIT')
        ecm_host_data = Initialization_script.get_model_objects(Initialization_script, 'ECM_CORE')
        ecm_server_ip = ecm_host_data._Ecm_core__ECM_Host_Blade_IP
        ecm_username = ecm_host_data._Ecm_core__ECM_Host_Blade_username
        ecm_password = ecm_host_data._Ecm_core__ECM_Host_Blade_Password
        core_vm_ip = ecm_host_data._Ecm_core__CORE_VM_IP
        vimzone_name = sit_data._SIT__vimzone_name
        mtas_image_names = sit_data._SIT__mtas_image_names
        mtas_image_ids = sit_data._SIT__mtas_image_ids
        image_names = mtas_image_names.split(',')
        image_ids = mtas_image_ids.split(',')
        
        for image_name,image_id in zip(image_names,image_ids):
            connection = Server_connection.get_connection(Server_connection, ecm_server_ip, ecm_username, ecm_password)
            token = Common_utilities.authToken(Common_utilities, connection, core_vm_ip)
            image_exists = check_image_registered(connection,image_name,token,core_vm_ip)
            if image_exists:
                Report_file.add_line(Report_file, 'Image with name '+image_name+ ' already registered in cloud manager')
            else:
                log.info('Going to register image with name ' +image_name)
                update_image_file('RegisterImage.json',image_name,vimzone_name,image_id)
                image_registration('RegisterImage.json')
        

        log.info('Finished register mtas images')
        Report_file.add_line(Report_file, 'Finished register mtas images')
        connection.close()
    except Exception as e:
        connection.close()
        log.error('Error register mtas images '+str(e))
        Report_file.add_line(Report_file, 'Error register mtas images '+str(e))
        assert False
"""
def update_mtas_node_onboard_file():
    log.info('Connecting with VNF-LCM server')
    ecm_host_data = Initialization_script.get_model_objects(Initialization_script, 'ECM_CORE')
    sit_data = SIT_initialization.get_model_objects(SIT_initialization, 'SIT')
    server_ip = ecm_host_data._Ecm_core__VNF_LCM_Servicedb_IP
    username = ecm_host_data._Ecm_core__VNF_LCM_Servicedb_Username
    password = ecm_host_data._Ecm_core__VNF_LCM_Servicedb_Password
    connection = ServerConnection.get_connection(server_ip, username, password)
        
    path = '/var/tmp/deployMTAS/'
    vnfd_id = sit_data._SIT__ims_vnfd_id
    
    ecm_zip_pacakge = path + vnfd_id +'.zip'
    
    try:
        log.info('Getting VNFD_Wrapper.json from server to get onboard params')
        Report_file.add_line('Getting VNFD_Wrapper.json from server to get onboard params')
        ServerConnection.get_file_sftp(connection, r'/vnflcm-ext/current/vnf_package_repo/' + vnfd_id + '/Resources/VnfdWrapperFiles/VNFD_Wrapper.json', r'com_ericsson_do_auto_integration_files/VNFD_Wrapper_MTAS.json')
        
        connection.close()
    except Exception as e:
        log.error('Error while getting the VNFD_Wrapper.json from server '+str(e))

    file_data = Json_file_handler.get_json_data(Json_file_handler,r'com_ericsson_do_auto_integration_files/VNFD_Wrapper_MTAS.json')
    global package_name 
    package_name = Common_utilities.get_name_with_timestamp(Common_utilities, 'TEST_MTAS_PACKAGE_UPLOAD')   
    sit_data._SIT__name = package_name
    log.info('MTAS ONBOARD PACKAGE NAME '+package_name)
    Report_file.add_line('MTAS ONBOARD PACKAGE NAME ' + package_name)
    onboard_file_name ='onboard_mtas.json'
    upload_file = vnfd_id +'.zip'
    update_mtas_onboard_file(r'com_ericsson_do_auto_integration_files/'+onboard_file_name,file_data,package_name)

    ecm_server_ip = ecm_host_data._Ecm_core__ECM_Host_Blade_IP
    ecm_username = ecm_host_data._Ecm_core__ECM_Host_Blade_username
    ecm_password = ecm_host_data._Ecm_core__ECM_Host_Blade_Password
    connection = ServerConnection.get_connection(ecm_server_ip, ecm_username, ecm_password)
    
    ServerConnection.get_file_sftp(connection, ecm_zip_pacakge, r'com_ericsson_do_auto_integration_files/' + upload_file)
    
    ServerConnection.put_file_sftp(connection, r'com_ericsson_do_auto_integration_files/' + onboard_file_name,
                                   SIT.get_base_folder(SIT) + onboard_file_name)
    ServerConnection.put_file_sftp(connection, r'com_ericsson_do_auto_integration_files/' + upload_file,
                                   SIT.get_base_folder(SIT) + upload_file)
    connection.close()

def onboard_mtas_package():
    
    sit_data = SIT_initialization.get_model_objects(SIT_initialization, 'SIT')
    vnfd_id = sit_data._SIT__ims_vnfd_id
    upload_file = vnfd_id +'.zip'
    
    onboard_node_package('onboard_mtas.json',upload_file,package_name)

def verify_mtas_package():
    log.info('start verifying the onboarded mtas package')
    sit_data = SIT_initialization.get_model_objects(SIT_initialization, 'SIT')
    ecm_host_data = Initialization_script.get_model_objects(Initialization_script, 'ECM_CORE')
    ecm_server_ip = ecm_host_data._Ecm_core__ECM_Host_Blade_IP
    ecm_username = ecm_host_data._Ecm_core__ECM_Host_Blade_username
    ecm_password = ecm_host_data._Ecm_core__ECM_Host_Blade_Password

    core_vm_ip = ecm_host_data._Ecm_core__CORE_VM_IP
    core_vm_hostname = ecm_host_data._Ecm_core__core_vm_hostname
    vnf_packageId = sit_data._SIT__vnf_packageId
    connection = ServerConnection.get_connection(ecm_server_ip, ecm_username, ecm_password)
    token = Common_utilities.authToken(Common_utilities, connection, core_vm_hostname)

    provisioningStatus, operationalState = get_package_status(connection, token, core_vm_hostname, vnf_packageId)

    if 'ACTIVE' in provisioningStatus and 'ENABLED' in operationalState:

        Report_file.add_line('provisioningStatus is : ' + provisioningStatus)
        Report_file.add_line('operationalState is : ' + operationalState)
        log.info('Verification of package uploaded is success')
        Report_file.add_line('Verification of package Upload is success')
        log.info('Finished onboarding package for ' + package_name)
        Report_file.add_line('Finished onboarding package for ' + package_name)
        connection.close()
    else:

        log.error('Verification of package uploaded failed. Please check the status of provisioning and operationalState  ')
        log.error('provisioningStatus : ' + provisioningStatus + ' operationalState : ' + operationalState)
        Report_file.add_line('Verification of package uploaded failed. Please check the status of provisioning and operationalState')
        connection.close()
        assert False

def update_mtas_node_deploy_file():
    sit_data = SIT_initialization.get_model_objects(SIT_initialization, 'SIT')
    ecm_host_data = Initialization_script.get_model_objects(Initialization_script, 'ECM_CORE')
    vnfd_id = sit_data._SIT__ims_vnfd_id
    node_name = vnfd_id+'_' + str(random.randint(0, 999))
    node_name = node_name.replace('.','_')
    file_name ='deploy_mtas.json'

    ecm_server_ip = ecm_host_data._Ecm_core__ECM_Host_Blade_IP
    ecm_username = ecm_host_data._Ecm_core__ECM_Host_Blade_username
    ecm_password = ecm_host_data._Ecm_core__ECM_Host_Blade_Password
    connection = ServerConnection.get_connection(ecm_server_ip, ecm_username, ecm_password)
    
    file_data = Json_file_handler.get_json_data(Json_file_handler,r'com_ericsson_do_auto_integration_files/VNFD_Wrapper_MTAS.json')
    update_mtas_deploy_file(r'com_ericsson_do_auto_integration_files/'+file_name,file_data,node_name)    
    ServerConnection.put_file_sftp(connection, r'com_ericsson_do_auto_integration_files/' + file_name,
                                   SIT.get_base_folder(SIT) + file_name)
    log.info('Going to start deployment of node '+node_name)
    connection.close()


def deploy_mtas_package():

    deploy_node('deploy_mtas.json')

def verify_mtas_deployment():
    try:

        log.info('waiting 60 seconds to verification of node')
        time.sleep(60)
        sit_data = SIT_initialization.get_model_objects(SIT_initialization, 'SIT')
        ecm_host_data = Initialization_script.get_model_objects(Initialization_script, 'ECM_CORE')
        ecm_server_ip = ecm_host_data._Ecm_core__ECM_Host_Blade_IP
        ecm_username = ecm_host_data._Ecm_core__ECM_Host_Blade_username
        ecm_password = ecm_host_data._Ecm_core__ECM_Host_Blade_Password
    
        core_vm_ip = ecm_host_data._Ecm_core__CORE_VM_IP
        core_vm_hostname = ecm_host_data._Ecm_core__core_vm_hostname
        node_id = sit_data._SIT__vapp_Id
        connection = ServerConnection.get_connection(ecm_server_ip, ecm_username, ecm_password)
        token = Common_utilities.authToken(Common_utilities, connection, core_vm_hostname)
        
        #file_data = Json_file_handler.get_json_data(Json_file_handler,r'com_ericsson_do_auto_integration_files/VNFD_Wrapper_MTAS.json')
        #OM_IP = file_data['instantiateVnfOpConfig']['OM_IPv4_address']
        #SC1_IP = file_data['instantiateVnfOpConfig']['SC-1_IPv4_address']
        #SC2_IP = file_data['instantiateVnfOpConfig']['SC-2_IPv4_address']
        
        #ping_response1 = get_ping_response(connection, OM_IP)
        #ping_response2= get_ping_response(connection, SC1_IP)
        #ping_response3 = get_ping_response(connection, SC2_IP)
        
        #log.info('ping response for IP '+OM_IP+'  is : '+ping_response1)
        #log.info('ping response for IP '+SC1_IP+'  is : '+ping_response2)
        #log.info('ping response for IP '+SC2_IP+'  is : '+ping_response3)

        
                
        #ping_response = ping_response1 and ping_response2 and ping_response3
    
        provisioningStatus, operationalState = get_node_status(connection,token,core_vm_hostname,node_id)
    
        if 'ACTIVE' == provisioningStatus and 'INSTANTIATED' == operationalState:
    
    
            #log.info('Ping Successful')
            Report_file.add_line('provisioningStatus is : ' + provisioningStatus)
            Report_file.add_line('operationalState is : ' + operationalState)
            #Report_file.add_line(Report_file, 'Ping Successful')
            log.info('Verification of package deployment is success')
            Report_file.add_line('Verification of package deployment is successful')
            connection.close()
    
        else:
            log.info('Verification of package deployment failed. Please check the status of provisioning and operationalState and ping response ')
            Report_file.add_line('Verification of package deployment failed. Please check the status of provisioning and operationalState and ping response')
            connection.close()
            assert False


    except Exception as e:
        connection.close()
        log.error('Error verifying node deployment '+str(e))
        Report_file.add_line('Error verifying node deployment ' + str(e))
        assert False