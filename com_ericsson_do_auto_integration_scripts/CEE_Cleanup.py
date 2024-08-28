# pylint: disable=C0209.W0612,E0602,E0401
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

import ast
import json
import time
from com_ericsson_do_auto_integration_model.Ecm_core import Ecm_core
from com_ericsson_do_auto_integration_model.EPIS import EPIS
from com_ericsson_do_auto_integration_utilities.ExecuteCurlCommand import ExecuteCurlCommand
from com_ericsson_do_auto_integration_utilities.Logger import Logger
from com_ericsson_do_auto_integration_utilities.ServerConnection import ServerConnection
from com_ericsson_do_auto_integration_utilities.Server_details import Server_details
from com_ericsson_do_auto_integration_utilities.Common_utilities import Common_utilities
from com_ericsson_do_auto_integration_utilities.Report_file import Report_file
from com_ericsson_do_auto_integration_utilities.Shell_handler import ShellHandler
from com_ericsson_do_auto_integration_initilization.SIT_initialization import SIT_initialization
from com_ericsson_do_auto_integration_initilization.ECM_PI_initialization import ECM_PI_Initialization

log = Logger.get_logger("CEE_Cleanup.py")


def create_openrc_file(openrc_filename, connection, data_dict, environment):
    """
    Method is used to create environment scripts
    @param openrc_filename :
    @param connection :
    @param data_dict :
    @param environment :
    """

    log.info("start creating openrc file %s", openrc_filename)
    if Ecm_core.get_enviornment(Ecm_core) == 'ORCH_STAGING_N53':
        reference_file = r"com_ericsson_do_auto_integration_files/v3_openrc_demo_N53"
    elif "v3" in data_dict["vim_url"]:
        reference_file = r"com_ericsson_do_auto_integration_files/v3_openrc_demo"
    else:
        reference_file = r"com_ericsson_do_auto_integration_files/openrc_demo"

    lines = None

    with open(reference_file, "r") as file_handler:

        lines = file_handler.readlines()

    for line in lines:
        if "export OS_AUTH_URL=" in line:
            index = lines.index(line)
            lines[index] = "export OS_AUTH_URL=" + data_dict["vim_url"] + "\n"
        elif "export OS_TENANT_NAME" in line:
            index = lines.index(line)
            lines[index] = 'export OS_TENANT_NAME="' + data_dict["project"] + '"\n'
        elif "export OS_USERNAME" in line:
            index = lines.index(line)
            lines[index] = 'export OS_USERNAME="' + data_dict["username"] + '"\n'
        elif "export OS_PASSWORD" in line:
            index = lines.index(line)
            lines[index] = 'export OS_PASSWORD="' + data_dict["password"] + '"\n'

        elif "export OS_DOMAIN_NAME" in line:

            if "v3" in data_dict["vim_url"]:
                index = lines.index(line)
                lines[index] = 'export OS_DOMAIN_NAME="Default"\n'
            else:
                index = lines.index(line)
                lines[index] = '#export OS_DOMAIN_NAME="Default"\n'

        elif "Devstack" in environment and "openrcauto_" in openrc_filename:

            if "export OS_PROJECT_DOMAIN_ID" in line:
                index = lines.index(line)
                lines[index] = "export OS_PROJECT_DOMAIN_ID=default" + "\n"
            elif "export OS_USER_DOMAIN_ID" in line:
                index = lines.index(line)
                lines[index] = "export OS_USER_DOMAIN_ID=default" + "\n"
            else:

                line = "export OS_PROJECT_DOMAIN_ID=default" + "\n"
                lines[29] = line

                line = "export OS_USER_DOMAIN_ID=default" + "\n"
                lines[30] = line

    with open(reference_file, "w+") as file_handler:

        file_handler.writelines(lines)

    ServerConnection.put_file_sftp(
        connection, reference_file, "/root/" + openrc_filename
    )

    log.info("Finished creating openrc file %s", openrc_filename)


