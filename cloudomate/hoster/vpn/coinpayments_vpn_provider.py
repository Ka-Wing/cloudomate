# If unforseen problems occur: make sure you are running this script with a user OTHER than root or WITHOUT "sudo"

import time
import re
import os
import requests
from selenium import webdriver
import sys

from selenium.common.exceptions import NoSuchElementException

from cloudomate.util.captcha_account_manager import captchaAccountManager
from abc import ABC, abstractmethod, abstractproperty
#from cloudomate.bitcoin_wallet import Wallet as BitcoinWallet
# from cloudomate.litcoin_wallet import Wallet as LitcoinWallet
from cloudomate.ethereum_wallet import Wallet as EthereumWallet
#from cloudomate import bitcoin_wallet as B_wallet_util
# from cloudomate import litcoin_wallet as L_wallet_util
from cloudomate import ethereum_wallet as E_wallet_util


class coinpaymentsVpnProvider(ABC):

    @abstractmethod
    def PURCHASE_URL(self):
        pass

    @abstractmethod
    def COINPAYMENTS_URL(self):
        pass

    @abstractmethod
    def saveUserLoginFile(self):
        pass

    driver = None

    user_used_for_payment = None

    #use to validate email user-setting
    def isValidEmail(self, email):
        if re.match("(^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$)", email) == None:
            print("\n\nPlease make sure the email you provide is a valid email")
            exit(0)

    #use to validate password user-setting
    def isValidPassword(self, password):
        valid = True
        if len(password) < 8:
            print("your password must be 8 characters long")
            valid = False
        if len(password) >24:
            print("Your password must be shorter than 24 characters")
            valid = False
        elif re.search(r"\d", password) is None:
            print("you need a digit in your password")
            valid = False
        elif re.search(r"[A-Z]", password) is None:
            print("you need a capital letter in your password")
            valid = False
        elif re.search(r"[a-z]", password) is None:
            print("you need a lowercase letter in your password")
            valid = False
        elif re.search(r"[ !#$%&'()*+,-./[\\\]^_`{|}~"+r'"]', password) is None:
            print("\n\n symbol in password")
            valid = False
        if valid == False:
            print("\n\nYour password is not up to standards, provide a password with te above standards met, or leave blank to automaticcally have a password generated\n\n")
            exit(0)

    # Creates an invoice that for a vpn service that requires Bitcoin payment (Returns the "BTC amount" and the "BTC address" to which the "BTC amount" needs to be send).
    def retrieve_bitcoin(self, user_settings):
        try:
            return self._retrieve_payment_info(["bitcoin", "BTC"], user_settings)
        except Exception as e:
            print(self._error_message(e))

    # Use this method for purchasing with Ethereum.
    # Retrieving Ethereum at the final page is different than for the other currencies.
    def retrieve_ethereum(self, user_settings):
        try:
            return self._retrieve_payment_info(["ethereum", "ETH"], user_settings)
        except Exception as e:
            print(self._error_message(e))

    # Used for generating error message.
    def _error_message(self, message):
        return "Error " + str(message) + "\nTry again. It it still does not work," \
                                         "website might have been updated, update script."

    def __init__(self):

        print("\nSetting up chrome-driver...")
        # Download the appropriate executable chromedirver and place this in the folder for the script to access
        res = requests.get('https://chromedriver.storage.googleapis.com/2.35/chromedriver_linux64.zip')
        file_test = os.path.expanduser("~") + '/.config/chromedriver_linux64.zip'
        with open(file_test, 'wb') as output:
            output.write(res.content)
            pass
        # extract the downloaded file
        unzip_command = 'unzip -o ' + file_test + ' -d ' + os.path.expanduser("~") + '/'
        test_ = os.popen(unzip_command).read()
        # remove the zip file after extraction
        os.popen('rm ' + file_test).read()
        # get the file path to pass to the chromdriver
        driver_loc = os.path.expanduser("~") + '/chromedriver'

        # Selenium setup: headless Chrome, Window size needs to be big enough, otherwise elements will not be found.
        options = webdriver.ChromeOptions()
        options.add_argument('headless')
        options.add_argument('disable-gpu');
        options.add_argument('window-size=1920,1080');

        connection_reset = True
        while connection_reset:
            connection_reset = False
            try:
                self.driver = webdriver.Chrome(executable_path=driver_loc, chrome_options=options)
                pass
            except Exception as e:
                if e.errno == 104:
                    connection_reset = True
                    print("\nResetting connection...\n")
                    pass
                else:
                    raise Exception(e)
            pass
        # self.driver = webdriver.Chrome()
        self.driver.maximize_window()


    @abstractmethod
    def goToCoinPaymentsPage(self):
        pass

    # Don't invoke this method directly.
    def _retrieve_payment_info(self, currency, user_settings):

        self.isValidEmail(user_settings['email'])
        if user_settings['password'] != None:
            self.isValidPassword(user_settings['password'])
        else:
            print("\n\nNo password provided --> password automatically set to 'Test_12345_Test_12345' \n\n")
            user_settings['password'] = 'Test_12345_Test_12345'

        self.goToCoinPaymentsPage(user_settings)

        print("Placing an order.")
        print("Retrieving the amount and address.")

        # Continue to the final page.
        try:
            self.driver.find_element_by_id("cpsform").click()
        except:
            print("\n\n*************************************************************************************\n")
            print("\nError: Perhaps you are using an E-mail that is already registered? ")
            print(
                "\n\n(You can specify whether the given  email is already registered as a parameter in the user settings for the script) \n")
            print("\nTry again with the approproate settings")
            print("\n\n*************************************************************************************\n")

        try:
            self.driver.find_element_by_id("coins_" + currency[1]).click()
            pass
        except NoSuchElementException:
            print("The service provider does not accept " + currency[1] + " (anymore).")
            sys.exit(0)

        self.driver.find_element_by_id("dbtnCheckout").click()

        # See if any error messages are returned.
        error_available = False
        try:
            error_message = self.driver.find_element_by_xpath('//*[@id="coform"]/div[1]/div').text
            error_available = True
        except NoSuchElementException:
            pass # No error found

        if error_available:
            print("Error message returned from coinpayments.net: \"" + error_message + "\"")
            sys.exit(0)


        tries = 0
        while not (self.driver.current_url == self.COINPAYMENTS_URL):
            try:
                error_message = self.driver.find_element_by_xpath("/html/body/div/div/div[2]").text
                if "3 unfinished" in error_message:
                    print("You already have 3 unfinished transfers with coinpayments.net from within the last "
                      "24 hours and therefore you cannot create anymore orders..")
                    exit(0)
            except NoSuchElementException:
                pass

            tries = tries + 1
            time.sleep(2)
            if tries > 10:
                #TODO CHECK IF YOU REALLY ARE ON THE CORRECT PAGE.
                self.driver.get(self.COINPAYMENTS_URL)

        time.sleep(2)

        amount = ""
        address = ""

        try:
            address = self.driver.find_element_by_xpath('//*[@id="email-form"]/div[2]/div[1]/div[3]/div[2]').text
            print("address: " + address)
        except NoSuchElementException:
            pass

        try:
            amount = self.driver.find_element_by_xpath('//*[@id="email-form"]/div[2]/div[1]/div[1]').text
        except NoSuchElementException:
            pass

        # Using page source to find address and amount because elements will not be found.
        page = self.driver.page_source
        address_re = ""
        amount_re = ""
        if currency[0] == "ethereum":
            address_re = '<div class="address">(.*?)</div>'
            amount_re = "<div>(.*?) ETH</div>"
        else:
            address_re = '<div><a href="' + currency[0] + ':(.*?)\?amount=(.*?)">(.*?)</a></div>'

        # Get address and amount
        if currency[0] == "ethereum":
            for line in page.split('\n'):
                line = line.lstrip().rstrip()
                match_amount = re.findall(amount_re, line)
                match_address = re.findall(address_re, line)
                if len(match_amount) > 0:
                    amount = match_amount[0]
                if len(match_address) > 0:
                    address = match_address[0]
        else:
            for line in page.split('\n'):
                line = line.lstrip().rstrip()
                match = re.findall(address_re, line)
                if len(match) > 0:
                    address = match[0][0]
                    amount = match[0][1]

        self.user_used_for_payment = user_settings
        time.sleep(2)
        return {'amount': str(amount), 'address': str(address)}

    def pay(self, amount, address, coin_type, wallet):
        # Pay amount using specified COIN wallet, if their is not enough balance available print "Not enough balance for the specified COIN-payment"

        print("\nPayment process of " + str(amount) + " of " + str(coin_type) + " to " + str(address) + " started")
        if (coin_type == 'BTC'):
            print("\nConnecting to bitcoin wallet")
            print("\nChecking Balance...")
            fee = B_wallet_util.get_network_fee()
        elif (coin_type == 'ETH'):
            print("\nConnecting to Ethereum Wallet...")
            print("\nChecking Balance...")
            fee = E_wallet_util.get_network_fee()
        print(('Calculated fee: %s' % fee))
        if (wallet.get_balance() >= fee + float(amount)):
            transaction_hash = wallet.pay(address, amount, fee)
            print('Done purchasing')
            return transaction_hash
        else:
            print(" Not enough " + str(coin_type))

    def saveLoginAfterPurchase(self):

        username = self.user_used_for_payment['email']
        password = self.user_used_for_payment['password']
        # save the login parameter so these can be used by the VPN instalaton script in the Utilities
        full_file_path = self.saveUserLoginFile
        file_contents = username + "\n" + password
        tempfile = open(full_file_path, 'w')
        tempfile.write(file_contents)
        tempfile.close()
        pass
