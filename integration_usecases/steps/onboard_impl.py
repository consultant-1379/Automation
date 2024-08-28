# Created by eiaavij at 10/9/2018

from behave import *

from com_ericsson_do_auto_integration_model.SIT import SIT
from com_ericsson_do_auto_integration_utilities.ServerConnection import ServerConnection
from com_ericsson_do_auto_integration_utilities.Logger import Logger
from com_ericsson_do_auto_integration_initilization.ECM_PI_initialization import ECM_PI_Initialization
from com_ericsson_do_auto_integration_utilities.Report_file import Report_file
from com_ericsson_do_auto_integration_utilities.Common_utilities import Common_utilities
from com_ericsson_do_auto_integration_initilization.Initialization_script import Initialization_script
from com_ericsson_do_auto_integration_utilities.SIT_files_update import *
from com_ericsson_do_auto_integration_initilization.SIT_initialization import SIT_initialization
from com_ericsson_do_auto_integration_model.Ecm_core import Ecm_core
import ast
import base64

log = Logger.get_logger('onboard_impl.py')
ecm_core_data = \
    Initialization_script.get_model_objects(Initialization_script,
        'ECM_CORE')
sit_data = SIT_initialization.get_model_objects(SIT_initialization,
        'SIT')
EPIS_data = ECM_PI_Initialization.get_model_objects(ECM_PI_Initialization, 'EPIS')

@given('I have an IP address')
def step_impl(context):

    context.ip = ecm_core_data._Ecm_core__ECM_Host_Blade_IP


@step('I have userID and password')
def step_impl(context):

    context.userID = ecm_core_data._Ecm_core__ECM_Host_Blade_username
    context.password = ecm_core_data._Ecm_core__ECM_Host_Blade_Password


@then('I login to server')
def step_impl(context):

    server_connection = \
        ServerConnection.get_connection(context.ip,
                                        context.userID, context.password)
    context.connection = server_connection


@step('close the connection')
def step_impl(context):

    context.connection.close()


@given('I have user inputs')
def step_impl(context):

    log.info('All inputs required for files has been fectched at the time of initialization '
             )


@step('I fetch the file from local directory')
def step_impl(context):

    context.on_board = \
        r'com_ericsson_do_auto_integration_files/on_board.json'
    context.vnflaf_cee = \
        r'com_ericsson_do_auto_integration_files/vnflaf/vnflaf_cee.yaml'
    context.deploy_file = \
        r'com_ericsson_do_auto_integration_files/deploy.json'
    context.terminate_file = \
        r'com_ericsson_do_auto_integration_files/terminate.json'
    context.vnflaf_cee_env = \
        r'com_ericsson_do_auto_integration_files/vnflaf/Resources/EnvironmentFiles/vnflaf_cee-env.yaml'
    context.vnflaf_services = \
        r'com_ericsson_do_auto_integration_files/vnflaf/Resources/HotFiles/vnflaf-services.yaml'
    context.VNFD_wrapper = \
        r'com_ericsson_do_auto_integration_files/vnflaf/Resources/VnfdWrapperFiles/VNFD_Wrapper_VNFLAF.json'
    context.vnflaf_cee_ecm = r'com_ericsson_do_auto_integration_files/vnflaf_cee.yaml'


@step('I update the flavour in files')
def step_impl(context):

    flavour_name = sit_data._SIT__services_flavor
    update_flavour(context.vnflaf_cee_ecm,flavour_name)
    update_flavour(context.vnflaf_cee,flavour_name)
    update_flavour(context.vnflaf_services, flavour_name)


@step('I update the json file {file_name}')
def step_impl(context, file_name):

    if 'onboard' in file_name:
        package_name = Common_utilities.get_name_with_timestamp(Common_utilities, 'Test_VNF_Package_Upload')
        update_dummy_onboard_file(package_name)
    elif 'VNFD_Wrapper_VNFLAF' in file_name:
        update_VNFD_wrapper()
    elif 'vnflaf_cee-env' in file_name:
        update_vnflaf_yaml()
    elif 'deploy' in file_name:
        update_deploy_file()
    elif 'terminate' in file_name:
        update_terminate_file()


@given('I have a connection with server')
def step_impl(context):

    log.info('connected with server' + context.ip)


