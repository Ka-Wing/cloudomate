from codecs import open
from os import path
import sys
import os
from setuptools import setup, find_packages

options_ = sys.argv

if len(options_) > 1:
    if options_[1] == 'install':

        #currently set to $HOME/.config
        agent_config_dir = os.path.expanduser("~") + '/.config'
        
        if os.path.isdir(agent_config_dir) == False:
            print("Creating dir " + agent_config_dir + " ....")
            os.popen('mkdir ' + agent_config_dir).read()
        else:
            print("\ndir '" + agent_config_dir + "' has already been created ... (Perhaps Server already had an agent installed?...)")


        #Agent needs a starting captcha account (stored in config_captcha_account.cfg), can be changed using the captcha account manager
        print("\nCreating agent's starting captcha account...")
        print("\n\nCopying agent's config_captcha_account.cfg to $HOME/.config")
        os.popen('cp config_captcha_account.cfg $HOME/.config/config_captcha_account.cfg').read()


        #Ip address info 
        print("\nGenerating ip-address info file $HOME/.config/server-ip-address.txt")
        starting_ipv4address = os.popen('curl ipv4bot.whatismyipaddress.com').read()
        server_ip_address_file = os.path.expanduser("~") + '/.config/server-ip-address.txt'
        tempfile = open(server_ip_address_file, 'w')
        tempfile.write(starting_ipv4address)
        tempfile.close()

        #Uniquely identifying agent information
        print("\n\nGenerating Agent identifier")
        agent_temp_hostname = os.popen("hostname").read() + '-' + starting_ipv4address
        #remove newlines, tabs, spaces etc..
        agent_temp_hostname = agent_temp_hostname.replace('\n', '').replace('\r', '')
        print("\n\nCurrent generated Agent Id: " + agent_temp_hostname)
        temp_agent_id_file = os.path.expanduser("~") + '/.config/cloudomate_agent_id.txt'
        tempfile = open(temp_agent_id_file, 'w')
        tempfile.write(agent_temp_hostname)
        tempfile.close()

        #Check wether to print out instalation results
        q_mode = False
        if len(options_) > 2:
            if options_[2] == '-q':
                q_mode = True

        print("\nstarting dependency installing process....")
        #dependecy libraries
        print("\ninstalling  python 3 dependences...\n")
        test_ = os.popen('apt-get install -y libssl-dev build-essential automake pkg-config libtool libffi-dev libgmp-dev libyaml-cpp-dev').read()
        if q_mode == False : print(test_)
        #curl dependency
        print("\ninstalling  curl...\n")
        test_ = os.popen('apt-get install -y curl').read()
        if q_mode == False : print(test_)
        #install pip for python 3
        print("\ninstalling pip for python 3...\n")
        test_ = os.popen('apt-get install -y python3-pip').read()
        if q_mode == False : print(test_)
        #install selenium library for python 3
        print("\ninstalling selenium for python3....\n")
        test_ = os.popen('pip3 install selenium').read()
        if q_mode == False : print(test_)
        #install python-crontab library for python 3
        print("\ninstalling python-crontab for python3....\n")
        test_ = os.popen('pip3 install python-crontab').read()
        if q_mode == False : print(test_)
        #
        print("\ninstalling future for python3....\n")
        test_ = os.popen('pip3 install future').read()
        if q_mode == False : print(test_)
        #
        print("\ninstalling cryptocompy for python3....\n")
        test_ = os.popen('pip3 install cryptocompy').read()
        if q_mode == False : print(test_)
        #
        print("\ninstalling rlp for python3....\n")
        test_ = os.popen('pip3 install rlp').read()
        if q_mode == False : print(test_)
        #
        print("\ninstalling web3 python3....\n")
        test_ = os.popen('pip3 install web3').read()
        if q_mode == False : print(test_)
        #
        print("\ninstalling ethereum python3....\n")
        test_ = os.popen('pip3 install ethereum').read()
        if q_mode == False : print(test_)
        #install zip
        print("\ninstalling zip....\n")
        test_ = os.popen('apt-get install -y zip').read()
        if q_mode == False : print(test_)
        #install openvpn
        print("\ninstalling openvpn....\n")
        test_ = os.popen('apt-get install -y openvpn').read()
        if q_mode == False : print(test_)
        #install chromedriver
        print("\ninstalling chromedriver....\n")
        test_ = os.popen('apt-get install -y chromium-chromedriver').read()
        if q_mode == False : print(test_)
        pass
here = path.abspath(path.dirname(__file__))

with open(path.join(here, 'README.rst'), encoding='utf-8') as f:
    long_description = f.read()

if sys.version_info.major == 2:
    package_data = {
        b'cloudomate': [],
    }
else:
    package_data = {
        'cloudomate': [],
    }

setup(
    name='cloudomate',

    version='1.0.0',

    description='Automate buying VPS instances with Bitcoin',
    long_description=long_description,

    url='https://github.com/Jaapp-/Cloudomate',

    author='PlebNet',
    author_email='plebnet@heijligers.me',

    license='LGPLv3',

    classifiers=[
        'Development Status :: 3 - Alpha',

        'Intended Audience :: Developers',
        'Topic :: System :: Installation/Setup',
        'Topic :: Software Development :: Libraries :: Python Modules',

        'License :: OSI Approved :: GNU Lesser General Public License v3 (LGPLv3)',

        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.6',

        'Operating System :: POSIX :: Linux',
        'Operating System :: MacOS',
    ],

    keywords='vps bitcoin',

    packages=find_packages(exclude=['docs', 'test']),

    install_requires=[
        'appdirs',
        'lxml',
        'MechanicalSoup',
        'bs4',
        'forex-python',
        'parameterized',
        'fake-useragent',
        'CaseInsensitiveDict',
        'ConfigParser',
        'future',
        'requests[security]'
    ],

    extras_require={
        'dev': [],
        'test': ['mock', 'parameterized'],
    },

    package_data=package_data,

    entry_points={
        'console_scripts': [
            'cloudomate=cloudomate.cmdline:execute',
        ],
    },
)
