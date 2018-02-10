from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import io
import os
import subprocess
import sys
from argparse import ArgumentParser
from builtins import dict
from builtins import input
from builtins import round
from builtins import str
from os import path

from CaseInsensitiveDict import CaseInsensitiveDict
from future import standard_library

from cloudomate import wallet as bitcoin_wallet_util
from cloudomate.hoster.vpn.azirevpn import AzireVpn
from cloudomate.hoster.vpn.mullvad import MullVad
from cloudomate.util.installvpn_mullvad import InstallMullvad
from cloudomate.hoster.vpn.vpnac_purchase import vpnacVPNPurchaser
from cloudomate.hoster.vpn.torguard_purchase import torguardVPNPurchaser
from cloudomate.hoster.vps.blueangelhost import BlueAngelHost
from cloudomate.hoster.vps.ccihosting import CCIHosting
from cloudomate.hoster.vps.crowncloud import CrownCloud
from cloudomate.hoster.vps.linevast import LineVast
from cloudomate.hoster.vps.pulseservers import Pulseservers
from cloudomate.hoster.vps.undergroundprivate import UndergroundPrivate
from cloudomate.util.fakeuserscraper import UserScraper
from cloudomate.util.settings import Settings
from cloudomate.ethereum_wallet import Wallet as ethereum_wallet
from cloudomate.wallet import Wallet as bitcoin_wallet

standard_library.install_aliases()


def _map_providers_to_dict(provider_list):
    return CaseInsensitiveDict(dict((provider.get_metadata()[0], provider) for provider in provider_list))


types = ["vps", "vpn"]

providers = CaseInsensitiveDict({
    "vps": _map_providers_to_dict([
        BlueAngelHost,
        CCIHosting,
        CrownCloud,
        LineVast,
        Pulseservers,
        UndergroundPrivate,
    ]),
    "vpn": _map_providers_to_dict([
        AzireVpn,
        MullVad,
        vpnacVPNPurchaser,
        torguardVPNPurchaser,
    ])
})


def execute(cmd=sys.argv[1:]):
    parser = ArgumentParser(description="Cloudomate")

    subparsers = parser.add_subparsers(dest="type")

    add_agent_status_notifier(subparsers)
    add_captcha_manager(subparsers)
    add_vpn_parsers(subparsers)
    add_vpn_purchase(subparsers)
    add_vpn_status(subparsers)
    add_vpn_subscription_status(subparsers)
    add_vpn_turn_on(subparsers)
    add_vpn_turn_off(subparsers)
    add_vps_parsers(subparsers)
    add_wallet(subparsers)
    subparsers.required = True

    args = parser.parse_args(cmd)
    args.func(args)

def add_vpn_purchase(subparsers):
    parser_purchase = subparsers.add_parser("vpn-purchase", help="Purchase VPN")
    parser_purchase.set_defaults(func=vpn_purchase)
    parser_purchase.add_argument("provider", help="The specified provider", choices=providers['vpn'])
    parser_purchase.add_argument("-c","--coin", help="Choose the cryptocurrency used for purchasing.")
    parser_purchase.add_argument("-fm", "--feemultiplier", help="Choose the fee used for purchasing.")
    parser_purchase.add_argument("-a", "--accountnr", help="Choose the cryptocurrency used for purchasing.")
    parser_purchase.add_argument("-un", "--username", help="Choose the username.")
    parser_purchase.add_argument("-pw", "--password", help="Choose the password.")
    parser_purchase.add_argument("-r", help="Given username is already registered.", action="store_true")
    parser_purchase.add_argument("-f", help="Don't prompt for user confirmation", dest="noconfirm", action="store_true")

def add_vpn_subscription_status(subparsers):
    parser_subscription_status = subparsers.add_parser("vpn-subscription-status", help="Check status of the subscription of the VPN service")
    parser_subscription_status.set_defaults(func=vpn_subscription_status)
    parser_subscription_status.add_argument("provider", help="The specified provider", choices=providers['vpn'])