@then('I put "{file}" on server')
def step_impl(context, file):

    if 'onboard' in file:
        file_path = context.on_board
        destination = f'{SIT.get_base_folder(SIT)}on_board.json'
    elif 'vnflaf_cee' in file:
        file_path = context.vnflaf_cee
        destination = f'{SIT.get_base_folder(SIT)}vnflaf_cee.yaml'
    elif 'deploy' in file:
        file_path = context.deploy_file
        destination = f'{SIT.get_base_folder(SIT)}deploy.json'
    elif 'terminate' in file:
        file_path = context.terminate_file
        destination = f'{SIT.get_base_folder(SIT)}terminate.json'

    log.info('Open a sftp connection for file ' + file_path)
    sftp = context.connection.open_sftp()
    sftp.put(file_path, destination)
    sftp.close()
    log.info('close sftp connection for file ' + file_path)


@step('I fetch the core_vm_ip')
def step_impl(context):

    context.core_vm_ip = ecm_core_data._Ecm_core__CORE_VM_IP


@step('I create the curl command for auth token')
def step_impl(context):

    # Generate a token in the host blade server using the following curl command
    context.ecm_gui_username = ecm_core_data._Ecm_core__ecm_gui_username
    context.ecm_gui_password = ecm_core_data._Ecm_core__ecm_gui_password     
    context.tenant_id = EPIS_data._EPIS__tenant_name
    context.core_vm_hostname = Ecm_core.get_core_vm_hostname(Ecm_core)
    context.is_cloudnative = Ecm_core.get_is_cloudnative(Ecm_core)
    auth_basic = base64.b64encode(bytes(context.ecm_gui_username+':'+context.ecm_gui_password, encoding='utf-8'))        
    context.decoded_auth_basic = auth_basic.decode('utf-8')
    log.info(context.decoded_auth_basic)        
    log.info('Generating AuthToken')
    if not context.is_cloudnative:
        curl = '''curl -X POST --header 'Authorization:Basic {}' --header 'TenantId:{}'  --insecure  https://{}:443/ecm_service/tokens'''.format(context.decoded_auth_basic,context.tenant_id,context.core_vm_ip)
        Report_file.add_line('curl command of auth token ' + curl)
        context.command = curl
    else:
        curl = '''curl -X POST --header 'Authorization:Basic {}' --header 'TenantId:{}'  --insecure  https://{}:443/ecm_service/tokens'''.format(context.decoded_auth_basic, context.tenant_id, context.core_vm_hostname)
        Report_file.add_line('curl command of auth token ' + curl)
        context.command = curl

@step('I execute the curl command')
def step_impl(context):

    (stdin, stdout, stderr) = \
        context.connection.exec_command(context.command)
    command_output = str(stdout.read())
    context.output = command_output
    Report_file.add_line('output of command  ' + context.output)


@step('save the Auth token')
def step_impl(context):

    Report_file.add_mesg('Step 1',
                         'OnBoarding Token Generation   ',
                         context.output)
    output = ast.literal_eval(context.output[2:-1:1])
    requestStatus = output['status']['reqStatus']

    if 'SUCCESS' in requestStatus:

        token_string = ast.literal_eval(context.output[2:-1:1])
        context.token = token_string['status']['credentials']

        log.info('OnBoarding Token Generated:  ' + context.token)

        Report_file.add_mesg('Step 2',
                             'OnBoarding Token Generated ',
                             context.token)
    elif 'ERROR' in requestStatus:

        command_error = output['status']['msgs'][0]['msgText']

        log.error(command_error)
        Report_file.add_line(command_error)
        Report_file.add_line('Error executing curl command for OnBoarding'
                             )
        context.connection.close()
        assert False

    # TODO save in model class

    sit_data.set_auth_token(sit_data, context.token)
    sit_data._SIT__auth_token = context.token
    Report_file.add_mesg('Step 2',
                         'OnBoarding Token Generated ', context.token)


@step('I fetch the Auth token')
def step_impl(context):

    context.auth_token = sit_data._SIT__auth_token
    log.info('Auth token fetched ' + context.auth_token)


