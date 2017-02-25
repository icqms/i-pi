"""
Contains classes for different geometry optimization algorithms.

TODO

Algorithms implemented by Michele Ceriotti and Benjamin Helfrecht, 2015
"""

# This file is part of i-PI.
# i-PI Copyright (C) 2014-2015 i-PI developers
# See the "licenses" directory for full license information.


import numpy as np
import time

from ipi.engine.motion import Motion
from ipi.utils.depend import depstrip, dobject
from ipi.utils.softexit import softexit
from ipi.utils.mintools import min_brent, BFGS,BFGSTRM ,L_BFGS
from ipi.utils.messages import verbosity, info
from ipi.utils.counter import counter


__all__ = ['GeopMotion']

class GeopMotion(Motion):
    """Geometry optimization class.

    Attributes:
        mode: minimization algorithm to use
        biggest_step: max allowed step size for BFGS/L-BFGS
        old_force: force on previous step
        old_direction: move direction on previous step 
        invhessian_bfgs: stored inverse Hessian matrix for BFGS
        hessian_trm: stored  Hessian matrix for trm
        ls_options:
        {tolerance: energy tolerance for exiting minimization algorithm
        iter: maximum number of allowed iterations for minimization algorithm for each MD step
        step: initial step size for steepest descent and conjugate gradient
        adaptive: T/F adaptive step size for steepest descent and conjugate
                gradient}
        tolerances:
        {energy: change in energy tolerance for ending minimization
        force: force/change in force tolerance foe ending minimization
        position: change in position tolerance for ending minimization}
        corrections_lbfgs: number of corrections to be stored for L-BFGS
        scale_lbfgs: Scale choice for the initial hessian.
        qlist_lbfgs: list of previous positions (x_n+1 - x_n) for L-BFGS. Number of entries = corrections_lbfgs
        glist_lbfgs: list of previous gradients (g_n+1 - g_n) for L-BFGS. Number of entries = corrections_lbfgs
    """

    def __init__(self, fixcom=False, fixatoms=None,
                 mode="lbfgs",
                 biggest_step=100.0,
                 old_pos=np.zeros(0, float),
                 old_pot= np.zeros(0, float),
                 old_force=np.zeros(0, float),
                 old_direction=np.zeros(0, float),
                 invhessian_bfgs=np.eye(0, 0, 0, float),
                 hessian_trm=np.eye(0, 0, 0, float),
                 tr_trm=np.zeros(0,float),
                 ls_options={"tolerance": 1e-6, "iter": 100, "step": 1e-3, "adaptive": 1.0},
                 tolerances={"energy": 1e-8, "force": 1e-8, "position": 1e-8},
                 corrections_lbfgs=5,
                 scale_lbfgs=1,
                 qlist_lbfgs=np.zeros(0, float),
                 glist_lbfgs=np.zeros(0, float)):
        """Initialises GeopMotion.

        Args:
           fixcom: An optional boolean which decides whether the centre of mass
              motion will be constrained or not. Defaults to False.
        """

        super(GeopMotion, self).__init__(fixcom=fixcom, fixatoms=fixatoms)
        
        # Optimization Options

        self.mode         = mode
        self.big_step     = biggest_step
        self.tolerances   = tolerances
        self.ls_options   = ls_options

        # 
        self.old_x        = old_pos
        self.old_u        = old_pot
        self.old_f        = old_force
        self.old_d        = old_direction

        # Classes for minimization routines and specific attributes
        if self.mode == "bfgs":
               self.invhessian   = invhessian_bfgs
               self.optimizer    = BFGSOptimizer()
        elif self.mode == "bfgstrm":
               self.tr           = tr_trm
               self.hessian      = hessian_trm
               self.optimizer    = BFGSTRMOptimizer()
        elif self.mode == "lbfgs":
               self.corrections  = corrections_lbfgs
               self.scale        = scale_lbfgs
               self.qlist        = qlist_lbfgs
               self.glist        = glist_lbfgs
               self.optimizer    = LBFGSOptimizer()
        elif self.mode == "sd":
               self.optimizer    = SDOptimizer()
        elif self.mode == "cg":
               self.optimizer    = CGOptimizer()
        else:
               self.optimizer    = DummyOptimizer()

    def bind(self, ens, beads, nm, cell, bforce, prng):
        """Binds beads, cell, bforce and prng to GeopMotion
        
            Args:
            beads: The beads object from whcih the bead positions are taken.
            nm: A normal modes object used to do the normal modes transformation.
            cell: The cell object from which the system box is taken.
            bforce: The forcefield object from which the force and virial are taken.
            prng: The random number generator object which controls random number generation.
        """

        super(GeopMotion,self).bind(ens, beads, nm, cell, bforce, prng)
        # Binds optimizer 
        self.optimizer.bind(self)
       
    def step(self, step=None):
        self.optimizer.step(step)
        