def add_vpn_status(subparsers):
    parser_vpn_status = subparsers.add_parser("vpn-status", help="Returns provider name of active VPN service if any.")
    parser_vpn_status.set_defaults(func=vpn_status)

def add_vpn_turn_on(subparsers):
    parser_turn_on = subparsers.add_parser("vpn-turn-on", help="Turn on specified VPN service.")
    parser_turn_on.set_defaults(func=vpn_turn_on)
    parser_turn_on.add_argument("provider", help="The specified provider", choices=providers['vpn'])
    parser_turn_on.add_argument("-c", "--country", help="The location of the server through which you would like to "
                                                         "router traffic")
    parser_turn_on.add_argument("-p", "--protocol", help="The protocol.")

def add_vpn_turn_off(subparsers):
    parser_turn_off = subparsers.add_parser("vpn-turn-off", help="Turn off active VPN service.")
    parser_turn_off.set_defaults(func=vpn_turn_off)
    parser_turn_off.add_argument("provider", help="The specified provider", choices=providers['vpn'])

def add_agent_status_notifier(subparser):
    parser_captcha = subparser.add_parser("agent-status-notifier", help="Status notifier of agent.")
    parser_captcha.set_defaults(type="agent_status_notifier")
    subparser_captcha = parser_captcha.add_subparsers(dest="command") #, help="Get account details"
    subparser_captcha.required = True

    status_parser = subparser_captcha.add_parser("status", help ="Get status of the notifier")
    status_parser.set_defaults(func=notifier_status)

    turnon_parser = subparser_captcha.add_parser("turnon", help ="Turn on the status notifier")
    turnon_parser.set_defaults(func=turnon_notifier)
    turnon_parser.add_argument("minutes", help="Amount of minutes.", type=int)
    turnon_parser.add_argument("recipient", help="Address where to send the email to")

    turnoff_parser = subparser_captcha.add_parser("turnoff", help="Turn off the status notifier.")
    turnoff_parser.set_defaults(func=turnoff_notifier)


def add_captcha_manager(subparser):
    parser_captcha = subparser.add_parser("captcha-manager", help="Manager of the captcha account.")
    parser_captcha.set_defaults(type="captcha_manager")
    subparser_captcha = parser_captcha.add_subparsers(dest="command")
    subparser_captcha.required = True

    view_amount_parser = subparser_captcha.add_parser("view-account", help ="Get account details")
    view_amount_parser.set_defaults(func=captcha_manager)

    get_balance_parser = subparser_captcha.add_parser("get-balance", help ="Get current balance")
    get_balance_parser.set_defaults(func=captcha_get_balance)

    reload_parser = subparser_captcha.add_parser("reload", help="Top up balance for anticaptcha account.")
    reload_parser.add_argument("amount", help="The amount to top up.")
    reload_parser.add_argument("-c", "--coin", help="The cryptocurrency to pay with.", default="btc")
    reload_parser.add_argument("-fm", "--feemultiplier", help="Choose the fee used for purchasing.")
    reload_parser.set_defaults(func=captcha_reload)
    pass

def turnon_notifier(args):
    print("turnon_notifier()")
    print(args)
    print(args.minutes)
    print(type(args.minutes))

def turnoff_notifier(args):
    print("turnoff_notifier()")
    print(args)


def notifier_status(args):
    print("notifier_status()")
    print(args)

def captcha_get_balance(args):
    print("captcha_get_balance()")
    print(args)

def captcha_reload(args):
    print("captcha_reload()")
    print(args)
    pass

def captcha_manager(args):
    print("captcha_manager()")
    print(args)

#TODO PHILIP
def vpnac_purchase_handler(args):
    pass

#TODO PHILIP
def torguard_purchase_handler(args):
    pass

#TODO KW DINESH
def mullvad_purchase_handler(args):
    settings = Settings()
    m = MullVad(settings)
    if settings.has_key('client', 'walletpath'):
        wallet = bitcoin_wallet(wallet_path=settings.get('client', 'walletpath'))
    else:
        wallet = bitcoin_wallet()

    m.purchase(wallet)

