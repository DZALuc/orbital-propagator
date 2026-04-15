"""
Test circular orbit propagation

This script validates the basic two-body propagator
with a simple circular Low Earth Orbit (LEO).
"""

import numpy as np
import sys
import os

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from src.propagator import OrbitalPropagator, orbital_period, circular_velocity, orbital_energy
from astropy import constants as const

def main():
    print("=" * 60)
    print("ORBITAL PROPAGATOR - Circular Orbit Test")
    print("=" * 60)
    
    # Earth parameters
    R_earth = 6371e3  # meters
    mu = const.GM_earth.value
    
    # Orbit parameters
    altitude = 400e3  # 400 km (ISS-like orbit)
    r_orbit = R_earth + altitude
    
    print(f"\nOrbit Configuration:")
    print(f"  Altitude: {altitude/1e3:.1f} km")
    print(f"  Orbital radius: {r_orbit/1e3:.1f} km")
    
    # Calculate circular velocity
    v_circ = circular_velocity(r_orbit, mu)
    print(f"  Circular velocity: {v_circ:.2f} m/s ({v_circ/1000:.2f} km/s)")
    
    # Calculate orbital period
    T = orbital_period(r_orbit, mu)
    print(f"  Orbital period: {T/60:.2f} minutes ({T/3600:.2f} hours)")
    
    # Initial conditions for circular orbit
    r0 = np.array([r_orbit, 0.0, 0.0])  # Start on X-axis
    v0 = np.array([0.0, v_circ, 0.0])    # Velocity in Y direction
    
    print(f"\nInitial State:")
    print(f"  Position: {r0/1e3} km")
    print(f"  Velocity: {v0/1e3} km/s")
    
    # Create propagator
    prop = OrbitalPropagator(mu=mu)
    
    # Propagate for one complete orbit
    t_span = (0, T)
    
    print(f"\nPropagating for {T/60:.2f} minutes...")
    
    solution = prop.propagate(r0, v0, t_span, dt=60.0)
    
    if solution['success']:
        print("✓ Integration successful!")
        print(f"  Integration message: {solution['message']}")
        print(f"  Number of time steps: {len(solution['t'])}")
        
        # Check orbit closure (should return to starting point)
        r_final = solution['r'][-1]
        r_error = np.linalg.norm(r_final - r0)
        print(f"\nOrbit Closure Check:")
        print(f"  Final position: {r_final/1e3} km")
        print(f"  Position error: {r_error:.2f} m ({r_error/1e3:.6f} km)")
        
        # Check energy conservation
        E0 = orbital_energy(solution['r'][0], solution['v'][0], mu)
        E_final = orbital_energy(solution['r'][-1], solution['v'][-1], mu)
        E_error = abs(E_final - E0)
        
        print(f"\nEnergy Conservation Check:")
        print(f"  Initial energy: {E0:.2f} J/kg")
        print(f"  Final energy: {E_final:.2f} J/kg")
        print(f"  Energy error: {E_error:.2e} J/kg")
        print(f"  Relative error: {E_error/abs(E0):.2e}")
        
        if E_error/abs(E0) < 1e-8:
            print("  ✓ Energy conserved to machine precision!")
        
    else:
        print("✗ Integration failed!")
        print(f"  Message: {solution['message']}")
    
    print("\n" + "=" * 60)
    print("Test complete!")
    print("=" * 60)

if __name__ == "__main__":
    main()