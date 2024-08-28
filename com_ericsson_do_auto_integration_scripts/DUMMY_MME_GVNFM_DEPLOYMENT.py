from com_ericsson_do_auto_integration_utilities.Logger import Logger
from com_ericsson_do_auto_integration_utilities.Report_file import Report_file
from com_ericsson_do_auto_integration_scripts.ECM_NODE_DEPLOYMENT import *
from com_ericsson_do_auto_integration_scripts.CEE_Cleanup import *
from com_ericsson_do_auto_integration_utilities.EPIS_files_update import *
from com_ericsson_do_auto_integration_scripts.ECM_POST_INSTALLATION import *
from com_ericsson_do_auto_integration_utilities.Common_utilities import Common_utilities
from com_ericsson_do_auto_integration_utilities.SIT_files_update import *
from com_ericsson_do_auto_integration_scripts.VERIFY_NODE_DEPLOYMENT import *
from com_ericsson_do_auto_integration_scripts.VCISCO_DEPLOY import *




log = Logger.get_logger('DUMMY_MME_GVNFM_DEPLOYMENT.py')

package_name = ''
flavor_name = ''
image_id = ''
def create_dummy_mme_flavors():
    try:
        log.info('start creating dummy MME flavor')
        Report_file.add_line('start creating dummy MME flavor')

        EPIS_data = ECM_PI_Initialization.get_model_objects(ECM_PI_Initialization, 'EPIS')
        openstack_ip = EPIS_data._EPIS__openstack_ip
        username = EPIS_data._EPIS__openstack_username
        password = EPIS_data._EPIS__openstack_password
        openrc_filename = EPIS_data._EPIS__openrc_filename
        sit_data = SIT_initialization.get_model_objects(SIT_initialization, 'SIT')
        tenant_name = sit_data._SIT__tenantName
        global flavor_name
        flavor_name = Json_file_handler.get_any_attribute_yaml_value(Json_file_handler,r'com_ericsson_do_auto_integration_files/ECDE_HOT-MME-DUMMY-VNF.yaml',['parameters','gpb_flavor'],'default')

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


def create_dummy_mme_image():
    try:

        log.info('start register dummy mme images')
        Report_file.add_line('start register dummy mme images')
        sit_data = SIT_initialization.get_model_objects(SIT_initialization, 'SIT')
        ecm_host_data = Initialization_script.get_model_objects(Initialization_script, 'ECM_CORE')
        ecm_server_ip = ecm_host_data._Ecm_core__ECM_Host_Blade_IP
        ecm_username = ecm_host_data._Ecm_core__ECM_Host_Blade_username
        ecm_password = ecm_host_data._Ecm_core__ECM_Host_Blade_Password
        core_vm_ip = ecm_host_data._Ecm_core__CORE_VM_IP
        core_vm_hostname = ecm_host_data._Ecm_core__core_vm_hostname

        vimzone_name = sit_data._SIT__vimzone_name
        software_path = sit_data._SIT__dummy_mme_path

        connection = ServerConnection.get_connection(ecm_server_ip, ecm_username, ecm_password)


        ServerConnection.get_file_sftp(connection, software_path + '/ECDE_HOT-MME-DUMMY-VNF.yaml', r'com_ericsson_do_auto_integration_files/ECDE_HOT-MME-DUMMY-VNF.yaml')
        global image_id
        image_name = Json_file_handler.get_any_attribute_yaml_value(Json_file_handler,r'com_ericsson_do_auto_integration_files/ECDE_HOT-MME-DUMMY-VNF.yaml', ['parameters','gpb_image_id'], 'description')
        image_id = Json_file_handler.get_any_attribute_yaml_value(Json_file_handler,r'com_ericsson_do_auto_integration_files/ECDE_HOT-MME-DUMMY-VNF.yaml', ['parameters','gpb_image_id'], 'default')

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
        connection.close()
    except Exception as e:
        connection.close()
        log.error('Error register mme images ' + str(e))
        Report_file.add_line('Error register mme images ' + str(e))
        assert False


def onboard_dummy_mme_ovf():
    ovf_package = 'ECDE_mme_networks_vlan.ovf'
    sit_data = SIT_initialization.get_model_objects(SIT_initialization, 'SIT')
    package_dir = sit_data._SIT__dummy_mme_path
    onboard_generic_ovf_package(ovf_package, package_dir)



def deploy_dummy_mme_ovf():
    file_name = r'deploy_dummy_mme_ovf.json'
    deploy_generic_ovf_package(file_name)

def onboard_dummy_mme_package():

    global package_name
    sit_data = SIT_initialization.get_model_objects(SIT_initialization, 'SIT')
    software_path = sit_data._SIT__dummy_mme_path
    package_name = Common_utilities.get_name_with_timestamp(Common_utilities, 'ECDE_HOT-MME-DUMMY-VNF') 
    upload_file = 'ECDE_HOT-MME-DUMMY-VNF.zip'
    onboard_node_hot_package(package_name, upload_file,software_path)

def deploy_dummy_mme_package():

    update_dummy_mme_deploy_file('deploy_dummy_mme_package.json',package_name,flavor_name,image_id)
    deploy_node_hot_package('deploy_dummy_mme_package.json')



def verify_dummy_mme_deployment():
    try:
        log.info('waiting 30 seconds to verification of node')
        time.sleep(30)
        sit_data = SIT_initialization.get_model_objects(SIT_initialization, 'SIT')
        ecm_host_data = Initialization_script.get_model_objects(Initialization_script, 'ECM_CORE')
        ecm_server_ip = ecm_host_data._Ecm_core__ECM_Host_Blade_IP
        ecm_username = ecm_host_data._Ecm_core__ECM_Host_Blade_username
        ecm_password = ecm_host_data._Ecm_core__ECM_Host_Blade_Password

        core_vm_ip = ecm_host_data._Ecm_core__CORE_VM_IP
        core_vm_hostname = ecm_host_data._Ecm_core__core_vm_hostname

        node_id = sit_data._SIT__vapp_Id
        connection = ServerConnection.get_connection(ecm_server_ip, ecm_username, ecm_password)
        token = Common_utilities.authToken(Common_utilities, connection, core_vm_ip)


        provisioningStatus, operationalState = get_node_status(connection, token, core_vm_hostname, node_id)

        if 'ACTIVE' == provisioningStatus:

            Report_file.add_line('provisioningStatus is : ' + provisioningStatus)
            Report_file.add_line('operationalState is : ' + operationalState)
            log.info('Verification of package deployment is success')
            Report_file.add_line('Verification of package deployment is successful')
            connection.close()

        else:
            log.error('Verification of package deployment failed. Please check the status of provisioning ')
            Report_file.add_line('Verification of package deployment failed. Please check the status of provisioning ')
            connection.close()
            assert False


    except Exception as e:
        connection.close()
        log.error('Error verifying node deployment ' + str(e))
        Report_file.add_line('Error verifying node deployment ' + str(e))
        assert False