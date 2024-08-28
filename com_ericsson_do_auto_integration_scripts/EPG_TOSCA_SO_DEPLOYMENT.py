# pylint: disable=C0302,C0103,C0301,C0412,E0602,W0621,W0601,W0401,C0411,R0915,E0602,W0611,W0212,W0703,R1714,W0613,R0914,W0105,R0913,E0401,W0705,W0612
# ********************************************************************
# Ericsson LMI                                    SCRIPT
# ********************************************************************
#
# (c) Ericsson LMI 2021
#
# The copyright to the computer program(s) herein is the property of
# Ericsson LMI. The programs may be used and/or copied only  with the
# written permission from Ericsson LMI or in accordance with the terms
# and conditions stipulated in the agreement/contract under which the
# program(s) have been supplied.
#
# ********************************************************************


from packaging import version
from com_ericsson_do_auto_integration_model.SIT import SIT
from com_ericsson_do_auto_integration_utilities.Logger import Logger
from com_ericsson_do_auto_integration_utilities.Report_file import Report_file
from com_ericsson_do_auto_integration_utilities.SO_file_update import (update_sol_service_template,
                                                                       update_epg_tosca_service_json_file)
from com_ericsson_do_auto_integration_scripts.EPG_ETSI_TOSCA_NSD_DEPLOYMENT import \
    update_onboard_sol_bgf_file
from com_ericsson_do_auto_integration_scripts.SO_NODE_DEPLOYMENT import (update_runtime_env_file,
                                                                         onboard_day1_template,
                                                                         fetch_so_version,
                                                                         onboard_sol_config_template,
                                                                         fetch_external_subnet_id,
                                                                         onboard_enm_ecm_subsystems,
                                                                         onboard_so_template,
                                                                         create_network_service,
                                                                         poll_status_so)
from com_ericsson_do_auto_integration_scripts.ECM_NODE_DEPLOYMENT import (remove_ecm_package_if_exists,
                                                                          Common_utilities,
                                                                          onboard_tosca_node_package,
                                                                          create_nsd_package,
                                                                          upload_nsd_package,
                                                                          Server_details)
from com_ericsson_do_auto_integration_scripts.EPG_SO_DEPLOYMENT import check_epg_tosca_lcm_workflow_status
from com_ericsson_do_auto_integration_initilization.SIT_initialization import (SIT_initialization,
                                                                               ServerConnection,
                                                                               Json_file_handler)
from com_ericsson_do_auto_integration_initilization.ECM_PI_initialization import ECM_PI_Initialization
from com_ericsson_do_auto_integration_scripts.VERIFY_NODE_DEPLOYMENT import node_ping_response

log = Logger.get_logger('EPG_TOSCA_SO_DEPLOYMENT.py')


def upload_vnfd_in_ecm():
    """
    Function is to upload vnfd in ecm
    """
    try:
        log.info('Start to upload VNFD...')
        Report_file.add_line('Start to upload VNFD...')
        sit_data = SIT_initialization.get_model_objects(SIT_initialization, 'SIT')
        package_path = sit_data._SIT__epgToscaSoftwarePath
        package_name = 'Tosca_EPG_VNFD.csar'
        pkg_name = package_name.split('.csar')[0]
        remove_ecm_package_if_exists(pkg_name)
        name = Common_utilities.get_name_with_timestamp(Common_utilities, pkg_name)
        sit_data._SIT__name = name
        update_runtime_env_file('ONBOARD_EPG_TOSCA_PACKAGE', name)
        file_name = 'onboard_epg_tosca.json'
        # using same method of sol bgf as functionality is same
        update_onboard_sol_bgf_file(file_name, package_name, name)
        onboard_tosca_node_package(file_name, package_name, package_path, 'TEPG')
        # This id will be used in TOSCA-EPG Rediscovery use case
        vnf_package_id = SIT.get_vnf_packageId(SIT)
        update_runtime_env_file('EPG_PACKAGE_ID', vnf_package_id)
    except Exception as e:
        log.error('Error While uploading EPG TOSCA VNFD %s', str(e))
        Report_file.add_line('Error while uploading EPG TOSCA VNFD ' + str(e))
        assert False


def epg_tosca_package_details():
    """
    Function to get the epg tosca package details
    """
    sit_data = SIT_initialization.get_model_objects(SIT_initialization, 'SIT')
    package_path = sit_data._SIT__epgToscaSoftwarePath
    package = 'NSD-vTEPG.zip'
    pkgs_dir_path = package_path + '/'
    package_name = package.split('.zip')[0]
    json_filename = 'createTEPGpackage.json'
    return pkgs_dir_path, package, package_name, json_filename


