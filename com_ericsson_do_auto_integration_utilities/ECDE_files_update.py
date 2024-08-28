'''
Created on Oct 10, 2019

@author: emaidns
'''

from com_ericsson_do_auto_integration_utilities.Logger import Logger
from com_ericsson_do_auto_integration_utilities.Report_file import Report_file
from com_ericsson_do_auto_integration_utilities.Json_file_handler import Json_file_handler
from com_ericsson_do_auto_integration_initilization.SIT_initialization import SIT_initialization
from com_ericsson_do_auto_integration_initilization.Initialization_script import Initialization_script
from com_ericsson_do_auto_integration_initilization.ECM_PI_initialization import ECM_PI_Initialization

log = Logger.get_logger('ECDE_files_update.py')


def update_aat_testsuite_file(file_name, ecde_aat_ip, ecde_aat_user, ecde_aat_password, aat_id, testcase_id):
    try:
        log.info('Start to update {} file '.format(file_name))
        Report_file.add_line('Start to update {} file '.format(file_name))

        file_path = r'com_ericsson_do_auto_integration_files/ECDE_files/' + file_name

        Json_file_handler.update_any_json_attr(Json_file_handler, file_path, [0, ], 'id',
                                               testcase_id)

        Json_file_handler.update_any_json_attr(Json_file_handler, file_path, [0, 'testHeadCatalog'], 'id',
                                               aat_id)
        Json_file_handler.update_any_json_attr(Json_file_handler, file_path, [0, 'testHeadCatalog'], 'ipAddress',
                                               ecde_aat_ip)
        Json_file_handler.update_any_json_attr(Json_file_handler, file_path, [0, 'testHeadCatalog'], 'password',
                                               ecde_aat_password)
        Json_file_handler.update_any_json_attr(Json_file_handler, file_path, [0, 'testHeadCatalog'], 'username',
                                               ecde_aat_user)

        log.info('Finished to update {} file '.format(file_name))
        Report_file.add_line('Finished to update {} file '.format(file_name))

    except Exception as e:

        log.error('Error to update {} file with error {}'.format(file_name, str(e)))
        Report_file.add_line('Error to update {} file with error {}'.format(file_name, str(e)))
        assert False


def update_aat_tool_file(file_name, ecde_aat_ip, ecde_aat_user, ecde_aat_password, id=2):
    try:
        log.info('Start to update {} file '.format(file_name))
        Report_file.add_line('Start to update {} file '.format(file_name))

        file_path = r'com_ericsson_do_auto_integration_files/ECDE_files/' + file_name

        Json_file_handler.update_any_json_attr(Json_file_handler, file_path, ['testHeadCatalog'], 'id',
                                               id)
        Json_file_handler.update_any_json_attr(Json_file_handler, file_path, ['testHeadCatalog'], 'ipAddress',
                                               ecde_aat_ip)
        Json_file_handler.update_any_json_attr(Json_file_handler, file_path, ['testHeadCatalog'], 'password',
                                               ecde_aat_password)
        Json_file_handler.update_any_json_attr(Json_file_handler, file_path, ['testHeadCatalog'], 'username',
                                               ecde_aat_user)

        log.info('Finished to update {} file '.format(file_name))
        Report_file.add_line('Finished to update {} file '.format(file_name))

    except Exception as e:

        log.error('Error to update {} file with error {}'.format(file_name, str(e)))
        Report_file.add_line('Error to update {} file with error {}'.format(file_name, str(e)))
        assert False


