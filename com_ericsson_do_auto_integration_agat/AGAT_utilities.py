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
'''
Created on 27 Aug 2021

@author: eiaavij
'''
from core_libs.eo.so.so_api import SoApi
from core_libs.eo.evnfm.evnfm_api import EvnfmApi
from com_ericsson_do_auto_integration_utilities.Logger import Logger
from com_ericsson_do_auto_integration_initilization.SIT_initialization import SIT_initialization
from com_ericsson_do_auto_integration_utilities.Json_file_handler import Json_file_handler

log = Logger.get_logger('AGAT_utilities')


def setup_so_api():
    """Fetching SO details"""
    log.info('Fetching the SO details')
    sit_data = SIT_initialization.get_model_objects(SIT_initialization, 'SIT')
    so_host_name = sit_data._SIT__so_host_name
    url = 'https://' + so_host_name
    username = 'staging-user'
    password = 'Testing12345!!'
    tenant = 'staging-tenant'
    return SoApi(url, username, password, tenant)


def setup_evnfm_api(evnfm_hostname, evnfm_username, evnfm_password):
    """
    Setting up E-VNFM API
    """
    log.info('Setting up E-VNFM API')
    url = 'https://' + evnfm_hostname
    tenant = 'master'
    return EvnfmApi(url, evnfm_username, evnfm_password, tenant)


def cnf_scale(instance_id, file_name, evnfm_hostname, evnfm_username, evnfm_password):
    evnfm_api = setup_evnfm_api(evnfm_hostname, evnfm_username, evnfm_password)
    payload = Json_file_handler.get_json_data(Json_file_handler, r'com_ericsson_do_auto_integration_files/' + file_name)
    response = evnfm_api.instances.scale_cnf(instance_id, payload)
    log.info('Response: %s', response)
    return response


def instantiate_cnf_agat(instance_id, file_name, evnfm_hostname, evnfm_username, evnfm_password):
    """
    Method to query a vnflcm operation for provided id
    """
    evnfm_api = setup_evnfm_api(evnfm_hostname, evnfm_username, evnfm_password)
    payload = Json_file_handler.get_json_data(Json_file_handler, r'com_ericsson_do_auto_integration_files/' + file_name)
    response = evnfm_api.instances.instantiate_cnf(instance_id, payload)
    log.info('Response: %s', response)
    return response


def terminate_cnf_agat(instance_id, file_name, evnfm_hostname, evnfm_username, evnfm_password):
    """
    Method to delete CNF instance
    """
    evnfm_api = setup_evnfm_api(evnfm_hostname, evnfm_username, evnfm_password)
    payload = Json_file_handler.get_json_data(Json_file_handler, r'com_ericsson_do_auto_integration_files/' + file_name)
    response = evnfm_api.instances.delete_cnf(instance_id, payload)
    log.info('Response: %s', response)
    return response


def delete_csar_package(package_id, evnfm_hostname, evnfm_username, evnfm_password):
    """
    Method to delete package by ID
    """
    evnfm_api = setup_evnfm_api(evnfm_hostname, evnfm_username, evnfm_password)
    response = evnfm_api.packages.delete_vnf_package(package_id)
    log.info('Response: %s', response)
    return response
