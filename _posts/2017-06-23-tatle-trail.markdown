---
layout: post
title:  "Tattle Trail"
date:   2017-06-16 10:33:20 -0500
categories: cloudtrail
---

<h1>Abstract</h1>

Providing business value by giving insight into who's doing what where and possibly why.

<h1>Overview</h1>

<p>
The goal here is to create a script that can scrape the CT data once a day to produce a report that can be used by operations
people to determine who's done what in the AWS network.
</p>

<p>
This goes beyhond the standard reporting mechanism provided by CT by reporting on specific actions.  Bubbling up things that
would be considered "dangerous" or "risky" by operations.
</p>

<p>
This report could then be lined up with the daily change review process to see if there are any actions that have happened
that are considered risky and not part of a CR.
</p>

<h1>Target Audience</h1>

<p>
Ops and SRE types.
</p>

<h1>Gatherting information</h1>

Describe what this would do and why we would care.
