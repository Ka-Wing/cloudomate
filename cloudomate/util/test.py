from cloudomate.util.settings import Settings
from cloudomate.hoster.vpn.mullvad import MullVad
from cloudomate.util.installvpn_mullvad import InstallMullvad
from cloudomate.wallet import Wallet as btc_wallet

class test:

    def purchase(self):
        coin = "eth"
        feemultiplier = "0"
        accountnr = "0"
        username = "a"
        password = "b"
        r = False
        f = False

        settings = Settings()
        m = MullVad(settings)

        if settings.has_key('client', 'walletpath'):
            w = btc_wallet(wallet_path=settings.get('client', 'walletpath'))
        else:
            w = btc_wallet()

        m.purchase(w)

    def install(self):
        m = InstallMullvad()
        country = "nl"
        m.setup_vpn(country)


if __name__ == "__main__":
    i = test()
    i.purchase()
    pass