def update_pipeline_tep_file(file_name, tep_name, onboarding_system_name, onboarding_type):
    try:
        log.info('Start to update {} file '.format(file_name))
        Report_file.add_line('Start to update {} file '.format(file_name))

        file_path = r'com_ericsson_do_auto_integration_files/ECDE_files/' + file_name

        Json_file_handler.update_any_json_attr(Json_file_handler, file_path, [], 'name', tep_name)
        Json_file_handler.update_any_json_attr(Json_file_handler, file_path, ['stages', 0, 'parameterValues'],
                                               'onboardingInstance', onboarding_system_name)
        Json_file_handler.update_any_json_attr(Json_file_handler, file_path, ['stages', 0, 'parameterValues'],
                                               'onboardingType', onboarding_type)

        Json_file_handler.update_any_json_attr(Json_file_handler, file_path, ['stages', 2, 'parameterValues'],
                                               'onboardingInstance', onboarding_system_name)
        Json_file_handler.update_any_json_attr(Json_file_handler, file_path, ['stages', 2, 'parameterValues'],
                                               'onboardingType', onboarding_type)

        Json_file_handler.update_any_json_attr(Json_file_handler, file_path, ['triggers', 0], 'source', tep_name)

        log.info('Finished to update {} file '.format(file_name))
        Report_file.add_line('Finished to update {} file '.format(file_name))

    except Exception as e:

        log.error('Error to update {} file with error {}'.format(file_name, str(e)))
        Report_file.add_line('Error to update {} file with error {}'.format(file_name, str(e)))
        assert False


def update_ecm_onboarding_system_file(file_name, record_name, update=False, onboard_system_id=1):
    try:

        log.info('Start to update {} file '.format(file_name))
        Report_file.add_line('Start to update {} file '.format(file_name))

        ecm_core_data = Initialization_script.get_model_objects(Initialization_script, 'ECM_CORE')
        sit_data = SIT_initialization.get_model_objects(SIT_initialization, 'SIT')

        core_vm_hostname = ecm_core_data._Ecm_core__core_vm_hostname
        ecm_gui_username = ecm_core_data._Ecm_core__ecm_gui_username
        ecm_gui_passwd = ecm_core_data._Ecm_core__ecm_gui_password

        vdc_name = sit_data._SIT__vdc_name
        vdc_id = sit_data._SIT__vdc_id
        tenant_name = sit_data._SIT__tenantName
        vim_zone_name = sit_data._SIT__vimzone_name

        if update:
            data = {
                "enableHttps": True,
                "id": onboard_system_id,
                "fqdn": core_vm_hostname,
                "onBoardingSysPassword": ecm_gui_passwd,
                "onBoardingSysTenantName": tenant_name,
                "onBoardingSysUsername": ecm_gui_username,
                "onBoardingSystemName": record_name,
                "onBoardingSystemType": "ECM",
                "vdcId": vdc_id,
                "vdcName": vdc_name,
                "vimZoneName": vim_zone_name
            }

        else:

            data = {
                "enableHttps": True,
                "fqdn": core_vm_hostname,
                "onBoardingSysPassword": ecm_gui_passwd,
                "onBoardingSysTenantName": tenant_name,
                "onBoardingSysUsername": ecm_gui_username,
                "onBoardingSystemName": record_name,
                "onBoardingSystemType": "ECM",
                "vdcId": vdc_id,
                "vdcName": vdc_name,
                "vimZoneName": vim_zone_name
            }

        Json_file_handler.update_json_file(Json_file_handler,
                                           r'com_ericsson_do_auto_integration_files/ECDE_files/' + file_name, data)
        log.info('Finished to update {} file '.format(file_name))
    except Exception as e:

        log.error('Error to update {} file with error {}'.format(file_name, str(e)))
        Report_file.add_line('Error to update {} file with error {}'.format(file_name, str(e)))
        assert False


