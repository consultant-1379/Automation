'''
Created on Jul 29, 2020

@author: emaidns
'''


class wano(object):

    def get_wano_hostname(self):
        return self.__wano_hostname

    def set_wano_hostname(self, value):
        self.__wano_hostname = value.strip()


    def get_wano_username(self):
        return self.__wano_username

    def set_wano_username(self, value):
        self.__wano_username = value.strip()


    def get_wano_password(self):
        return self.__wano_password

    def set_wano_password(self, value):
        self.__wano_password = value.strip()


    def get_metrics_host_url(self):
        return self.__metrics_host_url

    def set_metrics_host_url(self, value):
        self.__metrics_host_url = value.strip()


    def get_metrics_value_pack(self):
        return self.__metrics_value_pack

    def set_metrics_value_pack(self, value):
        self.__metrics_value_pack = value.strip()


