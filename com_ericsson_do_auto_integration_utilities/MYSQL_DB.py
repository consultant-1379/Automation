# pylint: disable=C0302,C0103,C0301
'''
Created on Sep 26, 2019

@author: emaidns
'''

import psycopg2
import time
import mysql.connector
from com_ericsson_do_auto_integration_utilities.Report_file import Report_file
from com_ericsson_do_auto_integration_utilities.Logger import Logger
from sshtunnel import SSHTunnelForwarder

log = Logger.get_logger('MYSQL_DB.py')


def get_PSQL_connection(host, database, user, password):
    """

    @param host:
    @param database:
    @param user:
    @param password:
    @return:
    """
    try:
        log.info('connecting with database ip %s', host)
        psql_connection = psycopg2.connect(database=database, user=user, password=password, host=host, port="5432")
        log.info('connected with database IP ' + host + ' name ' + database)
        return psql_connection

    except mysql.connector.Error as error:
        log.error('Error connecting with database error %s', str(error))
        Report_file.add_line('Error connecting with database ' + str(error))
        assert False


def get_eocm_cn_postgres_con(datbase_name, db_user, db_password, eocm_namespace, director_ip,
                             db_pod, dir_con):
    try:

        log.info('Initiating Port forwarding')
        log.info('Clearing up any existing port-forwarding')
        command = 'pkill -f "port-forward"'

        stdin, stdout, stderr = dir_con.exec_command(command)
        log.info(stdout.read().decode('utf-8'))
        error = stderr.read().decode('utf-8')

        if error != '':
            log.error(error)
            log.error("Error executing command %s.", command)
            assert False

        log.info('Finished clearing port-forwarding process')

        command = f'kubectl port-forward --address 0.0.0.0 {db_pod} -n {eocm_namespace} 5432:5432'
        log.info('Command to do port forward: %s', command)
        stdin, stdout, stderr = dir_con.exec_command(command)
        #log.info(stdout)
        time.sleep(3)
        log.info('connecting with eocm postgres database to fetch the data')

        conn = psycopg2.connect(database=datbase_name, user=db_user, password=db_password, host=director_ip,
                                port=5432)
        log.info('connected with postgres eocm database')
        return conn

    except Exception as e:
        log.error('Error connecting with database error %s', str(e))
        dir_con.exec_command('pkill -f "port-forward"')
        dir_con.close()
        assert False


def get_mySQL_connection(host, database, user, password):
    """

    @param host:
    @param database:
    @param user:
    @param password:
    @return:
    """
    try:
        log.info('connecting with database ip %s', host)
        connection = mysql.connector.connect(host=host, database=database, user=user, password=password)
        log.info('connected with database IP ' + host + ' name ' + database)
        return connection

    except mysql.connector.Error as error:
        log.error('Error connecting with database error %s', str(error))
        Report_file.add_line('Error connecting with database ' + str(error))
        assert False


def insert_data_mySQL_table(db_connection, table_name, column_string, values_tuple):
    """

    @rtype: object
    @param db_connection:
    @param table_name:
    @param column_string:
    @param values_tuple:
    """
    # columns is str(tuple) with column names  and values are tuple
    try:
        log.info('Inserting data in table %s', table_name)
        mySql_insert_query = ''' INSERT INTO {} {} VALUES {} '''.format(table_name, column_string, values_tuple)

        Report_file.add_line(mySql_insert_query)

        cursor = db_connection.cursor()

        result = cursor.execute(mySql_insert_query)

        db_connection.commit()

        Report_file.add_line("Record inserted successfully into {}".format(table_name))


    except mysql.connector.Error as error:
        log.error("Failed to insert record into %s table %s", table_name, str(error))
        Report_file.add_line("Failed to insert record into {} table {}".format(table_name, str(error)))
        assert False

    finally:
        cursor.close()


def check_record_exits_mySQL_table(db_connection, table_name, column_name, record_name):
    """

    @param db_connection:
    @param table_name:
    @param column_name:
    @param record_name:
    @return:
    """
    try:
        log.info('checking data in table %s', table_name)
        mySql_select_query = " SELECT * FROM {} WHERE {} = '{}' ".format(table_name, column_name, record_name)

        Report_file.add_line(mySql_select_query)

        cursor = db_connection.cursor()

        cursor.execute(mySql_select_query)

        record_data = cursor.fetchall()

        Report_file.add_line(record_data)

        row_count = cursor.rowcount

        log.info('row count : %s', str(row_count))

        if row_count == 0:
            return False

        else:
            return True

    except mysql.connector.Error as error:
        log.error("Failed to select record from %s table %s", table_name, str(error))
        Report_file.add_line("Failed to select record from {} table {}".format(table_name, str(error)))
        assert False

    finally:
        cursor.close()


