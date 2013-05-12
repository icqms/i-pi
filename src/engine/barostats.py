"""Contains the classes that deal with constant pressure dynamics.

Contains the algorithms which propagate the position and momenta steps in the
constant pressure and constant stress ensembles. Holds the properties directly
related to these ensembles, such as the internal and external pressure and
stress and the strain energy.

Classes:
   Barostat: Base barostat class with the generic methods and attributes.
   BaroRigid: Deals with rigid cell dynamics. Used for NPT ensembles.
"""

__all__ = ['Barostat', 'BaroBZP']

import numpy as np
from utils.depend import *
from utils.units import *
from utils.mathtools import eigensystem_ut3x3, invert_ut3x3, exp_ut3x3, det_ut3x3
from engine.thermostats import Thermostat
from inputs.thermostats import InputThermo

class Barostat(dobject):
   """Base barostat class.

   Gives the standard methods and attributes needed in all the barostat classes.

   Attributes:
      beads: A beads object giving the atoms positions
      cell: A cell object giving the system box.
      forces: A forces object giving the virial and the forces acting on
         each bead.

   Depend objects:
      dt: The time step used in the algorithms. Depends on the simulation dt.
      temp: The (classical) simulation temperature. Higher than the physical
         temperature by a factor of the number of beads.
      m: The mass associated with the cell degrees of freedom
      pext: The external pressure
   """

   def __init__(self, dt=None, temp=None, pext=None, tau=None, ebaro=None, thermostat=None):
      """Initialises base barostat class.

      Note that the external stress and the external pressure are synchronized.
      This makes most sense going from the stress to the pressure, but if you
      must go in the other direction the stress is assumed to be isotropic.

      Args:
         pext: Optional float giving the external pressure.
         m: Optional float giving the piston mass.
         dt: Optional float giving the time step for the algorithms. Defaults
            to the simulation dt.
         temp: Optional float giving the temperature for the thermostat.
            Defaults to the simulation temp.
      """

      dset(self,"dt",depend_value(name='dt'))
      if not dt is None:
         self.dt = dt
      else: self.dt = 1.0

      dset(self, "temp", depend_value(name="temp"))
      if not temp is None:
         self.temp = temp
      else: self.temp = 1.0

      dset(self,"tau",depend_value(name='tau'))
      if not tau is None:
         self.tau = tau
      else: self.tau = 1.0

      dset(self,"pext",depend_value(name='pext'))
      if not pext is None:
         self.pext = pext
      else: self.pext = 0.0

      dset(self,"ebaro",depend_value(name='ebaro'))
      if not ebaro is None:
         self.ebaro = ebaro
      else: self.ebaro = 0.0

      if thermostat is None:
         thermostat = Thermostat()
      self.thermostat = thermostat

      # pipes timestep and temperature to the thermostat
      deppipe(self,"dt", self.thermostat, "dt")
      deppipe(self, "temp", self.thermostat,"temp")


   def bind(self, beads, nm, cell, forces):
      """Binds beads, cell and forces to the barostat.

      This takes a beads object, a cell object and a forcefield object and
      makes them members of the barostat. It also then creates the objects that
      will hold the data needed in the barostat algorithms and the dependency
      network.

      Args:
         beads: The beads object from which the bead positions are taken.
         cell: The cell object from which the system box is taken.
         forces: The forcefield object from which the force and virial are
            taken.
      """

      self.beads = beads
      self.cell = cell
      self.forces = forces
      self.nm = nm

      dset(self,"pot",
         depend_value(name='pot', func=self.get_pot,
            dependencies=[ dget(cell,"V"), dget(self,"pext") ]))
      dset(self,"kstress",
         depend_value(name='kstress', func=self.get_kstress,
            dependencies=[ dget(beads,"q"), dget(beads,"qc"), dget(self,"temp") , dget(forces,"f") ]))
      dset(self,"stress",
         depend_value(name='stress', func=self.get_stress,
            dependencies=[ dget(self,"kstress"), dget(cell,"V"), dget(forces,"vir") ]))
      dset(self,"press",
         depend_value(name='press', func=self.get_press,
            dependencies=[ dget(self,"stress") ]))


   def get_pot(self):
      """Calculates the elastic strain energy of the cell."""

      return self.cell.V*self.pext

   def get_kstress(self):
      """Calculates the quantum centroid virial kinetic stress tensor
      estimator.
      """

      kst = np.zeros((3,3),float)
      q = depstrip(self.beads.q)
      qc = depstrip(self.beads.qc)

      na3 = 3*self.beads.natoms
      for b in range(self.beads.nbeads):
         for i in range(3):
            for j in range(i,3):
               kst[i,j] -= np.dot(q[b,i:na3:3] - qc[i:na3:3],
                  depstrip(self.forces.f[b])[j:na3:3])

      bkin = self.beads.kin*2.0/3
      print "KINCHK", bkin, Constants.kb*self.temp*(self.beads.natoms), np.trace(kst)
      for i in range(3):
         kst[i,i] += bkin #Constants.kb*self.temp*(self.beads.natoms) # here the temperature is the PI temperature -- so must divide by nbeads AFTER
      kst *= 1.0/self.beads.nbeads


      return kst

   def get_stress(self):
      """Calculates the internal stress tensor."""

      return (self.kstress + self.forces.vir/float(self.beads.nbeads))/self.cell.V

   def get_press(self):
      """Calculates the internal pressure."""

      return np.trace(self.stress)/3.0

   def pstep(self):
      """Dummy momenta propagator step."""

      pass

   def qcstep(self):
      """Dummy centroid position propagator step."""

      pass



