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

* [Finite-differences Suzuki-Chin PIMD](#finite-differences-suzuki-chin-pimd) (dev)
* [Reweighting-based high-order PIMD](#reweighting-based-high-order-pimd) (dev)
* [Multiple Time Step integrators](#multiple-time-step-integrators) (dev)
* [Ring-Polymer Contraction](#ring-polymer-contraction)
* [Direct Estimators for Isotope Fractionation](#direct-estimators-for-isotope-fractionation) (dev)
* [Free-energy Perturbation Estimators for Isotope Fractionation](#free-energy-perturbation-estimators-for-isotoope-fractionation) (dev)
* [Quantum Alchemical Transformation](#quantum-alchemical-transformation) (dev)
* [Path Integral GLEs](#path-integral-gles)
* [Generalized Langevin Equation Thermostats](#generalized-langevin-equation-thermostats)
* [Path-Integral Langevin Equation Thermostats](#path-integral-langevin-equation-thermostats)
* [Path Integrals at Constant Pressure](#path-integrals-at-constant-pressure)
* [Path Integral Molecular Dynamics](#path-integral-molecular-dynamics)


### Finite-differences Suzuki-Chin PIMD

### Reweighting-based high-order PIMD 

### Multiple Time Step integrators

A multiple time step integration scheme allows for integration of different components of forces with different time steps. It becomes advantageous when the total force can be decomposed into a slowly varying expensive part and a rapidly varying cheap part. A larger time step can be used to integrate the former, there by reducing the number of expensive computations.

**Main contributors:** Venkat Kapil   
**Implementation:**  
V.Kapil, J.VandeVondele, M.Ceriotti *"Accurate molecular dynamics and nuclear quantum effects at low cost by multiple steps in real and imaginary time: using density functional theory to accelerate wavefunction methods"*, J. Chem. Phys. 144, 054111 (2016)  
DOI: [10.1063/1.4941091](dx.doi.org/10.1063/1.4941091) --- BibTeX: [fetch](http://www.doi2bib.org/#/doi/10.1063/1.4941091)  
**Theory:**  
M.Tuckerman, B.J.Berne *"Reversible multiple time scale molecular dynamics"*, J. Chem. Phys. 97, 1990 (1992)  
DOI: [10.1063/1.463137](dx.doi.org/10.1063/1.463137) --- BibTeX: [fetch](http://www.doi2bib.org/#/doi/10.1063/1.463137)  

### Ring-Polymer Contraction

A ring-polymer contraction makes it possible to compute different components of the forces on different number of imaginary time slices. In order to reap maximum benefits, the implementation is fully compatible with the multiple time step integrators.

**Main contributors:** Michele Ceriotti, Venkat Kapil   
**Implementation:**  
V.Kapil, J.VandeVondele, M.Ceriotti *"Accurate molecular dynamics and nuclear quantum effects at low cost by multiple steps in real and imaginary time: using density functional theory to accelerate wavefunction methods"*, J. Chem. Phys. 144, 054111 (2016)
DOI: [10.1063/1.4941091](dx.doi.org/10.1063/1.4941091) --- BibTeX: [fetch](http://www.doi2bib.org/#/doi/10.1063/1.4941091)
**Theory:**   
T.Markland, D.E.Manolopoulos *"An efficient ring polymer contraction scheme for imaginary time path integral simulations"*, J. Chem. Phys. 129, 024105 (2008)  
DOI: [10.1063/1.2953308](dx.doi.org/10.1063/1.2953308) --- BibTeX: [fetch](http://www.doi2bib.org/#/doi/10.1063/1.2953308)  

### Direct Estimators for Isotope Fractionation

### Free-energy Perturbation Estimators for Isotope Fractionation

### Quantum Alchemical Transformation

### Path Integral GLEs


### Generalized Langevin Equation Thermostats
The Generalized Langevin Equation provides a very flexible framework
to manipulate the dynamics of a classical system, improving sampling
efficiency and obtaining quasi-equilibrium ensembles that mimic quantum
fluctuations. Parameters for the different modes of operation can be
obtained from the [GLE4MD website](http://gle4md.org/index.html?page=matrix).

**Main contributors:** Michele Ceriotti  
**Implementation:**  
M. Ceriotti, G. Bussi, M. Parrinello, *"M. Colored-Noise Thermostats à la Carte"*, J. Chem. Theory Comput. 6, 1170–1180 (2010)  
DOI: [10.1021/ct900563s](dx.doi.org/10.1021/ct900563s) --- BibTeX: [fetch](http://www.doi2bib.org/#/doi/10.1021/ct900563s)  
**Theory:**  
*Optimal Sampling Efficiency* ---
M. Ceriotti, G. Bussi, and M. Parrinello, *"Langevin Equation with Colored Noise for Constant-Temperature Molecular Dynamics Simulations"*, Phys. Rev. Lett. 102, 20601 (2009)  
DOI: [10.1103/PhysRevLett.102.020601](dx.doi.org/10.1103/PhysRevLett.102.020601) --- BibTeX: [fetch](http://www.doi2bib.org/#/doi/10.1103/PhysRevLett.102.020601)  
*Quantum Thermostat* --- 
M. Ceriotti, G. Bussi, and M. Parrinello, *"Nuclear Quantum Effects in Solids Using a Colored-Noise Thermostat"*, Phys. Rev. Lett. 103, 30603 (2009)  
DOI: [10.1103/PhysRevLett.103.030603](dx.doi.org/10.1103/PhysRevLett.103.030603) --- BibTeX: [fetch](http://www.doi2bib.org/#/doi/10.1103/PhysRevLett.103.030603)  
*Delta Thermostat* ---
M. Ceriotti and M. Parrinello, *"The δ-Thermostat: Selective Normal-Modes Excitation by Colored-Noise Langevin Dynamics"*, Procedia Comput. Sci. 1, 1607 (2010)  
DOI: [10.1016/j.procs.2010.04.180](dx.doi.org/10.1016/j.procs.2010.04.180) --- BibTeX: [fetch](http://www.doi2bib.org/#/doi/10.1016/j.procs.2010.04.180)  
*MTS Thermostat* ---
J. A. Morrone, T. E. Markland, M. Ceriotti, and B. J. Berne, *"Efficient Multiple Time Scale Molecular Dynamics: Using Colored Noise Thermostats to Stabilize Resonances"*, J. Chem. Phys. 134, 14103 (2011)  
DOI: [doi:10.1063/1.3518369](dx.doi.org/doi:10.1063/1.3518369) --- BibTeX: [fetch](http://www.doi2bib.org/#/doi/doi:10.1063/1.3518369)  

### Path-Integral Langevin Equation Thermostats

Simple yet efficient Langevin thermostat for PIMD, with normal-modes thermostats
optimally coupled to the ideal ring polymer frequencies 

**Main contributors:** Michele Ceriotti  
**Implementation and Theory:**  
M. Ceriotti, M. Parrinello, T. E. Markland, and D. E. Manolopoulos, *"Efficient stochastic thermostatting of path integral molecular dynamics"* J. Chem. Phys. 133, 124104 (2010).  
DOI: [10.1063/1.3489925](dx.doi.org/10.1063/1.3489925) --- BibTeX: [fetch](http://www.doi2bib.org/#/doi/10.1063/1.3489925)  


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

**Main contributors:** Michele Ceriotti, Joshua More  
**Implementation:**  
M. Ceriotti, J. More, D. Manolopoulos, *"i-PI: A Python interface for ab initio path integral molecular dynamics simulations"*, Comp. Phys. Comm. 185(3), 1019 (2014)
DOI: [10.1016/j.cpc.2013.10.027]( http://dx.doi.org/10.1016/j.cpc.2013.10.027)  ---  BibTeX: [fetch](http://www.doi2bib.org/#/doi/10.1016/j.cpc.2013.10.027)  
**Theory:** 
R. Feynman, A. Hibbs, *"Quantum Mechanics and Path Integrals"*, McGraw-Hill (1964)  
M. Tuckerman, *"Statistical Mechanics and Molecular Simulations"*, Oxford Univ. Press (2008)



