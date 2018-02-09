import os
import urllib.request
import random
import mechanicalsoup

class installVpnAC():

    #Urls for downloading opvpn config files
    configurl_files_url_AES_UDP = 'https://vpn.ac/ovpn/AES-256-UDP.zip'
    configurl_files_url_AES_TCP = 'https://vpn.ac/ovpn/AES-256-TCP.zip'

    #Path tho which to save config settings and logs
    c_logdir = os.path.expanduser("~") + '/.config/vpnac_log'
    c_vpn_config_dir = os.path.expanduser("~") + '/vpnac_openvpn_config_files'
    c_userpass_dir = os.path.expanduser("~") + '/vpnac_open_vpn_userpass'

    #name of the folder that ultimately is extracted by the downloaded zip files (containing .ovpn files)
    c_config_AES256TCP_folder_name = 'AES-256-TCP'
    c_config_AES256UDP_folder_name = 'AES-256-UDP'

    userpass_file_name = 'vpnac_openvpn_service_auth.txt'

    BASE_URL = 'https://www.vpn.ac/'

    service_expire_date_file_name = 'expiration_date_openvpn_service_auth.txt'

    #username en passw for open vpn: NOTE these are NOT THE SAME as vpnac-web login credentials
    vpnusern_ = None
    vpnpassw_ = None
    service_auth_active_until = None

    br = mechanicalsoup.StatefulBrowser()
    #Urls required to scrape the openvpn username and password authentication
    LOGIN_URL = 'https://www.vpn.ac/clientarea.php'
    vpn_config_password_to_be_set = 'Test_12345'
    ACTIVE_SERVICES_URL = 'https://vpn.ac/clientarea.php?action=products'

    def __init__(self,openvpn_user = None, openvpn_passw = None, openvpn_auth_active_until = None):
        self.service_auth_active_until = openvpn_auth_active_until
        if openvpn_user != None and openvpn_passw != None:
            self.vpnusern_ = openvpn_user
            self.vpnpassw_ = openvpn_passw
            #save user info required for vpn
            contents = self.vpnusern_ + "\n" + self.vpnpassw_
            auth_filedir = self.c_userpass_dir + '/' + self.userpass_file_name
            print(auth_filedir)
            self.saveToFile(contents,auth_filedir)
            service_expire_date_filedir = self.c_userpass_dir + '/' + self.service_expire_date_file_name
            if openvpn_auth_active_until == None:
                self.saveToFile("UNKNOWN",service_expire_date_filedir)
            else :
                self.saveToFile(openvpn_auth_active_until,service_expire_date_filedir)
            return

        openvpn_auth_file = self.c_userpass_dir + '/' + self.userpass_file_name
        if os.path.isfile(openvpn_auth_file):
            file = open(openvpn_auth_file, "r")
            lines = file.readlines()
            self.vpnusern_ = lines[0].replace('\n', '').replace('\r', '')
            self.vpnpassw_ = lines[1].replace('\n', '').replace('\r', '')
            print("--opnvpnusern found : " + self.vpnusern_)
            print("--opnvpnpassw found : " + self.vpnpassw_)
            return

        web_login_file = os.path.expanduser("~") + '/.config/vpnac_login.txt'
        if os.path.isfile(web_login_file):
            file = open(web_login_file,"r")
            lines = file.readlines()
            weblogin_user = lines[0].replace('\n', '').replace('\r', '')
            weblogin_passw = lines[1].replace('\n', '').replace('\r', '')
            print("--web-login user found: " + weblogin_user)
            print("--web-login passw found: " + weblogin_passw)
            self.extractOpenVpnUserInfo(weblogin_user, weblogin_passw)
            return

        elif openvpn_passw == None or openvpn_passw == None:
            print("\n**************************************\n\n")
            print("\nError: No login Credentials found file: 'vpnac_login.txt' does not exist in current path")
            print("\nPlease provide web-login crdentials by purchasing a vpnac service trough the vpnac_purchase.py script ")
            print("\nOR openvpn auth credentials (not the same as web credentials) manually as paramters directly to the script")
            print("\n\n**************************************\n\n")
            print("\n\nno credentials for neither web scraping nor openvpn found")
            exit(0)

    def getCountries(self,UDP = False):
        self.download_config_files(UDP)
        c_dir = self.c_vpn_config_dir + '/' + self.c_config_AES256TCP_folder_name
        if UDP == True:
            c_dir = self.c_vpn_config_dir + '/' + self.c_config_AES256UDP_folder_name

        file_list = os.popen('ls ' + c_dir + '/').read()

        options = file_list.splitlines()
        return options

    def startVpn(self, UDP = False, country_route = None):

        self.download_config_files(UDP)
        c_dir = self.c_vpn_config_dir + '/' + self.c_config_AES256TCP_folder_name
        if UDP == True:
            c_dir = self.c_vpn_config_dir + '/' + self.c_config_AES256UDP_folder_name

        file_list = os.popen('ls ' + c_dir + '/').read()

        options = file_list.splitlines()
        random_country = random.randint(0,len(options))

        random_vpn = None

        if country_route != None:
            if country_route in options:
                random_vpn = country_route

        if random_vpn == None: random_vpn = options[random_country]
        file_ = c_dir + '/' + random_vpn
        userpassfile = self.c_userpass_dir + '/' + self.userpass_file_name
        print(userpassfile)
        startvpn_cm = 'openvpn --config ' + file_ + ' --script-security 2 --dhcp-option DNS 8.8.8.8 --up /etc/openvpn/update-resolv-conf --down /etc/openvpn/update-resolv-conf --auth-user-pass ' + userpassfile
        print(startvpn_cm)
        output = os.popen(startvpn_cm).read()
        print(output)

    def download_config_files(self, UDP = False):

        #variable for storing some log information
        logging_info = "\n----------\n\n"

        #create config dir if they dont exist already
        if os.path.isdir(self.c_logdir) == False:
            os.popen('mkdir ' + self.c_logdir).read()
        if os.path.isdir(self.c_vpn_config_dir) == False:
            os.popen('mkdir ' + self.c_vpn_config_dir).read()
        if os.path.isdir(self.c_userpass_dir) == False:
            os.popen('mkdir ' + self.c_userpass_dir).read()

        #full file path and file name to which we will save the vpn config zip file
        file_test = os.path.expanduser("~") + '/vpnacconfig.zip'

        #the name of the folder that the zip file for the specified protocol wil extract
        foldername = self.c_config_AES256TCP_folder_name

        # downoad the correct config zip file for the specified protocol
        if(UDP == True):
            foldername = self.c_config_AES256UDP_folder_name
            urllib.request.urlretrieve(self.configurl_files_url_AES_UDP, file_test)
        else:
            urllib.request.urlretrieve(self.configurl_files_url_AES_TCP, file_test)

        #unzip the openvpn config files to the config openvpn dir
        unzip_command = 'unzip -o ' + file_test + ' -d ' + self.c_vpn_config_dir + '/'
        logging_info += os.popen(unzip_command).read()

        #dir containing the vpn files for the specified protocol (UDP or TCP)
        config_file_dir = self.c_vpn_config_dir + '/' + foldername

        #remove the zip file after it has been unzipped to the config dir (zip file no longer needed)
        logging_info += os.popen('rm ' + file_test).read()

    def extractOpenVpnUserInfo(self,login_username,login_password):

        self.br.open(self.LOGIN_URL)
        form = self.br.select_form()
        form["username"] = login_username
        form["password"] = login_password

        response = page = self.br.submit_selected()

        #set cookie header for login
        cookies = self.br.session.cookies.items()
        cookie = cookies[0]
        headercookie = "=".join(cookie)
        self.br.session.headers.update({'Cookie': headercookie})


        self.br.open(self.ACTIVE_SERVICES_URL)

        soup = self.br.get_current_page()
        rows = soup.find('table').find('tbody').find_all('tr')

        temphref = 'not set'

        #Retrieve an active an VPN service url from the vpnac account
        for row in rows:
            if 'Active' in row.text:
                temp = row.find('a')
                temphref = temp['href']
                tdlist = row.find_all('td')
                for td in tdlist:
                    if 'Next Due Date' in str(td):
                        self.service_auth_active_until = td.text
                        print("Service-Active-Until-value found : " + self.service_auth_active_until)
        if temphref == 'not set':
            print("\n\nhref >???????????? No Active vpn service found .. Perhaps it expired? \n")


        #go to the page containing vpn user info needed for openvpn
        vpn_info_url = self.BASE_URL + temphref

        #retrieve vpn username required for openvpn
        self.br.open(vpn_info_url)
        soup = self.br.get_current_page()
        #div containg the username
        div = soup.select('div.controls')[0]

        # Extract openvpn username in string format without spaces,newlines,tabs
        vpn_config_username = ''.join((''.join(map(str,div.contents))).split())
        self.vpnusern_ = vpn_config_username

        # set the password of the vpn user (required by openvpn)
        form = self.br.select_form()
        form['newpw'] = self.vpn_config_password_to_be_set
        form['confirmpw'] = self.vpn_config_password_to_be_set
        response = self.br.submit_selected()

        if 'Password Changed Successfully' in response.text:
            print("\nOpenvpn Username: "  + self.vpnusern_)
            print("\nPassword set to: " + self.vpn_config_password_to_be_set + "\n\n")
            self.vpnpassw_ = self.vpn_config_password_to_be_set

        #save user info required for vpn
        contents = self.vpnusern_ + "\n" + self.vpnpassw_
        auth_filedir = self.c_userpass_dir + '/' + self.userpass_file_name
        print(auth_filedir)
        self.saveToFile(contents,auth_filedir)
        service_expire_date_filedir = self.c_userpass_dir + '/' + self.service_expire_date_file_name
        self.saveToFile(self.service_auth_active_until,service_expire_date_filedir)
    
    def getStatus(self):
        pass

    def saveToFile(self, file_contents, full_file_path):
        tempfile = open(full_file_path, 'w')
        tempfile.write(file_contents)
        tempfile.close()

if __name__ == '__main__':
    vpnac = installVpnAC()
    vpnac.startVpn()
