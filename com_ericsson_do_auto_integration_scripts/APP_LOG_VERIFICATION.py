from com_ericsson_do_auto_integration_utilities.Logger import Logger
from com_ericsson_do_auto_integration_utilities.Server_details import Server_details
import requests

log = Logger.get_logger('APP_LOG_VERIFICATION.py')


def app_log_hits_verification(app, request_url):
    try:

        log.info('Start verifying logs hit for: %s', app)
        log.info('Request url: %s', request_url)

        response = requests.get(request_url)
        log.info('response: %s', str(response))

        content = response.json()
        log.info('response data : %s', str(content))

        total_hits = content['hits']['total']
        log.info('total hits: %s', str(total_hits))

        if total_hits == 0:
            log.error('Number of hits "0" , Test case failed !!!')
            assert False
        else:
            log.info('Number of hits %s, Test case Successful !!! ', total_hits)

        log.info('Finished verifying logs hit for %s', app)

    except Exception as e:
        log.info(f'Error verifying logs hit for %s. %s ', app, str(e))
        assert False


def evnfm_log_verify():
    log_verify_host_url = Server_details.get_log_verification_host_url(Server_details)

    if 'http' not in log_verify_host_url:
        request_url = f'http://{log_verify_host_url}/_all/_search?pretty=true&q=path:"/api/lcm/v2/cluster"'
    else:
        request_url = f'{log_verify_host_url}/_all/_search?pretty=true&q=path:"/api/lcm/v2/cluster"'

    app_log_hits_verification('EVNFM', request_url)


def so_logviewer_log_verify():
    log_verify_host_url = Server_details.get_log_verification_host_url(Server_details)

    if 'http' not in log_verify_host_url:
        request_url = f'http://{log_verify_host_url}/_all/_search?pretty=true&q="username=so_logviewer"'
    else:
        request_url = f'{log_verify_host_url}/_all/_search?pretty=true&q="username=so_logviewer"'

    app_log_hits_verification('SO_LOGVIEWER', request_url)


def so_subsystem_log_verify():
    log_verify_host_url = Server_details.get_log_verification_host_url(Server_details)

    if 'http' not in log_verify_host_url:
        request_url = f'http://{log_verify_host_url}/_all/_search?pretty=true&q=message:"subsystemType=SubsystemType"'
    else:
        request_url = f'{log_verify_host_url}/_all/_search?pretty=true&q=message:"subsystemType=SubsystemType"'

    app_log_hits_verification('SO_SUBSYSTEM', request_url)


def wano_log_verify():
    log_verify_host_url = Server_details.get_log_verification_host_url(Server_details)

    if 'http' not in log_verify_host_url:
        request_url = f'http://{log_verify_host_url}/_all/_search?pretty=true&q="/wano-nbi/wano/v1.1/services"'
    else:
        request_url = f'{log_verify_host_url}/_all/_search?pretty=true&q="/wano-nbi/wano/v1.1/services"'

    app_log_hits_verification('WANO', request_url)
