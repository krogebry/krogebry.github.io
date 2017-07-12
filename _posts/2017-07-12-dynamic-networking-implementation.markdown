---
layout: post
title:  "Dynamic Networking Implementation"
date:   2017-06-16 10:33:20 -0500
categories: aws
---

<h1>Overview</h1>

<p>
Now let's dive into how we can make this useful for other people, like other operations engineers, SRE types or
even our development teams.  In this section I'm going to switch into the perspective of being an engineer that
is going to use this layout to build a CF template.  This template will create an ASG with an ALB and be ready
to deploy a simple golang API application.
</p>

<p>
Instead of using meta code or doing some kind of rough markup, I'm going to write actual python code that works.
This code will work as advertised for this small example, however, the code itself is meant to paint a somewhat
clear picture of how and why this thing works.  I wanted to stay away from abstracting things into classes or
even functions because I want to keep things simple for this example.
</p>

<p>
The software here should create a basic application using ECS, however, because I'm leaving out some of the other
networking parts like IGW's, it won't actually work.  I plan on writing a different post to cover these elements
and others.  These elements start working into more of the compositing and modular design that I plan on working
with later on.
</p>

<p>
For now, hopefully this can explain how to approach a complex problem with a simple solution.
</p>

<h1>Developer integration and implementation</h1>

<p>
First I want to build the same kind of script that I used with the VPC composition.  This script will be slightly
different in that it won't require building a VPC map, but we will be using the same kind of composition idea.
</p>

<p>
The <a href="">code</a> demonstrates how to use boto3 to get the VPCs and subnets from AWS using filters.
</p>

<p>
In this example I'm moving away from the idea of compositing everything because, at least for now, in this case, it
doesn't make sense.  What makes more sense is to have my application infrastructure requirements expressed in a single,
easy to read file.  At some point this might change.  If, for example I decide that I want a more complex layout
or I want to modularlize things a bit to make it easier for me to crank out more application clusters that might
do different things.
</p>

<p>
I'm also using a feature of the aws cli which generates a cli.
</p>

{% highlight bash %}
$ ./make_application_template.py
aws cloudformation create-stack --cli-input-json file:////tmp//stack_skel.json
krogebry@krogebry-secure[krogebry]:~/dev/krogebry.github.io/code/app_on_dynamic_net$ aws cloudformation create-stack --cli-input-json file:////tmp//stack_skel.json
{
    "StackId": "arn:aws:cloudformation:us-east-1:903369196314:stack/app-test-2/82911500-6745-11e7-b9ab-500c28688861"
}
{% endhighlight %}
