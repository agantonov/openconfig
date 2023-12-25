#!/usr/bin/python3

import argparse
from jnpr.junos import Device
from lxml import etree


def read_config(device, user, password, model, format, filter, output):
    with Device(device, user, password) as dev:
        data = dev.rpc.get_config(
            filter_xml=filter, model=model, options={"format": format}
        )
    if format != "json":
        data = etree.tostring(data, encoding="unicode", pretty_print=True)
    if output is None:
        print(data)
        return

    with open(output.name, "w", encoding="utf-8") as file:
        file.write(data)


# execute
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Read Juniper Config")
    parser.add_argument(
        "-o",
        "--output",
        default=None,
        type=argparse.FileType("w"),
        help="Write output to a file",
    )
    parser.add_argument(
        "-m", "--model", type=str, help="YANG data model: custom, ietf, openconfig"
    )
    parser.add_argument(
        "-f", "--filter", type=str, help="return a specific XML subtree"
    )
    parser.add_argument(
        "format", type=str, help="Configuration output format: xml, text, set, json"
    )
    parser.add_argument(
        "device", type=str, help="IP address or domain name of the Juniper router"
    )
    parser.add_argument("-u", "--user", type=str, help="User name")
    parser.add_argument("-p", "--password", type=str, help="Password")

    args = parser.parse_args()

    read_config(**vars(args))
else:
    pass
