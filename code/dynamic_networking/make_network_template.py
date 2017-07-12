#!/usr/bin/env python
from netaddr import *
import copy
import json
import yaml
import pprint
import pprint

config = yaml.load(open('network_config.yml'))

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
    # print('NumBlocks: %s' % len(blocks))

    for subnet in vpc['subnets']:
        subnet['blocks'] = []

        for zone_name in azs:
            allocated_blocks = []

            for i in list(range(sizes[subnet['size']])):
                allocated_blocks.append(blocks.pop(0))

            subnet['blocks'].append({
                'zone': zone_name,
                'cidr_block': cidr_merge(allocated_blocks)
            })

    return vpc

cf_template = json.loads(open('cf_templates/base_plate.json').read())

vpc_tpl = json.loads(open('cf_templates/vpc.json').read())
subnet_tpl = json.loads(open('cf_templates/subnet.json').read())

global_element_id = 0

for vpc in config['vpcs']:
    vpc = make_subnet_map(vpc)

    new_vpc_tpl = copy.deepcopy(vpc_tpl)
    new_vpc_tpl['Resources']['VPC']['Properties']['CidrBlock'] = vpc['cidr']

    new_vpc_tpl['Resources']['VPC']['Properties']['Tags'].append({
        'Key': 'role',
        'Value': vpc['name']
    })

    cf_template['Resources']['vpc%s' % vpc['name']] = new_vpc_tpl['Resources']['VPC']

    for subnet in vpc['subnets']:
        for subnet_block in subnet['blocks']:
            new_subnet_tpl = copy.deepcopy(subnet_tpl)
            p = new_subnet_tpl['Resources']['Subnet']['Properties']
            p['CidrBlock'] = str(subnet_block['cidr_block'][0])
            p['Tags'].append({
                'Key': 'role',
                'Value': subnet['name']
            })
            p['AvailabilityZone'] = subnet_block['zone']
            p['VpcId'] = {'Ref': 'vpc%s' % vpc['name']}

            cf_template['Resources']['subblock%s' % global_element_id] = new_subnet_tpl['Resources']['Subnet']
            global_element_id += 1

f = open('/tmp/stack.json', 'w')
f.write(json.dumps(cf_template))
f.close()

print("Template saved to /tmp/stack.json")

