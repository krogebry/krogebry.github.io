---
layout: post
title:  "Dynamic Subnets in a Vpc"
date:   2017-06-16 10:33:20 -0500
categories: aws
---

<h1>Abstract</h1>


<h1>Overview</h1>

<p>
The goal here is to show how we can write code to build our VPC and subnets dynamically.
</p>

<p>
In complex, enterprise networks our VPCs and Subnets can get complicated quickly due to the requirements of
 security and compliance.
</p>

<h1>Introduction</h1>

<p>
In your basic AWS account you might have a single VPC and maybe a single subnet per zone.  That's pretty easy
to manage.  However, as I've demonstrated in this past, things can get very complicated very quickly.  This post
aims at solving that complication by showing how we can solve the complexity problem with some code.
</p>

<p>
The biggest challenge is how to allocate the CIDR blocks for respective subnets.
</p>

<a href="https://github.com/krogebry/krogebry.github.io/blob/master/code/dynamic_networking/generate_subnet_map.py">Code</a>

<p>
It's probably okay to assume that the number of avaliable data centers is going to stay a static value.  However,
in the name of being consistent let's ask AWS for the list instead of guessing.
</p>

{% highlight json %}
krogebry@krogebry-secure[krogebry]:~$ aws ec2 describe-availability-zones
{
    "AvailabilityZones": [
        {
            "ZoneName": "us-east-1a",
            "State": "available",
            "RegionName": "us-east-1",
            "Messages": []
        },
        {
            "ZoneName": "us-east-1b",
            "State": "available",
            "RegionName": "us-east-1",
            "Messages": []
        },
        {
            "ZoneName": "us-east-1c",
            "State": "available",
            "RegionName": "us-east-1",
            "Messages": []
        },
        {
            "ZoneName": "us-east-1d",
            "State": "available",
            "RegionName": "us-east-1",
            "Messages": []
        },
        {
            "ZoneName": "us-east-1e",
            "State": "available",
            "RegionName": "us-east-1",
            "Messages": []
        },
        {
            "ZoneName": "us-east-1f",
            "State": "available",
            "RegionName": "us-east-1",
            "Messages": []
        }
    ]
}
{% endhighlight %}

<p>
If we add a little jq to this we can get a more concise list:
</p>

{% highlight bash %}
krogebry@krogebry-secure[krogebry]:~$ aws ec2 describe-availability-zones| jq '.AvailabilityZones[].ZoneName'
"us-east-1a"
"us-east-1b"
"us-east-1c"
"us-east-1d"
"us-east-1e"
"us-east-1f"
{% endhighlight %}

<p>
We can see how this is different for us-west-2...
</p>

{% highlight bash %}
krogebry@krogebry-secure[krogebry]:~$ aws --region us-west-2 ec2 describe-availability-zones| jq '.AvailabilityZones[].ZoneName'
"us-west-2a"
"us-west-2b"
"us-west-2c"
{% endhighlight %}

<p>
The thing to point out here is that different regions have different zones.  Duh, right?  But this shows how we can
use a little bit of query magic to get the list that we should be using.  We'll use this list to build out our subnets
later on.
</p>

<p>
I've created a quick and dirty little python script that demonstrates how we can use a little code to solve a big
problem.  Specifically this will create a CIDR block mapping which describes our layout in the config.yml file.
Here is the output:
</p>

