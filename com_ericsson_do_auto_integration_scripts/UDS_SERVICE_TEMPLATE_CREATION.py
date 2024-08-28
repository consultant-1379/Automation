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

from com_ericsson_do_auto_integration_scripts.EPG_TOSCA_SO_DEPLOYMENT import epg_tosca_package_details
from com_ericsson_do_auto_integration_scripts.UDS_GENERIC_OPERATIONS import UDS_GENERIC as uds_generic
from com_ericsson_do_auto_integration_utilities.Common_utilities import Common_utilities
from com_ericsson_do_auto_integration_utilities.ExecuteCurlCommand import ExecuteCurlCommand
from com_ericsson_do_auto_integration_utilities.Json_file_handler import Json_file_handler
from com_ericsson_do_auto_integration_utilities.Logger import Logger
from com_ericsson_do_auto_integration_utilities.SIT_files_update import update_runtime_env_file
from com_ericsson_do_auto_integration_utilities.ServerConnection import ServerConnection
from com_ericsson_do_auto_integration_utilities.Server_details import Server_details
from com_ericsson_do_auto_integration_utilities.UDS_PROPERTIES import UDS_ST_CREATION as uds_params
from com_ericsson_do_auto_integration_utilities.CURL_UDS_SERVICE_TEMPLATE_CREATION import CurlUdsSTCreation as get_cmd
from com_ericsson_do_auto_integration_utilities.UDS_files_update import (update_create_uds_service_file,
                                                                         update_add_vfc_to_service_json_file,
                                                                         update_vfc_inputs_json_file,
                                                                         update_add_value_to_inputs_json_file,
                                                                         update_add_values_to_properties_file,
                                                                         update_add_inputs_file,
                                                                         update_tosca_function_file,
                                                                         update_add_directives_file,
                                                                         update_associate_vfc_file,
                                                                         update_config_file_upload)

log = Logger.get_logger("UDS_SERVICE_TEMPLATE_CREATION")


def create_uds_service():
    """
    Create UDS Service
    """
    try:
        log.info("Start to create service in UDS")
        MD5_code = "MTcxMmRhNWZjN2EwMWJiMGU4ZmQ4MTQ4ODQ5MmJmYTU="
        file_name = uds_params["uds_service_file"]
        svc_name = Common_utilities.get_name_with_random_plaintext(Common_utilities, "EPG_Service")
        log.info("Service name would be %s", svc_name)
        update_create_uds_service_file(file_name, svc_name)
        key_name_to_update = "UDS_SERVICE_UNIQUE_ID"
        create_service(file_name, key_name_to_update, MD5_code)
        update_runtime_env_file("UDS_SERVICE_UNIQUE_NAME", svc_name)
        log.info("Creating service in UDS is completed")
    except Exception as error:
        log.error("Failed to create service in UDS started: %s", str(error))
        assert False


def fetch_and_update_vfc_data():
    """
    Fetch and update VFC information to the runtime file
    """
    log.info("Start to collect VFC data")
    try:
        uds_hostname, uds_token, blade_connection = Common_utilities.get_uds_token(Common_utilities)
        command = get_cmd.get_vfc_data(uds_hostname, uds_token)
        log.info("command to get VFC data: %s", command)
        command_output = ExecuteCurlCommand.get_json_output(blade_connection, command)
        command_out = ExecuteCurlCommand.get_sliced_command_output(command_output)
        log.info("command output: %s", command_out)
        if "requestError" in command_out or not command_out:
            log.info("Failed to get VFC data")
            assert False
        command_out_dict = ast.literal_eval(command_out)
        if "Generic" in command_out_dict:
            for netwk_element in command_out_dict["Generic"]["Network Elements"]:
                if netwk_element["name"] in uds_params["vfc_names"]:
                    vfc_data = collect_vfc_data(netwk_element)
                    vfc_name = uds_params["vfc_names"][netwk_element["name"]]
                    update_runtime_env_file(f"{vfc_name}_VFC_DATA", vfc_data)
        else:
            log.error("Failed to fetch VFC data")
            assert False
        log.info("Collecting of VFC data is completed")
    except Exception as error:
        log.error("Failed to fetch VFC data :%s", str(error))
        assert False


def create_service(file_name, key_name_to_update, MD5_code):
    """
    To create a service in UDS
    @param file_name: payload json file
    @param key_name_to_update: save service id value in runtime file
    @param MD5_code: MD5 checksum code of the payload json file
    @return: ID of the UDS service generated
    """
    try:
        log.info("Started to create uds service")
        uds_hostname, uds_username, uds_password = Server_details.get_uds_host_data(Server_details)
        ecm_server_ip, ecm_username, ecm_password = Server_details.ecm_host_blade_details(Server_details)
        connection = ServerConnection.get_connection(ecm_server_ip, ecm_username, ecm_password)
        ServerConnection.put_file_sftp(connection, f"{uds_params['uds_source_path']}{file_name}",
                                       f"{uds_params['uds_dest_path']}{file_name}")
        uds_token = Common_utilities.generate_uds_token(Common_utilities, connection, uds_hostname, uds_username,
                                                        uds_password, 'master')
        command = get_cmd.create_uds_service(uds_hostname, uds_token, file_name, MD5_code)
        command_output = ExecuteCurlCommand.get_json_output(connection, command)
        command_out = ExecuteCurlCommand.get_sliced_command_output(command_output)
        if "requestError" in command_out or not command_out:
            if "already exists." in command_out:
                log.info("Service already exists in UDS")
                uds_service_id = Server_details.get_uds_service_id(Server_details)
            else:
                log.error("Request Error while creating service, check command output for more details")
                assert False
        else:
            output = ast.literal_eval(command_out)
            log.info("Fetching out unique id from command out ")
            uds_service_id = output["uniqueId"]
            log.info("create service id is %s", uds_service_id)
            update_runtime_env_file(key_name_to_update, uds_service_id)
        log.info("Creating of uds service with service id %s completed", uds_service_id)
        return uds_service_id
    except Exception as error:
        log.error("Failed to create UDS Service: %s", str(error))
        assert False

    finally:
        connection.close()


