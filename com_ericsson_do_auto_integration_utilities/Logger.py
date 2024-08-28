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
'''
Created on 10 Aug 2018

@author: emaidns
'''
import logging
import os
import shutil
import getpass


class Logger(object):
    # set up logging to file - see previous section for more details
    if os.path.exists('log.txt'):
        shutil.move('log.txt', 'log_backup.txt')

    logging.basicConfig(level=logging.DEBUG,
                        format='%(asctime)s  %(levelname)-8s ' + getpass.getuser() + ' %(name)-12s   %(message)s',
                        datefmt='%m-%d-%y %H:%M:%S',
                        filename='log.txt'
                        )

    # define a Handler which writes INFO messages or higher to the sys.stderr
    console = logging.StreamHandler()
    console.setLevel(logging.INFO)

    # set a format which is simpler for console use
    formatter = logging.Formatter(
        '%(asctime)s : %(levelname)-8s : ' + getpass.getuser() + ' : %(name)-12s :%(lineno)d : %(message)s')

    # tell the handler to use this format
    console.setFormatter(formatter)

    # add the handler to the root logger
    logging.getLogger('').addHandler(console)

    # Now, we can log to the root logger, or any other logger. First the root...

    # Now, define a couple of other loggers which might represent areas in your
    # application:


    @staticmethod
    def get_logger(name):
        return logging.getLogger(name)
