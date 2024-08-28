from com_ericsson_do_auto_integration_model.SIT import SIT
from com_ericsson_do_auto_integration_scripts.SCALE_HEAL import (epg_scale_heal, lcm_transfer_scale_files,
                                                                 transfer_scale_files, eocm_dummy_scale_out)
from com_ericsson_do_auto_integration_utilities.Logger import Logger
from com_ericsson_do_auto_integration_utilities.SIT_files_update import (update_epg_heal_json_file,
                                                                         update_tosca_epg_heal_json_file)
from com_ericsson_do_auto_integration_initilization.SIT_initialization import SIT_initialization

log = Logger.get_logger('EPG_SCALE_HEAL.py')


class EpgScaleOperations:

    @staticmethod
    def ecm_scale(scale_type, scale_option):
        if scale_option == "EPG_TOSCA_SCALE_HEAL":
            scale_conf_files = ['vsfo-cp3.xml']
            transfer_scale_files(scale_conf_files, scale_option)
            if scale_type == "SCALE_OUT":
                file_name = 'scaleOutEcm_vEPG.json'
            if scale_type == "SCALE_IN":
                file_name = 'scaleInEcm_vEPG.json'
        if scale_option == "EPG_SCALE_HEAL":
            scale_conf_files = ['epg_vsfo_cp3.xml']
            is_vm_vnfm = SIT.get_is_vm_vnfm(SIT)
            if is_vm_vnfm == 'TRUE':
                transfer_scale_files(scale_conf_files, scale_option)
            else:
                lcm_transfer_scale_files(scale_conf_files, scale_option)
            if scale_type == "SCALE_OUT":
                file_name = 'epgscaleOut.json'
            if scale_type == "SCALE_IN":
                file_name = 'epgscaleIn.json'

        eocm_dummy_scale_out(file_name, scale_option)

    @staticmethod
    def tosca_epg_ecm_scale_out():
        log.info('Start Tosca EPG Scale-Out')
        EpgScaleOperations.ecm_scale("SCALE_OUT", "EPG_TOSCA_SCALE_HEAL")
        log.info('Tosca EPG Scale-Out completed')

    @staticmethod
    def tosca_epg_ecm_scale_in():
        log.info('Start Tosca EPG Scale-In')
        EpgScaleOperations.ecm_scale("SCALE_IN", "EPG_TOSCA_SCALE_HEAL")
        log.info('Tosca EPG Scale-In completed')

    @staticmethod
    def epg_ecm_scale_out():
        log.info('Start EPG Scale-Out')
        EpgScaleOperations.ecm_scale("SCALE_OUT", "EPG_SCALE_HEAL")
        log.info('EPG Scale-Out completed')

    @staticmethod
    def epg_ecm_scale_in():
        log.info('Start EPG Scale-In')
        EpgScaleOperations.ecm_scale("SCALE_IN", "EPG_SCALE_HEAL")
        log.info('EPG Scale-In completed')

    def epg_heal(self):
        sit_data = SIT_initialization.get_model_objects(SIT_initialization, 'SIT')
        epg_vapp_name = sit_data._SIT__epg_vapp_name
        file_name = 'Heal.json'
        epg_vapp_name = epg_vapp_name + '_epg_vsfo_cp-29'
        update_epg_heal_json_file(file_name, epg_vapp_name)
        epg_scale_heal(file_name, epg_vapp_name, 'EPG_SCALE_HEAL')

    def tosca_epg_heal(self):
        sit_data = SIT_initialization.get_model_objects(SIT_initialization, 'SIT')
        tosca_epg_vapp_name = sit_data._SIT__tosca_epg_vapp
        file_name = 'Tosca_Heal.json'
        tosca_epg_vapp_name = tosca_epg_vapp_name + '_VSFO-CP-29'
        update_tosca_epg_heal_json_file(file_name, tosca_epg_vapp_name)
        epg_scale_heal(file_name, tosca_epg_vapp_name, 'TOSCA-EPG-HEAL')
