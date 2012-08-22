

import numpy as np
import math
from utils.depend import *
from utils import units
from utils import nmtransform

__all__ = [ "NormalModes" ]

class NormalModes(dobject):
   """ A helper class to manipulate the path NM.

   Normal-modes transformation, determination of path frequencies,
   dynamical mass matrix change, etc.
   """

   def __init__(self, mode="rpmd", freqs=None):
      """ Sets the options for the normal mode transform. """

      if freqs is None:
         freqs = []
      dset(self,"mode",   depend_value(name='mode', value=mode))
      dset(self,"nm_freqs",
         depend_array(name="nm_freqs",value=np.asarray(freqs, float) ) )

      pass

   def bind(self, beads, ensemble):
      """ Initializes the normal modes object and binds to beads and ensemble.

      Do all the work down here as we need a full-formed necklace and ensemble
      to know how this should be done. """

      self.nbeads = beads.nbeads
      self.natoms = beads.natoms

      # stores a reference to the bound beads and ensemble objects
      self.beads = beads
      self.ensemble = ensemble

      # sets up what's necessary to perform nm transformation.
      #self.setup_transform(self.nbeads)
      self.transform = nmtransform.nm_trans(nbeads=self.nbeads)


      # creates arrays to store normal modes representation of the path.
      # must do a lot of piping to create "ex post" a synchronization between the beads and the nm
      sync_q = synchronizer()
      sync_p = synchronizer()
      dset(self,"qnm",
         depend_array(name="qnm",value=np.zeros((self.nbeads,3*self.natoms), float),
            func={"q": (lambda : self.transform.b2nm(depstrip(self.beads.q)) ) }, synchro=sync_q ) )
      dset(self,"pnm",
         depend_array(name="pnm",value=np.zeros((self.nbeads,3*self.natoms), float),
            func={"p": (lambda : self.transform.b2nm(depstrip(self.beads.p)) ) }, synchro=sync_p ) )

      # must overwrite the functions
      dget(self.beads, "q")._func = { "qnm": (lambda : self.transform.nm2b(depstrip(self.qnm)) )  }
      dget(self.beads, "p")._func = { "pnm": (lambda : self.transform.nm2b(depstrip(self.pnm)) )  }
      dget(self.beads, "q").add_synchro(sync_q)
      dget(self.beads, "p").add_synchro(sync_p)

      # also within the "atomic" interface to beads
      for b in range(self.nbeads):
         dget(self.beads._blist[b],"q")._func = { "qnm": (lambda : self.transform.nm2b(depstrip(self.qnm)) )  }
         dget(self.beads._blist[b],"p")._func = { "pnm": (lambda : self.transform.nm2b(depstrip(self.pnm)) )  }
         dget(self.beads._blist[b],"q").add_synchro(sync_q)
         dget(self.beads._blist[b],"p").add_synchro(sync_p)


      # finally, we mark the beads as those containing the set positions
      dget(self.beads, "q").update_man()
      dget(self.beads, "p").update_man()

      # create path-frequencies related properties
      dset(self,"omegan",
         depend_value(name='omegan', func=self.get_omegan,
            dependencies=[dget(self.ensemble,"temp")]) )
      dset(self,"omegan2", depend_value(name='omegan2',func=self.get_omegan2,
            dependencies=[dget(self,"omegan")]) )
      dset(self,"omegak", depend_array(name='omegak',
         value=np.zeros(self.beads.nbeads,float),
            func=self.get_omegak, dependencies=[dget(self,"omegan")]) )

      # sets up "dynamical" masses -- mass-scalings to give the correct RPMD/CMD dynamics
      dset(self,"nm_mass", depend_array(name="nmm",
         value=np.zeros(self.nbeads, float), func=self.get_nmm,
            dependencies=[dget(self,"nm_freqs"), dget(self,"mode") ]) )
      dset(self,"dynm3", depend_array(name="dm3",
         value=np.zeros((self.nbeads,3*self.natoms), float),func=self.get_dynm3,
            dependencies=[dget(self,"nm_freqs"), dget(self.beads, "m3")] ) )
      dset(self,"dynomegak", depend_array(name="dynomegak",
         value=np.zeros(self.nbeads, float), func=self.get_dynwk,
            dependencies=[dget(self,"nm_mass"), dget(self,"omegak") ]) )

      dset(self,"prop_pq",
         depend_array(name='prop_pq',value=np.zeros((self.beads.nbeads,2,2)),
            func=self.get_prop_pq,
               dependencies=[dget(self,"omegak"), dget(self,"nm_mass"), dget(self.ensemble,"dt")]) )

      # if the mass matrix is not the RPMD one, the MD kinetic energy can't be
      # obtained in the bead representation because the masses are all mixed up
      dset(self,"kins",
         depend_array(name="kins",value=np.zeros(self.nbeads, float),
            func=self.get_kins,
               dependencies=[dget(self,"pnm"), dget(self.beads,"sm3"), dget(self, "nm_mass") ] ))
      dset(self,"kin",
         depend_value(name="kin", func=self.get_kin,
            dependencies=[dget(self,"kins")] ))
      dset(self,"kstress",
         depend_array(name="kstress",value=np.zeros((3,3), float),
            func=self.get_kstress,
               dependencies=[dget(self,"pnm"), dget(self.beads,"sm3"), dget(self, "nm_mass") ] ))

