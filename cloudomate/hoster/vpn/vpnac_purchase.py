from selenium.common.exceptions import NoSuchElementException

from cloudomate.hoster.vpn.coinpayments_vpn_provider import CoinpaymentsVpnProvider
import time
#from cloudomate.bitcoin_wallet import Wallet as BitcoinWallet
#from cloudomate.litcoin_wallet import Wallet as LitcoinWallet
#from cloudomate.ethereum_wallet import Wallet as EthereumWallet
#from cloudomate import bitcoin_wallet as B_wallet_util
# from cloudomate import litcoin_wallet as L_wallet_util
#from cloudomate import ethereum_wallet as E_wallet_util
import os

class VpnacVPNPurchaser(CoinpaymentsVpnProvider):

    PURCHASE_URL = 'https://vpn.ac/vpn-accounts'
    COINPAYMENTS_URL = 'https://www.coinpayments.net/index.php?cmd=checkout'

    saveUserLoginFile = \
        os.path.expanduser("~") \
        + '/.config/vpnac_login.txt'

    @staticmethod
    def get_metadata():
        return "VpnAc", "https://vpn.ac"

    @staticmethod
    def get_gateway():
        return None

    @staticmethod
    def get_required_settings():
        return {"user": ["username", "password"]}


    def go_to_coinpayments_page(self, user_settings):
        self.driver.get(self.PURCHASE_URL)
        self.driver.find_element_by_xpath('//*[@id="content"]/main/article[1]/div/div[1]/div[1]/div/div[3]/a').click()
        time.sleep(1)

        if user_settings.get("registered") == "1":
            self.driver.find_element_by_xpath('//*[@id="existingcust"]').click()
            time.sleep(1)
            self.driver.find_element_by_xpath('//*[@id="loginfrm"]/table/tbody/tr[1]/td[2]/input'). \
                send_keys(user_settings.get("email"))
            self.driver.find_element_by_xpath('//*[@id="loginfrm"]/table/tbody/tr[2]/td[2]/input'). \
                send_keys(user_settings.get("password"))

        else:
            self.driver.find_element_by_xpath('//*[@id="signupfrm"]/table/tbody/tr[3]/td[2]/input'). \
                send_keys(user_settings.get("email"))
            self.driver.find_element_by_xpath('//*[@id="newpw"]').send_keys(user_settings.get("password"))
            self.driver.find_element_by_xpath('//*[@id="signupfrm"]/table/tbody/tr[5]/td[2]/input'). \
                send_keys(user_settings.get("password"))

        time.sleep(1)
        self.driver.find_element_by_xpath('//*[@id="pgbtncoinpayments"]').click()
        time.sleep(1)
        self.driver.find_element_by_xpath('//*[@id="whmcsorderfrm"]/div[4]/input').click()

        # Checks if any error message can be found on the webpage. If so, print error message.
        error_message = False
        try:
            errorbox = self.driver.find_element_by_class_name("errorbox")
            error_message = True
        except NoSuchElementException:
            pass # No errors found.

        if error_message:
            print("Website returned an error during order placing: \"" + errorbox.text + "\"")
            exit(0)

        time.sleep(2)
        if (user_settings.get("registered") == "0"):
            pass  # Change registration to 1 for ever.
