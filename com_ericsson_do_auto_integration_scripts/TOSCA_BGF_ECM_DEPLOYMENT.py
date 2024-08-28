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
from com_ericsson_do_auto_integration_utilities.Common_utilities import Common_utilities
from com_ericsson_do_auto_integration_scripts.ECM_PACKAGE_DELETION import *

log = Logger.get_logger('TOSCA_BGF_ECM_DEPLOYMENT.py')


def generate_tosca_ssh_key():
    try:
        ssh_key_generate_on_lcm("")
        # using this key in update deploy tosca bgf file , no need to get the key here

    except Exception as e:
        log.error('Error TOSCA BGF ssh-key generation ' + str(e))
        Report_file.add_line('Error BGF ssh-key generation ' + str(e))


def generate_sol005_tosca_ssh_key():
    try:

        log.info('start to generate Sol005 BGF ssh keys from Jboss user')
        Report_file.add_line('start to generate Sol005 BGF ssh keys from Jboss user')

        ecm_host_data = Initialization_script.get_model_objects(Initialization_script, 'ECM_CORE')
        server_ip = ecm_host_data._Ecm_core__VNF_LCM_Servicedb_IP
        username = ecm_host_data._Ecm_core__VNF_LCM_Servicedb_Username
        password = ecm_host_data._Ecm_core__VNF_LCM_Servicedb_Password
        vm_vnfm_namespace = ecm_host_data._Ecm_core__vm_vnfm_namespace

        is_vm_vnfm = Server_details.is_vm_vnfm_usecase(Server_details)

        if 'TRUE' == is_vm_vnfm:
            connection = get_VMVNFM_host_connection()
            pod_name = get_vmvnfm_pod()
            command = 'kubectl exec {} -c eric-vnflcm-service -n {} -- sudo -u jboss_user bash -c {}rm -rf /vnflcm-ext/backups/workflows/private_keys/default/.ssh{}'.format(
                pod_name,
                vm_vnfm_namespace, "'", "'")
            log.info('removing .ssh directory on vm vnfm')
            Report_file.add_line('removing .ssh directory command on vm vnfm-' + command)
            stdin, stdout, stderr = connection.exec_command(command)
            command = 'kubectl exec {} -c eric-vnflcm-service -n {} -- sudo -u jboss_user bash -c {}cd /vnflcm-ext/backups/workflows/private_keys/default && mkdir .ssh && chmod 0700 .ssh && ssh-keygen -P "" -t rsa -f .ssh/id_rsa{}'.format(
                pod_name,
                vm_vnfm_namespace, "'", "'")

        else:
            connection = ServerConnection.get_connection(server_ip, username, password)
            command = 'sudo -u jboss_user bash -c {}rm -rf /vnflcm-ext/backups/workflows/private_keys/default/.ssh{}'.format(
                "'", "'")
            log.info('removing .ssh directory on lcm')
            Report_file.add_line('removing .ssh directory command on lcm -' + command)
            stdin, stdout, stderr = connection.exec_command(command)
            command = 'sudo -u jboss_user bash -c {}cd /vnflcm-ext/backups/workflows/private_keys/default && mkdir .ssh && chmod 0700 .ssh && ssh-keygen -P "" -t rsa -f .ssh/id_rsa{}'.format(
                "'", "'")

        log.info('generate Sol005 BGF ssh key command -' + command)
        Report_file.add_line('generate Sol005 BGF ssh key command -' + command)
        stdin, stdout, stderr = connection.exec_command(command)

        error_output = str(stderr.read())
        error = error_output[2:-1:1]

        std_output = str(stdout.read())
        output = std_output[2:-1:1]

        if error:
            log.error('Error in above command of ssh key ' + error)
            assert False

        log.info('command output of Sol005 BGF ssh keys ' + output)
        # Below key needed on default path also with above path for SOL 005 BGF.
        Report_file.add_line('generate Sol005 BGF ssh key on default path also ')

        ssh_key_generate_on_lcm("")

    except Exception as e:
        log.error('Error Sol005 BGF ssh-key generation ' + str(e))
        Report_file.add_line('Error Sol005 BGF ssh-key generation ' + str(e))
        assert False


