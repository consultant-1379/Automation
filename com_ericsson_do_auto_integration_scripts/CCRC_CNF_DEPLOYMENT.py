from com_ericsson_do_auto_integration_utilities.Logger import Logger
from com_ericsson_do_auto_integration_utilities.Common_utilities import Common_utilities
from com_ericsson_do_auto_integration_utilities.Server_details import Server_details
from com_ericsson_do_auto_integration_utilities.ServerConnection import ServerConnection
from com_ericsson_do_auto_integration_scripts.EVNFM_NODE_DEPLOYMENT import (create_vnf_package_resource_id,
                                                                            onboarding_cnf_csar, ccrc_node_deploy,
                                                                            create_node_vnf_identifier,
                                                                            get_ccrc_vnf_details,
                                                                            upgrade_ccrc_node_package,
                                                                            upload_node_ccd_target_cnfig,
                                                                            ccrc_node_scale_operation)
from com_ericsson_do_auto_integration_scripts.EVNFM_NODE_VERIFICATION import (verify_ccrc_node_operation_state,
                                                                              verify_ccrc_onboarding_state)
from com_ericsson_do_auto_integration_scripts.EVNFM_NODE_TERMINATE import (terminate_cnf, get_vnf_package,
                                                                           cleanup_after_termination,
                                                                           delete_vnf_identifier, terminate_evnfm_all,
                                                                           get_VMVNFM_host_connection)
from com_ericsson_do_auto_integration_utilities.SIT_files_update import (update_runtime_env_file)
from com_ericsson_do_auto_integration_utilities.General_files_update import (SIT_initialization, Json_file_handler,
                                                                             update_ccrc_scale_file)
from com_ericsson_do_auto_integration_model.Ecm_core import Ecm_core
from com_ericsson_do_auto_integration_model.SIT import SIT
from com_ericsson_do_auto_integration_model.EPIS import EPIS
from com_ericsson_do_auto_integration_utilities import Integration_properties as int_prop
from com_ericsson_do_auto_integration_utilities.file_utils import create_temp_dir, del_dir, handle_stderr


log = Logger.get_logger('CCRC_CNF_DEPLOYMENT.py')

software_dir = 'deployCCRC'
vnf_identifier_id = None
aspect_id = None


def onboard_ccrc_vnf_package():
    connection = None
    try:
        log.info('Uploading ccrc vnf package to create vnf package resource id ')

        sit_data = SIT_initialization.get_model_objects(SIT_initialization, 'SIT')
        ecm_server_ip, ecm_username, ecm_password = Server_details.ecm_host_blade_details(Server_details)

        connection = ServerConnection.get_connection(ecm_server_ip, ecm_username, ecm_password)
        evnfm_token = Common_utilities.get_evnfm_token(Common_utilities, connection)

        file_name = 'vnf_package_resource.json'

        resource_id = create_vnf_package_resource_id(connection, evnfm_token, software_dir, file_name)

        sit_data._SIT__ccrc_resource_id = resource_id
        update_runtime_env_file('CCRC_RESOURCE_ID', resource_id)

        log.info('Package resource id: %s', resource_id)
        log.info('VNF package resource id created successfully')

    except Exception as e:
        log.info('Error creating vnf package resource id %s', str(e))
        assert False
    finally:
        connection.close()


def onboard_ccrc_cnf_package(upgrade=False):
    connection = None
    try:
        log.info('Onboarding ccrc cnf csar package to create vnfd id ')

        ecm_server_ip, ecm_username, ecm_password = Server_details.ecm_host_blade_details(Server_details)
        connection = ServerConnection.get_connection(ecm_server_ip, ecm_username, ecm_password)
        evnfm_token = Common_utilities.get_evnfm_token(Common_utilities, connection)
        global software_dir
        if upgrade:
            software_dir = 'deployCCRC/UPGRADE'

        path = '/var/tmp/{}/'.format(software_dir)

        command = 'cd ' + path + ' ; find eric-ccrc*.csar | xargs ls -rt | tail -1'

        log.info('Executing command: %s', command)
        stdin, stdout, stderr = connection.exec_command(command)

        command_output = str(stdout.read())[2:-3:]
        log.info('Command output: %s', command_output)
        cnf_package = command_output

        onboard_status = onboarding_cnf_csar(connection, evnfm_token, software_dir, cnf_package)

        if onboard_status:
            log.info('ccrc cnf csar package on boarded, checking onboarding state..')

        else:
            log.error('ccrc cnf csar package Onboarding failed')
            assert False

    except Exception as e:
        log.info('Error on boarding ccrc cnf csar package %s', str(e))

        assert False
    finally:
        connection.close()