def add_wallet(subparsers):
    wallet_parsers = subparsers.add_parser("wallet")
    wallet_parsers.set_defaults(type="wallet")
    wallet_subparsers = wallet_parsers.add_subparsers(dest="wallet_type")
    #wallet_subparsers.add_argument("getbalance", help="Get balance of wallet.")
    wallet_subparsers.required = True

    add_ethereum_wallet(wallet_subparsers)
    add_bitcoin_wallet(wallet_subparsers)

def add_ethereum_wallet(subparsers):
    ethereum_parsers = subparsers.add_parser("ethereum")
    ethereum_parsers.set_defaults(type="wallet_type")
    ethereum_subparsers = ethereum_parsers.add_subparsers(dest="command")
    ethereum_subparsers.required = True

    add_parser_wallet_getbalance(ethereum_subparsers)
    add_parser_wallet_getaddress(ethereum_subparsers)
    add_parser_wallet_getprivatekey(ethereum_subparsers)
    add_parser_wallet_getfees(ethereum_subparsers)

def add_bitcoin_wallet(subparsers):
    bitcoin_parsers = subparsers.add_parser("bitcoin")
    bitcoin_parsers.set_defaults(type="wallet_type")
    bitcoin_subparsers = bitcoin_parsers.add_subparsers(dest="command")
    bitcoin_subparsers.required = True

    add_parser_wallet_getbalance(bitcoin_subparsers)
    add_parser_wallet_getaddress(bitcoin_subparsers)
    add_parser_wallet_getprivatekey(bitcoin_subparsers)
    add_parser_wallet_getfees(bitcoin_subparsers)

def add_parser_wallet_getbalance(subparsers):
    parser_getbalance = subparsers.add_parser("getbalance", help="Get balance of wallet.")
    parser_getbalance.set_defaults(type="command", func=wallet_getbalance)
    parser_getbalance.add_argument("hallo", help="This is a test method")
    parser_getbalance.add_argument("-a", "--armando", help="This is a test method")
    #parser_getbalance.add_argument('v', help="v")
    #parser_getbalance.set_argument('')
    pass

def add_parser_wallet_getaddress(subparsers):
    parser_getbalance = subparsers.add_parser("getaddress", help="Get address of wallet.")
    parser_getbalance.set_defaults(type="command", func=wallet_getaddress)
    pass

def add_parser_wallet_getprivatekey(subparsers):
    parser_getbalance = subparsers.add_parser("getprivatekey", help="Get private key of wallet.")
    parser_getbalance.set_defaults(type="command", func=wallet_getprivatekey)
    pass

def add_parser_wallet_getfees(subparsers):
    parser_getbalance = subparsers.add_parser("getfees", help="Get fees of wallet.")
    parser_getbalance.set_defaults(type="command", func=wallet_fees)
    pass

#TODO PHILIP
def wallet_getbalance(args):
    print(args)

    print("wallet_getbalance()")
    if args.wallet_type == "ethereum":
        print("ethereum_wallet: This can be used to call any method.")

#TODO PHILIP
def wallet_getaddress(args):
    print("wallet_getaddress()")
    if args.wallet_type == "ethereum":
        print("ethereum_wallet: This can be used to call any method.")

#TODO PHILIP
def wallet_getprivatekey(args):
    print("wallet_getprivatekey()")
    if args.wallet_type == "ethereum":
        print("ethereum_wallet: This can be used to call any method.")

#TODO PHILIP
def wallet_fees(args):
    print("wallet_getfees()")
    if args.wallet_type == "ethereum":
        print("ethereum_wallet: This can be used to call any method.")



def vpn_purchase(args):
    if args.provider == "torguard":
        torguard_purchase_handler(args)
    elif args.provider == "mullvad":
        mullvad_purchase_handler(args)
    elif args.provider == "azirevpn":
        pass
    elif args.provider == "vpnac":
        vpnac_purchase_handler(args)

