import os


class VpnStatusMonitor:

    # Path user auth
    c_userpass_dir_torguard = \
        os.path.expanduser("~") \
        + '/.config/torguard_open_vpn_userpass'
    userpass_file_name_torguard = 'torguard_openvpn_service_auth.txt'

    c_userpass_dir_vpnac = \
        os.path.expanduser("~") \
        + '/.config/vpnac_open_vpn_userpass'
    userpass_file_name_vpnac = 'vpnac_openvpn_service_auth.txt'

    service_expire_date_file_name = \
        'expiration_date_openvpn_service_auth.txt'

    def __init__(self):
        pass

    def get_status_vpnac(self):
        status = {"webuser_email": None,
                  "webuser_password": None,
                  "service_stored_user": None,
                  "service_stored_password": None,
                  "valid": None}
        openvpn_auth_file = self.c_userpass_dir_vpnac \
            + '/' + self.userpass_file_name_vpnac
        if os.path.isfile(openvpn_auth_file):
            file = open(openvpn_auth_file, "r")
            lines = file.readlines()
            status["service_stored_user"] = \
                lines[0].replace('\n', '').replace('\r', '')
            status["service_stored_password"] = \
                lines[1].replace('\n', '').replace('\r', '')

        openvpn_auth_expr_file = \
            self.c_userpass_dir_vpnac \
            + '/' \
            + self.service_expire_date_file_name
        if os.path.isfile(openvpn_auth_expr_file):
            file = open(openvpn_auth_expr_file, "r")
            lines = file.readlines()
            status['valid'] = \
                lines[0].replace('\n', '').replace('\r', '')

        web_login_file = \
            os.path.expanduser("~") \
            + '/.config/vpnac_login.txt'
        if os.path.isfile(web_login_file):
            file = open(web_login_file, "r")
            lines = file.readlines()
            status["webuser_email"] = \
                lines[0].replace('\n', '').replace('\r', '')
            status["webuser_password"] = \
                lines[1].replace('\n', '').replace('\r', '')
        return status

    def get_status_torguard(self):
        status = {"webuser_email": None,
                  "webuser_password": None,
                  "service_stored_user": None,
                  "service_stored_password": None,
                  "valid": None}
        openvpn_auth_file = \
            self.c_userpass_dir_torguard \
            + '/' \
            + self.userpass_file_name_torguard
        if os.path.isfile(openvpn_auth_file):
            file = open(openvpn_auth_file, "r")
            lines = file.readlines()
            status["service_stored_user"] = \
                lines[0].replace('\n', '').replace('\r', '')
            status["service_stored_password"] = \
                lines[1].replace('\n', '').replace('\r', '')

        openvpn_auth_expr_file = \
            self.c_userpass_dir_torguard \
            + '/' \
            + self.service_expire_date_file_name
        if os.path.isfile(openvpn_auth_expr_file):
            file = open(openvpn_auth_expr_file, "r")
            lines = file.readlines()
            status['valid'] = \
                lines[0].replace('\n', '').replace('\r', '')

        web_login_file = \
            os.path.expanduser("~") \
            + '/.config/torguard_login.txt'
        if os.path.isfile(web_login_file):
            file = open(web_login_file, "r")
            lines = file.readlines()
            status["webuser_email"] = \
                lines[0].replace('\n', '').replace('\r', '')
            status["webuser_password"] = \
                lines[1].replace('\n', '').replace('\r', '')
        return status

    def get_status_purchased(self):

        purchased = []
        status_torguard = self.get_status_torguard()
        if status_torguard['webuser_email'] is not None:
            purchased.append('torguard')
        status_vpnac = self.get_status_vpnac()
        if status_vpnac['webuser_email'] is not None:
            purchased.append('vpnac')
        return purchased

    #returns whether the traffic is currently being routed trough an ip address that is different from the one registered at time of instalation
    def getVpnIsActive(self):
        starting_ip_file = os.path.expanduser("~") + '/.config/server-ip-address.txt'
        s_ip_address = None
        if os.path.isfile(starting_ip_file):
            file = open(starting_ip_file, "r")
            lines = file.readlines()
            file.close()
            s_ip_address = lines[0].replace('\n', '').replace('\r', '')
        else:
            return 'Unknown'
        c_ip = os.popen('curl ipv4bot.whatismyipaddress.com').read()
        print("\nstarting ip: " + s_ip_address)
        print("\ncurrent ip: " + c_ip)
        if c_ip != s_ip_address:
            return 'Active'
        else:
            return 'Not Active'

    def fetch_account_info(self, weblogin_user, weblogin_password):
        pass


if __name__ == '__main__':
    print("\nTest")