def sol005_bgf_workflow_deployment():
    bgf_workflow_path = r'/var/tmp/SOL005_BGF_WORKFLOW'
    workflow_deployment(bgf_workflow_path, 'VBGF')


def create_tosca_flavours(version='', tosca_bgf_flavor=''):
    log.info('start creating tosca bgf flavor ' + tosca_bgf_flavor)
    Report_file.add_line('start creating tosca bgf flavor ' + tosca_bgf_flavor)

    EPIS_data = ECM_PI_Initialization.get_model_objects(ECM_PI_Initialization, 'EPIS')
    openstack_ip = EPIS_data._EPIS__openstack_ip
    username = EPIS_data._EPIS__openstack_username
    password = EPIS_data._EPIS__openstack_password
    openrc_filename = EPIS_data._EPIS__openrc_filename
    sit_data = SIT_initialization.get_model_objects(SIT_initialization, 'SIT')
    tenant_name = sit_data._SIT__tenantName

    flavor_exists = check_flavor_exists(openrc_filename, openstack_ip, username, password, tosca_bgf_flavor)
    if flavor_exists:
        log.info('Flavor with name ' + tosca_bgf_flavor + ' already exists in VIM')
        Report_file.add_line('Flavor with name ' + tosca_bgf_flavor + ' already exists in VIM')
    else:
        log.info('Flavor with name ' + tosca_bgf_flavor + ' does not  exists in VIM')
        Report_file.add_line('Flavor with name ' + tosca_bgf_flavor + ' does not  exists in VIM')
        name = tosca_bgf_flavor[3:]

        if version == 'sol_vbgf':

            update_any_flavor_file(name, 4, 8192, 6, tenant_name)

        elif version == 'sol_dummy':

            update_any_flavor_file(name, 2, 5120, 1, tenant_name)

        else:

            update_any_flavor_file(name, 4, 6144, 6, tenant_name)

        update_transfer_flavour_file()
        create_flavour('flavour.json', 'flavour_transfer.json', name)

    log.info('Finished creating tosca bgf flavors')
    Report_file.add_line('Finished creating tosca bgf flavors')


def create_tosca_sol_bgf_flavours():
    create_tosca_flavours(version='sol_vbgf', tosca_bgf_flavor='CM-TOSCA_SOL_BGF_FLAVOR')


def create_tosca_bgf_flavours():
    create_tosca_flavours(version='', tosca_bgf_flavor='CM-TOSCA_BGF_FLAVOR')


def tosca_bgf_package_download_parameter():
    add_package_download_parameter('TOSCA_BGF')


def create_tosca_bgf_security_group():
    update_tosca_security_group_files('bgf_security_group')
    create_node_security_group('TOSCA_BGF', 'create_node_security_group.json', 'transfer_node_security_group.json',
                               'bgf_security_group')


# method to get folder name that is named upon bfg software folder
def get_vnfd_id_tosca_bgf_nodes():
    get_vnfd_id_ims_nodes('BGF', 'deployETSIvBGF')


def update_tosca_bgf_node_onboard_file():
    global package_name

    package_name = Common_utilities.get_name_with_timestamp(Common_utilities, 'TOSCA_BGF')
    update_tosca_node_onboard_file(package_name)


def onboard_tosca_bgf_package():
    sit_data = SIT_initialization.get_model_objects(SIT_initialization, 'SIT')
    vnfd_id = sit_data._SIT__ims_vnfd_id
    package_name = vnfd_id + '.zip'
    package_path = '/var/tmp/deployETSIvBGF'
    onboard_tosca_node_package('onboard_tosca.json', package_name, package_path, 'TOSCA_BGF')


def onboard_sol_tosca_bgf_package():
    sol_bgf_package_path = '/var/tmp/deploySOL005vBGF'
    global sol_bgf_package_name
    sol_bgf_package_name = Common_utilities.get_name_with_timestamp(Common_utilities, 'MIP_PORT_SOL_VBGF')
    upload_file = 'ns-vbgf-env-setup-direct.zip'
    onboard_node_hot_package(sol_bgf_package_name, upload_file, sol_bgf_package_path)


def deploy_sol_tosca_bgf_package():
    external_network_id, sub_network_id, external_network_system_id, sub_network_system_id = fetch_external_subnet_id()
    update_sol_bgf_deploy_file('deploy_sol_vbgf.json', sol_bgf_package_name, external_network_id, sub_network_id)
    deploy_node_hot_package('deploy_sol_vbgf.json')


