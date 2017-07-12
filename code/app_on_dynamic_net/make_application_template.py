#!/usr/bin/env python3
import boto3
import json
import yaml

config = yaml.load(open('app_config.yml'))

cli_skel = json.loads(open('cf_templates/cli.json').read())
cf_template = json.loads(open('cf_templates/application.json').read())

ec2_client = boto3.client('ec2')

vpc_filters = [{
    'Name': 'tag:role',
    'Values': [config['vpc']['name']]
}]
vpcs = ec2_client.describe_vpcs(Filters=vpc_filters)
vpc_id = vpcs['Vpcs'][0]['VpcId']

alb_subnet_filters = [{
    'Name': 'vpc-id',
    'Values': [vpc_id]
},{
    'Name': 'tag:role',
    'Values': ['public load balancers']
}]
alb_subnets = ec2_client.describe_subnets(Filters=alb_subnet_filters)
alb_zones = []
alb_subnet_ids = []
for subnet in alb_subnets['Subnets']:
    alb_subnet_ids.append(subnet['SubnetId'])
    alb_zones.append(subnet['AvailabilityZone'])

app_subnet_filters = [{
    'Name': 'vpc-id',
    'Values': [vpc_id]
},{
    'Name': 'tag:role',
    'Values': ['application']
}]
app_subnets = ec2_client.describe_subnets(Filters=app_subnet_filters)
app_zones = []
app_subnet_ids = []
for subnet in app_subnets['Subnets']:
    app_subnet_ids.append(subnet['SubnetId'])
    app_zones.append(subnet['AvailabilityZone'])

params = []
params.append({
    'ParameterKey': 'ALBZones',
    'ParameterValue': ','.join(alb_zones)
})
params.append({
    'ParameterKey': 'ALBSubnetIds',
    'ParameterValue': ','.join(alb_subnet_ids)
})

params.append({
    'ParameterKey': 'AppZones',
    'ParameterValue': ','.join(app_zones)
})
params.append({
    'ParameterKey': 'AppSubnetIds',
    'ParameterValue': ','.join(app_subnet_ids)
})

params.append({
    'ParameterKey': 'VpcId',
    'ParameterValue': vpc_id
})

params.append({
    'ParameterKey': 'KeyPairName',
    'ParameterValue': config['key_pair_name']
})

cli_skel['StackName'] = 'app-test-2'
cli_skel['TemplateBody'] = json.dumps(cf_template)
cli_skel['Parameters'] = params

f = open('/tmp/stack_skel.json', 'w')
f.write(json.dumps(cli_skel))
f.close()

f = open('/tmp/stack.json', 'w')
f.write(json.dumps(cf_template))
f.close()

cmd = 'aws cloudformation create-stack --cli-input-json file:////tmp//stack_skel.json'
print(cmd)