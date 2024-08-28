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
from com_ericsson_do_auto_integration_utilities.Error_handler import handle_stderr
from com_ericsson_do_auto_integration_utilities.Report_file import Report_file
from com_ericsson_do_auto_integration_utilities.Logger import Logger
from com_ericsson_do_auto_integration_scripts.VM_VNFM_OPERATIONS import get_director_server_connection
from com_ericsson_do_auto_integration_initilization.SIT_initialization import SIT_initialization
from com_ericsson_do_auto_integration_utilities.ServerConnection import ServerConnection
from com_ericsson_do_auto_integration_utilities.Server_details import Server_details
from com_ericsson_do_auto_integration_model.SIT import SIT
import distutils.util

log = Logger.get_logger('CCD_POST_INSTALL.py')


def distribute_egad_certs():
    try:
        log.info('start distributing EGAD certificates ')
        Report_file.add_line('start distributing EGAD certificates')
        sit_data = SIT_initialization.get_model_objects(SIT_initialization, 'SIT')
        registry_name = sit_data._SIT__egadcert_registery_name

        # here in vnf_type we pass boolean value for director connection
        # if true the director connection is made to CCD1_VM_VNFM_DIRECTOR
        # else VM_VNFM_DIRECTOR
        ccd1_connection = sit_data._SIT__vnf_type
        ccd1_connection = bool(distutils.util.strtobool(ccd1_connection))
        director_connection = get_director_server_connection(ccd1_connection)

        command = 'rm -rf EricssonCerts'
        Report_file.add_line('remove directory command - ' + command)
        stdin, stdout, stderr = director_connection.exec_command(command)

        dir_name = 'EricssonCerts'

        ServerConnection.put_folder_scp(director_connection, r'com_ericsson_do_auto_integration_files/' + dir_name, '/home/eccd/')

        command = 'chmod 777 EricssonCerts/distributeEGADRoot.sh'
        Report_file.add_line('chmod permission command - ' + command)
        stdin, stdout, stderr = director_connection.exec_command(command)

        command = f'./EricssonCerts/distributeEGADRoot.sh {registry_name}'
        Report_file.add_line('certificate command - ' + command)
        stdin, stdout, stderr = director_connection.exec_command(command)
        command_output = str(stdout.read())

        if 'FAIL' in command_output:
            Report_file.add_line('script failed - output-' + command_output)
            assert False

        Report_file.add_line('output-' + command_output)

    except Exception as e:

        log.error('Error  distributing egad certificates %s', str(e))
        Report_file.add_line('Error  distributing egad certificates' + str(e))
        assert False
    finally:
        director_connection.close()


def update_authorize_keys():
    try:
        log.info('start updating authorize keys ')
        # changed ccd1_connection value with the new parameter of DIT SM-127194
        ccd1_connection = SIT.get_is_ccd(SIT)
        director_connection = get_director_server_connection(ccd1_connection)
        authorize_file_path = '/home/eccd/.ssh/authorized_keys'

        log.info('Getting authorize file to local to update ')
        ServerConnection.get_file_sftp(director_connection, authorize_file_path, 'authorized_keys')

        log.info('Updating authorized_keys file ')

        updated_content = '\nssh-rsa AAAAB3NzaC1yc2EAAAADAQABAAACAQCp44d/JJcN89zM1QmkkddtmEbBtW8T/0ODa9S7fIWUuI8whl4OffXewJXnvPilq0ogSVb/4MIbpPvfVs3ga53vwEkef119oNnr0tjKwH+Rq8sgB7uuw9V8CaRkQzFRuQUKxHTZqYUV1rmyrp+8wjDNN1Qcq3C+/OdgKZkQf7nvth7WD+TErezum0CZGqj4mZA5lEdQ5PjpWa9L+gCPVVKRcyiZTLBEAnxhk3AC8j8aidW9T334uqnHAMgbHr5IuhSIEUxo2DNt65++acppolEnBsx8EIImn39H/07KhOSoWRm0uOGdB4wD9Vockdq3volcVPe/Wtzgo2u4EibUh+7Z5CId3KYJPjQvjrqXgIob73qlkaJOuzVDpItI06zulxhhwyzj5wir8JM8xo1roFyf4AFj7Zzu8CIdXWhKzDMlUFY3g9OIdNj9jJjCj/f2lC1tl11DnEGTL26UYfrtJWpY6fua81glsYK8aIkJaK++YTVU+eIx3CMRlI5+cz6pXu8JUp/MsmOEjxKkiPs6Ba7CuJbr08/RcNX6D1XGQbWRS9cSdjS1f/546mybVbFhhcH4lkcHLHSRsKM1riNti9lP211I8zhL+uz8htOGt14ezQwimLugfN4EG8E17ddFBETOlhgcJctRk2QVq98O50eRO6CALImaC5Y1iu+19doFyw== terraform\nssh-rsa AAAAB3NzaC1yc2EAAAADAQABAAACAQCg+RVD7IiKz97ixl78zgX+6FmXIjrSnD4hLW6rTWT7yBL2452Bo5Me4nHE05vybUt4EOM+VDJRyDKvokDJuO8ZCecE9i7nH0Wj7q0ycJUWSSrDr3H2PZxC3eccDmx62d0Bb5whWhlztxtaqTl4I2hFfCRFdoEhmh1inKuc6P9jH4eZ6HxiZYMrc9c+otF+FdzjVKrCVQIjSKEePBAncV8cM7QA9uyraN/vciIWfYhuVJtJEDprYD7SrjaV11LBuYMgsH3AOefsH5wCuYWRVT7Vg0Xhtrs2CsPAYWDIeApdPTakfo+bIXwQkcBElKW7d+xVxMBMwkEqNWaHEH9X7NObYX1NRH2OeVQXIcILkXQqya+1YzShccLhHgYh2doMc+mnNSQlM8eiD3UIsW/htaTyZfnEsso9TMp2b2kOA5D7xQ6jR80Ah9+QJRkYRHi1KfUKE4BWRu7FZM3gN00gtH8FCAMBWpHhJai/wnt5Ra+7InmvpLqofRofKW54vLqkTk2/KNcH0sxWs7bCtcNQAckOi8zHzk/r6C3V/nwajz76lAsYRse89kDsixUhiJhATEbhqfMfGR7goWb1I6qdrI8dXh8uFWhW1n3+1zDInp3CRiOcKf3WJys6o8RuCfcC9U089KY70dxYyDFScnxSZBDrFtRq79CpOw/TSz68Kzu2lQ== Service Orchestration Automation\nssh-rsa AAAAB3NzaC1yc2EAAAADAQABAAABAQC9TKcg6FFJBRDfY5A+D6s8BWxSk48bzZSaqbtCR/Apc+oqMSBmKHE4qEXu+mEGtfbpEkdDTISlasv/sDPfJxqbMHwUnwnMhlSnAkxR9Dcme1xZV7U04GBOBFhMcKBxfUbyzmlLH1tk6CBdJkndhb0XgKa/6hCS6au7tTjqsr9g2dWUGQQjR4LjQwt8m+XnHH2b5NNtRYVfpyH4V52i4xpAd4egbh6Y48pZM4yC4Cc621vhM+sETQhMBO0e7s6G0C2/JGT++P2kGHPRODUEh2iTkRF+U9N36bdGCTM54It4m5kld6oMTi/mlRWzXmfaA3AQW1bGiAA1rQ7Gx5EDXjRN root@atvts3430.athtem.eei.ericsson.se'
        file_name = 'authorized_keys'
        with open(file_name, "a") as myfile:
            myfile.write(updated_content)

        log.info('Transferring authorized_keys file to director server ip ')
        ServerConnection.put_file_sftp(director_connection, 'authorized_keys', r'/home/eccd/.ssh/authorized_keys')

        Report_file.add_line('authorize_keys file updated')

    except Exception as e:

        log.error('Error updating authorize keys %s', str(e))
        Report_file.add_line('Error updating authorize keys' + str(e))
        assert False
    finally:
        director_connection.close()