# Checks the VPN subscription
def vpn_subscription_status(args):
    print(args)
    print("vpn_subscription_status()")
    pass

# Checks whether the VPN service is turned on or off.
def vpn_status(args):
    print(args)
    print("vpn_status()")
    pass

def vpn_turn_on(args):
    if args.provider == "torguard":
        torguard_turn_on_handler(args)
    elif args.provider == "mullvad":
        mullvad_turn_on_handler(args)
    elif args.provider == "azirevpn":
        pass
    elif args.provider == "vpnac":
        vpnac_turn_on_handler(args)


#TODO PHILIP
def torguard_turn_on_handler(args):
    pass

#TODO KW DINESH
def mullvad_turn_on_handler(args):
    m = InstallMullvad()

    if args.country is not None:
        m.setup_vpn(args.country)
    else:
        m.setup_vpn()

#TODO PHILIP
def vpnac_turn_on_handler(args):
    pass


def vpn_turn_off(args):
    if args.provider == "torguard":
        torguard_turn_off_handler(args)
    elif args.provider == "mullvad":
        mullvad_turn_off_handler()
    elif args.provider == "azirevpn":
        pass
    elif args.provider == "vpnac":
        vpnac_turn_off_handler(args)

#TODO PHILIP
def torguard_turn_off_handler(args):
    pass

#TODO KW DINESH
def mullvad_turn_off_handler():
    #Kills all active openvpn connections
    result = os.popen("sudo killall openvpn").read()

#TODO PHILIP
def vpnac_turn_off_handler(args):
    pass


def add_vpn_parsers(subparsers):
    vpn_parsers = subparsers.add_parser("vpn")
    vpn_parsers.set_defaults(type="vpn")
    vpn_subparsers = vpn_parsers.add_subparsers(dest="command")
    vpn_subparsers.required = True

    add_parser_list(vpn_subparsers, "vpn")
    add_parser_options(vpn_subparsers, "vpn")
    add_parser_purchase(vpn_subparsers, "vpn")
    add_parser_status(vpn_subparsers, "vpn")
    add_parser_info(vpn_subparsers, "vpn")


def add_vps_parsers(subparsers):
    vps_parsers = subparsers.add_parser("vps")
    vps_parsers.set_defaults(type="vps")
    vps_subparsers = vps_parsers.add_subparsers(dest="command")
    vps_subparsers.required = True

    add_parser_list(vps_subparsers, "vps")
    add_parser_options(vps_subparsers, "vps")
    add_parser_purchase(vps_subparsers, "vps")
    add_parser_status(vps_subparsers, "vps")
    add_parser_vps_setrootpw(vps_subparsers)
    add_parser_vps_get_ip(vps_subparsers)
    add_parser_vps_ssh(vps_subparsers)
    add_parser_info(vps_subparsers, "vps")


def add_parser_list(subparsers, provider_type):
    parser_list = subparsers.add_parser("list", help="List %s providers" % provider_type.upper())
    parser_list.set_defaults(func=list_providers)


def add_parser_options(subparsers, provider_type):
    parser_options = subparsers.add_parser("options", help="List %s provider configurations" % provider_type.upper())
    parser_options.add_argument("provider", help="The specified %s provider" % provider_type.upper(),
                                choices=providers[provider_type])
    parser_options.set_defaults(func=options)