#   def setup_transform(self, nbeads):
#      """ Sets up matrices for normal-mode transformation. """
#
#      # Todo: optional Fourier transform?
#
#      self.Cb2nm = np.zeros((nbeads,nbeads))
#      self.Cb2nm[0,:] = math.sqrt(1.0/nbeads)
#      for i in range(1,nbeads/2+1):
#         for j in range(nbeads):
#            self.Cb2nm[i,j] = math.sqrt(2.0/nbeads)*math.cos(2*math.pi*j*i/float(nbeads))
#      if (nbeads%2) == 0:
#         self.Cb2nm[nbeads/2,0:nbeads:2] = math.sqrt(1.0/nbeads)
#         self.Cb2nm[nbeads/2,1:nbeads:2] = -math.sqrt(1.0/nbeads)
#      for i in range(nbeads/2+1, nbeads):
#         for j in range(nbeads):
#            self.Cb2nm[i,j] = math.sqrt(2.0/nbeads)*math.sin(2*math.pi*j*i/float(nbeads))
#
#      self.Cnm2b = self.Cb2nm.T.copy()

   # A few functions which just transform back and forth from beads to NM representation
   #~ def nm2b_q(self):  return self.transform.reverse(depstrip(self.qnm))
   #~ def nm2b_p(self):  return self.transform.reverse(depstrip(self.pnm))
   #~ def b2nm_q(self):  return self.transform.forward(depstrip(self.beads.q))
   #~ def b2nm_p(self):  return self.transform.forward(depstrip(self.beads.p))