def create_epg_tosca_nsd():
    """
    Function to create epg  tosca nsd
    """
    try:
        log.info('Start to create EPG TOSCA NSD package...')
        Report_file.add_line('Start to create EPG TOSCA NSD package...')
        pkgs_dir_path, package, packageName, json_filename = epg_tosca_package_details()
        create_nsd_package(packageName, json_filename)
    except Exception as e:
        log.error('Error While creating EPG TOSCA NSD package: %s', str(e))
        Report_file.add_line('Error while creating EPG TOSCA NSD package: ' + str(e))
        assert False


def upload_epg_tosca_nsd_package():
    """
    Function to upload epg tosca nsd package
    """
    try:
        log.info('Start to upload EPG TOSCA NSD package...')
        Report_file.add_line('Start to upload EPG TOSCA NSD package...')
        pkgs_dir_path, package, package_name, json_filename = epg_tosca_package_details()
        upload_nsd_package(pkgs_dir_path, package)
    except Exception as e:
        log.error('Error While uploading EPG TOSCA NSD package: %s', str(e))
        Report_file.add_line('Error while uploading EPG TOSCA NSD package: ' + str(e))
        assert False


def epg_tosca_onboard_day1():
    """
    FUnction to start the onboarding day1 epg tosca
    """

    try:

        log.info('Start to onboard day1 config file...')
        Report_file.add_line('Start to onboard day1 config file..')
        """
        Onboard day1ConfigTEPG.xml
        """
        sit_data = SIT_initialization.get_model_objects(SIT_initialization, 'SIT')
        epg_tosca_nsd_software_path = sit_data._SIT__epgToscaSoftwarePath
        onboard_day1_template(epg_tosca_nsd_software_path, 'TEPG', fetch_so_version('TEPG'))
    except Exception as e:
        log.error('Error While onboarding day1: %s', str(e))
        Report_file.add_line('Error While onboarding day1: ' + str(e))
        assert False


def onboard_epg_tosca_config_template():
    """
    Function to start onboard epg tosca config template
    """
    try:
        log.info('Start to onboard configuration templates...')
        Report_file.add_line('Start to onboard configuration templates...')
        global nsparam_form_name, vnfparam_form_name
        ecm_host_data = ECM_PI_Initialization.get_model_objects(ECM_PI_Initialization, 'ECMPI')
        ecm_server_ip, ecm_username, ecm_password = Server_details.ecm_host_blade_details(Server_details)
        ecm_connection = ServerConnection.get_connection(ecm_server_ip, ecm_username, ecm_password)

        pkgs_dir_path, package, package_name, json_filename = epg_tosca_package_details()
        source_path = f'{pkgs_dir_path}so-artifacts'

        log.info('Getting nsAdditionalParamTEPG.json file from blade software path %s', source_path)
        ns_param_file = 'nsAdditionalParamTEPG.json'
        ServerConnection.get_file_sftp(ecm_connection, source_path + '/' + ns_param_file,
                                       r'com_ericsson_do_auto_integration_files/' + ns_param_file)
        nsparam_form_name = Common_utilities.get_name_with_timestamp(Common_utilities, 'nsAdditionalParamTEPG')

        log.info('Getting vnfAdditionalParamTEPG.json file from blade software path %s', source_path)
        vnf_param_file = 'vnfAdditionalParamTEPG.json'
        ServerConnection.get_file_sftp(ecm_connection, source_path + '/' + vnf_param_file,
                                       r'com_ericsson_do_auto_integration_files/' + vnf_param_file)
        vnfparam_form_name = Common_utilities.get_name_with_timestamp(Common_utilities, 'vnfAdditionalParamTEPG')
        ecm_connection.close()

        onboard_sol_config_template(nsparam_form_name, ns_param_file, vnfparam_form_name, vnf_param_file,
                                    fetch_so_version('Sol005_Dummy'), key_check=False)

        fetch_and_update_subnet_data()

    except Exception as e:
        log.error('Error While onboarding configuration templates: %s', str(e))
        Report_file.add_line('Error While onboarding configuration templates: ' + str(e))
        assert False


def fetch_and_update_subnet_data():
    log.info("Fetch external network id and subnet id and save to sit_data")
    external_network_id, sub_network_id, external_network_system_id, sub_network_system_id = \
        fetch_external_subnet_id()
    SIT.set_external_network_system_id(SIT, external_network_system_id)
    SIT.set_sub_network_system_id(SIT, sub_network_system_id)
    log.info("external network system id and sub network system id and  is %s, %s", external_network_system_id,
             sub_network_system_id)


def onboard_tepg_node_subsytems():
    """
    Method to onboard the tepg node subsytems
    """
    onboard_enm_ecm_subsystems('TEPG')


