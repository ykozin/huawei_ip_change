#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# Yevgeny Kozin (c) 2018
# https://twitter.com/YevgenyKozin
#
import requests
import ipaddress
import re
from xml.etree import ElementTree

# Get current modem IP address
while True:
    try:
        raw_ip = input("Please enter CURRENT modem IP address: ")
        cur_ip = ipaddress.ip_address(raw_ip)
        break
    except ValueError:
        print('"{}" does not appear to be an IPv4 or IPv6 address'.format(raw_ip))
        continue

# Get credentials
try:
    response = requests.get('http://{}/api/webserver/SesTokInfo'.format(cur_ip))

    if not response.status_code == 200:
        raise
except:
    raise SystemExit('Error connect!')

try:
    tree = ElementTree.fromstring(response.content)
    session_id = tree.find('./SesInfo').text.split('=')[1]
    token = tree.find('./TokInfo').text
except:
    raise SystemExit('Response error!')

# Get DHCP settings
cookies = {'SessionID': session_id}
headers = {'__RequestVerificationToken': token, 'content-type': 'text/xml'}
response = requests.get('http://{}/api/dhcp/settings'.format(cur_ip), cookies=cookies, headers=headers)

tree = ElementTree.fromstring(response.content)
mask = tree.find('./DhcpLanNetmask').text
cur_network = ipaddress.ip_network('{}/{}'.format(re.sub('1$', '0', cur_ip.exploded), mask))

# Set new IP address
while True:
    try:
        raw_ip = input("Please enter NEW modem IP address: ")
        new_ip = ipaddress.ip_address(raw_ip)
        break
    except ValueError:
        print('"{}" does not appear to be an IPv4 or IPv6 address'.format(raw_ip))
        continue


cut_cur_ip = ('.'.join(cur_ip.exploded.split('.')[:3]))
cut_new_ip = ('.'.join(new_ip.exploded.split('.')[:3]))

data = response.text.replace(cut_cur_ip, cut_new_ip)

requests.post('http://{}/api/dhcp/settings'.format(cur_ip), data=data, cookies=cookies, headers=headers)

print('Ok.')
