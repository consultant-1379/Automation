from com_ericsson_do_auto_integration_model.Ecm_core import Ecm_core

ecm_namespace = Ecm_core.get_ecm_namespace(Ecm_core)
vm_vnfm_namespace = Ecm_core.get_vm_vnfm_namespace(Ecm_core)
# awk check PODs status other than Completed and Running or PODs that restarted
NAMESPACES = {ecm_namespace: 'ecm-namespace', vm_vnfm_namespace: 'eo-namespace'}
RESOURCE_TYPES =['deployments', 'statefulsets', 'cronjobs', 'daemonsets', 'rediscluster', 'pvc']