def add_parser_purchase(subparsers, provider_type):
    parser_purchase = subparsers.add_parser("purchase", help="Purchase %s" % provider_type.upper())
    parser_purchase.set_defaults(func=purchase)
    parser_purchase.add_argument("provider", help="The specified provider", choices=providers[provider_type])

    parser_purchase.add_argument("-c", "--config", help="Set custom config file")
    parser_purchase.add_argument("-f", help="Don't prompt for user confirmation", dest="noconfirm", action="store_true")
    parser_purchase.add_argument("-e", "--email", help="email")
    parser_purchase.add_argument("-fn", "--firstname", help="first name")
    parser_purchase.add_argument("-ln", "--lastname", help="last name")
    parser_purchase.add_argument("-cn", "--companyname", help="company name")
    parser_purchase.add_argument("-pn", "--phonenumber", help="phone number", metavar="phonenumber")
    parser_purchase.add_argument("-pw", "--password", help="password")
    parser_purchase.add_argument("-a", "--address", help="address")
    parser_purchase.add_argument("-ct", "--city", help="city")
    parser_purchase.add_argument("-s", "--state", help="state")
    parser_purchase.add_argument("-cc", "--countrycode", help="country code")
    parser_purchase.add_argument("-z", "--zipcode", help="zipcode")
    parser_purchase.add_argument("--randomuser", action="store_true", help="Use random user info")

    if provider_type == 'vps':
        parser_purchase.add_argument("option", help="The %s option number (see options)" % provider_type.upper(),
                                     type=int)
        parser_purchase.add_argument("-rp", "--rootpw", help="root password")
        parser_purchase.add_argument("-ns1", "--ns1", help="ns1")
        parser_purchase.add_argument("-ns2", "--ns2", help="ns2")
        parser_purchase.add_argument("--hostname", help="hostname")


def add_parser_status(subparsers, provider_type):
    parser_status = subparsers.add_parser("status", help="Get the status of the %s services" % provider_type.upper())
    parser_status.add_argument("provider", help="The specified provider", nargs="?", choices=providers[provider_type])
    parser_status.add_argument("-e", "--email", help="The login email address")
    parser_status.add_argument("-pw", "--password", help="The login password")
    parser_status.set_defaults(func=status)


def add_parser_vps_get_ip(subparsers):
    parser_get_ip = subparsers.add_parser("getip", help="Get the IP address of the specified service")
    parser_get_ip.add_argument("provider", help="The specified provider", nargs="?", choices=providers['vps'])
    parser_get_ip.add_argument("-n", "--number", help="The number of the service get the IP address for")
    parser_get_ip.add_argument("-e", "--email", help="The login email address")
    parser_get_ip.add_argument("-pw", "--password", help="The login password")
    parser_get_ip.set_defaults(func=print_ip)


def add_parser_vps_ssh(subparsers):
    parser_ssh = subparsers.add_parser("ssh", help="SSH into an active service")
    parser_ssh.add_argument("provider", help="The specified provider", nargs="?", choices=providers['vps'])
    parser_ssh.add_argument("-n", "--number", help="The number of the service to SSH into")
    parser_ssh.add_argument("-e", "--email", help="The login email address")
    parser_ssh.add_argument("-pw", "--password", help="The login password")
    parser_ssh.add_argument("-p", "--rootpw", help="The root password used to login")
    parser_ssh.add_argument("-u", "--user", help="The user password used to login", default="root")
    parser_ssh.set_defaults(func=ssh)


def add_parser_info(subparsers, provider_type):
    parser_info = subparsers.add_parser("info",
                                        help="Get information of the specified %s service" % provider_type.upper())
    parser_info.add_argument("provider", help="The specified provider", nargs="?", choices=providers[provider_type])
    parser_info.add_argument("-n", "--number",
                             help="The number of the %s service to get the info of" % provider_type.upper())
    parser_info.add_argument("-e", "--email", help="The login email address")
    parser_info.add_argument("-pw", "--password", help="The login password")

    if provider_type == "vpn":
        parser_info.add_argument("-o", "--ovpn", help="Save the ovpn file to the specified location")

    parser_info.set_defaults(func=info)


def add_parser_vps_setrootpw(subparsers):
    parser_setrootpw = subparsers.add_parser("setrootpw", help="Set the root password of the last activated service")
    parser_setrootpw.add_argument("provider", help="The specified provider", choices=providers['vps'])
    parser_setrootpw.add_argument("root_password", help="The new root password")
    parser_setrootpw.add_argument("-n", "--number", help="The number of the VPS service to change the password for")
    parser_setrootpw.add_argument("-e", "--email", help="The login email address")
    parser_setrootpw.add_argument("-pw", "--password", help="The login password")
    parser_setrootpw.set_defaults(func=change_root_password_ssh)