def add_vfc_to_the_service(vfc_name):
    """
    Add VFC to the UDS service
    @param vfc_name: Name of the VFC to be added to the UDS
    """
    try:
        log.info("Start to add VFC %s to the service started", vfc_name)
        vfc_data = Common_utilities.fetch_attribute_from_runtimefile(Common_utilities, f"{vfc_name}_VFC_DATA")
        vfc_input_dict_key = f"{vfc_name}_VFC_INPUT_DICT"
        log.info("Start adding the vfc %s with id %s to the service", vfc_name, vfc_data["uniqueId"])
        file_name = uds_params["add_vfc_to_service"]
        update_add_vfc_to_service_json_file(file_name, vfc_name, vfc_data["uniqueId"])
        add_vfc(file_name, vfc_input_dict_key)
        log.info("Adding VFC %s to the service is completed", vfc_name)
    except Exception as error:
        log.error("Add VFC %s to the service failed: %s", vfc_name, str(error))
        assert False


def add_vfc(file_name, vfc_input_dict_key):
    """
    Add VFC to the UDS service
    @param file_name: payload json file
    @param vfc_input_dict_key: key name to save output data of Add VFC to UDS service
    """
    blade_connection = None
    try:
        log.info("Started to add VFC to the service")
        uds_service_unique_id = Common_utilities.fetch_attribute_from_runtimefile(Common_utilities,
                                                                                  "UDS_SERVICE_UNIQUE_ID")
        uds_hostname, uds_token, blade_connection = Common_utilities.get_uds_token(Common_utilities)
        ServerConnection.put_file_sftp(blade_connection, f"{uds_params['uds_source_path']}{file_name}",
                                       f"{uds_params['uds_dest_path']}{file_name}")
        command = get_cmd.add_vfc_to_the_service(uds_hostname, uds_token, file_name, uds_service_unique_id)
        command_output = ExecuteCurlCommand.get_json_output(blade_connection, command)
        command_out = ExecuteCurlCommand.get_sliced_command_output(command_output)
        log.info("command output: %s", command_out)
        if "requestError" in command_out or not command_out:
            log.error("Failed to add VFC to the uds service")
            assert False
        command_out_dict = ast.literal_eval(command_out)

        # parse the required information from the output and save it in run time file
        vfc_ownerid = command_out_dict["capabilities"]["tosca.capabilities.Node"][0]["ownerId"]
        vfc_input_dict = {"vfc_name": command_out_dict["name"], "ownerId": vfc_ownerid,
                          "ownerName": command_out_dict["capabilities"]["tosca.capabilities.Node"][0]["ownerName"],
                          "source": command_out_dict["capabilities"]["tosca.capabilities.Node"][0]["source"],
                          "componentVersion": command_out_dict["componentVersion"],
                          "version": command_out_dict["version"], "componentUid": command_out_dict["componentUid"],
                          "invariantName": command_out_dict["invariantName"],
                          "componentName": command_out_dict["componentName"],
                          "normalizedName": command_out_dict["normalizedName"],
                          "customizationUUID": command_out_dict["customizationUUID"], "attributes": []}
        for attribute in command_out_dict["attributes"]:
            attr_dict = {
                "parentUniqueId": attribute["parentUniqueId"],
                "definition": False,
                "name": attribute["name"],
                "type": "string",
                "uniqueId": attribute["uniqueId"],
                "ownerId": attribute["ownerId"],
                "getOutputAttribute": False,
                "empty": False
            }
            vfc_input_dict["attributes"].append(attr_dict)
        feature_capability = command_out_dict["capabilities"]["tosca.capabilities.Node"][0]
        vfc_input_dict["capability_uid"] = feature_capability["uniqueId"]

        for attribute in command_out_dict["properties"]:
            parent_unique_id = attribute["parentUniqueId"] if attribute["parentUniqueId"] else vfc_ownerid
            vfc_input_dict[attribute["name"]] = {"type": attribute["type"],
                                                 "parentUniqueId": parent_unique_id,
                                                 "uniqueId": attribute["uniqueId"],
                                                 "schemaType": attribute["schemaType"]}
        vfc_input_dict["requirements"] = {}
        for requirement in command_out_dict["requirements"]["tosca.capabilities.Node"]:
            vfc_input_dict["requirements"][requirement["name"]] = {"name": requirement["name"],
                                                                   "source": requirement["source"],
                                                                   "uniqueId": requirement["uniqueId"],
                                                                   "capability": requirement["capability"],
                                                                   "ownerId": requirement["ownerId"],
                                                                   "ownerName": requirement["ownerName"]}
        update_runtime_env_file(vfc_input_dict_key, vfc_input_dict)
        log.info("Adding of VFC to the service is completed")
    except Exception as error:
        log.error("Error while adding VFC to the service %s", str(error))
        assert False

    finally:
        if blade_connection:
            blade_connection.close()


