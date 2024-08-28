from com_ericsson_do_auto_integration_utilities.Report_file import Report_file
from com_ericsson_do_auto_integration_utilities.Logger import Logger
from com_ericsson_do_auto_integration_initilization.SIT_initialization import SIT_initialization
from com_ericsson_do_auto_integration_initilization.ECM_PI_initialization import ECM_PI_Initialization
from com_ericsson_do_auto_integration_utilities.EPIS_files_update import *
from com_ericsson_do_auto_integration_scripts.ECM_POST_INSTALLATION import *
from com_ericsson_do_auto_integration_scripts.ECM_NODE_DEPLOYMENT import *
from com_ericsson_do_auto_integration_utilities.SIT_files_update import *
from com_ericsson_do_auto_integration_scripts.VERIFY_NODE_DEPLOYMENT import *
from com_ericsson_do_auto_integration_scripts.LCM_POST_INSTALLATION import *
from com_ericsson_do_auto_integration_scripts.TOSCA_BGF_ECM_DEPLOYMENT import *
from com_ericsson_do_auto_integration_scripts.DUMMY_TOSCA_PRETOSCA_WORKFLOW import *
from com_ericsson_do_auto_integration_scripts.CEE_Cleanup import *
from com_ericsson_do_auto_integration_utilities.Server_details import Server_details

log = Logger.get_logger('ETSI_TOSCA_DUMMY_DEPLOYMENT.py')


def get_epis_host_details():
    log.info('start fetching epis host server details. ')
    Report_file.add_line('start fetching epis host server details.')

    try:
        EPIS_data = ECM_PI_Initialization.get_model_objects(ECM_PI_Initialization, 'EPIS')
        openstack_ip = EPIS_data._EPIS__openstack_ip
        username = EPIS_data._EPIS__openstack_username
        password = EPIS_data._EPIS__openstack_password
        openrc_filename = EPIS_data._EPIS__openrc_filename
        return openstack_ip, username, password, openrc_filename
    except Exception as e:
        log.error('Error while fetching openstack server details from DIT ' + str(e))
        Report_file.add_line('Error while fetching openstack server details from DIT ' + str(e))
        assert False


def get_tenantname_sit():
    log.info('Fetching tenant name form sit')
    Report_file.add_line('Fetching tenant name form sit')

    try:
        sit_data = SIT_initialization.get_model_objects(SIT_initialization, 'SIT')
        tenant_name = sit_data._SIT__tenantName
        return tenant_name
    except Exception as e:
        log.error('Error while fetching tenant name form sit ' + str(e))
        Report_file.add_line('Error while fetching tenant name form sit ' + str(e))
        assert False


def get_pre_requisite_details():
    flavor_name = 'CM-Vnflaf_Etsi_Tosca_Dummy_Flavor'
    numberOfCpu = 2
    ram = 5120
    diskSize = 0
    return flavor_name, numberOfCpu, ram, diskSize


def remove_old_vnflaf_dir():
    try:

        sit_data = SIT_initialization.get_model_objects(SIT_initialization, 'SIT')

        is_vm_vnfm = sit_data._SIT__is_vm_vnfm

        if 'TRUE' == is_vm_vnfm:

            ecm_host_data = Initialization_script.get_model_objects(Initialization_script, 'ECM_CORE')
            vm_vnfm_namespace = ecm_host_data._Ecm_core__vm_vnfm_namespace
            connection = get_VMVNFM_host_connection()
            log.info('Removing old vnflaf package from vm vnfm')
            cmd = "rm -rf /vnflcm-ext/current/vnf_package_repo/vnflaf"
            command = get_vmvnfm_pod_cmd(cmd)

        else:

            lcm_server_ip, lcm_username, lcm_password = Server_details.lcm_host_server_details(Server_details)
            connection = ServerConnection.get_connection(lcm_server_ip, lcm_username, lcm_password)
            log.info('Removing old vnflaf package from vnflcm')
            command = 'rm -rf /vnflcm-ext/current/vnf_package_repo/vnflaf'

        Report_file.add_line('Removing folder command ' + command)
        connection.exec_command(command)
        time.sleep(2)

    except Exception as e:
        log.error('Error Removing old vnflaf package from vnflcm ' + str(e))
        assert False
    finally:
        connection.close()