def prepare_openrc_files(ecm_environment, openrc_filename, project_name, openstack_ip,
                         username, password):
    connection = None
    try:
        static_project_name = EPIS.get_static_project(EPIS)
        static_project_username = EPIS.get_static_project_username(EPIS)
        static_project_password = EPIS.get_static_project_password(EPIS)
        vim_url = EPIS.get_vim_url(EPIS)
        adminUserName = project_name + "_admin"
        adminPassword = project_name.capitalize() + ".laf"
        static_openrc_file = "openrcauto_" + ecm_environment

        connection = ServerConnection.get_connection(openstack_ip,
                                                     username,
                                                     password)

        dynamic_project_data = {
            "project": project_name,
            "vim_url": vim_url,
            "username": adminUserName,
            "password": adminPassword
        }

        static_project_data = {
            "project": static_project_name,
            "vim_url": vim_url,
            "username": static_project_username,
            "password": static_project_password
        }

        # In case of ORCH_STAGING_N53 and TEST_HOTEL_QUEENS we are creating single openrc file
        if openrc_filename != static_openrc_file:
            create_openrc_file(openrc_filename, connection, dynamic_project_data, ecm_environment)

        create_openrc_file(static_openrc_file, connection, static_project_data, ecm_environment)
        time.sleep(2)

    except Exception as e:
        log.error("Error in creation of openrc files: %s", str(e))
        assert False
    finally:
        if connection:
            connection.close()


def de_register_license():
    connection = None
    try:
        log.info("Deregistering vCisco License ")
        ecm_host_data = ECM_PI_Initialization.get_model_objects(
            ECM_PI_Initialization, "ECMPI"
        )
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
        command = "ssh " + vcisco_management_username + "@" + vcisco_management_ip

        interact.send(command + "\n")
        time.sleep(3)

        resp = interact.recv(9999)
        buff = str(resp)

        if "Password:" in buff:
            interact.send(vcisco_management_password + "\n")
            time.sleep(3)

        command = "license smart deregister"
        interact.send(command + "\n")
        time.sleep(5)
        resp = interact.recv(9999)

        command = "show license status"
        interact.send(command + "\n")
        time.sleep(3)
        resp = interact.recv(9999)
        buff = str(resp)
        log.info(buff)

        if "No Licenses in Use" in buff:
            log.info(
                'License command "license smart deregister " completed successfully.'
            )
        else:
            log.info(
                'License command "license smart deregister " failed. Smart Agent not registered'
            )

        interact.shutdown(2)

    except Exception as e:
        log.error("Error in deregister license %s ", str(e))
        Report_file.add_line("Error in deregister license %s", str(e))
        assert False
    finally:
        if connection:
            connection.close()


def delete_cee_stack(stack_name):
    try:
        command = " y | openstack stack delete {}".format(stack_name)
        stdin, stdout, stderr = ShellHandler.execute(ShellHandler, command)
        if not stderr:
            log.info("stack " + stack_name + " deleted successfully")
            Report_file.add_line("stack " + stack_name + " deleted successfully")
        else:
            log.error(
                "problem deleting the stack " + stack_name + " ERROR : " + str(stderr)
            )
            Report_file.add_line()
    except Exception as e:
        log.error("Exception while deleting stack " + stack_name + "ERROR: " + str(e))
        ShellHandler.__del__(ShellHandler)
        assert False


def check_project_exists(
        openrc_filename, project_name, openstack_ip, username, password
):
    try:

        log.info("Project exists : start checking project exists on CEE ")

        ShellHandler.__init__(ShellHandler, openstack_ip, username, password)
        command = "source {}".format(openrc_filename)
        stdin, stdout, stderr = ShellHandler.execute(ShellHandler, command)
        command = "openstack project list | grep -i {}".format(project_name)
        stdin, stdout, stderr = ShellHandler.execute(ShellHandler, command)

        if stdout:
            log.info("details of project : " + str(stdout))
            Report_file.add_line("details of project : " + str(stdout))
            return True
        else:
            return False
    except Exception as e:
        log.error(
            "Exception while checking project " + project_name + "ERROR: " + str(e)
        )
        assert False
    finally:
        ShellHandler.__del__(ShellHandler)


