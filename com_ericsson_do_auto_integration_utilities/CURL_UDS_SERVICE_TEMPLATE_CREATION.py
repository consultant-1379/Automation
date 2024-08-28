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

from com_ericsson_do_auto_integration_utilities.Logger import Logger

log = Logger.get_logger('CURL_UDS_VNF_SERVICE.py')

class CurlUdsSTCreation(object):

    @staticmethod
    def create_uds_service(uds_hostname, uds_token, file_name, MD5_code):
        """
        Curl command for creating the uds service
        """
        curl = (f"curl --insecure -X POST -H 'Accept: */*' -H 'Content-MD5:{MD5_code}' -H 'Content-Type: "
                f"application/json' -H 'Cookie: JSESSIONID={uds_token}; HTTP_IV_USER=cs0008; USER_ID=cs0008;"
                f" HTTP_CSP_FIRSTNAME=Carlos; HTTP_CSP_EMAIL=csantana@sdc.com; HTTP_CSP_LASTNAME=Santana; "
                f"HTTP_IV_REMOTE_ADDRESS=0.0.0.0; HTTP_CSP_WSTYPE=Intranet; EPService=portal' "
                f"https://{uds_hostname}/sdc1/feProxy/rest/v1/catalog/services -d @{file_name}")
        return curl


    @staticmethod
    def add_vfc_to_the_service(uds_hostname, uds_token, file_name, uds_service_unique_id):
        """
        Curl command for adding vfc to the service
        """
        curl = (f"curl --insecure -X POST -H 'Accept: */*' -H 'Content-Type: application/json' "
                f"-H 'Cookie: JSESSIONID={uds_token}; HTTP_IV_USER=cs0008; USER_ID=cs0008; "
                f"HTTP_CSP_FIRSTNAME=Carlos; HTTP_CSP_EMAIL=csantana@sdc.com; HTTP_CSP_LASTNAME=Santana; "
                f"HTTP_IV_REMOTE_ADDRESS=0.0.0.0; HTTP_CSP_WSTYPE=Intranet; EPService=portal' "
                f"https://{uds_hostname}/sdc1/feProxy/rest/v1/catalog/services/{uds_service_unique_id}/"
                f"resourceInstance -d @{file_name}")
        return curl

    @staticmethod
    def declare_vfc_inputs(uds_hostname, uds_token, file_name, uds_service_unique_id):
        """
        Curl command to declare vfc inputs
        """
        curl = (f"curl --insecure -X POST -H 'Accept: */*' -H 'Content-Type: application/json' "
                f"-H 'Cookie: JSESSIONID={uds_token}; HTTP_IV_USER=cs0008; USER_ID=cs0008; "
                f"HTTP_CSP_FIRSTNAME=Carlos; HTTP_CSP_EMAIL=csantana@sdc.com; "
                f"HTTP_CSP_LASTNAME=Santana; HTTP_IV_REMOTE_ADDRESS=0.0.0.0; "
                f"HTTP_CSP_WSTYPE=Intranet; EPService=portal;' https://{uds_hostname}/sdc1/feProxy/"
                f"rest/v1/catalog/services/{uds_service_unique_id}/create/inputs -d @{file_name}")
        return curl

    @staticmethod
    def get_vfc_data(uds_hostname, uds_token):
        """
        Curl command to get vfc data
        """
        curl = (f"curl --insecure 'https://{uds_hostname}/sdc1/feProxy/"
                f"uicache/v1/catalog/resources/latestversion/notabstract/metadata?internalComponentType="
                f"SERVICE&componentModel=EO-CTM&includeNormativeExtensionModels=true'  -H 'Accept: */*' "
                f"-H 'Content-Type: application/json' -H 'Cookie: JSESSIONID={uds_token}; USER_ID=cs0008'")
        return curl

    @staticmethod
    def add_values_to_the_vfc_inputs(uds_hostname, uds_token, file_name, uds_unique_service_id):
        """
        Curl command to add value to the VFC inputs
        """
        curl = (f"curl --insecure -X POST -H 'Accept: */*' -H 'Content-Type: application/json' "
                f"-H 'Cookie: JSESSIONID={uds_token}; HTTP_IV_USER=cs0008; USER_ID=cs0008; "
                f"HTTP_IV_REMOTE_ADDRESS=0.0.0.0;' https://{uds_hostname}/sdc1/feProxy/rest/v1/catalog/"
                f"services/{uds_unique_service_id}/update/inputs -d @{file_name}")
        return curl

    @staticmethod
    def add_values_to_the_properties(uds_hostname, uds_token, file_name, uds_unique_service_id, vfc_inputid_dict):
        """
        Curl command to add values to the VFC properties
        """
        curl = (f"curl --insecure -X POST -H 'Accept: */*' -H 'Content-Type: application/json' "
                f"-H 'Cookie: JSESSIONID={uds_token}; HTTP_IV_USER=cs0008; USER_ID=cs0008; "
                f"HTTP_IV_REMOTE_ADDRESS=0.0.0.0;' https://{uds_hostname}/sdc1/feProxy/rest/v1/catalog/"
                f"services/{uds_unique_service_id}/resourceInstance/{vfc_inputid_dict['ownerId']}/"
                f"properties -d @{file_name}")
        return curl

    @staticmethod
    def add_inputs_to_the_vfc(uds_hostname, uds_token, file_name, uds_unique_service_id):
        """
        Curl command to add inputs to the VFC
        """
        curl = (f"curl --insecure -X POST -H 'Accept: */*' -H 'Content-Type: application/json' "
                f"-H 'Cookie: JSESSIONID={uds_token}; HTTP_IV_USER=cs0008; USER_ID=cs0008; "
                f"HTTP_IV_REMOTE_ADDRESS=0.0.0.0;' https://{uds_hostname}/sdc1/feProxy/rest/v1/catalog/"
                f"services/{uds_unique_service_id}/create/input -d @{file_name}")
        return curl

    @staticmethod
    def add_tosca_function_to_the_vfc(uds_hostname, uds_token, file_name,
                                      uds_unique_service_id, add_vfc_dict):
        """
        Curl command to add tosca function to the VFC
        """
        curl = (f"curl --insecure -X POST -H 'Accept: */*' -H 'Content-Type: application/json' "
                f"-H 'Cookie: JSESSIONID={uds_token}; HTTP_IV_USER=cs0008; USER_ID=cs0008; "
                f"HTTP_IV_REMOTE_ADDRESS=0.0.0.0;' https://{uds_hostname}/sdc1/feProxy/rest/v1/"
                f"catalog/services/{uds_unique_service_id}/resourceInstance/"
                f"{add_vfc_dict['ownerId']}/properties -d @{file_name}")
        return curl

    @staticmethod
    def add_directives_to_the_vfc(uds_hostname, uds_token, file_name, uds_unique_service_id, add_vfc_data):
        """
        Curl command to add directives to the VFC
        """
        curl = (f"curl --insecure -X POST -H 'Accept: */*' -H 'Content-Type: application/json' "
                f"-H 'Cookie: JSESSIONID={uds_token}; HTTP_IV_USER=cs0008; USER_ID=cs0008; "
                f"HTTP_IV_REMOTE_ADDRESS=0.0.0.0;' https://{uds_hostname}/sdc1/feProxy/rest/v1/"
                f"catalog/services/{uds_unique_service_id}/resourceInstance/"
                f"{add_vfc_data['ownerId']} -d @{file_name}")
        return curl

    @staticmethod
    def add_vfc_node_filter_properties(uds_hostname, uds_token, file_name,
                                       uds_unique_service_id, add_vfc_data):
        """
        Curl command to add VFC node filter properties
        """
        curl = (f"curl --insecure -X POST -H 'Accept: */*' -H 'Content-Type: application/json' "
                f"-H 'Cookie: JSESSIONID={uds_token}; HTTP_IV_USER=cs0008; USER_ID=cs0008; "
                f"HTTP_IV_REMOTE_ADDRESS=0.0.0.0;' https://{uds_hostname}/sdc1/feProxy/rest/v1/"
                f"catalog/services/{uds_unique_service_id}/componentInstance/{add_vfc_data['ownerId']}"
                f"/properties/nodeFilter -d @{file_name}")
        return curl

    @staticmethod
    def associate_two_vfcs(uds_hostname, uds_token, file_name, uds_unique_service_id):
        """
        Curl command to associate two VFCs
        """
        curl = (f"curl --insecure -X POST -H 'Accept: */*' -H 'Content-Type: application/json' "
                f"-H 'Cookie: JSESSIONID={uds_token}; HTTP_IV_USER=cs0008; USER_ID=cs0008; "
                f"HTTP_IV_REMOTE_ADDRESS=0.0.0.0;' https://{uds_hostname}/sdc1/feProxy/"
                f"rest/v1/catalog/services/{uds_unique_service_id}/"
                f"resourceInstance/associate -d @{file_name}")
        return curl

    @staticmethod
    def checkout_vfc(uds_hostname, uds_token, fetch_vfc_data):
        """
        Curl command to checkout VFC
        """
        curl = (f"curl --insecure -X POST -H 'Accept: */*' -H 'Content-Type: application/json' "
                f"-H 'Cookie: JSESSIONID={uds_token}; HTTP_IV_USER=cs0008; USER_ID=cs0008; "
                f"HTTP_IV_REMOTE_ADDRESS=0.0.0.0;' https://{uds_hostname}/sdc1/feProxy/rest/v1/"
                f"catalog/resources/{fetch_vfc_data['uniqueId']}/lifecycleState/CHECKOUT")
        return curl

    @staticmethod
    def add_properties_to_vfc(uds_hostname, uds_token, payload_json, vfc_unique_id):
        """
        Curl command to add properties to the VFC
        """
        curl = (f"curl --insecure -X POST -H 'Accept: */*' -H 'Content-Type: application/json' "
                f"-H 'Cookie: JSESSIONID={uds_token}; HTTP_IV_USER=cs0008; USER_ID=cs0008; "
                f"HTTP_IV_REMOTE_ADDRESS=0.0.0.0;' https://{uds_hostname}/sdc1/feProxy/rest/"
                f"v1/catalog/resources/{vfc_unique_id}/properties -d '{payload_json}'")
        return curl

    @staticmethod
    def cetify_vfc(uds_hostname, uds_token, payload_json, vfc_id):
        """
        Curl command to certify the VFC
        """
        curl = (f"curl --insecure -X POST -H 'Accept: */*' -H 'Content-Type: application/json' "
                f"-H 'Cookie: JSESSIONID={uds_token}; HTTP_IV_USER=cs0008; USER_ID=cs0008; "
                f"HTTP_IV_REMOTE_ADDRESS=0.0.0.0;' https://{uds_hostname}/sdc1/feProxy/rest/"
                f"v1/catalog/resources/{vfc_id}/lifecycleState/certify "
                f" -d '{payload_json}'")
        return curl

    @staticmethod
    def certify_service(uds_hostname, uds_token, payload_json, service_id):
        """
        Curl command to certify the Service
        """
        curl = (f"curl --insecure -X POST -H 'Accept: */*' -H 'Content-Type: application/json' "
                f"-H 'Cookie: JSESSIONID={uds_token}; HTTP_IV_USER=cs0008; USER_ID=cs0008; "
                f"HTTP_IV_REMOTE_ADDRESS=0.0.0.0;' https://{uds_hostname}/sdc1/feProxy/rest/v1/"
                f"catalog/services/{service_id}/lifecycleState/certify -d '{payload_json}'")
        return curl

    @staticmethod
    def distribute_the_service_to_so(uds_hostname, uds_token, certified_service_unique_id):
        """
        Curl command to distribute the UDS service to SO
        """
        curl = (f"curl --insecure  -X POST -H 'Accept: */*' -H 'Content-Type: application/json'"
                f" -H 'Content-Length: 0' -H 'Cookie: JSESSIONID={uds_token};HTTP_IV_USER=cs0008; "
                f"USER_ID=cs0008; HTTP_CSP_FIRSTNAME=Carlos; HTTP_CSP_EMAIL=csantana@sdc.com; "
                f"HTTP_CSP_LASTNAME=Santana; HTTP_IV_REMOTE_ADDRESS=0.0.0.0; HTTP_CSP_WSTYPE=Intranet; "
                f"EPService=portal' https://{uds_hostname}/sdc1/feProxy/rest/v1/catalog/services/"
                f"{certified_service_unique_id}/distribution/PROD/activate")
        return curl

    @staticmethod
    def get_so_service_template_id(so_host_name, so_token, st_name):
        """
        Curl command to fetch SO service template id
        """
        curl = (f"curl --insecure 'https://{so_host_name}/catalog-manager/artifact/catalog-manager/"
                f"v2/catalogs?latest=true&listInternalArtifacts=false&offset=0&limit=50&sortAttr"
                f"=name&sortDir=asc&filters=%7B%22name%22:%22{st_name}%22,%22"
                f"type%22:%5B%22SERVICE_TEMPLATE%22%5D%7D' -H 'cookie: amlbcookie=01; tenantName=master;"
                f" userName=so-user; JSESSIONID={so_token}'")
        return curl

    @staticmethod
    def onboard_config_template(uds_hostname, uds_token, file_name, vf_unique_id, MD5_code):
        """
        Curl command to upload the config templates to UDS
        """
        curl = (f"curl -i --insecure -X POST -H 'Accept: */*' -H 'Content-Type: application/json' -H "
                f"'Content-MD5:{MD5_code}'  -H 'Cookie: JSESSIONID={uds_token}; HTTP_IV_USER=cs0008; "
                f"USER_ID=cs0008;HTTP_CSP_FIRSTNAME=Carlos;HTTP_CSP_EMAIL=csantana@sdc.com;"
                f"HTTP_CSP_LASTNAME=Santana;HTTP_IV_REMOTE_ADDRESS=0.0.0.0;HTTP_CSP_WSTYPE=Intranet;"
                f"EPService=portal' https://{uds_hostname}/sdc1/feProxy/rest/v1/catalog/services"
                f"/{vf_unique_id}/artifacts -d @{file_name}")
        return curl
