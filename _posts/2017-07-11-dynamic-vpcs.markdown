---
layout: post
title:  "Tattle Trail"
date:   2017-06-16 10:33:20 -0500
categories: cloudtrail
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
But why bother?  Can't I just hard code things and make my life easier?  Of course you can, but let's take a quick
look at what that looks like.
</p>

{% highlight yaml %}
public_load_balancer:
  - Name: "APP-ENV-VPC-PublicLB-2A"
  - Name: "APP-ENV-VPC-WebTier-2B"
  - Name: "APP-ENV-VPC-WebTier-2C"
private_applications:
  - Name: "APP-ENV-VPC-ApplicationAndDataTier-2A"
  - Name: "APP-ENV-VPC-ApplicationAndDataTier-2B"
  - Name: "APP-ENV-VPC-ApplicationAndDataTier-2C"
public_nginx:
  - Name: "APP-ENV-VPC-CustomerFacing-2A"
  - Name: "APP-ENV-VPC-CustomerFacing-2B"
  - Name: "APP-ENV-VPC-CustomerFacing-2C"
</pre>
{% endhighlight %}

<h3>Where</h3>

<ul>
    <li>APP: Application name, could be any 3-letter combination that uniquely identifies the product.</li>
    <li>ENV: Environment name, dev, prd, stg, etc...</li>
    <li>VPC: simply defines this VPC as a VPC</li>
</ul>

<p>
This is a no bullshit real live layout from an "enterprise" client.  And yes, they put the word "VPC" in the name of
VPC in order to help identify it as a VPC.  In most cases we wouldn't bother doing that, or even having any information
in the name field which identifies the VPC, and we'll find out why this is later.
</p>

<p>
In this case we have 3 <b>topics</b>.  You might also see that the public_load_balancer names don't even match
correctly.  This was an actual setup in a real environment, but I'm leaving it here because it points out the importance
of what we're about to talk about.
</p>

<p>
Normalization is important here and allows us to start leaning on doing things with code instead of relying on
humans to type things in by hand.  Another example of this would be trying to manage a database of cars where each
row in the date base was named uniquely as such:
</p>

<b>MAKE-MODEL-CAR-COLOR-OWNER</b>

<p>
This may seem silly, but is there any point in defining that this is a car when we already know it's a car?  Normalization
states that we should break things up so that we have fields for each thing that identifies this car.  We do the same
thing using the AWS databases and tags.
</p>

<p>
Here is what this would look like if we were using the Name field to get a subnet:
</p>

{% highlight python %}
vpc_id = ## find_vpc_id()
filters = []
filters.push({ Name: "Main-Prod-VPC-CustomerFacing-2A" })
filters.push({ vpc_id: vpc_id })
subnets = vpc_client.find_vpc(filters: filters)
{% endhighlight %}

<p>
Obviously we would do this in a loop reading from the configuration data.  There's nothing inherintly wrong with this
approach, but let's take a look at what this might look like with meta data instead of just using the name.
</p>

{% highlight python %}
vpc_id = ## find_vpc_id()
filters = []
filters.push({ Role: 'public_load_balancer' })
filters.push({ vpc_id: vpc_id })
subnets = vpc_client.find_vpc(filters: filters)
{% endhighlight %}

<p>
This would allow us to completely do away with having a configuration data all together; it's no longer needed
as input from the user.  This is, of course, assuming that our subnets are tagged properly ( we'll get to that
later ).  I touched on this in a previous post, but the idea here is to make it as easy as possible for developers
of new stacks to be able to easily access the appropriate infrastructure.
</p>

<p>
Hard coding things like this is ultimatly bad value for the company.  For example, if we go to build out a new disaster
recovery ( DR ) region, then we'll have to go through and hard code new values for new subnets.  Ideally we'd want
to be able to run the same chunk of code ( whatever language that happens to be in ) and get the same results.  In the
case of us-west-[1,2] and us-east-1 we can't always guarantee that the zones will be in a specific order of a, then
b, then c.  In fact, we might want to use a different mix based on some other qualifier, but we absolutely want to
avoid forcing developers to have to deal with these differences.
</p>