class BaroBZP(Barostat):
   """Bussi-Zykova-Parrinello barostat class.

   Just extends the standard class adding finite-dt propagators for the barostat
   velocities, positions, piston.

   Attributes:
   thermostat: A thermostat object used to keep the cell momenta at a
         specified kinetic temperature.

   """

   def __init__(self, dt=None, temp=None, pext=None, tau=None, ebaro=None, thermostat=None, p=None):
      """Initializes BZP barostat.

      Just calls the general initializer, and creates an eta object to store the
      velocity of the piston.

      Args:
         thermostat: Optional thermostat object. Defaults to Thermostat().
      """


      super(BaroBZP, self).__init__(dt, temp, pext, tau, ebaro, thermostat)

      dset(self,"p", depend_array(name='p', value=np.atleast_1d(0.0)))

      if not p is None:
         self.p = np.asarray([p])
      else: self.p = 0.0


   def bind(self, beads, nm, cell, forces):

      super(BaroBZP, self).bind(beads, nm, cell, forces)

      # obtain the thermostat mass from the
      dset(self,"m", depend_array(name='m', value=np.atleast_1d(0.0),
                        func=(lambda:np.asarray([3*self.beads.natoms*Constants.kb*self.temp* self.tau**2])), dependencies =  [ dget(self,"tau"), dget(self,"temp") ] ))

      # binds the thermostat to the piston degrees of freedom
      self.thermostat.bind(pm=[ self.p, self.m ])

      dset(self,"kin",depend_value(name='kin', func=(lambda:0.5*self.p[0]**2/self.m[0]),
                            dependencies= [dget(self,"p"), dget(self,"m")]   ) )

      # the barostat energy must be computed from bits & pieces (overwrite the default)
      dset(self, "ebaro", depend_value(name='ebaro', func=self.get_ebaro,
                     dependencies = [ dget(self, "kin"), dget(self, "pot"), dget(self.cell, "V"),
                        dget(self, "temp"), dget(self.thermostat,"ethermo")]
                        ))

   def get_ebaro(self):

      print self.kin, self.pot,  - 2.0*Constants.kb*self.temp*np.log(self.cell.V) , self.thermostat.ethermo
      return self.kin + self.pot  - 2.0*Constants.kb*self.temp*np.log(self.cell.V) + self.thermostat.ethermo


   def pstep(self):
      """Dummy momenta propagator step."""

      dthalf = self.dt*0.5
      dthalf2 = dthalf**2
      dthalf3 = dthalf**3/3.0

      self.p += dthalf*3.0*(self.cell.V*(self.press - self.pext) + 2.0*Constants.kb*self.temp)

      fc = np.sum(depstrip(self.forces.f),0)/self.beads.nbeads
      m = depstrip(self.beads.m3[0])
      pc = depstrip(self.beads.pc)

      self.p += dthalf2*np.dot(pc,fc/m) + dthalf3*np.dot(fc,fc/m)

      self.beads.p += depstrip(self.forces.f)*dthalf


   def qcstep(self):
      """Dummy centroid position propagator step."""

      vel = self.p[0]/self.m[0]
      exp, neg_exp = (np.exp(vel*self.dt), np.exp(-vel*self.dt))
      sinh = 0.5*(exp - neg_exp)

      m = depstrip(self.beads.m3[0])

      self.nm.qnm[0,:] *= exp
      self.nm.qnm[0,:] += (sinh/vel)* (depstrip(self.nm.pnm[0,:])/depstrip(self.beads.m3[0]))
      self.nm.pnm[0,:] *= neg_exp

      self.cell.h *= exp
