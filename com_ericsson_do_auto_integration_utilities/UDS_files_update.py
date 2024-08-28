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

import yaml
import json
from copy import copy
from com_ericsson_do_auto_integration_utilities.Logger import Logger
from com_ericsson_do_auto_integration_utilities.Report_file import Report_file
from com_ericsson_do_auto_integration_utilities.Json_file_handler import Json_file_handler
from com_ericsson_do_auto_integration_utilities.UDS_PROPERTIES import UDS_ST_CREATION as uds_params
from com_ericsson_do_auto_integration_utilities.Common_utilities import Common_utilities

log = Logger.get_logger('UDS_files_update.py')


def update_vfc_yaml_file(file_name,node_type,random_number):
    try:
        log.info('Start to update {} file '.format(file_name))
        Report_file.add_line('Start to update {} file '.format(file_name))
        file_path = r'com_ericsson_do_auto_integration_files/UDS_files/'+file_name
        with open(file_path) as file:
            data_dict = yaml.load(file)

        data_dict['metadata']['name'] = data_dict['metadata']['name'] + str(random_number)
        data_dict['metadata']['description'] = data_dict['metadata']['description'] + str(random_number)

        for key in data_dict['node_types'].keys():
            log.info(key)

        data_dict['node_types'][node_type + str(random_number)] = data_dict['node_types'].pop(node_type)

        if key != "com.ericsson.so.resource":

            data_dict['node_types'][node_type + str(random_number)]['derived_from'] = data_dict['node_types'][node_type + str(random_number)]['derived_from'] +str(random_number)

        with open(file_path, "w") as yaml_file:
            yaml.dump(data_dict, yaml_file, default_flow_style=False)

        log.info('Finished to update {} file '.format(file_name))
        Report_file.add_line('Finished to update {} file '.format(file_name))
    except Exception as e:

        log.error('Error to update {} file with error {}'.format(file_name, str(e)))
        Report_file.add_line('Error to update {} file with error {}'.format(file_name, str(e)))
        assert False


def update_vfc_json_file(file_name,base64_yamlfile,random_number):
    try:
        log.info('Start to update {} file '.format(file_name))
        Report_file.add_line('Start to update {} file '.format(file_name))
        file_path = r'com_ericsson_do_auto_integration_files/UDS_files/' + file_name
        with open(file_path) as file:
            data_dict = json.load(file)
        data_dict['name'] = data_dict['name'] + str(random_number)
        data_dict['description'] = data_dict['description'] + str(random_number)
        data_dict['tags'][0] = data_dict['tags'][0] + str(random_number)
        data_dict['payloadData'] = base64_yamlfile

        with open(file_path, "w") as json_file:
            json.dump(data_dict, json_file)
        log.info('Finished to update {} file '.format(file_name))
        Report_file.add_line('Finished to update {} file '.format(file_name))
    except Exception as e:

        log.error('Error to update {} file with error {}'.format(file_name, str(e)))
        Report_file.add_line('Error to update {} file with error {}'.format(file_name, str(e)))
        assert False


def update_create_uds_service_file(file_name, service_name):
    """
    Update the uds_service_file
    @param file_name: uds_service_file
    @param service_name: name of the UDS service to be created

    """
    try:
        log.info("Start to update %s file", file_name)
        Json_file_handler.modify_attribute(Json_file_handler,
                                           f"{uds_params['uds_source_path']}{file_name}", "name", service_name)
        Json_file_handler.modify_attribute(Json_file_handler,
                                           f"{uds_params['uds_source_path']}{file_name}", "tags", [service_name])
        Json_file_handler.modify_attribute(Json_file_handler,
                                           f"{uds_params['uds_source_path']}{file_name}", "description", service_name)
        log.info("Updating of %s file is completed", file_name)
    except Exception as error:
        log.error("Error while updating %s: %s", file_name, str(error))
        assert False


def update_add_vfc_to_service_json_file(file_name, vfc_name, vfc_id):
    """
    Update the payload json file to add VFC to the UDS service
    @param file_name: add_vfc_to_service payload json file
    @param vfc_name: name of the VFC to be added
    @param vfc_id: uniqueId of the VFC
    """
    try:
        log.info("Start to update %s file", file_name)
        file_path = f"{uds_params['uds_source_path']}{file_name}"
        Json_file_handler.modify_attribute(Json_file_handler, file_path, 'name', vfc_name)
        Json_file_handler.modify_attribute(Json_file_handler, file_path, 'componentUid', vfc_id)
        Json_file_handler.modify_attribute(Json_file_handler, file_path, 'uniqueId', vfc_id)
        log.info("Updating of %s file completed", file_name)
    except Exception as error:
        log.error("Error while updating the file %s: %s ", file_name, str(error))
        assert False


