---
layout: page
title: "The Socket Interface"
subheadline: ""
teaser: "Run i-PI and the force calculator over different HPC centers!"
permalink: "/about/interface/"
header:
   image_fullwidth: "wpig6_blue.jpg"
---

Although the modular design of the code allows for direct, library-like
calls to force evaluators, the main mode of functioning of i-PI allows
to use a separate ab initio or empirical force evaluation code to
compute interatomic forces.
The implementation is based on a client-server paradigm, where i-PI
acts as the server and deals with the propagation of the nuclear
dynamics, whereas the calculation of the potential energy, forces and
the potential energy part of the pressure virial is delegated to one
or more instances of an external code, acting as clients. Since the
main focus is on performing ab initio PIMD - where the cost of the
force evaluation is overwhelming relative to the ionic dynamics -
clarity has been privileged over speed. Still, the implementation of
i-PI is efficient enough that it can be used with empirical
forcefields to perform simple benchmarks and preparatory
simulations. See more about i-PI implementation in the publication
that accompanies its release.

![socket-interface scheme](/images/ipi-interface-scheme.png)
