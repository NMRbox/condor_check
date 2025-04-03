#!/usr/bin/env python3
import argparse
import logging
import htcondor 
import socket 
import sys 
from condor_check import condor_check_logger

def check_ports(timeout=3):
    """
    timeout (int, optional): Connection timeout in seconds. Defaults to 3.
    """
    good = True
    port = htcondor.param.get('COLLECTOR_PORT')
    collector = htcondor.Collector()
    # Retrieve all startd ads (execution nodes)
    startd_ads = collector.locateAll(htcondor.DaemonTypes.Startd)

    # Use a set to avoid duplicate hostnames (in case a machine has multiple slots)
    unique_hostnames = set()

    for ad in startd_ads:
        # Prefer the "Machine" attribute, which should be just the hostname
        hostname = ad.get("Machine")
        if not hostname:
            # Fallback: use "Name" and split on '@'
            name_attr = ad.get("Name", "Unknown")
            if "@" in name_attr:
                hostname = name_attr.split("@")[1]
            else:
                hostname = name_attr
        unique_hostnames.add(hostname)

    # Attempt to connect to each unique hostname on the specified port
    for hostname in unique_hostnames:
        try:
            with socket.create_connection((hostname, port), timeout=timeout):
                condor_check_logger.info(f"{hostname} {port} good")
        except Exception as e:
            good =  False
            condor_check_logger.warning(f"{hostname} {port} bad {e}")
    return good



def main():
    logging.basicConfig()
    parser = argparse.ArgumentParser(formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument('-l', '--loglevel', default='WARN', help="Python logging level")
    parser.add_argument('--timeout',type=int,default=3, help="Connection timeout")

    args = parser.parse_args()
    condor_check_logger.setLevel(getattr(logging,args.loglevel))
    if not check_ports(args.timeout):
        sys.exit(1)


if __name__ == "__main__":
    main()

