from tempfile import mkstemp
from shutil import move
from os import fdopen, remove
import paramiko
import os
from com_ericsson_do_auto_integration_utilities.Error_handler import handle_stderr
from com_ericsson_do_auto_integration_utilities.Logger import Logger

log = Logger.get_logger('file_utils.py')


def create_property_file(filename, key, value):
    """
    This method is used to create file and
    add key=value as a line in file
    """
    try:
        log.info(f"updating file: {filename} with key: {key} and value: {value}")
        with open(filename, 'w+') as f:
            f.write('%s=%s\n' % (key, value))

    except Exception as e:
        log.error(f'Failed to update the details in file name {filename} for key {key} and value {value}')
        assert False


def set_value_in_property_file(filename, key, value):
    """
    This method is used to append the key=value as a line in file
    """
    try:
        with open(filename, 'a') as f:
            f.write('%s=%s\n' % (key, value))

    except Exception as e:
        log.error(f'Failed to update the details in file name {filename} for key {key} and value {value}')
        assert False


def replace(file_path, pattern, subst):
    """
    This method is used to search for the given pattern and replace it with
    given substitute in each line of file .
    """
    fh, abs_path = mkstemp()
    with fdopen(fh, 'w') as new_file:
        with open(file_path) as old_file:
            for line in old_file:
                new_file.write(line.replace(pattern, subst))

    remove(file_path)
    move(abs_path, file_path)


def create_temp_dir(connection, command='mktemp -d'):
    """Creates temporary directory"""
    log.info('creating temp folder with command : %s', command)
    stdin, stdout, stderr = connection.exec_command(command)
    tmp_dir_path = stdout.read().decode('utf-8')
    log.info('created tmp directory path : %s ', tmp_dir_path)
    return tmp_dir_path


def del_dir(connection, dir_name):
    """Deletes directory"""
    stdin, stdout, stderr = connection.exec_command(f'/bin/rm -rf {dir_name}')
    return stderr


class MySFTPClient(paramiko.SFTPClient):
    def put_dir(self, source, target):
        ''' Uploads the contents of the source directory to the target path. The
            target directory needs to exists. All subdirectories in source are
            created under target.
        '''
        for item in os.listdir(source):
            if os.path.isfile(os.path.join(source, item)):
                self.put(os.path.join(source, item), '%s/%s' % (target, item))
            else:
                self.mkdir('%s/%s' % (target, item), ignore_existing=True)
                self.put_dir(os.path.join(source, item), '%s/%s' % (target, item))

    def mkdir(self, path, mode=511, ignore_existing=False):
        ''' Augments mkdir by adding an option to not fail if the folder exists  '''
        try:
            super(MySFTPClient, self).mkdir(path, mode)
        except IOError:
            if ignore_existing:
                pass
            else:
                raise