def verify_tosca_bgf_package():
    log.info('start verifying the onboarded bgf package')
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
        log.info('Finished onboarding package for ')
        Report_file.add_line('Finished onboarding package for ')
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


def search_transfer_image(image_name):
    try:

        log.info('start searching image in ECM for TOSCA BGF')
        Report_file.add_line('start searching image in ECM for TOSCA BGF')
        ecm_host_data = Initialization_script.get_model_objects(Initialization_script, 'ECM_CORE')
        ecm_server_ip = ecm_host_data._Ecm_core__ECM_Host_Blade_IP
        ecm_username = ecm_host_data._Ecm_core__ECM_Host_Blade_username
        ecm_password = ecm_host_data._Ecm_core__ECM_Host_Blade_Password
        core_vm_ip = ecm_host_data._Ecm_core__CORE_VM_IP
        core_vm_hostname = ecm_host_data._Ecm_core__core_vm_hostname
        connection = ServerConnection.get_connection(ecm_server_ip, ecm_username, ecm_password)
        token = Common_utilities.authToken(Common_utilities, connection, core_vm_hostname)
        image_exists = check_image_registered(connection, image_name, token, core_vm_hostname)
        if image_exists:
            Report_file.add_line('Image with name ' + image_name + ' already registered in cloud manager')
            update_transfer_image_file()
            file_name = 'transfer_image.json'
            # Node name is tosca bgf only in both cases of sol and normal.
            transfer_image_to_vim('TOSCA_BGF', file_name)
        else:
            log.error('Image not registered in ECM , something went wrong in onboarding tosca package')
            Report_file.add_line('Image not registered in ECM , something went wrong in onboarding tosca package')
            assert False


    except Exception as e:

        log.error('Error Searching image in ECM ' + str(e))
        Report_file.add_line('Error Searching image in ECM ' + str(e))
        assert False
    finally:
        connection.close()


def search_transfer_tosca_bgf_image():
    image_name = 'vBGF_1_20_0_image'
    search_transfer_image(image_name)


def search_transfer_sol_tosca_bgf_image():
    image_name = 'vbgf-image-corei7-mrsv-64-e2e02'
    search_transfer_image(image_name)


def fetch_net_subnet_ids_tosca_bgf():
    try:

        sit_data = SIT_initialization.get_model_objects(SIT_initialization, 'SIT')
        ecm_host_data = Initialization_script.get_model_objects(Initialization_script, 'ECM_CORE')
        vnf_packageId = sit_data._SIT__vnf_packageId
        enviornment = ecm_host_data._Ecm_core__enviornment
        cloud_type = sit_data._SIT__cloudManagerType
        provider_net = 'P3_' + cloud_type + '01_' + enviornment + '_PROV'
        global network_list
        network_list = ['vbgf_DO_Net_li_sp1', provider_net, 'vbgf_DO_sig_sp0', 'vbgf_DO_sig_sp1', 'vbgf_DO_sig_sp2',
                        'vbgf_DO_sig_sp3']

        global net_subnet_data
        net_subnet_data = fetch_net_subnet_ids_tosca_node(network_list)

    except Exception as e:

        log.info('Failed fetching net subnets Doing Clean up of Tosca Package ' + vnf_packageId)
        delete_tosca_vnf_package(vnf_packageId)
        assert False