def print_ip(args):
    provider = _get_provider(args)
    name, _ = provider.get_metadata()
    user_settings = _get_user_settings(args, name)

    provider_instance = provider(user_settings)
    configuration = provider_instance.get_configuration()
    print(configuration.ip)


def info(args):
    provider = _get_provider(args)
    name, _ = provider.get_metadata()
    user_settings = _get_user_settings(args, name)

    config = provider(user_settings).get_configuration()

    if args.type == "vps":
        print(("Info for " + name))
        _print_info_vps(config)
    elif args.type == "vpn":
        if args.ovpn:
            _save_info_vpn(config, args.ovpn)
        else:
            print(("Info for " + name))
            _print_info_vpn(config)


def status(args):
    provider = _get_provider(args)
    name, _ = provider.get_metadata()
    print(("Getting status for %s." % name))
    user_settings = _get_user_settings(args, name)
    p = provider(user_settings)
    s = p.get_status()

    if args.type == "vps":
        # If we don't currently support usage statistics for this provider
        if s.memory.used == -1.0:
            row = "{:20}" * 2
            print(row.format("Online", "Expiration"))
            print(row.format(str(s.online), s.expiration.isoformat()))
        else:
            row = "{:20}" * 5
            print(row.format("Memory used (GB)", "Storage used (GB)", "Bandwidth used (GB)", "Online", "Expiration"))
            print(row.format(
                '{:.2f}/{:.2f}'.format(s.memory.used, s.memory.total),
                '{:.2f}/{:.2f}'.format(s.storage.used, s.storage.total),
                '{:.2f}/{:.2f}'.format(s.bandwidth.used, s.bandwidth.total),
                str(s.online),
                s.expiration.isoformat()
            ))
    elif args.type == "vpn":
        row = "{:18}" * 2
        print(row.format("Online", "Expiration"))
        print(row.format(str(s.online), s.expiration.isoformat()))


def options(args):
    provider = _get_provider(args)

    if args.type == "vps":
        _options_vps(provider)
    elif args.type == "vpn":
        _options_vpn(provider)


def purchase(args):
    if "provider" not in vars(args):
        sys.exit(2)
    provider = _get_provider(args)
    name, _ = provider.get_metadata()
    user_settings = _get_user_settings(args, name)

    if args.randomuser:
        _merge_random_user_data(user_settings)

    if not _check_provider(provider, user_settings):
        print("Missing option")
        sys.exit(2)

    if args.type == 'vps':
        _purchase_vps(provider, user_settings, args)
    else:
        _purchase_vpn(provider, user_settings, args)


def _check_provider(provider, config):
    return config.verify_options(provider.get_required_settings())


def _merge_random_user_data(user_settings):
    usergenerator = UserScraper()
    randomuser = usergenerator.get_user()
    for section in randomuser.keys():
        for key in randomuser[section].keys():
            user_settings.put(section, key, randomuser[section][key])


def _get_user_settings(args, provider=None):
    user_settings = Settings()
    if 'config' in vars(args):
        user_settings.read_settings(filename=args.config)
    else:
        user_settings.read_settings()
    _merge_arguments(user_settings, provider, vars(args))
    return user_settings


def _merge_arguments(config, provider, args):
    for key in args:
        if args[key] is not None:
            config.put(provider, key, args[key])


