#testkey: fd58e13e22604e820052b44611d61d6c
import json
import os
import requests
from cloudomate.util.captchareload import anticaptchaReloader


class CaptchaAccountManager:

    captcha_api_key_location = \
        os.path.expanduser("~") \
        + '/.config/config_captcha_account.cfg'

    def __init__(self):
        # print("\nCaptcha account config file: "
        # + self.captcha_api_key_location)
        pass

    # get the API-key needed for Anti-Captcha Api account
    def get_api_key(self):
        # retrieve the Captcha-Solving API key from
        # self.captcha_api_key_location
        if os.path.isfile(self.captcha_api_key_location):
            file = open(self.captcha_api_key_location, "r")
            lines = file.readlines()
            return lines[0].replace('\n', '').replace('\r', '')
        else:
            raise Exception("missing captcha configuration file")

    # Only set the API-key for the account (wil remain the same)
    # currently assigned to this agent
    def set_api_key(self, api_key):
        ltest = self.get_anticaptcha_account_login()
        print(
            "\nSetting API key for captcha account: "
            + ltest["username"])
        login_temp = self.get_anticaptcha_account_login()
        tempfile = open(self.captcha_api_key_location, 'w')
        tempfile.write(
            api_key
            + "\n"
            + login_temp["username"]
            + "\n"
            + login_temp["password"])
        tempfile.close()
        print("\nSuccesfully written config files....")

    def get_balance(self):
        # Query API for account balance
        response = \
            requests.post("https://api.anti-captcha.com/get_balance",
                          json={"clientKey": self.get_api_key()})

        # Check response of HTTP request
        if response.status_code == requests.codes.ok:
            response_json = json.loads(response.text)
            if response_json["errorId"] == 0:
                # print("Successful, account balance returned")
                return response_json["balance"]
            else:
                # Print API error
                print(response.text)
        else:
            # Print request error
            print(response.status_code)

    def reload_account(self, wallet, amount, feemultiplier):
        login = self.get_anticaptcha_account_login()
        print("Reloading captcha account...")
        a = anticaptchaReloader(login['username'], login['password'])
        a.purchase_bitcoin(wallet, amount, feemultiplier)
    
    # Get the Account login (for signing into anti-captcha) currently
    # assigned to this agent
    def get_anticaptcha_account_login(self):
        if os.path.isfile(self.captcha_api_key_location):
            file = open(self.captcha_api_key_location, "r")
            lines = file.readlines()
            if len(lines) != 3:
                print("\n\n****************************************\n\n"
                      " Error: Your captcha account configuration "
                      "(captcha_account.cfg) is not in correct format\n"
                      "\n****************************************\n\n")
                raise Exception("Captcha configuration "
                                "file incorrect format")
            pass
            usern = lines[1].replace('\n', '').replace('\r', '')
            passw = lines[2].replace('\n', '').replace('\r', '')
            user_login = {"username": usern, "password": passw}
            return user_login
        else:
            raise Exception("missing captcha configuration file")

    # Set the API-key along with the account associated account
    # (username/email and password) for this agent
    def set_captcha_api_account(self, api_key, username, password):
        tempfile = open(self.captcha_api_key_location, 'w')
        contents = api_key + "\n" + username + "\n" + password
        tempfile.write(contents)
        tempfile.close()
        print("\nCapthca account set to: " + username)


if __name__ == '__main__':
    key_manager = CaptchaAccountManager()
    keyretrieved = key_manager.get_api_key()
    print("\n-->key retrieved: " + keyretrieved)
    w_login = key_manager.get_anticaptcha_account_login()
    print(
        "\nweb login: \n\tusername: "
        + w_login["username"]
        + "\n\tpassword: "
        + w_login["password"])
    # test = "whuuut"
    # key_manager.set_api_key(test)
    # print("\nkey set to: " + test)
    keyretrieved = key_manager.get_api_key()
    print("\n-->key retrieved: " + keyretrieved)
    w_login = key_manager.get_anticaptcha_account_login()
    print("\nweb login: \n\tusername: "
          + w_login["username"]
          + "\n\tpassword: "
          + w_login["password"])
