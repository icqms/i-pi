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


# i-PI v2 beta is out for testing!
**The second release of i-PI is currently being prepared for release.
A number of new features and improved infrastructure components will
be merged over the next few weeks, and become available in the master
branch of the [developers repo](https://github.com/cosmo-epfl/i-pi-dev)
as well as in the [official i-PI repo](https://github.com/i-pi/i-pi).
This is the time to report bugs and help us make this release efficient 
and stable!**



i-PI is a universal force engine interface
written in Python, designed to be used together with an ab-initio (or 
force-field based) evaluation of the interactions between the atoms. 
The main goal is to
decouple the problem of evolving the ionic positions to sample the
appropriate thermodynamic ensemble and the problem of computing the
inter-atomic forces.

<p align="center">
  <img src="{{ site.urlimg }}ipi-logo-alpha.png" alt="iPi-logo" />
</p>

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

As of today, the following codes provide out-of-the-box an i-PI interface: 
[CP2K](https://www.cp2k.org/),
[DFTB+](http://www.dftb-plus.info/),
[Lammps](http://lammps.sandia.gov/),
[Quantum ESPRESSO](http://quantum-espresso.org),
[Siesta](http://departments.icmab.es/leem/siesta/),
[FHI-aims](https://aimsclub.fhi-berlin.mpg.de/),
[Yaff](http://molmod.github.io/yaff/).
If you are interested in interfacing your code to i-PI please get in touch,
we are always glad to help!

If you have questions about running i-PI calculations, or including new features
into the code, you can get help on the [user forum](https://groups.google.com/forum/#!forum/ipi-users), 
or on the [github developers branch](https://github.com/cosmo-epfl/i-pi-dev).