def verify_ccrc_cnf_onboarding(upgrade=False):
    connection = None
    try:
        log.info('Verifying ccrc cnf csar package onboarding state. ')
        ecm_server_ip, ecm_username, ecm_password = Server_details.ecm_host_blade_details(Server_details)
        connection = ServerConnection.get_connection(ecm_server_ip, ecm_username, ecm_password)
        evnfm_token = Common_utilities.get_evnfm_token(Common_utilities, connection)
        onboard_status, output, pkg_id = verify_ccrc_onboarding_state(connection, evnfm_token, 60)

        if onboard_status:
            vnfd_id = output
            log.info('ccrc cnf csar package on boarded successfully. vnfdId is: %s', vnfd_id)
            if upgrade:
                update_runtime_env_file('CCRC_UPGRADE_VNFD_ID', vnfd_id)
                Common_utilities.create_artifact_prop_file(Common_utilities, [pkg_id], 'CCRC_UPGRADE')
            else:
                update_runtime_env_file('CCRC_DEPLOY_VNFD_ID', vnfd_id)
                Common_utilities.create_artifact_prop_file(Common_utilities, [pkg_id], 'CCRC_INSTALL')

        else:
            log.error('Verification of ccrc cnf csar package Onboarding failed. %s', str(output))
            assert False

    except Exception as e:
        log.info('Error verifying ccrc cnf csar package onboarding state. %s', str(e))
        assert False
    finally:
        connection.close()


def create_ccrc_vnf_identifier():
    file_name = 'create_vnf_identifier.json'
    vnfd_id = Common_utilities.fetch_attribute_from_runtimefile(Common_utilities, "CCRC_DEPLOY_VNFD_ID")
    ecm_server_ip, ecm_username, ecm_password = Server_details.ecm_host_blade_details(Server_details)
    connection = ServerConnection.get_connection(ecm_server_ip, ecm_username, ecm_password)
    log.info('updating vnfdId in %s', file_name)
    Json_file_handler.modify_attribute(Json_file_handler, f'{int_prop.int_files}/{file_name}', 'vnfdId',
                                       vnfd_id)
    ServerConnection.put_file_sftp(connection, f'{int_prop.int_files}/{file_name}',
                                   f'{SIT.get_base_folder(SIT)}{file_name}')
    create_node_vnf_identifier('CCRC_CNF', file_name)
    global vnf_identifier_id
    vnf_identifier_id = SIT.get_vnf_identifier_id(SIT)
    update_runtime_env_file('VNF_IDENTIFIER_ID', vnf_identifier_id)


def upload_ccrc_ccd_target_cnfig():
    cluster_config_file = SIT.get_cluster_config_file(SIT)
    path = '/var/tmp/{}/'.format(software_dir)
    upload_node_ccd_target_cnfig('CCRC_CNF', cluster_config_file, path)


def upload_ccrc_ccd_target_cnfig_app_staging():
    cluster_config_file = SIT.get_cluster_config_file(SIT)
    upload_node_ccd_target_cnfig('App-Staging', cluster_config_file, '/var/tmp/app_staging_cluster/')


