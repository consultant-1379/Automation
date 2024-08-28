# Created by eshetra at 10/19/2018

from behave import *
from com_ericsson_do_auto_integration_utilities.ServerConnection import ServerConnection
from com_ericsson_do_auto_integration_utilities.Logger import Logger
from com_ericsson_do_auto_integration_initilization.ECM_PI_initialization import ECM_PI_Initialization
from com_ericsson_do_auto_integration_utilities.Report_file import Report_file
from com_ericsson_do_auto_integration_utilities.Common_utilities import Common_utilities
import ast

log = Logger.get_logger('delete_impl.py')



@step("I create the curl command for delete vApp")
def step_impl(context):

    log.info('Curl command for deleting the vApp')
    curl = '''curl -X DELETE --insecure --insecure --header 'Content-Type: application/json' --header 'Accept: application/json' --header 'AuthToken:{}' --data @terminate.json 'https://{}/ecm_service/v2/vapps/{}/terminate{}'''.format(context.auth_token, context.core_vm_ip, context.vApp_id,"'")
    context.command = curl



@then("I verify the curl command response for deletion")
def step_impl(context):
    Report_file.add_mesg('Step 8', 'Deleting vApp ', context.output)
    log.info('Deleting vApp ' +context.vApp_id)
    Report_file.add_line('Deleting vApp : ' + context.vApp_id)
    command_out = context.output[2:-1:1]
    try:
        command_out = command_out.replace('true', 'True')
        command_out = command_out.replace('false', 'False')
    except:

        log.error('ERROR while updating the command_output')

    output = ast.literal_eval(command_out)

    requestStatus = output['status']['reqStatus']

    if 'SUCCESS' in requestStatus:

        correlation_id = output['correlationId']
        order_status, order_output = Common_utilities.orderReqStatus(Common_utilities, context.connection, context.auth_token, context.core_vm_ip,correlation_id, 30)
        
        if order_status:
          log.info('vApp deleted successfully. Verifying the Ping Response of external_ip_for_services_vm ' +context.vApp_id)
          Report_file.add_line('vApp deleted successfully. Verifying the Ping Response of external_ip_for_services_vm ' + context.vApp_id)

        else:
          Report_file.add_line(order_output)
          log.error('order status for  node termination is errored  '+correlation_id)
          Report_file.add_line('order status for  node termination is errored  ' + correlation_id)
          assert False 

    elif 'ERROR' in requestStatus:

        command_error = output['status']['msgs'][0]['msgText']

        log.error('Error executing curl command for Deleting the package ' + command_error)
        Report_file.add_line(command_error)
        Report_file.add_line('Error executing curl command for deleting the package')
        context.connection.close()
        assert False



@then("I verify the vApp Deletion")
def step_impl(context):

   if False == context.ping_response:
       log.info('vApp deleted successfully. ' + context.cmd_output)
       Report_file.add_line('vApp deleted successfully. ' + context.cmd_output)

   else:
       log.info('vApp deletion failed. ' + context.cmd_output)
       Report_file.add_line('vApp deletion failed. ' + context.cmd_output)
       assert False