def delete_stacks_from_cee(openrc_filename, project_name, openstack_ip, username, password, all_stack=False):
    try:

        log.info("delete_stacks_from_cee : start deleting stacks exists in project %s", project_name)
        ShellHandler.__init__(ShellHandler, openstack_ip, username, password)

        command = "source {}".format(openrc_filename)
        stdin, stdout, stderr = ShellHandler.execute(ShellHandler, command)
        if all_stack:
            command = "openstack stack list"
        else:
            command = "openstack stack list | grep -i CREATE_COMPLETE"
        stdin, stdout, stderr = ShellHandler.execute(ShellHandler, command)
        log.info("Fetching stack details from CEE")
        stack_list = []
        for line in stdout:
            if "|" in line and 'Stack Name' not in line:
                stack_data = line.split("|")
                stack_list.append(stack_data[2].strip())
            else:
                continue
        if stack_list:
            vapp_stack = ""
            vnf_security_stack = ""
            for stack_name in stack_list:
                if "vapp_" in stack_name:
                    vapp_stack = stack_name
                elif "security" in stack_name:
                    vnf_security_stack = stack_name

            log.info("Executing delete stack tasks")

            if vapp_stack:
                delete_cee_stack(vapp_stack)

            deleted_stacks = \
                [delete_cee_stack(stack)
                 for stack in stack_list if all(pattern not in stack for pattern in ['vapp_', 'security'])]
            if not deleted_stacks:
                log.info("All stacks are deleted successfully")

            if vnf_security_stack:
                delete_cee_stack(vnf_security_stack)

            log.info("delete_stacks_from_cee : Finished deleting stacks exists in project %s", project_name)
        else:
            log.info("There is no stack is available for cleanup")


    except Exception as error:
        log.error("Exception while deleting stack ERROR: %s", str(error))
        assert False
    finally:
        ShellHandler.__del__(ShellHandler)


def delete_vm_instance(openrc_filename, project_name, openstack_ip, username, password):
    try:

        log.info(
            "delete VM instance from cee : start deleting VM instance exists in project "
            + project_name
        )
        Report_file.add_line(
            "delete VM instance from cee : start deleting VM instance exists in project  "
            + project_name
        )
        ShellHandler.__init__(ShellHandler, openstack_ip, username, password)
        command = "source {}".format(openrc_filename)
        stdin, stdout, stderr = ShellHandler.execute(ShellHandler, command)
        command = "openstack server list --project {}".format(project_name)
        stdin, stdout, stderr = ShellHandler.execute(ShellHandler, command)
        server_list = []
        for line in stdout:
            try:
                server_data = line.split("|")
                server_list.append(server_data[1].strip())

            except:
                log.info("")

        log.info(server_list)

        for ids in server_list[1:]:

            try:
                log.info(ids)
                command = "openstack server delete {}".format(ids)
                log.info(command)
                stdin, stdout, stderr = ShellHandler.execute(ShellHandler, command)
                time.sleep(10)

            except Exception as e:
                log.error(
                    "Error in deleting the VM instance from CEE "
                    + ids
                    + "ERROR "
                    + str(e)
                )
                Report_file.add_line(
                    "Error in deleting the VM instance from CEE " + str(e)
                )
                assert False

        log.info(
            "delete VM instance from cee : Finished deleting VM instance exists in project "
            + project_name
        )
        Report_file.add_line(
            "delete VM instance from cee : Finished deleting VM instance exists in project "
            + project_name
        )

    except Exception as e:

        log.error(
            "Error in Deletion of VM Instance exists in project "
            + project_name
            + "ERROR: "
            + str(e)
        )
        Report_file.add_line(
            "Error in Deletion of VM Instance exists in project "
            + project_name
            + "ERROR: "
            + str(e)
        )
        assert False
    finally:
        ShellHandler.__del__(ShellHandler)


