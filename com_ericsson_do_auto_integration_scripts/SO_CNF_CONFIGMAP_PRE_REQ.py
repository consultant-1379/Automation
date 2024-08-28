'''
Created on 28 Apr 2021

@author: zsyapra
'''

from com_ericsson_do_auto_integration_model.SIT import SIT
from com_ericsson_do_auto_integration_scripts.CNF_NS_DEPLOYMENT import upload_tosca_cnf_package
from com_ericsson_do_auto_integration_utilities.Logger import Logger

log = Logger.get_logger('SO_CNF_CONFIGMAP_PRE_REQ.py')

class CnfConfigmapPreReq:
   
    def upload_cnfd_packages(self):
        pkgs_dir_path = SIT.get_cnf_configmap_software_path(SIT)
        upload_tosca_cnf_package(pkgs_dir_path)
        