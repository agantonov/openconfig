#!/usr/bin/python3

import argparse
from jnpr.junos import Device
from jnpr.junos.utils.config import Config


def load_config(device, user, password, config, format):
    with Device(host=device, user=user, password=password).open() as dev:
        with Config(dev, mode="private") as cu:
            cu.load(path=config.name, format=format)
            cu.pdiff()
            cu.commit()


# execute
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Load Juniper Config")
    parser.add_argument(
        "config",
        type=open,
        help="Name of the file containing the configuration to be uploaded",
    )
    parser.add_argument("format", type=str, help="Configuration file format")
    parser.add_argument(
        "device", type=str, help="IP address or domain name of the Juniper router"
    )
    parser.add_argument("-u", "--user", type=str, help="User name")
    parser.add_argument("-p", "--password", type=str, help="Password")
    #    parser.add_argument('-k','--key', type=str, help='SSH private key file')

    args = parser.parse_args()

    load_config(**vars(args))
else:
    pass