def update_tosca_bgf_node_deploy_file():
    try:
        ecm_host_data = Initialization_script.get_model_objects(Initialization_script, 'ECM_CORE')
        sit_data = SIT_initialization.get_model_objects(SIT_initialization, 'SIT')

        vnf_packageId = sit_data._SIT__vnf_packageId
        server_ip = ecm_host_data._Ecm_core__VNF_LCM_Servicedb_IP
        username = ecm_host_data._Ecm_core__VNF_LCM_Servicedb_Username
        password = ecm_host_data._Ecm_core__VNF_LCM_Servicedb_Password
        lcm_connection = ServerConnection.get_connection(server_ip, username, password)

        command = 'sudo -i cat /home/jboss_user/.ssh/id_rsa.pub'
        log.info(command)
        stdin, stdout, stderr = lcm_connection.exec_command(command, get_pty=True)
        command_output = str(stdout.read())

        ssh_key = command_output[2:-5:1]
        Report_file.add_line('Generated TOSCA ssh_key ::  ' + ssh_key)
        time.sleep(2)

        file_name = 'tosca_bgf_deploy.json'
        vapp_name = package_name
        tosca_bgf_flavor = 'os-tosca'

        update_tosca_node_deploy_file(file_name, vapp_name, tosca_bgf_flavor, ssh_key, network_list, net_subnet_data)

        ecm_server_ip = ecm_host_data._Ecm_core__ECM_Host_Blade_IP
        ecm_username = ecm_host_data._Ecm_core__ECM_Host_Blade_username
        ecm_password = ecm_host_data._Ecm_core__ECM_Host_Blade_Password
        ecm_connection = ServerConnection.get_connection(ecm_server_ip, ecm_username, ecm_password)

        ServerConnection.put_file_sftp(ecm_connection, r'com_ericsson_do_auto_integration_files/' + file_name,
                                       SIT.get_base_folder(SIT) + file_name)

    except Exception as e:

        log.error('Error updating tosca bgf deploy file ' + str(e))
        Report_file.add_line('Error updating tosca bgf deploy file ' + str(e))
        log.info('Doing Clean up of Tosca Package ' + vnf_packageId)
        delete_tosca_vnf_package(vnf_packageId)

        assert False
    finally:
        lcm_connection.close()
        ecm_connection.close()


def deploy_tosca_bgf_package():
    try:

        sit_data = SIT_initialization.get_model_objects(SIT_initialization, 'SIT')
        vnf_packageId = sit_data._SIT__vnf_packageId
        deploy_node('tosca_bgf_deploy.json')


    except Exception as e:

        log.info('Doing Clean up of Tosca Package ' + vnf_packageId)
        delete_tosca_vnf_package(vnf_packageId)
        assert False


def verify_tosca_bgf_deployment():
    try:

        log.info('waiting 60 seconds to verification of node')
        time.sleep(60)
        sit_data = SIT_initialization.get_model_objects(SIT_initialization, 'SIT')
        ecm_host_data = Initialization_script.get_model_objects(Initialization_script, 'ECM_CORE')

        ecm_server_ip = ecm_host_data._Ecm_core__ECM_Host_Blade_IP
        ecm_username = ecm_host_data._Ecm_core__ECM_Host_Blade_username
        ecm_password = ecm_host_data._Ecm_core__ECM_Host_Blade_Password
        core_vm_hostname = ecm_host_data._Ecm_core__core_vm_hostname
        core_vm_ip = ecm_host_data._Ecm_core__CORE_VM_IP
        node_id = sit_data._SIT__vapp_Id
        connection = ServerConnection.get_connection(ecm_server_ip, ecm_username, ecm_password)
        token = Common_utilities.authToken(Common_utilities, connection, core_vm_hostname)

        # file_data = Json_file_handler.get_json_data(Json_file_handler,r'com_ericsson_do_auto_integration_files/VNFD_Wrapper_BGF.json')
        # management_ip = file_data['instantiateVnfOpConfig']['management_ip_address']

        # ping_response = get_ping_response(connection, management_ip)

        provisioningStatus, operationalState = get_node_status(connection, token, core_vm_hostname, node_id)

        if 'ACTIVE' == provisioningStatus and 'INSTANTIATED' == operationalState:

            # log.info('Ping Successful')
            Report_file.add_line('provisioningStatus is : ' + provisioningStatus)
            Report_file.add_line('operationalState is : ' + operationalState)
            # Report_file.add_line(Report_file, 'Ping Successful')
            log.info('Verification of package deployment is success')
            Report_file.add_line('Verification of package deployment is successful')
            connection.close()

        else:
            log.info(
                'Verification of package deployment failed. Please check the status of provisioning and operationalState and ping response ')
            Report_file.add_line(
                'Verification of package deployment failed. Please check the status of provisioning and operationalState and ping response')
            assert False


    except Exception as e:
        connection.close()
        log.error('Error verifying node deployment ' + str(e))
        Report_file.add_line('Error verifying node deployment ' + str(e))
        assert False


