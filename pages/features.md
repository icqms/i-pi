---
layout: page
show_meta: false
title: "Features"
teaser: ""
header:
   image_fullwidth: "wpig6_blue.jpg"

permalink: "/about/features/"
---

i-PI includes a large number of sophisticated methods, that
have been contributed over the years by many people. Here you
will find a comprehensive list, that we try to keep updated. 
Please get in touch if we are missing something or someone, and 
please format your contribution section following this 
[template]({{ site.url }}/assets/pdf/example_feature.md). 

Developers receive too little recognition for their implementation
efforts. For this reason, we list together with every feature
not only the paper(s) that first introduced the methods, but also
those that were connected with the implementation of the method in i-PI.
Finding these features readily available is saving you weeks of work:
reward the developers by spending 15 seconds to add one more citation
to your manuscript!


### Multiple Time Step integrators


### Ring-Polymer Contraction


### Generalized Langevin Equation Thermostats
The Generalized Langevin Equation provides a very flexible framework
to manipulate the dynamics of a classical system, improving sampling
efficiency and obtaining quasi-equilibrium ensembles that mimic quantum
fluctuations. Parameters for the different modes of operation can be
obtained from the [GLE4MD website](gle4md.org/index.html?page=matrix).


### Path-Integral Langevin Equation Thermostats


### Path Integrals at Constant Pressure

The constant-pressure implementation allows for arbitrary 
thermostats to be applied to the cell degrees of freedom, and 
work in both constant-shape and variable-cell mode. 

**Main contributors:**  Michele Ceriotti, Joshua More  
**Implementation:**   
M. Ceriotti, J. More, D. Manolopoulos, *"i-PI: A Python interface for ab initio path integral molecular dynamics simulations"*, Comp. Phys. Comm. 185(3), 1019 (2014)  
DOI: [10.1016/j.cpc.2013.10.027]( http://dx.doi.org/10.1016/j.cpc.2013.10.027)  ---  BibTeX: [fetch](http://www.doi2bib.org/#/doi/10.1016/j.cpc.2013.10.027)  
**Theory:**  
G. J. Martyna, A. Hughes, M. Tuckerman, *"Molecular dynamics algorithms for path integrals at constant pressure"*, J. Chem. Phys. 110(7), 3275 (1999)  
DOI: [10.1063/1.478193](http://dx.doi.org/10.1063/1.478193) --- BibTeX: [fetch](http://www.doi2bib.org/#/doi/10.1063/1.478193)  
G. Bussi, T. Zykova-Timan, M. Parrinello, *"Isothermal-isobaric molecular dynamics using stochastic velocity rescaling"*, J. Chem. Phys. 130(7), 074101 (2009)  
DOI: [10.1063/1.3073889](http://dx.doi.org/10.1063/1.3073889)  --- BibTeX: [fetch](http://www.doi2bib.org/#/doi/10.1063/1.3073889)  
P. Raiteri, J. D. Gale, G. Bussi, *"Reactive force field simulation of proton diffusion in BaZrO<sub>3</sub> using an empirical valence bond approach"*, J. Phys. Cond. Matt. 23(33), 334213 (2011)  
DOI: [10.1088/0953-8984/23/33/334213](http://dx.doi.org/10.1088/0953-8984/23/33/334213)  --- BibTeX: [fetch](http://www.doi2bib.org/#/doi/10.1088/0953-8984/23/33/334213)  


### Path Integral Molecular Dynamics

The basic PIMD implementation in i-PI relies on a normal-modes
integrator, and allows setting non-physical masses, so that both
RPMD and CMD can be easily realized.

*Main contributors:* Michele Ceriotti, Joshua More  
*Implementation:*  
M. Ceriotti, J. More, D. Manolopoulos, *"i-PI: A Python interface for ab initio path integral molecular dynamics simulations"*, Comp. Phys. Comm. 185(3), 1019 (2014)
DOI: [10.1016/j.cpc.2013.10.027]( http://dx.doi.org/10.1016/j.cpc.2013.10.027)  ---  BibTeX: [fetch](http://www.doi2bib.org/#/doi/10.1016/j.cpc.2013.10.027)
*Theory:* 
R. Feynman, A. Hibbs, *"Quantum Mechanics and Path Integrals"*, McGraw-Hill (1964)  
M. Tuckerman, *"Statistical Mechanics and Molecular Simulations"*, Oxford Univ. Press (2008)