{% highlight bash %}
krogebry@krogebry-secure[krogebry]:~/dev/krogebry.github.io/code/dynamic_subnets$ ./generate.py
NumBlocks: 256
{'blocks': [{'cidr_block': [IPNetwork('172.16.0.0/22')],
             'zone': 'us-east-1a'},
            {'cidr_block': [IPNetwork('172.16.4.0/22')],
             'zone': 'us-east-1b'},
            {'cidr_block': [IPNetwork('172.16.8.0/22')],
             'zone': 'us-east-1c'},
            {'cidr_block': [IPNetwork('172.16.12.0/22')],
             'zone': 'us-east-1d'},
            {'cidr_block': [IPNetwork('172.16.16.0/22')],
             'zone': 'us-east-1e'},
            {'cidr_block': [IPNetwork('172.16.20.0/22')],
             'zone': 'us-east-1f'}],
 'name': 'public load balancers',
 'size': 'large'}
{'blocks': [{'cidr_block': [IPNetwork('172.16.24.0/23')],
             'zone': 'us-east-1a'},
            {'cidr_block': [IPNetwork('172.16.26.0/23')],
             'zone': 'us-east-1b'},
            {'cidr_block': [IPNetwork('172.16.28.0/23')],
             'zone': 'us-east-1c'},
            {'cidr_block': [IPNetwork('172.16.30.0/23')],
             'zone': 'us-east-1d'},
            {'cidr_block': [IPNetwork('172.16.32.0/23')],
             'zone': 'us-east-1e'},
            {'cidr_block': [IPNetwork('172.16.34.0/23')],
             'zone': 'us-east-1f'}],
 'name': 'public facing nginx',
 'size': 'medium'}
NumBlocks: 256
{'blocks': [{'cidr_block': [IPNetwork('172.17.0.0/22')],
             'zone': 'us-east-1a'},
            {'cidr_block': [IPNetwork('172.17.4.0/22')],
             'zone': 'us-east-1b'},
            {'cidr_block': [IPNetwork('172.17.8.0/22')],
             'zone': 'us-east-1c'},
            {'cidr_block': [IPNetwork('172.17.12.0/22')],
             'zone': 'us-east-1d'},
            {'cidr_block': [IPNetwork('172.17.16.0/22')],
             'zone': 'us-east-1e'},
            {'cidr_block': [IPNetwork('172.17.20.0/22')],
             'zone': 'us-east-1f'}],
 'name': 'operations',
 'size': 'large'}
{'blocks': [{'cidr_block': [IPNetwork('172.17.24.0/22')],
             'zone': 'us-east-1a'},
            {'cidr_block': [IPNetwork('172.17.28.0/22')],
             'zone': 'us-east-1b'},
            {'cidr_block': [IPNetwork('172.17.32.0/22')],
             'zone': 'us-east-1c'},
            {'cidr_block': [IPNetwork('172.17.36.0/22')],
             'zone': 'us-east-1d'},
            {'cidr_block': [IPNetwork('172.17.40.0/22')],
             'zone': 'us-east-1e'},
            {'cidr_block': [IPNetwork('172.17.44.0/22')],
             'zone': 'us-east-1f'}],
 'name': 'security',
 'size': 'large'}
{'blocks': [{'cidr_block': [IPNetwork('172.17.48.0/24')],
             'zone': 'us-east-1a'},
            {'cidr_block': [IPNetwork('172.17.49.0/24')],
             'zone': 'us-east-1b'},
            {'cidr_block': [IPNetwork('172.17.50.0/24')],
             'zone': 'us-east-1c'},
            {'cidr_block': [IPNetwork('172.17.51.0/24')],
             'zone': 'us-east-1d'},
            {'cidr_block': [IPNetwork('172.17.52.0/24')],
             'zone': 'us-east-1e'},
            {'cidr_block': [IPNetwork('172.17.53.0/24')],
             'zone': 'us-east-1f'}],
 'name': 'bastion',
 'size': 'small'}
{% endhighlight %}

<p>
As you can see the bastion subnets are getting a smaller /24 subnet ( 172.17.48.0/24 for example ), but we're also
allocating a /22 for large subnets and a /23 for medium sized subnets.
</p>

<p>
The sizes dict is doing the work to determine how this works.
</p>

{% highlight python %}
sizes = {
    'large': 4,
    'medium': 2,
    'small': 1
}
{% endhighlight %}

