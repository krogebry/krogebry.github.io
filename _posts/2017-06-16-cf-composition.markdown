---
layout: post
title:  "CloudFormation discovery and composition methodology"
date:   2017-06-16 10:33:20 -0500
categories: cloudformation 
---

<h1>Abstract</h1>

<p>
Complex enterprise network layouts with multiple product offerings which each contain clusters of microservices
require complex solutions that can sustain changes though time and fluctuating security requirements.
</p>

<h1>Overview</h1>

<p>
I doubt I'm saying anything new if I stated that the cloud is a complicated landscape.
The post covers on specific aspect of dealing with a complicated ecosystem using multiple products hosted in AWS.
Specifically how to manage clusters of microservices using CloudFormation and any programming language you want.
The language itself is irrelevant for this discussion; use whatever you want.  The important thing is to take a look
at why we would bother investing time in doing certain things.
</p>

<p>
I use the word <i>investment</i> with intention because it really is an investment.  It's in investment in not having
to do things over and over again with unpredictable results.  It's an investment in aligning the goals of the
infrastructure teams with some of the goals that guide and govern the software development world.  Ultimately
they're the same thing, however, because we're talking about infrastruction the goal usually changes to "just get
it done."  That's fine, but just like with the software development world this attitude will incur technical debt
that can sometimes compound faster than "vanilla" software.
</p>

<h1>Audience</h1>

<p>
The intended audience here isn't the hardcore devops hacker that already knows the power of Infrastructure
as Code ( IaC ).  This is targeted at those that might still be on the fence as to <b>why</b> we go to such
efforts and invest so much into this approach.
</p>

<h1>The AWS Networking Ecosystem</h1>

<p>
In the past few years AWS has done an amazing job building out their consumer facing networking infrastructure.
These new tools allow us to build complicated network designs that often match what we see in the data center.
</p>

<p>
In parallel AWS has also built out an automation tool which allows us to capture our infrastructure expectations
in the form of either JSON or YAML documents which are stored in a service called CloudFormation.  CF soars above
competitors like Teraform and Ansible because it's part of the AWS ecosystem.  It's a tool inside a set of other
tools which gives it the competitive advantage.  It also gives us a wealth of programmtic access to objects
that are not offered in other systems.  More on that in other posts.
</p>

<p>
These two technologies together allow us to build things that give us security and resiliency on our compute
infrastructure.
</p>

<h1>CloudFormaiton Template Design</h1>

<p>
Diving right into the CFT world.
At a high-level view people use one of two approaches when building CF stacks:
</p>

<ul>
	<li>All logic in the stack.</li>
	<li>Discovery and composition</li>
</ul>

Let's take a look at both approaches.



<h2>All logic in the stack.</h2>

<p>
In this approach people generally try to cram everything into the stack, using if conditionals and
the newly added "Comment" bits to give their stacks structure and definition.
There's nothing wrong with this approach, however, it does make things quite confusing at times.
This is especially evident when people try to cram many similar things into a template.
This is basically like trying to have <b>every</b> single piece of business logic <b>in</b> the stack
rather than trying to pull out some of the logic into your programming language.
</p>

<p>
This approach usually starts with the best of intentions, but I've often observed developers who start down
this path switch gears during the lifecycle of a project and switch to breaking things up a little.
Eventually they start to realize that managing python/ruby/go code is easier than trying to manipulate
the stack itself with a complicated series of CFT language-specific constructs.
</p>

<h3>For example</h3>

<p>
An example of this would be like trying to use CFT mappings to determine the CIDR of a subnet.
This ends up being a giant nightmare of complicated JSON structures that end up being a huge pain to maintain.
</p>

<p>
If anyone is curious, I can crack out some code examples of how this works with large-scale VPC structures.
It's super ugly.
</p>

<h2>Discovery and composition</h2>

<p>
A different approach is to move the logic out of the CF stack into the programming space.
Since the CF template is nothing but JSON data we can use structures to create the CF stack data.
This allows us to utilize several benefits that any given programming language give us:
</p>

<ul>
	<li>Patterns and templates for repeatability and reuse.</li>
	<li>Verification and validation steps.</li>
	<li>Ability to look up resources that might exist outside of the stack, or even AWS itself.</li>
	<li>Access control, logging and accountability.</li>