class LineMapper(object):
    
    """Creation of the one-dimensional function that will be minimized.
    Used in steepest descent and conjugate gradient minimizers.

    Attributes:
        x0: initial position
        d: move direction
    """
    
    def __init(self):
        self.x0 = self.d = None
        
    def bind(self, dumop):
        self.dbeads = dumop.beads.copy()
        self.dcell = dumop.cell.copy()
        self.dforces = dumop.forces.copy(self.dbeads, self.dcell)
    
    def set_dir(self, x0, mdir):
        self.x0 = x0.copy()
        self.d = mdir.copy() / np.sqrt(np.dot(mdir.flatten(), mdir.flatten()))
        if self.x0.shape != self.d.shape:
            raise ValueError("Incompatible shape of initial value and displacement direction")
            
    def __call__(self, x):
        """ computes energy and gradient for optimization step
            determines new position (x0+d*x)"""
        
        self.dbeads.q = self.x0 + self.d * x
        e = self.dforces.pot   # Energy
        g = - np.dot(depstrip(self.dforces.f).flatten(), self.d.flatten())   # Gradient
        counter.count()      # counts number of function evaluations
        return e, g
    
class GradientMapper(object):
       
    """Creation of the multi-dimensional function that will be minimized.
    Used in the BFGS and L-BFGS minimizers.

    Attributes:
        x0: initial position
        d: move direction
        xold: previous position
    """
    
    def __init__(self):
    #    self.x0 = None
    #    self.d = None
    #    self.xold = None
        pass
    
    def bind(self, dumop):
        self.dbeads = dumop.beads.copy()
        self.dcell = dumop.cell.copy()
        self.dforces = dumop.forces.copy(self.dbeads, self.dcell)
        
    def __call__(self,x):
        """computes energy and gradient for optimization step"""
        
        self.dbeads.q = x
        e = self.dforces.pot   # Energy
        g = -self.dforces.f   # Gradient
        counter.count()        # counts number of function evaluations
        return e, g

class DummyOptimizer(dobject):
    """ Dummy class for all optimization classes """
    
    def __init__(self):
        """initialises object for LineMapper (1-d function) and for GradientMapper (multi-dimensional function) """
        
        self.lm           = LineMapper()
        self.gm           = GradientMapper()
        
    def step(self, step=None):
        """Dummy simulation time step which does nothing."""
        pass
        
    def bind(self, geop):
        """ 
        bind optimization options and call bind function of LineMapper and GradientMapper (get beads, cell,forces)
        check whether force size, direction size and inverse Hessian size from previous step match system size
        """
        self.beads = geop.beads
        self.cell = geop.cell
        self.forces = geop.forces
        self.fixcom = geop.fixcom
        self.fixatoms = geop.fixatoms

        self.mode = geop.mode               
        self.tolerances = geop.tolerances


        #The resize action must be done before the bind
        if geop.old_x.size != self.beads.q.size:
            if geop.old_x.size == 0:
                geop.old_x =np.zeros((self.beads.nbeads,3*self.beads.natoms), float)  
            else:
                raise ValueError("Conjugate gradient force size does not match system size")
        if geop.old_u.size != 1:
            if geop.old_u.size == 0:
                geop.old_u = np.zeros(1, float)
            else:
                raise ValueError("Conjugate gradient force size does not match system size")
        if geop.old_f.size != self.beads.q.size:
            if geop.old_f.size == 0:
                geop.old_f = np.zeros((self.beads.nbeads,3*self.beads.natoms), float)  
            else:
                raise ValueError("Conjugate gradient force size does not match system size")
        if geop.old_d.size != self.beads.q.size:
            if geop.old_d.size == 0:
                geop.old_d = np.zeros((self.beads.nbeads,3*self.beads.natoms), float)  
            else:
                raise ValueError("Conjugate gradient direction size does not match system size")


        self.old_x      = geop.old_x
        self.old_u      = geop.old_u
        self.old_f      = geop.old_f
        self.old_d      = geop.old_d




    def exitstep(self, fx, u0, x):
        """ Exits the simulation step. Computes time, checks for convergence. """
       
        info(" @GEOP: Updating bead positions", verbosity.debug)
        
        self.qtime += time.time()

        if (np.absolute((fx - u0) / self.beads.natoms) <= self.tolerances["energy"])\
            and ( ( np.amax(np.absolute(self.forces.f)) <= self.tolerances["force"]   )  or
                  ( np.linalg.norm(self.forces.f.flatten() - self.old_f.flatten()) <= 1e-10)  )\
            and (x <= self.tolerances["position"]):
            info("Total number of function evaluations: %d" % counter.func_eval, verbosity.low) 
            softexit.trigger("Geometry optimization converged. Exiting simulation")
         
