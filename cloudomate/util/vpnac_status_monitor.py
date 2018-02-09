import os
import mechanicalsoup

class VpnAcStatusMonitor:

    #Path user auth
    c_userpass_dir = os.path.expanduser("~") + '/.config/vpnac_open_vpn_userpass'

    userpass_file_name = 'vpnac_openvpn_service_auth.txt'

    BASE_URL = 'https://www.vpn.ac/'

    service_expire_date_file_name = 'expiration_date_openvpn_service_auth.txt'

    #Urls required to scrape the openvpn username and password authentication
    LOGIN_URL = 'https://www.vpn.ac/clientarea.php'
    ACTIVE_SERVICES_URL = 'https://vpn.ac/clientarea.php?action=products'

    def __init__(self):
        pass

    def getStatus(self):
        status = {"webuser_email": None, "webuser_password": None, "service_stored_user": None, "service_stored_password": None, "valid": None}
        openvpn_auth_file = self.c_userpass_dir + '/' + self.userpass_file_name
        if os.path.isfile(openvpn_auth_file):
            file = open(openvpn_auth_file, "r")
            lines = file.readlines()
            status["service_stored_user"] = lines[0].replace('\n', '').replace('\r', '')
            status["service_stored_password"] = lines[1].replace('\n', '').replace('\r', '')

        openvpn_auth_expr_file = self.c_userpass_dir + '/' + self.service_expire_date_file_name
        if os.path.isfile(openvpn_auth_expr_file):
            file = open(openvpn_auth_expr_file, "r")
            lines = file.readlines()
            status['valid'] = lines[0].replace('\n', '').replace('\r', '')

        web_login_file = os.path.expanduser("~") + '/.config/vpnac_login.txt'
        if os.path.isfile(web_login_file):
            file = open(web_login_file,"r")
            lines = file.readlines()
            status["webuser_email"] = lines[0].replace('\n', '').replace('\r', '')
            status["webuser_password"] = lines[1].replace('\n', '').replace('\r', '')

        return status

    def fetchAccountInfo(self,weblogin_user,weblogin_password):

        br = mechanicalsoup.StatefulBrowser()     
        status ={"service_user": None, "service_password": "***********", "valid": None}
        br.open(self.LOGIN_URL)
        form = br.select_form()
        form["username"] = login_username
        form["password"] = login_password

        response = br.submit_selected()

        if 'Login Details Incorrect' in response.text:
            print("\n\nLogin incorrect")
            exit(0)

        #set cookie header for login
        cookies = br.session.cookies.items()
        cookie = cookies[0]
        headercookie = "=".join(cookie)
        session.headers.update({'Cookie': headercookie})


        br.open(self.ACTIVE_SERVICES_URL)

        soup = br.get_current_page()
        rows = soup.find('table').find('tbody').find_all('tr')

        temphref = None

        #Retrieve an active an VPN service url from the vpnac account
        for row in rows:
            if 'Active' in row.text:
                temp = row.find('a')
                temphref = temp['href']
                tdlist = row.find_all('td')
                for td in tdlist:
                    if 'Next Due Date' in str(td):
                        status[valid] = td.text
                        print("Service-Active-Until-value found : " + self.service_auth_active_until)
        if temphref == None:
            print("\n\nhref >???????????? No Active vpn service found For the given login.. Perhaps it expired? \n")
            exit(0)

        #go to the page containing vpn user info needed for openvpn
        vpn_info_url = self.BASE_URL + temphref

        #retrieve vpn username required for openvpn
        self.br.open(vpn_info_url)
        soup = self.br.get_current_page()
        #div containg the username
        div = soup.select('div.controls')[0]

        # Extract openvpn username in string format without spaces,newlines,tabs
        vpn_config_username = ''.join((''.join(map(str,div.contents))).split())
        status["service_user"] = vpn_config_username
        
        return status

if __name__ == '__main__':
    print("\nTest")