def declare_vfc_inputs(vfc_type):
    """
    Declare required inputs for the VFC and save parsed output data to runtime file
    @param vfc_type: VFC for which inputs needs to be declared
    """
    try:
        log.info("Start to declare inputs to VFC %s started", vfc_type)
        file_name = uds_params["declare_inputs"]
        inputs_dict = uds_params["inputs_to_declare"]
        vfc_inputid_dict = Common_utilities.fetch_attribute_from_runtimefile(Common_utilities,
                                                                             f"{vfc_type}_VFC_INPUT_DICT")
        update_vfc_inputs_json_file(file_name, inputs_dict[vfc_type], vfc_inputid_dict)
        vfc_declare_input_data = declare_inputs(file_name)
        update_runtime_env_file(f"{vfc_type}_DECLARE_INPUT_DATA", vfc_declare_input_data)
        log.info("Declaring of inputs to VFC %s is completed", vfc_type)
    except Exception as error:
        log.error("Failed to declare inputs to VFC: %s", str(error))
        assert False


def declare_inputs(file_name):
    """
    Declare inputs using the payload created
    @param file_name: payload json file
    @return: parsed output data
    """
    try:
        log.info("Started to declare inputs to the VFCs")
        uds_service_unique_id = Common_utilities.fetch_attribute_from_runtimefile(Common_utilities,
                                                                                  "UDS_SERVICE_UNIQUE_ID")
        uds_hostname, uds_token, blade_connection = Common_utilities.get_uds_token(Common_utilities)
        ServerConnection.put_file_sftp(blade_connection, f"{uds_params['uds_source_path']}{file_name}",
                                       f"{uds_params['uds_dest_path']}{file_name}")
        command = get_cmd.declare_vfc_inputs(uds_hostname, uds_token, file_name, uds_service_unique_id)
        log.info("command to create uds service: %s", command)
        command_output = ExecuteCurlCommand.get_json_output(blade_connection, command)
        command_out = ExecuteCurlCommand.get_sliced_command_output(command_output)
        log.info("command output: %s", command_out)
        if "requestError" in command_out or not command_out:
            log.info("Failed to create uds service")
            assert False
        command_out_dict = ast.literal_eval(command_out)
        declare_input_dict = {}
        for input_data in command_out_dict:
            declare_input_dict[input_data["properties"][0]["name"]] = {"declare_vfc_input_name": input_data["name"],
                                                                       "uniqueId": input_data["uniqueId"],
                                                                       "instanceUniqueId": input_data[
                                                                           "instanceUniqueId"],
                                                                       "propertyId": input_data["propertyId"]}

        log.info("command output: %s", command_out_dict)
        log.info("Declaring of inputs to the VFCs is completed")
        return declare_input_dict
    except Exception as error:
        log.error("Failed to add inputs to the VFCs: %s", str(error))
        assert False


def collect_vfc_data(netwk_elements):
    vfc_data = {"name": netwk_elements["name"], "uniqueId": netwk_elements["uniqueId"],
                "uuid": netwk_elements["uuid"], "description": netwk_elements["description"],
                "version": netwk_elements["version"]}
    log.info("collected VFC data is %s", str(vfc_data))
    return vfc_data


def add_values_to_the_vfc_inputs(vfc_type):
    """
    Add values to the declared inputs of the VFC
    @param vfc_type: VFC to which values to be added
    """
    try:
        log.info("Started to add values to inputs of VFC %s", vfc_type)
        file_name = uds_params["add_values_to_vfc_inputs"]
        input_value_dict = uds_params["input_value_dict"]
        vfc_declare_inputs_data = Common_utilities.fetch_attribute_from_runtimefile(Common_utilities,
                                                                                    f"{vfc_type}_DECLARE_INPUT_DATA")
        update_add_value_to_inputs_json_file(file_name, vfc_declare_inputs_data, input_value_dict[vfc_type])
        add_values_to_the_inputs(file_name)
        log.info("Adding values to inputs of VFC %s is successful", vfc_type)
    except Exception as error:
        log.error("Add values to VFC inputs failed: %s", str(error))
        assert False


def add_values_to_the_inputs(file_name):
    try:
        log.info("Start to add values to the VFC inputs")
        uds_unique_service_id = Common_utilities.fetch_attribute_from_runtimefile(Common_utilities,
                                                                                  "UDS_SERVICE_UNIQUE_ID")
        uds_hostname, uds_token, blade_connection = Common_utilities.get_uds_token(Common_utilities)
        ServerConnection.put_file_sftp(blade_connection, f"{uds_params['uds_source_path']}{file_name}",
                                       f"{uds_params['uds_dest_path']}{file_name}")
        command = get_cmd.add_values_to_the_vfc_inputs(uds_hostname, uds_token, file_name, uds_unique_service_id)
        log.info("command to add values to the inputs: %s", command)
        command_output = ExecuteCurlCommand.get_json_output(blade_connection, command)
        time.sleep(10)
        command_out = ExecuteCurlCommand.get_sliced_command_output(command_output)
        log.info("command output: %s", command_out)
        if "requestError" in command_out or not command_out:
            log.error("Failed to add values to the VFC inputs")
            assert False
        command_out_dict = ast.literal_eval(command_out)
        log.info("command output for adding values to the input: %s", command_out_dict)
        log.info("Successfully added values to the VFC inputs")
    except Exception as error:
        log.error("Failed to add values to the inputs: %s", str(error))
        assert False


