import configparser
import logging
import random

import requests


DISCOVERY_SERVICES = [
    'https://ip.seeip.org/jsonip',
    'https://api.my-ip.io/ip.json',
    'http://ifconfig.co/json',
    'https://api.myip.com',
    'https://api.ipify.org?format=json',
]


ZONEEDIT_API = {
    'url': 'https://api.cp.zoneedit.com/dyn/ez-ipupdate.php',
    'params': {
        'action': 'edit',
        'myip': None,
        'wildcard': 'ON',
        'partner': 'zoneedit',
        'hostname': None
    },
    'headers': {
        'Host': 'api.cp.zoneedit.com'
    }
}


logging.basicConfig(filename='update-dns.log', level=logging.INFO)


def get_my_ip():
    urls = list(DISCOVERY_SERVICES)
    random.shuffle(urls)
    for service in urls:
        try:
            response = requests.get(service)
        except ConnectionError as err:
            logging.warning('URL {} failed with {}'.format(service, err))
            pass
        else:
            ip = response.json()['ip']
            logging.info('IP {} obtained from {}'.format(ip, service))
            return ip


def do_update(ip, config):
    for name in config['names']:
        url = ZONEEDIT_API['url']
        params = ZONEEDIT_API['params']
        params['myip'] = ip
        params['hostname'] = name
        headers = ZONEEDIT_API['headers']
        auth = config['user'], config['token']
        response = requests.get(url, params, headers=headers, auth=auth)
        if response.status_code == 200:
            logging.info(
                'Update of {} succeeded\n'.format(name) +
                response.content.decode('utf-8').strip()
            )
        else:
            logging.error(
                'Update of {} failed with code {}\n'.format(name, response.status_code) +
                response.content.decode('utf-8').strip()
            )


def get_config():
    cfg = configparser.ConfigParser()
    cfg.read('private.ini')
    return {
        'names': cfg['default'].get('names', '').split(),
        'user': cfg['default']['user'],
        'token': cfg['default']['token']
    }


config = get_config()
ip = get_my_ip()
do_update(ip, config)
