
from com_ericsson_do_auto_integration_utilities.Report_file import Report_file
from com_ericsson_do_auto_integration_utilities.Logger import Logger
from com_ericsson_do_auto_integration_scripts.UDS_GENERIC_OPERATIONS import UDS_GENERIC as uds_generic
from com_ericsson_do_auto_integration_utilities.UDS_files_update import *
from com_ericsson_do_auto_integration_utilities.Common_utilities import Common_utilities
import random

log = Logger.get_logger('UDS_VFC_OPERATIONS.py')

class UDS_VFC:


    def onboard_resource_vfc(self):

        global random_number

        random_number = random.randint(0,99)

        log.info('Generated random number is '+str(random_number))

        yaml_filename = 'resource-soResource-template.yml'

        update_vfc_yaml_file(yaml_filename,"com.ericsson.so.resource",random_number)

        yaml_file_path = r'com_ericsson_do_auto_integration_files/UDS_files/'+yaml_filename

        base64_code_yaml = Common_utilities.generate_base64_code_for_yamlfile(Common_utilities,yaml_file_path)

        json_filename = 'onboard_so_resource_vfc.json'

        update_vfc_json_file(json_filename,base64_code_yaml,random_number)

        json_filepath = r'com_ericsson_do_auto_integration_files/UDS_files/' +json_filename

        MD5_code = Common_utilities.generate_MD5_checksum_for_json(Common_utilities,json_filepath)

        self.resource_vfc_id = uds_generic.onboard_uds_vfcs(uds_generic,'RESOURCE',json_filename,'ONBOARD_RESOURCE_VFC_ID',MD5_code)


    def certify_resource_vfc(self):
        uds_generic.certify_uds_vfcs(uds_generic,'CERTIFY_RESOURCE',self.resource_vfc_id,'CERTIFY_RESOURCE_VFC_ID')


    def onboard_network_function_vfc(self):

        yaml_filename = 'resource-soNetworkfunction-template.yml'

        update_vfc_yaml_file(yaml_filename, "com.ericsson.so.NetworkFunction", random_number)

        yaml_file_path = r'com_ericsson_do_auto_integration_files/UDS_files/' + yaml_filename

        base64_code_yaml = Common_utilities.generate_base64_code_for_yamlfile(Common_utilities, yaml_file_path)

        json_filename = 'onboard_so_networkfunction_vfc.json'

        update_vfc_json_file(json_filename, base64_code_yaml, random_number)

        json_filepath = r'com_ericsson_do_auto_integration_files/UDS_files/' + json_filename

        MD5_code = Common_utilities.generate_MD5_checksum_for_json(Common_utilities, json_filepath)
        self.network_function_vfc_id = uds_generic.onboard_uds_vfcs(uds_generic, 'NETWORK_FUNCTION', json_filename,
                                                            'ONBOARD_NETWORK_FUNCTION_VFC_ID',MD5_code)


    def certify_network_function_vfc(self):
        uds_generic.certify_uds_vfcs(uds_generic,'CERTIFY_NETWORK_FUNCTION',self.network_function_vfc_id,'CERTIFY_NETWORK_FUNCTION_VFC_ID')


    def onboard_network_service_vfc(self):

        yaml_filename = 'resource-soNetworkservice-template.yml'

        update_vfc_yaml_file(yaml_filename, "com.ericsson.so.NetworkService", random_number)

        yaml_file_path = r'com_ericsson_do_auto_integration_files/UDS_files/' + yaml_filename

        base64_code_yaml = Common_utilities.generate_base64_code_for_yamlfile(Common_utilities, yaml_file_path)

        json_filename = 'onboard_so_networkservice_vfc.json'

        update_vfc_json_file(json_filename, base64_code_yaml, random_number)

        json_filepath = r'com_ericsson_do_auto_integration_files/UDS_files/' + json_filename

        MD5_code = Common_utilities.generate_MD5_checksum_for_json(Common_utilities, json_filepath)


        self.network_service_vfc_id = uds_generic.onboard_uds_vfcs(uds_generic,'NETWORK_SERVICE',json_filename,'ONBOARD_NETWORK_SERVICE_VFC_ID',MD5_code)


    def certify_network_service_vfc(self):
        uds_generic.certify_uds_vfcs(uds_generic,'CERTIFY_NETWORK_SERVICE',self.network_service_vfc_id,'CERTIFY_NETWORK_SERVICE_VFC_ID')


    def onboard_epg_vfc(self):

        yaml_filename = 'resource-soEPG-template.yml'

        update_vfc_yaml_file(yaml_filename, "com.ericsson.so.NetworkFunction.EPG", random_number)

        yaml_file_path = r'com_ericsson_do_auto_integration_files/UDS_files/' + yaml_filename

        base64_code_yaml = Common_utilities.generate_base64_code_for_yamlfile(Common_utilities, yaml_file_path)

        json_filename = 'onboard_so_epg_vfc.json'

        update_vfc_json_file(json_filename, base64_code_yaml, random_number)

        json_filepath = r'com_ericsson_do_auto_integration_files/UDS_files/' + json_filename

        MD5_code = Common_utilities.generate_MD5_checksum_for_json(Common_utilities, json_filepath)


        self.epg_vfc_id = uds_generic.onboard_uds_vfcs(uds_generic,'EPG',json_filename,'ONBOARD_EPG_VFC_ID',MD5_code)


    def certify_epg_vfc(self):
        uds_generic.certify_uds_vfcs(uds_generic,'CERTIFY_EPG',self.epg_vfc_id,'CERTIFY_EPG_VFC_ID')