def ccrc_instantiate_cnf():
    inst_file = 'instantiate.json'
    valu_file = 'eric-ccrc-values.yml'
    ecm_server_ip, ecm_username, ecm_password = Server_details.ecm_host_blade_details(Server_details)

    src_inst_file = f'/var/tmp/{software_dir}/{inst_file}'
    dst_inst_file = f'{int_prop.int_files}/{inst_file}'
    log.info('src_inst_file = %s', src_inst_file)
    log.info('dst_inst_file = %s', dst_inst_file)

    src_valu_file = f'/var/tmp/{software_dir}/{valu_file}'
    dst_valu_file = f'{int_prop.int_files}/{valu_file}'
    log.info('src_valu_file = %s', src_valu_file)
    log.info('dst_valu_file = %s', dst_valu_file)

    log.info('Fetching file %s from blade', src_inst_file)
    # ftp instantiate.json file from blade
    conn = ServerConnection.get_connection(ecm_server_ip, ecm_username, ecm_password)
    ServerConnection.get_file_sftp(conn, src_inst_file, dst_inst_file)

    log.info('Fetching file %s from blade', src_valu_file)
    # ftp eric-ccrc-values.yml file from blade
    ServerConnection.get_file_sftp(conn, src_valu_file, dst_valu_file)

    # Update some attributes of the file
    update_files(dst_inst_file, dst_valu_file)

    # Put updated file back to blade to tmp folder
    tmp_dir = create_temp_dir(conn).strip()
    log.info('inst_file: %s', f'{tmp_dir}/{inst_file}')
    log.info('valu_file: %s', f'{tmp_dir}/{valu_file}')
    ServerConnection.put_file_sftp(conn, dst_inst_file, f'{tmp_dir}/{inst_file}')
    ServerConnection.put_file_sftp(conn, dst_valu_file, f'{tmp_dir}/{valu_file}')

    ccrc_node_deploy('CCRC_CNF', inst_file, valu_file, tmp_dir, vnf_identifier_id)

    # Delete tmp dir after its no longer needed
    # stderr = del_dir(conn, tmp_dir)


def update_files(inst_file, values_file):
    """Update attributes of instantiate.json
    and eric-ccrc-values.yml files"""

    log.info('Updating file %s', inst_file)

    cluster_name = SIT.get_cluster_config_file(SIT)
    cluster_name = cluster_name.split(',')[0].split('.')[0]
    log.info('Updating key %s with value %s', 'clusterName', cluster_name)
    Json_file_handler.modify_attribute(Json_file_handler, inst_file, 'clusterName', cluster_name)

    namespace = f'ccrc-{EPIS.get_cn_env_name(EPIS).lower()}'
    Json_file_handler.modify_first_level_attr(Json_file_handler, inst_file, 'additionalParams', 'namespace', namespace)

    global_reg_url = SIT.get_egad_cert_registery_name(SIT)
    log.info('Updating key %s with value %s', 'global.registry.url', global_reg_url)
    Json_file_handler.modify_first_level_attr(Json_file_handler, inst_file, 'additionalParams', 'global.registry.url', global_reg_url)

    kubernetes_ip = SIT.get_ccrc_ip_address(SIT)
    log.info('Updating key %s with value %s', 'kubernetes_service_ipaddress', kubernetes_ip)
    Json_file_handler.update_second_attr_yaml(Json_file_handler, values_file, 'global', 'istio', 'kubernetes_service_ipaddress', kubernetes_ip)

    log.info('Finished updating file %s', inst_file)


def ccrc_verify_cnf():
    instantiate_status = verify_ccrc_node_operation_state(60, 'CCRC_CNF', vnf_identifier_id)

    if instantiate_status:
        log.info('Successfully instantiated CCRC_CNF VNF with Operation state COMPLETED')
    else:
        log.error('Error instantiated CCRC_CNF VNF with Operation state FAILED')
        assert False


def terminate_ccrc_cnf():
    sit_data = SIT_initialization.get_model_objects(SIT_initialization, 'SIT')
    global vnf_identifier_id
    vnf_identifier_id = sit_data._SIT__vnf_identifier_id

    file_name = 'terminate_CNF.json'
    terminate_cnf('CCRC_CNF', file_name, software_dir, vnf_identifier_id)


def verify_ccrc_cnf_terminate():
    terminate_status = verify_ccrc_node_operation_state(60, 'CCRC_CNF', vnf_identifier_id)

    if terminate_status:
        log.info('Successfully terminated CCRC_CNF VNF with Operation state COMPLETED')
    else:
        log.error('Error termination CCRC_CNF VNF with Operation state FAILED')
        assert False


def ccrc_cleanup():
    cleanup_after_termination()


def delete_ccrc_vnf_identifier():
    delete_vnf_identifier(vnf_identifier_id)


def delete_ccrc_vnf_package():
    vnf_product_name = SIT.get_vnf_type(SIT)
    get_vnf_package(vnf_product_name)


def terminate_ccrc_cnf_all():
    terminate_evnfm_all()