def add_values_to_vfc_properties(vfc_type):
    """
    Add values to the VFC properties
    @param vfc_type: VFC for which the values to be added
    """
    try:
        log.info("Add values to the properties of the VFC, %s started", vfc_type)

        file_name = uds_params["add_values_to_properties"]
        if vfc_type == "GEOSITE":
            property_value_dict = {"type": "Data Center", "status": "operating"}
        elif vfc_type == "SUBSYSTEM":
            property_value_dict = {"status": "operating"}
        elif vfc_type == "VIMZONE0":
            property_value_dict = {"type": "Ericsson - Cloud Execution Environment (CEE)", "status": "operating"}
        elif vfc_type == "NS":
            ns_config_template = uds_params["ns_config_template"]
            ns_config_template_name = Common_utilities.get_name_with_timestamp(Common_utilities,
                                                                               ns_config_template.split(".")[0])
            update_runtime_env_file("NS_CONFIG_TEMPLATE", ns_config_template_name)
            ns_config_template_data = [{"name": "additionalParamsForNsTemplate", "catalogRef": ns_config_template_name}]
            property_value_dict = {"SO_RESOURCE::resourceType": "NetworkService", "description": "NetworkService",
                                   "SO_RESOURCE::customTemplates": str(ns_config_template_data)}
        elif vfc_type == "EPG":
            vnf_config_template = uds_params["vnf_config_template"]
            vnf_config_template_name = Common_utilities.get_name_with_timestamp(Common_utilities,
                                                                                vnf_config_template.split(".")[0])
            update_runtime_env_file("VNF_CONFIG_TEMPLATE", vnf_config_template_name)
            day1_config_template = uds_params["day1_config_template"]
            day1_config_template_name = Common_utilities.get_name_with_timestamp(Common_utilities,
                                                                                 day1_config_template.split(".")[0])
            update_runtime_env_file("DAY1_CONFIG_TEMPLATE", day1_config_template_name)
            vnf_config_template_data = [
                {"name": "additionalParamsForVnfTemplate", "catalogRef": vnf_config_template_name},
                {"name": "day1ConfigTemplate", "catalogRef": day1_config_template_name}]
            property_value_dict = {"SO_RESOURCE::resourceType": "NetworkFunction",
                                   "description": "NetworkFunction",
                                   "SO_RESOURCE::customTemplates": str(vnf_config_template_data)}

        log.info("start adding values to properties of the VFC %s", vfc_type)
        vfc_inputid_dict = Common_utilities.fetch_attribute_from_runtimefile(Common_utilities,
                                                                             f"{vfc_type}_VFC_INPUT_DICT")
        update_add_values_to_properties_file(file_name, vfc_inputid_dict, property_value_dict)
        add_values_to_the_properties(file_name, vfc_inputid_dict)
        log.info("Adding values to the properties of the VFC %s completed", vfc_type)
    except Exception as error:
        log.error("Failed to add values to properties of the VFC: %s", str(error))
        assert False


def add_values_to_the_properties(file_name, vfc_inputid_dict):
    try:
        log.info("Adding values to the properties started")
        uds_unique_service_id = Common_utilities.fetch_attribute_from_runtimefile(Common_utilities,
                                                                                  "UDS_SERVICE_UNIQUE_ID")
        uds_hostname, uds_token, blade_connection = Common_utilities.get_uds_token(Common_utilities)
        ServerConnection.put_file_sftp(blade_connection, f"{uds_params['uds_source_path']}{file_name}",
                                       f"{uds_params['uds_dest_path']}{file_name}")
        command = get_cmd.add_values_to_the_properties(uds_hostname, uds_token, file_name,
                                                       uds_unique_service_id, vfc_inputid_dict)
        log.info("command to add values to the properties: %s", command)
        command_output = ExecuteCurlCommand.get_json_output(blade_connection, command)
        command_out = ExecuteCurlCommand.get_sliced_command_output(command_output)
        log.info("command output: %s", command_out)
        if "requestError" in command_out or not command_out:
            log.error("Failed to add values to the VFC properties")
            assert False
        command_out_dict = ast.literal_eval(command_out)
        log.info("command output for adding values to the VFC properties: %s", command_out_dict)
        log.info("Adding values to the properties completed")
    except Exception as error:
        log.error("Failed to add values to the VFC properties: %s", str(error))
        assert False


def add_inputs_to_vfc(vfc_type):
    """
    Add new inputs to the VFC
    @param vfc_type: VFC to which inputs needs to be added
    """
    try:
        log.info("Start to add inputs to the VFC %s", vfc_type)
        file_name = uds_params["add_inputs_to_vfc"]
        if vfc_type == "NS":
            inputs = uds_params["inputs_to_add"]
            add_input_data = {}
            for input_name, input_type in inputs.items():
                update_add_inputs_file(file_name, input_name, input_type)
                log.info("Start to add inputs %s, type %s", input_name, input_type)
                result = add_inputs(file_name)
                add_input_data.update(result)
            log.info("Add vfc input response", add_input_data)
            update_runtime_env_file("ADD_VFC_INPUT_DATA", add_input_data)
            log.info("Adding inputs to the VFC completed %s", vfc_type)
    except Exception as error:
        log.error("Failed to add inputs to the VFC: %s", str(error))
        assert False