def create_etsi_tosca_dummy_depl_flavours():
    log.info('start creating etis tosca dummy deployment flavors ')
    Report_file.add_line('start creating etis tosca dummy deployment flavors')

    openstack_ip, username, password, openrc_filename = get_epis_host_details()
    tenant_name = get_tenantname_sit()

    flavor_name, numberOfCpu, ram, diskSize = get_pre_requisite_details()

    flavor_exists = check_flavor_exists(openrc_filename, openstack_ip, username, password, flavor_name)
    if flavor_exists:
        log.info('Flavor with name ' + flavor_name + ' already exists in VIM')
        Report_file.add_line('Flavor with name ' + flavor_name + ' already exists in VIM')
    else:
        log.info('Flavor with name ' + flavor_name + ' does not  exists in VIM')
        Report_file.add_line('Flavor with name ' + flavor_name + ' does not  exists in VIM')
        name = flavor_name[3:]

        update_any_flavor_file(name, numberOfCpu, ram, diskSize, tenant_name)

        update_transfer_flavour_file()
        create_flavour('flavour.json', 'flavour_transfer.json', flavor_name)

    log.info('Finished creating etis tosca dummy deployment flavors')
    Report_file.add_line('Finished creating etis tosca dummy deployment flavors')


def etsi_tosca_package_download_parameter():
    add_package_download_parameter('TOSCA_DUMMY')


def get_vnfd_id_tosca_dummy_nodes():
    get_vnfd_id_ims_nodes('TOSCA_DUMMY', 'deployETSIDummyTosca')


def update_tosca_dummy_node_onboard_file():
    global package_name

    package_name = Common_utilities.get_name_with_timestamp(Common_utilities, 'TOSCA_DUMMY')

    update_tosca_node_onboard_file(package_name)


def create_etis_dummy_package_in_cm():
    sit_data = SIT_initialization.get_model_objects(SIT_initialization, 'SIT')
    vnfd_id = sit_data._SIT__ims_vnfd_id
    package_name = vnfd_id + '.zip'

    package_path = '/var/tmp/deployETSIDummyTosca'
    onboard_tosca_node_package('onboard_tosca.json', package_name, package_path, 'TOSCA_DUMMY')


def verify_etis_dummy_package_in_cm():
    log.info('start verifying the onboarded TOSCA dummy package')
    sit_data = SIT_initialization.get_model_objects(SIT_initialization, 'SIT')
    ecm_host_data = Initialization_script.get_model_objects(Initialization_script, 'ECM_CORE')
    ecm_server_ip = ecm_host_data._Ecm_core__ECM_Host_Blade_IP
    ecm_username = ecm_host_data._Ecm_core__ECM_Host_Blade_username
    ecm_password = ecm_host_data._Ecm_core__ECM_Host_Blade_Password

    core_vm_ip = ecm_host_data._Ecm_core__CORE_VM_IP
    core_vm_hostname = ecm_host_data._Ecm_core__core_vm_hostname
    vnf_packageId = sit_data._SIT__vnf_packageId
    connection = ServerConnection.get_connection(ecm_server_ip, ecm_username, ecm_password)
    token = Common_utilities.authToken(Common_utilities, connection, core_vm_ip)

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

        log.error(
            'Verification of package uploaded failed. Please check the status of provisioning and operationalState  ')
        log.error('provisioningStatus : ' + provisioningStatus + ' operationalState : ' + operationalState)
        Report_file.add_line(
            'Verification of package uploaded failed. Please check the status of provisioning and operationalState')
        log.info('Failed verification of package upload Doing Clean up of Tosca Package ' + vnf_packageId)
        delete_tosca_vnf_package(vnf_packageId)
        assert False


def get_image_and_node_name():
    image_name = 'ERICrhelvnflafimage'
    node_name = 'TOSCA_DUMMY'
    return image_name, node_name


def transfer_dummy_image_openstack():
    try:

        log.info('start searching image in ECM for TOSCA Dummy')
        Report_file.add_line('start searching image in ECM for TOSCA Dummy')

        ecm_server_ip, ecm_username, ecm_password = get_ecm_core_ecm_host_details()
        ecm_host_data = Initialization_script.get_model_objects(Initialization_script, 'ECM_CORE')
        core_vm_ip = get_ecm_core_corevmip()
        core_vm_hostname = ecm_host_data._Ecm_core__core_vm_hostname
        image_name, node_name = get_image_and_node_name()

        connection = ServerConnection.get_connection(ecm_server_ip, ecm_username, ecm_password)
        token = Common_utilities.authToken(Common_utilities, connection, core_vm_hostname)
        image_exists = check_image_registered(connection, image_name, token, core_vm_hostname)
        if image_exists:
            Report_file.add_line('Image with name ' + image_name + ' already registered in cloud manager')
            update_transfer_image_file()
            file_name = 'transfer_image.json'
            transfer_image_to_vim(node_name, file_name)
            connection = ServerConnection.get_connection(ecm_server_ip, ecm_username, ecm_password)
            image_exists = check_image_registered(connection, image_name, token, core_vm_hostname,
                                                  transfered_to_vim=True)
        else:
            log.error('Image not registered in ECM , something went wrong in onboarding dummy tosca package')
            Report_file.add_line('Image not registered in ECM , something went wrong in onboarding dummy tosca package')
            assert False


    except Exception as e:

        log.error('Error Searching image in ECM for dummy tosca ' + str(e))
        Report_file.add_line('Error Searching image in ECM for dummy tosca' + str(e))
        assert False
    finally:
        connection.close()


