import os
import urllib.request
import random
import requests
import re
import time
from cloudomate.util.torguard_web_retriever import TorguardServiceRetriever


class InstallVpnTorguard():

    # Config files download location
    configurl_files_url_AES_UDP = \
        'https://torguard.net/downloads/OpenVPN-UDP.zip'
    configurl_files_url_AES_TCP = \
        'https://torguard.net/downloads/OpenVPN-TCP.zip'

    # directories for saving config files
    c_logdir = os.path.expanduser("~") + '/.config/torguard_log'
    c_vpn_config_dir = \
        os.path.expanduser("~") \
        + '/.config/torguard_openvpn_config_files'
    c_userpass_dir = \
        os.path.expanduser("~") + '/.config/torguard_open_vpn_userpass'

    # config folder names (folders zip file extracts to)
    c_config_AES256TCP_folder_name = 'OpenVPN-TCP'
    c_config_AES256UDP_folder_name = 'OpenVPN-UDP'

    userpass_file_name = 'torguard_openvpn_service_auth.txt'

    # username en passw for open vpn: NOTE these
    # are NOT THE SAME as vpnac-web login credentials
    vpnusern_ = None
    vpnpassw_ = None

    # Selenium webdriver
    driver = None

    # arguments username and password are required by openvpn service
    def __init__(self, openvpn_user=None, openvpn_passw=None):

        if openvpn_user is not None and openvpn_passw is not None:
            self.vpnusern_ = openvpn_user
            self.vpnpassw_ = openvpn_passw
            print("\nusername set to: '" + self.vpnusern_ + "'")
            print("\npassword set to: '" + self.vpnpassw_ + "'")
            return

        openvpn_auth_file = \
            self.c_userpass_dir \
            + '/' \
            + self.userpass_file_name
        if os.path.isfile(openvpn_auth_file):
            file = open(openvpn_auth_file, "r")
            lines = file.readlines()
            self.vpnusern_ = \
                lines[0].replace('\n', '').replace('\r', '')
            self.vpnpassw_ = \
                lines[1].replace('\n', '').replace('\r', '')
            print("--opnvpnusern found : " + self.vpnusern_)
            print("--opnvpnpassw found : " + self.vpnpassw_)
            return

        web_login_file = \
            os.path.expanduser("~") \
            + '/.config/torguard_login.txt'
        if os.path.isfile(web_login_file):
            # print("\n\nOnly weblogin credentials found:
            # please run torguard_service_auth_retriever.py before
            # calling this script to retrieve service credentials
            # from web credentials")
            torguardServiceRetriever()
            # exit(0)
            return
            pass
        elif openvpn_passw is None or openvpn_passw is None:
            print("\n**************************************\n\n")
            print("\nError: No login Credentials found file: "
                  "'torguard_login.txt' does not exist in :"
                  + os.path.expanduser("~") + '/.config/')
            print("\nPlease provide web-login crdentials by "
                  "purchasing a vpnac service trough the "
                  "vpnac_purchase.py script ")
            print("\nOR openvpn auth credentials (not the same as "
                  "web credentials) manually as paramters directly "
                  "to the script")
            print("\n\n**************************************\n\n")
            print("no credentials for neither web scraping "
                  "nor openvpn found")
            exit(0)
            pass

        pass
    
    def get_countries(self, udp=False):

        # Either set the config dir to point to eiter the  TCP or
        # UDP folder (depending on which was specified for download)
        self.download_config_files(udp)
        c_dir = \
            self.c_vpn_config_dir \
            + '/' \
            + self.c_config_AES256TCP_folder_name
        if udp:
            c_dir = self.c_vpn_config_dir \
                    + '/' \
                    + self.c_config_AES256UDP_folder_name

        # create a list of all the areas
        # trough which traffic can be routed
        file_list = os.popen('ls ' + c_dir + '/').read()

        options = file_list.splitlines()

        # remove ca.crt and ta.key from routing options
        if 'ca.crt' in options:
            options.remove('ca.crt')
        if 'ta.key' in options:
            options.remove('ta.key')
        return options

    # start vpn with either Standard TCP or UDP
    def start_vpn(self, udp=False, country_route=None):

        # Either set the config dir to point to eiter the TCP
        # or UDP folder (depending on which was specified for download)
        self.download_config_files(udp)

        # save user info required for vpn
        contents = self.vpnusern_ + "\n" + self.vpnpassw_
        filedir = self.c_userpass_dir + '/' + self.userpass_file_name
        print(filedir)
        self.save_to_file(contents, filedir)

        c_dir = \
            self.c_vpn_config_dir \
            + '/' \
            + self.c_config_AES256TCP_folder_name
        if udp:
            c_dir = self.c_vpn_config_dir \
                    + '/' \
                    + self.c_config_AES256UDP_folder_name

        # create a list of all the areas trough
        # which traffic can be routed
        file_list = os.popen('ls ' + c_dir + '/').read()

        options = file_list.splitlines()

        use_ta_key = False

        # remove ca.crt and ta.key from routing options
        if 'ca.crt' in options:
            options.remove('ca.crt')
        if 'ta.key' in options:
            use_ta_key = True
            options.remove('ta.key')

        random_country = random.randint(0, len(options)-1)

        random_vpn = None
        # Check to route to country_route given by user
        if country_route is not None:
            if country_route in options:
                print("\n\nCountry found: " + country_route)
                random_vpn = country_route

        if random_vpn is None:
            random_vpn = options[random_country]
        file_ = c_dir + '/' + random_vpn
        userpassfile = \
            self.c_userpass_dir \
            + '/' \
            + self.userpass_file_name
        print(userpassfile)

        c_config_crt = \
            self.c_vpn_config_dir \
            + '/' \
            + self.c_config_AES256TCP_folder_name \
            + '/ca.crt'
        c_config_key = \
            self.c_vpn_config_dir \
            + '/' \
            + self.c_config_AES256TCP_folder_name \
            + '/ta.key'

        if udp:
            c_config_crt = \
                self.c_vpn_config_dir \
                + '/' \
                + self.c_config_AES256UDP_folder_name \
                + '/ca.crt'
            c_config_key = \
                self.c_vpn_config_dir \
                + '/' \
                + self.c_config_AES256UDP_folder_name \
                + '/ta.key'

        print(c_config_crt)

        startvpn_cm = \
            'sudo openvpn --config ' \
            + file_ \
            + ' --script-security 2 --dhcp-option DNS 8.8.8.8 ' \
              '--up /etc/openvpn/update-resolv-conf --down ' \
              '/etc/openvpn/update-resolv-conf --ca ' \
            + c_config_crt \
            + ' --auth-user-pass ' \
            + userpassfile + '> /dev/null &'
        if use_ta_key:
            startvpn_cm = \
                'openvpn --config ' \
                + file_ \
                + ' --script-security 2 --dhcp-option DNS 8.8.8.8 ' \
                  '--up /etc/openvpn/update-resolv-conf --down ' \
                  '/etc/openvpn/update-resolv-conf --ca ' \
                + c_config_crt \
                + ' --tls-auth ' \
                + c_config_key \
                + ' 1 ' \
                + ' --auth-user-pass ' \
                + userpassfile + ' > /dev/null &'

        print(startvpn_cm)
        print("\n\nVPN started")
        output = os.popen(startvpn_cm).read()
        print(output)

    def download_config_files(self, udp=False):

        # variable for storing some log information
        logging_info = "\n----------\n\n"

        # create config dir if they dont exist already
        if not os.path.isdir(self.c_logdir):
            os.popen('mkdir ' + self.c_logdir).read()
        if not os.path.isdir(self.c_vpn_config_dir):
            os.popen('mkdir ' + self.c_vpn_config_dir).read()
        if not os.path.isdir(self.c_userpass_dir):
            os.popen('mkdir ' + self.c_userpass_dir).read()

        # full file path and file name to which we will save the vpn
        # config zip file
        file_test = os.path.expanduser("~") + '/toruguardconfig.zip'

        # the name of the folder that the zip file for the specified
        # protocol wil extract
        foldername = self.c_config_AES256TCP_folder_name

        # downoad the correct config zip file for the specified protocol
        if udp:
            res = requests.get(self.configurl_files_url_AES_UDP)
            with open(file_test, 'wb') as output:
                output.write(res.content)
            pass
        else:
            res = requests.get(self.configurl_files_url_AES_TCP)
            with open(file_test, 'wb') as output:
                output.write(res.content)
            pass

        # unzip the openvpn config files to the config openvpn dir
        unzip_command = \
            'unzip -o ' \
            + file_test \
            + ' -d ' \
            + self.c_vpn_config_dir \
            + '/'
        logging_info += os.popen(unzip_command).read()

        # dir containing the vpn files for the specified protocol (
        # UDP or TCP)
        config_file_dir = self.c_vpn_config_dir + '/' + foldername

        # remove the zip file after it has been unzipped to the
        # config dir (zip file no longer needed)
        logging_info += os.popen('rm ' + file_test).read()

    def save_to_file(self, file_contents, full_file_path):
        tempfile = open(full_file_path, 'w')
        tempfile.write(file_contents)
        tempfile.close()
