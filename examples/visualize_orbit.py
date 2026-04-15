"""
Visualize orbital propagation results

Generates 2D, 3D, and analysis plots for orbital trajectory.
"""

import numpy as np
import sys
import os

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from src.propagator import OrbitalPropagator, orbital_period, circular_velocity
from src.visualization import (plot_orbit_2d, plot_orbit_3d, 
                                plot_orbital_elements, plot_position_components)
from astropy import constants as const

def main():
    print("=" * 60)
    print("ORBITAL VISUALIZATION - Circular LEO Orbit")
    print("=" * 60)
    
    # Earth parameters
    R_earth = 6371e3  # meters
    mu = const.GM_earth.value
    
    # Orbit setup - ISS-like orbit
    altitude = 400e3  # 400 km
    r_orbit = R_earth + altitude
    v_circ = circular_velocity(r_orbit, mu)
    T = orbital_period(r_orbit, mu)
    
    print(f"\nOrbit: {altitude/1e3:.0f} km altitude")
    print(f"Period: {T/60:.2f} minutes")
    print(f"Velocity: {v_circ/1e3:.2f} km/s")
    
    # Initial conditions
    r0 = np.array([r_orbit, 0.0, 0.0])
    v0 = np.array([0.0, v_circ, 0.0])
    
    # Propagate
    print(f"\nPropagating for {T/60:.2f} minutes...")
    prop = OrbitalPropagator(mu=mu)
    solution = prop.propagate(r0, v0, (0, T), dt=60.0)
    
    if not solution['success']:
        print(f"✗ Integration failed: {solution['message']}")
        return
    
    print("✓ Integration successful!")
    print(f"\nGenerating visualizations...")
    
    # Create docs directory if doesn't exist
    docs_dir = os.path.join(os.path.dirname(__file__), '..', 'docs')
    os.makedirs(docs_dir, exist_ok=True)
    
    # Generate plots
    print("\n1. 2D Projection...")
    plot_orbit_2d(solution, R_body=R_earth, 
                  title="ISS-like Orbit - 400 km Altitude (2D)",
                  save_path=os.path.join(docs_dir, 'orbit_2d.png'),
                  show=False)
    
    print("2. 3D Trajectory...")
    plot_orbit_3d(solution, R_body=R_earth,
                  title="ISS-like Orbit - 400 km Altitude (3D)",
                  save_path=os.path.join(docs_dir, 'orbit_3d.png'),
                  show=False)
    
    print("3. Orbital Elements...")
    plot_orbital_elements(solution, mu=mu,
                          save_path=os.path.join(docs_dir, 'orbital_elements.png'),
                          show=False)
    
    print("4. Position Components...")
    plot_position_components(solution,
                             save_path=os.path.join(docs_dir, 'position_components.png'),
                             show=False)
    
    print("\n" + "=" * 60)
    print("✓ All visualizations generated successfully!")
    print(f"✓ Figures saved in: {docs_dir}/")
    print("=" * 60)
    
    # Display all plots
    print("\nDisplaying plots (close windows to continue)...")
    import matplotlib.pyplot as plt
    
    # Regenerate for display
    plot_orbit_2d(solution, R_body=R_earth, show=True)
    plot_orbit_3d(solution, R_body=R_earth, show=True)
    plot_orbital_elements(solution, mu=mu, show=True)
    plot_position_components(solution, show=True)

if __name__ == "__main__":
    main()