def _purchase_vps(provider, user_settings, args):
    vps_option = args.option
    configurations = provider.get_options()
    if not 0 <= vps_option < len(configurations):
        print(('Specified configuration %s is not in range 0-%s' % (vps_option, len(configurations))))
        sys.exit(1)
    vps_option = configurations[vps_option]
    row_format = "{:15}" * 6
    print("Selected configuration:")
    print((row_format.format("Name", "CPU", "RAM", "Storage", "Bandwidth", "Price (USD)")))
    bandwidth = "Unlimited" if vps_option.bandwidth == sys.maxsize else vps_option.bandwidth
    print((row_format.format(
        vps_option.name,
        str(vps_option.cores),
        str(vps_option.memory),
        str(vps_option.storage),
        str(bandwidth),
        str(vps_option.price))))

    if args.noconfirm or (
            user_settings.has_key('client', 'noconfirm') and user_settings.get('client', "noconfirm") == "1"):
        choice = True
    else:
        choice = _confirmation("Purchase this option?", default="no")
    if choice:
        _register(provider, vps_option, user_settings)
    else:
        return False


def _purchase_vpn(provider, user_settings, args):
    print("Selected configuration:")
    options = provider.get_options()
    option = options[0]

    row = "{:18}" * 5
    print(row.format("Name", "Protocol", "Bandwidth", "Speed", "Price (USD)"))
    bandwidth = "Unlimited" if option.bandwidth == sys.maxsize else str(option.bandwidth)
    speed = "Unlimited" if option.speed == sys.maxsize else option.speed
    print(row.format(option.name, option.protocol, bandwidth, speed, str(option.price)))

    if args.noconfirm or (
            user_settings.has_key('client', 'noconfirm') and user_settings.get('client', "noconfirm") == "1"):
        choice = True
    else:
        choice = _confirmation("Purchase this option?", default="no")

    if choice:
        _register(provider, options[0], user_settings)
    else:
        return False


def _confirmation(message, default="y"):
    valid_options = {"yes": True, "ye": True, "y": True, "no": False, "n": False}
    if default in valid_options and valid_options[default] is True:
        prompt = "Y/n"
    elif default in valid_options and valid_options[default] is False:
        prompt = "y/N"
    else:
        prompt = "y/n"

    while True:
        try:
            choice = input("%s (%s) " % (message, prompt)).lower()
        except EOFError:
            sys.exit(2)
        if default is not None and choice == '':
            return valid_options[default]
        elif choice in valid_options:
            return valid_options[choice]
        print("Please respond with y[es] or n[o]")


def list_providers(args):
    _list_providers(args.type)


def _print_unknown_provider(provider):
    if provider:
        print(("Unknown provider: %s\n" % provider))
    else:
        print("Please specify a provider")


def _print_unknown_provider_type(provider_type):
    if provider_type:
        print(("Unknown provider type: %s\n" % provider_type))
    else:
        print("Please specify a provider type")


def _list_providers(provider_type):
    print("Providers:")
    for provider in providers[provider_type].values():
        name, website = provider.get_metadata()
        print("   {:15}{:30}".format(name, website))


def _list_provider_types():
    print("Provider Types:")
    for provider_type in types:
        print(("   {:15}".format(provider_type)))


def _options_vps(p):
    name, _ = p.get_metadata()
    print(("Options for %s:\n" % name))
    options = p.get_options()

    # Print heading
    row = "{:<5}" + "{:20}" * 8
    print(row.format("#", "Name", "Cores", "Memory (GB)", "Storage (GB)", "Bandwidth", "Connection (Gbit/s)",
                     "Est. Price (mBTC)", "Price (USD)"))

    for i, option in enumerate(options):
        bandwidth = "Unlimited" if option.bandwidth == sys.maxsize else str(option.bandwidth)

        # Calculate the estimated price
        rate = bitcoin_wallet_util.get_rate("USD")
        fee = bitcoin_wallet_util.get_network_fee()
        gateway = p.get_gateway()
        estimate = gateway.estimate_price(option.price * rate) + fee  # BTC
        estimate = round(1000 * estimate, 2)  # mBTC

        print(row.format(i, option.name, str(option.cores), str(option.memory), str(option.storage), bandwidth,
                         str(option.connection), str(estimate), str(option.price)))