class BFGSOptimizer(DummyOptimizer):
    """ BFGS Minimization """

    def bind(self, geop):
        # call bind function from DummyOptimizer
        super(BFGSOptimizer,self).bind(geop)


        if geop.invhessian.size != (self.beads.q.size * self.beads.q.size):
            if geop.invhessian.size == 0:
                geop.invhessian = np.eye(self.beads.q.size, self.beads.q.size, 0, float)
            else:
                raise ValueError("Inverse Hessian size does not match system size")


        self.invhessian = geop.invhessian
        self.gm.bind(self)
        self.big_step = geop.big_step       
        self.ls_options = geop.ls_options   

    def step(self, step=None):
        """ Does one simulation time step.
            Attributes:
            qtime: The time taken in updating the positions.
        """

        self.qtime = -time.time()
        info("\nMD STEP %d" % step, verbosity.debug)

        if step == 0:
            info(" @GEOP: Initializing BFGS", verbosity.debug)
            self.old_d += depstrip(self.forces.f) / np.sqrt(np.dot(self.forces.f.flatten(), self.forces.f.flatten()))
   

        self.old_x[:] = self.beads.q
        self.old_u[:] = self.forces.pot
        self.old_f[:] = self.forces.f

        if len(self.fixatoms) > 0:
 
            for dqb in self.old_f:
                dqb[self.fixatoms*3] = 0.0
                dqb[self.fixatoms*3+1] = 0.0
                dqb[self.fixatoms*3+2] = 0.0

        fdf0 = (self.old_u,-self.old_f)
         
        # Do one iteration of BFGS, return movement (d_x), energy (fx), gradient (dfx).
        # MR: Note that energy and gradient are already stored in every step from self.gm.dforces.f and so on.
        # MR: All the outputs of mintools should be adjusted not to return at least fx and dfx 
        # MR: Note also that self.gm.dbeads.q also contains the updated geometries so even that could/should be done automatically
        # MR: If I'm not mistaken, even in mintools itself, 
        # The invhessian is updated inside.
        d_x,fx,dfx,new_d = BFGS(self.old_x,
                self.old_d, self.gm, fdf0, self.invhessian,
                self.big_step, self.ls_options["tolerance"],
                self.ls_options["iter"])

        self.old_d[:] = new_d

        #TODO update the forces with 'dfx' <- MR: no, self.gm.dforces hold all real info.
        #TODO update the potential energy with 'fx' <- MR: no, self.gm.dforces hold all real info.
          
        self.beads.q += d_x #Meanwhile we update here <- should be really self.gm.dbeads.q or something like that
        self.forces.transfer_forces(self.gm.dforces) #This forces the update of the forces before full update from geometries is triggered

        # Exit simulation step
        d_x_max =np.amax(np.absolute(d_x))
        self.exitstep(self.forces.pot, self.old_u, d_x_max)

class BFGSTRMOptimizer(DummyOptimizer):
    """ BFGSTRM Minimization with Trust Radius Method.	"""

    def bind(self, geop):

        super(BFGSTRMOptimizer,self).bind(geop)

        if geop.hessian.size != (self.beads.q.size * self.beads.q.size):
            if geop.hessian.size == 0:
                geop.hessian = np.eye(self.beads.q.size, self.beads.q.size, 0, float)
            else:
                raise ValueError("Hessian size does not match system size")

        self.hessian    = geop.hessian
        if geop.tr.size == 0:
            geop.tr = np.array([0.4])
        self.tr    = geop.tr
        self.gm.bind(self)
        self.big_step = geop.big_step       

    
    def step(self, step=None):
        """ Does one simulation time step.

            Attributes:
            qtime : The time taken in updating the real positions.
            tr    : current trust radius
        """

        self.qtime = -time.time()
        info("\nMD STEP %d" % step, verbosity.debug)

        if step == 0:
            info(" @GEOP: Initializing BFGSTRM", verbosity.debug)
        self.old_x[:] = self.beads.q
        self.old_u[:] = self.forces.pot
        self.old_f[:] = self.forces.f

        if len(self.fixatoms) > 0:
            for dqb in self.old_f:
                dqb[self.fixatoms*3] = 0.0
                dqb[self.fixatoms*3+1] = 0.0
                dqb[self.fixatoms*3+2] = 0.0

        #Make one step. ( A step is finished when a movement is accepted)
        d_x,fx,dfx = BFGSTRM(self.old_x,self.old_u,self.old_f,self.hessian,self.tr,
                      self.gm,self.big_step)
         
        #TODO update position without computing the forces
        #TODO update the forces with 'dfx'
        #TODO update the potential energy with 'fx'

        self.beads.q += d_x #Meanwhile we update here
 
        # Exit simulation step
        d_x_max =np.amax(np.absolute(d_x))
        self.exitstep(self.forces.pot, self.old_u, d_x_max)