def onboard_epg_tosca_service_template():
    """
    Method to start onboarding epg tosca service template
    """
    try:
        log.info('Start to onboard TEPG service template...')
        Report_file.add_line('Start to onboard TEPG service template...')

        sit_data = SIT_initialization.get_model_objects(SIT_initialization, 'SIT')
        ecm_server_ip, ecm_username, ecm_password = Server_details.ecm_host_blade_details(Server_details)
        ecm_connection = ServerConnection.get_connection(ecm_server_ip, ecm_username, ecm_password)

        pkgs_dir_path, package, package_name, json_filename = epg_tosca_package_details()
        source_path = f'{pkgs_dir_path}so-artifacts'

        st_file_name = 'TEPG_ServiceTemplate.csar'
        # log.info('Getting % file from blade software path %s', st_file_name, source_path)
        ServerConnection.get_file_sftp(ecm_connection, source_path + '/' + st_file_name,
                                       r'com_ericsson_do_auto_integration_files/' + st_file_name)
        ecm_connection.close()
        day1_template_name = sit_data._SIT__day1_template_name
        global so_version
        so_version = fetch_so_version('TEPG')
        update_sol_service_template(st_file_name, nsparam_form_name, vnfparam_form_name, 'TEPG', day1_template_name)
        onboard_so_template(st_file_name, 'TEPG', so_version)
        log.info('Onboarded SO Template.')
        Report_file.add_line('Onboarded SO Template.')
    except Exception as e:
        log.error('Error While onboarding TEPG service template %s', str(e))
        Report_file.add_line('Error While onboarding TEPG service template ' + str(e))
        assert False


def create_epg_tosca_network_service():
    """
    Method to create the epg tosca network service
    """
    try:
        log.info('Start to create epg tosca network service...')
        Report_file.add_line('Start to create epg tosca network service...')
        ecm_host_data = ECM_PI_Initialization.get_model_objects(ECM_PI_Initialization, 'ECMPI')
        environment = ecm_host_data._Ecm_PI__ECM_Host_Name
        ecm_server_ip, ecm_username, ecm_password = Server_details.ecm_host_blade_details(Server_details)
        external_network_id, sub_network_id, external_network_system_id, sub_network_system_id = fetch_external_subnet_id()
        new_ecm_connection = ServerConnection.get_connection(ecm_server_ip, ecm_username,
                                                             ecm_password)
        # source_path= r'/var/tmp/deployTOSCAEPG3.14/so-artifacts'

        # Server_connection.get_file_sftp(Server_connection, new_ecm_connection, source_path+'/'+file_name,r'com_ericsson_do_auto_integration_files/' +file_name)
        data_file = r'com_ericsson_do_auto_integration_files/run_time_' + environment + '.json'
        source = r'/root/' + 'run_time_' + environment + '.json'
        ServerConnection.get_file_sftp(new_ecm_connection, source, data_file)
        onboard_package_name = Json_file_handler.get_json_attr_value(Json_file_handler, data_file,
                                                                     'ONBOARD_EPG_TOSCA_PACKAGE')
        update_runtime_env_file('TOSCA_EPG_VAPP', onboard_package_name)
        if so_version >= version.parse('2.11.0-118'):

            file_name = 'TEPG_DeployService_v1_serviceOrder.json'
            update_epg_tosca_service_json_file(file_name, external_network_system_id, sub_network_system_id,
                                               onboard_package_name, so_version)
            payload = Json_file_handler.get_json_data(Json_file_handler,
                                                      r'com_ericsson_do_auto_integration_files/' + file_name)
            Report_file.add_line(' Passing Payload Data to Create Network Service ')
            new_ecm_connection.close()
            create_network_service(payload, so_version)
        else:
            file_name = 'TEPG_DeployService_v1.json'

            update_epg_tosca_service_json_file(file_name, external_network_system_id, sub_network_system_id,
                                               onboard_package_name, so_version)
            ServerConnection.put_file_sftp(new_ecm_connection,
                                           r'com_ericsson_do_auto_integration_files/' + file_name,
                                           SIT.get_base_folder(SIT) + file_name)
            # using this method as below method has the new API curl command which is used for dummy as well.
            new_ecm_connection.close()
            create_network_service(file_name, so_version)
    except Exception as e:
        log.error('Error while creating service %s', str(e))
        Report_file.add_line('Error while creating service' + str(e))
        assert False


def verify_epg_tosca_service_status():
    """
    Method to verify  status of  epg tosca service
    """
    poll_status_so()


def check_tepg_lcm_workflow_status():
    """
    Method to check the status of tepg lcm workflow
    """
    check_epg_tosca_lcm_workflow_status()


def check_tosca_egp_ping_status():
    """
    This method is fetch tosca epg ip and pass to get ping status
    """
    vnf_param_file = r'com_ericsson_do_auto_integration_files/vnfAdditionalParamTEPG.json'
    ip_address = Json_file_handler.get_json_attr_value(Json_file_handler, vnf_param_file, "ossTopology.nodeIpAddress")
    node_ping_response(ip_address)