def delete_block_storage(
        openrc_filename, project_name, openstack_ip, username, password
):
    try:

        log.info(
            "delete Cinder volume from cee : start deleting Cinder volume exists in project "
            + project_name
        )
        Report_file.add_line(
            "delete Cinder volume from cee : start deleting Cinder volume exists in project  "
            + project_name
        )

        ShellHandler.__init__(ShellHandler, openstack_ip, username, password)

        command = "source {}".format(openrc_filename)
        stdin, stdout, stderr = ShellHandler.execute(ShellHandler, command)
        command = "openstack volume list --project {}".format(project_name)
        stdin, stdout, stderr = ShellHandler.execute(ShellHandler, command)
        volume_list = []
        for line in stdout:
            try:
                volume_data = line.split("|")
                volume_list.append(volume_data[1].strip())

            except:
                log.info("")

        log.info(volume_list)

        for ids in volume_list[1:]:

            try:
                log.info(ids)
                command = "openstack volume delete {}".format(ids)
                log.info(command)
                stdin, stdout, stderr = ShellHandler.execute(ShellHandler, command)
                time.sleep(30)

            except Exception as e:
                log.error(
                    "Error in deleting the Cinder volume from CEE "
                    + ids
                    + "ERROR: "
                    + str(e)
                )
                Report_file.add_line(
                    "Error in deleting the cinder volume from CEE " + str(e)
                )
                assert False

        log.info(
            "delete cinder volume from cee : Finished deleting Cinder Volume exists in project "
            + project_name
        )
        Report_file.add_line(
            "delete Cinder Volume from cee : Finished deleting Cinder Volume exists in project "
            + project_name
        )

    except Exception as e:
        log.error(
            "Error while deleting Cinder Volume exists in project "
            + project_name
            + "ERROR: "
            + str(e)
        )
        Report_file.add_line(
            "Error in Deletion of Cinder Volume exists in project "
            + project_name
            + "ERROR: "
            + str(e)
        )
        assert False
    finally:
        ShellHandler.__del__(ShellHandler)


def delete_port_network(
        project_name, openrc_filename, openstack_ip, username, password
):
    try:

        ShellHandler.__init__(ShellHandler, openstack_ip, username, password)
        command = "source {}".format(openrc_filename)
        stdin, stdout, stderr = ShellHandler.execute(ShellHandler, command)

        log.info("start fetching the ports for project to delete " + project_name)

        command = """openstack port list --project {} | awk -F'|' {}""".format(
            project_name, "'{print $2}'"
        )
        Report_file.add_line("Command to fetch ports for project " + command)
        stdin, stdout, stderr = ShellHandler.execute(ShellHandler, command)

        Report_file.add_line("Command Output : " + str(stdout))
        if not stdout:

            log.info("ports for project does not exists")
            Report_file.add_line("ports for project does not exists")

        else:
            output = stdout
            total_ports = len(output)

            log.info("start deleting port for project " + project_name)
            for i in range(3, total_ports):
                port_id = output[i][:-1:].strip()
                command = "openstack port delete {}".format(port_id)
                stdin, stdout, stderr = ShellHandler.execute(ShellHandler, command)
                log.info("wait 4 seconds after delete port with id  : " + port_id)
                time.sleep(4)

        log.info("Finished deleting port for project " + project_name)

        log.info("start deleting Networks for project " + project_name)

        command = """openstack network list --project {} | awk -F'|' {}""".format(
            project_name, "'{print $2}'"
        )
        Report_file.add_line("Command to fetch networks for project " + command)
        stdin, stdout, stderr = ShellHandler.execute(ShellHandler, command)

        Report_file.add_line("Command Output : " + str(stdout))

        if not stdout:

            log.info("networks for project does not exists")
            Report_file.add_line("networks for project does not exists")

        else:
            output = stdout
            total_networks = len(output)
            for i in range(3, total_networks):
                net_id = output[i][:-1:].strip()
                command = "openstack network delete {}".format(net_id)
                stdin, stdout, stderr = ShellHandler.execute(ShellHandler, command)
                log.info("wait 5 seconds after delete network with id  : " + net_id)
                time.sleep(5)

        log.info("Finished deleting Networks for project " + project_name)

    except Exception as e:
        log.error("Exception while deleting port and network. ERROR: " + str(e))
        assert False
    finally:
        ShellHandler.__del__(ShellHandler)