#~

   def get_omegan(self):
      """Returns the effective vibrational frequency for the interaction
      between replicas.
      """

      return self.ensemble.temp*self.nbeads*units.Constants.kb/units.Constants.hbar

   def get_omegan2(self):
      """Returns omegan**2."""

      return self.omegan**2

   def get_omegak(self):
      """Gets the normal mode frequencies.

      Returns:
         A list of the normal mode frequencies for the free ring polymer.
         The first element is the centroid frequency (0.0).
      """

      return 2*self.omegan*np.array([math.sin(k*math.pi/self.nbeads) for k in range(self.nbeads)])

   def get_dynwk(self):
      """Gets the normal mode frequencies.

      Returns:
         A list of the normal mode frequencies for the free ring polymer.
         The first element is the centroid frequency (0.0).
      """

      return self.omegak/np.sqrt(self.nm_mass)

   def get_prop_pq(self):
      """Gets the normal mode propagator matrix.

      Note the special treatment for the centroid normal mode, which is
      propagated using the standard velocity Verlet algorithm as required.
      Note that both the normal mode positions and momenta are propagated
      using this matrix.

      Returns:
         An array of the form (nbeads, 2, 2). Each 2*2 array prop_pq[i,:,:]
         gives the exact propagator for the i-th normal mode of the
         ring polymer.
      """

      dt=self.ensemble.dt
      pqk = np.zeros((self.nbeads,2,2), float)
      pqk[0] = np.array([[1,0], [dt,1]])

      for b in range(1, self.nbeads):
         sk = np.sqrt(self.nm_mass[b]) # NOTE THAT THE PROPAGATOR USES MASS-SCALED MOMENTA!

         dtomegak = self.omegak[b]*dt/sk
         c = math.cos(dtomegak)
         s = math.sin(dtomegak)
         pqk[b,0,0] = c
         pqk[b,1,1] = c
         pqk[b,0,1] = -s*self.omegak[b]*sk
         pqk[b,1,0] = s/(self.omegak[b]*sk)

      print "mass", self.nm_mass
      print pqk


      return pqk

   def get_nmm(self):
      """Returns dynamical mass factors, i.e. the scaling of normal mode
      masses that determine the path dynamics (but not statics)."""

      # also checks that the frequencies and the mode given in init are consistent with the beads and ensemble

      dmf = np.zeros(self.nbeads,float)
      dmf[:] = 1.0
      if self.mode == "rpmd":
         if len(self.nm_freqs) > 0:
            print "Warning: nm.frequencies will be ignored for RPMD mode."
      elif self.mode == "manual":
         if len(self.nm_freqs) != self.nbeads-1:
            raise ValueError("Manual path mode requires <frequencies> to contain (nbeads-1) frequencies, one for each internal mode of the path.")
         for b in range(1, self.nbeads):
            sk = self.omegak[b]/self.nm_freqs[b-1]
            dmf[b] = sk**2
      elif self.mode == "pa-cmd":
         if len(self.nm_freqs) > 1:
            print "Warning: only the first element in nm.frequencies will be considered for PA-CMD mode."
         if len(self.nm_freqs) == 0:
            raise ValueError("PA-CMD mode requires <frequencies> to contain the target frequency of all the internal modes.")
         for b in range(1, self.nbeads):
            sk = self.omegak[b]/self.nm_freqs[0]
            dmf[b] = sk**2
      elif self.mode == "wmax-cmd":
         if len(self.nm_freqs) > 2:
            print "Warning: only the first two element in nm.frequencies will be considered for WMAX-CMD mode."
         if len(self.nm_freqs) < 2:
            raise ValueError("WMAX-CMD mode requires <frequencies> to contain [wmax, wtarget]. All the internal modes for a SHO of frequency wmax will be matched with wtarget.")
         wmax = self.nm_freqs[0]
         wt = self.nm_freqs[1]
         for b in range(1, self.nbeads):
            sk = 1.0/np.sqrt((wt/wmax)**2*(1+(wmax/self.omegak[1])**2)/(1.0+(self.omegak[b]/wmax)**2))
            dmf[b] = sk**2

      return dmf

   def get_dynm3(self):
      """Takes the mass array and returns the square rooted mass array."""
      #TODO make this doc string correct.

      dm3 = np.zeros(self.beads.m3.shape,float)
      for b in range(self.nbeads):
         dm3[b] = self.beads.m3[b]*self.nm_mass[b]

      return dm3

   def free_qstep(self):
      """Exact normal mode propagator for the free ring polymer.

      Note that the propagator works in mass scaled coordinates, so that the
      propagator matrix can be determined independently from the particular
      atom masses, and so the same propagator will work for all the atoms in
      the system. All the ring polymers are propagated at the same time by a
      matrix multiplication.

      Also note that the centroid coordinate is propagated in qcstep, so is
      not altered here.
      """

      if self.nbeads == 1:
         pass
      else:
         pq = np.zeros((2,self.natoms*3),float)
         sm = depstrip(self.beads.sm3[0])
         for k in range(1,self.nbeads):
            pq[0,:] = depstrip(self.pnm[k])/sm
            pq[1,:] = depstrip(self.qnm[k])*sm
            pq = np.dot(self.prop_pq[k],pq)
            self.qnm[k] = pq[1,:]/sm
            self.pnm[k] = pq[0,:]*sm


   def get_kins(self):
      """Gets the MD kinetic energy for all the normal modes.

      Returns:
         A list of the kinetic energy for each NM.
      """

      kmd = np.zeros(self.nbeads,float)
      sm = depstrip(self.beads.sm3[0])
      pnm = depstrip(self.pnm)
      for b in range(self.nbeads):
         sp = pnm[b]/sm  # mass-scaled momentum of b-th NM
         kmd[b] = np.dot(sp,sp)*0.5/self.nm_mass[b]   # also takes care of the possibility of having non-RPMD masses

      return kmd

   def get_kin(self):
      """Gets the total MD kinetic energy.

      Note that this does not correspond to the total kinetic energy estimate
      for the system.

      Returns:
         The sum of the kinetic energy of each NM in the path.
      """

      return self.kins.sum()

   def get_kstress(self):
      """Calculates the total MD kinetic stress tensor.

      Note that this does not correspond to the quantum kinetic stress tensor
      estimate for the system.

      Returns:
         The sum of the MD kinetic stress tensor contributions from each NM.
      """

      #TODO MUST VERIFY THIS IS CORRECT
      kmd = np.zeros((3,3),float)
      sm = depstrip(self.beads.sm3[0])
      pnm = depstrip(self.pnm)
      for b in range(self.nbeads):
         sp = pnm[b]/sm  # mass-scaled momentum of b-th NM

         for i in range(3):
            for j in range(3):
               # computes the outer product of the p of various normal modes singling out Cartesian components to build the tensor
               # also takes care of the possibility of having non-RPMD masses
               kmd[i,j] += np.dot(sp[i:3*self.natoms:3],sp[j:3*self.natoms:3])*0.5/self.nm_mass[b]

      return kmd
