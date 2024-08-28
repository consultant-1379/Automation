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
Created on 7 Sep 2018

@author: emaidns
'''

import argparse
import textwrap
import sys
import time
import urllib3
import behave2cucumber
import json
import requests
from com_ericsson_do_auto_integration_scripts import VNF_LCM_ECM
from com_ericsson_do_auto_integration_scripts import ECM_POST_INSTALLATION
from com_ericsson_do_auto_integration_utilities.Logger import Logger
from com_ericsson_do_auto_integration_utilities.Json_file_handler import Json_file_handler
from com_ericsson_do_auto_integration_initilization.SIT_initialization import SIT_initialization
from com_ericsson_do_auto_integration_initilization.Initialization_script import Initialization_script
from com_ericsson_do_auto_integration_model.Ecm_core import Ecm_core
from com_ericsson_do_auto_integration_scripts import VNF_LCM_ENM
from com_ericsson_do_auto_integration_utilities.Report_file import Report_file
from behave import __main__ as runner_with_options
from config import DitConfig

urllib3.disable_warnings()
log = Logger.get_logger('start_script.py')

# operation name must be in CAPITAL LETTERS

operations = ['WORKFLOW-INSTALL', 'UDS-VNF-PRE-REQ', 'TEST-HOTEL-EVNFM-INTEGRATION', 'SO-SUBSYSTEM-GET', 'RPM-INSTALL',
              'TEST-HOTEL-VM-VNFM-INTEGRATION', 'MODIFY-TOSCA-EPG-PARAM', 'UDS-RESTORE-DATABASE', 'EPG-TOSCA-SO-DEPLOY',
              'EPG-TOSCA-SCALE-OUT', 'EPG-TOSCA-SCALE-IN', 'EO_STAGING_UDS_SO_TEPG_DEPLOYMENT',
              'TOSCA-EPG-HEAL', 'EVNFM-CISMS-ZONE-REGISTER', 'EVNFM-CISMS-ZONE-DEREGISTER', 'SO-CNF-CONFIGMAP-DEPL',
              'SO-CNF-CONFIGMAP-PRE_REQ', 'CDD-KEYS', 'EPG-TOSCA-PRE', 'EGAD-CERTS',
              'EO_STAGING_DISTRIBUTE_EGAD_CERTS_CN', 'ECDE-CDD-PREREQ', 'EO_STAGING_UDS_ST_CREATE_AND_DISTRIBUTE',
              'ECDE-CDD-DEPLOY', 'CCRC-SECRET', 'DISABLE-LOG', 'ENABLE-LOG', 'NAMESPACE-DEL', 'EVNFM-PACKAGE-DEL',
              'DUMMY-TOSCA-HEAL', 'EPG-ETSI-NSD-PRE', 'EPG-ETSI-NSD-DEPLOY', 'REFRESH-POD-TOKEN-EO', 'PYTEST-JOB',
              'SO-DUMMY-SCALE', 'SOL-DUMMY-PRE-REQ', 'SO-DEPLOY-SOL-DUMMY', 'L2-L3-DCGW', 'UDS-CLEANUP',
              'UDS-POST-INST', 'EPG-SCALE', 'EPG-HEAL', 'TEST-HOTEL-VIM-ADD', 'UDS-EPG-DEPLOY', 'UDS-VF', 'UDS-SERVICE',
              'UDS-VFC', 'EPG-MME-DISCOVERY', 'TEST-HOTEL-SIT', 'FETCH-VNF-MANGER-ID', 'TEST-HOTEL-LPIS',
              'TEST-HOTEL-EPIS', 'WANO-LOG', 'EVNFM-LOG', 'SO-SUBSYSTEM_LOG', 'SO-LOGVIEWER_LOG', 'IMAGE-REG',
              'CREATE-FLAVOUR', 'EO-PURGE', 'EO-CM-CERT', 'ECDE-SPIN', 'ECDE-AAT-SETUP', 'ECDE-POST-INSTALL',
              'EVNFM-TERMINATE', 'CCRC-UPGRADE-ONBOARD', 'CCRC-CNF-CLEANUP', 'WANO-SERVICE', 'EPG-VNF-ECM',
              'EPG-VNF-ECM-PRE', 'MME-VNF-ECM-PRE', 'MME-VNF-ECM', 'SOL-BGF-PRE-REQ', 'SO-DEPLOY-SOL-BGF',
              'CLUSTER-CONFIG', 'SO-DEPLOY-DUMMY', 'DUMMY-NODE-HEAL', 'SO-LOGVIEWER-ROLE', 'SO-SUBSYSTEM-CHECK',
              'SO-RANDOM-TASK', 'CCRC-CNF-UPGRADE', 'CCRC-CNF-SCALE', 'CCRC-CNF-ONBOARD', 'CCRC-CNF-DEPLOY',
              'CCRC-CNF-TERMINATE', 'SO-DEPLOY-LCM-VM-SHUT', 'EPG-SO-VM-VNFM', 'EPG-PRE-VM-VNFM', 'MME-PRE-VM-VNFM',
              'MME-SO-VM-VNFM', 'MODIFY_TOSCA_DUMMY_PARAM', 'ECM-SESSION-UPDATE', 'EOCM-DUMMY-SCALE',
              'CISMS-ZONE-REGISTER', 'CISMS-ZONE-DEREGISTER', 'ETSI_TOSCA_DUMMY_DEPLOYMENT',
              'ETSI_DUMMY_TOSCA_SCALE_HEAL', 'VM-VNFM-INTEGRATION', 'SO-DUMMY-VM-VNFM', 'MME-REDISCOVERY',
              'ENM-LCM-INTEGRATION', 'ECM-PACKAGE-DEL', 'VBGF_TOSCA_PRE', 'ENM-POST', 'VBGF_TOSCA_DEPLOY',
              'RECONCILE-DUMMY', 'ECDE-ECM-3PP-DEPLOY', 'SO-CCD', 'EPG-REDISCOVERY', 'ECDE-DYANAMIC-VNFLCM-DEPLOY',
              'ECDE-EVNFM-DUMMY-DEPLOY', 'ECDE-ECM-DEPLOY', 'VNF-ECM', 'ECDE-EVNFM-PRE', 'ECDE-ECM-PRE',
              'ECDE-VNFLCM-PRE', 'SC', 'RVPC', 'EPIS', 'SIT', 'VNF-ENM', 'CEE-CLEANUP', 'SYNC-VIM-CAPACITY', 'PROJ-VIM',
              'LPIS', 'SIT-SO', 'SO-CLEANUP', 'EPG-ECM', 'EPG-ECM-PRE', 'EPG-SO', 'MME-PRE', 'MME-SO', 'SBG-ECM',
              'SBG-ECM-PRE', 'MTAS-ECM', 'MTAS-ECM-PRE', 'CSCF-ECM', 'CSCF-ECM-PRE', 'BGF-ECM', 'BGF-ECM-PRE',
              'VCISCO-DEPLOY', 'DC-GATEWAY', 'DUMMY-MME', 'SO-SERVICES-DEL', 'ECM-DEL', 'LPIS-DYNAMIC', 'SIT-EO-VNFLCM',
              'LCM-VM-SHUT-STATIC', 'LCM-VM-SHUT-DYNAMIC', 'IMS-ECM-PRE', 'SO-POST', 'CNF-NS-INSTANTIATION-PRE-REQ',
              'EO_STAGING_ECM_CNF_ONBOARD', 'EO_STAGING_ECM_CNF_NS_DEPLOY', 'COLLECT-RUNTIME-DATA',
              'COLLECT-METRICS-TESTS', 'EO_STAGING_ECM_CNF_NS_SCALE_IN', 'EO_STAGING_ECM_CNF_NS_SCALE_OUT',
              'EO_STAGING_ECM_NS_TERMINATE', 'CNFNS-DELETE-SECRET-EVNFM', 'TOSCA-PRETOSCA-WORKFLOW-DEPL',
              'EAIND-SUPERUSER-CREATION', 'EO_STAGING_TOSCA_EPG_ECM_SCALE', 'VERIFY-PROJECT-EXISTS-CCM',
              'ENM-TOSCA-NODE-CLEANUP', 'CHECK-POD-RESTARTS', 'EO_STAGING_EPG_TOSCA_ECM_DEPLOY',
              'EO_STAGING_ECM_EPG_ETSI_TOSCA_DEPLOY', 'ENM-ETSI-TOSCA-NODE-CLEANUP', 'UDS-NFV-PRE-REQ',
              'UDS-DELETE-PRE-REQ', 'TEST-HOTEL-NETWORK-ADD', 'EO_STAGING_ECM_CNF_NS_REMOVE', 'EO_STAGING_ECM_CNF_NS_ADD',
              'EO_STAGING_NS_PDB_CHECK', 'EO_STAGING_HELM_CHART_VERSION', 'EO_STAGING_MODIFY_CISMS_ZONE',
              'EO_STAGING_ECM_CMDB_VAPP_CLEANUP', 'EO_STAGING_ECM_CMDB_NS_CLEANUP',
              'EO_STAGING_OPENSTACK_STACK_CLEANUP', 'NODESELCTOR-VERIFICATION',
              'EO_STAGING_MONITOR_UNAPPROVED_RESOURCES_DEPLOYED']


def error(self, message):
    sys.stderr.write('error: %s\n' % message)
    self.print_help(self)
    sys.exit(2)


def update_duration_in_cucumber_json():
    try:

        log.info('start updating duration from behave format to cucumber format ')
        with open('cucumber_reports/cucumber.json', 'r') as jsonFile:
            print('file open')
            data = json.load(jsonFile)
            for item in data:
                elements = item['elements']
                for element in elements:
                    steps = element['steps']
                    for step in steps:
                        duration = step['result']['duration']
                        step['result']['duration'] = round(duration * 1000000000)

        with open('cucumber_reports/cucumber.json', "w+") as jsonFile:
            json.dump(data, jsonFile, indent=4, sort_keys=False)
    except Exception as e:
        log.error('Error while updating duration in cucumber report file ' + str(e))


def generate_cucumber_report():
    with open('reports/output.json') as behave_json:
        cucumber_json = behave2cucumber.convert(json.load(behave_json))

    with open('cucumber_reports/cucumber.json', "w+") as jsonFile:
        json.dump(cucumber_json, jsonFile, indent=4, sort_keys=False)

    update_duration_in_cucumber_json()


def is_serializable(payload):
    try:
        payload.json()
    except AttributeError as e:
        log.error(str(e))
        return False
    return True


def validate_dit(dit_name):
    retry = DitConfig.RETRIES.value
    url = f"{DitConfig.DIT_URL.value}{dit_name}"

    while retry >= 0:
        resp = requests.get(url, verify=False)

        if is_serializable(resp):
            return resp
        else:
            if retry <= 0:
                assert False
            retry -= 1
            time.sleep(1)
            log.info("Retrying to fetch DIT")


def get_do_init(dit_name, user_input_file):
    try:
        log.info('Start fetching out data from DIT for document %s', dit_name)
        Report_file.add_line('Content data command ' + f"{DitConfig.DIT_URL.value}{dit_name}")

        resp = validate_dit(dit_name)
        content = resp.json()
        data = (content[0]['content'])
        Json_file_handler.update_json_file(Json_file_handler, user_input_file, data)

        log.info('Finished fetching data from DIT: %s', dit_name)

    except Exception as e:
        log.error('Error fetching user input from DIT: %s', str(e))
        assert False


def start_execution(operation, dit_document_name, parser, vnf_type, user_input):
    user_input_file = 'do_init.json'

    if user_input == 'True':
        log.info('It is productize version of automation , Reading the user input file (do_init.json) for this task')
    else:
        log.info('It is for non productize version of automation , Reading the user input file from DIT')
        get_do_init(dit_document_name, user_input_file)

    if operation not in operations:
        print('Message :  operation not matched : ' + operation + '\n\n***Please refer the help ***\n')
        print(parser.description)
        assert False

    # validate the Do_init file
    schema_file = r'com_ericsson_do_auto_integration_files/schema.json'
    Json_file_handler.validate_schema(Json_file_handler, schema_file, user_input_file)

    if operation == 'VNF-ECM':
        log.info('operation : ' + operation + ' input file path : ' + user_input_file)
        ECM_POST_INSTALLATION.initialize_user_input(user_input_file)
        Initialization_script.store_user_input(Initialization_script, user_input_file)
        Initialization_script.store_LCM_service_server_data(Initialization_script, user_input_file)
        VNF_LCM_ECM.main()

    elif operation == 'PYTEST-JOB':

        log.info('operation : ' + operation + ' input file path : ' + user_input_file)
        ECM_POST_INSTALLATION.initialize_user_input(user_input_file)
        Initialization_script.store_user_input(Initialization_script, user_input_file)

        SIT_initialization.initialize_user_input(SIT_initialization, user_input_file, vnf_type=vnf_type)

    elif operation == 'SC':
        log.info('operation : ' + operation + ' input file path : ' + user_input_file)
        ECM_POST_INSTALLATION.initialize_user_input(user_input_file)
        ECM_POST_INSTALLATION.site_creation()

    elif operation == 'SO-SUBSYSTEM-GET':

        log.info('operation : ' + operation + ' input file path : ' + user_input_file)

        ECM_POST_INSTALLATION.initialize_user_input(user_input_file)
        Initialization_script.store_user_input(Initialization_script, user_input_file)
        Initialization_script.store_LCM_service_server_data(Initialization_script, user_input_file)
        SIT_initialization.initialize_user_input(SIT_initialization, user_input_file)

        report_file_related = ' -f=json.pretty -o=reports/output.json' + ' '
        feature_file_path = r'so_random_operations/features/so_get_subsystem.feature '
        options = ' --no-capture --no-capture-stderr --no-logcapture -f plain'

        full_runner_options = report_file_related + feature_file_path + options

        runner_with_options.main(full_runner_options)
        generate_cucumber_report()

    elif operation == 'SO-LOGVIEWER-ROLE':
        log.info('operation : ' + operation + ' input file path : ' + user_input_file)

        ECM_POST_INSTALLATION.initialize_user_input(user_input_file)
        Initialization_script.store_user_input(Initialization_script, user_input_file)
        Initialization_script.store_LCM_service_server_data(Initialization_script, user_input_file)
        SIT_initialization.initialize_user_input(SIT_initialization, user_input_file)

        report_file_related = ' -f=json.pretty -o=reports/output.json' + ' '
        feature_file_path = r'so_random_operations/features/so_log_view_user.feature '
        options = ' --no-capture --no-capture-stderr --no-logcapture -f plain'

        full_runner_options = report_file_related + feature_file_path + options

        runner_with_options.main(full_runner_options)
        generate_cucumber_report()


    elif operation == 'SO-SUBSYSTEM-CHECK':
        log.info('operation : ' + operation + ' input file path : ' + user_input_file)

        ECM_POST_INSTALLATION.initialize_user_input(user_input_file)
        Initialization_script.store_user_input(Initialization_script, user_input_file)
        Initialization_script.store_LCM_service_server_data(Initialization_script, user_input_file)
        SIT_initialization.initialize_user_input(SIT_initialization, user_input_file)

        report_file_related = ' -f=json.pretty -o=reports/output.json' + ' '
        feature_file_path = r'so_random_operations/features/so_check_subsystem.feature '
        options = ' --no-capture --no-capture-stderr --no-logcapture -f plain'

        full_runner_options = report_file_related + feature_file_path + options

        runner_with_options.main(full_runner_options)
        generate_cucumber_report()



    elif operation == 'SO-RANDOM-TASK':
        log.info('operation : ' + operation + ' input file path : ' + user_input_file)

        ECM_POST_INSTALLATION.initialize_user_input(user_input_file)
        Initialization_script.store_user_input(Initialization_script, user_input_file)
        Initialization_script.store_LCM_service_server_data(Initialization_script, user_input_file)
        SIT_initialization.initialize_user_input(SIT_initialization, user_input_file, vnf_type=vnf_type.upper())

        report_file_related = ' -f=json.pretty -o=reports/output.json' + ' '
        feature_file_path = r'so_random_operations/features/so_subsystem_create.feature '
        options = ' --no-capture --no-capture-stderr --no-logcapture -f plain'

        full_runner_options = report_file_related + feature_file_path + options

        runner_with_options.main(full_runner_options)
        generate_cucumber_report()


    elif operation == 'EPG-MME-DISCOVERY':

        log.info('operation : ' + operation + ' input file path : ' + user_input_file)
        ECM_POST_INSTALLATION.initialize_user_input(user_input_file)
        Initialization_script.store_user_input(Initialization_script, user_input_file)
        SIT_initialization.initialize_user_input(SIT_initialization, user_input_file)

        report_file_related = ' -f=json.pretty -o=reports/output.json' + ' '
        feature_file_path = r'epg_mme_discovery/features/epg_mme_discovery.feature  '
        options = ' --no-capture --no-capture-stderr --no-logcapture -f plain'

        full_runner_options = report_file_related + feature_file_path + options

        runner_with_options.main(full_runner_options)
        generate_cucumber_report()



    elif operation == 'TOSCA-PRETOSCA-WORKFLOW-DEPL':
        log.info('operation : ' + operation + ' input file path : ' + user_input_file)

        ECM_POST_INSTALLATION.initialize_user_input(user_input_file)
        Initialization_script.store_user_input(Initialization_script, user_input_file)
        Initialization_script.store_LCM_service_server_data(Initialization_script, user_input_file)
        SIT_initialization.initialize_user_input(SIT_initialization, user_input_file)

        report_file_related = ' -f=json.pretty -o=reports/output.json' + ' '
        feature_file_path = r'tosca_pretosca_workflow_deployment/features/tosca_pretosca_workflow_deployment.feature '
        options = ' --no-capture --no-capture-stderr --no-logcapture -f plain'

        full_runner_options = report_file_related + feature_file_path + options

        runner_with_options.main(full_runner_options)
        generate_cucumber_report()

    elif operation == 'SO-CCD':
        log.info('operation : ' + operation + ' input file path : ' + user_input_file)
        ECM_POST_INSTALLATION.initialize_user_input(user_input_file)
        SIT_initialization.initialize_user_input(SIT_initialization, user_input_file)
        report_file_related = ' -f=json.pretty -o=reports/output.json' + ' '
        feature_file_path = r'epg_node_deployment/features/so_ccd.feature '
        options = ' --no-capture --no-capture-stderr --no-logcapture -f plain'

        full_runner_options = report_file_related + feature_file_path + options

        runner_with_options.main(full_runner_options)
        generate_cucumber_report()

    elif operation == 'ENM-POST':
        log.info('operation : ' + operation + ' input file path : ' + user_input_file)
        ECM_POST_INSTALLATION.initialize_user_input(user_input_file)
        Initialization_script.store_user_input(Initialization_script, user_input_file)
        Initialization_script.store_LCM_service_server_data(Initialization_script, user_input_file)
        SIT_initialization.initialize_user_input(SIT_initialization, user_input_file)

        report_file_related = ' -f=json.pretty -o=reports/output.json' + ' '
        feature_file_path = r'enm_post_installation/features/enm_post_installation.feature '
        options = ' --no-capture --no-capture-stderr --no-logcapture -f plain'

        full_runner_options = report_file_related + feature_file_path + options

        runner_with_options.main(full_runner_options)
        generate_cucumber_report()




    elif operation == 'RVPC':
        log.info('operation : ' + operation + ' input file path : ' + user_input_file)
        ECM_POST_INSTALLATION.initialize_user_input(user_input_file)
        ECM_POST_INSTALLATION.vim_registration()
        ECM_POST_INSTALLATION.project_creation()

    elif operation == 'TEST-HOTEL-EVNFM-INTEGRATION':

        log.info('operation : ' + operation + ' input file path : ' + user_input_file)
        ECM_POST_INSTALLATION.initialize_user_input(user_input_file)
        Initialization_script.store_user_input(Initialization_script, user_input_file)
        SIT_initialization.initialize_user_input(SIT_initialization, user_input_file)

        report_file_related = ' -f=json.pretty -o=reports/output.json' + ' '
        feature_file_path = r'test_hotel/features/test_hotel_evnfm_integration.feature  '
        options = ' --no-capture --no-capture-stderr --no-logcapture -f plain'

        full_runner_options = report_file_related + feature_file_path + options

        runner_with_options.main(full_runner_options)
        generate_cucumber_report()

    elif operation == 'TEST-HOTEL-VM-VNFM-INTEGRATION':
        log.info('operation : ' + operation + ' input file path : ' + user_input_file)
        ECM_POST_INSTALLATION.initialize_user_input(user_input_file)
        Initialization_script.store_user_input(Initialization_script, user_input_file)
        SIT_initialization.initialize_user_input(SIT_initialization, user_input_file)

        report_file_related = ' -f=json.pretty -o=reports/output.json' + ' '
        feature_file_path = r'test_hotel/features/test_hotel_vm_vnfm_integration.feature'
        options = ' --no-capture --no-capture-stderr --no-logcapture -f plain'

        full_runner_options = report_file_related + feature_file_path + options

        runner_with_options.main(full_runner_options)
        generate_cucumber_report()

    elif operation == 'TEST-HOTEL-NETWORK-ADD':
        log.info('operation : ' + operation + ' input file path : ' + user_input_file)
        ECM_POST_INSTALLATION.initialize_user_input(user_input_file)
        SIT_initialization.initialize_user_input(SIT_initialization, user_input_file)

        report_file_related = ' -f=json.pretty -o=reports/output.json' + ' '
        feature_file_path = r'test_hotel/features/test_hotel_ecm_create_network.feature'
        options = ' --no-capture --no-capture-stderr --no-logcapture -f plain'

        full_runner_options = report_file_related + feature_file_path + options

        runner_with_options.main(full_runner_options)
        generate_cucumber_report()

    elif operation == 'TEST-HOTEL-EPIS':
        log.info('operation : ' + operation + ' input file path : ' + user_input_file)
        ECM_POST_INSTALLATION.initialize_user_input(user_input_file)
        SIT_initialization.initialize_user_input(SIT_initialization, user_input_file)

        report_file_related = ' -f=json.pretty -o=reports/output.json' + ' '
        feature_file_path = r'test_hotel/features/test_hotel_ecm_post_installation.feature'
        options = ' --no-capture --no-capture-stderr --no-logcapture -f plain'

        full_runner_options = report_file_related + feature_file_path + options

        runner_with_options.main(full_runner_options)
        generate_cucumber_report()


    elif operation == 'TEST-HOTEL-VIM-ADD':
        log.info('operation : ' + operation + ' input file path : ' + user_input_file)

        ECM_POST_INSTALLATION.initialize_user_input(user_input_file)
        Initialization_script.store_user_input(Initialization_script, user_input_file)
        Initialization_script.store_LCM_service_server_data(Initialization_script, user_input_file)
        SIT_initialization.initialize_user_input(SIT_initialization, user_input_file)

        report_file_related = ' -f=json.pretty -o=reports/output.json' + ' '
        feature_file_path = r'test_hotel/features/test_hotel_vim_addition.feature'
        options = ' --no-capture --no-capture-stderr --no-logcapture -f plain'

        full_runner_options = report_file_related + feature_file_path + options

        runner_with_options.main(full_runner_options)
        generate_cucumber_report()


    elif operation == 'TEST-HOTEL-LPIS':
        log.info('operation : ' + operation + ' input file path : ' + user_input_file)

        ECM_POST_INSTALLATION.initialize_user_input(user_input_file)
        Initialization_script.store_user_input(Initialization_script, user_input_file)
        Initialization_script.store_LCM_service_server_data(Initialization_script, user_input_file)
        SIT_initialization.initialize_user_input(SIT_initialization, user_input_file)

        report_file_related = ' -f=json.pretty -o=reports/output.json' + ' '
        feature_file_path = r'test_hotel/features/test_hotel_lcm_post_installation.feature'
        options = ' --no-capture --no-capture-stderr --no-logcapture -f plain'

        full_runner_options = report_file_related + feature_file_path + options

        runner_with_options.main(full_runner_options)
        generate_cucumber_report()


    elif operation == 'NAMESPACE-DEL':

        log.info(
            'operation : ' + operation + ' input file path : ' + user_input_file + ' with VNF_TYPE ' + str(vnf_type))
        ECM_POST_INSTALLATION.initialize_user_input(user_input_file)
        # vnf type is namespaces string comma saperated , no need to make it capital otherwise issue may occur while deletion
        SIT_initialization.initialize_user_input(SIT_initialization, user_input_file, vnf_type=vnf_type)
        report_file_related = ' -f=json.pretty -o=reports/output.json' + ' '
        feature_file_path = r'ccd_namspace_delete/features/ccd_namespace_delete.feature '
        options = ' --no-capture --no-capture-stderr --no-logcapture -f plain'

        full_runner_options = report_file_related + feature_file_path + options

        runner_with_options.main(full_runner_options)
        generate_cucumber_report()

    elif operation == 'FETCH-VNF-MANGER-ID':
        log.info('operation : ' + operation + ' input file path : ' + user_input_file)

        ECM_POST_INSTALLATION.initialize_user_input(user_input_file)
        Initialization_script.store_user_input(Initialization_script, user_input_file)
        Initialization_script.store_LCM_service_server_data(Initialization_script, user_input_file)

        report_file_related = ' -f=json.pretty -o=reports/output.json' + ' '
        feature_file_path = r'test_hotel/features/fetch_vnf_manager_id.feature'
        options = ' --no-capture --no-capture-stderr --no-logcapture -f plain'

        full_runner_options = report_file_related + feature_file_path + options

        runner_with_options.main(full_runner_options)
        generate_cucumber_report()

    elif operation == 'EPIS':
        log.info('operation : ' + operation + ' input file path : ' + user_input_file)
        ECM_POST_INSTALLATION.initialize_user_input(user_input_file)
        SIT_initialization.initialize_user_input(SIT_initialization, user_input_file)

        report_file_related = ' -f=json.pretty -o=reports/output.json' + ' '
        feature_file_path = r'ecm_post_installation/features/ecm_post_installation.feature '
        options = ' --no-capture --no-capture-stderr --no-logcapture -f plain'

        full_runner_options = report_file_related + feature_file_path + options

        runner_with_options.main(full_runner_options)
        generate_cucumber_report()

    elif operation == 'ETSI_TOSCA_DUMMY_DEPLOYMENT':

        log.info('operation : ' + operation + ' input file path : ' + user_input_file)
        ECM_POST_INSTALLATION.initialize_user_input(user_input_file)
        SIT_initialization.initialize_user_input(SIT_initialization, user_input_file)

        report_file_related = ' -f=json.pretty -o=reports/output.json' + ' '
        feature_file_path = r'etsi_tosca_dummy_deployment/features/etsi_tosca_dummy_deployment.feature  '
        options = ' --no-capture --no-capture-stderr --no-logcapture -f plain'

        full_runner_options = report_file_related + feature_file_path + options

        runner_with_options.main(full_runner_options)
        generate_cucumber_report()

    elif operation == 'ETSI_DUMMY_TOSCA_SCALE_HEAL':

        log.info('operation : ' + operation + ' input file path : ' + user_input_file)
        ECM_POST_INSTALLATION.initialize_user_input(user_input_file)
        SIT_initialization.initialize_user_input(SIT_initialization, user_input_file)
        Initialization_script.store_user_input(Initialization_script, user_input_file)

        report_file_related = ' -f=json.pretty -o=reports/output.json' + ' '
        feature_file_path = r'etsi_dummy_tosca_scaleheal/features/etsi_dummy_tosca_scaleheal.feature  '
        options = ' --no-capture --no-capture-stderr --no-logcapture -f plain'

        full_runner_options = report_file_related + feature_file_path + options

        runner_with_options.main(full_runner_options)
        generate_cucumber_report()


    elif operation == 'CDD-KEYS':

        log.info('operation : ' + operation + ' input file path : ' + user_input_file)
        ECM_POST_INSTALLATION.initialize_user_input(user_input_file)
        SIT_initialization.initialize_user_input(SIT_initialization, user_input_file, vnf_type=vnf_type)
        Initialization_script.store_user_input(Initialization_script, user_input_file)

        report_file_related = ' -f=json.pretty -o=reports/output.json' + ' '
        feature_file_path = r'ccd_post_install/features/update_authorize_key.feature'
        options = ' --no-capture --no-capture-stderr --no-logcapture -f plain'

        full_runner_options = report_file_related + feature_file_path + options

        runner_with_options.main(full_runner_options)
        generate_cucumber_report()


    elif operation == 'EGAD-CERTS':

        log.info('operation: %s input file path: %s  CCD1 environment %s ', operation, user_input_file, str(vnf_type))
        ECM_POST_INSTALLATION.initialize_user_input(user_input_file)
        SIT_initialization.initialize_user_input(SIT_initialization, user_input_file, vnf_type=vnf_type)
        Initialization_script.store_user_input(Initialization_script, user_input_file)

        report_file_related = ' -f=json.pretty -o=reports/output.json' + ' '
        feature_file_path = r'ccd_post_install/features/distribute_egad_certs.feature '
        options = ' --no-capture --no-capture-stderr --no-logcapture -f plain'

        full_runner_options = report_file_related + feature_file_path + options

        runner_with_options.main(full_runner_options)
        generate_cucumber_report()

    elif operation == 'EO_STAGING_DISTRIBUTE_EGAD_CERTS_CN':

        log.info('operation: %s input file path: %s  CCD1 environment %s ', operation, user_input_file, str(vnf_type))
        ECM_POST_INSTALLATION.initialize_user_input(user_input_file)
        SIT_initialization.initialize_user_input(SIT_initialization, user_input_file, vnf_type=vnf_type)
        Initialization_script.store_user_input(Initialization_script, user_input_file)

        report_file_related = ' -f=json.pretty -o=reports/output.json' + ' '
        feature_file_path = r'ccd_post_install/features/distribute_egad_certs_cn.feature '
        options = ' --no-capture --no-capture-stderr --no-logcapture -f plain'

        full_runner_options = report_file_related + feature_file_path + options

        runner_with_options.main(full_runner_options)
        generate_cucumber_report()


    elif operation == 'MODIFY_TOSCA_DUMMY_PARAM':

        log.info('operation : ' + operation + ' input file path : ' + user_input_file)
        ECM_POST_INSTALLATION.initialize_user_input(user_input_file)
        SIT_initialization.initialize_user_input(SIT_initialization, user_input_file)
        Initialization_script.store_user_input(Initialization_script, user_input_file)

        report_file_related = ' -f=json.pretty -o=reports/output.json' + ' '
        feature_file_path = r'etsi_tosca_dummy_deployment/features/modify_tosca_dummy_params.feature  '
        options = ' --no-capture --no-capture-stderr --no-logcapture -f plain'

        full_runner_options = report_file_related + feature_file_path + options

        runner_with_options.main(full_runner_options)
        generate_cucumber_report()


    elif operation == 'MODIFY-TOSCA-EPG-PARAM':

        log.info('operation : %s input file path : %s', operation, user_input_file)
        ECM_POST_INSTALLATION.initialize_user_input(user_input_file)
        SIT_initialization.initialize_user_input(SIT_initialization, user_input_file)
        Initialization_script.store_user_input(Initialization_script, user_input_file)

        report_file_related = ' -f=json.pretty -o=reports/output.json' + ' '
        feature_file_path = r'epg_tosca_deployment/features/modify_epg_tosca_params.feature  '
        options = ' --no-capture --no-capture-stderr --no-logcapture -f plain'

        full_runner_options = report_file_related + feature_file_path + options

        runner_with_options.main(full_runner_options)
        generate_cucumber_report()


    elif operation == 'WANO-SERVICE':

        log.info('operation : ' + operation + ' input file path : ' + user_input_file)
        ECM_POST_INSTALLATION.initialize_user_input(user_input_file)
        ECM_POST_INSTALLATION.initialize_user_input(user_input_file)
        SIT_initialization.initialize_user_input(SIT_initialization, user_input_file)

        report_file_related = ' -f=json.pretty -o=reports/output.json' + ' '
        feature_file_path = r'wano_usecases/features/wano_service_test.feature  '
        options = ' --no-capture --no-capture-stderr --no-logcapture -f plain'

        full_runner_options = report_file_related + feature_file_path + options

        runner_with_options.main(full_runner_options)
        generate_cucumber_report()

    elif operation == 'COLLECT-METRICS-TESTS':

        log.info('operation : ' + operation + ' input file path : ' + user_input_file)
        SIT_initialization.initialize_user_input(SIT_initialization, user_input_file)

        report_file_related = ' -f=json.pretty -o=reports/output.json' + ' '
        feature_file_path = r'codeploy_metrics_test/features/codeploy_metrics_test.feature  '
        options = ' --no-capture --no-capture-stderr --no-logcapture -f plain'

        full_runner_options = report_file_related + feature_file_path + options

        runner_with_options.main(full_runner_options)
        generate_cucumber_report()

    elif operation == 'SIT':
        log.info('operation : ' + operation + ' input file path : ' + user_input_file)
        ECM_POST_INSTALLATION.initialize_user_input(user_input_file)
        SIT_initialization.initialize_user_input(SIT_initialization, user_input_file)

        report_file_related = ' -f=json.pretty -o=reports/output.json' + ' '
        feature_file_path = r'integration_usecases/features/onboard_package.feature integration_usecases/features/deploy_package.feature integration_usecases/features/delete_package.feature integration_usecases/features/so_node_deploy.feature integration_usecases/features/scale_heal_vm.feature '
        options = ' --no-capture --no-capture-stderr --no-logcapture -f plain'

        full_runner_options = report_file_related + feature_file_path + options

        runner_with_options.main(full_runner_options)
        generate_cucumber_report()


    elif operation == 'TEST-HOTEL-SIT':
        log.info('operation : ' + operation + ' input file path : ' + user_input_file)
        ECM_POST_INSTALLATION.initialize_user_input(user_input_file)
        SIT_initialization.initialize_user_input(SIT_initialization, user_input_file)
        report_file_related = ' -f=json.pretty -o=reports/output.json' + ' '
        feature_file_path = r'integration_usecases/features/onboard_package.feature integration_usecases/features/deploy_package_test_hotel.feature integration_usecases/features/delete_package.feature  '
        options = ' --no-capture --no-capture-stderr --no-logcapture -f plain'
        full_runner_options = report_file_related + feature_file_path + options
        runner_with_options.main(full_runner_options)
        generate_cucumber_report()


    elif operation == 'SO-POST':
        log.info('operation : ' + operation + ' input file path : ' + user_input_file)
        ECM_POST_INSTALLATION.initialize_user_input(user_input_file)
        SIT_initialization.initialize_user_input(SIT_initialization, user_input_file)

        report_file_related = ' -f=json.pretty -o=reports/output.json' + ' '
        feature_file_path = r'so_post_installation/features/so_post_installation.feature '
        options = ' --no-capture --no-capture-stderr --no-logcapture -f plain'

        full_runner_options = report_file_related + feature_file_path + options

        runner_with_options.main(full_runner_options)
        generate_cucumber_report()

    elif operation == 'SYNC-VIM-CAPACITY':
        log.info('operation : ' + operation + ' input file path : ' + user_input_file)

        Json_file_handler.validate_schema(Json_file_handler, schema_file, user_input_file)
        ECM_POST_INSTALLATION.initialize_user_input(user_input_file)
        SIT_initialization.initialize_user_input(SIT_initialization, user_input_file)
        report_file_related = ' -f=json.pretty -o=reports/output.json' + ' '
        feature_file_path = r'sync_vim_capacity/features/sync_vim_capacity.feature '
        options = ' --no-capture --no-capture-stderr --no-logcapture -f plain'

        full_runner_options = report_file_related + feature_file_path + options

        runner_with_options.main(full_runner_options)
        generate_cucumber_report()

    elif operation == 'PROJ-VIM':
        log.info('operation : ' + operation + ' input file path : ' + user_input_file)

        Json_file_handler.validate_schema(Json_file_handler, schema_file, user_input_file)
        ECM_POST_INSTALLATION.initialize_user_input(user_input_file)
        SIT_initialization.initialize_user_input(SIT_initialization, user_input_file)
        report_file_related = ' -f=json.pretty -o=reports/output.json' + ' '
        feature_file_path = r'project_vim/features/project_vim.feature '
        options = ' --no-capture --no-capture-stderr --no-logcapture -f plain'

        full_runner_options = report_file_related + feature_file_path + options

        runner_with_options.main(full_runner_options)
        generate_cucumber_report()


    elif operation == 'EPG-REDISCOVERY':
        log.info('operation : ' + operation + ' input file path : ' + user_input_file)
        ECM_POST_INSTALLATION.initialize_user_input(user_input_file)
        SIT_initialization.initialize_user_input(SIT_initialization, user_input_file)
        report_file_related = ' -f=json.pretty -o=reports/output.json' + ' '
        feature_file_path = r'epg_node_rediscovery/features/epg_rediscovery.feature '
        options = ' --no-capture --no-capture-stderr --no-logcapture -f plain'

        full_runner_options = report_file_related + feature_file_path + options

        runner_with_options.main(full_runner_options)
        generate_cucumber_report()


    elif operation == 'MME-REDISCOVERY':
        log.info('operation : ' + operation + ' input file path : ' + user_input_file)
        ECM_POST_INSTALLATION.initialize_user_input(user_input_file)
        SIT_initialization.initialize_user_input(SIT_initialization, user_input_file)
        report_file_related = ' -f=json.pretty -o=reports/output.json' + ' '
        feature_file_path = r'mme_node_rediscovery/features/mme_rediscovery.feature '
        options = ' --no-capture --no-capture-stderr --no-logcapture -f plain'

        full_runner_options = report_file_related + feature_file_path + options

        runner_with_options.main(full_runner_options)
        generate_cucumber_report()

    elif operation == 'WANO-LOG':
        log.info('operation : ' + operation + ' input file path : ' + user_input_file)
        ECM_POST_INSTALLATION.initialize_user_input(user_input_file)
        SIT_initialization.initialize_user_input(SIT_initialization, user_input_file)
        report_file_related = ' -f=json.pretty -o=reports/output.json' + ' '
        feature_file_path = r'app_log_verification/features/wano_log_verify.feature '
        options = ' --no-capture --no-capture-stderr --no-logcapture -f plain'

        full_runner_options = report_file_related + feature_file_path + options

        runner_with_options.main(full_runner_options)
        generate_cucumber_report()

    elif operation == 'EVNFM-LOG':
        log.info('operation : ' + operation + ' input file path : ' + user_input_file)
        ECM_POST_INSTALLATION.initialize_user_input(user_input_file)
        SIT_initialization.initialize_user_input(SIT_initialization, user_input_file)
        report_file_related = ' -f=json.pretty -o=reports/output.json' + ' '
        feature_file_path = r'app_log_verification/features/evnfm_log_verify.feature '
        options = ' --no-capture --no-capture-stderr --no-logcapture -f plain'

        full_runner_options = report_file_related + feature_file_path + options

        runner_with_options.main(full_runner_options)
        generate_cucumber_report()


    elif operation == 'SO-SUBSYSTEM_LOG':
        log.info('operation : ' + operation + ' input file path : ' + user_input_file)
        ECM_POST_INSTALLATION.initialize_user_input(user_input_file)
        SIT_initialization.initialize_user_input(SIT_initialization, user_input_file)
        report_file_related = ' -f=json.pretty -o=reports/output.json' + ' '
        feature_file_path = r'app_log_verification/features/subsystem_log_verify.feature '
        options = ' --no-capture --no-capture-stderr --no-logcapture -f plain'

        full_runner_options = report_file_related + feature_file_path + options

        runner_with_options.main(full_runner_options)
        generate_cucumber_report()


    elif operation == 'SO-LOGVIEWER_LOG':
        log.info('operation : ' + operation + ' input file path : ' + user_input_file)
        ECM_POST_INSTALLATION.initialize_user_input(user_input_file)
        SIT_initialization.initialize_user_input(SIT_initialization, user_input_file)
        report_file_related = ' -f=json.pretty -o=reports/output.json' + ' '
        feature_file_path = r'app_log_verification/features/so_logviewer_log_verify.feature '
        options = ' --no-capture --no-capture-stderr --no-logcapture -f plain'

        full_runner_options = report_file_related + feature_file_path + options

        runner_with_options.main(full_runner_options)
        generate_cucumber_report()

    elif operation == 'SIT-EO-VNFLCM':
        log.info('operation : ' + operation + ' input file path : ' + user_input_file)
        ECM_POST_INSTALLATION.initialize_user_input(user_input_file)
        SIT_initialization.initialize_user_input(SIT_initialization, user_input_file, dynamic_project=True)

        report_file_related = ' -f=json.pretty -o=reports/output.json' + ' '
        feature_file_path = r'integration_usecases/features/dynamic_onboard_package.feature integration_usecases/features/dynamic_deploy_package.feature integration_usecases/features/dynamic_delete_package.feature  '
        options = ' --no-capture --no-capture-stderr --no-logcapture -f plain'

        full_runner_options = report_file_related + feature_file_path + options

        runner_with_options.main(full_runner_options)
        generate_cucumber_report()


    elif operation == 'SO-DEPLOY-LCM-VM-SHUT':
        log.info('operation : ' + operation + ' input file path : ' + user_input_file)

        ECM_POST_INSTALLATION.initialize_user_input(user_input_file)
        Initialization_script.store_user_input(Initialization_script, user_input_file)
        Initialization_script.store_LCM_service_server_data(Initialization_script, user_input_file)
        SIT_initialization.initialize_user_input(SIT_initialization, user_input_file)

        report_file_related = ' -f=json.pretty -o=reports/output.json' + ' '
        feature_file_path = r'integration_usecases/features/onboard_package_shutdown_vm.feature integration_usecases/features/dummy_node_deploy_so_shutdown_vm.feature integration_usecases/features/scale_heal_vm_shutdown_vm.feature integration_usecases/features/dummy_workflow.feature '
        options = ' --no-capture --no-capture-stderr --no-logcapture -f plain'

        full_runner_options = report_file_related + feature_file_path + options

        runner_with_options.main(full_runner_options)
        generate_cucumber_report()


    elif operation == 'SO-DEPLOY-DUMMY':

        # This job only deploys Dummy node from SO. No SCALE HEAL operation in this job.
        # https://fem1s11-eiffel052.eiffel.gic.ericsson.se:8443/jenkins/job/EO_STAGING_SO_DUMMY_DEPLOY/
        log.info('operation : ' + operation + ' input file path : ' + user_input_file)

        ECM_POST_INSTALLATION.initialize_user_input(user_input_file)
        Initialization_script.store_user_input(Initialization_script, user_input_file)
        Initialization_script.store_LCM_service_server_data(Initialization_script, user_input_file)
        SIT_initialization.initialize_user_input(SIT_initialization, user_input_file)

        report_file_related = ' -f=json.pretty -o=reports/output.json' + ' '
        feature_file_path = r'integration_usecases/features/onboard_package_shutdown_vm.feature integration_usecases/features/dummy_node_deploy_so_shutdown_vm.feature '
        options = ' --no-capture --no-capture-stderr --no-logcapture -f plain'

        full_runner_options = report_file_related + feature_file_path + options

        runner_with_options.main(full_runner_options)
        generate_cucumber_report()

    elif operation == 'DUMMY-NODE-HEAL':

        # This job only HEAL Dummy node.
        # https://fem1s11-eiffel052.eiffel.gic.ericsson.se:8443/jenkins/job/EO_STAGING_DUMMY_HEAL/
        log.info('operation : ' + operation + ' input file path : ' + user_input_file)

        ECM_POST_INSTALLATION.initialize_user_input(user_input_file)
        Initialization_script.store_user_input(Initialization_script, user_input_file)
        Initialization_script.store_LCM_service_server_data(Initialization_script, user_input_file)
        SIT_initialization.initialize_user_input(SIT_initialization, user_input_file)

        report_file_related = ' -f=json.pretty -o=reports/output.json' + ' '
        feature_file_path = r'integration_usecases/features/dummy_heal.feature '
        options = ' --no-capture --no-capture-stderr --no-logcapture -f plain'

        full_runner_options = report_file_related + feature_file_path + options

        runner_with_options.main(full_runner_options)
        generate_cucumber_report()

    elif operation == 'EOCM-DUMMY-SCALE':

        # This job only SCALE IN and OUT in case of vm vnfm and normal LCM on Dummy node.
        # https://fem1s11-eiffel052.eiffel.gic.ericsson.se:8443/jenkins/job/EO_STAGING_ECM_SCALE/

        log.info('operation : ' + operation + ' input file path : ' + user_input_file)
        ECM_POST_INSTALLATION.initialize_user_input(user_input_file)
        SIT_initialization.initialize_user_input(SIT_initialization, user_input_file)

        report_file_related = ' -f=json.pretty -o=reports/output.json' + ' '
        feature_file_path = r'eocm_dummy_scale/features/eocm_dummy_scale.feature  '
        options = ' --no-capture --no-capture-stderr --no-logcapture -f plain'

        full_runner_options = report_file_related + feature_file_path + options

        runner_with_options.main(full_runner_options)
        generate_cucumber_report()


    elif operation == 'LCM-VM-SHUT-STATIC':
        log.info('operation : ' + operation + ' input file path : ' + user_input_file)

        ECM_POST_INSTALLATION.initialize_user_input(user_input_file)
        Initialization_script.store_user_input(Initialization_script, user_input_file)
        Initialization_script.store_LCM_service_server_data(Initialization_script, user_input_file)
        SIT_initialization.initialize_user_input(SIT_initialization, user_input_file)

        report_file_related = ' -f=json.pretty -o=reports/output.json' + ' '
        feature_file_path = r'integration_usecases/features/onboard_package_shutdown_vm.feature integration_usecases/features/deploy_package_shutdown_vm.feature integration_usecases/features/delete_package_shutdown_vm.feature integration_usecases/features/so_node_deploy_shutdown_vm.feature integration_usecases/features/scale_heal_vm_shutdown_vm.feature '
        options = ' --no-capture --no-capture-stderr --no-logcapture -f plain'

        full_runner_options = report_file_related + feature_file_path + options

        runner_with_options.main(full_runner_options)
        generate_cucumber_report()


    elif operation == 'LCM-VM-SHUT-DYNAMIC':
        log.info('operation : ' + operation + ' input file path : ' + user_input_file)
        ECM_POST_INSTALLATION.initialize_user_input(user_input_file)
        Initialization_script.store_user_input(Initialization_script, user_input_file)
        Initialization_script.store_LCM_service_server_data(Initialization_script, user_input_file)
        SIT_initialization.initialize_user_input(SIT_initialization, user_input_file, dynamic_project=True)

        report_file_related = ' -f=json.pretty -o=reports/output.json' + ' '
        feature_file_path = r'integration_usecases/features/dynamic_onboard_package_shutdown_vm.feature integration_usecases/features/dynamic_deploy_package_shutdown_vm.feature integration_usecases/features/dynamic_delete_package_shutdown_vm.feature  '
        options = ' --no-capture --no-capture-stderr --no-logcapture -f plain'

        full_runner_options = report_file_related + feature_file_path + options

        runner_with_options.main(full_runner_options)
        generate_cucumber_report()

    elif operation == 'VM-VNFM-INTEGRATION':
        log.info('operation : ' + operation + ' input file path : ' + user_input_file)

        ECM_POST_INSTALLATION.initialize_user_input(user_input_file)
        Initialization_script.store_user_input(Initialization_script, user_input_file)
        SIT_initialization.initialize_user_input(SIT_initialization, user_input_file)

        report_file_related = ' -f=json.pretty -o=reports/output.json' + ' '
        feature_file_path = r'vm_vnfm_lcm_post_installation/features/vm_vnfm_lcm_post_install_tasks.feature '
        options = ' --no-capture --no-capture-stderr --no-logcapture -f plain'

        full_runner_options = report_file_related + feature_file_path + options

        runner_with_options.main(full_runner_options)
        generate_cucumber_report()


    elif operation == 'SO-DUMMY-VM-VNFM':
        log.info('operation : ' + operation + ' input file path : ' + user_input_file)

        ECM_POST_INSTALLATION.initialize_user_input(user_input_file)
        Initialization_script.store_user_input(Initialization_script, user_input_file)
        SIT_initialization.initialize_user_input(SIT_initialization, user_input_file)

        report_file_related = ' -f=json.pretty -o=reports/output.json' + ' '
        feature_file_path = r'integration_usecases/features/vm_vnfm_onboard_dummy_package.feature integration_usecases/features/so_dummy_node_deploy_vm_vnfm.feature '
        # integration_usecases/features/vm_vnfm_delete_dummy_package.feature
        options = ' --no-capture --no-capture-stderr --no-logcapture -f plain'

        full_runner_options = report_file_related + feature_file_path + options

        runner_with_options.main(full_runner_options)
        generate_cucumber_report()

    elif operation == 'EO_STAGING_MODIFY_CISMS_ZONE':
        log.info('operation : ' + operation + ' input file path : ' + user_input_file)

        ECM_POST_INSTALLATION.initialize_user_input(user_input_file)
        Initialization_script.store_user_input(Initialization_script, user_input_file)
        SIT_initialization.initialize_user_input(SIT_initialization, user_input_file)

        report_file_related = ' -f=json.pretty -o=reports/output.json' + ' '
        feature_file_path = r'cism_zone_cluster/features/modify_cism_zone_cluster.feature '
        options = ' --no-capture --no-capture-stderr --no-logcapture -f plain'

        full_runner_options = report_file_related + feature_file_path + options

        runner_with_options.main(full_runner_options)
        generate_cucumber_report()

    elif operation == 'CISMS-ZONE-REGISTER':
        log.info('operation : ' + operation + ' input file path : ' + user_input_file)

        ECM_POST_INSTALLATION.initialize_user_input(user_input_file)
        Initialization_script.store_user_input(Initialization_script, user_input_file)
        SIT_initialization.initialize_user_input(SIT_initialization, user_input_file)

        report_file_related = ' -f=json.pretty -o=reports/output.json' + ' '
        feature_file_path = r'cism_zone_cluster/features/register_cism_zone_cluster.feature '
        options = ' --no-capture --no-capture-stderr --no-logcapture -f plain'

        full_runner_options = report_file_related + feature_file_path + options

        runner_with_options.main(full_runner_options)
        generate_cucumber_report()



    elif operation == 'CISMS-ZONE-DEREGISTER':
        log.info('operation : ' + operation + ' input file path : ' + user_input_file)

        ECM_POST_INSTALLATION.initialize_user_input(user_input_file)
        Initialization_script.store_user_input(Initialization_script, user_input_file)
        SIT_initialization.initialize_user_input(SIT_initialization, user_input_file)

        report_file_related = ' -f=json.pretty -o=reports/output.json' + ' '
        feature_file_path = r'cism_zone_cluster/features/deregister_cism_zone_cluster.feature '
        options = ' --no-capture --no-capture-stderr --no-logcapture -f plain'

        full_runner_options = report_file_related + feature_file_path + options

        runner_with_options.main(full_runner_options)
        generate_cucumber_report()


    elif operation == 'EVNFM-CISMS-ZONE-REGISTER':
        log.info('operation : ' + operation + ' input file path : ' + user_input_file)

        ECM_POST_INSTALLATION.initialize_user_input(user_input_file)
        Initialization_script.store_user_input(Initialization_script, user_input_file)
        SIT_initialization.initialize_user_input(SIT_initialization, user_input_file)

        report_file_related = ' -f=json.pretty -o=reports/output.json' + ' '
        feature_file_path = r'cism_zone_cluster/features/evnfm_register_cism_zone_cluster.feature '
        options = ' --no-capture --no-capture-stderr --no-logcapture -f plain'

        full_runner_options = report_file_related + feature_file_path + options

        runner_with_options.main(full_runner_options)
        generate_cucumber_report()



    elif operation == 'EVNFM-CISMS-ZONE-DEREGISTER':
        log.info('operation : ' + operation + ' input file path : ' + user_input_file)

        ECM_POST_INSTALLATION.initialize_user_input(user_input_file)
        Initialization_script.store_user_input(Initialization_script, user_input_file)
        SIT_initialization.initialize_user_input(SIT_initialization, user_input_file)

        report_file_related = ' -f=json.pretty -o=reports/output.json' + ' '
        feature_file_path = r'cism_zone_cluster/features/evnfm_deregister_cism_zone_cluster.feature '
        options = ' --no-capture --no-capture-stderr --no-logcapture -f plain'

        full_runner_options = report_file_related + feature_file_path + options

        runner_with_options.main(full_runner_options)
        generate_cucumber_report()




    elif operation == 'UDS-POST-INST':
        log.info('operation : ' + operation + ' input file path : ' + user_input_file)
        ECM_POST_INSTALLATION.initialize_user_input(user_input_file)
        Initialization_script.store_user_input(Initialization_script, user_input_file)
        SIT_initialization.initialize_user_input(SIT_initialization, user_input_file)
        report_file_related = ' -f=json.pretty -o=reports/output.json' + ' '
        feature_file_path = r'uds_post_installation/features/uds_post_installation.feature '
        options = ' --no-capture --no-capture-stderr --no-logcapture -f plain'

        full_runner_options = report_file_related + feature_file_path + options

        runner_with_options.main(full_runner_options)
        generate_cucumber_report()

    elif operation == 'UDS-CLEANUP':
        log.info('operation : ' + operation + ' input file path : ' + user_input_file)
        ECM_POST_INSTALLATION.initialize_user_input(user_input_file)
        Initialization_script.store_user_input(Initialization_script, user_input_file)
        SIT_initialization.initialize_user_input(SIT_initialization, user_input_file)
        report_file_related = ' -f=json.pretty -o=reports/output.json' + ' '
        feature_file_path = r'uds_post_installation/features/uds_cleanup.feature '
        options = ' --no-capture --no-capture-stderr --no-logcapture -f plain'

        full_runner_options = report_file_related + feature_file_path + options

        runner_with_options.main(full_runner_options)
        generate_cucumber_report()

    elif operation == 'UDS-RESTORE-DATABASE':
        log.info('operation : ' + operation + ' input file path : ' + user_input_file)
        ECM_POST_INSTALLATION.initialize_user_input(user_input_file)
        Initialization_script.store_user_input(Initialization_script, user_input_file)
        SIT_initialization.initialize_user_input(SIT_initialization, user_input_file)
        report_file_related = ' -f=json.pretty -o=reports/output.json' + ' '
        feature_file_path = r'uds_post_installation/features/uds_database_restore.feature '
        options = ' --no-capture --no-capture-stderr --no-logcapture -f plain'

        full_runner_options = report_file_related + feature_file_path + options

        runner_with_options.main(full_runner_options)
        generate_cucumber_report()

    elif operation == 'UDS-VFC':

        log.info('operation : ' + operation + ' input file path : ' + user_input_file)
        ECM_POST_INSTALLATION.initialize_user_input(user_input_file)
        SIT_initialization.initialize_user_input(SIT_initialization, user_input_file)

        report_file_related = ' -f=json.pretty -o=reports/output.json' + ' '
        feature_file_path = r'uds_app_testcases/features/uds_vfc.feature  '
        options = ' --no-capture --no-capture-stderr --no-logcapture -f plain'

        full_runner_options = report_file_related + feature_file_path + options

        runner_with_options.main(full_runner_options)
        generate_cucumber_report()


    elif operation == 'UDS-VF':

        log.info('operation : ' + operation + ' input file path : ' + user_input_file)
        ECM_POST_INSTALLATION.initialize_user_input(user_input_file)
        SIT_initialization.initialize_user_input(SIT_initialization, user_input_file)

        report_file_related = ' -f=json.pretty -o=reports/output.json' + ' '
        feature_file_path = r'uds_app_testcases/features/uds_vf.feature  '
        options = ' --no-capture --no-capture-stderr --no-logcapture -f plain'

        full_runner_options = report_file_related + feature_file_path + options

        runner_with_options.main(full_runner_options)
        generate_cucumber_report()


    elif operation == 'UDS-SERVICE':

        log.info('operation : ' + operation + ' input file path : ' + user_input_file)
        ECM_POST_INSTALLATION.initialize_user_input(user_input_file)
        SIT_initialization.initialize_user_input(SIT_initialization, user_input_file)

        report_file_related = ' -f=json.pretty -o=reports/output.json' + ' '
        feature_file_path = r'uds_app_testcases/features/uds_service.feature  '
        options = ' --no-capture --no-capture-stderr --no-logcapture -f plain'

        full_runner_options = report_file_related + feature_file_path + options

        runner_with_options.main(full_runner_options)
        generate_cucumber_report()


    elif operation == 'UDS-EPG-DEPLOY':

        log.info('operation : ' + operation + ' input file path : ' + user_input_file)
        ECM_POST_INSTALLATION.initialize_user_input(user_input_file)
        SIT_initialization.initialize_user_input(SIT_initialization, user_input_file)

        report_file_related = ' -f=json.pretty -o=reports/output.json' + ' '
        feature_file_path = r'epg_node_deployment/features/epg_uds_so_deploy.feature  '
        options = ' --no-capture --no-capture-stderr --no-logcapture -f plain'

        full_runner_options = report_file_related + feature_file_path + options

        runner_with_options.main(full_runner_options)
        generate_cucumber_report()


    elif operation == 'LPIS':
        log.info('operation : ' + operation + ' input file path : ' + user_input_file)
        ECM_POST_INSTALLATION.initialize_user_input(user_input_file)
        Initialization_script.store_user_input(Initialization_script, user_input_file)
        Initialization_script.store_LCM_service_server_data(Initialization_script, user_input_file)

        report_file_related = ' -f=json.pretty -o=reports/output.json' + ' '
        feature_file_path = r'lcm_post_installation/features/vnf_lcm_int_static_project.feature '
        options = ' --no-capture --no-capture-stderr --no-logcapture -f plain'

        full_runner_options = report_file_related + feature_file_path + options

        runner_with_options.main(full_runner_options)
        generate_cucumber_report()


    elif operation == 'LPIS-DYNAMIC':
        log.info('operation : ' + operation + ' input file path : ' + user_input_file)
        ECM_POST_INSTALLATION.initialize_user_input(user_input_file)
        Initialization_script.store_user_input(Initialization_script, user_input_file)
        Initialization_script.store_LCM_service_server_data(Initialization_script, user_input_file)

        report_file_related = ' -f=json.pretty -o=reports/output.json' + ' '
        feature_file_path = r'lcm_post_installation/features/vnf_lcm_int_dynamic_project.feature '
        options = ' --no-capture --no-capture-stderr --no-logcapture -f plain'

        full_runner_options = report_file_related + feature_file_path + options

        runner_with_options.main(full_runner_options)
        generate_cucumber_report()

    elif operation == 'SIT-SO':
        log.info('operation : ' + operation + ' input file path : ' + user_input_file)
        SIT_initialization.initialize_user_input(SIT_initialization, user_input_file)

        report_file_related = ' -f=json.pretty -o=reports/output.json' + ' '
        feature_file_path = r'so_node_deployment/features/so_node_deploy.feature '
        options = ' --no-capture --no-capture-stderr --no-logcapture -f plain'

        full_runner_options = report_file_related + feature_file_path + options

        runner_with_options.main(full_runner_options)
        generate_cucumber_report()

    elif operation == 'SO-CLEANUP':
        log.info('operation : ' + operation + ' input file path : ' + user_input_file + ' with STAGING_TYPE ' + str(
            vnf_type))
        SIT_initialization.initialize_user_input(SIT_initialization, user_input_file, vnf_type=vnf_type.upper())
        ECM_POST_INSTALLATION.initialize_user_input(user_input_file)

        report_file_related = ' -f=json.pretty -o=reports/output.json' + ' '
        feature_file_path = r'so_node_deployment/features/so_cleanup.feature '
        options = ' --no-capture --no-capture-stderr --no-logcapture -f plain'

        full_runner_options = report_file_related + feature_file_path + options

        runner_with_options.main(full_runner_options)
        generate_cucumber_report()

    elif operation == 'VNF-ENM':
        log.info('operation : ' + operation + ' input file path : ' + user_input_file)
        Initialization_script.store_LCM_service_server_data(Initialization_script, user_input_file)
        VNF_LCM_ENM.main()


    elif operation == 'CEE-CLEANUP':
        log.info('operation : ' + operation + ' input file path : ' + user_input_file)
        ECM_POST_INSTALLATION.initialize_user_input(user_input_file)
        SIT_initialization.initialize_user_input(SIT_initialization, user_input_file)
        report_file_related = ' -f=json.pretty -o=reports/output.json' + ' '
        feature_file_path = r'cee_cleanup/features/cee_cleanup.feature '
        options = ' --no-capture --no-capture-stderr --no-logcapture -f plain'

        full_runner_options = report_file_related + feature_file_path + options

        runner_with_options.main(full_runner_options)
        generate_cucumber_report()

    elif operation == 'EPG-ECM-PRE':
        log.info('operation : ' + operation + ' input file path : ' + user_input_file)
        ECM_POST_INSTALLATION.initialize_user_input(user_input_file)
        SIT_initialization.initialize_user_input(SIT_initialization, user_input_file)
        report_file_related = ' -f=json.pretty -o=reports/output.json' + ' '
        feature_file_path = r'epg_node_deployment/features/epg_node_prerequisite.feature '
        options = ' --no-capture --no-capture-stderr --no-logcapture -f plain'

        full_runner_options = report_file_related + feature_file_path + options

        runner_with_options.main(full_runner_options)
        generate_cucumber_report()

    elif operation == 'EPG-VNF-ECM-PRE':
        # https: // fem1s11 - eiffel052.eiffel.gic.ericsson.se: 8443 / jenkins / job / EO_VNF_STAGING_EPG_PRE_REQUISITE /
        log.info('operation : ' + operation + ' input file path : ' + user_input_file)
        ECM_POST_INSTALLATION.initialize_user_input(user_input_file)
        SIT_initialization.initialize_user_input(SIT_initialization, user_input_file)
        report_file_related = ' -f=json.pretty -o=reports/output.json' + ' '
        feature_file_path = r'epg_node_deployment/features/epg_vnf_staging_ecm_prerequisite.feature '
        options = ' --no-capture --no-capture-stderr --no-logcapture -f plain'

        full_runner_options = report_file_related + feature_file_path + options

        runner_with_options.main(full_runner_options)
        generate_cucumber_report()

    elif operation == 'EPG-ECM':
        log.info('operation : ' + operation + ' input file path : ' + user_input_file)
        ECM_POST_INSTALLATION.initialize_user_input(user_input_file)
        SIT_initialization.initialize_user_input(SIT_initialization, user_input_file)
        report_file_related = ' -f=json.pretty -o=reports/output.json' + ' '
        feature_file_path = r'epg_node_deployment/features/epg_ecm_deploy.feature '
        options = ' --no-capture --no-capture-stderr --no-logcapture -f plain'

        full_runner_options = report_file_related + feature_file_path + options

        runner_with_options.main(full_runner_options)
        generate_cucumber_report()


    elif operation == 'EPG-VNF-ECM':
        # https://fem1s11-eiffel052.eiffel.gic.ericsson.se:8443/jenkins/job/EO_VNF_STAGING_EPG_ECM_DEPLOY/
        log.info('operation : ' + operation + ' input file path : ' + user_input_file)
        ECM_POST_INSTALLATION.initialize_user_input(user_input_file)
        SIT_initialization.initialize_user_input(SIT_initialization, user_input_file)
        report_file_related = ' -f=json.pretty -o=reports/output.json' + ' '
        feature_file_path = r'epg_node_deployment/features/epg_ecm_deploy_vnf_staging.feature '
        options = ' --no-capture --no-capture-stderr --no-logcapture -f plain'

        full_runner_options = report_file_related + feature_file_path + options

        runner_with_options.main(full_runner_options)
        generate_cucumber_report()

    elif operation == 'EPG-SO':
        log.info('operation : ' + operation + ' input file path : ' + user_input_file)
        ECM_POST_INSTALLATION.initialize_user_input(user_input_file)
        SIT_initialization.initialize_user_input(SIT_initialization, user_input_file)
        report_file_related = ' -f=json.pretty -o=reports/output.json' + ' '
        feature_file_path = r'epg_node_deployment/features/epg_so_deploy.feature '
        options = ' --no-capture --no-capture-stderr --no-logcapture -f plain'

        full_runner_options = report_file_related + feature_file_path + options

        runner_with_options.main(full_runner_options)
        generate_cucumber_report()

    elif operation == 'MME-PRE':
        log.info('operation : ' + operation + ' input file path : ' + user_input_file)
        ECM_POST_INSTALLATION.initialize_user_input(user_input_file)
        SIT_initialization.initialize_user_input(SIT_initialization, user_input_file)
        report_file_related = ' -f=json.pretty -o=reports/output.json' + ' '
        feature_file_path = r'mme_node_deployment/features/mme_node_prerequisite.feature '
        options = ' --no-capture --no-capture-stderr --no-logcapture -f plain'

        full_runner_options = report_file_related + feature_file_path + options

        runner_with_options.main(full_runner_options)
        generate_cucumber_report()

    elif operation == 'MME-VNF-ECM-PRE':
        # https: // fem1s11 - eiffel052.eiffel.gic.ericsson.se: 8443 / jenkins / job / EO_VNF_STAGING_MME_PRE_REQUISITE /
        log.info('operation : ' + operation + ' input file path : ' + user_input_file)
        ECM_POST_INSTALLATION.initialize_user_input(user_input_file)
        SIT_initialization.initialize_user_input(SIT_initialization, user_input_file)
        report_file_related = ' -f=json.pretty -o=reports/output.json' + ' '
        feature_file_path = r'mme_node_deployment/features/mme_vnf_staging_node_prerequisite.feature '
        options = ' --no-capture --no-capture-stderr --no-logcapture -f plain'

        full_runner_options = report_file_related + feature_file_path + options

        runner_with_options.main(full_runner_options)
        generate_cucumber_report()

    elif operation == 'MME-SO':
        log.info('operation : ' + operation + ' input file path : ' + user_input_file)
        ECM_POST_INSTALLATION.initialize_user_input(user_input_file)
        SIT_initialization.initialize_user_input(SIT_initialization, user_input_file)
        report_file_related = ' -f=json.pretty -o=reports/output.json' + ' '
        feature_file_path = r'mme_node_deployment/features/mme_so_deploy.feature '
        options = ' --no-capture --no-capture-stderr --no-logcapture -f plain'

        full_runner_options = report_file_related + feature_file_path + options

        runner_with_options.main(full_runner_options)
        generate_cucumber_report()

    elif operation == 'MME-VNF-ECM':
        # https: // fem1s11 - eiffel052.eiffel.gic.ericsson.se: 8443 / jenkins / job / EO_VNF_STAGING_ECM_MME_DEPLOY /
        log.info('operation : ' + operation + ' input file path : ' + user_input_file)
        ECM_POST_INSTALLATION.initialize_user_input(user_input_file)
        SIT_initialization.initialize_user_input(SIT_initialization, user_input_file)
        report_file_related = ' -f=json.pretty -o=reports/output.json' + ' '
        feature_file_path = r'mme_node_deployment/features/mme_vnf_staging_ecm_deploy.feature '
        options = ' --no-capture --no-capture-stderr --no-logcapture -f plain'

        full_runner_options = report_file_related + feature_file_path + options

        runner_with_options.main(full_runner_options)
        generate_cucumber_report()

    elif operation == 'EPG-PRE-VM-VNFM':
        log.info('operation : ' + operation + ' input file path : ' + user_input_file)
        ECM_POST_INSTALLATION.initialize_user_input(user_input_file)
        SIT_initialization.initialize_user_input(SIT_initialization, user_input_file)
        report_file_related = ' -f=json.pretty -o=reports/output.json' + ' '
        feature_file_path = r'epg_node_deployment/features/epg_node_vm_vnfm_prerequisite.feature '
        options = ' --no-capture --no-capture-stderr --no-logcapture -f plain'

        full_runner_options = report_file_related + feature_file_path + options

        runner_with_options.main(full_runner_options)
        generate_cucumber_report()

    elif operation == 'EPG-SO-VM-VNFM':
        log.info('operation : ' + operation + ' input file path : ' + user_input_file)
        ECM_POST_INSTALLATION.initialize_user_input(user_input_file)
        SIT_initialization.initialize_user_input(SIT_initialization, user_input_file)
        report_file_related = ' -f=json.pretty -o=reports/output.json' + ' '
        feature_file_path = r'epg_node_deployment/features/epg_so_vm_vnfm_deploy.feature '
        options = ' --no-capture --no-capture-stderr --no-logcapture -f plain'

        full_runner_options = report_file_related + feature_file_path + options

        runner_with_options.main(full_runner_options)
        generate_cucumber_report()

    elif operation == 'MME-PRE-VM-VNFM':
        log.info('operation : ' + operation + ' input file path : ' + user_input_file)
        ECM_POST_INSTALLATION.initialize_user_input(user_input_file)
        SIT_initialization.initialize_user_input(SIT_initialization, user_input_file)
        report_file_related = ' -f=json.pretty -o=reports/output.json' + ' '
        feature_file_path = r'mme_node_deployment/features/mme_node_vm_vnfm_prerequisite.feature '
        options = ' --no-capture --no-capture-stderr --no-logcapture -f plain'

        full_runner_options = report_file_related + feature_file_path + options

        runner_with_options.main(full_runner_options)
        generate_cucumber_report()

    elif operation == 'MME-SO-VM-VNFM':
        log.info('operation : ' + operation + ' input file path : ' + user_input_file)
        ECM_POST_INSTALLATION.initialize_user_input(user_input_file)
        SIT_initialization.initialize_user_input(SIT_initialization, user_input_file)
        report_file_related = ' -f=json.pretty -o=reports/output.json' + ' '
        feature_file_path = r'mme_node_deployment/features/mme_so_vm_vnfm_deploy.feature '
        options = ' --no-capture --no-capture-stderr --no-logcapture -f plain'

        full_runner_options = report_file_related + feature_file_path + options

        runner_with_options.main(full_runner_options)
        generate_cucumber_report()


    elif operation == 'IMS-ECM-PRE':
        log.info('operation : ' + operation + ' input file path : ' + user_input_file)
        ECM_POST_INSTALLATION.initialize_user_input(user_input_file)
        SIT_initialization.initialize_user_input(SIT_initialization, user_input_file)
        report_file_related = ' -f=json.pretty -o=reports/output.json' + ' '
        feature_file_path = r'ims_node_pre_requisite/features/ims_node_prerequisite.feature '
        options = ' --no-capture --no-capture-stderr --no-logcapture -f plain'

        full_runner_options = report_file_related + feature_file_path + options

        runner_with_options.main(full_runner_options)
        generate_cucumber_report()



    elif operation == 'BGF-ECM-PRE':
        log.info('operation : ' + operation + ' input file path : ' + user_input_file)
        ECM_POST_INSTALLATION.initialize_user_input(user_input_file)
        SIT_initialization.initialize_user_input(SIT_initialization, user_input_file)
        report_file_related = ' -f=json.pretty -o=reports/output.json' + ' '
        feature_file_path = r'bgf_node_deployment/features/bgf_node_prerequisite.feature '
        options = ' --no-capture --no-capture-stderr --no-logcapture -f plain'

        full_runner_options = report_file_related + feature_file_path + options

        runner_with_options.main(full_runner_options)
        generate_cucumber_report()

    elif operation == 'BGF-ECM':
        log.info('operation : ' + operation + ' input file path : ' + user_input_file)
        ECM_POST_INSTALLATION.initialize_user_input(user_input_file)
        SIT_initialization.initialize_user_input(SIT_initialization, user_input_file)
        report_file_related = ' -f=json.pretty -o=reports/output.json' + ' '
        feature_file_path = r'bgf_node_deployment/features/bgf_ecm_deploy.feature '
        options = ' --no-capture --no-capture-stderr --no-logcapture -f plain'

        full_runner_options = report_file_related + feature_file_path + options

        runner_with_options.main(full_runner_options)
        generate_cucumber_report()




    elif operation == 'VBGF_TOSCA_PRE':
        log.info('operation : ' + operation + ' input file path : ' + user_input_file)
        ECM_POST_INSTALLATION.initialize_user_input(user_input_file)
        SIT_initialization.initialize_user_input(SIT_initialization, user_input_file)
        report_file_related = ' -f=json.pretty -o=reports/output.json' + ' '
        feature_file_path = r'bgf_tosca_node_deployment/features/bgf_tosca_node_prerequisite.feature '
        options = ' --no-capture --no-capture-stderr --no-logcapture -f plain'

        full_runner_options = report_file_related + feature_file_path + options

        runner_with_options.main(full_runner_options)
        generate_cucumber_report()

    elif operation == 'VBGF_TOSCA_DEPLOY':
        log.info('operation : ' + operation + ' input file path : ' + user_input_file)
        ECM_POST_INSTALLATION.initialize_user_input(user_input_file)
        SIT_initialization.initialize_user_input(SIT_initialization, user_input_file)
        report_file_related = ' -f=json.pretty -o=reports/output.json' + ' '
        feature_file_path = r'bgf_tosca_node_deployment/features/bgf_tosca_ecm_deploy.feature '
        options = ' --no-capture --no-capture-stderr --no-logcapture -f plain'

        full_runner_options = report_file_related + feature_file_path + options

        runner_with_options.main(full_runner_options)
        generate_cucumber_report()


    elif operation == 'SOL-BGF-PRE-REQ':
        # https://fem1s11-eiffel052.eiffel.gic.ericsson.se:8443/jenkins/job/EO_STAGING_SOL_vBGF_TOSCA_PRE/
        log.info('operation : ' + operation + ' input file path : ' + user_input_file)
        ECM_POST_INSTALLATION.initialize_user_input(user_input_file)
        SIT_initialization.initialize_user_input(SIT_initialization, user_input_file)
        report_file_related = ' -f=json.pretty -o=reports/output.json' + ' '
        feature_file_path = r'sol_005_bgf_tosca_node_deployment/features/sol_005_bgf_tosca_node_prerequisite.feature '
        options = ' --no-capture --no-capture-stderr --no-logcapture -f plain'

        full_runner_options = report_file_related + feature_file_path + options

        runner_with_options.main(full_runner_options)
        generate_cucumber_report()


    elif operation == 'SO-DEPLOY-SOL-BGF':
        # https://fem1s11-eiffel052.eiffel.gic.ericsson.se:8443/jenkins/job/EO_STAGING_SOL_vBGF_TOSCA_SO_DEPLOY/
        log.info('operation : ' + operation + ' input file path : ' + user_input_file)
        ECM_POST_INSTALLATION.initialize_user_input(user_input_file)
        SIT_initialization.initialize_user_input(SIT_initialization, user_input_file)
        report_file_related = ' -f=json.pretty -o=reports/output.json' + ' '
        feature_file_path = r'sol_005_bgf_tosca_node_deployment/features/sol_005_bgf_tosca_so_deploy.feature '
        options = ' --no-capture --no-capture-stderr --no-logcapture -f plain'

        full_runner_options = report_file_related + feature_file_path + options

        runner_with_options.main(full_runner_options)
        generate_cucumber_report()


    elif operation == 'SOL-DUMMY-PRE-REQ':
        # https://fem1s11-eiffel052.eiffel.gic.ericsson.se:8443/jenkins/job/EO_STAGING_SOL_DUMMY_PRE/
        log.info('operation : ' + operation + ' input file path : ' + user_input_file)
        ECM_POST_INSTALLATION.initialize_user_input(user_input_file)
        SIT_initialization.initialize_user_input(SIT_initialization, user_input_file)
        report_file_related = ' -f=json.pretty -o=reports/output.json' + ' '
        feature_file_path = r'dummy_sol_005_node_deployment/features/dummy_sol_005_node_prerequisite.feature '
        options = ' --no-capture --no-capture-stderr --no-logcapture -f plain'

        full_runner_options = report_file_related + feature_file_path + options

        runner_with_options.main(full_runner_options)
        generate_cucumber_report()


    elif operation == 'SO-DEPLOY-SOL-DUMMY':
        # https://fem1s11-eiffel052.eiffel.gic.ericsson.se:8443/jenkins/job/EO_STAGING_SOL_DUMMY_SO_DEPLOY/
        log.info('operation : ' + operation + ' input file path : ' + user_input_file)
        ECM_POST_INSTALLATION.initialize_user_input(user_input_file)
        SIT_initialization.initialize_user_input(SIT_initialization, user_input_file)
        report_file_related = ' -f=json.pretty -o=reports/output.json' + ' '
        feature_file_path = r'dummy_sol_005_node_deployment/features/dummy_sol_005_so_deploy.feature '
        options = ' --no-capture --no-capture-stderr --no-logcapture -f plain'

        full_runner_options = report_file_related + feature_file_path + options

        runner_with_options.main(full_runner_options)
        generate_cucumber_report()


    elif operation == 'SO-DUMMY-SCALE':

        # https://fem1s11-eiffel052.eiffel.gic.ericsson.se:8443/jenkins/job/EO_STAGING_SCALE_SOL_DUMMY/
        log.info('operation : ' + operation + ' input file path : ' + user_input_file)
        ECM_POST_INSTALLATION.initialize_user_input(user_input_file)
        SIT_initialization.initialize_user_input(SIT_initialization, user_input_file)
        report_file_related = ' -f=json.pretty -o=reports/output.json' + ' '
        feature_file_path = r'dummy_sol_005_node_deployment/features/dummy_sol_005_so_scale.feature '
        options = ' --no-capture --no-capture-stderr --no-logcapture -f plain'

        full_runner_options = report_file_related + feature_file_path + options

        runner_with_options.main(full_runner_options)
        generate_cucumber_report()

    elif operation == 'DUMMY-TOSCA-HEAL':

        # https://fem1s11-eiffel052.eiffel.gic.ericsson.se:8443/jenkins/job/EO_STAGING_DUMMY_TOSCA_HEAL/
        log.info('operation : ' + operation + ' input file path : ' + user_input_file)
        ECM_POST_INSTALLATION.initialize_user_input(user_input_file)
        SIT_initialization.initialize_user_input(SIT_initialization, user_input_file)
        report_file_related = ' -f=json.pretty -o=reports/output.json' + ' '
        feature_file_path = r'dummy_sol_005_node_deployment/features/dummy_tosca_heal.feature '
        options = ' --no-capture --no-capture-stderr --no-logcapture -f plain'

        full_runner_options = report_file_related + feature_file_path + options

        runner_with_options.main(full_runner_options)
        generate_cucumber_report()

    elif operation == 'SBG-ECM-PRE':
        log.info('operation : ' + operation + ' input file path : ' + user_input_file)
        ECM_POST_INSTALLATION.initialize_user_input(user_input_file)
        SIT_initialization.initialize_user_input(SIT_initialization, user_input_file)
        report_file_related = ' -f=json.pretty -o=reports/output.json' + ' '
        feature_file_path = r'sbg_node_deployment/features/sbg_node_prerequisite.feature '
        options = ' --no-capture --no-capture-stderr --no-logcapture -f plain'

        full_runner_options = report_file_related + feature_file_path + options

        runner_with_options.main(full_runner_options)
        generate_cucumber_report()

    elif operation == 'SBG-ECM':
        log.info('operation : ' + operation + ' input file path : ' + user_input_file)
        ECM_POST_INSTALLATION.initialize_user_input(user_input_file)
        SIT_initialization.initialize_user_input(SIT_initialization, user_input_file)
        report_file_related = ' -f=json.pretty -o=reports/output.json' + ' '
        feature_file_path = r'sbg_node_deployment/features/sbg_ecm_deploy.feature '
        options = ' --no-capture --no-capture-stderr --no-logcapture -f plain'

        full_runner_options = report_file_related + feature_file_path + options

        runner_with_options.main(full_runner_options)
        generate_cucumber_report()


    elif operation == 'MTAS-ECM-PRE':
        log.info('operation : ' + operation + ' input file path : ' + user_input_file)
        ECM_POST_INSTALLATION.initialize_user_input(user_input_file)
        SIT_initialization.initialize_user_input(SIT_initialization, user_input_file)
        report_file_related = ' -f=json.pretty -o=reports/output.json' + ' '
        feature_file_path = r'mtas_node_deployment/features/mtas_node_prerequisite.feature '
        options = ' --no-capture --no-capture-stderr --no-logcapture -f plain'

        full_runner_options = report_file_related + feature_file_path + options

        runner_with_options.main(full_runner_options)
        generate_cucumber_report()

    elif operation == 'MTAS-ECM':
        log.info('operation : ' + operation + ' input file path : ' + user_input_file)
        ECM_POST_INSTALLATION.initialize_user_input(user_input_file)
        SIT_initialization.initialize_user_input(SIT_initialization, user_input_file)
        report_file_related = ' -f=json.pretty -o=reports/output.json' + ' '
        feature_file_path = r'mtas_node_deployment/features/mtas_ecm_deploy.feature '
        options = ' --no-capture --no-capture-stderr --no-logcapture -f plain'

        full_runner_options = report_file_related + feature_file_path + options

        runner_with_options.main(full_runner_options)
        generate_cucumber_report()


    elif operation == 'CSCF-ECM-PRE':
        log.info('operation : ' + operation + ' input file path : ' + user_input_file)
        ECM_POST_INSTALLATION.initialize_user_input(user_input_file)
        SIT_initialization.initialize_user_input(SIT_initialization, user_input_file)
        report_file_related = ' -f=json.pretty -o=reports/output.json' + ' '
        feature_file_path = r'cscf_node_deployment/features/cscf_node_prerequisite.feature '
        options = ' --no-capture --no-capture-stderr --no-logcapture -f plain'

        full_runner_options = report_file_related + feature_file_path + options

        runner_with_options.main(full_runner_options)
        generate_cucumber_report()

    elif operation == 'CSCF-ECM':
        log.info('operation : ' + operation + ' input file path : ' + user_input_file)
        ECM_POST_INSTALLATION.initialize_user_input(user_input_file)
        SIT_initialization.initialize_user_input(SIT_initialization, user_input_file)
        report_file_related = ' -f=json.pretty -o=reports/output.json' + ' '
        feature_file_path = r'cscf_node_deployment/features/cscf_ecm_deploy.feature '
        options = ' --no-capture --no-capture-stderr --no-logcapture -f plain'

        full_runner_options = report_file_related + feature_file_path + options

        runner_with_options.main(full_runner_options)
        generate_cucumber_report()

    elif operation == 'EO-CM-CERT':
        log.info('operation : ' + operation + ' input file path : ' + user_input_file)
        ECM_POST_INSTALLATION.initialize_user_input(user_input_file)
        SIT_initialization.initialize_user_input(SIT_initialization, user_input_file)
        report_file_related = ' -f=json.pretty -o=reports/output.json' + ' '
        feature_file_path = r'ecm_post_installation/features/eocm_ha_certificate.feature '
        options = ' --no-capture --no-capture-stderr --no-logcapture -f plain'

        full_runner_options = report_file_related + feature_file_path + options

        runner_with_options.main(full_runner_options)
        generate_cucumber_report()

    elif operation == 'SO-SERVICES-DEL':
        log.info(
            'operation : ' + operation + ' input file path : ' + user_input_file + ' with VNF_TYPE ' + str(vnf_type))
        ECM_POST_INSTALLATION.initialize_user_input(user_input_file)
        SIT_initialization.initialize_user_input(SIT_initialization, user_input_file, vnf_type=vnf_type.upper())
        report_file_related = ' -f=json.pretty -o=reports/output.json' + ' '
        feature_file_path = r'so_services_deletion/features/so_services_deletion.feature '
        options = ' --no-capture --no-capture-stderr --no-logcapture -f plain'

        full_runner_options = report_file_related + feature_file_path + options

        runner_with_options.main(full_runner_options)
        generate_cucumber_report()


    elif operation == 'RECONCILE-DUMMY':
        log.info('operation : ' + operation + ' input file path : ' + user_input_file)
        ECM_POST_INSTALLATION.initialize_user_input(user_input_file)
        SIT_initialization.initialize_user_input(SIT_initialization, user_input_file, reconcile=True)

        report_file_related = ' -f=json.pretty -o=reports/output.json' + ' '
        feature_file_path = r'reconcile_dummy_usecase/features/reconcile_dummy_deploy.feature reconcile_dummy_usecase/features/reconcile_usecases.feature '
        options = ' --no-capture --no-capture-stderr --no-logcapture -f plain'

        full_runner_options = report_file_related + feature_file_path + options

        runner_with_options.main(full_runner_options)
        generate_cucumber_report()


    elif operation == 'IMAGE-REG':
        # https://fem1s11-eiffel052.eiffel.gic.ericsson.se:8443/jenkins/job/EO_STAGING_IMAGE_REGISTER/

        log.info(
            'operation : ' + operation + ' input file path : ' + user_input_file + ' with VNF_TYPE ' + str(vnf_type))
        ECM_POST_INSTALLATION.initialize_user_input(user_input_file)
        SIT_initialization.initialize_user_input(SIT_initialization, user_input_file, vnf_type=vnf_type.upper())
        report_file_related = ' -f=json.pretty -o=reports/output.json' + ' '
        feature_file_path = r'image_registration/features/image_registration.feature '
        options = ' --no-capture --no-capture-stderr --no-logcapture -f plain'

        full_runner_options = report_file_related + feature_file_path + options

        runner_with_options.main(full_runner_options)
        generate_cucumber_report()



    elif operation == 'CREATE-FLAVOUR':
        # https://fem1s11-eiffel052.eiffel.gic.ericsson.se:8443/jenkins/job/EO_STAGING_FLAVOUR_CREATE/

        log.info(
            'operation : ' + operation + ' input file path : ' + user_input_file + ' with VNF_TYPE ' + str(vnf_type))
        ECM_POST_INSTALLATION.initialize_user_input(user_input_file)
        SIT_initialization.initialize_user_input(SIT_initialization, user_input_file, vnf_type=vnf_type.upper())
        report_file_related = ' -f=json.pretty -o=reports/output.json' + ' '
        feature_file_path = r'create_flavour/features/create_flavour.feature '
        options = ' --no-capture --no-capture-stderr --no-logcapture -f plain'

        full_runner_options = report_file_related + feature_file_path + options

        runner_with_options.main(full_runner_options)
        generate_cucumber_report()


    elif operation == 'ECM-DEL':
        log.info(
            'operation : ' + operation + ' input file path : ' + user_input_file + ' with VNF_TYPE ' + str(vnf_type))
        ECM_POST_INSTALLATION.initialize_user_input(user_input_file)
        SIT_initialization.initialize_user_input(SIT_initialization, user_input_file, vnf_type=vnf_type.upper())
        report_file_related = ' -f=json.pretty -o=reports/output.json' + ' '
        feature_file_path = r'ecm_deletion/features/ecm_deletion.feature '
        options = ' --no-capture --no-capture-stderr --no-logcapture -f plain'

        full_runner_options = report_file_related + feature_file_path + options

        runner_with_options.main(full_runner_options)
        generate_cucumber_report()

    elif operation == 'CCRC-SECRET':
        log.info('operation : ' + operation + ' input file path : ' + user_input_file)

        ECM_POST_INSTALLATION.initialize_user_input(user_input_file)
        Initialization_script.store_user_input(Initialization_script, user_input_file)
        SIT_initialization.initialize_user_input(SIT_initialization, user_input_file)

        report_file_related = ' -f=json.pretty -o=reports/output.json' + ' '
        feature_file_path = r'ccrc_cnf_deployment/features/ccrc_secret_creation.feature '
        options = ' --no-capture --no-capture-stderr --no-logcapture -f plain'

        full_runner_options = report_file_related + feature_file_path + options

        runner_with_options.main(full_runner_options)
        generate_cucumber_report()


    elif operation == 'CCRC-CNF-ONBOARD':
        log.info('operation : ' + operation + ' input file path : ' + user_input_file)

        ECM_POST_INSTALLATION.initialize_user_input(user_input_file)
        Initialization_script.store_user_input(Initialization_script, user_input_file)
        SIT_initialization.initialize_user_input(SIT_initialization, user_input_file)

        report_file_related = ' -f=json.pretty -o=reports/output.json' + ' '
        feature_file_path = r'ccrc_cnf_deployment/features/onboard_ccrc.feature '
        options = ' --no-capture --no-capture-stderr --no-logcapture -f plain'

        full_runner_options = report_file_related + feature_file_path + options

        runner_with_options.main(full_runner_options)
        generate_cucumber_report()

    elif operation == 'CCRC-UPGRADE-ONBOARD':
        log.info('operation : ' + operation + ' input file path : ' + user_input_file)

        ECM_POST_INSTALLATION.initialize_user_input(user_input_file)
        Initialization_script.store_user_input(Initialization_script, user_input_file)
        SIT_initialization.initialize_user_input(SIT_initialization, user_input_file)

        report_file_related = ' -f=json.pretty -o=reports/output.json' + ' '
        feature_file_path = r'ccrc_cnf_deployment/features/onboard_upgrade_package.feature '
        options = ' --no-capture --no-capture-stderr --no-logcapture -f plain'

        full_runner_options = report_file_related + feature_file_path + options

        runner_with_options.main(full_runner_options)
        generate_cucumber_report()


    elif operation == 'CCRC-CNF-DEPLOY':
        log.info('operation : ' + operation + ' input file path : ' + user_input_file)

        ECM_POST_INSTALLATION.initialize_user_input(user_input_file)
        Initialization_script.store_user_input(Initialization_script, user_input_file)
        SIT_initialization.initialize_user_input(SIT_initialization, user_input_file)

        report_file_related = ' -f=json.pretty -o=reports/output.json' + ' '
        feature_file_path = r'ccrc_cnf_deployment/features/deploy_ccrc.feature '
        options = ' --no-capture --no-capture-stderr --no-logcapture -f plain'

        full_runner_options = report_file_related + feature_file_path + options

        runner_with_options.main(full_runner_options)
        generate_cucumber_report()

    elif operation == 'SO-CNF-CONFIGMAP-PRE_REQ':
        log.info('operation : ' + operation + ' input file path : ' + user_input_file)

        ECM_POST_INSTALLATION.initialize_user_input(user_input_file)
        Initialization_script.store_user_input(Initialization_script, user_input_file)
        Initialization_script.store_LCM_service_server_data(Initialization_script, user_input_file)
        SIT_initialization.initialize_user_input(SIT_initialization, user_input_file)

        report_file_related = ' -f=json.pretty -o=reports/output.json' + ' '
        feature_file_path = r'so_cnf_configmap_pre_req/features/so_cnf_configmap_pre_req.feature '
        options = ' --no-capture --no-capture-stderr --no-logcapture -f plain'

        full_runner_options = report_file_related + feature_file_path + options

        runner_with_options.main(full_runner_options)
        generate_cucumber_report()

    elif operation == 'SO-CNF-CONFIGMAP-DEPL':
        log.info('operation : ' + operation + ' input file path : ' + user_input_file)

        ECM_POST_INSTALLATION.initialize_user_input(user_input_file)
        Initialization_script.store_user_input(Initialization_script, user_input_file)
        Initialization_script.store_LCM_service_server_data(Initialization_script, user_input_file)
        SIT_initialization.initialize_user_input(SIT_initialization, user_input_file)

        report_file_related = ' -f=json.pretty -o=reports/output.json' + ' '
        feature_file_path = r'so_cnf_configmap_depl/features/so_cnf_configmap_depl.feature '
        options = ' --no-capture --no-capture-stderr --no-logcapture -f plain'

        full_runner_options = report_file_related + feature_file_path + options

        runner_with_options.main(full_runner_options)
        generate_cucumber_report()
    elif operation == 'CLUSTER-CONFIG':
        # This job created particular to Kieran's new team
        # https: // fem1s11 - eiffel052.eiffel.gic.ericsson.se: 8443 / jenkins / job / EO_STAGING_CLUSTER_CONFIG_EVNFM /
        log.info('operation : ' + operation + ' input file path : ' + user_input_file)

        ECM_POST_INSTALLATION.initialize_user_input(user_input_file)
        Initialization_script.store_user_input(Initialization_script, user_input_file)
        SIT_initialization.initialize_user_input(SIT_initialization, user_input_file)

        report_file_related = ' -f=json.pretty -o=reports/output.json' + ' '
        feature_file_path = r'ccrc_cnf_deployment/features/app_staging_upload_cluster_config.feature '
        options = ' --no-capture --no-capture-stderr --no-logcapture -f plain'

        full_runner_options = report_file_related + feature_file_path + options

        runner_with_options.main(full_runner_options)
        generate_cucumber_report()


    elif operation == 'CCRC-CNF-UPGRADE':
        log.info('operation : ' + operation + ' input file path : ' + user_input_file)

        ECM_POST_INSTALLATION.initialize_user_input(user_input_file)
        Initialization_script.store_user_input(Initialization_script, user_input_file)
        SIT_initialization.initialize_user_input(SIT_initialization, user_input_file)

        report_file_related = ' -f=json.pretty -o=reports/output.json' + ' '
        feature_file_path = r'ccrc_cnf_deployment/features/upgrade_ccrc.feature '
        options = ' --no-capture --no-capture-stderr --no-logcapture -f plain'

        full_runner_options = report_file_related + feature_file_path + options

        runner_with_options.main(full_runner_options)
        generate_cucumber_report()

    elif operation == 'CCRC-CNF-SCALE':
        log.info('operation : ' + operation + ' input file path : ' + user_input_file)

        ECM_POST_INSTALLATION.initialize_user_input(user_input_file)
        Initialization_script.store_user_input(Initialization_script, user_input_file)
        SIT_initialization.initialize_user_input(SIT_initialization, user_input_file)

        report_file_related = ' -f=json.pretty -o=reports/output.json' + ' '
        feature_file_path = r'ccrc_cnf_deployment/features/scale_ccrc.feature '
        options = ' --no-capture --no-capture-stderr --no-logcapture -f plain'

        full_runner_options = report_file_related + feature_file_path + options

        runner_with_options.main(full_runner_options)
        generate_cucumber_report()

    elif operation == 'CCRC-CNF-TERMINATE':
        log.info('operation : ' + operation + ' input file path : ' + user_input_file)

        ECM_POST_INSTALLATION.initialize_user_input(user_input_file)
        Initialization_script.store_user_input(Initialization_script, user_input_file)
        SIT_initialization.initialize_user_input(SIT_initialization, user_input_file)

        report_file_related = ' -f=json.pretty -o=reports/output.json' + ' '
        feature_file_path = r'ccrc_cnf_deployment/features/terminate_ccrc.feature '
        options = ' --no-capture --no-capture-stderr --no-logcapture -f plain'

        full_runner_options = report_file_related + feature_file_path + options

        runner_with_options.main(full_runner_options)
        generate_cucumber_report()

    elif operation == 'EVNFM-PACKAGE-DEL':
        log.info(
            'operation : ' + operation + ' input file path : ' + user_input_file + ' with VNF_TYPE ' + str(vnf_type))
        ECM_POST_INSTALLATION.initialize_user_input(user_input_file)
        SIT_initialization.initialize_user_input(SIT_initialization, user_input_file, vnf_type=vnf_type.upper())
        report_file_related = ' -f=json.pretty -o=reports/output.json' + ' '
        feature_file_path = r'ccrc_cnf_deployment/features/package_delete_ccrc.feature '
        options = ' --no-capture --no-capture-stderr --no-logcapture -f plain'

        full_runner_options = report_file_related + feature_file_path + options

        runner_with_options.main(full_runner_options)
        generate_cucumber_report()

    elif operation == 'EPG-SCALE':
        log.info('operation : ' + operation + ' input file path : ' + user_input_file)
        ECM_POST_INSTALLATION.initialize_user_input(user_input_file)
        Initialization_script.store_user_input(Initialization_script, user_input_file)
        SIT_initialization.initialize_user_input(SIT_initialization, user_input_file)
        report_file_related = ' -f=json.pretty -o=reports/output.json' + ' '
        feature_file_path = r'epg_scale_heal/features/epg_scale.feature '
        options = ' --no-capture --no-capture-stderr --no-logcapture -f plain'

        full_runner_options = report_file_related + feature_file_path + options

        runner_with_options.main(full_runner_options)
        generate_cucumber_report()

    elif operation == 'EO_STAGING_TOSCA_EPG_ECM_SCALE':
        log.info('operation : ' + operation + ' input file path : ' + user_input_file)
        ECM_POST_INSTALLATION.initialize_user_input(user_input_file)
        Initialization_script.store_user_input(Initialization_script, user_input_file)
        SIT_initialization.initialize_user_input(SIT_initialization, user_input_file)
        report_file_related = ' -f=json.pretty -o=reports/output.json' + ' '
        feature_file_path = r'tosca_epg_ecm_scale/features/tosca_epg_ecm_scale.feature '
        options = ' --no-capture --no-capture-stderr --no-logcapture -f plain'

        full_runner_options = report_file_related + feature_file_path + options

        runner_with_options.main(full_runner_options)
        generate_cucumber_report()

    elif operation == 'EPG-TOSCA-SCALE-OUT':
        log.info('operation : ' + operation + ' input file path : ' + user_input_file)
        ECM_POST_INSTALLATION.initialize_user_input(user_input_file)
        Initialization_script.store_user_input(Initialization_script, user_input_file)
        SIT_initialization.initialize_user_input(SIT_initialization, user_input_file)
        report_file_related = ' -f=json.pretty -o=reports/output.json' + ' '
        feature_file_path = r'epg_tosca_scale/features/epg_tosca_scale_out.feature'
        options = ' --no-capture --no-capture-stderr --no-logcapture -f plain'

        full_runner_options = report_file_related + feature_file_path + options

        runner_with_options.main(full_runner_options)
        generate_cucumber_report()

    elif operation == 'EPG-TOSCA-SCALE-IN':
        log.info('operation : ' + operation + ' input file path : ' + user_input_file)
        ECM_POST_INSTALLATION.initialize_user_input(user_input_file)
        Initialization_script.store_user_input(Initialization_script, user_input_file)
        SIT_initialization.initialize_user_input(SIT_initialization, user_input_file)
        report_file_related = ' -f=json.pretty -o=reports/output.json' + ' '
        feature_file_path = r'epg_tosca_scale/features/epg_tosca_scale_in.feature'
        options = ' --no-capture --no-capture-stderr --no-logcapture -f plain'

        full_runner_options = report_file_related + feature_file_path + options

        runner_with_options.main(full_runner_options)
        generate_cucumber_report()

    elif operation == 'EPG-HEAL':
        log.info('operation : ' + operation + ' input file path : ' + user_input_file)
        ECM_POST_INSTALLATION.initialize_user_input(user_input_file)
        Initialization_script.store_user_input(Initialization_script, user_input_file)
        SIT_initialization.initialize_user_input(SIT_initialization, user_input_file)
        report_file_related = ' -f=json.pretty -o=reports/output.json' + ' '
        feature_file_path = r'epg_scale_heal/features/epg_heal.feature '
        options = ' --no-capture --no-capture-stderr --no-logcapture -f plain'

        full_runner_options = report_file_related + feature_file_path + options

        runner_with_options.main(full_runner_options)
        generate_cucumber_report()

    elif operation == 'TOSCA-EPG-HEAL':
        log.info('operation : ' + operation + ' input file path : ' + user_input_file)
        ECM_POST_INSTALLATION.initialize_user_input(user_input_file)
        Initialization_script.store_user_input(Initialization_script, user_input_file)
        SIT_initialization.initialize_user_input(SIT_initialization, user_input_file)
        report_file_related = ' -f=json.pretty -o=reports/output.json' + ' '
        feature_file_path = r'epg_scale_heal/features/tosca_epg_heal.feature '
        options = ' --no-capture --no-capture-stderr --no-logcapture -f plain'

        full_runner_options = report_file_related + feature_file_path + options

        runner_with_options.main(full_runner_options)
        generate_cucumber_report()

    elif operation == 'EVNFM-TERMINATE':
        log.info('operation : ' + operation + ' input file path : ' + user_input_file)

        ECM_POST_INSTALLATION.initialize_user_input(user_input_file)
        Initialization_script.store_user_input(Initialization_script, user_input_file)
        SIT_initialization.initialize_user_input(SIT_initialization, user_input_file)

        report_file_related = ' -f=json.pretty -o=reports/output.json' + ' '
        feature_file_path = r'ccrc_cnf_deployment/features/terminate_evnfm_all.feature '
        options = ' --no-capture --no-capture-stderr --no-logcapture -f plain'

        full_runner_options = report_file_related + feature_file_path + options

        runner_with_options.main(full_runner_options)
        generate_cucumber_report()

    elif operation == 'CCRC-CNF-CLEANUP':
        log.info('operation : ' + operation + ' input file path : ' + user_input_file)

        ECM_POST_INSTALLATION.initialize_user_input(user_input_file)
        Initialization_script.store_user_input(Initialization_script, user_input_file)
        SIT_initialization.initialize_user_input(SIT_initialization, user_input_file)

        report_file_related = ' -f=json.pretty -o=reports/output.json' + ' '
        feature_file_path = r'ccrc_cnf_deployment/features/cleanup_ccrc.feature '
        options = ' --no-capture --no-capture-stderr --no-logcapture -f plain'

        full_runner_options = report_file_related + feature_file_path + options

        runner_with_options.main(full_runner_options)
        generate_cucumber_report()
    elif operation == 'ECM-PACKAGE-DEL':
        log.info(
            'operation : ' + operation + ' input file path : ' + user_input_file + ' with VNF_TYPE ' + str(vnf_type))
        SIT_initialization.initialize_user_input(SIT_initialization, user_input_file, vnf_type=vnf_type.upper())

        ECM_POST_INSTALLATION.initialize_user_input(user_input_file)
        report_file_related = ' -f=json.pretty -o=reports/output.json' + ' '
        feature_file_path = r'ecm_package_deletion/features/ecm_package_deletion.feature '
        options = ' --no-capture --no-capture-stderr --no-logcapture -f plain'

        full_runner_options = report_file_related + feature_file_path + options

        runner_with_options.main(full_runner_options)
        generate_cucumber_report()


    elif operation == 'ENM-LCM-INTEGRATION':
        log.info('operation : ' + operation + ' input file path : ' + user_input_file)

        ECM_POST_INSTALLATION.initialize_user_input(user_input_file)
        Initialization_script.store_user_input(Initialization_script, user_input_file)
        Initialization_script.store_LCM_service_server_data(Initialization_script, user_input_file)
        SIT_initialization.initialize_user_input(SIT_initialization, user_input_file)

        report_file_related = ' -f=json.pretty -o=reports/output.json' + ' '
        feature_file_path = r'enm_lcm_integration/features/enm_lcm_integration.feature '
        options = ' --no-capture --no-capture-stderr --no-logcapture -f plain'

        full_runner_options = report_file_related + feature_file_path + options

        runner_with_options.main(full_runner_options)
        generate_cucumber_report()


    elif operation == 'VCISCO-DEPLOY':
        log.info('operation : ' + operation + ' input file path : ' + user_input_file)
        ECM_POST_INSTALLATION.initialize_user_input(user_input_file)
        SIT_initialization.initialize_user_input(SIT_initialization, user_input_file)
        report_file_related = ' -f=json.pretty -o=reports/output.json' + ' '
        feature_file_path = r'vcisco_node_deployment/features/vcisco_deploy.feature '
        options = ' --no-capture --no-capture-stderr --no-logcapture -f plain'

        full_runner_options = report_file_related + feature_file_path + options

        runner_with_options.main(full_runner_options)
        generate_cucumber_report()

    elif operation == 'DC-GATEWAY':
        log.info('operation : ' + operation + ' input file path : ' + user_input_file)
        ECM_POST_INSTALLATION.initialize_user_input(user_input_file)
        SIT_initialization.initialize_user_input(SIT_initialization, user_input_file)
        report_file_related = ' -f=json.pretty -o=reports/output.json' + ' '
        feature_file_path = r'dc_gateway/features/dcgw_deploy.feature '
        options = ' --no-capture --no-capture-stderr --no-logcapture -f plain'

        full_runner_options = report_file_related + feature_file_path + options

        runner_with_options.main(full_runner_options)
        generate_cucumber_report()

    elif operation == 'DUMMY-MME':
        log.info('operation : ' + operation + ' input file path : ' + user_input_file)
        ECM_POST_INSTALLATION.initialize_user_input(user_input_file)
        SIT_initialization.initialize_user_input(SIT_initialization, user_input_file)

        report_file_related = ' -f=json.pretty -o=reports/output.json' + ' '
        feature_file_path = r'dummy_mme_gvnfm_deployment/features/dummy_mme_gvnfm_deploy.feature '
        options = ' --no-capture --no-capture-stderr --no-logcapture -f plain'

        full_runner_options = report_file_related + feature_file_path + options

        runner_with_options.main(full_runner_options)
        generate_cucumber_report()
    elif operation == 'ECM-SESSION-UPDATE':
        log.info('operation : ' + operation + ' input file path : ' + user_input_file)
        ECM_POST_INSTALLATION.initialize_user_input(user_input_file)
        SIT_initialization.initialize_user_input(SIT_initialization, user_input_file)

        report_file_related = ' -f=json.pretty -o=reports/output.json' + ' '
        feature_file_path = r'ecm_session_update/features/ecm_session_update.feature '
        options = ' --no-capture --no-capture-stderr --no-logcapture -f plain'

        full_runner_options = report_file_related + feature_file_path + options

        runner_with_options.main(full_runner_options)
        generate_cucumber_report()

    elif operation == 'ECDE-POST-INSTALL':

        log.info('operation : ' + operation + ' input file path : ' + user_input_file)
        ECM_POST_INSTALLATION.initialize_user_input(user_input_file)
        SIT_initialization.initialize_user_input(SIT_initialization, user_input_file)

        report_file_related = ' -f=json.pretty -o=reports/output.json' + ' '
        feature_file_path = r'ecde_node_deployment/features/ecde_post_install.feature  '
        options = ' --no-capture --no-capture-stderr --no-logcapture -f plain'

        full_runner_options = report_file_related + feature_file_path + options

        runner_with_options.main(full_runner_options)
        generate_cucumber_report()

    elif operation == 'ECDE-CDD-PREREQ':

        log.info('operation : ' + operation + ' input file path : ' + user_input_file)
        ECM_POST_INSTALLATION.initialize_user_input(user_input_file)
        SIT_initialization.initialize_user_input(SIT_initialization, user_input_file)

        report_file_related = ' -f=json.pretty -o=reports/output.json' + ' '
        feature_file_path = r'ecde_node_deployment/features/ecde_cdd_node_prerequisite.feature  '
        options = ' --no-capture --no-capture-stderr --no-logcapture -f plain'

        full_runner_options = report_file_related + feature_file_path + options

        runner_with_options.main(full_runner_options)
        generate_cucumber_report()



    elif operation == 'ECDE-CDD-DEPLOY':

        log.info('operation : ' + operation + ' input file path : ' + user_input_file)
        ECM_POST_INSTALLATION.initialize_user_input(user_input_file)
        SIT_initialization.initialize_user_input(SIT_initialization, user_input_file)

        report_file_related = ' -f=json.pretty -o=reports/output.json' + ' '
        feature_file_path = r'ecde_node_deployment/features/ecde_cdd_node_deploy.feature  '
        options = ' --no-capture --no-capture-stderr --no-logcapture -f plain'

        full_runner_options = report_file_related + feature_file_path + options

        runner_with_options.main(full_runner_options)
        generate_cucumber_report()

    elif operation == 'ECDE-SPIN':

        log.info('operation : ' + operation + ' input file path : ' + user_input_file)
        ECM_POST_INSTALLATION.initialize_user_input(user_input_file)
        SIT_initialization.initialize_user_input(SIT_initialization, user_input_file)

        report_file_related = ' -f=json.pretty -o=reports/output.json' + ' '
        feature_file_path = r'ecde_node_deployment/features/ecde_spinnaker_clean.feature  '
        options = ' --no-capture --no-capture-stderr --no-logcapture -f plain'

        full_runner_options = report_file_related + feature_file_path + options

        runner_with_options.main(full_runner_options)
        generate_cucumber_report()

    elif operation == 'ECDE-AAT-SETUP':

        log.info('operation : ' + operation + ' input file path : ' + user_input_file)
        ECM_POST_INSTALLATION.initialize_user_input(user_input_file)
        SIT_initialization.initialize_user_input(SIT_initialization, user_input_file)

        report_file_related = ' -f=json.pretty -o=reports/output.json' + ' '
        feature_file_path = r'ecde_node_deployment/features/ecde_aat_setup.feature  '
        options = ' --no-capture --no-capture-stderr --no-logcapture -f plain'

        full_runner_options = report_file_related + feature_file_path + options

        runner_with_options.main(full_runner_options)
        generate_cucumber_report()

    elif operation == 'ECDE-ECM-PRE':

        log.info('operation : ' + operation + ' input file path : ' + user_input_file)
        ECM_POST_INSTALLATION.initialize_user_input(user_input_file)
        SIT_initialization.initialize_user_input(SIT_initialization, user_input_file)

        report_file_related = ' -f=json.pretty -o=reports/output.json' + ' '
        feature_file_path = r'ecde_node_deployment/features/ecde_ecm_dummy_prerequisites.feature  '
        options = ' --no-capture --no-capture-stderr --no-logcapture -f plain'

        full_runner_options = report_file_related + feature_file_path + options

        runner_with_options.main(full_runner_options)
        generate_cucumber_report()


    elif operation == 'ECDE-VNFLCM-PRE':

        log.info('operation : ' + operation + ' input file path : ' + user_input_file)
        ECM_POST_INSTALLATION.initialize_user_input(user_input_file)
        SIT_initialization.initialize_user_input(SIT_initialization, user_input_file)

        report_file_related = ' -f=json.pretty -o=reports/output.json' + ' '
        feature_file_path = r'ecde_node_deployment/features/ecde_vnf-lcm_dummy_prerequisites.feature  '
        options = ' --no-capture --no-capture-stderr --no-logcapture -f plain'

        full_runner_options = report_file_related + feature_file_path + options

        runner_with_options.main(full_runner_options)
        generate_cucumber_report()

    elif operation == 'ECDE-EVNFM-PRE':

        log.info('operation : ' + operation + ' input file path : ' + user_input_file)
        ECM_POST_INSTALLATION.initialize_user_input(user_input_file)
        SIT_initialization.initialize_user_input(SIT_initialization, user_input_file)

        report_file_related = ' -f=json.pretty -o=reports/output.json' + ' '
        feature_file_path = r'ecde_node_deployment/features/ecde_evnfm_prerequisites.feature  '
        options = ' --no-capture --no-capture-stderr --no-logcapture -f plain'

        full_runner_options = report_file_related + feature_file_path + options

        runner_with_options.main(full_runner_options)
        generate_cucumber_report()

    elif operation == 'COLLECT-RUNTIME-DATA':
        log.info('operation : ' + operation + ' input file path : ' + user_input_file)
        ECM_POST_INSTALLATION.initialize_user_input(user_input_file)

        report_file_related = ' -f=json.pretty -o=reports/output.json' + ' '
        feature_file_path = r'collect_runtime_data/features/collect_runtime_data.feature  '
        options = ' --no-capture --no-capture-stderr --no-logcapture -f plain'

        full_runner_options = report_file_related + feature_file_path + options

        runner_with_options.main(full_runner_options)
        generate_cucumber_report()

    elif operation == 'CNF-NS-INSTANTIATION-PRE-REQ':

        log.info('operation : ' + operation + ' input file path : ' + user_input_file)
        ECM_POST_INSTALLATION.initialize_user_input(user_input_file)
        Initialization_script.store_user_input(Initialization_script, user_input_file)
        SIT_initialization.initialize_user_input(SIT_initialization, user_input_file)
        ecm_host_data = Initialization_script.get_model_objects(Initialization_script, 'ECM_CORE')
        is_cloudnative = Ecm_core.get_is_cloudnative(Ecm_core)

        report_file_related = ' -f=json.pretty -o=reports/output.json' + ' '
        if is_cloudnative:
            feature_file_path = r'cnf_ns_pre_requisite/features/cnf_ns_cn_pre_requisite.feature  '
        else:
            feature_file_path = r'cnf_ns_pre_requisite/features/cnf_ns_pre_requisite.feature  '
        options = ' --no-capture --no-capture-stderr --no-logcapture -f plain'

        full_runner_options = report_file_related + feature_file_path + options

        runner_with_options.main(full_runner_options)
        generate_cucumber_report()


    elif operation == 'EO_STAGING_ECM_CNF_ONBOARD':

        log.info('operation : ' + operation + ' input file path : ' + user_input_file)
        ECM_POST_INSTALLATION.initialize_user_input(user_input_file)
        Initialization_script.store_user_input(Initialization_script, user_input_file)
        SIT_initialization.initialize_user_input(SIT_initialization, user_input_file)

        report_file_related = ' -f=json.pretty -o=reports/output.json' + ' '
        feature_file_path = r'cnf_ns_deployment/features/cnf_package_onboard.feature '
        options = ' --no-capture --no-capture-stderr --no-logcapture -f plain'

        full_runner_options = report_file_related + feature_file_path + options

        runner_with_options.main(full_runner_options)
        generate_cucumber_report()

    elif operation == 'EO_STAGING_ECM_CNF_NS_ADD':

        log.info('operation : ' + operation + ' input file path : ' + user_input_file)
        ECM_POST_INSTALLATION.initialize_user_input(user_input_file)
        Initialization_script.store_user_input(Initialization_script, user_input_file)
        SIT_initialization.initialize_user_input(SIT_initialization, user_input_file)

        report_file_related = ' -f=json.pretty -o=reports/output.json' + ' '
        feature_file_path = r'cnf_ns_deployment/features/cnf_add.feature '
        options = ' --no-capture --no-capture-stderr --no-logcapture -f plain'

        full_runner_options = report_file_related + feature_file_path + options

        runner_with_options.main(full_runner_options)
        generate_cucumber_report()

    elif operation == 'EO_STAGING_ECM_CNF_NS_REMOVE':

        log.info('operation : ' + operation + ' input file path : ' + user_input_file)
        ECM_POST_INSTALLATION.initialize_user_input(user_input_file)
        Initialization_script.store_user_input(Initialization_script, user_input_file)
        SIT_initialization.initialize_user_input(SIT_initialization, user_input_file)

        report_file_related = ' -f=json.pretty -o=reports/output.json' + ' '
        feature_file_path = r'cnf_ns_deployment/features/cnf_remove.feature '
        options = ' --no-capture --no-capture-stderr --no-logcapture -f plain'

        full_runner_options = report_file_related + feature_file_path + options

        runner_with_options.main(full_runner_options)
        generate_cucumber_report()


    elif operation == 'EO_STAGING_ECM_CNF_NS_SCALE_OUT':

        log.info('operation : %s input file path : %s', operation, user_input_file)
        ECM_POST_INSTALLATION.initialize_user_input(user_input_file)
        Initialization_script.store_user_input(Initialization_script, user_input_file)
        SIT_initialization.initialize_user_input(SIT_initialization, user_input_file)

        report_file_related = ' -f=json.pretty -o=reports/output.json' + ' '
        feature_file_path = r'cnf_ns_deployment/features/cnf_ns_scale_out.feature '
        options = ' --no-capture --no-capture-stderr --no-logcapture -f plain'

        full_runner_options = report_file_related + feature_file_path + options

        runner_with_options.main(full_runner_options)
        generate_cucumber_report()


    elif operation == 'EO_STAGING_ECM_CNF_NS_SCALE_IN':

        log.info('operation : %s input file path : %s', operation, user_input_file)
        ECM_POST_INSTALLATION.initialize_user_input(user_input_file)
        Initialization_script.store_user_input(Initialization_script, user_input_file)
        SIT_initialization.initialize_user_input(SIT_initialization, user_input_file)

        report_file_related = ' -f=json.pretty -o=reports/output.json' + ' '
        feature_file_path = r'cnf_ns_deployment/features/cnf_ns_scale_in.feature '
        options = ' --no-capture --no-capture-stderr --no-logcapture -f plain'

        full_runner_options = report_file_related + feature_file_path + options

        runner_with_options.main(full_runner_options)
        generate_cucumber_report()

    elif operation == 'EO_STAGING_ECM_CNF_NS_DEPLOY':

        log.info('operation : ' + operation + ' input file path : ' + user_input_file)
        ECM_POST_INSTALLATION.initialize_user_input(user_input_file)
        Initialization_script.store_user_input(Initialization_script, user_input_file)
        SIT_initialization.initialize_user_input(SIT_initialization, user_input_file)

        report_file_related = ' -f=json.pretty -o=reports/output.json' + ' '
        feature_file_path = r'cnf_ns_deployment/features/cnf_ns_deployment.feature '
        options = ' --no-capture --no-capture-stderr --no-logcapture -f plain'

        full_runner_options = report_file_related + feature_file_path + options

        runner_with_options.main(full_runner_options)
        generate_cucumber_report()

    elif operation == 'EO_STAGING_ECM_NS_TERMINATE':

        log.info('operation %s input file path : %s with VNF_TYPE %s', operation, user_input_file, str(vnf_type))
        ECM_POST_INSTALLATION.initialize_user_input(user_input_file)
        Initialization_script.store_user_input(Initialization_script, user_input_file)
        SIT_initialization.initialize_user_input(SIT_initialization, user_input_file, vnf_type=vnf_type)

        report_file_related = ' -f=json.pretty -o=reports/output.json' + ' '
        feature_file_path = r'cnf_ns_deployment/features/terminate_network_service.feature  '
        options = ' --no-capture --no-capture-stderr --no-logcapture -f plain'

        full_runner_options = report_file_related + feature_file_path + options

        runner_with_options.main(full_runner_options)
        generate_cucumber_report()

    elif operation == 'CNFNS-DELETE-SECRET-EVNFM':

        log.info('operation : ' + operation + ' input file path : ' + user_input_file)
        ECM_POST_INSTALLATION.initialize_user_input(user_input_file)
        Initialization_script.store_user_input(Initialization_script, user_input_file)
        SIT_initialization.initialize_user_input(SIT_initialization, user_input_file)

        report_file_related = ' -f=json.pretty -o=reports/output.json' + ' '
        feature_file_path = r'cnf_ns_deployment/features/delete_secret_on_evnfm.feature  '
        options = ' --no-capture --no-capture-stderr --no-logcapture -f plain'

        full_runner_options = report_file_related + feature_file_path + options

        runner_with_options.main(full_runner_options)
        generate_cucumber_report()

    elif operation == 'ENABLE-LOG':

        log.info('operation : ' + operation + ' input file path : ' + user_input_file)
        ECM_POST_INSTALLATION.initialize_user_input(user_input_file)

        SIT_initialization.initialize_user_input(SIT_initialization, user_input_file)

        report_file_related = ' -f=json.pretty -o=reports/output.json' + ' '
        feature_file_path = r'app_log_enable_disbale/features/app_log_enable.feature  '
        options = ' --no-capture --no-capture-stderr --no-logcapture -f plain'

        full_runner_options = report_file_related + feature_file_path + options

        runner_with_options.main(full_runner_options)
        generate_cucumber_report()

    elif operation == 'DISABLE-LOG':

        log.info('operation : ' + operation + ' input file path : ' + user_input_file)
        ECM_POST_INSTALLATION.initialize_user_input(user_input_file)

        SIT_initialization.initialize_user_input(SIT_initialization, user_input_file)

        report_file_related = ' -f=json.pretty -o=reports/output.json' + ' '
        feature_file_path = r'app_log_enable_disbale/features/app_log_disable.feature  '
        options = ' --no-capture --no-capture-stderr --no-logcapture -f plain'

        full_runner_options = report_file_related + feature_file_path + options

        runner_with_options.main(full_runner_options)
        generate_cucumber_report()

    elif operation == 'ECDE-ECM-DEPLOY':

        log.info('operation : ' + operation + ' input file path : ' + user_input_file)
        ECM_POST_INSTALLATION.initialize_user_input(user_input_file)
        SIT_initialization.initialize_user_input(SIT_initialization, user_input_file)

        report_file_related = ' -f=json.pretty -o=reports/output.json' + ' '
        feature_file_path = r'ecde_node_deployment/features/ecde_ecm_dummy_deployment.feature  '
        options = ' --no-capture --no-capture-stderr --no-logcapture -f plain'

        full_runner_options = report_file_related + feature_file_path + options

        runner_with_options.main(full_runner_options)
        generate_cucumber_report()


    elif operation == 'ECDE-DYANAMIC-VNFLCM-DEPLOY':

        log.info('operation : ' + operation + ' input file path : ' + user_input_file)

        # Add nfvo initialization if add nfvo scenario comes in picture
        ECM_POST_INSTALLATION.initialize_user_input(user_input_file)
        SIT_initialization.initialize_user_input(SIT_initialization, user_input_file, dynamic_project=True)

        report_file_related = ' -f=json.pretty -o=reports/output.json' + ' '
        feature_file_path = r'ecde_node_deployment/features/ecde_vnflcm_dummy_deployment.feature  '
        options = ' --no-capture --no-capture-stderr --no-logcapture -f plain'

        full_runner_options = report_file_related + feature_file_path + options

        runner_with_options.main(full_runner_options)
        generate_cucumber_report()

    elif operation == 'ECDE-ECM-3PP-DEPLOY':

        log.info('operation : ' + operation + ' input file path : ' + user_input_file)

        # Add nfvo initialization if add nfvo scenario comes in picture
        ECM_POST_INSTALLATION.initialize_user_input(user_input_file)
        SIT_initialization.initialize_user_input(SIT_initialization, user_input_file, dynamic_project=True)

        report_file_related = ' -f=json.pretty -o=reports/output.json' + ' '
        feature_file_path = r'ecde_node_deployment/features/ecde_ecm_3pp_deployment.feature  '
        options = ' --no-capture --no-capture-stderr --no-logcapture -f plain'

        full_runner_options = report_file_related + feature_file_path + options

        runner_with_options.main(full_runner_options)
        generate_cucumber_report()


    elif operation == 'ECDE-EVNFM-DUMMY-DEPLOY':

        log.info('operation : ' + operation + ' input file path : ' + user_input_file)
        ECM_POST_INSTALLATION.initialize_user_input(user_input_file)
        SIT_initialization.initialize_user_input(SIT_initialization, user_input_file)

        report_file_related = ' -f=json.pretty -o=reports/output.json' + ' '
        feature_file_path = r'ecde_node_deployment/features/ecde_evnfm_dummy_deployment.feature  '
        options = ' --no-capture --no-capture-stderr --no-logcapture -f plain'

        full_runner_options = report_file_related + feature_file_path + options

        runner_with_options.main(full_runner_options)
        generate_cucumber_report()

    elif operation == 'EO-PURGE':

        log.info('operation : ' + operation + ' input file path : ' + user_input_file)
        ECM_POST_INSTALLATION.initialize_user_input(user_input_file)
        SIT_initialization.initialize_user_input(SIT_initialization, user_input_file)

        report_file_related = ' -f=json.pretty -o=reports/output.json' + ' '
        feature_file_path = r'eo_purge/features/eo_purge.feature  '
        options = ' --no-capture --no-capture-stderr --no-logcapture -f plain'

        full_runner_options = report_file_related + feature_file_path + options

        runner_with_options.main(full_runner_options)
        generate_cucumber_report()

    elif operation == 'L2-L3-DCGW':
        log.info('operation : ' + operation + ' input file path : ' + user_input_file)
        ECM_POST_INSTALLATION.initialize_user_input(user_input_file)
        SIT_initialization.initialize_user_input(SIT_initialization, user_input_file)

        report_file_related = ' -f=json.pretty -o=reports/output.json' + ' '
        feature_file_path = r'l2_l3_dcgw/features/l2_l3_dcgw.feature  '
        options = ' --no-capture --no-capture-stderr --no-logcapture -f plain'

        full_runner_options = report_file_related + feature_file_path + options

        runner_with_options.main(full_runner_options)
        generate_cucumber_report()

    elif operation == 'REFRESH-POD-TOKEN-EO':
        log.info('operation : ' + operation + ' input file path : ' + user_input_file)
        ECM_POST_INSTALLATION.initialize_user_input(user_input_file)
        SIT_initialization.initialize_user_input(SIT_initialization, user_input_file)

        report_file_related = ' -f=json.pretty -o=reports/output.json' + ' '
        feature_file_path = r'eo_purge/features/refresh_pod_token.feature  '
        options = ' --no-capture --no-capture-stderr --no-logcapture -f plain'

        full_runner_options = report_file_related + feature_file_path + options

        runner_with_options.main(full_runner_options)
        generate_cucumber_report()

    elif operation == 'EPG-ETSI-NSD-PRE':
        log.info('operation : ' + operation + ' input file path : ' + user_input_file)
        ECM_POST_INSTALLATION.initialize_user_input(user_input_file)
        SIT_initialization.initialize_user_input(SIT_initialization, user_input_file)

        report_file_related = ' -f=json.pretty -o=reports/output.json' + ' '
        feature_file_path = r'epg_etsi_tosca_nsd_deployment/features/epg_etsi_tosca_nsd_prerequisite.feature  '
        options = ' --no-capture --no-capture-stderr --no-logcapture -f plain'

        full_runner_options = report_file_related + feature_file_path + options

        runner_with_options.main(full_runner_options)
        generate_cucumber_report()

    elif operation == 'EPG-TOSCA-PRE':
        log.info('operation : ' + operation + ' input file path : ' + user_input_file)
        ECM_POST_INSTALLATION.initialize_user_input(user_input_file)
        SIT_initialization.initialize_user_input(SIT_initialization, user_input_file)

        report_file_related = ' -f=json.pretty -o=reports/output.json' + ' '
        feature_file_path = r'epg_tosca_deployment/features/epg_tosca_prerequisite.feature  '
        options = ' --no-capture --no-capture-stderr --no-logcapture -f plain'

        full_runner_options = report_file_related + feature_file_path + options

        runner_with_options.main(full_runner_options)
        generate_cucumber_report()

    elif operation == 'EPG-ETSI-NSD-DEPLOY':
        log.info('operation : ' + operation + ' input file path : ' + user_input_file)
        ECM_POST_INSTALLATION.initialize_user_input(user_input_file)
        SIT_initialization.initialize_user_input(SIT_initialization, user_input_file)

        report_file_related = ' -f=json.pretty -o=reports/output.json' + ' '
        feature_file_path = r'epg_etsi_tosca_nsd_deployment/features/epg_etsi_tosca_nsd_deploy.feature  '
        options = ' --no-capture --no-capture-stderr --no-logcapture -f plain'

        full_runner_options = report_file_related + feature_file_path + options

        runner_with_options.main(full_runner_options)
        generate_cucumber_report()

    elif operation == 'EO_STAGING_ECM_EPG_ETSI_TOSCA_DEPLOY':
        log.info('operation : ' + operation + ' input file path : ' + user_input_file)
        ECM_POST_INSTALLATION.initialize_user_input(user_input_file)
        SIT_initialization.initialize_user_input(SIT_initialization, user_input_file)

        report_file_related = ' -f=json.pretty -o=reports/output.json' + ' '
        feature_file_path = r'epg_etsi_tosca_nsd_deployment/features/ecm_epg_etsi_tosca_deploy.feature  '
        options = ' --no-capture --no-capture-stderr --no-logcapture -f plain'

        full_runner_options = report_file_related + feature_file_path + options

        runner_with_options.main(full_runner_options)
        generate_cucumber_report()

    elif operation == 'EPG-TOSCA-SO-DEPLOY':
        log.info('operation : ' + operation + ' input file path : ' + user_input_file)
        ECM_POST_INSTALLATION.initialize_user_input(user_input_file)
        SIT_initialization.initialize_user_input(SIT_initialization, user_input_file)

        report_file_related = ' -f=json.pretty -o=reports/output.json' + ' '
        feature_file_path = r'epg_tosca_deployment/features/epg_tosca_so_deployment.feature  '
        options = ' --no-capture --no-capture-stderr --no-logcapture -f plain'

        full_runner_options = report_file_related + feature_file_path + options

        runner_with_options.main(full_runner_options)
        generate_cucumber_report()

    elif operation == 'EO_STAGING_EPG_TOSCA_ECM_DEPLOY':
        log.info('operation : ' + operation + ' input file path : ' + user_input_file)
        ECM_POST_INSTALLATION.initialize_user_input(user_input_file)
        SIT_initialization.initialize_user_input(SIT_initialization, user_input_file)

        report_file_related = ' -f=json.pretty -o=reports/output.json' + ' '
        feature_file_path = r'epg_tosca_deployment/features/epg_tosca_ecm_deployment.feature  '
        options = ' --no-capture --no-capture-stderr --no-logcapture -f plain'

        full_runner_options = report_file_related + feature_file_path + options

        runner_with_options.main(full_runner_options)
        generate_cucumber_report()

    elif operation == 'WORKFLOW-INSTALL':
        log.info(
            'operation : ' + operation + ' input file path : ' + user_input_file + ' with RPM ' + str(vnf_type))
        ECM_POST_INSTALLATION.initialize_user_input(user_input_file)
        SIT_initialization.initialize_user_input(SIT_initialization, user_input_file, vnf_type=vnf_type.upper())
        report_file_related = ' -f=json.pretty -o=reports/output.json' + ' '
        feature_file_path = r'workflow_rpm_install/features/workflow_rpm_install.feature '
        options = ' --no-capture --no-capture-stderr --no-logcapture -f plain'

        full_runner_options = report_file_related + feature_file_path + options

        runner_with_options.main(full_runner_options)
        generate_cucumber_report()

    elif operation == 'RPM-INSTALL':
        log.info(
            'operation : ' + operation + ' input file path : ' + user_input_file + ' with RPM_LINK ' + str(vnf_type))
        ECM_POST_INSTALLATION.initialize_user_input(user_input_file)
        SIT_initialization.initialize_user_input(SIT_initialization, user_input_file, vnf_type=vnf_type.upper())
        report_file_related = ' -f=json.pretty -o=reports/output.json' + ' '
        feature_file_path = r'generic_workflow_install/features/generic_workflow_install.feature '
        options = ' --no-capture --no-capture-stderr --no-logcapture -f plain'

        full_runner_options = report_file_related + feature_file_path + options

        runner_with_options.main(full_runner_options)
        generate_cucumber_report()

    elif operation == 'UDS-VNF-PRE-REQ':
        log.info('operation : ' + operation + ' input file path : ' + user_input_file)
        ECM_POST_INSTALLATION.initialize_user_input(user_input_file)
        SIT_initialization.initialize_user_input(SIT_initialization, user_input_file)

        report_file_related = ' -f=json.pretty -o=reports/output.json' + ' '
        feature_file_path = r'uds_vnf_pre_req/features/uds_vnf_pre_req.feature  '
        options = ' --no-capture --no-capture-stderr --no-logcapture -f plain'

        full_runner_options = report_file_related + feature_file_path + options

        runner_with_options.main(full_runner_options)
        generate_cucumber_report()

    elif operation == 'UDS-NFV-PRE-REQ':
        log.info('operation : ' + operation + ' input file path : ' + user_input_file)
        ECM_POST_INSTALLATION.initialize_user_input(user_input_file)
        SIT_initialization.initialize_user_input(SIT_initialization, user_input_file)

        report_file_related = ' -f=json.pretty -o=reports/output.json' + ' '
        feature_file_path = r'uds_nfv_pre_req/features/uds_nfv_pre_req.feature  '
        options = ' --no-capture --no-capture-stderr --no-logcapture -f plain'
        full_runner_options = report_file_related + feature_file_path + options

        runner_with_options.main(full_runner_options)
        generate_cucumber_report()

    elif operation == 'UDS-DELETE-PRE-REQ':
        log.info('operation : ' + operation + ' input file path : ' + user_input_file)
        ECM_POST_INSTALLATION.initialize_user_input(user_input_file)
        SIT_initialization.initialize_user_input(SIT_initialization, user_input_file)
        report_file_related = ' -f=json.pretty -o=reports/output.json' + ' '
        feature_file_path = r'uds_delete_pre_req/features/uds_delete_pre_req.feature  '
        options = ' --no-capture --no-capture-stderr --no-logcapture -f plain'
        full_runner_options = report_file_related + feature_file_path + options
        runner_with_options.main(full_runner_options)
        generate_cucumber_report()

    elif operation == 'EAIND-SUPERUSER-CREATION':
        log.info('operation : ' + operation + ' input file path : ' + user_input_file)
        ECM_POST_INSTALLATION.initialize_user_input(user_input_file)
        SIT_initialization.initialize_user_input(SIT_initialization, user_input_file)

        report_file_related = ' -f=json.pretty -o=reports/output.json' + ' '
        feature_file_path = r'eai_nd_superuser_creation/features/eai_nd_superuser_creation.feature  '
        options = ' --no-capture --no-capture-stderr --no-logcapture -f plain'

        full_runner_options = report_file_related + feature_file_path + options

        runner_with_options.main(full_runner_options)
        generate_cucumber_report()


    elif operation == 'VERIFY-PROJECT-EXISTS-CCM':
        log.info(
            'operation : ' + operation + ' input file path : ' + user_input_file + ' with VNF_TYPE ' + str(vnf_type))
        ECM_POST_INSTALLATION.initialize_user_input(user_input_file)
        SIT_initialization.initialize_user_input(SIT_initialization, user_input_file, vnf_type=vnf_type.upper())
        report_file_related = ' -f=json.pretty -o=reports/output.json' + ' '
        feature_file_path = r'ccm_project_verification/features/ccm_project_verification.feature '
        options = ' --no-capture --no-capture-stderr --no-logcapture -f plain'

        full_runner_options = report_file_related + feature_file_path + options

        runner_with_options.main(full_runner_options)
        generate_cucumber_report()

    elif operation == 'ENM-TOSCA-NODE-CLEANUP':
        log.info(
            'operation : ' + operation + ' input file path : ' + user_input_file + ' with VNF_TYPE ' + str(vnf_type))
        ECM_POST_INSTALLATION.initialize_user_input(user_input_file)
        SIT_initialization.initialize_user_input(SIT_initialization, user_input_file, vnf_type=vnf_type.upper())
        report_file_related = ' -f=json.pretty -o=reports/output.json' + ' '
        feature_file_path = r'enm_node_cleanup/features/enm_tosca_node_cleanup.feature '
        options = ' --no-capture --no-capture-stderr --no-logcapture -f plain'

        full_runner_options = report_file_related + feature_file_path + options

        runner_with_options.main(full_runner_options)
        generate_cucumber_report()

    elif operation == 'ENM-ETSI-TOSCA-NODE-CLEANUP':
        log.info(
            'operation : ' + operation + ' input file path : ' + user_input_file + ' with VNF_TYPE ' + str(vnf_type))
        ECM_POST_INSTALLATION.initialize_user_input(user_input_file)
        SIT_initialization.initialize_user_input(SIT_initialization, user_input_file, vnf_type=vnf_type.upper())
        report_file_related = ' -f=json.pretty -o=reports/output.json' + ' '
        feature_file_path = r'enm_node_cleanup/features/enm_etsi_tosca_node_cleanup.feature '
        options = ' --no-capture --no-capture-stderr --no-logcapture -f plain'

        full_runner_options = report_file_related + feature_file_path + options

        runner_with_options.main(full_runner_options)
        generate_cucumber_report()

    elif operation == 'EO_STAGING_UDS_ST_CREATE_AND_DISTRIBUTE':
        log.info('operation : ' + operation + ' input file path : ' + user_input_file)
        ECM_POST_INSTALLATION.initialize_user_input(user_input_file)
        SIT_initialization.initialize_user_input(SIT_initialization, user_input_file)

        report_file_related = ' -f=json.pretty -o=reports/output.json' + ' '
        feature_file_path = r'uds_so_st_creation_and_distribution/features/uds_st_create_and_distribute.feature  '
        options = ' --no-capture --no-capture-stderr --no-logcapture -f plain'

        full_runner_options = report_file_related + feature_file_path + options

        runner_with_options.main(full_runner_options)
        generate_cucumber_report()

    elif operation == 'EO_STAGING_UDS_SO_TEPG_DEPLOYMENT':
        log.info('operation : ' + operation + ' input file path : ' + user_input_file)
        ECM_POST_INSTALLATION.initialize_user_input(user_input_file)
        SIT_initialization.initialize_user_input(SIT_initialization, user_input_file)

        report_file_related = ' -f=json.pretty -o=reports/output.json' + ' '
        feature_file_path = r'uds_so_tepg_deployment/features/uds_so_tepg_deploy.feature  '
        options = ' --no-capture --no-capture-stderr --no-logcapture -f plain'

        full_runner_options = report_file_related + feature_file_path + options

        runner_with_options.main(full_runner_options)
        generate_cucumber_report()

    elif operation == 'EO_STAGING_ECM_CMDB_VAPP_CLEANUP':
        log.info('operation : ' + operation + ' input file path : ' + user_input_file)
        ECM_POST_INSTALLATION.initialize_user_input(user_input_file)
        SIT_initialization.initialize_user_input(SIT_initialization, user_input_file)

        report_file_related = ' -f=json.pretty -o=reports/output.json' + ' '
        feature_file_path = r'eocm_cmdb_cleanup/features/cmdb_vapp_cleanup.feature  '
        options = ' --no-capture --no-capture-stderr --no-logcapture -f plain'

        full_runner_options = report_file_related + feature_file_path + options

        runner_with_options.main(full_runner_options)
        generate_cucumber_report()

    elif operation == 'EO_STAGING_ECM_CMDB_NS_CLEANUP':
        log.info('operation : ' + operation + ' input file path : ' + user_input_file)
        ECM_POST_INSTALLATION.initialize_user_input(user_input_file)
        SIT_initialization.initialize_user_input(SIT_initialization, user_input_file)

        report_file_related = ' -f=json.pretty -o=reports/output.json' + ' '
        feature_file_path = r'eocm_cmdb_cleanup/features/cmdb_ns_cleanup.feature  '
        options = ' --no-capture --no-capture-stderr --no-logcapture -f plain'

        full_runner_options = report_file_related + feature_file_path + options

        runner_with_options.main(full_runner_options)
        generate_cucumber_report()

    elif operation == 'NODESELCTOR-VERIFICATION':
        log.info('operation: ' + operation + ' input file path: ' + user_input_file + ' with VNF_TYPE ' + str(vnf_type))

        ECM_POST_INSTALLATION.initialize_user_input(user_input_file)
        SIT_initialization.initialize_user_input(SIT_initialization, user_input_file, vnf_type=vnf_type)

        report_file_related = ' -f=json.pretty -o=reports/output.json' + ' '
        feature_file_path = r'nodeselector_test/features/nodeselector_test.feature'
        options = ' --no-capture --no-capture-stderr --no-logcapture -f plain'

        full_runner_options = report_file_related + feature_file_path + options

        runner_with_options.main(full_runner_options)
        generate_cucumber_report()

    elif operation == 'EO_STAGING_NS_PDB_CHECK':
        log.info(
            'operation : ' + operation + ' input file path : ' + user_input_file + ' with VNF_TYPE ' + str(vnf_type))
        ECM_POST_INSTALLATION.initialize_user_input(user_input_file)
        SIT_initialization.initialize_user_input(SIT_initialization, user_input_file, vnf_type=vnf_type)
        report_file_related = ' -f=json.pretty -o=reports/output.json' + ' '
        feature_file_path = r'ns_pdb_monitor/features/ns_pdb_monitor.feature'
        options = ' --no-capture --no-capture-stderr --no-logcapture -f plain'

        full_runner_options = report_file_related + feature_file_path + options

        runner_with_options.main(full_runner_options)
        generate_cucumber_report()

    elif operation == 'CHECK-POD-RESTARTS':
        log.info(
            'operation : ' + operation + ' input file path : ' + user_input_file + ' with VNF_TYPE ' + str(vnf_type))
        ECM_POST_INSTALLATION.initialize_user_input(user_input_file)
        SIT_initialization.initialize_user_input(SIT_initialization, user_input_file, vnf_type=vnf_type.upper())
        report_file_related = ' -f=json.pretty -o=reports/output.json' + ' '
        feature_file_path = r'pod_monitor/features/pod_monitor.feature'
        options = ' --no-capture --no-capture-stderr -f plain'

        full_runner_options = report_file_related + feature_file_path + options

        runner_with_options.main(full_runner_options)
        generate_cucumber_report()

    elif operation == 'EO_STAGING_HELM_CHART_VERSION':
        log.info(
            'operation : ' + operation + ' input file path : ' + user_input_file + ' with helm name ' + str(vnf_type))
        ECM_POST_INSTALLATION.initialize_user_input(user_input_file)
        SIT_initialization.initialize_user_input(SIT_initialization, user_input_file, vnf_type=vnf_type)
        report_file_related = ' -f=json.pretty -o=reports/output.json' + ' '
        feature_file_path = r'helm_chart_version/features/helm_chart_version.feature'
        options = ' --no-capture --no-capture-stderr --no-logcapture -f plain'

        full_runner_options = report_file_related + feature_file_path + options

        runner_with_options.main(full_runner_options)
        generate_cucumber_report()

    elif operation == 'EO_STAGING_OPENSTACK_STACK_CLEANUP':
        log.info(f'operation :  {operation} input file path :  {user_input_file}')
        ECM_POST_INSTALLATION.initialize_user_input(user_input_file)
        SIT_initialization.initialize_user_input(SIT_initialization, user_input_file)
        report_file_related = ' -f=json.pretty -o=reports/output.json' + ' '
        feature_file_path = r'openstack_stack_cleanup/features/openstack_stack_cleanup.feature'
        options = ' --no-capture --no-capture-stderr --no-logcapture -f plain'

        full_runner_options = report_file_related + feature_file_path + options

        runner_with_options.main(full_runner_options)
        generate_cucumber_report()

    elif operation == 'EO_STAGING_MONITOR_UNAPPROVED_RESOURCES_DEPLOYED':
        log.info('operation : %s input file path : %s', operation, user_input_file)
        ECM_POST_INSTALLATION.initialize_user_input(user_input_file)
        SIT_initialization.initialize_user_input(SIT_initialization, user_input_file, vnf_type=vnf_type)
        report_file_related = ' -f=json.pretty -o=reports/output.json' + ' '
        feature_file_path = r'monitor_resources_deployed/features/monitor_unapproved_resources.feature'
        options = ' --no-capture --no-capture-stderr --no-logcapture -f plain'

        full_runner_options = report_file_related + feature_file_path + options

        runner_with_options.main(full_runner_options)
        generate_cucumber_report()

def main():
    parser = argparse.ArgumentParser(formatter_class=argparse.RawDescriptionHelpFormatter,
                                     description=textwrap.dedent('''\
                                          <<< DO - AUTOMATON Help page >>>
                                        ----------------------------------------------------------------------------------------
                                        operation keywords:
                                        ----------------------------------------------------------------------------------------
                                        VNF-ECM      : To integrate VNF-LCM with ECM
                                        VNF-ENM      : To integrate VNF-LCM with ENM
                                        SC           : To create site
                                        RVPC         : To VIM Registration using ECM API & To Project creation
                                        EPIS         : To ECM post installation steps
                                        SIT          : To System integration test with VNF-LCM deployed on static project (onboard ,deploy ,terminate for dummy node )
                                        CEE-CLEANUP  : To clean up the CEE (openstack )
                                        LPIS         : To VNF-LCM Post installation steps for Static Project
                                        SIT-SO       : To deploy a node from Service orchestrator 
                                        SO-CLEANUP   : To clean the SO subsystems and services
                                        EPG-ECM-PRE  : TO get the environment ready to deploy EPG
                                        EPG-ECM      : To deploy EPG node from EO-CM
                                        EPG-SO       : To deploy EPG node from SO
                                        MME-PRE      : TO get the environment ready to deploy MME
                                        MME-SO       : To deploy MME node from SO
                                        SBG-ECM-PRE  : TO get the environment ready to deploy SBG
                                        SBG-ECM      : To deploy SBG node from EO-CM
                                        BGF-ECM-PRE  : TO get the environment ready to deploy BGF
                                        BGF-ECM      : To deploy BGF node from EO-CM
                                        MTAS-ECM-PRE : TO get the environment ready to deploy MTAS
                                        MTAS-ECM     : To deploy MTAS node from EO-CM
                                        CSCF-ECM-PRE : TO get the environment ready to deploy CSCF
                                        CSCF-ECM     : To deploy CSCF node from EO-CM
                                        VCISCO-DEPLOY: To deploy vCisco
                                        DC-GATEWAY   : To Configure DC-Gateway
                                        DUMMY-MME    : To deploy a dummy MME node using GVNFM
                                        SO-SERVICES-DEL : To Delete all the network services from SO
                                        ECM-DEL      : To Delete all the nodes and network from ECM
                                        LPIS-DYNAMIC: To VNF-LCM Post installation steps for Dynamic Project
                                        SIT-EO-VNFLCM : To System integration test with VNF-LCM deployed on dynamic project (onboard ,deploy ,terminate for dummy node )
                                        LCM-VM-SHUT-STATIC: To Test the VNFLCM deployed in Static project Fail over VM
                                        LCM-VM-SHUT-DYNAMIC: To Test the VNFLCM deployed in Dynamic project Fail over VM
                                        IMS-ECM-PRE: To configure common task of IMS node
                                        PROJ-VIM: To synch the existing project with VIM
                                        SYNC-VIM-CAPACITY: To synch vim capacity
                                        ECDE-ECM-PRE: To get the environment ready for ECDE-ECM dummy deployment
                                        ECDE-EVNFM-PRE: To get the environment ready for ECDE-EVNFM dummy deployment
                                        ECDE-VNFLCM-PRE: To get the environment ready for ECDE-VNFLCM dummy deployment
                                        ECDE-ECM-DEPLOY: To deploy dummy VNF ECDE-ECM
                                        ECDE-DYANAMIC-VNFLCM-DEPLOY : To deploy dummy VNF ECDE-VNFLCM dynamic
                                        ECDE-ECM-3PP-DEPLOY: To deploy 3pp VNF ECDE-ECM
                                        ECDE-EVNFM-DUMMY-DEPLOY: To deploy dummy VNF ECDE-EVNFM
                                        SO-POST : To SO post installation steps
                                        SO-CCD : To fetch CCD Version
                                        RECONCILE-DUMMY : To Reconcile vApp
                                        EPG-REDISCOVERY : Redisover EPG from ECM
                                        MME-REDISCOVERY : Rediscover MME from ECM
                                        VBGF_TOSCA_PRE :To get the environment ready to deploy TOSCA BGF                                       
                                        VBGF_TOSCA_DEPLOY : To deploy TOSCA BGF node from EO-CM
                                        ECM-PACKAGE-DEL : To delete all the packages on ECM
                                        ENM-POST : To perform ENM post install activities
                                        ENM-LCM-INTEGRATION : Job to integrate between ENM and VNF-LCM
                                        VM-VNFM-INTEGRATION : Job to integrate VM-VNFM and ECM
                                        SO-DUMMY-VM-VNFM : Job to deploy VM-VNFM dummy node from SO
                                        ETSI_TOSCA_DUMMY_DEPLOYMENT : Dummy tosca VNF deployement in ECM 
                                        ETSI_DUMMY_TOSCA_SCALE_HEAL : Scale heal for dummy tosca
                                        CISMS-ZONE-REGISTER : Job to Register CISMS Zone Cluster
                                        CISMS-ZONE-DEREGISTER : Job to De-register CISMS Zone Cluster
                                        ECM-SESSION-UPDATE : To update the session of ECM in OPEN-AM
                                        MODIFY_TOSCA_DUMMY_PARAM: to modify configurable attributes for TOSCA_DUMMY
                                        EOCM-DUMMY-SCALE : To perform SCALE IN and OUT of dummy node from EOCM
                                        EPG-SO-VM-VNFM       : To deploy EPG node from SO into VM-VNFM
                                        EPG-PRE-VM-VNFM      : To get the environment ready to deploy EPG into VM-VNFM
                                        MME-PRE-VM-VNFM      : To get the environment ready to deploy MME into VM-VNFM
                                        CNF-NS-INSTANTIATION-PRE-REQ : To get the environment ready to deploy E-VNFM
                                        MME-SO-VM-VNFM        : To deploy MME node from SO into VM-VNFM
                                        SO-DEPLOY-LCM-VM-SHUT : To Test the SO Dummy Deploy LCM Fail over VM
                                        CCRC-CNF-ONBOARD : To Onboard CCRC CNF Package
                                        CCRC-CNF-DEPLOY : To Deploy CCRC CNF Package
                                        CCRC-CNF-UPGRADE : To upgrade CCRC CNF Package
                                        CCRC-CNF-SCALE : To scale out -in  CCRC CNF Package
                                        CCRC-CNF-TERMINATE : To clean CCRC deployment
                                        EVNFM-PACKAGE-DEL : To delete CCRC packages 
                                        SO-RANDOM-TASK : To perform SO Random Operations
                                        SO-LOGVIEWER-ROLE : To create SO user with Logview Role
                                        SO-SUBSYSTEM-CHECK : To check subsystem accessibility
                                        DUMMY-NODE-HEAL : To perform HEAL on Dummy node
                                        SO-DEPLOY-DUMMY : To deploy Dummy node from SO
                                        CLUSTER-CONFIG   : TO upload cluster config to EVNFM
                                        SOL-BGF-PRE-REQ : To get the environment ready to deploy SOL TOSCA BGF 
                                        SO-DEPLOY-SOL-BGF: To deploy SOL TOSCA BGF node from SO
                                        EO_STAGING_ECM_CNF_ONBOARD : To onboard CNF package from EO-CM
                                        EO_STAGING_ECM_CNF_NS_DEPLOY: To deploy CNF NS Instantiation from EO-CM
                                        EPG-VNF-ECM : To deploy EPG from ECM for VNF-STAGING 
                                        EPG-VNF-ECM-PRE : to prepare env for deploy EPG from ECM for VNF-STAGING
                                        MME-VNF-ECM-PRE : to prepare env for deploy MME from ECM for VNF-STAGING
                                        MME-VNF-ECM : To deploy MME from ECM for VNF-STAGING
                                        WANO-SERVICE :To create service in wano
                                        CCRC-UPGRADE-ONBOARD: To onboard upgrade package 
                                        CCRC-CNF-CLEANUP: To cleanup the env after CNF terminate
                                        COLLECT-RUNTIME-DATA : To collect runtime data from local machine if any new attribute exist
                                        COLLECT-METRICS-TESTS: To collect codeploy metrics tests
                                        EO_STAGING_ECM_NS_TERMINATE : To clean NS Instantiate
                                        CNFNS-DELETE-SECRET-EVNFM : To clean CNF-NS secret on EVNFM
                                        ECDE-POST-INSTALL : To perform ECDE post installation tasks
                                        ECDE-AAT-SETUP : To setup the test tool in ECDE
                                        ECDE-SPIN : To cleanup the ecde spinnaker pipelines 
                                        TOSCA-PRETOSCA-WORKFLOW-DEPL : To Install Tosca or PreTosca Workflow
                                        EO-CM-CERT : To install EO-CM certificates in HA and NON HA env
                                        EO-PURGE : To delete and verify helm command and all resources belongs to the deployment 
                                        CREATE-FLAVOUR : To create flavour of different nodes
                                        IMAGE-REG : To register image of different node
                                        TEST-HOTEL-EPIS : TEST HOTEL ECM post install steps
                                        TEST-HOTEL-LPIS : TEST HOTEL LCM post install steps
                                        TEST-HOTEL-EVNFM-INTEGRATION : TEST HOTEL evnfm integration
                                        FETCH-VNF-MANGER-ID : To fetch VNF Manager Id
                                        TEST-HOTEL-SIT : To deploy Dummy Node
                                        EPG-MME-DISCOVERY : Discovery of EPG and MME into Single VDC
                                        UDS-VFC : To onboard and certify VFCs on UDS
                                        UDS-VF : To Create and Certify VF
                                        UDS-SERVICE : To Create and Certify Service
                                        UDS-EPG-DEPLOY : To deploy a EPG from SO using UDS templates
                                        TEST-HOTEL-VIM-ADD : To add vim in test hotel LCM
                                        EPG-SCALE :  To create EPG Scale
                                        EPG-TOSCA-SCALE-OUT : To create EPG Tosca Scale Out
                                        EPG-TOSCA-SCALE-IN : To create EPG Tosca Scale In
                                        EPG-HEAL :  To create EPG Heal
                                        UDS-POST-INST : TO take back up of UDS on before uds deployment
                                        UDS-CLEANUP : To clean the UDS as a Work around 
                                        L2-L3-DCGW : To Test DC-GW creation and VRF creation
                                        SOL-DUMMY-PRE-REQ : To get the environment ready to deploy SOL DUMMY
                                        SO-DEPLOY-SOL-DUMMY : To deploy SOL Dummy node from SO
                                        SO-DUMMY-SCALE : To Scale the SOL 005 Dummy Node
                                        REFRESH-POD-TOKEN-EO : To Refresh cinder pod token in EO
                                        EPG-ETSI-NSD-PRE : TO get the environment ready to deploy EPG ETSI TOSCA NSD on VNF LCM and VM VNFM
                                        EPG-ETSI-NSD-DEPLOY : To deploy EPG ETSI TOSCA NSD on VNF LCM and VM VNFM
                                        EPG-TOSCA-PRE : TO get the environment ready to deploy EPG TOSCA on VNF LCM and VM VNFM
                                        DUMMY-TOSCA-HEAL : To Heal the SOL 005 Dummy Node
                                        NAMESPACE-DEL : To delete the namespaces on director server (ccd1)
                                        DISABLE-LOG : To disbale to debug logs for vnflcm/vmvnfm
                                        ENABLE-LOG : To enable to debug logs for vnflcm/vmvnfm
                                        CCRC-SECRET : To Create CCRC Secret
                                        ECDE-CDD-DEPLOY : To deploy cdd node from ecde 
                                        ECDE-CDD-PREREQ : To create pre requisite for ecde cdd deploy
                                        EGAD-CERTS : To Distribute EGAD Certificate
                                        EO_STAGING_DISTRIBUTE_EGAD_CERTS_CN : To Distribute EGAD Certificate In CN
                                        CDD-KEYS : To update authorize keys for CCD
                                        SO-CNF-CONFIGMAP-PRE_REQ : To get the environment ready to deploy CNF CONFIG packages on SO 
                                        SO-CNF-CONFIGMAP-DEPL : to deploy CNF-CONFIG from SO
                                        EVNFM-CISMS-ZONE-REGISTER : To register CISM using EVNFM
                                        EVNFM-CISMS-ZONE-DEREGISTER : To deregister CISM using EVNFM
                                        TOSCA-EPG-HEAL : To perform Heal on Tosca EPG
                                        EPG-TOSCA-SO-DEPLOY : To deploy EPG TOSCA on SO
                                        UDS-RESTORE-DATABASE : Restore the UDS DATABASE
                                        MODIFY-TOSCA-EPG-PARAM: To Modify configurable attributes for TOSCA_EPG
                                        TEST-HOTEL-VM-VNFM-INTEGRATION: To register vm on vnfm for test hotel
                                        RPM-INSTALL: To install Generic Workflow
                                        SO-SUBSYSTEM-GET: Get SO Subsystem in an infinite loop
                                        UDS-VNF-PRE-REQ: To create pre requisite for uds vnf deployment
                                        UDS-NFV-PRE-REQ: To create pre requistie for uds nfv deployment
                                        UDS-DELETE-PRE-REQ: To delete pre requisite for uds
                                        WORKFLOW-INSTALL: To install workflows
                                        EAIND-SUPERUSER-CREATION: To create EAI ND super user
                                        VERIFY-PROJECT-EXISTS-CCM: To verify master project exists in cCM
                                        ENM-TOSCA-NODE-CLEANUP: To cleanup tosca node in ENM if unsynchronized
                                        ENM-ETSI-TOSCA-NODE-CLEANUP: To cleanup etsi tosca node in ENM if unsynchronized
                                        TEST-HOTEL-NETWORK-ADD: To create Test hotel Network
                                        EO_STAGING_ECM_CNF_NS_ADD: To Update NS to Add CNF
                                        EO_STAGING_ECM_CNF_NS_REMOVE: To Update NS to Remove CNF
                                        EO_STAGING_UDS_ST_CREATE_AND_DISTRIBUTE: UDS to create and distribute CTS base ST
                                        EO_STAGING_UDS_SO_TEPG_DEPLOYMENT: Deploy node using ST created and distributed by UDS
                                        EO_STAGING_ECM_CNF_NS_SCALE_OUT: scale out cnf ns vapp in EOCM
                                        EO_STAGING_ECM_CNF_NS_SCALE_IN: scale in cnf ns vapp in EOCM
                                        EO_STAGING_EPG_TOSCA_ECM_DEPLOY: deploy epg tosca from EOCM 
                                        EO_STAGING_MODIFY_CISMS_ZONE: Modify CISM zone cluster
                                        NODESELCTOR-VERIFICATION: To verify the nodeselectors
                                        ----------------------------------------------------------------------------------------
                                        ----------------------------------------------------------------------------------------
                                        do_init:
                                        ----------------------------------------------------------------------------------------
                                        This is json file path which would be used by this start_script as user_inputs to perform the respective operation.
                                        ----------------------------------------------------------------------------------------
                                        NOTE : **** All operations are not case-sensitive ****
                                        ----------------------------------------------------------------------------------------
                                           '''))

    parser.add_argument('operation', help='action that need be performed')
    parser.add_argument('dit_name', help='DIT document name that contains the user inputs')
    parser.add_argument('vnf_type',
                        help='optional argument only required in case of ECM-TERMINATE JOB,IMAGE-REG,CREATE-FLAVOUR',
                        nargs='?', const=None)
    parser.add_argument('user_input',
                        help='optional argument only required in case of productize version of automation (True)',
                        nargs='?', const=None)
    args = parser.parse_args()

    start_execution(args.operation.upper(), args.dit_name, parser, args.vnf_type, args.user_input)


if __name__ == '__main__':
    main()
