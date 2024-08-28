'''
Created on 15 July 2021

@author: eiaavij
'''

from com_ericsson_do_auto_integration_utilities.Report_file import Report_file
from com_ericsson_do_auto_integration_utilities.Logger import Logger
from com_ericsson_do_auto_integration_scripts.ECM_NODE_DEPLOYMENT import *
from com_ericsson_do_auto_integration_scripts.VERIFY_NODE_DEPLOYMENT import verify_result_in_vnflaf_db
from com_ericsson_do_auto_integration_initilization.SIT_initialization import SIT_initialization
from com_ericsson_do_auto_integration_scripts.VERIFY_NODE_DEPLOYMENT import verify_result_in_vnflaf_db

log = Logger.get_logger('MODIFY_TOSCA_PARAMS.py')


def get_tosca_vnf_vapp_id(vapp_name):
    """Returning the tosca vapp and vnf ids."""
    global tosca_vapp_id
    global tosca_vnf_id
    tosca_vapp_id, tosca_vnf_id = get_node_vnf_vapp_id_ECM(vapp_name)


def modify_configurable_prop_tosca(node_name, vapp_name, file_name, result):
    """Modifying parameters of tosca node."""
    try:
        log.info('Modify parameter of node- %s', node_name)
        Report_file.add_line('Modify parameter of node-' + node_name)
        sit_data = SIT_initialization.get_model_objects(SIT_initialization, 'SIT')
        ecm_host_data = Initialization_script.get_model_objects(Initialization_script, 'ECM_CORE')
        global is_vm_vnfm
        global vm_vnfm_namespace
        is_vm_vnfm = sit_data._SIT__is_vm_vnfm
        vm_vnfm_namespace = ecm_host_data._Ecm_core__vm_vnfm_namespace

        get_tosca_vnf_vapp_id(vapp_name)
        modify_configurable_node_parameters(node_name, 'CONFIGURABLE_PROPERTIES', file_name, tosca_vapp_id)

        if 'TRUE' == is_vm_vnfm:

            db_query = '''kubectl exec eric-vnflcm-db-0 -c eric-vnflcm-db -n {} -- psql -U postgres -d vnflafdb -c "select vnfconfigurableproperties from vnfs where vnfid='{}';"'''.format(
                vm_vnfm_namespace, tosca_vnf_id)

        else:

            db_query = '''select vnfconfigurableproperties from vnfs where vnfid='{}';'''.format(tosca_vnf_id)

        Report_file.add_line('db query - ' + db_query)
        verify_result_in_vnflaf_db(node_name, 'CONFIGURABLE_PROPERTIES', db_query, result, is_vm_vnfm)

    except Exception as e:
        log.error('Error modifying configurable properties for TOSCA node %s', str(e))
        Report_file.add_line('Error modifying configurable properties for TOSCA node ' + str(e))
        assert False


def modify_metadata_tosca(node_name, file_name, result):
    """Modifying metadata of tosca epg."""
    try:
        log.info('Modify meta data of node- %s', node_name)
        Report_file.add_line('Modify meta data of node- ' + node_name)

        modify_configurable_node_parameters(node_name, 'METADATA', file_name, tosca_vapp_id)

        log.info("Waiting for 5 seconds before verifying configurable parameter in vnflaf DB")
        time.sleep(5)

        if 'TRUE' == is_vm_vnfm:

            db_query = '''kubectl exec eric-vnflcm-db-0 -c eric-vnflcm-db -n {} -- psql -U postgres -d vnflafdb -c "select metadata from instantiatedvnf where vnfid='{}';"'''.format(
                vm_vnfm_namespace, tosca_vnf_id)

        else:

            db_query = '''select metadata from instantiatedvnf where vnfid='{}';'''.format(tosca_vnf_id)

        Report_file.add_line('db query - ' + db_query)
        verify_result_in_vnflaf_db(node_name, 'METADATA', db_query, result, is_vm_vnfm)

    except Exception as e:
        log.error('Error  modifying meta data for TOSCA node %s', str(e))
        Report_file.add_line('Error  modifying meta data for TOSCA ' + str(e))
        assert False


def modify_extension_tosca(node_name, file_name, result):
    """Modifying extension of tosca epg."""
    try:

        log.info('Modify extension of node- %s', node_name)
        Report_file.add_line('Modify extension of node- ' + node_name)

        modify_configurable_node_parameters('TOSCA_DUMMY', 'EXTENSION', file_name, tosca_vapp_id)

        if 'TRUE' == is_vm_vnfm:
            vmvnfm_conn = get_VMVNFM_host_connection()
            vmvnfm_version = fetch_vmvnfm_version(vmvnfm_conn, vm_vnfm_namespace)

            if vmvnfm_version >= version.parse("2.50.0-13"):
                log.info("VM VNFM version is greater than 2.50.0-13, using new db query")
                query = f"select extensions from vnfs where vnfid='{tosca_vnf_id}';"
            else:
                query = f"select extensions from instantiatedvnf where vnfid='{tosca_vnf_id}';"

            db_query = f'kubectl exec eric-vnflcm-db-0 -c eric-vnflcm-db -n {vm_vnfm_namespace} -- psql -U postgres ' \
                       f'-d vnflafdb -c "{query}" '

            vmvnfm_conn.close()
        else:

            db_query = f"select extensions from vnfs where vnfid='{tosca_vnf_id}';"

        Report_file.add_line('db query - ' + db_query)
        verify_result_in_vnflaf_db(node_name, 'EXTENSION', db_query, result, is_vm_vnfm)

    except Exception as e:
        log.error('Error modifying extension parameter for TOSCA node %s', str(e))
        Report_file.add_line('Error modifying extension parameter for TOSCA node ' + str(e))
        assert False