def update_vfc_inputs_json_file(file_name, inputs_to_add, vfc_inputid_dict):
    """
    Update payload json file for declaring inputs for VFC
    @param file_name: payload json file
    @param inputs_to_add: list of inputs to add to the VFC
    @param vfc_inputid_dict: ID of the VFC inputs to be declared
    """
    try:
        log.info("Start updating %s file", file_name)
        file = f"{uds_params['uds_source_path']}{file_name}"

        with open(file) as fp:
            file_data = json.load(fp)

        list_of_inputs = []
        for input_name in inputs_to_add:
            input_dict = copy(list(file_data["componentInstanceProperties"].values())[0][0])
            input_dict["name"] = input_name
            input_dict["origName"] = input_name
            input_dict["parentUniqueId"] = vfc_inputid_dict[input_name]["parentUniqueId"]
            input_dict["uniqueId"] = vfc_inputid_dict[input_name]["uniqueId"]
            list_of_inputs.append(input_dict)

        file_data["componentInstanceProperties"] = {vfc_inputid_dict["ownerId"]: list_of_inputs}

        Json_file_handler.update_json_file(Json_file_handler, file, file_data)
        log.info("Updating of %s file is completed", file_name)
    except Exception as error:
        log.error("Failed to update %s file: %s", file_name, str(error))
        assert False


def update_add_value_to_inputs_json_file(file_name, vfc_declare_inputs_data, input_default_value_dict):
    try:
        log.info("start to update %s file", file_name)
        file = f"{uds_params['uds_source_path']}{file_name}"

        with open(file) as fp:
            data = json.load(fp)

        list_of_inputs = []
        for input_element in input_default_value_dict:
            data_dict = copy(data[0])
            data_dict["defaultValue"] = input_default_value_dict[input_element]
            data_dict["instanceUniqueId"] = vfc_declare_inputs_data[input_element]["instanceUniqueId"]
            data_dict["name"] = vfc_declare_inputs_data[input_element]["declare_vfc_input_name"]
            data_dict["propertyId"] = vfc_declare_inputs_data[input_element]["propertyId"]
            data_dict["uniqueId"] = vfc_declare_inputs_data[input_element]['uniqueId']
            list_of_inputs.append(data_dict)

        Json_file_handler.update_json_file(Json_file_handler, file, list_of_inputs)
        log.info("Successfully updated %s file", file_name)

    except Exception as error:
        log.error("Error while updating the %s file, %s", file_name, str(error))
        assert False

def update_add_values_to_properties_file(file_name, vfc_inputid_dict, property_default_value_dict):
    try:
        log.info("Updating of file %s started", file_name)
        file = f"{uds_params['uds_source_path']}{file_name}"

        log.info("Collect contents of file %s", file_name)
        with open(file) as fp:
            data = json.load(fp)

        list_of_properties = []
        for input_name, default_value in property_default_value_dict.items():
            properties_dict = copy(data[0])
            schema_property_type = "map" if vfc_inputid_dict[input_name]["schemaType"] == "map" else None
            properties_dict["name"] = input_name
            properties_dict["parentUniqueId"] = vfc_inputid_dict[input_name]["parentUniqueId"]
            properties_dict["schema"]["property"]["type"] = schema_property_type
            properties_dict["schemaType"] = vfc_inputid_dict[input_name]["schemaType"]
            properties_dict["toscaPresentation"]["ownerId"] = vfc_inputid_dict["ownerId"]
            properties_dict["type"] = vfc_inputid_dict[input_name]["type"]
            properties_dict["uniqueId"] = vfc_inputid_dict[input_name]["uniqueId"]
            properties_dict["value"] = default_value
            list_of_properties.append(properties_dict)
        log.info("json properties %s", str(list_of_properties))
        Json_file_handler.update_json_file(Json_file_handler, file, list_of_properties)
        log.info("Updating of file %s completed", file_name)
    except Exception as error:
        log.error("Failed to update File %s: %s", file_name, str(error))
        assert False


def update_add_inputs_file(file_name, input_name, input_type):
    try:
        log.info("Start updating of file %s:", file_name)
        file = f"{uds_params['uds_source_path']}{file_name}"
        data = {input_name: {"name": input_name,
                             "schema": {"property": {"type": ""}},
                             "type": input_type}}

        log.info("json properties %s", str(data))
        Json_file_handler.update_json_file(Json_file_handler, file, data)
        log.info("Updating of file %s completed", file_name)
    except Exception as error:
        log.error("Failed to update the file: %s", str(error))
        assert False


def update_tosca_function_file(file_name, add_vfc_dict, vfc_add_input_dict, attribute, input_name):
    try:
        log.info("Start to update %s file", file_name)
        file = f"{uds_params['uds_source_path']}{file_name}"
        uds_unique_service_name = Common_utilities.fetch_attribute_from_runtimefile(Common_utilities,
                                                                                    "UDS_SERVICE_UNIQUE_NAME")
        with open(file) as fp:
            data_dict = json.load(fp)

        data_dict[0]["name"] = attribute
        data_dict[0]["origName"] = attribute
        data_dict[0]["parentUniqueId"] = add_vfc_dict[attribute]["parentUniqueId"]
        data_dict[0]["toscaFunction"]["propertyName"] = input_name
        data_dict[0]["toscaFunction"]["propertyPathFromSource"] = [input_name]
        data_dict[0]["toscaFunction"]["propertyUniqueId"] = vfc_add_input_dict[input_name]["uniqueId"]
        data_dict[0]["toscaFunction"]["sourceName"] = uds_unique_service_name
        data_dict[0]["toscaFunction"]["sourceUniqueId"] = vfc_add_input_dict[input_name]["parentUniqueId"]
        data_dict[0]["uniqueId"] = add_vfc_dict[attribute]["uniqueId"]

        log.info("json properties %s", str(data_dict))
        Json_file_handler.update_json_file(Json_file_handler, file, data_dict)
        log.info("Updating of %s file is completed", file_name)
    except Exception as error:
        log.error("Error while updating the add_vf_to_service json file %s ", str(error))
        assert False