@then('I create the curl command for generating the package id')
def step_impl(context):

    # Generating package id with curl command
    context.core_vm_hostname = Ecm_core.get_core_vm_hostname(Ecm_core)
    context.is_cloudnative = Ecm_core.get_is_cloudnative(Ecm_core)
    log.info('curl command of generating package id ')
    if not context.is_cloudnative:
        curl = \
            '''curl -X POST --insecure --header 'Content-Type: application/json' --header 'Accept: application/json' --header 'AuthToken:{}' --data @on_board.json 'https://{}/ecm_service/vnf_packages{}'''.format(context.auth_token,
                context.core_vm_ip, "'")
    else:
        curl = \
            '''curl -X POST --insecure --header 'Content-Type: application/json' --header 'Accept: application/json' --header 'AuthToken:{}' --data @on_board.json 'https://{}/ecm_service/vnf_packages{}'''.format(
                context.auth_token,
                context.core_vm_hostname, "'")
    context.command = curl
    Report_file.add_line('Curl command for generating package id '
                         + curl)


@step('I save the vnfPackage id')
def step_impl(context):

    Report_file.add_mesg('Step 3',
                         'Generating Package Id for OnBoarding ',
                         context.output)
    log.info('Generating vnfPackage Id for OnBoarding')
    output = ast.literal_eval(context.output[2:-1:1])
    requestStatus = output['status']['reqStatus']

    if 'SUCCESS' in requestStatus:
        context.vnfPackage_id = output['data']['vnfPackage']['id']
        log.info('vnfPackage id is : ' + context.vnfPackage_id)
        Report_file.add_line('vnfPackage id is : '
                             + context.vnfPackage_id)
        log.info('package created successfully')
        log.info(context.vnfPackage_id)
        Report_file.add_line('Executed the curl command for creation of package : '
                             + context.vnfPackage_id)
        Report_file.add_line('Created package successfully'
                             )
    elif 'ERROR' in requestStatus:

        command_error = output['status']['msgs'][0]['msgText']

        log.error('Error executing curl command for creating the package '
                   + command_error)
        Report_file.add_line(command_error)
        Report_file.add_line('Error executing curl command for creating the package'
                             )
        context.connection.close()
        assert False

    sit_data.set_vnf_packageId(sit_data, context.vnfPackage_id)
    sit_data._SIT__vnf_packageId = context.vnfPackage_id


@step('fetch the values for content range, filechecksum and chunk size')
def step_impl(context):

    file_name = \
        r'com_ericsson_do_auto_integration_files/vnflaf/vnflaf_cee.yaml'
    context.file_checksum = Common_utilities.crc(Common_utilities,
            file_name)


    # chunk_size = '(wc -c < vnflaf_cee.yaml)' #TODO it will one numric no. as output like 25122
    # content_range = '25121/25122' #TODO this value depends on chunk_size and -1 chunk size.
    # chunk_data = '#TODO base64 (file_name)'

@step('I fetch the vnf package id')
def step_impl(context):

    context.vnfPackage_id = sit_data._SIT__vnf_packageId


@then('I create the curl command for uploading the package')
def step_impl(context):

    # Uploading a Package
    context.core_vm_hostname = Ecm_core.get_core_vm_hostname(Ecm_core)
    context.is_cloudnative = Ecm_core.get_is_cloudnative(Ecm_core)
    log.info('Creating the curl command of uploading the package')

    data = \
        '"{\\"chunkSize\\":\\"$(wc -c < vnflaf_cee.yaml)\\",\\"fileChecksum\\":\\"' \
        + context.file_checksum \
        + '\\",\\"chunkData\\":\\"$(base64 vnflaf_cee.yaml)\\"}"'

    command = 'echo ' + data + ' > file_input.base64.req.body'
    log.info('command to create file_input.base64.req.body file '
             + command)
    context.connection.exec_command(command)
    if not context.is_cloudnative:
        curl = \
            '''curl --insecure -X PUT "https://{}:443/ecm_service/vnf_packages/{}/content" --header "AuthToken:{}" --header "Content-Range: bytes 0-$(expr $(wc -c < vnflaf_cee.yaml) - 1)/$(wc -c < vnflaf_cee.yaml)" --header "tenantId:ECM" --header "Content-Type: application/json" --data @file_input.base64.req.body'''.format(context.core_vm_ip,
                context.vnfPackage_id, context.auth_token)
    else:
        curl = \
            '''curl --insecure -X PUT "https://{}:443/ecm_service/vnf_packages/{}/content" --header "AuthToken:{}" --header "Content-Range: bytes 0-$(expr $(wc -c < vnflaf_cee.yaml) - 1)/$(wc -c < vnflaf_cee.yaml)" --header "tenantId:ECM" --header "Content-Type: application/json" --data @file_input.base64.req.body'''.format(
                context.core_vm_hostname,
                context.vnfPackage_id, context.auth_token)
    context.command = curl
    Report_file.add_line('Curl command for uploading the package '
                         + context.command)


