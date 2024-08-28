class LCM_service(object):


    def get_lcm_service_ip(self):
        return self.__lcm_service_ip

    def set_lcm_service_ip(self, value):
        self.__lcm_service_ip = value.strip()

    def get_vnf_service_ip(self):
        return self.__vnf_service_ip

    def set_vnf_service_ip(self, value):
        self.__vnf_service_ip = value.strip()

    def get_lcm_user_name(self):
        return self.__lcm_user_name

    def set_lcm_user_name(self, value):
        self.__lcm_user_name = value.strip()

    def get_lcm_password(self):
        return self.__lcm_password

    def set_lcm_password(self, value):
        self.__lcm_password = value.strip()


    def get_httpd_ips_list(self):
        return self.__httpd_ips_list

    def set_httpd_ips_list(self, value):
        self.__httpd_ips_list = value