</ul>

<p>
These tools give us the ability to compose our stacks by combining similar parts, processing those parts,
and creating something new.
Let's take a look at a very simple example using the ImageId attribute.  In most cases we'd see something like this:
</p>

{% highlight json %}
{
    "Parameters": {
        "ImageId": {
            "Type": "String"
        }
    },

    "Resources": {
        "ASG": {
            "ImageId": { "Ref": "ImageId" }
        }
    }
}
{% endhighlight %}

<p>
This is the first step down the road of "programming" with JSON/CF stacks.
Here we're defining a param into a global space, then using a function ( "Ref" ) to reference that variable.
This is all fine and good, but let's look at another, slightly more complicated example:
</p>

{% highlight json %}
{
    "Mappings": {
        "RegionMap" : {
            "us-east-1"      : { "32" : "ami-6411e20d"},
            "us-west-1"      : { "32" : "ami-c9c7978c"},
            "eu-west-1"      : { "32" : "ami-37c2f643"},
            "ap-southeast-1" : { "32" : "ami-66f28c34"},
            "ap-northeast-1" : { "32" : "ami-9c03a89d"}
        }
    },
    "Resources": {
        "EC2": {
            "Properties": {
                "ImageId" : { "Fn::FindInMap" : ["RegionMap", { "Ref" : "AWS::Region" }, "AMI"] }
            }
        }
    }
}
{% endhighlight %}

<p>
In this example we're using a slightly more complex way of deriving the AMI.
In this example we're expecting that the ImageId map will always be consistent,never change, and be bundled with the stack.
</p>

<p>
Again, nothing wrong with this approach, however, let's really dive into this and take a
look at where this starts becoming a big problem.  In this example we're going to create two ASG's:
</p>

{% highlight json %}
{
    "Resources": {
        "ASGLeft": {
            "Properties": {
                "Min": 1,
                "Max": 1
            }
        },
        "ASGRight": {
            "Properties": {
                "Min": 1,
                "Max": 1
            }
        }
    }
}
{% endhighlight %}

<p>
This is a perfect use case for not using CF for things.
Having two chunks of code in the stack like this increases the probability of errors in that
each <b>ASG</b> has to be maintained.
For example, if a bug fix is implemented in the ASGLeft chunk, but isn't put into the
ASGRight chunk, then you have a serious problem.  Debugging this problem is hard ( we know this from experience ).
And yes, this has actually happened.
</p>

<p>
Now let's take a look at a different approach to this using a pattern.
The first thing we do is create a template for the ASG:
</p>

<h4>templates/main.json:</h4>

{% highlight json %}
{
    "Resources": {},
    "Mappings": {},
    "Parameters": {}
}
{% endhighlight %}

<h4>templates/asg.json:</h4>

{% highlight json %}
{
    "ASGNameTemplate": {
        "Properties": {
            "Key": "Value",
            "Min": 1,
            "Max": 1
        }
    }
}
{% endhighlight %}

<p>
Now we use some code to composite the CF stack, I like ruby, but you can use whatever language
you want as most languages these days have easy support for JSON.
</p>

{% highlight ruby %}
stack = JSON.parse(File.read( "templates/main.json" ))
asg_tpl = JSON.parse(File.read( "templates/asg.json" ))

["Left", "Right"].each do |asg_name|
  tpl = asg_tpl.clone

  tpl["SpecialSetting"] = if(ast_name == "Left")
    true
  else
    false
  end

  stack["Resources"]["ASG%s" % asg_name] = tpl["ASGNameTemplate"]
end
{% endhighlight %}

<p>
The idea here is that we're using an iterator and a template to create a pattern based approach to solving this problem.
Just before we launch the stack we would have something like this:
</p>

{% highlight ruby %}
## Open a template file.
fs_tmp_file = "/tmp/blah/%i.json" % Time.new.to_i
f = File.open( fs_tmp_file, "w" )

## Dump the json to the file.
f.puts( stack.to_json )
f.close

## Launch the stack using the aws cli.
aws cloudformation launch-stack --template-body file://#{fs_tmp_file}
{% endhighlight %}