def add_inputs(file_name):
    try:
        log.info("Start to add inputs to VFC")
        uds_unique_service_id = Common_utilities.fetch_attribute_from_runtimefile(Common_utilities,
                                                                                  "UDS_SERVICE_UNIQUE_ID")
        uds_hostname, uds_token, blade_connection = Common_utilities.get_uds_token(Common_utilities)
        ServerConnection.put_file_sftp(blade_connection, f"{uds_params['uds_source_path']}{file_name}",
                                       f"{uds_params['uds_dest_path']}{file_name}")
        command = get_cmd.add_inputs_to_the_vfc(uds_hostname, uds_token, file_name, uds_unique_service_id)
        log.info("command to add inputs: %s", command)
        command_output = ExecuteCurlCommand.get_json_output(blade_connection, command)
        command_out = ExecuteCurlCommand.get_sliced_command_output(command_output)
        log.info("command output: %s", command_out)
        if "requestError" in command_out or not command_out:
            log.error("Failed to add inputs")
            assert False
        command_out_dict = ast.literal_eval(command_out)
        if "uniqueId" in command_out_dict:
            parsed_data = {command_out_dict["name"]: {"uniqueId": command_out_dict["uniqueId"],
                                                      "parentUniqueId": command_out_dict["parentUniqueId"],
                                                      "ownerId": command_out_dict["ownerId"]
                                                      }}
            return parsed_data
        else:
            log.error("Failed to add inputs")
        log.info("Adding inputs to the VFC completed")
    except Exception as error:
        log.error("Failed to add inputs: %s", str(error))
        assert False


def add_vfc_tosca_function(vfc_type):
    """
    Add Tosca function to the VFC
    """
    try:
        log.info("Start to add TOSCA function to VFC %s", vfc_type)
        file_name = uds_params["add_tosca_function"]
        if vfc_type == "NS":
            inputs = uds_params["ns_tosca_function_values"]
        for attribute, input_name in inputs.items():
            add_vfc_dict = Common_utilities.fetch_attribute_from_runtimefile(Common_utilities,
                                                                             f"{vfc_type}_VFC_INPUT_DICT")
            vfc_add_input_dict = Common_utilities.fetch_attribute_from_runtimefile(Common_utilities,
                                                                                   "ADD_VFC_INPUT_DATA")
            update_tosca_function_file(file_name, add_vfc_dict, vfc_add_input_dict, attribute, input_name)
            add_tosca_function(file_name, add_vfc_dict)
            log.info("Adding of TOSCA function to VFC %s is completed", vfc_type)
    except Exception as error:
        log.error("Failed to add TOSCA function to VFC %s: %s", vfc_type, str(error))
        assert False


def add_tosca_function(file_name, add_vfc_dict):
    try:
        log.info("Started to add tosca function to the VFC")
        uds_unique_service_id = Common_utilities.fetch_attribute_from_runtimefile(Common_utilities,
                                                                                  "UDS_SERVICE_UNIQUE_ID")
        uds_hostname, uds_token, blade_connection = Common_utilities.get_uds_token(Common_utilities)
        ServerConnection.put_file_sftp(blade_connection, f"{uds_params['uds_source_path']}{file_name}",
                                       f"{uds_params['uds_dest_path']}{file_name}")
        log.info("start adding tosca function")
        command = get_cmd.add_tosca_function_to_the_vfc(uds_hostname, uds_token, file_name,
                                                        uds_unique_service_id, add_vfc_dict)
        log.info("command to add tosca function: %s", command)
        command_output = ExecuteCurlCommand.get_json_output(blade_connection, command)
        command_out = ExecuteCurlCommand.get_sliced_command_output(command_output)
        log.info("command output: %s", command_out)
        if "requestError" in command_out or not command_out:
            log.error("Failed to add tosca function to the VFC")
            assert False
        log.info("Adding tosca function to the VFC completed")
    except Exception as error:
        log.error("Failed to add tosca function to the VFC: %s", str(error))
        assert False


def add_vfc_directives(vfc_type):
    """
    Add directives to the VFC
    """
    try:
        log.info("Start adding directives to the VFC %s", vfc_type)
        file_name = uds_params["add_directives"]
        fetch_vfc_data = Common_utilities.fetch_attribute_from_runtimefile(Common_utilities, f"{vfc_type}_VFC_DATA")
        add_vfc_data = Common_utilities.fetch_attribute_from_runtimefile(Common_utilities, f"{vfc_type}_VFC_INPUT_DICT")
        update_add_directives_file(file_name, fetch_vfc_data, add_vfc_data)
        add_directives(file_name, add_vfc_data)
        log.info("Adding of directives to the VFC %s completed", vfc_type)
    except Exception as error:
        log.error("Failed to add directives to %s VFC %s", vfc_type, str(error))
        assert False