def _options_vpn(provider):
    name, _ = provider.get_metadata()
    print(("Options for %s:\n" % name))
    options = provider.get_options()

    # Print heading
    row = "{:18}" * 6
    print(row.format("Name", "Protocol", "Bandwidth", "Speed", "Est. Price (mBTC)", "Price (USD)"))

    for option in options:
        bandwidth = "Unlimited" if option.bandwidth == sys.maxsize else str(option.bandwidth)
        speed = "Unlimited" if option.speed == sys.maxsize else option.speed

        # Calculate the estimated price
        rate = bitcoin_wallet_util.get_rate("USD")
        fee = bitcoin_wallet_util.get_network_fee()
        gateway = provider.get_gateway()
        estimate = gateway.estimate_price(option.price * rate) + fee  # BTC
        estimate = round(1000 * estimate, 2)  # mBTC

        print(row.format(option.name, option.protocol, bandwidth, speed, str(estimate), str(option.price)))


def _register(provider, vps_option, settings):
    # For now use standard wallet implementation through Electrum
    # If wallet path is defined in config, use that.
    if settings.has_key('client', 'walletpath'):
        wallet = bitcoin_wallet(wallet_path=settings.get('client', 'walletpath'))
    else:
        wallet = bitcoin_wallet()

    provider_instance = provider(settings)
    provider_instance.purchase(wallet, vps_option)


def _get_provider(args):
    provider_type = args.type
    provider = args.provider
    if not provider_type or provider_type not in providers:
        _print_unknown_provider_type(provider_type)
        _list_provider_types()
        sys.exit(2)

    if not provider or provider not in providers[provider_type]:
        _print_unknown_provider(provider)
        _list_providers(provider_type)
        sys.exit(2)
    return providers[provider_type][provider]


def ssh(args, command=None):
    provider = _get_provider(args)
    name, _ = provider.get_metadata()
    user_settings = _get_user_settings(args, name)
    config = provider(user_settings).get_configuration()
    commandline = ['sshpass', '-p', config.root_password, 'ssh', '-o', 'StrictHostKeyChecking=no',
                   'root@' + config.ip]

    if command:
        commandline.append(command)

    try:
        subprocess.call(commandline)
        return True
    except OSError as e:
        print(e)
        print('Install sshpass to use this command')
        return False


def change_root_password_ssh(args):
    if ssh(args, 'echo "root:' + args.root_password + '" | chpasswd'):
        provider = _get_provider(args)
        name, _ = provider.get_metadata()
        user_settings = _get_user_settings(args, name)
        user_settings.put("server", "root_password", args.root_password)
        user_settings.save_settings()
        print("Successfully set new root password in the config")
    else:
        print("Failed to set the new root password")
        sys.exit(2)


def _print_info_vps(info):
    row = "{:18}" * 2
    print(row.format("IP address", "Root password"))
    print(row.format(str(info.ip), str(info.root_password)))


def _print_info_vpn(provider_info):
    credentials = "credentials.conf"
    header = "=" * 20

    ovpn = provider_info.ovpn
    ovpn += "\nauth-user-pass " + credentials

    print("\ncredentials.conf")
    print(header)
    print(provider_info.username)
    print(provider_info.password)
    print("\nsettings.ovpn")
    print(header)
    print(ovpn)
    print(header)


def _save_info_vpn(info, ovpn):
    if not ovpn.endswith('.ovpn'):
        ovpn = ovpn + '.ovpn'

    ovpn = path.normcase(path.normpath(path.join(os.getcwd(), ovpn)))
    dir, _ = path.split(ovpn)
    credentials = 'credentials.conf'

    with io.open(ovpn, 'w', encoding='utf-8') as ovpn_file:
        ovpn_file.write(info.ovpn + '\nauth-user-pass ' + credentials)

    with io.open(path.join(dir, credentials), 'w', encoding='utf-8') as credentials_file:
        credentials_file.writelines([info.username + '\n', info.password])

    print("Saved VPN configuration to " + ovpn)


if __name__ == '__main__':
    execute()
