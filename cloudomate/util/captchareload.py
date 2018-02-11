import time
import re
import sys
from selenium import webdriver
from cloudomate.util.recaptchasolver import reCaptchaSolver
from selenium.common.exceptions import NoSuchElementException

class anticaptcha:

    loginlink = "https://anti-captcha.com/clients/entrance/login"
    username = ""
    password = ""

    def __init(self, login_username, login_password):
        self.username = login_username
        self.password = login_password

    # Use this method for purchasing with Bitcoin.
    def purchase_bitcoin(self, amount=10):
        try:
            dict = self._return_address(["Bitcoin", "BTC", "btc"], amount)
            amount = dict['amount']
            address = dict['address']

            print("Paying " + amount + "BTC to " + address)
            #TODO: Pay with bitcoin


        except Exception as e:
            print("Error " + str(e) + "Try again. It it still does not work, "
                                      "website might have been updated, update script.")

    # Use this method for purchasing with Litecoin.
    def purchase_litecoin(self, amount=10):
        try:
            dict = self._return_address(["Litecoin", "LTC", "ltc"], amount)
            amount = dict['amount']
            address = dict['address']

            print("Paying " + amount + "LTC to " + address)
            print("LTC wallet not implemented (yet).")
            sys.exit(0)

        except Exception:
            print("Something went wrong. Try again. It it still does not work, update script.")

    # Use this method for purchasing with DASH.
    def purchase_dash(self, amount=10):
        try:
            dict = self._return_address(["DASH", "DASH", "dash"], amount)
            amount = dict['amount']
            address = dict['address']

            print("Paying " + amount + "DASH to " + address)
            print("DASH wallet not implemented (yet).")
            sys.exit(0)

        except Exception:
            print("Something went wrong. Try again. It it still does not work, update script.")

    # Returns the address of the given currency.
    def _return_address(self, currency, amount=10):
        # Selenium setup: headless Chrome, Window size needs to be big enough, otherwise elements will not be found.

        # Download the appropriate executable chromedirver and place this in the folder for the script to access
        print("\nsetting up chrome-driver...")
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

        options = webdriver.ChromeOptions()
        options.add_argument('headless')
        options.add_argument('disable-gpu');
        options.add_argument('window-size=1920,1080');
        driver = webdriver.Chrome(executable_path=driver_loc, chrome_options=options)
        driver.maximize_window()

        # Logs in
        driver.get(self.loginlink)
        driver.find_element_by_id('enterlogin').send_keys(self.username)
        driver.find_element_by_id('password').send_keys(self.password)
        driver.find_element_by_css_selector("button.btn.btn-primary").click()
        time.sleep(2)

        # Captcha (if any)
        captcha_element = None
        try:
            captcha_element = driver.find_element_by_id('recaptchaForm')

            #TODO: Solve reCaptcha
            #captcha_element = captcha_element.find_element_by_class_name('g-recaptcha')
            #data_sitekey = captcha_element.get_attribute('data-sitekey')
            #print(data_sitekey)
            #response = webdriver.request('POST', )
            #print(response)
        except NoSuchElementException: # If there is no CAPTCHA to solve.
            pass

        # Check if logged in
        try:
            error_message = str(driver.find_element_by_css_selector("div.form-msg.active").text)
            print(error_message)
            sys.exit(0)
        except NoSuchElementException:
            pass # No error message found.
        except Exception:
            print("Something went wrong during login.")
            sys.exit(0)

        # Clicking menu
        print("Click Finance")
        driver.find_element_by_id("menu2").find_element_by_class_name("head").click()
        time.sleep(2)
        print("Click Add Funds")
        driver.find_element_by_id("menu2").find_element_by_class_name("submenu").\
            find_element_by_tag_name("li").find_element_by_tag_name("a").click()
        time.sleep(2)

        # Choosing cryptocurrency as payment option
        payment_methods = driver.find_element_by_id("listSection").find_elements_by_class_name("col")
        for payment_method in payment_methods:
            text = payment_method.find_element_by_tag_name("a").get_attribute("action-parameter")
            if text == "Bitcoins":
                payment_method.click()
                print("Click cryptocurrency")
                break

        time.sleep(2)

        # Choosing the correct cryptocurrency.
        cryptocurrencies = driver.find_elements_by_class_name("grid-middle")
        for c in cryptocurrencies:
            text = c.find_element_by_class_name("col")
            if text is not None:
                if currency[0] in text.text:
                    button = c.find_element_by_class_name("col-3_xs-12")
                    button = button.find_element_by_css_selector("a.btn.btn-primary.btn-manager")
                    print("Click Select " + currency[0])
                    button.click()
                    break

        time.sleep(2)

        # Filling in the amount.
        print("Filling in $" + str(amount) + ".")
        form = driver.find_element_by_id("amountInput")
        form.clear()
        for i in range(0, len(str(amount))): # Because of a small bug, the numbers need to be send one by one.
            form.send_keys(str(amount)[i])
        time.sleep(1)
        print("Click Pay.")
        driver.find_element_by_id("paymentButton").find_element_by_css_selector("button.btn.btn-primary.btn-manager")\
            .click()

        # Waiting for status to become "waiting for transaction"
        print("Requesting status.")
        while(True):
            time.sleep(3)
            status = driver.find_element_by_id(currency[2]+"status")
            if status.text == "Status: waiting for transaction":
                print("Done waiting")
                break

        # Finds Address
        address = driver.find_element_by_id("customSection")
        address = address.find_element_by_css_selector("div.tac.font24").text

        # Finds Amount
        instructions = driver.find_element_by_id("customSection").find_element_by_css_selector("div.desc").\
            find_element_by_tag_name("div")
        amount = re.findall("send (.*?)" + currency[1] + " to", instructions.text)[0]

        return {'amount' : str(amount), 'address' : str(address)}

if __name__ == "__main__":
    a = anticaptcha()
    a.purchase_bitcoin()
