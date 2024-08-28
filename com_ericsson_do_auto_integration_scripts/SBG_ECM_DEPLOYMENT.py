
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

log = Logger.get_logger('SBG_ECM_DEPLOYMENT.py')

package_name =''



def remove_LCM_entry():
    remove_host_lcm_entry()


def admin_heatstack_rights():
    update_admin_heatstack_rights()

def update_lcm_password():
    update_lcm_oss_password()

# method to get folder name that is named upon sbg software folder
def get_vnfd_id_sbg_nodes():    
    get_vnfd_id_ims_nodes('SBG','deploySBG')   

# new changes for IMS nodes
def transfer_sbg_software():
        
    transfer_node_software_vnflcm('SBG','deploySBG')

#Not in use after auto download from Node ARM Repo    
"""def unpack_sbg_software():
    sit_data = SIT_initialization.get_model_objects(SIT_initialization, 'SIT')
    sbg_version = sit_data._SIT__sbg_version
    hot_file = 'vsbg_template.yaml'
    unpack_node_software('SBG', sbg_version, 'SBG_Software_complete.tar', 'SBG_Software_resources.tar', hot_file)

def sbg_workflow_deployment():
    try:
        log.info('start SBG workflow bundle install on LCM')
        Report_file.add_line(Report_file, 'SBG Workflow  bundle install on LCM begins...')
        sit_data = SIT_initialization.get_model_objects(SIT_initialization, 'SIT')

        ecm_host_data = Initialization_script.get_model_objects(Initialization_script, 'ECM_CORE')
        server_ip = ecm_host_data._Ecm_core__VNF_LCM_Servicedb_IP
        username = ecm_host_data._Ecm_core__VNF_LCM_Servicedb_Username
        password = ecm_host_data._Ecm_core__VNF_LCM_Servicedb_Password
        sbg_software_path = r'/var/tmp/' + sit_data._SIT__sbg_version

        connection = Server_connection.get_connection(Server_connection, server_ip, username, password)

        command = 'cd ' + sbg_software_path +' ;ls -ltr | grep -i .rpm'
        stdin, stdout, stderr = connection.exec_command(command)
        command_output = str(stdout.read())
        output = command_output.split()
        rpm_name = output[-1][:-3]
        log.info('rpm name :' + rpm_name)
        log.info('command output  : ' + command_output)

        log.info('Starting Install of LCM Workflow using rpm bundle')
        Report_file.add_line(Report_file, 'Starting Install of LCM Workflow using rpm bundle downloaded')

        command = 'sudo -i wfmgr bundle install --package={}/{}'.format(sbg_software_path, rpm_name)
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
        log.info('Error SBG workflow bundle install on LCM '+str(e))
        Report_file.add_line(Report_file, 'Error SBG workflow bundle install on LCM '+str(e))
        assert False

def sbg_so_files_transfer():
    sit_data = SIT_initialization.get_model_objects(SIT_initialization, 'SIT')
    sbg_software_path = sit_data._SIT__sbg_software_path
    so_files_transfer(sbg_software_path)"""

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
        ServerConnection.get_file_sftp(connection, r'/vnflcm-ext/current/vnf_package_repo/' + vnfd_id + '/Resources/VnfdWrapperFiles/VNFD_Wrapper.json', r'com_ericsson_do_auto_integration_files/VNFD_Wrapper_SBG.json')
        
        file_name = 'VNFD_Wrapper_SBG.json' 
        command = 'sudo -i cat /home/jboss_user/.ssh/id_rsa.pub' 
        log.info(command)
        stdin, stdout, stderr = connection.exec_command(command, get_pty = True)
        command_output = str(stdout.read())        
        key = command_output[2:-5:1]
        log.info('updating the VNFD_Wrapper.json with id_rsa.pub key ' +key)
        Json_file_handler.update_any_json_attr(Json_file_handler,r'com_ericsson_do_auto_integration_files/'+file_name,['instantiateVnfOpConfig'],'admin_authorized_key',key)        
        ServerConnection.put_file_sftp(connection, r'com_ericsson_do_auto_integration_files/' + file_name, r'/home/cloud-user/VNFD_Wrapper.json')
        command = 'sudo -i cp /home/cloud-user/VNFD_Wrapper.json /vnflcm-ext/current/vnf_package_repo/'+vnfd_id+'/Resources/VnfdWrapperFiles/VNFD_Wrapper.json' 
        log.info('Putting back the VNFD_Wrapper.json after updating the admin_authorized_key '+command)
        stdin, stdout, stderr = connection.exec_command(command, get_pty = True)
        time.sleep(2)    
        connection.close()
        
    except Exception as e:
        connection.close()
        log.error('Error SBG ssh-key generation '+str(e))
        Report_file.add_line('Error SBG ssh-key generation ' + str(e))
        assert False