<p>
We have the option of tuning this map to give us different options on subnet sizes and allocations.  What I'm leaving
out here is all of the bounds checking.  For example, what if you run out of blocks for a given subnet?  I'm leaving
up to the individual ( you ) to figure out with your implementation.  The idea here is to show how we can use a little
code to solve a big problem.
</p>

<p>
The problem here is that we don't want to do any manual work to define our network topology.  Instead we want to
make the machine do the work for us.  In most situations there really is no need to manually assign cidr blocks
to subnets, in fact that can create a huge amount of unneccessary overhead when building our cloud things.
</p>

<p>
The important thing here is to focus on the business of being in whatever business you're currently in.  Not on building
complex networking layouts.  In a datacenter you would have to hire at least one networking person to do all of this
work.  Here we're giving that work to a small script.  Win!
</p>

<h1>Integration into CloudFormation</h1>

<p>
For the moment I'm going to skip talking about how to integrate into something like terraform because, frankly, I
don't think it's capable of handling a situation like this.  TF would need to allow users to write custom code.  Or
maybe you could write .tf param files to make this work.  For the purpose of this document I'm going to stick with
what I know, which is CF.
</p>

<p>
In my previous post I talked about how to composite ( or glue ) various CF bits together and why that was important
to know.  Now I'm going to expand on that idea by integrating the code from above into a CF stack which creates the
VPC and Subnet elements.
</p>

<p>
Run the script to compile the template.
</p>



{% highlight bash %}
$ ./make_network_template.py
Template saved to /tmp/stack.json
{% endhighlight %}



<p>
Validate the template using the aws cli.
</p>

{% highlight bash %}
$ aws cloudformation validate-template --template-body file:////tmp//stack.json

{
    "Description": "",
    "Parameters": []
}
{% endhighlight %}



<p>
If everything looks correct we can create the stack.
</p>

{% highlight bash %}
$ aws cloudformation create-stack --stack-name vpc-test-0 --template-body file:////tmp//stack.json

{
    "StackId": "arn:aws:cloudformation:us-east-1:903369196314:stack/vpc-test-0/8d7cc500-66a9-11e7-95a5-500c5cc81217"
}
{% endhighlight %}



<p>
There is an existing VPC by default, so with our two new VPCs we now have 3 total:
</p>

{% highlight bash %}
$ aws ec2 describe-vpcs|jq '.Vpcs[].VpcId'
"vpc-a0be2dd9"
"vpc-00bc2f79"
"vpc-21d67f46"
{% endhighlight %}

<p>
Now let's query to find our subnets for the <b>public load balancers</b> role.
</p>

{% highlight bash %}
$ aws ec2 describe-subnets --filters "Name=vpc-id,Values=vpc-f7f3638e" "Name=tag:role,Values=public load balancers"
{% endhighlight %}

<a href="">Example output</a>

<p>
At this point we have a fully functioning set of networking gear that allows us to enable our developers quick
and easy access to the resources without them having to know much about the complexity of this world.  In the next
post I will cover how we can implement this layout with a script to build a template.
</p>

<h2>Global Id</h2>

<p>
I used a <b>global_element_id</b> counter to keep track of my subnets.  This is because each element in the resources
list needs a unique name.  I use the counter to help make that happen.  In some cases your template might have to
reference a subnet by name using "Ref", however, in this case we can get away with not worrying about this because
the template is intentionally locked down to only dealing with the VPC and subnet creation.
</p>

<p>
Anything that happens outside of this template will reference the subnets by the tags or other metadata and won't
care about the name I give it in the stack.  If you're trying to reference a given subnet from within a template,
then you might want consider changing this such that the name reflects the AZ and role somehow.  However, if you did
go down that road you would most likely end up having to enforce rules for how your roles are named.  For example,
you would have to prevent spaces in your role names, or remove spaces from the names in the script.  If you remove
the spaces then, obviously, you'll have to deal with inconsistencies that arise from having one name in the config
and a different name in the template.
</p>

