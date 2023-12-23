#!/usr/bin/python3

import argparse
from jnpr.junos import Device
from jnpr.junos.utils.config import Config

def load_config():
    parser = argparse.ArgumentParser(description='Load Juniper Config')    
    parser.add_argument('config', type=open, help='Name of the file with configuration to be uploaded')
    parser.add_argument('format', type=str, help='Configuration file format')
    parser.add_argument('device', type=str, help='IP address or domain name of Juniper router')
    parser.add_argument('-u','--user', type=str, help='User name')
    parser.add_argument('-p','--passwd', type=str, help='Password')
#    parser.add_argument('-k','--key', type=str, help='SSH private key file')

    args = parser.parse_args()

    with (Device(host=args.device, user=args.user, password=args.passwd).open()) as dev:
        with Config(dev, mode='private') as cu:
            cu.load(path=args.config.name, format=args.format)
            cu.pdiff()
            cu.commit()

# execute
if __name__ == "__main__":
    load_config()
else:
    pass