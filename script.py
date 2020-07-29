#!/bin/python3

import requests
from urllib.request import urlopen
from xml.etree import ElementTree as ET
from datetime import datetime


def get_ip():
    '''
    Return this computer's public IP
    '''

    with urlopen('https://api.ipify.org') as response:
        return response.read().decode('utf-8')


ip = get_ip()
print(f'My public IP is {ip}')

comment = f'Updated IP to {ip} on {datetime.now().strftime("%m/%d/%Y-%H:%M:%S")}'
print(f'Submitting comment: {comment}')

xmlns = 'https://route53.amazonaws.com/doc/2013-04-01/'  # AWS Route 53 XML namespace


def get_xml(myip, comment):
    '''
    Load the XML template and replace the necessary fields, then
    return the element tree root.
    '''

    tree = ET.ElementTree(file="request.xml")
    root = tree.getroot()

    # Update the comment
    comment_path = f'.//{{{xmlns}}}Comment'
    comment_els = root.findall(comment_path)
    if not comment_els:
        raise Exception(
            f'could not find Comment element with path: {comment_path}')
    comment_el = comment_els[0]
    comment_el.text = comment

    # Update the record's IP
    ip_path = f'.//{{{xmlns}}}ResourceRecord/{{{xmlns}}}Value'
    ip_els = root.findall(ip_path)
    if not ip_els:
        raise Exception(f'could not find IP element with path: {ip_path}')
    ip_el = ip_els[0]
    ip_el.text = myip

    return root


xml = get_xml(ip, comment)
xmlbytes = ET.tostring(xml, xml_declaration=True,
                       encoding="UTF-8", default_namespace=xmlns)
xmlstr = xmlbytes.decode('utf-8')

# POST /2013-04-01/hostedzone/Z2BTS599RFFOO/rrset HTTP/1.1
