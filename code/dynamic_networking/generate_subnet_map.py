#!/usr/bin/env python
from netaddr import *
import yaml
import pprint
import pprint

config = yaml.load(open('config.yml'))

azs = [
    'us-east-1a',
    'us-east-1b',
    'us-east-1c',
    'us-east-1d',
    'us-east-1e',
    'us-east-1f'
]

sizes = {
    'large': 4,
    'medium': 2,
    'small': 1
}

def make_subnet_map( vpc ):
    ip = IPNetwork(vpc['cidr'])
    blocks = list(ip.subnet(24))
    print("NumBlocks: %s" % len(blocks))

    for subnet in vpc['subnets']:
        subnet["blocks"] = []

        for zone_name in azs:
            allocated_blocks = []

            for i in list(range(sizes[subnet['size']])):
                allocated_blocks.append(blocks.pop(0))

            subnet["blocks"].append({
                'zone': zone_name,
                'cidr_block': cidr_merge(allocated_blocks)
            })

        pprint.pprint(subnet)

for vpc in config['vpcs']:
    make_subnet_map(vpc)