#---------------------------------------------------------------------------------------
class LBFGSOptimizer(DummyOptimizer):
    """ L-BFGS Minimization """
    
    def bind(self, geop):
        # call bind function from DummyOptimizer
        super(LBFGSOptimizer,self).bind(geop)

        self.corrections = geop.corrections
        self.gm.bind(self)
        self.big_step = geop.big_step       
        self.ls_options = geop.ls_options   

        if geop.qlist.size != (self.corrections * self.beads.q.size):
            if geop.qlist.size == 0:
                geop.qlist = np.zeros((self.corrections, self.beads.q.size), float)
            else:
                raise ValueError("qlist size does not match system size")
        if geop.glist.size != (self.corrections * self.beads.q.size):
            if geop.glist.size == 0:
                geop.glist = np.zeros((self.corrections, self.beads.q.size), float)
            else:
                raise ValueError("qlist size does not match system size")


        self.qlist = geop.qlist
        self.glist = geop.glist

	if geop.scale not in [0,1,2]:
            raise ValueError("Scale option is not valid")

        self.scale = geop.scale


    def step(self, step=None):
        """ Does one simulation time step 
            Attributes:
            ttime: The time taken in applying the thermostat steps.
        """
        
        self.qtime = -time.time()

        info("\nMD STEP %d" % step, verbosity.debug)
        
        if step == 0:  
            info(" @GEOP: Initializing L-BFGS", verbosity.debug)
            self.old_d += depstrip(self.forces.f) / np.sqrt(np.dot(self.forces.f.flatten(), self.forces.f.flatten()))

        self.old_x[:] = self.beads.q
        self.old_u[:] = self.forces.pot
        self.old_f[:] = self.forces.f

        if len(self.fixatoms) > 0:

            for dqb in self.old_f:
                dqb[self.fixatoms*3] = 0.0
                dqb[self.fixatoms*3+1] = 0.0
                dqb[self.fixatoms*3+2] = 0.0

        fdf0 = (self.old_u,-self.old_f)

        d_x, fx, dfx,new_d, new_qlist, new_glist = L_BFGS(self.old_x,
                self.old_d, self.gm, self.qlist, self.glist,
                fdf0, self.big_step, self.ls_options["tolerance"],
                self.ls_options["iter"],
                self.corrections,self.scale, step)

        self.old_d[:] = new_d
        self.qlist[:] = new_qlist 
        self.glist[:] = new_glist 
 

        #TODO update position without computing the forces
        #TODO update the forces with 'dfx'
        #TODO update the potential energy with 'fx'
        self.beads.q += d_x #Meanwhile we update here 

        # Exit simulation step
	d_x_max =np.amax(np.absolute(d_x))
        self.exitstep(self.forces.pot, self.old_u, d_x_max)
      