def upgrade_ccrc_cnf_package():
    log.info("Started to upgrade CCRC CNF")
    file_name = 'upgrade_ccrc.json'
    vnfd_id = Common_utilities.fetch_attribute_from_runtimefile(Common_utilities, "CCRC_UPGRADE_VNFD_ID")
    ecm_server_ip, ecm_username, ecm_password = Server_details.ecm_host_blade_details(Server_details)
    connection = ServerConnection.get_connection(ecm_server_ip, ecm_username, ecm_password)
    log.info('updating vnfdId in %s', file_name)
    Json_file_handler.modify_attribute(Json_file_handler, f'{int_prop.int_files}/{file_name}', 'vnfdId',
                                       vnfd_id)
    ServerConnection.put_file_sftp(connection, f'{int_prop.int_files}/{file_name}',
                                   f'{SIT.get_base_folder(SIT)}{file_name}')
    global vnf_identifier_id
    vnf_identifier_id = SIT.get_vnf_identifier_id(SIT)
    upgrade_ccrc_node_package('CCRC_CNF', 'upgrade_ccrc.json', vnf_identifier_id)
    log.info("Successfully upgraded CCRC CNF")


def ccrc_verify_upgrade():
    instantiate_status = verify_ccrc_node_operation_state(60, 'CCRC_CNF', vnf_identifier_id)

    if instantiate_status:
        log.info('Successfully upgraded  CCRC_CNF VNF with Operation state COMPLETED')
    else:
        log.error('Error upgrade CCRC_CNF VNF with Operation state FAILED')
        assert False


def get_aspect_id_for_scale():
    global vnf_identifier_id
    vnf_identifier_id = SIT.get_vnf_identifier_id(SIT)
    global aspect_id
    aspect_id = get_ccrc_vnf_details('CCRC_CNF', vnf_identifier_id)


def scale_out_ccrc_cnf():
    file_name = 'ccrc_vnf_scale_file.json'
    operation = 'SCALE_OUT'
    update_ccrc_scale_file(file_name, operation, aspect_id)

    ccrc_node_scale_operation(file_name, operation, 'CCRC_CNF', vnf_identifier_id)


def verify_ccrc_cnf_scale_out():
    scale_out_status = verify_ccrc_node_operation_state(60, 'CCRC_CNF', vnf_identifier_id)

    if scale_out_status:
        log.info('Successfully scale_out CCRC_CNF VNF with Operation state COMPLETED')
    else:
        log.error('Error scale_out CCRC_CNF VNF with Operation state FAILED')
        assert False


def scale_in_ccrc_cnf():
    file_name = 'ccrc_vnf_scale_file.json'
    operation = 'SCALE_IN'
    update_ccrc_scale_file(file_name, operation, aspect_id)

    ccrc_node_scale_operation(file_name, operation, 'CCRC_CNF', vnf_identifier_id)


def verify_ccrc_cnf_scale_in():
    scale_in_status = verify_ccrc_node_operation_state(60, 'CCRC_CNF', vnf_identifier_id)

    if scale_in_status:
        log.info('Successfully scale_in CCRC_CNF VNF with Operation state COMPLETED')
    else:
        log.error('Error scale_in CCRC_CNF VNF with Operation state FAILED')
        assert False


def ccrc_secret_creation():
    director_connection = None
    try:
        log.info('Creating ccrc secret')

        director_connection = get_VMVNFM_host_connection(ccd1=True)

        source = f'{int_prop.int_files}/CCRC_Pre_Reqs'
        dest = f'/home/{Ecm_core.get_ccd1_vm_vnfm_director_username(Ecm_core)}'

        ServerConnection.put_folder_scp(director_connection, source, dest)

        cmd = 'chmod 700 CCRC_Pre_Reqs/create_ccrc_secrets.sh'
        log.info('Executing command: %s', cmd)
        stdin, stdout, stderr = director_connection.exec_command(cmd)
        namespace = f'ccrc-{EPIS.get_cn_env_name(EPIS).lower()}'
        _, username = Server_details.vm_vnfm_director_details(Server_details)
        cmd = f'./CCRC_Pre_Reqs/create_ccrc_secrets.sh {namespace} {username}'
        log.info('Executing create secret command: %s', cmd)
        stdin, stdout, stderr = director_connection.exec_command(cmd)

        log.info('output: %s', stdout.read().decode("utf-8"))
        log.info('Finished creating ccrc secret')

    except Exception as e:
        log.error('Error creating ccrc secret: %s', str(e))
        assert False
    finally:
        director_connection.close()