def update_vnflcm_onboarding_system_file(file_name, system_name, update=False, onboard_system_id=1):
    try:

        log.info('Start to update {} file '.format(file_name))
        Report_file.add_line('Start to update {} file '.format(file_name))

        epis_data = ECM_PI_Initialization.get_model_objects(ECM_PI_Initialization, 'EPIS')
        ecde_data = SIT_initialization.get_model_objects(SIT_initialization, 'Ecde')

        ecde_enm_ip = ecde_data._Ecde__ecde_enm_ipaddress
        ecde_enm_username = ecde_data._Ecde__ecde_enm_username
        ecde_enm_password = ecde_data._Ecde__ecde_enm_password
        project_id = ecde_data._Ecde__project_id
        image_auth_url = ecde_data._Ecde__image_auth_url

        vim_zone_name = epis_data._EPIS__vimzone_name
        cloud_type = epis_data._EPIS__cloudManagerType
        vim_url = epis_data._EPIS__vim_url

        project_name = epis_data._EPIS__project_name
        project_admin_username = project_name + '_admin'

        if update:
            data = {
                "authURL": vim_url,
                "id": onboard_system_id,
                "enableHttps": False,
                "imageUploadUrl": image_auth_url,
                "ip4Address": ecde_enm_ip,
                "onBoardingSysUsername": ecde_enm_username,
                "onBoardingSysPassword": ecde_enm_password,
                "onBoardingSystemName": system_name,
                "onBoardingSystemType": "VNFM",
                "projectId": project_id,
                "vimName": vim_zone_name,
                "vimPassword": project_name.capitalize() + '.laf',
                "vimTenantName": project_name,
                "vimType": cloud_type,
                "vimUsername": project_admin_username
            }
        else:

            data = {
                "authURL": vim_url,
                "enableHttps": False,
                "imageUploadUrl": image_auth_url,
                "ip4Address": ecde_enm_ip,
                "onBoardingSysUsername": ecde_enm_username,
                "onBoardingSysPassword": ecde_enm_password,
                "onBoardingSystemName": system_name,
                "onBoardingSystemType": "VNFM",
                "projectId": project_id,
                "vimName": vim_zone_name,
                "vimPassword": project_name.capitalize() + '.laf',
                "vimTenantName": project_name,
                "vimType": cloud_type,
                "vimUsername": project_admin_username
            }

        Json_file_handler.update_json_file(Json_file_handler,
                                           r'com_ericsson_do_auto_integration_files/ECDE_files/' + file_name, data)
        log.info('Finished to update {} file '.format(file_name))
    except Exception as e:

        log.error('Error to update {} file with error {}'.format(file_name, str(e)))
        Report_file.add_line('Error to update {} file with error {}'.format(file_name, str(e)))
        assert False


def update_evnfm_onboarding_system_file(file_name, system_name, update=False, onboard_system_id=1):
    try:

        log.info('Start to update {} file '.format(file_name))
        Report_file.add_line('Start to update {} file '.format(file_name))

        ecm_host_data = Initialization_script.get_model_objects(Initialization_script, 'ECM_CORE')

        evnfm_hostname = ecm_host_data._Ecm_core__evnfm_hostname
        evnfm_username = ecm_host_data._Ecm_core__evnfm_auth_username
        evnfm_password = ecm_host_data._Ecm_core__evnfm_auth_password

        if update:
            data = {
                "id": onboard_system_id,
                "onBoardingSystemType": "EVNFM",
                "onBoardingSystemName": system_name,
                "onBoardingSysUsername": evnfm_username,
                "onBoardingSysPassword": evnfm_password,
                "fqdn": evnfm_hostname,
                "enableHttps": True
            }
        else:

            data = {
                "onBoardingSystemType": "EVNFM",
                "onBoardingSystemName": system_name,
                "onBoardingSysUsername": evnfm_username,
                "onBoardingSysPassword": evnfm_password,
                "fqdn": evnfm_hostname,
                "enableHttps": True
            }

        Json_file_handler.update_json_file(Json_file_handler,
                                           r'com_ericsson_do_auto_integration_files/ECDE_files/' + file_name, data)
        log.info('Finished to update {} file '.format(file_name))
    except Exception as e:

        log.error('Error to update {} file with error {}'.format(file_name, str(e)))
        Report_file.add_line('Error to update {} file with error {}'.format(file_name, str(e)))
        assert False