<p>
There's an interesting side effect to doing things like this in that the JSON that is dumped
to the temp file is compiled.  Which just means that all the line breaks are taken out.  This
makes the overall payload smaller which means you can pack more stupid bullshit into your
stack.
</p>

<p>
The idea here is that we're going to use this idea of composition to create a CF stack,
then write the JSON data to disk and send that file off to the CF API.
Of course, we could do the same thing using API calls, which is just as fine.
This is a choice I make but it can go one of two ways.
</p>

<ul>
    <li>If I'm working with mostly SRE/Ops people I'll generally prefer to use the AWS CLI.</li>
    <li>If I'm working with mostly Developers, I'll generally prefer to use aws-sdk/boto3 for interactions with AWS</li>
</ul>

<p>
Generally speaking, it's easier for ops people to debug problems by looking at the CLI input/output ; we understand
system interactions in this manner.  However, developers are probably most accustomed to seeing failures as stack
traces and working with debugging API's in a different way.
</p>

<p>
We can extend this idea to include many types of commonly used objects.  In fact there are libraries built
to extend this idea by creating generic objects which act like CloudFormation types.  These are
great for going all in on the IaC concepts, but so far still leave a bit of a gap in functionality.
Worth looking into if any of these ideas are sparking your creative genious ( or your evil genious,
whatever, we don't judge ).
</p>

<p>
Let's take a look at a more practical example using VPC's.  In most cases people are fond of this kind of pattern:
</p>

{% highlight json %}
{
    "Parameters": {
        "VpcId": {
            "Type": "String"
        }
    },
    "Resources": {
        "ASG": {
            "VpcId": { "Ref": "VpcId" }
        }
    }
}
{% endhighlight %}

<p>
Most people will have the VpcId stored in a YAML file that lives in the project.  Or, some people will
use something like a params file where they keep the VPC/Subnet values stored.
The idea being that the VPC will never change and most people have only one or two VPC's, which is easy to track.
However, let's assume we live in a world where we have much more complexity.
In fact, let's do a little math problem here:
</p>

<p>
Let's say we have 5 products, each product has 3 AWS accounts.  Each product can have any number of services
running.  Let's say we're using ECS and docker because we're awesome and that's fun.
</p>

<ul>
    <li>preprod</li>
    <li>prod</li>
    <li>disaster recovery</li>
</ul>

<p>
For each account we're active in 2 regions, but generally we're only going to use 1.
In some cases like mongodb we'll need to use at least two regions for failover, but that only appiles
to production and maybe DR, but not pre-prod.
We also assume that, by default, the security team is going to do us a solid by installing our VPC's for us
by creating a CF stack which has everything we'll need for the VPC's, bastions and subnets.
</p>

<p>
5 products * 3 accounts = 15 service accounts
</p>

<p>
15 service accounts * 2 regions = 30 service account regions.
</p>

<p>
Right off the bat, that's 30 VPC's we'd be tracking.
That doesn't include what happens when a single new service is spun up,
which will add 3 accounts * 2 regions = 6 service account regions and therefor 6 more VPC's to track.
</p>

<p>
We assume that change is going to happen, even at the networking level.  There may be a case where
we have to move everything over to a new version of the VPC stacks.  If we did everything by hand
we'd have to trak 30 different VPC's in, potentially, 30 different YAML files.
Good engineers ( DevOps/SRE/whatever ) will find a way to program this problem.
Bad engineers will often just do it by hand because it's a one off and in their mind
programming is more difficult and time consuming and therefor not worth the effort
( read: <b>investment</b> ).
</p>

<p>
Let's make this even more complicated by stating that we have a rather complicated
subnet layout in which each topic has it's own subnet:
</p>

<ul>
    <li>Public web for things like [E,A]LB's</li>
    <li>Bastion hosts ( jump boxes )</li>
    <li>Things that the ELB's hit ( routers like nginx and such )</li>
    <li>Service things that do business logic ( java apps, nodejs, etc... )</li>
    <li>Backend services ( AMQ, DB, etc... )</li>
    <li>Security scanning and compliance subnet</li>
</ul>

<p>
We could have anywhere between 1 and 5 zones, but on average, typically 3 are used
</p>

<p>
6 topics * 3 zones = 18 subnets per service account region.
30 service account regions ( or VPC's ) * 18 subnets = 540 total subnets.
</p>

<p>
That means that in total, accross all accounts someone will have to manage a total of 540
things that might move.  Looking at the numbers it's hard to imagine anyone trying to justify
not making the <b>investment</b> to code their way out of this problem.
</p>

<p>
Here's where the magic of a code-based approach comes in.
Instead of trying to maintain hordes of YAML files for all of these 540 subnets,
we use the aws cli to find our resources.  We <b>invest</b> in a more sustainable
solution by implementing deterministic resource discovery.
</p>

<h4>Deterministic resource discovery</h4>

<p>
This is a huge win because now we can use vague names for things.  For example let's compare and contrast
the two approaches available here.
</p>

<p>
First, let's take a look at the more traditional way of handling the VPC and Subnet Id's.
In this example we're going to use a YAML file to act as our high level configuration.
This is a fairly common practice which allows us to use a YAML file to specify a few high level
ideas that our stack creation software that expands to more specific things.
</p>

{% highlight yaml %}
---
region: us-east-1
vpc: vpc-12345678
public_subnet_az1: subnet-12345678
public_subnet_az2: subnet-12345678
public_subnet_az3: subnet-87654321
private_subnet_az1: subnet-12345678
private_subnet_az2: subnet-12345678
private_subnet_az3: subnet-87654321
...and so on...
{% endhighlight %}

<p>
To be clear, this may seem horribly wrong, but this is something people actively commit to in the
enterprise world.  Which is part of why I've created this post.  It's important to call this out
as a bad patthern.
</p>

<p>
Let's look at how this would look if we were to apply the rules of data normalization and deterministic
resource discovery.
</p>

{% highlight yaml %}
---
region: us-east-1
vpc:
    Name: main
    Version: 0.1.0
public_subnets:
    Role: public
private_subnets:
    Role: private
{% endhighlight %}

<p>
The code would perform a look up based on the key/value pair ( kvp ) provided for the resources.
For example it might look something like this in ruby.
</p>

{% highlight ruby %}
require 'aws-sdk'

creds = Aws::SharedCredentials.new()
ec2_client = Aws::EC2::Client.new(region: ENV['AWS_DEFAULT_REGION'], credentials: creds)

yaml = ## load yaml from file

filters = []

for k,v in yaml['vpc'] do
    filters.push(
        name: format('tag:%s' % k),
        values: [v]
    )
end

res = ec2_client.describe_vpcs(filters: filters)

vpc = ## get vpc

public_subnets = []

public_subnet_filters = [{
    name: 'vpc-id',
    values: [vpc.vpc_id]
},{
    name: 'tag:Role',
    values: [yaml['public_subnets']['Role']]
}]
public_subnets = ec2_client.desciribe_subnets( public_subnet_filters )
{% endhighlight %}

<p>
This is intended as meta code just to convey the idea.  Obviously we'd want to extend this out into functions
and other contructs.

The idea here is that we're trying to get the programming to do the work for us here and make it as easy
and painles on the end user as possible.

In this example we might return 3 subnets, or 5 depending on how the security team has things setup.  In
either case we don't have to care.  If we were changing from 3 to 5 subnets, or maybe the subnets
have changed, then we'd be on the hook to update the YAML files accordingly.
</p>

<p>
Something else to note here is that I'm also using a version string for the VPC.  With this kind of methodoogy
we can now version or infrastrcture and allow for any kind of blue green deployment at the networking level.
Try doing that in a datacenter. ;)
</p>

<h4>Client configs</h4>

<p>
In many cases our end users are the consumers of our platform tools and not the end
users of the products we're deploying.  I've been on 3 projects so far where
we ended up putting a giant shotgun-sized hole in our foot by forcing the develoopers and operational
support teams to manage complex YAML configurations which define the environment they'll be working in.
</p>

<p>
Taking the complexity away from developers and support staff is a huge win.  Esspecially in complex
enterprise organizations which often utilize contract help to build out the infrastrcture.
</p>

<p>
Regardless of what you call the approach the result is the same: solve your problems with code.
</p>