def distribute_egad_certs_cn():
    director_connection = None
    try:
        log.info('Start distributing EGAD certificates')
        ccd1_connection = SIT.get_is_ccd(SIT)
        director_connection = get_director_server_connection(ccd1_connection)
        check_if_egad_cert_exists(director_connection, 'Ericsson_IT_Issuing_CA-03.crt')
        check_if_egad_cert_exists(director_connection, 'EGADRootCA.crt')
        check_if_egad_cert_exists(director_connection, 'EGADIssuingCA3.crt')
        cmds_list = ["kubectl get nodes -o wide | grep worker | awk {'print $6'} > workers",
                     "for n in $(cat workers); do scp -o StrictHostKeyChecking=no EGAD* Ericsson_IT_Issuing_CA-03.crt $n:;done",
                     "for n in $(cat workers); do ssh $n 'sudo cp EGAD* Ericsson_IT_Issuing_CA-03.crt /etc/ssl/certs/';done",
                     "for n in $(cat workers); do ssh $n 'sudo systemctl restart containerd';done"]
        command = 'rm -rf workers'
        stdin, stdout, stderr = director_connection.exec_command(command)
        for cmd in cmds_list:
            log.info("certificate command - %s", cmd)
            stdin, stdout, stderr = director_connection.exec_command(cmd)
            log.info("certificate command output - %s", stdout.read().decode("utf-8"))
            handle_stderr(stderr, log)
    except Exception as e:
        log.error('Error  distributing egad certificates %s', str(e))
        assert False
    finally:
        if director_connection:
            director_connection.close()


def check_if_egad_cert_exists(director_connection, cert_file):
    """This method is to check if an EGAD cert exists on server and transfer if not"""
    try:
        cmd = f'[ -f {cert_file} ] && echo "Found" || echo "Not found"'
        _, stdout, _ = director_connection.exec_command(cmd)
        output = (stdout.read().decode("utf-8"))

        if 'Found' in output:
            log.info('EGAD Cert %s is present in CCD', cert_file)
        else:
            log.info('EGAD Cert %s is not present, transferring EGAD certs from blade', cert_file)
            ecm_server_ip, ecm_username, ecm_password = Server_details.ecm_host_blade_details(Server_details)
            blade_server_connection = ServerConnection.get_connection(ecm_server_ip, ecm_username, ecm_password)
            vm_vnfm_director_ip, vm_vnfm_director_username = Server_details.vm_vnfm_director_details(Server_details)
            pem_file_path = 'eccd-2-3.pem'
            ServerConnection.transfer_files_with_an_encrypted_pem_file(blade_server_connection, pem_file_path,
                                                                       cert_file,
                                                                       vm_vnfm_director_username,
                                                                       vm_vnfm_director_ip, '')
    except Exception as e:
        log.error('Error checking egad certificates %s', str(e))
        assert False
