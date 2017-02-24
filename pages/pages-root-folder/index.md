---
#
# Use the widgets beneath and the content will be
# inserted automagically in the webpage. To make
# this work, you have to use › layout: frontpage
#
layout: page
header:
  image_fullwidth: wpig6_blue.jpg

#callforaction:
#  url: https://tinyletter.com/feeling-responsive
#  text: Inform me about new updates and features ›
#  style: alert
#
permalink: /index.html
#
# This is a nasty hack to make the navigation highlight
# this page as active in the topbar navigation
#
homepage: true
---

About i-PI
==========
i-PI is a universal force engine interface
written in Python, designed to be used together with an ab-initio (or 
force-field based) evaluation of the interactions between the atoms. 
The main goal is to
decouple the problem of evolving the ionic positions to sample the
appropriate thermodynamic ensemble and the problem of computing the
inter-atomic forces.

-> ![iPi-logo]({{ site.urlimg }}ipi-logo-alpha.png) <-

The implementation is based on a client-server paradigm, where i-PI
acts as the server and deals with the propagation of the nuclear
motion, whereas the calculation of the potential energy, forces and
the potential energy part of the pressure virial is delegated to one
or more instances of an external code, acting as clients.

i-PI is free software, distributed under a dual MIT/GPLv3 licence. You
are welcome to dowload, use, modify and redistribute it. If you find it
useful for your research, a citation to
[Ceriotti, More, Manolopoulos, Comp. Phys. Comm. 185, 1019-1026 (2014)](http://dx.doi.org/10.1016/j.cpc.2013.10.027)
would be appreciated.

As of today, the following codes provide out-of-the-box an i-PI interface
[CP2K](https://www.cp2k.org/),
[DFTB+](http://www.dftb-plus.info/),
[Lammps](http://lammps.sandia.gov/),
[QuatumEspresso](http://quantum-espresso.org),
[Siesta](http://departments.icmab.es/leem/siesta/),
[FHI-aims](https://aimsclub.fhi-berlin.mpg.de/).
If you are interested in interfacing your code to i-PI please get in touch,
we are always glad to help!