"""def create_sbg_flavours():

    log.info('start creating sbg flavors')
    Report_file.add_line(Report_file, 'start creating sbg flavors')

    EPIS_data = ECM_PI_Initialization.get_model_objects(ECM_PI_Initialization, 'EPIS')
    openstack_ip = EPIS_data._EPIS__openstack_ip
    username = EPIS_data._EPIS__openstack_username
    password = EPIS_data._EPIS__openstack_password
    openrc_filename = EPIS_data._EPIS__openrc_filename
    sit_data = SIT_initialization.get_model_objects(SIT_initialization, 'SIT')
    tenant_name = sit_data._SIT__tenantName
    sbg_flavors = sit_data._SIT__sbg_flavors
    flavors_list = sbg_flavors.split(',')
    for flavor_name in flavors_list:

        flavor_exists = check_flavor_exists(openrc_filename,openstack_ip,username,password,flavor_name)
        if flavor_exists:
            log.info('Flavor with name '+flavor_name+ ' already exists in CEE')
            Report_file.add_line(Report_file, 'Flavor with name '+flavor_name+ ' already exists in CEE')
        else:
            log.info('Flavor with name ' + flavor_name + ' does not  exists in CEE')
            Report_file.add_line(Report_file, 'Flavor with name ' + flavor_name + ' does not  exists in CEE')
            name = flavor_name[3:]
            if 'vSBG-4-0-2' in name:
                update_any_flavor_file(name,2,4096,0,tenant_name)                               
            else:
                log.warn('Flavor name does not match with requirements , please check the confluence for SBG deployment '+flavor_name)
                Report_file.add_line(Report_file, 'Flavor name does not match with requirements , please check the confluence for SBG deployment '+flavor_name)
                assert False

            update_transfer_flavour_file()
            create_flavour('flavour.json','flavour_transfer.json',name)

    log.info('Finished creating sbg flavors')
    Report_file.add_line(Report_file, 'Finished creating sbg flavors')

def register_sbg_images():
    try:

        log.info('start register sbg images')
        Report_file.add_line(Report_file, 'start register sbg images')
        sit_data = SIT_initialization.get_model_objects(SIT_initialization, 'SIT')
        ecm_host_data = Initialization_script.get_model_objects(Initialization_script, 'ECM_CORE')
        ecm_server_ip = ecm_host_data._Ecm_core__ECM_Host_Blade_IP
        ecm_username = ecm_host_data._Ecm_core__ECM_Host_Blade_username
        ecm_password = ecm_host_data._Ecm_core__ECM_Host_Blade_Password
        core_vm_ip = ecm_host_data._Ecm_core__CORE_VM_IP
        vimzone_name = sit_data._SIT__vimzone_name
        sbg_image_names = sit_data._SIT__sbg_image_names
        sbg_image_ids = sit_data._SIT__sbg_image_ids
        image_names = sbg_image_names.split(',')
        image_ids = sbg_image_ids.split(',')
        
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
        

        log.info('Finished register sbg images')
        Report_file.add_line(Report_file, 'Finished register sbg images')
        connection.close()
    except Exception as e:
        connection.close()
        log.error('Error register sbg images '+str(e))
        Report_file.add_line(Report_file, 'Error register sbg images '+str(e))
        assert False
"""
def update_sbg_node_onboard_file():
    log.info('Connecting with VNF-LCM server')
    ecm_host_data = Initialization_script.get_model_objects(Initialization_script, 'ECM_CORE')
    sit_data = SIT_initialization.get_model_objects(SIT_initialization, 'SIT')
    server_ip = ecm_host_data._Ecm_core__VNF_LCM_Servicedb_IP
    username = ecm_host_data._Ecm_core__VNF_LCM_Servicedb_Username
    password = ecm_host_data._Ecm_core__VNF_LCM_Servicedb_Password
    connection = ServerConnection.get_connection(server_ip, username, password)
    
    path = '/var/tmp/deploySBG/'
    vnfd_id = sit_data._SIT__ims_vnfd_id
    
    ecm_zip_pacakge = path + vnfd_id +'.zip'
    #code change at this place  
    
    try:
        log.info('Getting VNFD_Wrapper_SBG.json from server to get onboard params')
        Report_file.add_line('Getting VNFD_Wrapper_SBG.json from server to get onboard params')
        ServerConnection.get_file_sftp(connection, r'/vnflcm-ext/current/vnf_package_repo/' + vnfd_id + '/Resources/VnfdWrapperFiles/VNFD_Wrapper.json', r'com_ericsson_do_auto_integration_files/VNFD_Wrapper_SBG.json')
        
        connection.close()
    except Exception as e:
        log.error('Error while getting the VNFD_Wrapper_SBG.json from server '+str(e))

    file_data = Json_file_handler.get_json_data(Json_file_handler,r'com_ericsson_do_auto_integration_files/VNFD_Wrapper_SBG.json')
    global package_name
    package_name = Common_utilities.get_name_with_timestamp(Common_utilities,'TEST_SBG_PACKAGE_UPLOAD')  
    sit_data._SIT__name = package_name
    log.info('SBG ONBOARD PACKAGE NAME '+package_name)
    Report_file.add_line('SBG ONBOARD PACKAGE NAME ' + package_name)
    
    onboard_file_name ='onboard_sbg.json'
    upload_file = vnfd_id +'.zip'
    update_sbg_onboard_file(r'com_ericsson_do_auto_integration_files/'+onboard_file_name,file_data,package_name)

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