def add_directives(file_name, add_vfc_data):
    try:
        log.info("Started to add directives to the VFC")
        uds_unique_service_id = Common_utilities.fetch_attribute_from_runtimefile(Common_utilities,
                                                                                  "UDS_SERVICE_UNIQUE_ID")
        uds_hostname, uds_token, blade_connection = Common_utilities.get_uds_token(Common_utilities)
        ServerConnection.put_file_sftp(blade_connection, f"{uds_params['uds_source_path']}{file_name}",
                                       f"{uds_params['uds_dest_path']}{file_name}")
        log.info("start adding directives")
        command = get_cmd.add_directives_to_the_vfc(uds_hostname, uds_token, file_name,
                                                    uds_unique_service_id, add_vfc_data)
        log.info("command to add tosca function: %s", command)
        command_output = ExecuteCurlCommand.get_json_output(blade_connection, command)
        command_out = ExecuteCurlCommand.get_sliced_command_output(command_output)
        log.info("command output: %s", command_out)
        if "requestError" in command_out or not command_out:
            log.error("Failed to create inputs")
            assert False
        log.info("Adding of directives to the VFC completed")
    except Exception as error:
        log.error("Failed to add directives to VFC: %s", str(error))
        assert False


def add_vfc_node_filter_properties(vfc_type):
    """
    Add vfc node filter properties to the each of the VFC
    """
    try:
        log.info("Start adding node filter properties to the VFC %s", vfc_type)
        declare_input_data = Common_utilities.fetch_attribute_from_runtimefile(Common_utilities,
                                                                               f"{vfc_type}_DECLARE_INPUT_DATA")
        add_vfc_data = Common_utilities.fetch_attribute_from_runtimefile(Common_utilities, f"{vfc_type}_VFC_INPUT_DICT")
        uds_unique_service_id = Common_utilities.fetch_attribute_from_runtimefile(Common_utilities,
                                                                                  "UDS_SERVICE_UNIQUE_ID")
        uds_hostname, uds_token, blade_connection = Common_utilities.get_uds_token(Common_utilities)

        file_name = uds_params["add_node_filter_properties"]
        file_path = f"{uds_params['uds_source_path']}{file_name}"
        Json_file_handler.modify_attribute(Json_file_handler, file_path, 'value',
                                           declare_input_data["name"]["declare_vfc_input_name"])
        ServerConnection.put_file_sftp(blade_connection, f"{uds_params['uds_source_path']}{file_name}",
                                       f"{uds_params['uds_dest_path']}{file_name}")
        command = get_cmd.add_vfc_node_filter_properties(uds_hostname, uds_token, file_name,
                                                         uds_unique_service_id, add_vfc_data)
        log.info("command to add node filter properties: %s", command)
        command_output = ExecuteCurlCommand.get_json_output(blade_connection, command)
        command_out = ExecuteCurlCommand.get_sliced_command_output(command_output)
        log.info("command output: %s", command_out)
        if "requestError" in command_out or not command_out:
            log.error('Failed to add node filter properties')
            assert False
        log.info("Adding of node filter properties to the VFC %s completed", vfc_type)
    except Exception as error:
        log.error("Failed to add node filter properties: %s", str(error))
        assert False


def associate_two_vfcs(vfc1, vfc2):
    """
    Associate two VFCs vfc1 and vfc2
    """
    try:
        log.info("Start associating two VFCs %s and %s", vfc1, vfc2)
        file_name = uds_params["associate_vfc"]
        log.info("start associating VFCs")
        from_vfc_data = Common_utilities.fetch_attribute_from_runtimefile(Common_utilities, f"{vfc1}_VFC_INPUT_DICT")
        to_vfc_data = Common_utilities.fetch_attribute_from_runtimefile(Common_utilities, f"{vfc2}_VFC_INPUT_DICT")
        update_associate_vfc_file(file_name, from_vfc_data, to_vfc_data)
        associate_vfcs(file_name)
        log.info("Associating of two VFCs %s and %s completed", vfc1, vfc2)
    except Exception as error:
        log.error("Failed to associate two VFCs, %s, %s: %s", vfc1, vfc2, str(error))
        assert False


def associate_vfcs(file_name):
    try:
        log.info("Started associating two VFCs")
        uds_unique_service_id = Common_utilities.fetch_attribute_from_runtimefile(Common_utilities,
                                                                                  "UDS_SERVICE_UNIQUE_ID")
        uds_hostname, uds_token, blade_connection = Common_utilities.get_uds_token(Common_utilities)
        ServerConnection.put_file_sftp(blade_connection, f"{uds_params['uds_source_path']}{file_name}",
                                       f"{uds_params['uds_dest_path']}{file_name}")
        command = get_cmd.associate_two_vfcs(uds_hostname, uds_token, file_name, uds_unique_service_id)
        log.info("command to associating two VFC: %s", command)
        command_output = ExecuteCurlCommand.get_json_output(blade_connection, command)
        blade_connection.close()
        command_out = ExecuteCurlCommand.get_sliced_command_output(command_output)
        log.info("command output: %s", command_out)
        if "requestError" in command_out or not command_out:
            log.error("Failed to associate two VFCs")
            assert False
        log.info("Associating two VFCs completed")
    except Exception as error:
        log.error("Failed to associate two VFCs: %s", str(error))
        assert False