def get_deply_dummy_tosca_file():
    file_name = 'deployDummyETSITosca.json'
    return file_name


def get_flavor_name():
    tosca_dummy_depl_flavor = 'CM-Vnflaf_Etsi_Tosca_Dummy_Flavor'
    return tosca_dummy_depl_flavor


def update_tosca_dummy_node_deploy_file():
    try:
        ecm_host_data = Initialization_script.get_model_objects(Initialization_script, 'ECM_CORE')
        sit_data = SIT_initialization.get_model_objects(SIT_initialization, 'SIT')

        vnf_packageId = sit_data._SIT__vnf_packageId

        file_name = get_deply_dummy_tosca_file()
        vapp_name = package_name
        tosca_dummy_depl_flavor = get_flavor_name()
        vimobjectId = get_image_vimobjectId()
        update_dummy_tosca_deploy_file(file_name, vapp_name, tosca_dummy_depl_flavor, vimobjectId)

        ecm_server_ip = ecm_host_data._Ecm_core__ECM_Host_Blade_IP
        ecm_username = ecm_host_data._Ecm_core__ECM_Host_Blade_username
        ecm_password = ecm_host_data._Ecm_core__ECM_Host_Blade_Password
        ecm_connection = ServerConnection.get_connection(ecm_server_ip, ecm_username, ecm_password)

        ServerConnection.put_file_sftp(ecm_connection, r'com_ericsson_do_auto_integration_files/' + file_name,
                                       SIT.get_base_folder(SIT) + file_name)

    except Exception as e:

        log.error('Error updating dummy tosca deploy file ' + str(e))
        Report_file.add_line('Error updating dummy tosca deploy file ' + str(e))
        log.info('Doing Clean up of Tosca Package ' + vnf_packageId)
        delete_tosca_vnf_package(vnf_packageId)

        assert False
    finally:
        ecm_connection.close()


def deploy_dummy_tosca_package():
    try:

        sit_data = SIT_initialization.get_model_objects(SIT_initialization, 'SIT')
        vnf_packageId = sit_data._SIT__vnf_packageId
        deploy_node('deployDummyETSITosca.json')


    except Exception as e:
        log.error('Error while deploying Dummy TOSCA ')
        log.info('Doing Clean up of Dummy Deployment of Tosca Package ' + vnf_packageId)
        delete_tosca_vnf_package(vnf_packageId)
        assert False


def verify_etsi_dummy_deployment():
    verify_tosca_bgf_deployment()


def get_ecm_core_ecm_host_details():
    try:
        ecm_host_data = Initialization_script.get_model_objects(Initialization_script, 'ECM_CORE')
        ecm_server_ip = ecm_host_data._Ecm_core__ECM_Host_Blade_IP
        ecm_username = ecm_host_data._Ecm_core__ECM_Host_Blade_username
        ecm_password = ecm_host_data._Ecm_core__ECM_Host_Blade_Password
        return ecm_server_ip, ecm_username, ecm_password
    except Exception as e:
        log.error('Error while fetching ecm host data server details from DIT ' + str(e))
        Report_file.add_line('Error while fetching ecm host data server details from DIT ' + str(e))
        assert False


def get_ecm_core_lcm_host_details():
    try:
        ecm_host_data = Initialization_script.get_model_objects(Initialization_script, 'ECM_CORE')
        lcm_server_ip = ecm_host_data._Ecm_core__VNF_LCM_Servicedb_IP
        lcm_username = ecm_host_data._Ecm_core__VNF_LCM_Servicedb_Username
        lcm_password = ecm_host_data._Ecm_core__VNF_LCM_Servicedb_Password
        return lcm_server_ip, lcm_username, lcm_password
    except Exception as e:
        log.error('Error while fetching lcm server details from DIT ' + str(e))
        Report_file.add_line('Error while fetching lcm server details from DIT ' + str(e))
        assert False


def get_ecm_core_env():
    try:
        ecm_host_data = Initialization_script.get_model_objects(Initialization_script, 'ECM_CORE')
        environment = ecm_host_data._Ecm_core__enviornment
        return environment
    except Exception as e:
        log.error('Error while fetching ecm core env details from DIT ' + str(e))
        Report_file.add_line('Error while fetchig ecm core env details from DIT ' + str(e))
        assert False


def get_ecm_core_corevmip():
    try:
        ecm_host_data = Initialization_script.get_model_objects(Initialization_script, 'ECM_CORE')
        core_vm_ip = ecm_host_data._Ecm_core__CORE_VM_IP

        return core_vm_ip

    except Exception as e:
        log.error('Error while fetching ecm core server ip details from DIT ' + str(e))
        Report_file.add_line('Error while fetching ecm core server ip details from DIT ' + str(e))
        assert False


def verfiy_etsi_dummy_tosca_workflow_version():
    verify_worklow_version(package_name)