def update_product_file(file_name, product_name, vnftype_name, vnftype_id, vendor_name, vendor_id):
    try:

        log.info('Start to update {} file '.format(file_name))
        Report_file.add_line('Start to update {} file '.format(file_name))

        data = {
            "id": None,
            "productName": product_name,
            "productVersion": "1.0",
            "templateName": "Create",
            "vendor": {
                "id": vendor_id,
                "vendorName": vendor_name
            },
            "vnftype": {
                "id": vnftype_id,
                "vnfName": vnftype_name,
                "vnfDescription": "Eo-staging automation used for dummy and 3pp both vnf",
                "documnetId": None,
                "vnfTypeStatus": "ACTIVE"
            }
        }

        Json_file_handler.update_json_file(Json_file_handler,
                                           r'com_ericsson_do_auto_integration_files/ECDE_files/' + file_name, data)

        log.info('Finished to update {} file '.format(file_name))

    except Exception as e:

        log.error('Error to update {} file with error {}'.format(file_name, str(e)))
        Report_file.add_line('Error to update {} file with error {}'.format(file_name, str(e)))
        assert False


def update_validate_product_file(file_name, product_id, resources_id_list, val_level_id, val_stream_id,
                                 evnfm_vnf_type_id, evnfm_vendor_id):
    try:

        log.info('Start to update {} file '.format(file_name))
        Report_file.add_line('Start to update {} file '.format(file_name))

        data = {
            "id": None,
            "vnfProductId": product_id,
            "productResources": resources_id_list,
            "waitTime": None,
            "sites": ["swdp_templateConfigData"],
            "validationOrder": {
                "vnfProductId": product_id,
                "id": None,
                "orderStatus": "SUBMITTED",
                "pauseAfterInstantiation": "N",
                "haltOnFailure": "N",
                "vendor": {
                    "id": evnfm_vendor_id,
                    "vendorName": "AUTO_VENDOR"
                },
                "avopUser": {
                    "username": "AUTO_USER"
                },
                "waitTime": None,
                "validationStream": {
                    "id": val_stream_id
                },
                "validationLevel": {
                    "id": val_level_id
                },
                "vnftype": {
                    "id": evnfm_vnf_type_id
                }
            }
        }

        Json_file_handler.update_json_file(Json_file_handler,
                                           r'com_ericsson_do_auto_integration_files/ECDE_files/' + file_name, data)
        log.info('Finished to update {} file '.format(file_name))
    except Exception as e:

        log.error('Error to update {} file with error {}'.format(file_name, str(e)))
        Report_file.add_line('Error to update {} file with error {}'.format(file_name, str(e)))
        assert False


def update_dummy_hot_template(file_name, flavor_name, image_name, external_net_id, dummy_vnf_ip):
    try:

        log.info('Start to update {} file '.format(file_name))
        Report_file.add_line('Start to update {} file '.format(file_name))
        file_path = r'com_ericsson_do_auto_integration_files/ECDE_files/' + file_name

        attribute_list = ['parameters', 'public_net']
        Json_file_handler.update_nested_dict_yaml(Json_file_handler, file_path, attribute_list, 'default',
                                                  external_net_id)

        attribute_list = ['parameters', 'public_net_IP']
        Json_file_handler.update_nested_dict_yaml(Json_file_handler, file_path, attribute_list, 'default', dummy_vnf_ip)

        attribute_list = ['parameters', 'bootable_image']
        Json_file_handler.update_nested_dict_yaml(Json_file_handler, file_path, attribute_list, 'label', image_name)
        Json_file_handler.update_nested_dict_yaml(Json_file_handler, file_path, attribute_list, 'default', image_name)

        attribute_list = ['parameters', 'flavor1']
        Json_file_handler.update_nested_dict_yaml(Json_file_handler, file_path, attribute_list, 'default', flavor_name)

        log.info('Finished to update {} file '.format(file_name))
    except Exception as e:

        log.error('Error to update {} file with error {}'.format(file_name, str(e)))
        Report_file.add_line('Error to update {} file with error {}'.format(file_name, str(e)))
        assert False