def checkout_vfc(vfc_type):
    """
    Checkout a VFC (VFC NS) from the Catalog menu
    @param vfc_type: VFC which needs to be checked out
    """
    try:
        log.info("Start to checkout VFC %s", vfc_type)
        fetch_vfc_data = Common_utilities.fetch_attribute_from_runtimefile(Common_utilities, f"{vfc_type}_VFC_DATA")
        uds_hostname, uds_token, blade_connection = Common_utilities.get_uds_token(Common_utilities)
        command = get_cmd.checkout_vfc(uds_hostname, uds_token, fetch_vfc_data)
        log.info("command to checkout VFC: %s", command)
        command_output = ExecuteCurlCommand.get_json_output(blade_connection, command)
        command_out = ExecuteCurlCommand.get_sliced_command_output(command_output)
        log.info("command output: %s", command_out)
        if "requestError" in command_out or not command_out:
            log.error("Failed to checkout VFC %s", vfc_type)
            assert False
        output = ast.literal_eval(command_out)
        log.info("Fetching out unique id from command out ")
        vfc_unique_id = output['uniqueId']
        update_runtime_env_file(f"{vfc_type}_CHECKED_OUT_VFC_ID", vfc_unique_id)
        log.info("Checkout of VFC, %s completed", vfc_type)
    except Exception as error:
        log.error("Failed to checkout VFC %s: %s", vfc_type, str(error))
        assert False


def add_properties_to_vfc(vfc_type):
    """
    Add properties to the checked out VFC (NS)
    """
    try:
        log.info("Start to Add properties to the VfC, %s", vfc_type)
        vfc_unique_id = Common_utilities.fetch_attribute_from_runtimefile(Common_utilities,
                                                                          f"{vfc_type}_CHECKED_OUT_VFC_ID")
        inputs_dict = uds_params["ns_properties"]
        for property_name, property_type in inputs_dict.items():
            payload = {property_name: {"type": property_type, "required": False, "defaultValue": None,
                                       "description": None, "isPassword": False, "schema": {"property": {}},
                                       "name": property_name}}
            add_properties(json.dumps(payload), vfc_unique_id)
        log.info("Adding of properties to the VfC completed, %s", vfc_type)
    except Exception as error:
        log.error("Failed to to Add properties to VfC %s: %s", vfc_type, str(error))
        assert False


def add_properties(payload_json, vfc_unique_id):
    try:
        log.info("Started to add properties to VFC")
        uds_hostname, uds_token, blade_connection = Common_utilities.get_uds_token(Common_utilities)
        command = get_cmd.add_properties_to_vfc(uds_hostname, uds_token, payload_json, vfc_unique_id)
        log.info("command to add properties VFC: %s", command)
        command_output = ExecuteCurlCommand.get_json_output(blade_connection, command)
        command_out = ExecuteCurlCommand.get_sliced_command_output(command_output)
        log.info("command output: %s", command_out)

        if "requestError" in command_out or not command_out:
            if "name already exists" in command_out:
                log.info("Property name already present in the VFC")
                pass
            else:
                log.error("Failed to add properties to VFC")
                assert False
        log.info("Adding of properties to the VFC completed")
    except Exception as error:
        log.error("Failed to add properties to VFC: %s", str(error))
        assert False


def certify_vfc(vfc_type):
    """
    Certify the checked out VFC
    """
    try:
        log.info("start certifying VFC %s", vfc_type)
        vfc_id = Common_utilities.fetch_attribute_from_runtimefile(Common_utilities,
                                                                   f"{vfc_type}_CHECKED_OUT_VFC_ID")
        uds_hostname, uds_token, blade_connection = Common_utilities.get_uds_token(Common_utilities)

        payload_json = json.dumps({"userRemarks": "Certify virtNetservice vfc"})
        command = get_cmd.cetify_vfc(uds_hostname, uds_token, payload_json, vfc_id)
        log.info("command to certify VFC: %s", command)
        command_output = ExecuteCurlCommand.get_json_output(blade_connection, command)
        command_out = ExecuteCurlCommand.get_sliced_command_output(command_output)
        log.info("command output: %s", command_out)
        if "requestError" in command_out or not command_out:
            log.error('Failed to certify VFC %s', vfc_type)
            assert False
        output = ast.literal_eval(command_out)
        vfc_data = {"name": output["name"], "uniqueId": output["uniqueId"],
                    "uuid": output["uuid"], "description": output["description"],
                    "version": output["version"]}
        update_runtime_env_file("NS_VFC_DATA", vfc_data)
        log.info("Certifying of VFC %s completed", vfc_type)
    except Exception as error:
        log.error("Failed to certify VFC %s: %s", vfc_type, str(error))
        assert False


def certify_service():
    try:
        log.info("Start certifying service")
        service_id = Common_utilities.fetch_attribute_from_runtimefile(Common_utilities,
                                                                       "UDS_SERVICE_UNIQUE_ID")
        uds_hostname, uds_token, blade_connection = Common_utilities.get_uds_token(Common_utilities)
        payload_json = json.dumps({"userRemarks": "Certify service"})
        command = get_cmd.certify_service(uds_hostname, uds_token, payload_json, service_id)
        log.info("command to certify service: %s", command)
        command_output = ExecuteCurlCommand.get_json_output(blade_connection, command)
        command_out = ExecuteCurlCommand.get_sliced_command_output(command_output)
        log.info("command output: %s", command_out)
        if "requestError" in command_out or not command_out:
            log.error("Failed to certify service, %s", service_id)
            assert False
        output = ast.literal_eval(command_out)
        log.info("Fetching out unique id from command out ")
        certifyied_service_unique_id = output['uniqueId']
        update_runtime_env_file("CERTIFIED_SERVICE_ID", certifyied_service_unique_id)
        log.info("Certifying of service with service id %s completed", service_id)
    except Exception as error:
        log.error("Failed to certify service: %s", str(error))
        assert False