def check_flavor_exists_ecm(flavor_name):
    flavor_connection = None
    try:
        log.info("Checking Flavor exists in ECM ")
        Report_file.add_line("Checking Flavor exists in ECM")
        ecm_flavor_name = flavor_name[3:]
        (
            ecm_server_ip,
            ecm_username,
            ecm_password,
        ) = Server_details.ecm_host_blade_details(Server_details)
        core_vm_ip = Server_details.ecm_host_blade_corevmip(Server_details)
        # core_vm_ip is replaced with core_vm_hostname due to token issue for Ipv6 address
        ecm_host_data = ECM_PI_Initialization.get_model_objects(
            ECM_PI_Initialization, "ECMPI"
        )
        core_vm_hostname = ecm_host_data._Ecm_PI__core_vm_hostname
        flavor_connection = ServerConnection.get_connection(ecm_server_ip, ecm_username, ecm_password)
        token = Common_utilities.authToken(
            Common_utilities, flavor_connection, core_vm_ip
        )

        command = """curl --insecure --header 'Accept: application/json' --header 'AuthToken:{}' 'https://{}/ecm_service/srts{}""".format(
            token, core_vm_hostname, "'"
        )

        Report_file.add_line("Executing curl command for flavor check " + command)
        command_output = ExecuteCurlCommand.get_json_output(flavor_connection, command)

        Report_file.add_line("Flavor check curl output  " + command_output)
        command_out = ExecuteCurlCommand.get_sliced_command_output(command_output)

        output = ast.literal_eval(command_out)

        requestStatus = output["status"]["reqStatus"]

        if "SUCCESS" in requestStatus:

            if "data" in output:
                flavor_list = output["data"]["srts"]

                for flavor in flavor_list:
                    name = flavor["name"]
                    if ecm_flavor_name == name:
                        log.info("flavor exists in ECM ")
                        return True, flavor["id"]

                log.info("flavor does not exists in ECM")
                return False, ""
            else:
                log.info("flavor data is not there output")
                return False, ""

        elif "ERROR" in requestStatus:

            command_error = output["status"]["msgs"][0]["msgText"]

            log.error(
                "Error executing curl command for checking the flavor " + command_error
            )
            Report_file.add_line(command_error)
            Report_file.add_line("Error executing curl command for checking the flavor")
            assert False

    except Exception as e:
        log.error("Exception while deleting port and network. ERROR: " + str(e))
        assert False

    finally:
        flavor_connection.close()


def delete_flavor_ecm(flavor_name, flavor_id):
    """
    delete given flavor from ECM if flavor does not exists
    in Vimzone .
    """
    connection = None
    try:
        log.info("Start deleting flavor %s from ECM", flavor_name)
        ecm_server_ip, ecm_username, ecm_password = Server_details.ecm_host_blade_details(Server_details)
        core_vm_hostname = Ecm_core.get_core_vm_hostname(Ecm_core)
        connection = ServerConnection.get_connection(ecm_server_ip, ecm_username, ecm_password)
        token = Common_utilities.authToken(Common_utilities, connection, core_vm_hostname)

        command = f'curl --insecure -X DELETE ' \
                  f'-H "authtoken:{token}" ' \
                  f'-H "content-type: application/json" ' \
                  f'"https://{core_vm_hostname}/ecm_service/srts/{flavor_id}"'

        log.info("Flavor delete command : %s", command)
        command_output = ExecuteCurlCommand.get_json_output(connection, command)
        log.info("command output: %s", str(command_output))
        command_out = ExecuteCurlCommand.get_sliced_command_output(command_output)
        output = ast.literal_eval(command_out)

        requestStatus = output['status']['reqStatus']

        if 'SUCCESS' in requestStatus:
            order_id = output['data']['order']['id']
            log.info('order id  : %s', order_id)
            order_status, order_output = Common_utilities.orderReqStatus(
                Common_utilities, connection, token, core_vm_hostname, order_id, 10
            )
            if order_status:
                log.info("Flavor %s deleted successfully", flavor_name)
            else:
                log.error("Error deleting flavor, Details : %s", str(order_output))
                assert False
        else:
            log.error("Something wrong in curl command, please check logs")
            assert False

    except Exception as e:
        log.error("Exception while deleting flavor %s , ERROR: %s", flavor_name, str(e))
        assert False
    finally:
        connection.close()


