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
"""
Created on 22 Aug 2022
@author: zsheroo
"""

import argparse
import requests
from requests.auth import HTTPBasicAuth

from com_ericsson_do_auto_integration_utilities.Logger import Logger

Logger.get_logger("urllib3").propagate = False
log = Logger.get_logger("update_dit_schema_version.py")


def requests_error_handling(func):
    """Decorator method for generic error handling for api requests methods"""
    def inner_function(*arguments):
        try:
            return func(*arguments)
        except requests.exceptions.HTTPError as errh:
            log.error("Http Error: %s", str(errh))
            assert False
        except requests.exceptions.ConnectionError as errc:
            log.error("Error Connecting: %s", str(errc))
            assert False
        except requests.exceptions.Timeout as errt:
            log.error("Timeout Error: %s", str(errt))
            assert False
        except requests.exceptions.RequestException as err:
            log.error("OOps: Something went wrong: %s", str(err))
            assert False
        except Exception as error:
            log.error("%s failed: %s", str(func.__name__), str(error))
            assert False
    return inner_function


@requests_error_handling
def get_schema_id(schema):
    """
    schema: Example do_automation-19.2.15
    Returns: schema id
    """
    schema_name, schema_version = schema.split("-")
    url = f"https://atvdit.athtem.eei.ericsson.se/api/schemas?q=name={schema_name}&" \
          f"fields=_id,name,version,created_at"
    log.info("Fetch schemas with name %s : %s", schema_name, url)
    schema_collection = requests.get(url, data={})
    schema_collection.raise_for_status()
    schema_collection = schema_collection.json()
    log.info("list of schema with name %s : %s", schema_name, str(schema_collection))
    schema_id = ""
    for element in schema_collection:
        if element["name"] == schema_name and element["version"] == schema_version:
            schema_id = element["_id"]
            log.info("schema id of %s is %s", schema, schema_id)
            return schema_id
    if not schema_id:
        log.error("invalid schema, unable to fetch schema id for %s", schema)
        assert False


@requests_error_handling
def update_schema_version(present_schema, new_schema, functional_user_pass):
    """
    Updates all the DITs listed under the present schema version to new schema version
    present_schema: Example do_automation-19.2.15
    new_schema: Example do_automation-19.2.16
    functional_user_pass: functional user password for the username doadm100(Jenkins slave cred)
    """
    log.info("Start fetching schema id")
    present_schema_id = get_schema_id(present_schema)
    new_schema_id = get_schema_id(new_schema)
    present_schema_url = (
        "https://atvdit.athtem.eei.ericsson.se/api/documents?fields=_id,name&q=schema_id%3D{}".format(
            present_schema_id))
    log.info("Start fetching details of present schema, url: %s", present_schema_url)
    schema_details = requests.get(present_schema_url)
    schema_details.raise_for_status()
    dit_list = schema_details.json()
    log.info("DITs listed under present schema version %s are: %s", present_schema, str(dit_list))
    if not dit_list:
        log.info("There is no DIT's listed under present schema version %s", present_schema)
    else:
        log.info("Start updating schema version for all DIT from %s to %s", present_schema, new_schema)
        count = 0
        for dit in dit_list:
            url = "https://atvdit.athtem.eei.ericsson.se/api/documents/{}".format(dit["_id"])
            put_req = requests.put(url, data={"schema_id": new_schema_id},
                                   auth=HTTPBasicAuth("doadm100", functional_user_pass))
            put_req.raise_for_status()
            count += 1
            log.info("%s. Schema version of dit %s is updated to %s", str(count), dit["name"], new_schema)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("present_schema", help="existing schema version of dit")
    parser.add_argument("new_schema", help="new schema version to which dit needs to be updated")
    parser.add_argument("functional_user_pass", help="Jenkins slave password for user doadm100")
    args = parser.parse_args()
    update_schema_version(args.present_schema, args.new_schema, args.functional_user_pass)