def update_3pp_hot_template(file_name, flavor_name, image_name, external_net_id, vnf_3pp_ips, network_name):
    try:

        log.info('Start to update {} file '.format(file_name))
        Report_file.add_line('Start to update {} file '.format(file_name))
        file_path = r'com_ericsson_do_auto_integration_files/ECDE_files/' + file_name

        ip_list = vnf_3pp_ips.split(',')

        attribute_list = ['parameters', 'oam_net']
        Json_file_handler.update_nested_dict_yaml(Json_file_handler, file_path, attribute_list, 'default',
                                                  external_net_id)
        Json_file_handler.update_nested_dict_yaml(Json_file_handler, file_path, attribute_list, 'label', network_name)

        attribute_list = ['parameters', 'oam_net_IP']
        Json_file_handler.update_nested_dict_yaml(Json_file_handler, file_path, attribute_list, 'default', ip_list[0])

        attribute_list = ['parameters', 'bootable_image']
        Json_file_handler.update_nested_dict_yaml(Json_file_handler, file_path, attribute_list, 'default', image_name)

        attribute_list = ['parameters', 'flavor1']
        Json_file_handler.update_nested_dict_yaml(Json_file_handler, file_path, attribute_list, 'default', flavor_name)

        attribute_list = ['parameters', 'test_net_1']
        Json_file_handler.update_nested_dict_yaml(Json_file_handler, file_path, attribute_list, 'default',
                                                  external_net_id)
        Json_file_handler.update_nested_dict_yaml(Json_file_handler, file_path, attribute_list, 'label', network_name)

        attribute_list = ['parameters', 'test_net_1_IP']
        Json_file_handler.update_nested_dict_yaml(Json_file_handler, file_path, attribute_list, 'default', ip_list[1])

        attribute_list = ['parameters', 'test_net_2']
        Json_file_handler.update_nested_dict_yaml(Json_file_handler, file_path, attribute_list, 'default',
                                                  external_net_id)
        Json_file_handler.update_nested_dict_yaml(Json_file_handler, file_path, attribute_list, 'label', network_name)

        attribute_list = ['parameters', 'test_net_2_IP']
        Json_file_handler.update_nested_dict_yaml(Json_file_handler, file_path, attribute_list, 'default', ip_list[2])

        attribute_list = ['parameters', 'public_net']
        Json_file_handler.update_nested_dict_yaml(Json_file_handler, file_path, attribute_list, 'default', network_name)

        log.info('Finished to update {} file '.format(file_name))
    except Exception as e:

        log.error('Error to update {} file with error {}'.format(file_name, str(e)))
        Report_file.add_line('Error to update {} file with error {}'.format(file_name, str(e)))
        assert False


def update_dummy_wrapper_file(file_name, flavor_name, image_name, external_net_id, dummy_vnf_ip):
    try:

        log.info('Start to update {} file '.format(file_name))
        Report_file.add_line('Start to update {} file '.format(file_name))
        file_path = r'com_ericsson_do_auto_integration_files/ECDE_files/' + file_name

        attribute_list = ['instantiateVnfOpConfig']

        Json_file_handler.update_any_json_attr(Json_file_handler, file_path, attribute_list, 'servicesImage',
                                               image_name)
        Json_file_handler.update_any_json_attr(Json_file_handler, file_path, attribute_list, 'services_flavor',
                                               flavor_name)
        Json_file_handler.update_any_json_attr(Json_file_handler, file_path, attribute_list, 'external_net_id',
                                               external_net_id)
        Json_file_handler.update_any_json_attr(Json_file_handler, file_path, attribute_list,
                                               'external_ip_for_services_vm', dummy_vnf_ip)

        log.info('Finished to update {} file '.format(file_name))

    except Exception as e:

        log.error('Error to update {} file with error {}'.format(file_name, str(e)))
        Report_file.add_line('Error to update {} file with error {}'.format(file_name, str(e)))
        assert False


def update_vendor_user_file(file_name, vendor_id):
    try:

        log.info('Start to update {} file '.format(file_name))
        Report_file.add_line('Start to update {} file '.format(file_name))
        file_path = r'com_ericsson_do_auto_integration_files/ECDE_files/' + file_name

        Json_file_handler.update_any_json_attr(Json_file_handler, file_path, ["vendor"], "id", vendor_id)

        log.info('Finished to update {} file '.format(file_name))

    except Exception as e:

        log.error('Error to update {} file with error {}'.format(file_name, str(e)))
        Report_file.add_line('Error to update {} file with error {}'.format(file_name, str(e)))
        assert False


