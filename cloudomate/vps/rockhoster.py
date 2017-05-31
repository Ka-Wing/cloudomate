import itertools
from bs4 import BeautifulSoup

from cloudomate.gateway.coinbase import extract_info
from cloudomate.vps.hoster import Hoster
from cloudomate.vps.vpsoption import VpsOption


class RockHoster(Hoster):
    name = "rockhoster"
    website = "https://rockhoster.com/"
    required_settings = [
        'firstname',
        'lastname',
        'email',
        'address',
        'city',
        'state',
        'zipcode',
        'phonenumber',
        'password',
        'hostname',
        'rootpw']
    clientarea_url = 'https://rockhoster.com/cloud/clientarea.php'
    client_data_url = 'https://rockhoster.com/cloud/modules/servers/solusvmpro/get_client_data.php'

    def __init__(self):
        super(RockHoster, self).__init__()

    def register(self, user_settings, vps_option):
        """
        Register RockHoster provider, pay through CoinBase
        :param user_settings: 
        :param vps_option: 
        :return: 
        """
        self.br.open(vps_option.purchase_url)
        self.br.select_form(nr=4)
        self.fill_in_server_form(user_settings)
        self.br.submit()
        self.br.open('https://rockhoster.com/cloud/cart.php?a=view')
        self.br.follow_link(text_regex=r"Checkout")
        self.br.select_form(nr=4)
        self.fill_in_user_form(user_settings)
        self.br.submit()
        page = self.br.follow_link(url_regex="coinbase")
        amount, address = extract_info(page.geturl())
        return amount, address

    def fill_in_server_form(self, user_settings):
        """
        Fills in the form containing server configuration.
        :param user_settings: settings
        :return: 
        """
        self.br.form['hostname'] = user_settings.get("hostname")
        self.br.form['rootpw'] = user_settings.get("rootpw")
        self.br.form['ns1prefix'] = user_settings.get("ns1")
        self.br.form['ns2prefix'] = user_settings.get("ns2")
        self.br.form['configoption[20]'] = ['53']  # Paris
        self.br.form['configoption[2]'] = ['13']
        self.br.form.new_control('text', 'ajax', {'name': 'ajax', 'value': 1})
        self.br.form.new_control('text', 'a', {'name': 'a', 'value': 'confproduct'})
        self.br.form.method = "POST"

    def fill_in_user_form(self, user_settings):
        """
        Fills in the form with user information.
        :param user_settings: settings
        :return: 
        """
        self.br.form['firstname'] = user_settings.get("firstname")
        self.br.form['lastname'] = user_settings.get("lastname")
        self.br.form['email'] = user_settings.get("email")
        self.br.form['phonenumber'] = user_settings.get("phonenumber")
        self.br.form['companyname'] = user_settings.get("companyname")
        self.br.form['address1'] = user_settings.get("address")
        self.br.form['city'] = user_settings.get("city")
        countrycode = user_settings.get("countrycode")

        # State input changes based on country: USA (default) -> Select, Other -> Text
        self.br.form['state'] = user_settings.get("state")
        self.br.form['postcode'] = user_settings.get("zipcode")
        self.br.form['country'] = [countrycode]
        self.br.form['password'] = user_settings.get("password")
        self.br.form['password2'] = user_settings.get("password")
        self.br.form['paymentmethod'] = ['coinbase']
        self.br.find_control('accepttos').items[0].selected = True

    def start(self):
        """
        Linux (OpenVZ) and Windows (KVM) pages are slightly different, therefore their pages are parsed by different 
        methoods. Windows configurations allow a selection of Linux distributions, but not vice-versa.
        :return: possible configurations.
        """
        openvz_hosting_page = self.br.open("https://rockhoster.com/linux.html")
        options = self.parse_openvz_hosting(openvz_hosting_page.get_data())

        kvm_hosting_page = self.br.open("https://rockhoster.com/windows-vps")
        options = itertools.chain(options, self.parse_kvm_hosting(kvm_hosting_page.get_data()))
        return options

    def parse_openvz_hosting(self, page):
        soup = BeautifulSoup(page, "lxml")
        details = soup.findAll('div', {'class': 'pacdetails'})
        for column in details:
            yield self.parse_openvz_option(column)

    @staticmethod
    def parse_openvz_option(column):
        elements = column.findAll("li")
        option = VpsOption()
        storage = elements[0].text.split(": ")[1]
        option.storage = storage.split("G")[0]
        ram = elements[1].text.split("G")[0]
        option.ram = ram.split("RAM: ")[1]
        option.bandwidth = 'unmetered'
        option.cpu = elements[3].text.split(':')[1]
        connection = elements[5].text.split(": ")[1]
        option.connection = connection.split('M')[0]
        option.name = column.div.h2.string
        price = column.div.strong.text
        price = price.split('$')[1]
        option.price = price.split('/')[0]
        option.purchase_url = column.find('div', {'class': 'bottom'}).a['href']
        return option

    def parse_kvm_hosting(self, page):
        soup = BeautifulSoup(page, "lxml")
        details = soup.findAll('div', {'class': 'pacdetails'})
        for column in details:
            yield self.parse_kvm_option(column)

    @staticmethod
    def parse_kvm_option(column):
        elements = column.findAll("li")
        option = VpsOption()
        storage = elements[0].text.split(": ")[1]
        option.storage = storage.split('G')[0]
        ram = elements[1].text.split("RAM:")[1].strip()
        ram = int(ram.split('M')[0])/1024
        option.ram = str(ram)
        option.bandwidth = 'unmetered'
        option.cpu = elements[3].text.split(':')[1]
        option.connection = '1000'
        option.name = column.div.h2.string
        option.price = column.div.strong.text
        option.price = option.price.split('$')[1]
        option.price = option.price.split('/')[0]
        option.purchase_url = column.find('div', {'class': 'bottom'}).a['href']
        return option

    def get_status(self, user_settings):
        self._clientarea_get_status(user_settings, self.clientarea_url)

    def set_rootpw(self, user_settings):
        self._clientarea_set_rootpw(user_settings, self.clientarea_url)

    def get_ip(self, user_settings):
        self._clientarea_get_ip(user_settings, self.clientarea_url, self.client_data_url)