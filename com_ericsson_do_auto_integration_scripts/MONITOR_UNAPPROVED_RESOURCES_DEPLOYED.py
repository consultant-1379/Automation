"""Monitor resources deployed in the target cluster"""
# pylint: disable=C0116
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
import json
import csv
import pandas as pd

from com_ericsson_do_auto_integration_utilities.Report_file import Report_file
from com_ericsson_do_auto_integration_files.MONITOR_RESOURCES_DEPLOYED.config import NAMESPACES, RESOURCE_TYPES
from com_ericsson_do_auto_integration_model.SIT import SIT
from com_ericsson_do_auto_integration_scripts.VM_VNFM_OPERATIONS import get_VMVNFM_host_connection
from com_ericsson_do_auto_integration_utilities.Common_utilities import Common_utilities
from com_ericsson_do_auto_integration_utilities.Logger import Logger

log = Logger.get_logger('MONITOR_UNAPPROVED_RESOURCES_DEPLOYED.py')
RESOURCE_HEADERS = ['Namespace', 'Resource Type', 'Number of Resources']


class ResourceMonitor:
    def __init__(self):
        self.resources_deployed = {}
        self.resources_deployed_details = {}
        self.df_dict = {}
        self.summary_df = pd.DataFrame(columns=RESOURCE_HEADERS)
        self.df_dict["Resource Information"] = self.summary_df
        self.unapproved_resources = []
        self.unapproved_resources_details = []
        self.differing_resource = []
        self.unapproved_resources_excel = []

    def collect_resources_deployed(self, resource_type='deployments'):
        log.info('fetching %s deployed in EO', resource_type)
        conn = get_VMVNFM_host_connection(SIT.get_is_ccd(SIT))
        self.resources_deployed[resource_type] = {}

        for namespace in NAMESPACES:
            command = f"kubectl get {resource_type} -n {namespace} | awk 'NR>1 {{print $1}}'"
            log.info('Executing command: %s', command)
            Report_file.add_line('command: ' + command)
            _, stdout, _ = conn.exec_command(command)
            out = stdout.read().decode('utf-8')
            Report_file.add_line('output: ' + str(out))
            num_resource = len(out.splitlines())
            log.info('Command output:\n%s', out)
            log.info('Number of %s in %s: %s', resource_type, namespace, num_resource)

            if out and 'No resources found' not in out:
                resource_list = out.strip().split('\n')
            else:
                log.info('No %s found for namespace %s', resource_type, namespace)
                resource_list = []

            temp_df = pd.DataFrame([{
                'Namespace': namespace,
                'Resource Type': resource_type,
                'Number of Resources': num_resource
            }])
            self.summary_df = pd.concat([self.summary_df, temp_df], ignore_index=True)
            self.df_dict["Resource Information"] = self.summary_df

            resource_df = pd.DataFrame(resource_list, columns=['Resource'])
            resource_df['Namespace'] = namespace
            resource_df['Resource Type'] = resource_type
            temp_df = pd.DataFrame([{
                'Resource': 'Total Number of Resources',
                'Namespace': '',
                'Resource Type': num_resource
            }])
            resource_df = pd.concat([resource_df, temp_df], ignore_index=True)
            self.df_dict[f'{resource_type}_{namespace}'] = resource_df
            self.resources_deployed.setdefault(resource_type, {})[namespace] = resource_list

        with pd.ExcelWriter('resources.xlsx', engine='xlsxwriter') as writer:
            for sheet_name, df in self.df_dict.items():
                df.to_excel(writer, sheet_name=sheet_name, index=False)

    def collect_resources_pods(self, resource_type):
        resources = self.resources_deployed
        log.info('Collecting pods of approved resources')
        conn = get_VMVNFM_host_connection(SIT.get_is_ccd(SIT))
        for namespace, _ in resources[resource_type].items():
            self.resources_deployed_details[resource_type][namespace] = {}
            for dep_name in resources[resource_type][namespace]:
                resource_pods_command = f"kubectl describe {resource_type} {dep_name} -n" \
                                        f"{namespace} | grep 'Pod Name:' | awk '{{print $3}}'"
                Report_file.add_line('Collect Resources Pods command:' + resource_pods_command)
                _, resource_pod_stdout, _ = conn.exec_command(resource_pods_command)
                resource_pod_out = resource_pod_stdout.read().decode('utf-8').strip().split("\n")
                Report_file.add_line(resource_pod_out)
                self.resources_deployed_details[resource_type][namespace].update(
                    {dep_name: {"data": resource_pod_out}})

    def collect_details_of_resources(self):
        log.info('Collecting details of approved resources')
        conn = get_VMVNFM_host_connection(SIT.get_is_ccd(SIT))

        resources = self.resources_deployed
        for resource_type in resources:
            self.resources_deployed_details[resource_type] = {}
            if resource_type not in RESOURCE_TYPES:
                continue
            if resource_type == "rediscluster":
                self.collect_resources_pods("rediscluster")
            else:
                for namespace, namespace_json in resources[resource_type].items():
                    self.resources_deployed_details[resource_type][namespace] = {}
                    for dep_name in resources[resource_type][namespace]:
                        if resource_type == "pvc":
                            pvc_capacity_command = f"kubectl describe pvc {dep_name} -n {namespace} | grep 'Capacity:' | awk '{{print $2}}'"
                            Report_file.add_line('Collect PVC Capacity command: ' + pvc_capacity_command)
                            _, pvc_capacity_stdout, _ = conn.exec_command(pvc_capacity_command)
                            pvc_capacity = pvc_capacity_stdout.read().decode('utf-8').strip()
                            Report_file.add_line('PVC Capacity: ' + pvc_capacity)
                            self.resources_deployed_details[resource_type][namespace].update({
                                dep_name: {"capacity": pvc_capacity}
                            })
                            log.info('PVC: %s. PVC Capacity: %s', dep_name, pvc_capacity)
                        else:
                            resource_replica_command = f"kubectl describe {resource_type} {dep_name} -n " \
                                                       f"{namespace} | grep 'Replicas:' | awk '{{print $2}}'"
                            Report_file.add_line('Collect Resources Replica command: ' + resource_replica_command)
                            _, resource_rep_stdout, _ = conn.exec_command(resource_replica_command)
                            resource_rep_out = resource_rep_stdout.read().decode('utf-8')
                            Report_file.add_line('number of replica: ' + resource_rep_out)
                            if resource_type == "cronjobs":
                                json_path = "'{range .spec.jobTemplate.spec.template.spec." \
                                            "containers[*]}\"{.name}\": {.resources},{end}'"
                            else:
                                json_path = "'{range .spec.template.spec.containers[*]}\"{.name}\": {.resources},{end}'"
                            resource_info_command = "kubectl get %s %s -n %s -o=jsonpath=%s" % \
                                                    (resource_type, dep_name, namespace, json_path)
                            Report_file.add_line('Collect Resources Details command: ' + resource_info_command)
                            _, resource_info_stdout, _ = conn.exec_command(resource_info_command)
                            resource_info_out = resource_info_stdout.read().decode('utf-8')
                            Report_file.add_line(resource_info_out)
                            resource_info_out = json.loads("{ %s }" % resource_info_out.rstrip(","))
                            self.resources_deployed_details[resource_type][namespace].update(
                                {dep_name: {"data": resource_info_out, "replica_count": resource_rep_out.strip()}})
                            log.info('Resource details: %s. Replica count: %s', resource_info_out, resource_rep_out)

        # Generate CSV files for resource details
        log.info("Generating CSV files")
        self.generate_resource_details_csv()

    def check_for_unapproved_resources_details(self):
        log.info('Finding unapproved resources details')
        with open('com_ericsson_do_auto_integration_files/eo_resources_details_baseline.json',
                  encoding='utf-8') as resource_file:
            approved_resources = json.load(resource_file)
        log.info('Compare resources details deployed against the initial baseline')
        deployed_details = self.resources_deployed_details
        for resource_type in approved_resources:
            for namespace in approved_resources[resource_type]:
                if namespace == "eo-namespace":
                    namespace_text = "eo-deploy"
                else:
                    namespace_text = "cm-deploy"

                for dep_name, value in deployed_details[resource_type][namespace_text].items():
                    dep_data_compare = value
                    if dep_name not in approved_resources[resource_type][namespace]:
                        in_baseline = "No"
                        dep_data_approved = "Not in baseline"
                    else:
                        in_baseline = "Yes"
                        dep_data_approved = approved_resources[resource_type][namespace][dep_name]

                    if resource_type == "rediscluster" and isinstance(dep_data_approved,
                                                                      dict) and "data" in dep_data_approved:
                        pods_approved = len(dep_data_approved.get("data", []))
                        pods_deployed = len(dep_data_compare.get("data", []))
                        if pods_approved != pods_deployed:
                            self.unapproved_resources_details.append(
                                f"Deployed pods count for {dep_name}: {pods_deployed}")
                            self.unapproved_resources_details.append(
                                f"Approved pods count for {dep_name}: {pods_approved}")
                            self.unapproved_resources.extend([(resource_type, namespace_text, dep_name, in_baseline)])
                            self.collect_differing_details(resource_type, namespace, dep_name)
                    else:
                        if dep_data_approved != dep_data_compare:
                            self.unapproved_resources_details.append(
                                f"Deployed resource details: {dep_data_compare} \n")
                            self.unapproved_resources_details.append(f"Approved resource details: {dep_data_approved}")
                            self.unapproved_resources.extend([(resource_type, namespace_text, dep_name, in_baseline)])
                            if in_baseline == "Yes":
                                self.collect_differing_details(resource_type, namespace, dep_name)
                            else:
                                if dep_data_approved == "Not in baseline":
                                    details = [resource_type, namespace_text, dep_name, value]
                                    self.unapproved_resources_excel.append(details)

        if self.unapproved_resources:
            log.error('Unapproved resources found')
            Common_utilities.tabulate_data(self.unapproved_resources,
                                           headers=['RESOURCE_TYPE', 'NAMESPACE', 'RESOURCE_NAME', 'IN_BASELINE'])
            for details in self.unapproved_resources_details:
                log.info(details)
            self.generate_details_excel()
            assert False
        log.info('No unapproved resources details found')

    def generate_resource_details_csv(self):
        csv_files = []
        for resource_type, resource_type_data in self.resources_deployed_details.items():
            csv_filename = f"{resource_type}.csv"
            with open(csv_filename, mode='w', newline='') as file:
                writer = csv.writer(file)

                if resource_type == "rediscluster":
                    writer.writerow([resource_type.capitalize(), "Namespace", "Pods"])
                elif resource_type == "pvc":
                    writer.writerow([resource_type.capitalize(), "Namespace", "Resource Name", "Capacity"])
                else:
                    writer.writerow(
                        [resource_type.capitalize(), "Namespace", "Container", "Replica Count", "CPU Limits",
                         "Memory Limits", "Ephemeral-storage Limits", "CPU Requests", "Memory Requests",
                         "Ephemeral-storage Requests"])

                for namespace, resource_type_data_dict in resource_type_data.items():
                    for dep_name, dep_data in resource_type_data_dict.items():
                        if resource_type == "rediscluster":
                            writer.writerow([dep_name, namespace, ', '.join(dep_data["data"])])
                        elif resource_type == "pvc":
                            capacity = dep_data.get("capacity", "N/A")
                            writer.writerow([dep_name, namespace, dep_name, capacity])
                        else:
                            replicas = dep_data.get("replica_count", "N/A")
                            for container_name, container_info in dep_data.get("data", {}).items():
                                limits = container_info.get("limits", {})
                                requests = container_info.get("requests", {})
                                writer.writerow([
                                    dep_name, namespace, container_name, replicas,
                                    limits.get("cpu", "N/A"), limits.get("memory", "N/A"),
                                    limits.get("ephemeral-storage", "N/A"),
                                    requests.get("cpu", "N/A"), requests.get("memory", "N/A"),
                                    requests.get("ephemeral-storage", "N/A")
                                ])
            csv_files.append({"file": csv_filename, "sheet_name": resource_type})
            log.info("CSV file %s has been generated successfully.", csv_filename)

        self.generate_excel_from_csvs(csv_files)

    def generate_excel_from_csvs(self, csv_files):
        excel_file = "resources_details.xlsx"
        with pd.ExcelWriter(excel_file, engine='xlsxwriter') as writer:
            for csv_info in csv_files:
                df = pd.read_csv(csv_info["file"])
                df.to_excel(writer, sheet_name=csv_info["sheet_name"], index=False)
        log.info("Excel file %s created with multiple sheets.", excel_file)

    def collect_differing_details(self, resource_type, namespace, dep_name):
        with open('com_ericsson_do_auto_integration_files/eo_resources_details_baseline.json',
                  encoding='utf-8') as resource_file:
            approved_resources = json.load(resource_file)
        if namespace == "eo-namespace":
            namespace_text = "eo-deploy"
        else:
            namespace_text = "cm-deploy"
        dep_data_approved = ExtendedDict(
            approved_resources.get(resource_type, {}).get(namespace, {}).get(dep_name, {}))
        dep_data_deployed = ExtendedDict(
            self.resources_deployed_details.get(resource_type, {}).get(namespace_text, {}).get(dep_name, {}))

        if resource_type == "rediscluster":
            if "data" in dep_data_approved and "data" in dep_data_deployed:
                details = [resource_type, namespace_text, dep_name, "None", "Pods number",
                           len(dep_data_deployed.get("data")),
                           len(dep_data_approved.get("data"))]
                self.differing_resource.append(details)
                return

        elif resource_type == "pvc":
            approved_capacity = dep_data_approved.get('capacity', 'N/A')
            deployed_capacity = dep_data_deployed.get('capacity', 'N/A')
            if (resource_type, namespace_text, dep_name, "None", "Capacity", deployed_capacity,
                approved_capacity) not in self.differing_resource:
                if approved_capacity != deployed_capacity and approved_capacity != "N/A":
                    details = [
                        resource_type, namespace_text, dep_name, "None", "Capacity",
                        deployed_capacity, approved_capacity
                    ]
                    self.differing_resource.append(details)
                    log.info("PVC capacity mismatch for %s - Deployed: %s, Approved: %s",
                             dep_name, deployed_capacity, approved_capacity)

        else:
            if "data" in dep_data_approved and "data" in dep_data_deployed:
                for container_name in dep_data_approved["data"]:
                    container_info_approved = dep_data_approved["data"].get(container_name, {})
                    container_info = dep_data_deployed["data"].get(container_name, {})

                    if not container_info:
                        log.info(f"Missing container details in deployed data: %s", container_name)
                        self.differing_resource.append(
                            [resource_type, namespace_text, dep_name, container_name,
                             "Container in baseline, but missing in deployed", "N/A", "N/A"])
                        continue

                    limits_approved = container_info_approved.get("limits", {})
                    requests_approved = container_info_approved.get("requests", {})
                    limits_deployed = container_info.get("limits", {})
                    requests_deployed = container_info.get("requests", {})
                    if limits_deployed.get("cpu", {}) != limits_approved.get("cpu", {}):
                        details = [resource_type, namespace_text, dep_name, container_name, "CPU Limits",
                                   limits_deployed.get("cpu"), limits_approved.get("cpu")]
                        self.differing_resource.append(details)

                    if limits_deployed.get("memory", {}) != limits_approved.get("memory", {}):
                        details = [resource_type, namespace_text, dep_name, container_name, "Memory Limits",
                                   limits_deployed.get("memory"), limits_approved.get("memory")]
                        self.differing_resource.append(details)

                    if limits_deployed.get("ephemeral-storage", {}) != limits_approved.get("ephemeral-storage", {}):
                        details = [resource_type, namespace_text, dep_name, container_name, "Ephemeral-storage Limits",
                                   limits_deployed.get("ephemeral-storage"), limits_approved.get("ephemeral-storage")]
                        self.differing_resource.append(details)

                    if requests_deployed.get("cpu", {}) != requests_approved.get("cpu", {}):
                        details = [resource_type, namespace_text, dep_name, container_name, "CPU Requests",
                                   requests_deployed.get("cpu"), requests_approved.get("cpu")]
                        self.differing_resource.append(details)

                    if requests_deployed.get("memory", {}) != requests_approved.get("memory", {}):
                        details = [resource_type, namespace_text, dep_name, container_name, "Memory Requests",
                                   requests_deployed.get("memory"), requests_approved.get("memory")]
                        self.differing_resource.append(details)

                    if requests_deployed.get("ephemeral-storage", {}) != requests_approved.get("ephemeral-storage", {}):
                        details = [resource_type, namespace_text, dep_name, container_name,
                                   "Ephemeral-storage Requests",
                                   requests_deployed.get("ephemeral-storage"),
                                   requests_approved.get("ephemeral-storage")]
                        self.differing_resource.append(details)
                if dep_data_deployed.get("replica_count") != dep_data_approved.get("replica_count"):
                    details = [resource_type, namespace_text, dep_name, "None", "Replica count",
                               dep_data_deployed.get("replica_count"), dep_data_approved.get("replica_count")]
                    self.differing_resource.append(details)
            else:
                log.info("No 'data' key found for resource %s of type %s.", dep_name, resource_type)

    def generate_details_excel(self):
        differing_details_df = pd.DataFrame(self.differing_resource,
                                            columns=["Resource_Type", "Namespace", "Deployed_Resource_Name",
                                                     "Container", "Differing_Details", "Deployed_Value",
                                                     "Approved_Value"])
        unapproved_resources_df = pd.DataFrame(self.unapproved_resources_excel,
                                               columns=["Resource_Type", "Namespace", "Deployed_Resource_Name", "Deployed Value"])

        with pd.ExcelWriter('differing_resource_details.xlsx', engine='xlsxwriter') as writer:
            differing_details_df.to_excel(writer, sheet_name='Differing_Details', index=False)
            unapproved_resources_df.to_excel(writer, sheet_name='Unapproved_Resources', index=False)
        log.info("Excel file 'differing_resource_details.xlsx' generated successfully.")


class ExtendedDict(dict):
    def get_all_resource_keys(self):
        """A method to get all keys from a nested dictionary."""
        keys = list(self.keys())
        for key, value in self.items():
            if isinstance(value, dict):
                nested_dict = ExtendedDict(value)
                keys.extend(nested_dict.get_all_resource_keys())
        return keys