def check_flavor_exists(openrc_filename, openstack_ip, username, password, flavor_name):
    try:

        log.info("check_flavor_exists : start checking flavor exists")
        Report_file.add_line("check_flavor_exists : start checking flavor exists")
        ecm_host_data = ECM_PI_Initialization.get_model_objects(
            ECM_PI_Initialization, "ECMPI"
        )
        ecm_environment = ecm_host_data._Ecm_PI__ECM_Host_Name
        # Using the static_open_rc file , not removing from method argument to avoid changes at many places. may be later
        static_openrc_file = "openrcauto_" + ecm_environment

        ShellHandler.__init__(ShellHandler, openstack_ip, username, password)
        command = "source {}".format(static_openrc_file)
        stdin, stdout, stderr = ShellHandler.execute(ShellHandler, command)
        command = "openstack flavor list --all | grep -i {}".format(flavor_name)
        stdin, stdout, stderr = ShellHandler.execute(ShellHandler, command)
        if stdout:
            log.info("details of flavor : " + str(stdout))
            Report_file.add_line("details of flavor : " + str(stdout))

            flavor_check, flavor_id = check_flavor_exists_ecm(flavor_name)

            if flavor_check:
                log.info("Flavor is already exists in ECM and Vimzone")
                return True

            else:
                log.info("removing flavor from open stack as flavor not exists in ECM")
                command = "source {}".format(static_openrc_file)
                stdin, stdout, stderr = ShellHandler.execute(ShellHandler, command)
                command = "openstack flavor delete {}".format(flavor_name)
                stdin, stdout, stderr = ShellHandler.execute(ShellHandler, command)
                return False

        else:
            log.info("flavor %s does not exist in Vimzone, checking in ECM", flavor_name)
            flavor_check, flavor_id = check_flavor_exists_ecm(flavor_name)
            if flavor_check:
                delete_flavor_ecm(flavor_name, flavor_id)
            return False
    except Exception as e:
        log.error("Exception while checking flavor %s, ERROR: %s", flavor_name, str(e))
        assert False
    finally:
        ShellHandler.__del__(ShellHandler)