class SDOptimizer(DummyOptimizer):
    """
    Steepest descent minimization
    dq1 = direction of steepest descent
    dq1_unit = unit vector of dq1
    """
    def bind(self, geop):
        # call bind function from DummyOptimizer
        super(SDOptimizer,self).bind(geop)
        self.lm.bind(self)
        self.ls_options = geop.ls_options   

    def step(self, step=None):
        """ Does one simulation time step 
            Attributes:
            ttime: The time taken in applying the thermostat steps.
        """
        
        self.qtime = -time.time()
        info("\nMD STEP %d" % step, verbosity.debug)

        dq1 = depstrip(self.forces.f)
 
	# Move direction for steepest descent
        dq1_unit = dq1 / np.sqrt(np.dot(dq1.flatten(), dq1.flatten()))
        info(" @GEOP: Determined SD direction", verbosity.debug)

        #Check for fixatoms        
        if len(self.fixatoms) > 0:
            for dqb in dq1_unit:
                dqb[self.fixatoms*3] = 0.0
                dqb[self.fixatoms*3+1] = 0.0
                dqb[self.fixatoms*3+2] = 0.0

        #Set position and direction inside the mapper 
        self.lm.set_dir(depstrip(self.beads.q), dq1_unit)
        
        # Reuse initial value since we have energy and forces already
        u0, du0 = (self.forces.pot.copy(), np.dot(depstrip(self.forces.f.flatten()), dq1_unit.flatten()))

        # Do one SD iteration; return positions and energy
        (x, fx,dfx) = min_brent(self.lm, fdf0=(u0, du0), x0=0.0,
                    tol=self.ls_options["tolerance"],
                    itmax=self.ls_options["iter"], init_step=self.ls_options["step"])

        # Automatically adapt the search step for the next iteration.
        # Relaxes better with very small step --> multiply by factor of 0.1 or 0.01
        self.ls_options["step"] = 0.1 * x * self.ls_options["adaptive"] + (1 - self.ls_options["adaptive"]) * self.ls_options["step"]

        #TODO update position without computing the forces
        #TODO update the forces with 'dfx'
        #TODO update the potential energy with 'fx'
           
        self.beads.q += dq1_unit * x   #Meanwhile we update here 
        
        # Exit simulation step
        self.exitstep(fx, u0, x)

class CGOptimizer(DummyOptimizer):
    """
    Conjugate gradient, Polak-Ribiere
    gradf1: force at current atom position
    gradf0: force at previous atom position
    dq1 = direction to move
    dq0 = previous direction
    dq1_unit = unit vector of dq1
    """
    def bind(self, geop):
        # call bind function from DummyOptimizer
        super(CGOptimizer,self).bind(geop)
        self.lm.bind(self)
        self.ls_options = geop.ls_options   

    def step(self, step=None):
        """Does one simulation time step 
           Attributes:
           ptime: The time taken in updating the velocities.
           qtime: The time taken in updating the positions.
           ttime: The time taken in applying the thermostat steps.
        """
        
        self.ptime = 0.0
        self.ttime = 0.0
        self.qtime = -time.time()

        info("\nMD STEP %d" % step, verbosity.debug)

        if step == 0:
            gradf1 = dq1 = depstrip(self.forces.f)

            # Move direction for 1st conjugate gradient step
            dq1_unit = dq1 / np.sqrt(np.dot(gradf1.flatten(), gradf1.flatten()))
            info(" @GEOP: Determined SD direction", verbosity.debug)
    
        else:
        
            gradf0 = self.old_f
            dq0 = self.old_d
            gradf1 = depstrip(self.forces.f)
            beta = np.dot((gradf1.flatten() - gradf0.flatten()), gradf1.flatten()) / (np.dot(gradf0.flatten(), gradf0.flatten()))
            dq1 = gradf1 + max(0.0, beta) * dq0
            dq1_unit = dq1 / np.sqrt(np.dot(dq1.flatten(), dq1.flatten()))
            info(" @GEOP: Determined CG direction", verbosity.debug)

        # Store force and direction for next CG step
        self.old_d[:] = dq1
        self.old_f[:] = gradf1

        if len(self.fixatoms) > 0:
            for dqb in dq1_unit:
                dqb[self.fixatoms*3] = 0.0
                dqb[self.fixatoms*3+1] = 0.0
                dqb[self.fixatoms*3+2] = 0.0

        self.lm.set_dir(depstrip(self.beads.q), dq1_unit)

        # Reuse initial value since we have energy and forces already
        u0, du0 = (self.forces.pot.copy(), np.dot(depstrip(self.forces.f.flatten()), dq1_unit.flatten()))

        # Do one CG iteration; return positions and energy
        (x, fx) = min_brent(self.lm, fdf0=(u0, du0), x0=0.0,
                    tol=self.ls_options["tolerance"],
                    itmax=self.ls_options["iter"], init_step=self.ls_options["step"])

        # Automatically adapt the search step for the next iteration.
        # Relaxes better with very small step --> multiply by factor of 0.1 or 0.01
        self.ls_options["step"] = 0.1 * x * self.ls_options["adaptive"] + (1 -     self.ls_options["adaptive"]) * self.ls_options["step"]

        self.beads.q += dq1_unit * x
        
        # Exit simulation step
        self.exitstep(fx, u0, x)