def get_record_id_from_mySQL_table(db_connection, table_name, id_column_name, column_name, record_name):
    """

    @param db_connection:
    @param table_name:
    @param id_column_name:
    @param column_name:
    @param record_name:
    @return:
    """
    try:
        log.info('Fetching record id of ' + record_name + ' in table ' + table_name)

        mySql_select_query = ''' SELECT {} FROM {} WHERE {} = "{}" '''.format(id_column_name, table_name, column_name,
                                                                              record_name)

        cursor = db_connection.cursor()

        Report_file.add_line(mySql_select_query)

        cursor.execute(mySql_select_query)

        record_data = cursor.fetchall()

        Report_file.add_line(record_data)

        record_id = record_data[0][0]

        return record_id

    except mysql.connector.Error as error:
        log.error("Failed to get record id from %s table %s", table_name, str(error))
        Report_file.add_line("Failed to get record id from {} table {}".format(table_name, str(error)))
        assert False

    finally:
        cursor.close()


def get_record_id_from_mySQL_two_inputs(db_connection, table_name, id_column_name, column_name, record_name,
                                        column_name2, record_value):
    """

    @param db_connection:
    @param table_name:
    @param id_column_name:
    @param column_name:
    @param record_name:
    @param column_name2:
    @param record_value:
    @return:
    """
    try:
        log.info('Fetching record id of ' + record_name + ' in table ' + table_name)

        mySql_select_query = ''' SELECT {} FROM {} WHERE {} = "{}" and {} = {}'''.format(id_column_name, table_name,
                                                                                         column_name, record_name,
                                                                                         column_name2, record_value)

        cursor = db_connection.cursor()

        Report_file.add_line(mySql_select_query)

        cursor.execute(mySql_select_query)

        record_data = cursor.fetchall()

        Report_file.add_line(record_data)

        record_id = record_data[0][0]

        return record_id

    except mysql.connector.Error as error:
        log.error("Failed to get record id from %s table %s", table_name, str(error))
        Report_file.add_line("Failed to get record id from {} table {}".format(table_name, str(error)))
        assert False

    finally:
        cursor.close()


def get_record_id_from_PSQL_table(db_connection, table_name, id_column_name, column_name, record_name):
    """

    @param db_connection:
    @param table_name:
    @param id_column_name:
    @param column_name:
    @param record_name:
    @return:
    """
    try:
        log.info('Fetching record id of ' + record_name + ' in table ' + table_name)

        mySql_select_query = "SELECT {} FROM {} WHERE {} = '{}'".format(id_column_name, table_name, column_name,
                                                                        record_name)

        cursor = db_connection.cursor()

        Report_file.add_line(mySql_select_query)

        cursor.execute(mySql_select_query)

        record_data = cursor.fetchall()

        Report_file.add_line(record_data)

        record_id = record_data[0][0]

        return record_id

    except Exception as error:
        log.error("Failed to get record id from %s table %s", table_name, str(error))
        Report_file.add_line("Failed to get record id from {} table {}".format(table_name, str(error)))
        assert False

    finally:
        cursor.close()


def get_table_data_from_PSQL_table_for_ecm_package_deletion(db_connection, column1, column2, column3, column4,
                                                            table_name, column5, column6):
    """

    @param db_connection:
    @param column1:
    @param column2:
    @param column3:
    @param column4:
    @param table_name:
    @param column5:
    @param column6:
    @return:
    """
    try:
        log.info('Fetching table data from %s', table_name)

        mySql_select_query = "SELECT {},{},{},{} FROM {} where {}='{}'".format(column1, column2, column3, column4,
                                                                               table_name, column5, column6)

        cursor = db_connection.cursor()

        Report_file.add_line(mySql_select_query)

        cursor.execute(mySql_select_query)

        data = cursor.fetchall()
        log.info(data)

        return data

    except Exception as error:
        log.error("Failed to fetch table data from %s Error : %s ", table_name, str(error))
        Report_file.add_line("Failed to fetch table data from {} Error : {} ".format(table_name, str(error)))
        assert False

    finally:
        cursor.close()
        db_connection.close()

def get_table_data_from_PSQL_table(db_connection, table_name, column1, column2, column3):
    """

    @param db_connection:
    @param table_name:
    @param column1:
    @param column2:
    @param column3:
    @return:
    """
    try:
        log.info('Fetching table data from %s', table_name)

        mySql_select_query = "SELECT {},{},{} FROM {}".format(column1, column2, column3, table_name)

        cursor = db_connection.cursor()

        Report_file.add_line(mySql_select_query)

        cursor.execute(mySql_select_query)

        data = cursor.fetchall()

        return data

    except Exception as error:
        log.error("Failed to fetch table data from %s Error : %s ", table_name, str(error))
        Report_file.add_line("Failed to fetch table data from {} Error : {} ".format(table_name, str(error)))
        assert False

    finally:
        cursor.close()