@step('I Verify the curl command')
def step_impl(context):

    Report_file.add_mesg('Step 4',
                         'Uploading Package for OnBoarding ',
                         context.output)
    log.info('Uploading Package for OnBoarding')
    output = ast.literal_eval(context.output[2:-1:1])
    requestStatus = output['status']['reqStatus']

    if 'SUCCESS' in requestStatus:

        log.info('package uploaded successfully. Verifying the status of provisioning and operationalState.'
                 )
        log.info(context.vnfPackage_id)
        Report_file.add_line('Executed the curl command for uploading the package : '
                             + context.vnfPackage_id)
        Report_file.add_line('Uploaded package successfully. Verifying the status of provisioning and operationalState.'
                             )
    elif 'ERROR' in requestStatus:

        command_error = output['status']['msgs'][0]['msgText']

        log.error('Error executing curl command for uploading the package '
                   + command_error)
        Report_file.add_line(command_error)
        Report_file.add_line('Error executing curl command for uploading the package'
                             )
        context.connection.close()
        assert False


@then('I create the curl command for verifying uploading the package')
def step_impl(context):

    # Verifying Upload of a Package
    context.core_vm_hostname = Ecm_core.get_core_vm_hostname(Ecm_core)
    context.is_cloudnative = Ecm_core.get_is_cloudnative(Ecm_core)
    log.info('curl command of verification of uploading the package')
    if not context.is_cloudnative:
        curl = \
            '''curl -X GET --insecure --header 'Accept: application/json' --header 'AuthToken: {}' 'https://{}/ecm_service/vnfpackages/{}'''.format(context.auth_token,
                context.core_vm_ip, context.vnfPackage_id + "'")
    else:
        curl = \
            '''curl -X GET --insecure --header 'Accept: application/json' --header 'AuthToken: {}' 'https://{}/ecm_service/vnfpackages/{}'''.format(
                context.auth_token,
                context.core_vm_hostname, context.vnfPackage_id + "'")
    context.command = curl
    Report_file.add_line('Curl command for verifying uploading the package '
                         + curl)


@then('I verify the onboard usecase')
def step_impl(context):

    Report_file.add_mesg('Step 5',
                         'Verification of OnBoarding Use Case ',
                         context.output)
    log.info('Verification of OnBoarding Use Case')
    command_out = context.output[2:-1:1]
    try:

        command_out = command_out.replace('true', 'True')
        command_out = command_out.replace('false', 'False')
    except:

        log.error('ERROR while updating the command_output')

    output = ast.literal_eval(command_out)
    requestStatus = output['status']['reqStatus']

    if 'SUCCESS' in requestStatus:

        provisioningStatus = output['data']['vnfPackage'
                ]['provisioningStatus']
        operationalState = output['data']['vnfPackage'
                ]['operationalState']

        if 'ACTIVE' in provisioningStatus and 'ENABLED' \
            in operationalState:
            log.info('provisioningStatus is : ' + provisioningStatus)
            log.info('operationalState is : ' + operationalState)
            Report_file.add_line('provisioningStatus is : '
                                 + provisioningStatus)
            Report_file.add_line('operationalState is : '
                                 + operationalState)
            log.info('Verification of package uploaded is success')
            Report_file.add_line('Verification of package Upload is success'
                                 )
        else:

            log.error('Verification of package uploaded failed. Please check the status of provisioning and operationalState  '
                      )
            log.error('provisioningStatus : ' + provisioningStatus
                      + ' operationalState : ' + operationalState)
            Report_file.add_line('Verification of package uploaded failed. Please check the status of provisioning and operationalState'
                                 )
            context.connection.close()
            assert False
    elif 'ERROR' in requestStatus:

        command_error = output['status']['msgs'][0]['msgText']

        log.error('Error executing curl command for verification of OnBoard package '
                   + command_error)
        Report_file.add_line(command_error)
        Report_file.add_line('Error executing curl command for verification of OnBoard package'
                             )
        context.connection.close()
        assert False


			