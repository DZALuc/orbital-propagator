"""
Orbital Propagator Module

Two-body orbital mechanics simulator with perturbations support.
Designed for satellite trajectory analysis and mission planning.

Author: Damián Zúñiga Avelar
Date: April 2026
"""

import numpy as np
from scipy.integrate import solve_ivp
from astropy import units as u
from astropy import constants as const


class OrbitalPropagator:
    """
    Numerical propagator for satellite orbits.
    
    Implements two-body problem with support for perturbations
    (J2, atmospheric drag in future versions).
    
    Attributes
    ----------
    mu : float
        Gravitational parameter (m^3/s^2)
    """
    
    def __init__(self, mu=const.GM_earth.value):
        """
        Initialize orbital propagator.
        
        Parameters
        ----------
        mu : float, optional
            Gravitational parameter in m^3/s^2
            Default is Earth's GM (3.986004418e14)
        """
        self.mu = mu
    
    def equations_of_motion(self, t, state):
        """
        Two-body equations of motion.
        
        Implements the fundamental equation:
        d²r/dt² = -μ/r³ * r
        
        Parameters
        ----------
        t : float
            Time (seconds) - not used but required by solve_ivp
        state : array_like, shape (6,)
            State vector [x, y, z, vx, vy, vz] in meters and m/s
        
        Returns
        -------
        derivatives : ndarray, shape (6,)
            State derivatives [vx, vy, vz, ax, ay, az]
        
        Notes
        -----
        This is the classical two-body problem. The acceleration is
        purely gravitational and depends only on position.
        """
        # Extract position and velocity
        r_vec = state[0:3]  # Position vector [x, y, z]
        v_vec = state[3:6]  # Velocity vector [vx, vy, vz]
        
        # Calculate distance from central body
        r = np.linalg.norm(r_vec)
        
        # Calculate gravitational acceleration
        # a = -μ/r³ * r_vec
        a_vec = -(self.mu / r**3) * r_vec
        
        # Return derivatives: [velocity, acceleration]
        derivatives = np.concatenate([v_vec, a_vec])
        
        return derivatives
    
    def propagate(self, r0, v0, t_span, dt=60.0, method='DOP853', 
                  rtol=1e-10, atol=1e-12):
        """
        Propagate orbit from initial conditions.
        
        Uses high-accuracy numerical integration to solve the
        equations of motion.
        
        Parameters
        ----------
        r0 : array_like, shape (3,)
            Initial position vector [x, y, z] in meters
        v0 : array_like, shape (3,)
            Initial velocity vector [vx, vy, vz] in m/s
        t_span : tuple of float
            Integration time span (t_start, t_end) in seconds
        dt : float, optional
            Time step for output in seconds (default: 60)
        method : str, optional
            Integration method for solve_ivp
            Options: 'RK45', 'RK23', 'DOP853' (default), 'Radau', 'BDF'
            DOP853 is high-accuracy for smooth problems
        rtol : float, optional
            Relative tolerance for integration (default: 1e-10)
        atol : float, optional
            Absolute tolerance for integration (default: 1e-12)
        
        Returns
        -------
        solution : dict
            Dictionary containing:
            - 't': time array (seconds)
            - 'r': position array, shape (n_points, 3) (meters)
            - 'v': velocity array, shape (n_points, 3) (m/s)
            - 'success': bool indicating successful integration
            - 'message': integration status message
        
        Examples
        --------
        >>> prop = OrbitalPropagator()
        >>> r0 = [7000e3, 0, 0]  # 629 km altitude
        >>> v0 = [0, 7546, 0]    # circular velocity
        >>> T = 2*np.pi*np.sqrt((7000e3)**3 / prop.mu)  # orbital period
        >>> sol = prop.propagate(r0, v0, (0, T))
        """
        # Initial state vector
        state0 = np.concatenate([r0, v0])
        
        # Time evaluation points
        t_eval = np.arange(t_span[0], t_span[1], dt)
        
        # Integrate equations of motion
        sol = solve_ivp(
            fun=self.equations_of_motion,
            t_span=t_span,
            y0=state0,
            method=method,
            t_eval=t_eval,
            rtol=rtol,
            atol=atol,
            dense_output=False
        )
        
        # Extract results
        solution = {
            't': sol.t,
            'r': sol.y[0:3, :].T,  # Transpose to (n_points, 3)
            'v': sol.y[3:6, :].T,
            'success': sol.success,
            'message': sol.message
        }
        
        return solution


# Utility functions

def orbital_period(a, mu=const.GM_earth.value):
    """
    Calculate orbital period using Kepler's third law.
    
    T = 2π * sqrt(a³/μ)
    
    Parameters
    ----------
    a : float
        Semi-major axis in meters
    mu : float, optional
        Gravitational parameter in m^3/s^2
        Default is Earth's GM
    
    Returns
    -------
    T : float
        Orbital period in seconds
    
    Examples
    --------
    >>> a = 7000e3  # 7000 km (629 km altitude for Earth)
    >>> T = orbital_period(a)
    >>> print(f"Period: {T/60:.1f} minutes")
    """
    T = 2 * np.pi * np.sqrt(a**3 / mu)
    return T


def circular_velocity(r, mu=const.GM_earth.value):
    """
    Calculate circular orbital velocity at given radius.
    
    v_circ = sqrt(μ/r)
    
    Parameters
    ----------
    r : float
        Orbital radius from center of body in meters
    mu : float, optional
        Gravitational parameter in m^3/s^2
    
    Returns
    -------
    v : float
        Circular orbital velocity in m/s
    """
    v = np.sqrt(mu / r)
    return v


def orbital_energy(r, v, mu=const.GM_earth.value):
    """
    Calculate specific orbital energy (energy per unit mass).
    
    ε = v²/2 - μ/r
    
    This should be constant for Keplerian orbits.
    
    Parameters
    ----------
    r : array_like or float
        Position vector or radius in meters
    v : array_like or float
        Velocity vector or speed in m/s
    mu : float, optional
        Gravitational parameter
    
    Returns
    -------
    energy : float or ndarray
        Specific orbital energy in J/kg (m²/s²)
    """
    if isinstance(r, np.ndarray) and r.ndim > 1:
        r_mag = np.linalg.norm(r, axis=1)
    else:
        r_mag = np.linalg.norm(r) if isinstance(r, np.ndarray) else r
    
    if isinstance(v, np.ndarray) and v.ndim > 1:
        v_mag = np.linalg.norm(v, axis=1)
    else:
        v_mag = np.linalg.norm(v) if isinstance(v, np.ndarray) else v
    
    energy = (v_mag**2) / 2 - mu / r_mag
    
    return energy