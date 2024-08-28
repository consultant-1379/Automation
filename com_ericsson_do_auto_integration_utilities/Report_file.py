#pylint: disable=C0103,C0103
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
Created on 24 Aug 2018

@author: emaidns
'''
import shutil
import os


class Report_file():
    """
    A class to update report_file
    """
    if os.path.exists('report_file.txt'):
        shutil.move('report_file.txt', 'report_file_backup.txt')

    @staticmethod
    def add_mesg(step, details, data):
        """
        Add message to report file
        @param step:
        @param details:
        @param data:
        """
        with open('report_file.txt', 'a+') as file:
            file.write('**************************************'
                       '*********************************************\n\n')
            file.write(
                "{0} : {1} :\n\n {2}\n\n".format(step, details, data)

            )


    @staticmethod
    def add_line(line):
        """
        Add line to message file
        @param line:
        """
        with open('report_file.txt', 'a+') as file:
            file.write('***************************************'
                       '********************************************\n\n')
            file.write(
                "{0} \n\n".format(line)

            )