def upload_tosca_epg_config_templates():
    """
    Upload json TEPG configuration templates to the UDS
    """
    try:
        log.info("Start uploading of epg config template")
        service_id = Common_utilities.fetch_attribute_from_runtimefile(Common_utilities, "UDS_SERVICE_UNIQUE_ID")
        payload_file = "config_file_upload.json"
        for file_attribute in ["ns_config_template", "vnf_config_template"]:
            file = uds_params[file_attribute]
            payload_data = base64_code_for_config_file(file)
            payload_filepath = f"{uds_params['uds_source_path']}{payload_file}"
            # get template name added to the VFC of service which is saved in runtime file
            template_with_timestamp = Common_utilities.fetch_attribute_from_runtimefile(Common_utilities,
                                                                                        f"{file_attribute.upper()}")
            update_config_file_upload(payload_file, template_with_timestamp, payload_data)
            md5_code = Common_utilities.generate_MD5_checksum_for_json(Common_utilities, payload_filepath)
            uds_generic.onboard_the_template(uds_generic, "configTemplate", payload_file, md5_code, service_id)
            log.info("Uploading of config template %s completed", file)
    except Exception as error:
        log.error("Failed to upload config template: %s", str(error))
        assert False


def upload_tosca_epg_day1config_templates():
    """
    Upload TEPG day1config xml file to the UDS
    """
    try:
        log.info("Start uploading of day1 config template")
        service_id = Common_utilities.fetch_attribute_from_runtimefile(Common_utilities, "UDS_SERVICE_UNIQUE_ID")
        payload_file = "day1config_file_upload.json"
        file = uds_params["day1_config_template"]
        payload_filepath = f"{uds_params['uds_source_path']}{payload_file}"
        # get template name added to the VFC of service which is saved in runtime file
        template_with_timestamp = Common_utilities.fetch_attribute_from_runtimefile(Common_utilities,
                                                                                    "DAY1_CONFIG_TEMPLATE")
        update_config_file_upload(payload_file, template_with_timestamp, None)
        md5_code = Common_utilities.generate_MD5_checksum_for_json(Common_utilities, payload_filepath)
        uds_generic.onboard_the_template(uds_generic, "configTemplate", payload_file, md5_code, service_id)
        log.info("Uploading of config template %s completed", file)
    except Exception as error:
        log.error("Failed to upload config template: %s", str(error))
        assert False


def base64_code_for_config_file(config_file):
    log.info("Started to generate base64 code for config file %s", config_file)
    ecm_server_ip, ecm_username, ecm_password = Server_details.ecm_host_blade_details(Server_details)
    ecm_connection = ServerConnection.get_connection(ecm_server_ip, ecm_username, ecm_password)
    pkgs_dir_path, package, package_name, json_filename = epg_tosca_package_details()
    source_path = f"{pkgs_dir_path}so-artifacts/"
    log.info("Getting file %s from blade software path %s", config_file, source_path)
    dest_file = f"{source_path}{config_file}"
    source_file = f"{uds_params['uds_source_path']}{config_file}"
    ServerConnection.get_file_sftp(ecm_connection, dest_file, source_file)
    log.info("Generating base64 code for file %s", source_file)
    base64_code = Common_utilities.generate_base64_code_for_jsonfile(Common_utilities, source_file)
    log.info("Generating of base64 code for config file %s completed", config_file)
    return base64_code


def distribute_the_service_to_so():
    """
    Distribute the UDS service to the SO
    """
    try:
        log.info("Start to distribute service to SO")
        service_id = Common_utilities.fetch_attribute_from_runtimefile(Common_utilities, "CERTIFIED_SERVICE_ID")
        distribute_the_service(service_id)
        log.info("Distribution of service with service id %s to SO completed", service_id)
    except Exception as error:
        log.error("Failed to distribute service to SO: %s", str(error))
        assert False


def distribute_the_service(certified_service_unique_id):
    blade_connection = None
    try:
        log.info("Started to distribute the service with service id %s, to SO", certified_service_unique_id)
        uds_hostname, uds_token, blade_connection = Common_utilities.get_uds_token(Common_utilities)
        command = get_cmd.distribute_the_service_to_so(uds_hostname, uds_token, certified_service_unique_id)
        command_output = ExecuteCurlCommand.get_json_output(blade_connection, command)
        log.info("command to distribute the service to so: %s", command)
        command_out = ExecuteCurlCommand.get_sliced_command_output(command_output)
        log.info("command output: %s", command_out)
        if "requestError" in command_out or not command_out:
            log.error("Failed to distribute the service to SO")
            assert False
        command_out_dict = ast.literal_eval(command_out)
        artifact_name = command_out_dict['toscaArtifacts']['assettoscacsar']['artifactName']
        update_runtime_env_file("DISTRIBUTED_SERVICE_NAME", artifact_name)
        log.info("Distributing of the service with service id %s, to SO completed", certified_service_unique_id)
    except Exception as error:
        log.error("Error while distributing the service to the so: %s", str(error))
        assert False
    finally:
        if blade_connection:
            blade_connection.close()