def update_add_directives_file(file_name, fetch_vfc_data, add_vfc_data):
    try:
        log.info("Start to update file %s", file_name)
        file_path = f"{uds_params['uds_source_path']}{file_name}"
        directives = ["select", "instantiate"]
        all_versions = {add_vfc_data["componentVersion"]: add_vfc_data["source"]}

        Json_file_handler.modify_attribute(Json_file_handler, file_path, "componentUid", add_vfc_data["componentUid"])
        Json_file_handler.modify_attribute(Json_file_handler, file_path, "componentName", add_vfc_data["componentName"])
        Json_file_handler.modify_attribute(Json_file_handler, file_path, "description", fetch_vfc_data["description"])
        Json_file_handler.modify_attribute(Json_file_handler, file_path, "name", add_vfc_data["vfc_name"])
        Json_file_handler.modify_attribute(Json_file_handler, file_path, "normalizedName",
                                           add_vfc_data["normalizedName"])
        Json_file_handler.modify_attribute(Json_file_handler, file_path, "componentVersion",
                                           add_vfc_data["componentVersion"])
        Json_file_handler.modify_attribute(Json_file_handler, file_path, "uniqueId", add_vfc_data["ownerId"])
        Json_file_handler.modify_attribute(Json_file_handler, file_path, "customizationUUID",
                                           add_vfc_data["customizationUUID"])
        Json_file_handler.modify_attribute(Json_file_handler, file_path, "invariantName", add_vfc_data["invariantName"])
        Json_file_handler.modify_attribute(Json_file_handler, file_path, "directives", directives)
        Json_file_handler.modify_attribute(Json_file_handler, file_path, "tags", [add_vfc_data["componentName"]])
        Json_file_handler.modify_attribute(Json_file_handler, file_path, "version", add_vfc_data["componentVersion"])
        Json_file_handler.modify_attribute(Json_file_handler, file_path, "allVersions", all_versions)
        Json_file_handler.modify_attribute(Json_file_handler, file_path, "uuid", fetch_vfc_data["uuid"])
        Json_file_handler.modify_attribute(Json_file_handler, file_path, "systemName", fetch_vfc_data["name"])
        Json_file_handler.modify_attribute(Json_file_handler, file_path, "attributes", add_vfc_data["attributes"])
        log.info("Updating of file %s completed", file_name)
    except Exception as error:
        log.error("Failed to update file %s: %s", file_name, str(error))
        assert False


def update_associate_vfc_file(file_name, from_vfc_data, to_vfc_data):
    try:
        log.info("Start to update %s file", file_name)
        file = f"{uds_params['uds_source_path']}{file_name}"
        if to_vfc_data["componentName"] == "virtNetworkServ":
            requirement = "virtualNetServices"
        elif to_vfc_data["componentName"] == "subsystemRef":
            requirement = "subsystemReferences"
        else:
            requirement = to_vfc_data["componentName"]
        for item in from_vfc_data["requirements"].keys():
            if item == requirement:
                requirement_owner_id = from_vfc_data["requirements"][requirement]["ownerId"]
                requirement_uid = from_vfc_data["requirements"][requirement]["uniqueId"]

        data = {"fromNode": from_vfc_data["ownerId"],
                "toNode": to_vfc_data["ownerId"],
                "relationships": [{"relation": {"relationship": {"type": "tosca.capabilities.Node"},
                                                "capability": "feature",
                                                "capabilityOwnerId": to_vfc_data["ownerId"],
                                                "capabilityUid": to_vfc_data["capability_uid"],
                                                "requirement": requirement,
                                                "requirementOwnerId": requirement_owner_id,
                                                "requirementUid": requirement_uid}}],
                }

        Json_file_handler.update_json_file(Json_file_handler, file, data)
        log.info("Updating of %s file completed", file_name)
    except Exception as error:
        log.error("Failed to update file %s: %s", file_name, str(error))
        assert False


def update_config_file_upload(file_name, config_template_name, base64_code=None):
    try:
        log.info("Start to update %s file ", file_name)
        file_path = f"{uds_params['uds_source_path']}{file_name}"
        with open(file_path) as file:
            data_dict = json.load(file)
        data_dict["artifactName"] = config_template_name
        data_dict["artifactLabel"] = config_template_name.rsplit("_", 3)[0]
        if base64_code:
            data_dict["payloadData"] = base64_code

        with open(file_path, "w") as json_file:
            json.dump(data_dict, json_file)
        log.info("Finished to update %s file ", file_name)
    except Exception as error:
        log.error("Error to update %s file with error %s", file_name, str(error))
        assert False