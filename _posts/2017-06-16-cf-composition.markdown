---
layout: post
title:  "CloudFormation discovery and composition methodology"
date:   2017-06-16 10:33:20 -0500
categories: cloudformation 
---

<h1>Getting the most out of your CloudFormation stacks</h1>

At a high-level view people use one of two approaches when building CF stacks:

<ul>
	<li>All logic in the stack.</li>
	<li>Discovery and composition</li>
</ul>

Let's take a look at both approaches.

<h2>All logic in the stack.</h2>

In this approach people generally try to cram everything into the stack, using if conditionals and the newly added "Comment" bits to give their stacks structure and definition.

There's nothing wrong with this approach, however, it does make things quite confusing at times.  This is especially evident when people try to cram many similar things into a template.
Discovery and composition

A different approach is to move the logic out of the CF stack into the programming space.  Since the CF template is nothing but JSON data we can use structures to create the CF stack data.  This allows us to utilize several benefits that any given programming language give us:

<ul>
	<li>Patterns and templates for repeatability and reuse.</li>
	<li>Verification and validation steps.</li>
	<li>Ability to look up resources that might exist outside of the stack, or even AWS itself.</li>
	<li>Access control, logging and accountability.</li>
</ul>

These tools give us the ability to compose our stacks by combining similar parts, processing those parts, and creating something new.

Let's take a look at a very simple example using the ImageId attribute.  In most cases we'd see something like this:

{% highlight json %}
{ "Parameters": { "ImageId": { "Type": "String" } } }
{ "Resources": {
  "ASG": {
    "ImageId": { "Ref": "ImageId" }
  }
}
{% endhighlight %}

This is the first step down the road of "programming" with JSON/CF stacks.  Here we're defining a param into a global space, then using a function ( "Ref" ) to reference that variable.  This is all fine and good, but let's look at another, slightly more complicated example:

"ImageId" : { "Fn::FindInMap" : ["RegionMap", { "Ref" : "AWS::Region" }, "AMI"] }

In this example we're using a slightly more complex way of deriving the AMI.  In this example we're expecting that the ImageId map will always be consistent, never change, and be bundled with the stack.

Again, nothing wrong with this approach, however, let's really dive into this and take a look at where this starts becoming a big problem.  In this example we're going to create two ASG's:

{ "Resources": {
  "ASGLeft": {
    "Min": 1, "Max": 1,
    [ config stuff for left ... ]  
  },
  "ASGRight": {
    "Min": 1, "Max": 1,
    [ config stuff for right ... ]
  }
}}

This is a perfect use case for not using CF for things.  Having two chunks of code in the stack like this increases the probability of errors in that each "ASG" has to be maintained.  For example, if a bug fix is implemented in the ASGLeft chunk, but isn't put into the ASGRight chunk, then you have a serious problem.  Debugging this problem is hard ( we know this from experience ).

Now let's take a look at a different approach to this using a pattern.  The first thing we do is create a template for the ASG:

templates/asg.json:
{ "Resources": { [ config stuff for everyone... ] }}

Now we use some code to composite the CF stack, I like ruby, but you can use whatever language you want as most languages these days have easy support for JSON.

stack = JSON.parse(File.read( "templates/main.json" ))
asg_tpl = JSON.parse(File.read( "templates/asg.json" ))

["Left", "Right"].each do |asg_name|
  tpl = asg_tpl.clone

  tpl["SpecialSetting"] = if(ast_name == "Left")
    true
  else
    false
  end

  stack["Resources"]["ASG%s" % asg_name] = tpl
end

The idea here is that we're using an iterator and a template to create a pattern based approach to solving this problem.

Just before we launch the stack we would have something like this:

fs_tmp_file = "/tmp/blah/%i.json" % Time.new.to_i
f = File.open( fs_tmp_file, "w" )
f.puts( stack.to_json )
f.close
aws cloudformation launch-stack --template-body file://#{fs_tmp_file}

The idea here is that we're going to use this idea of compositing to create a CF stack, then write the JSON data to disk and send that file off to the CF API.  Of course, we could do the same thing using API calls, which is just as fine.

Let's take a look at a more practical example using VPC's.  In most cases people are fond of this kind of pattern:

"Parameters": { "VpcId": { "Type": "String" }}, "Resources": { "ASG": { "VpcId": { "Ref": "VpcId" } } }

Most people will have the VpcId stored in a JSON file that lives in their project.  The idea being that the VPC will never change and most people have only one or two VPC's, which is easy to track.  However, let's assume we live in a world where we have much more complexity.  In fact, let's do a little math problem here:

Let's say we have 5 services, each service has 3 AWS accounts ( preprod, prod, and disaster recovery ).  Let's also say that we use all 3 US regions.

5 services * 3 accounts = 15 service accounts * 3 regions = 45 service account regions.

Right off the bat, that's 45 VPC's we'd be tracking.  That doesn't include what happens when a single new service is spun up, which will add 3 accounts * 3 regions = 9 service account regions and therefor 9 more VPC's to track.  Also, when something changes, which it might, how can we guarantee that the changes that happen in the AWS space are reflected in our git repo?  The answer is, of course: we can't.

Let's make this even more complicated by suggesting that we have a rather complicated subnet layout in which each topic has it's own subnet:
ELB's
Bastion hosts ( jump boxes )
Things that the ELB's hit ( routers like nginx and such )
Service things that do business logic ( tomcat, service layer )
Backend services ( AMQ, DB, etc... )
Security scanning and compliance subnet
That's 6 topics and we end up having at least 2 of each of these per zone, so if we span across 3 zones we have:

6 topics * 3 zones = 18 subnet topic zones per service account region = 810 subnet ids that are going to be tracked.

Wow, that's quite a few subnets!

That doesn't include things like SNS topics, IAM things, or any other thing that might be a part of an operating environment.

But here's where we the magic of a code-based approach comes in.  Instead of trying to maintain hordes of json files for all of these 810 subnets, we use the aws cli to find our resources, for example:

vpc = aws ec2 describe-vpcs --filters 'Name=tag:Role,Values=ApprovedVPCTag' 'Name=tag:Lifecycle,Values=current' 
elb_subnets = aws ec2 describe-vpc-subnets --filters 'Name=tag:Role,Values=elb' 'Name=vpc-id,Values=#{vpc[VpcId]}'

We "discover" our resources, then send the Id's into the CF stack using params.  This is where we get the "discovery" part of the "discovery and composition" methodology.

In this model we can be assured that if something in the environment changes, we won't have to care.  Our stuff will "just work" which means resiliency and reliability are enhanced.

It also means that we have to do less "hunt and peck" operations to find out what "should" be in the json files and what is in the environment.