def transfer_ssh_key_jboss():
    try:

        is_vm_vnfm = Server_details.is_vm_vnfm_usecase(Server_details)

        if 'TRUE' == is_vm_vnfm:

            log.info(' VM VNFM True , transferring ssh key ')
            ecm_host_data = Initialization_script.get_model_objects(Initialization_script, 'ECM_CORE')
            vm_vnfm_namespace = ecm_host_data._Ecm_core__vm_vnfm_namespace

            connection = get_VMVNFM_host_connection()
            cmd = "sudo -u jboss_user bash -c 'mkdir -pm 0600 ~/.ssh; cp -p /vnflcm-ext/backups/workflows/private_keys/default/.ssh/id_rsa  ~/.ssh;'"
            command = get_vmvnfm_pod_cmd(cmd)
            Report_file.add_line('copy command  : ' + command)

        else:

            lcm_server_ip, lcm_username, lcm_password = Server_details.lcm_host_server_details(Server_details)
            log.info('LCM Connection open ')
            connection = ServerConnection.get_connection(lcm_server_ip, lcm_username, lcm_password)
            log.info('Copying ssh key on jboss path ')
            command = 'sudo -u jboss_user bash -c {}mkdir -pm 0600 ~/.ssh; cp -p /vnflcm-ext/backups/workflows/private_keys/default/.ssh/id_rsa  ~/.ssh;{}'.format(
                "'", "'")
            Report_file.add_line('copy command  : ' + command)

        connection.exec_command(command, get_pty=True)
        time.sleep(2)
        connection.close()
        log.info('Connection close')

    except Exception as e:
        connection.close()
        log.error('Error transferring ssh key on jboss  ' + str(e))
        Report_file.add_line('Error transferring ssh key on jboss  ' + str(e))
        assert False


def upload_sol_tosca_vnfd():
    try:
        log.info('Start to upload ETSI TOSCA VNFD')
        Report_file.add_line('Start to upload ETSI TOSCA VNFD')
        package_path = '/var/tmp/deploySOL005vBGF'
        package_name = 'eric_vbgf_1.25_0.0.0-e2e02.csar'
        pkg_name = package_name.split('.csar')[0]
        name = Common_utilities.get_name_with_timestamp(Common_utilities, pkg_name)
        file_name = 'onboard_tosca.json'
        update_onboard_sol_bgf_file(file_name, package_name, name)
        onboard_tosca_node_package(file_name, package_name, package_path, 'SOL_TOSCA_VNFD')

    except Exception as e:
        log.error('Error While uploading ETSI TOSCA VNFD ' + str(e))
        Report_file.add_line('Error while uploading ETSI TOSCA VNFD ' + str(e))
        assert False


def etsi_tosca_nsd_package_details():
    pkgs_dir_path = "/var/tmp/deploySOL005vBGF/"
    package = 'NSD-vBGF-Service-Basic-1.0.3.csar'
    packageName = package.split('.csar')[0]
    json_filename = 'createToscaNsdPackage.json'
    return pkgs_dir_path, package, packageName, json_filename


def create_sol_tosca_nsd():
    try:
        log.info('Start to create ETSI TOSCA NSD package')
        Report_file.add_line('Start to create ETSI TOSCA NSD package')
        pkgs_dir_path, package, packageName, json_filename = etsi_tosca_nsd_package_details()
        create_nsd_package(packageName, json_filename)

    except Exception as e:
        log.error('Error While creating ETSI TOSCA NSD package ' + str(e))
        Report_file.add_line('Error while creating ETSI TOSCA NSD package ' + str(e))
        assert False


def upload_sol_tosca_nsd_package():
    try:
        log.info('Start to upload ETSI TOSCA NSD package')
        Report_file.add_line('Start to upload ETSI TOSCA NSD package')
        # etsi_tosca_bgf_deployment = 'ETSI_TOSCA_DEPL'
        pkgs_dir_path, package, packageName, json_filename = etsi_tosca_nsd_package_details()
        upload_nsd_package(pkgs_dir_path, package)

    except Exception as e:
        log.error('Error While uploading ETSI TOSCA NSD package ' + str(e))
        Report_file.add_line('Error while uploading ETSI TOSCA NSD package ' + str(e))
        assert False