def delete_flavour(openrc_filename, openstack_ip, username, password):
    try:
        log.info("delete_flavour : start deleting flavor")
        Report_file.add_line("delete_flavour : start deleting flavor")
        sit_data = SIT_initialization.get_model_objects(SIT_initialization, "SIT")
        epg_flavors = sit_data._SIT__epg_flavors
        epg_flavors = r"\|".join(epg_flavors.split(","))
        mme_flavors = sit_data._SIT__mme_flavors
        mme_flavors = r"\|".join(mme_flavors.split(","))
        vCisco_flavor = sit_data._SIT__vcisco_flavour_name
        Valid9m_flavor = sit_data._SIT__valid9m_flavour_name
        ShellHandler.__init__(ShellHandler, openstack_ip, username, password)
        command = "source {}".format(openrc_filename)
        stdin, stdout, stderr = ShellHandler.execute(ShellHandler, command)

        sol_bgf_flavor = 'CM-TOSCA_SOL_BGF_FLAVOR'
        ecde_flavor = '3pp_ecde_flavor'
        tosca_bgf_flavor = 'CM-TOSCA_BGF_FLAVOR'
        reconcile_flavor_name = 'CM-Reconcile_SRT'
        os_reconcile_flavor_name = 'CM-Reconcile_SRT_OS'
        tosca_dummy_flavor = 'CM-Vnflaf_Etsi_Tosca_Dummy_Flavor'
        services_flavor = "CM-Auto_test_flavour"
        sol_dummy_flavor = "CM-sol005_flavor_dummy"
        flavor_name = (
            f"{services_flavor}\|"
            f"{reconcile_flavor_name}\|"
            f"{sol_bgf_flavor}\|"
            f"{tosca_dummy_flavor}\|"
            f"{tosca_bgf_flavor}\|"
            f"{os_reconcile_flavor_name}\|"
            f"{epg_flavors}\|"
            f"{ecde_flavor}\|"
            f"{sol_dummy_flavor}\|"
            f"{mme_flavors}\|"
            f"{vCisco_flavor}\|"
            f"{Valid9m_flavor}\|EOST"
        )

        command = 'openstack flavor list --all| grep -i {}'.format("'" + flavor_name + "'")
        log.info('command to list flavor ' + command)
        Report_file.add_line('command to list flavor ' + command)
        stdin, stdout, stderr = ShellHandler.execute(ShellHandler, command)
        Report_file.add_line("command output " + str(stdout))

        flavour_list = []
        if stdout:
            for items in stdout:
                flavour_data = items.split("|")
                flavour_list.append(flavour_data[2])

            for flavour in flavour_list:
                try:

                    command = "openstack flavor delete {}".format(flavour)
                    stdin, stdout, stderr = ShellHandler.execute(ShellHandler, command)

                except:
                    log.error("Error deleting the flavour " + flavour)

            log.info("delete_flavor : Finished deleting flavor")
            Report_file.add_line("delete_flavor : Finished deleting flavor")

        else:
            log.info("flavor does not exists")
            Report_file.add_line("flavor does not exists")

    except Exception as e:
        log.error("Exception while deleting flavour " + flavour + "ERROR: " + str(e))
        assert False
    finally:
        ShellHandler.__del__(ShellHandler)


def delete_project(openrc_filename, project_name, openstack_ip, username, password):
    try:

        log.info("delete_project : start deleting project " + project_name)
        Report_file.add_line("delete_project : start deleting project " + project_name)
        ShellHandler.__init__(ShellHandler, openstack_ip, username, password)
        command = "source {}".format(openrc_filename)
        stdin, stdout, stderr = ShellHandler.execute(ShellHandler, command)
        command = "openstack project delete {}".format(project_name)
        stdin, stdout, stderr = ShellHandler.execute(ShellHandler, command)
        log.info("delete_project : Finished deleting project " + project_name)
        Report_file.add_line(
            "delete_project : Finished deleting project " + project_name
        )

    except Exception as e:
        log.error(
            "Exception while deleting project " + project_name + "ERROR: " + str(e)
        )
        assert False
    finally:
        ShellHandler.__del__(ShellHandler)


def delete_users(
        ecm_environment, openrc_filename, project_name, openstack_ip, username, password
):
    try:

        log.info("delete_users : start deleting users for " + project_name)
        Report_file.add_line("delete_users : start deleting users for  " + project_name)
        ShellHandler.__init__(ShellHandler, openstack_ip, username, password)

        static_openrc_file = "openrcauto_" + ecm_environment

        command = "source {}".format(static_openrc_file)
        stdin, stdout, stderr = ShellHandler.execute(ShellHandler, command)

        command = "openstack user list | grep -i {}".format(project_name)
        stdin, stdout, stderr = ShellHandler.execute(ShellHandler, command)

        if stdout:
            for items in stdout:
                try:
                    user_data = items.split("|")
                    user = user_data[2].strip()
                    command = "openstack user delete {}".format(user)
                    stdin, stdout, stderr = ShellHandler.execute(ShellHandler, command)
                except:
                    log.error("Error deleting the user " + user)

            log.info("delete_users : Finished deleting users for " + project_name)
            Report_file.add_line(
                "delete_users : Finished deleting users for  " + project_name
            )

        else:
            log.info("user does not exists")
            Report_file.add_line("user does not exists")

    except Exception as e:
        log.error("Exception while deleting user " + user + "ERROR: " + str(e))

        assert False
    finally:
        ShellHandler.__del__(ShellHandler)
