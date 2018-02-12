import os
import time
import re
import sys
from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException
from cloudomate import wallet as wallet_util
import requests

class anticaptchaReloader:

    loginlink = "https://anti-captcha.com/clients/entrance/login"
    username = ""
    password = ""

    def __init__(self, login_username, login_password):
        self.username = login_username
        self.password = login_password

    # Use this method for purchasing with Bitcoin, with parameter
    # amount in dollars.
    def purchase_bitcoin(self, wallet, amount=10, fee_multiplier=1):
        try:
            dictionary = \
                self._return_address(["Bitcoin", "BTC", "btc"], amount)
            amount = dictionary['amount']
            address = dictionary['address']

            # TODO: Pay with bitcoin
            fee = wallet_util.get_network_fee()*fee_multiplier
            print("Paying " + amount + "BTC to " + address +
                  "with fee = " + fee)
            transaction_hash = wallet.pay(address, amount, fee)
            if transaction_hash is not None:
                print("Transaction hash = " + str(transaction_hash))

        except Exception as e:
            print("Error "
                  + str(e)
                  + "Try again. It it still does not work, website "
                    "might have been updated, update script.")

    # Use this method for purchasing with Litecoin.
    def purchase_litecoin(self, amount=10):
        try:
            dictionary = \
                self._return_address(["Litecoin", "LTC", "ltc"], amount)
            amount = dictionary['amount']
            address = dictionary['address']

            print("Paying " + amount + "LTC to " + address)
            print("LTC wallet not implemented (yet).")
            sys.exit(0)

        except Exception:
            print("Something went wrong. Try again. "
                  "It it still does not work, update script.")

    # Use this method for purchasing with DASH.
    def purchase_dash(self, amount=10):
        try:
            dictionary = \
                self._return_address(["DASH", "DASH", "dash"], amount)
            amount = dictionary['amount']
            address = dictionary['address']

            print("Paying " + amount + "DASH to " + address)
            print("DASH wallet not implemented (yet).")
            sys.exit(0)

        except Exception:
            print("Something went wrong. Try again. "
                  "It it still does not work, update script.")

    # Returns the address of the given currency.
    def _return_address(self, currency, amount=10):
        # Download the appropriate executable chromedirver and
        # place this in the folder for the script to access
        print("\nsetting up chrome-driver...")
        res = requests.get(
            'https://chromedriver.storage.googleapis.com/2.35/'
            'chromedriver_linux64.zip')
        file_test = \
            os.path.expanduser("~") \
            + '/.config/chromedriver_linux64.zip'
        with open(file_test, 'wb') as output:
            output.write(res.content)
            pass
        # extract the downloaded file
        unzip_command = \
            'unzip -o ' \
            + file_test \
            + ' -d ' \
            + os.path.expanduser("~") \
            + '/'
        os.popen(unzip_command).read()
        # remove the zip file after extraction
        os.popen('rm ' + file_test).read()
        # get the file path to pass to the chromdriver
        driver_loc = os.path.expanduser("~") + '/chromedriver'

        # Selenium setup: headless Chrome, Window size needs to be
        # big enough, otherwise elements will not be found.
        options = webdriver.ChromeOptions()
        options.add_argument('headless')
        options.add_argument('disable-gpu')
        options.add_argument('window-size=1920,1080')
        driver = None

        connection_reset = True
        while connection_reset:
            connection_reset = False
            try:
                driver = webdriver.Chrome(
                    executable_path=driver_loc, chrome_options=options)
                pass
            except Exception as e:
                if e.errno == 104:
                    connection_reset = True
                    print("\nResetting connection...\n")
                    pass
                else:
                    raise Exception(e)
            pass

        driver.maximize_window()

        # Logs in
        driver.get(self.loginlink)
        driver.find_element_by_id('enterlogin').send_keys(self.username)
        driver.find_element_by_id('password').send_keys(self.password)
        driver.find_element_by_css_selector(
            "button.btn.btn-primary").click()
        time.sleep(2)

        # Captcha (if any)
        try:
            driver.find_element_by_id('recaptchaForm')

            # TODO: Solve reCaptcha
        except NoSuchElementException:
            pass

        # Check if logged in
        try:
            error_message = str(driver.find_element_by_css_selector(
                "div.form-msg.active").text)
            print(error_message)
            sys.exit(0)
        except NoSuchElementException:
            pass
        except Exception:
            print("Something went wrong during login.")
            sys.exit(0)

        # Clicking menu
        print("Click Finance")
        driver.find_element_by_id("menu2").\
            find_element_by_class_name("head").click()
        time.sleep(2)
        print("Click Add Funds")
        driver.find_element_by_id("menu2").\
            find_element_by_class_name("submenu").\
            find_element_by_tag_name("li").\
            find_element_by_tag_name("a").click()
        time.sleep(2)

        # Choosing cryptocurrency as payment option
        payment_methods = driver.find_element_by_id("listSection")\
            .find_elements_by_class_name("col")
        for payment_method in payment_methods:
            text = payment_method.find_element_by_tag_name("a")\
                .get_attribute("action-parameter")
            if text == "Bitcoins":
                payment_method.click()
                print("Click cryptocurrency")
                break

        time.sleep(2)

        # Choosing the correct cryptocurrency.
        cryptocurrencies = \
            driver.find_elements_by_class_name("grid-middle")
        for c in cryptocurrencies:
            text = c.find_element_by_class_name("col")
            if text is not None:
                if currency[0] in text.text:
                    button = c.find_element_by_class_name("col-3_xs-12")
                    button = button.find_element_by_css_selector(
                        "a.btn.btn-primary.btn-manager")
                    print("Click Select " + currency[0])
                    button.click()
                    break

        time.sleep(2)

        # Filling in the amount.
        print("Filling in $" + str(amount) + ".")
        form = driver.find_element_by_id("amountInput")
        form.clear()
        # The numbers need to be send one by one due to Selenium bug.
        for i in range(0, len(str(amount))):
            form.send_keys(str(amount)[i])
        time.sleep(1)
        print("Click Pay.")
        driver.find_element_by_id("paymentButton").\
            find_element_by_css_selector(
            "button.btn.btn-primary.btn-manager").click()

        # Waiting for status to become "waiting for transaction"
        print("Requesting status.")
        while True:
            time.sleep(3)
            status = driver.find_element_by_id(currency[2]+"status")
            if status.text == "Status: waiting for transaction":
                print("Done waiting")
                break

        # Finds Address
        address = driver.find_element_by_id("customSection")
        address = \
            address.find_element_by_css_selector("div.tac.font24").text

        # Finds Amount
        instructions = \
            driver.find_element_by_id("customSection").\
            find_element_by_css_selector("div.desc").\
            find_element_by_tag_name("div")
        amount = re.findall(
            "send (.*?)" + currency[1] + " to", instructions.text)[0]

        return {'amount': str(amount), 'address': str(address)}
