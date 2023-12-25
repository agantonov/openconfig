#!/usr/bin/python3

import argparse
from jnpr.junos import Device
from jnpr.junos.utils.config import Config
from lxml import etree

def read_config():
    parser = argparse.ArgumentParser(description='Read Juniper Config')    
    parser.add_argument('-o','--output', type=argparse.FileType('w'), help='Write output to a file')
    parser.add_argument('-m','--model', type=str, help='YANG data model: custom, ietf, openconfig')
    parser.add_argument('-f','--filter', type=str, help='return a specific XML subtree')
    parser.add_argument('format', type=str, help='Configuration output format: xml, text, set, json')
    parser.add_argument('device', type=str, help='IP address or domain name of the Juniper router')
    parser.add_argument('-u','--user', type=str, help='User name')
    parser.add_argument('-p','--passwd', type=str, help='Password')
#    parser.add_argument('-k','--key', type=str, help='SSH private key file')

    args = parser.parse_args()

    with (Device(host=args.device, user=args.user, password=args.passwd).open()) as dev:
        data = dev.rpc.get_config(filter_xml=args.filter, model=args.model, options={'format':args.format})
        if args.format != 'json':
            data = etree.tostring(data, encoding='unicode', pretty_print=True)
        if args.output:
            with open(args.output.name, 'w') as file:
                file.write(data)
        else:
            print (data)

# execute
if __name__ == "__main__":
    read_config()
else:
    pass
