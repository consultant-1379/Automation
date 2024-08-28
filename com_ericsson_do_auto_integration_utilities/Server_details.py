"""
Created on 30 Apr 2020

@author: zsyapra
"""
from com_ericsson_do_auto_integration_model.Ecm_core import Ecm_core
from com_ericsson_do_auto_integration_utilities.Logger import Logger
from com_ericsson_do_auto_integration_utilities.Report_file import Report_file
from com_ericsson_do_auto_integration_initilization.ECM_PI_initialization import ECM_PI_Initialization
from com_ericsson_do_auto_integration_initilization.Initialization_script import Initialization_script
from com_ericsson_do_auto_integration_initilization.SIT_initialization import SIT_initialization

log = Logger.get_logger('Server_details')


class Server_details(object):

    def openstack_host_server_details(self):
        log.info('start fetching epis host server details. ')
        Report_file.add_line('start fetching epis host server details.')

        try:
            EPIS_data = ECM_PI_Initialization.get_model_objects(ECM_PI_Initialization, 'EPIS')
            openstack_ip = EPIS_data._EPIS__openstack_ip
            username = EPIS_data._EPIS__openstack_username
            password = EPIS_data._EPIS__openstack_password
            openrc_filename = EPIS_data._EPIS__openrc_filename
            return openstack_ip, username, password, openrc_filename
        except Exception as e:
            log.error('Error while fetching openstack server details from DIT ' + str(e))
            Report_file.add_line('Error while fetching openstack server details from DIT ' + str(e))
            assert False

    def ecm_host_blade_details(self):
        try:
            ecm_host_data = Initialization_script.get_model_objects(Initialization_script, 'ECM_CORE')
            ecm_server_ip = ecm_host_data._Ecm_core__ECM_Host_Blade_IP
            ecm_username = ecm_host_data._Ecm_core__ECM_Host_Blade_username
            ecm_password = ecm_host_data._Ecm_core__ECM_Host_Blade_Password
            return ecm_server_ip, ecm_username, ecm_password
        except Exception as e:
            log.error('Error while fetching ecm host data server details from DIT ' + str(e))
            Report_file.add_line('Error while fetching ecm host data server details from DIT ' + str(e))
            assert False

    def lcm_host_server_details(self):
        try:
            ecm_host_data = Initialization_script.get_model_objects(Initialization_script, 'ECM_CORE')
            lcm_server_ip = ecm_host_data._Ecm_core__VNF_LCM_Servicedb_IP
            lcm_username = ecm_host_data._Ecm_core__VNF_LCM_Servicedb_Username
            lcm_password = ecm_host_data._Ecm_core__VNF_LCM_Servicedb_Password
            return lcm_server_ip, lcm_username, lcm_password
        except Exception as e:
            log.error('Error while fetching lcm server details from DIT ' + str(e))
            Report_file.add_line('Error while fetching lcm server details from DIT ' + str(e))
            assert False

    def ecm_host_blade_env(self):
        try:
            ecm_host_data = Initialization_script.get_model_objects(Initialization_script, 'ECM_CORE')
            environment = ecm_host_data._Ecm_core__enviornment
            return environment
        except Exception as e:
            log.error('Error while fetching ecm core env details from DIT ' + str(e))
            Report_file.add_line('Error while fetchig ecm core env details from DIT ' + str(e))
            assert False

    def ecm_host_blade_corevmip(self):
        try:
            # This core_VM will always used in curl commands towords ECM
            ecm_host_data = Initialization_script.get_model_objects(Initialization_script, 'ECM_CORE')
            core_vm_ip = ecm_host_data._Ecm_core__CORE_VM_IP
            return core_vm_ip

        except Exception as e:
            log.error('Error while fetching ecm core server ip details from DIT ' + str(e))
            Report_file.add_line('Error while fetching ecm core server ip details from DIT ' + str(e))
            assert False

    def enm_host_server_details(self):
        try:
            enm_data = Initialization_script.get_model_objects(Initialization_script, 'VNFM')
            enm_hostname = enm_data._Vnfm__authIpAddress
            enm_username = enm_data._Vnfm__authUserName
            enm_password = enm_data._Vnfm__authPassword

            return enm_hostname, enm_username, enm_password
        except Exception as e:
            log.error('Error while fetching  enm host server details from DIT ' + str(e))
            Report_file.add_line('Error while fetching enm host server details from DIT ' + str(e))
            assert False

    def core_vm_details(self, core_vm_2=False):
        try:

            core_vm_data = ECM_PI_Initialization.get_model_objects(ECM_PI_Initialization, 'ECMPI')
            username = core_vm_data._Ecm_PI__CORE_VM_USERNAME
            password = core_vm_data._Ecm_PI__CORE_VM_PASSWORD
            deployment_type = core_vm_data._Ecm_PI__deployment_type

            if deployment_type == 'HA':
                if core_vm_2:
                    core_vm_ip = core_vm_data._Ecm_PI__CORE_VM_2_HA_IP
                else:
                    core_vm_ip = core_vm_data._Ecm_PI__CORE_VM_HA_IP
            else:
                core_vm_ip = core_vm_data._Ecm_PI__CORE_VM_IP

            return core_vm_ip, username, password
        except Exception as e:
            log.error('Error while fetching  core_vm details from DIT ' + str(e))
            Report_file.add_line('Error while fetching core_vm server details from DIT ' + str(e))
            assert False

    def get_deployment_type(self):
        try:
            core_vm_data = ECM_PI_Initialization.get_model_objects(ECM_PI_Initialization, 'ECMPI')
            deployment_type = core_vm_data._Ecm_PI__deployment_type
            return deployment_type

        except Exception as e:
            log.error('Error while fetching deployment type ' + str(e))
            Report_file.add_line('Error while fetching deployment type ' + str(e))
            assert False

    def vm_vnfm_director_details(self, ccd1=False):
        try:
            if ccd1:
                vm_vnfm_director_ip = Ecm_core.get_ccd1_vm_vnfm_director_ip(Ecm_core)
                vm_vnfm_director_username = Ecm_core.get_ccd1_vm_vnfm_director_username(Ecm_core)
            else:
                vm_vnfm_director_ip = Ecm_core.get_vm_vnfm_director_ip(Ecm_core)
                vm_vnfm_director_username = Ecm_core.get_vm_vnfm_director_username(Ecm_core)
            log.info('vmvnfm director ip : %s and vmvnfm username : %s',
                     vm_vnfm_director_ip, vm_vnfm_director_username)
            return vm_vnfm_director_ip, vm_vnfm_director_username
        except Exception as e:
            log.error('Error while fetching vm-vnfm director details  %s', str(e))
            assert False

    def is_vm_vnfm_usecase(self):

        sit_data = SIT_initialization.get_model_objects(SIT_initialization, 'SIT')
        is_vm_vnfm = sit_data._SIT__is_vm_vnfm

        return is_vm_vnfm

    def get_evnfm_details(self):
        ecm_host_data = Initialization_script.get_model_objects(Initialization_script, 'ECM_CORE')

        evnfm_hostname = ecm_host_data._Ecm_core__evnfm_hostname
        evnfm_username = ecm_host_data._Ecm_core__evnfm_auth_username
        evnfm_password = ecm_host_data._Ecm_core__evnfm_auth_password

        return evnfm_hostname, evnfm_username, evnfm_password

    def get_wano_details(self):

        wano_data = SIT_initialization.get_model_objects(SIT_initialization, 'wano')

        wano_hostname = wano_data._wano__wano_hostname
        wano_user = wano_data._wano__wano_username
        wano_password = wano_data._wano__wano_password

        return wano_hostname, wano_user, wano_password

    def get_metrics_details(self):
        wano_data = SIT_initialization.get_model_objects(SIT_initialization, 'wano')
        metrics_host_url = wano_data._wano__metrics_host_url
        metrics_value_pack = wano_data._wano__metrics_value_pack

        return metrics_host_url, metrics_value_pack

    def get_tenant_name(self):
        sit_data = SIT_initialization.get_model_objects(SIT_initialization, 'SIT')
        tenant_name = sit_data._SIT__tenantName

        return tenant_name

    def get_abcd_vm_details(self):
        try:
            ecm_host_data = Initialization_script.get_model_objects(Initialization_script, 'ECM_CORE')
            abcd_vm_serverip = ecm_host_data._Ecm_core__abcd_vm_ip
            abcd_username = ecm_host_data._Ecm_core__abcd_vm_username
            abcd_password = ecm_host_data._Ecm_core__abcd_vm_password
            return abcd_vm_serverip, abcd_username, abcd_password
        except Exception as e:
            log.error('Error while fetching abcd vm details  ' + str(e))
            Report_file.add_line('Error while fetching abcd vm details ' + str(e))
            assert False

    def get_vm_vnfm_namespace(self):

        try:
            ecm_host_data = Initialization_script.get_model_objects(Initialization_script, 'ECM_CORE')
            vm_vnfm_namespace = ecm_host_data._Ecm_core__vm_vnfm_namespace
            return vm_vnfm_namespace

        except Exception as e:
            log.error('Error while fetching vm_vnfm_namespace' + str(e))
            Report_file.add_line('Error while fetching vm_vnfm_namespace' + str(e))
            assert False

    def get_environment_user_platform(self):
        try:
            sit_data = SIT_initialization.get_model_objects(SIT_initialization, 'SIT')
            environment_user_platform = sit_data._SIT__environment_user_platform
            return environment_user_platform

        except Exception as e:
            log.error('Error while fetching platform type ' + str(e))
            Report_file.add_line('Error while fetching platform type ' + str(e))
            assert False

    def ecde_user_details(self, user):
        ecde_data = SIT_initialization.get_model_objects(SIT_initialization, 'Ecde')

        if user == 'admin':
            ecde_fqdn = ecde_data._Ecde__ecde_fqdn
            ecde_admin_user = ecde_data._Ecde__ecde_admin_username
            ecde_admin_password = ecde_data._Ecde__ecde_admin_password
            return ecde_fqdn, ecde_admin_user, ecde_admin_password

        elif user == 'vendor':
            ecde_fqdn = ecde_data._Ecde__ecde_fqdn
            ecde_vendor_user = 'AUTO_USER'
            ecde_vendor_password = 'User@123'
            return ecde_fqdn , ecde_vendor_user, ecde_vendor_password

    def ecde_AAT_details(self):
        ecde_data = SIT_initialization.get_model_objects(SIT_initialization, 'Ecde')

        ecde_aat_ip = ecde_data._Ecde__ecde_aat_ip
        ecde_aat_user = ecde_data._Ecde__ecde_aat_username
        ecde_aat_password = ecde_data._Ecde__ecde_aat_password
        return ecde_aat_ip, ecde_aat_user, ecde_aat_password

    def ecde_spinnaker_details(self):
        ecde_data = SIT_initialization.get_model_objects(SIT_initialization, 'Ecde')

        ecde_spinnaker_hostname = ecde_data._Ecde__ecde_spinnaker_hostname
        ecde_spinnaker_user = ecde_data._Ecde__ecde_spinnaker_username
        ecde_spinnaker_password = ecde_data._Ecde__ecde_spinnaker_password
        return ecde_spinnaker_hostname, ecde_spinnaker_user, ecde_spinnaker_password

    def get_log_verification_host_url(self):

        sit_data = SIT_initialization.get_model_objects(SIT_initialization, 'SIT')
        log_verify_host_url = sit_data._SIT__log_verify_host_url

        return log_verify_host_url

    def get_uds_host_data(self):

        sit_data = SIT_initialization.get_model_objects(SIT_initialization, 'SIT')

        uds_hostname = sit_data._SIT__uds_hostname
        uds_username = sit_data._SIT__uds_username
        uds_password = 'Ericsson123!'

        return uds_hostname, uds_username, uds_password

    def get_onboarded_vfc_id(self, vfc_type):
        sit_data = SIT_initialization.get_model_objects(SIT_initialization, 'SIT')

        vfc_id_dict = sit_data._SIT__vfc_onboarded_ids_dict

        return vfc_id_dict[vfc_type]

    def get_certified_vfc_id(self, vfc_type):
        sit_data = SIT_initialization.get_model_objects(SIT_initialization, 'SIT')

        vfc_cert_id_dict = sit_data._SIT__vfc_certified_ids_dict

        return vfc_cert_id_dict[vfc_type]

    def get_created_vf_id(self):
        sit_data = SIT_initialization.get_model_objects(SIT_initialization, 'SIT')

        uds_vnf_id = sit_data._SIT__uds_vf_unique_id

        return uds_vnf_id

    def get_add_vfc_composition_ids(self):
        sit_data = SIT_initialization.get_model_objects(SIT_initialization, 'SIT')

        
        ns_composition_id = sit_data._SIT__ns_composition_id
        capabilities_unique_id = sit_data._SIT__capabilities_unique_id
        requirements_unique_id = sit_data._SIT__requirements_unique_id

        return ns_composition_id, capabilities_unique_id, requirements_unique_id

    def get_add_epg_vfc_composition_id(self):
        sit_data = SIT_initialization.get_model_objects(SIT_initialization, 'SIT')

        epg_composition_id = sit_data._SIT__epg_composition_id
        return epg_composition_id

    def get_uds_service_id(self):
        sit_data = SIT_initialization.get_model_objects(SIT_initialization, 'SIT')

        uds_service_id = sit_data._SIT__uds_service_unique_id

        return uds_service_id