def update_validation_profile_file(file_name, profile_name):
    try:

        log.info('Start to update {} file '.format(file_name))
        Report_file.add_line('Start to update {} file '.format(file_name))
        file_path = r'com_ericsson_do_auto_integration_files/ECDE_files/' + file_name

        Json_file_handler.update_any_json_attr(Json_file_handler, file_path, [], "validationStreamName", profile_name)

        log.info('Finished to update {} file '.format(file_name))

    except Exception as e:

        log.error('Error to update {} file with error {}'.format(file_name, str(e)))
        Report_file.add_line('Error to update {} file with error {}'.format(file_name, str(e)))
        assert False


def update_validation_track_file(file_name, vendor_id, vnf_type_id, val_level_id, val_profile_id):
    try:

        log.info('Start to update {} file '.format(file_name))
        Report_file.add_line('Start to update {} file '.format(file_name))
        file_path = r'com_ericsson_do_auto_integration_files/ECDE_files/' + file_name

        data = {
            "trackStatus": None,
            "id": None,
            "templateName": "Create",
            "paramtext": "EditSpecificTrack",
            "vendor": {
                "id": vendor_id
            },
            "vNFType": {
                "id": vnf_type_id
            },
            "validationStream": {
                "id": val_profile_id
            },
            "validationLevel": {
                "id": val_level_id
            }
        }

        Json_file_handler.update_json_file(Json_file_handler,
                                           r'com_ericsson_do_auto_integration_files/ECDE_files/' + file_name, data)

        log.info('Finished to update {} file '.format(file_name))

    except Exception as e:

        log.error('Error to update {} file with error {}'.format(file_name, str(e)))
        Report_file.add_line('Error to update {} file with error {}'.format(file_name, str(e)))
        assert False


def update_assign_validation_track_file(file_name,vendor_id, vnf_type_id,val_level_id,val_profile_id,val_profile_name,val_track_id,evnfm_test_env_profile_id):
    try:

        log.info('Start to update {} file '.format(file_name))
        Report_file.add_line('Start to update {} file '.format(file_name))
        file_path = r'com_ericsson_do_auto_integration_files/ECDE_files/' + file_name

        data =  {
            "id":val_track_id,
            "vendor":{
              "id":vendor_id,
              "vendorName":"AUTO_VENDOR",
              "address":"address",
              "email":"vendortest@ericsson.com",
              "phonenumber":"1234567",
              "vendorStatus":"ACTIVE",
              "createdDate":"2021-02-18 12:47:51",
              "lastModifiedDate":"2021-02-18 12:47:51",
              "avopUsers":None
            },
            "validationStream":{
              "id":val_profile_id,
              "validationStreamName":val_profile_name,
              "validationStreamStatus":"ACTIVE",
              "description":"ValidationProfile_Test",
              "associatedSteamsVNFTypeSet":None,
              "documet":None,
              "associatedValidationStreamAndLevels":None
            },
            "validationLevel":{
              "id":val_level_id,
              "validationLevelName":"AUTO_INSTANTIATION",
              "validationLevelStatus":"ACTIVE",
              "description":"ValidationLevel_Test",
              "associatedValidationStreamAndLevels":None
            },
            "vNFType":{
              "id":vnf_type_id,
              "vnfName":"AUTO_DUMMY",
              "vnfDescription":"VNFType_Test",
              "documnetId":None,
              "documentName":None,
              "vnfTypeStatus":"ACTIVE",
              "assignedVNFTypes":None,
              "vnfProducts":None,
              "validationTracks":None,
              "validationOrders":None,
              "asociatedSteamsVNFTypeSet":None
            },
            "paramtext":"AssignTEP",
            "testEnvironment":{
              "id":evnfm_test_env_profile_id
            }
        }
        Json_file_handler.update_json_file(Json_file_handler,
                                           r'com_ericsson_do_auto_integration_files/ECDE_files/' + file_name, data)

        log.info('Finished to update {} file '.format(file_name))

    except Exception as e:

        log.error('Error to update {} file with error {}'.format(file_name, str(e)))
        Report_file.add_line('Error to update {} file with error {}'.format(file_name, str(e)))
        assert False