def onboard_sbg_package():
    sit_data = SIT_initialization.get_model_objects(SIT_initialization, 'SIT')
    vnfd_id = sit_data._SIT__ims_vnfd_id
    upload_file = vnfd_id +'.zip'
    onboard_node_package('onboard_sbg.json',upload_file,package_name)

def verify_sbg_package():
    log.info('start verifying the onboarded sbg package')
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

def update_sbg_node_deploy_file():
    sit_data = SIT_initialization.get_model_objects(SIT_initialization, 'SIT')
    ecm_host_data = Initialization_script.get_model_objects(Initialization_script, 'ECM_CORE')
    node_version = sit_data._SIT__ims_vnfd_id
    node_name = node_version+'_' + str(random.randint(0, 999))
    node_name = node_name.replace('.','_')
    file_name ='deploy_sbg.json'

    ecm_server_ip = ecm_host_data._Ecm_core__ECM_Host_Blade_IP
    ecm_username = ecm_host_data._Ecm_core__ECM_Host_Blade_username
    ecm_password = ecm_host_data._Ecm_core__ECM_Host_Blade_Password
    connection = ServerConnection.get_connection(ecm_server_ip, ecm_username, ecm_password)
    
    file_data = Json_file_handler.get_json_data(Json_file_handler,r'com_ericsson_do_auto_integration_files/VNFD_Wrapper_SBG.json')
    update_sbg_deploy_file(r'com_ericsson_do_auto_integration_files/'+file_name,file_data,node_name)
    ServerConnection.put_file_sftp(connection, r'com_ericsson_do_auto_integration_files/' + file_name,
                                   SIT.get_base_folder(SIT) + file_name)
    log.info('Going to start deployment of node '+node_name)
    connection.close()


def deploy_sbg_package():

    deploy_node('deploy_sbg.json')

def verify_sbg_deployment():
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
        
        #file_data = Json_file_handler.get_json_data(Json_file_handler,r'com_ericsson_do_auto_integration_files/VNFD_Wrapper_SBG.json')
        #OM_IP = file_data['instantiateVnfOpConfig']['OM_ip_address']
        
        
        #ping_response = get_ping_response(connection, OM_IP)
    
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
