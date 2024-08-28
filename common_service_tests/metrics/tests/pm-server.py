import sys
import requests
import pytest
from com_ericsson_do_auto_integration_utilities.Report_file import Report_file

#### command for running this is pytest pm-server.py --url http://<insert pm-server url>

def getUpMetric(url,PARAMS):

    params = (
        ('query', PARAMS),
    )
    response = requests.get(
        url + '/metrics/viewer/api/v1/query', params=params)
    try:
        Report_file.add_line('response: ' + str(response.json()))
        json_data = response.json()['data']['result'][0]['metric']['app']
        return json_data
    except requests.exceptions.RequestException as err:
        print ("Metric not found",err)
        return err

# so to run only so use -m so in the command line

@pytest.mark.so
@pytest.mark.eo
def test_eric_eo_api_gateway(url):
    """tests availability of eric eo api gateway endpoind."""


    if getUpMetric(url, 'up{app="eric-eo-api-gateway"}') is True:
        print("Passed")
    else:
        print("eric-eo-api-gateway not found")
        sys.exit(1)
