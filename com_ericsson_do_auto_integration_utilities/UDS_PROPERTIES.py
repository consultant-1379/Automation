"""
Created on 22-09-2022
contains all the constants and file paths required for UDS VNF and NFV service creation jobs
@author: zbhaper
"""

from com_ericsson_do_auto_integration_model.SIT import SIT
VLM = {"create_vlm_file": "createVLM.json",
       "create_vlm_source_path":  "com_ericsson_do_auto_integration_files/UDS_files/createVLM.json",
       "create_vlm_destination_path": f"{SIT.get_base_folder(SIT)}createVLM.json",
       "submit_vlm_file": "submit.json",
       "submit_vlm_source_path": "com_ericsson_do_auto_integration_files/UDS_files/submit.json",
       "submit_vlm_destination_path": f"{SIT.get_base_folder(SIT)}submit.json"
       }

VSP = {"create_vsp_file": "createVSP.json",
       "create_vsp_source_path": "com_ericsson_do_auto_integration_files/UDS_files/createVSP.json",
       "create_vsp_destination_path": f"{SIT.get_base_folder(SIT)}createVSP.json",
       "process_vsp_file": "test.json",
       "process_vsp_source_path": "com_ericsson_do_auto_integration_files/UDS_files/test.json",
       "process_vsp_destination_path": f"{SIT.get_base_folder(SIT)}test.json",
       "commit_vsp_file": "commitVSP.json",
       "commit_vsp_source_path": "com_ericsson_do_auto_integration_files/UDS_files/commitVSP.json",
       "commit_vsp_destination_path": f"{SIT.get_base_folder(SIT)}commitVSP.json",
       "submit_vsp_file": "submit.json",
       "submit_vsp_source_path": "com_ericsson_do_auto_integration_files/UDS_files/submit.json",
       "submit_vsp_destination_path": f"{SIT.get_base_folder(SIT)}submit.json",
       "create_vsp_package_source_path": "com_ericsson_do_auto_integration_files/UDS_files/createPackage.json",
       "create_vsp_package_destination_path": f"{SIT.get_base_folder(SIT)}createPackage.json",
       }

VSP_AS_VF = {"import_vsp_file": "importVSPasVF.json",
             "import_vsp_source_path": "com_ericsson_do_auto_integration_files/UDS_files/importVSPasVF.json",
             "import_vsp_destination_path": f"{SIT.get_base_folder(SIT)}importVSPasVF.json",
             "result_source": f"{SIT.get_base_folder(SIT)}importvspasVF_result.json",
             "result_destination": "com_ericsson_do_auto_integration_files/UDS_files/importvspasVF_result.json",
             "certify_vf_file": "certifyVF.json",
             "certify_vf_source_path": "com_ericsson_do_auto_integration_files/UDS_files/certifyVF.json",
             "certify_vf_destination_path": f"{SIT.get_base_folder(SIT)}certifyVF.json"}

NFV_SERVICE = {"nfv_service_file": "createNFVService.json",
               "nfv_service_source_path": "com_ericsson_do_auto_integration_files/UDS_files/createNFVService.json",
               "nfv_service_destination_path": f"{SIT.get_base_folder(SIT)}createNFVService.json"}

VNF_SERVICE = {"vnf_service_file": "createVNFService.json",
               "vnf_service_source_path": "com_ericsson_do_auto_integration_files/UDS_files/createVNFService.json",
               "vnf_service_destination_path": f"{SIT.get_base_folder(SIT)}createVNFService.json",
               "add_vnf_service_file": "addVFtoVNFService.json",
               "add_vnf_service_source_path": "com_ericsson_do_auto_integration_files/UDS_files/addVFtoVNFService.json",
               "add_vnf_service_destination_path": f"{SIT.get_base_folder(SIT)}addVFtoVNFService.json",
               "certify_vnf_file": "certify.json",
               "certify_vnf_source_path": "com_ericsson_do_auto_integration_files/UDS_files/certify.json",
               "certify_vnf_destination_path": f"{SIT.get_base_folder(SIT)}certify.json",
               "out_certify_destination": "com_ericsson_do_auto_integration_files/UDS_files/output_CertifyService.json",
               "out_certify_source": f"{SIT.get_base_folder(SIT)}output_CertifyService.json",
               "distribute_Service_source": f"{SIT.get_base_folder(SIT)}output_distributeService.txt",
               "distribute_Service_des": "com_ericsson_do_auto_integration_files/UDS_files/output_distributeService.txt"
               }

UDS_ST_CREATION = {"uds_source_path": "com_ericsson_do_auto_integration_files/UDS_files/",
                   "uds_dest_path": SIT.get_base_folder(SIT),
                   "uds_service_file": "uds_service.json",
                   "add_vfc_to_service": "add_vfc_to_service.json",
                   "declare_inputs": "declare_inputs.json",
                   "add_values_to_vfc_inputs": "add_values_to_vfc_inputs.json",
                   "add_values_to_properties": "add_values_to_properties.json",
                   "add_inputs_to_vfc": "add_inputs_to_vfc.json",
                   "add_tosca_function": "add_tosca_function.json",
                   "add_directives": "add_directives.json",
                   "add_node_filter_properties": "add_node_filter_properties.json",
                   "associate_vfc": "associate_vfc.json",
                   "ns_config_template": "nsAdditionalParamTEPG_uds.json",
                   "vnf_config_template": "vnfAdditionalParamTEPG.json",
                   "day1_config_template": "day1ConfigTEPG.xml",
                   "vfc_names": {"geographicSite": "GEOSITE", "vimZone": "VIMZONE0",
                                 "subsystemRef": "SUBSYSTEM", "virtNetworkServ": "NS",
                                 "vnf": "EPG"},
                   "inputs_to_declare": {"GEOSITE": ["name"], "SUBSYSTEM": ["name", "accessId"],
                                         "VIMZONE0": ["name"], "NS": ["name"], "EPG": ["name"]},
                   "input_value_dict": {"GEOSITE": {"name": "Athlone Data Center Test"},
                                        "SUBSYSTEM": {"name": "SOL005_EOCM_367", "accessId": "ECM_Sol005"},
                                        "VIMZONE0": {"name": "vimzone1"},
                                        "NS": {"name": "tepg_sol005"},
                                        "EPG": {"name": "Tosca_EPG_VNFD"}},
                   "inputs_to_add": {"nsdId": "string", "vdcName": "string", "connectionName": "string",
                                     "subnetId": "string", "targetVdc": "string", "vnfmId": "string",
                                     "connectedVn": "string"},
                   "ns_tosca_function_values": {"SO_NS::nsdId": "nsdId", "SO_NS::vdcName": "vdcName",
                                                "CUSTOM_NS::connectedVn": "connectedVn",
                                                "CUSTOM_NS::connectionName": "connectionName",
                                                "CUSTOM_NS::subnetId": "subnetId", "CUSTOM_NS::targetVdc": "targetVdc",
                                                "CUSTOM_NS::vnfmId": "vnfmId"},
                   "ns_properties": {"CUSTOM_NS::connectedVn": "string", "CUSTOM_NS::connectionName": "string",
                                     "CUSTOM_NS::subnetId": "string", "CUSTOM_NS::targetVdc": "string",
                                     "CUSTOM_NS::vnfmId": "string"}
                   }

PACKAGE_NAME = "/Tosca_EPG_VNFD.csar"
TENANT = "master"


