"""
3D Interactive Visualization Module

Visualización 3D interactiva de órbitas y transferencias usando poliastro + Plotly.

Author: Damián Zúñiga Avelar
Date: Abril 2026
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

import numpy as np
from astropy import units as u
from astropy.time import Time

# poliastro imports
from poliastro.bodies import Earth, Sun, Mars
from poliastro.twobody import Orbit
from poliastro.plotting import OrbitPlotter3D
from poliastro.maneuver import Maneuver
from poliastro.core.maneuver import hohmann

# Nuestros módulos
from src.delta_v import hohmann_transfer
from src.mission_database import ORBITS_EARTH, get_orbit


def visualize_hohmann_transfer(r1_km, r2_km, orbit1_name="Initial", orbit2_name="Final"):
    """
    Visualiza transferencia Hohmann en 3D interactivo.
    
    Parameters
    ----------
    r1_km : float
        Radio órbita inicial (km)
    r2_km : float
        Radio órbita final (km)
    orbit1_name : str
        Nombre órbita inicial
    orbit2_name : str
        Nombre órbita final
    
    Returns
    -------
    plotter : OrbitPlotter3D
        Objeto plotter (llamar .show() para visualizar)
    """
    
    # Crear plotter
    plotter = OrbitPlotter3D()
    
    # Órbita inicial (circular)
    orbit_initial = Orbit.circular(Earth, r1_km * u.km)
    plotter.plot(orbit_initial, label=f"{orbit1_name} ({r1_km:.0f} km)", color='blue')
    
    # Órbita final (circular)
    orbit_final = Orbit.circular(Earth, r2_km * u.km)
    plotter.plot(orbit_final, label=f"{orbit2_name} ({r2_km:.0f} km)", color='green')
    
    # Órbita de transferencia
    a_transfer = (r1_km + r2_km) / 2  # Semi-major axis
    e_transfer = (r2_km - r1_km) / (r2_km + r1_km)  # Eccentricity
    
    orbit_transfer = Orbit.from_classical(
        Earth,
        a_transfer * u.km,
        e_transfer * u.one,
        0 * u.deg,  # inclination
        0 * u.deg,  # raan
        0 * u.deg,  # argp
        0 * u.deg   # nu (true anomaly)
    )
    plotter.plot(orbit_transfer, label=f"Transfer orbit", color='orange')
    
    return plotter


def visualize_common_mission(mission_key):
    """
    Visualiza misión común desde la base de datos.
    
    Parameters
    ----------
    mission_key : tuple
        (orbit1_key, orbit2_key) de ORBITS_EARTH
    
    Returns
    -------
    plotter : OrbitPlotter3D
    """
    orbit1_key, orbit2_key = mission_key
    
    orbit1 = get_orbit(orbit1_key)
    orbit2 = get_orbit(orbit2_key)
    
    r1_km = orbit1['radius_m'] / 1000
    r2_km = orbit2['radius_m'] / 1000
    
    return visualize_hohmann_transfer(
        r1_km, r2_km,
        orbit1['name'], 
        orbit2['name']
    )


def visualize_plane_change_transfer(r1_km, r2_km, delta_i_deg,
                                    orbit1_name="Initial", orbit2_name="Final"):
    """
    Visualiza transferencia con cambio de plano.
    
    Parameters
    ----------
    r1_km : float
        Radio órbita inicial (km)
    r2_km : float
        Radio órbita final (km)
    delta_i_deg : float
        Cambio de inclinación (grados)
    orbit1_name : str
    orbit2_name : str
    
    Returns
    -------
    plotter : OrbitPlotter3D
    """
    
    plotter = OrbitPlotter3D()
    
    # Órbita inicial (ecuatorial)
    orbit_initial = Orbit.from_classical(
        Earth,
        r1_km * u.km,
        0 * u.one,      # circular
        0 * u.deg,      # ecuatorial
        0 * u.deg,
        0 * u.deg,
        0 * u.deg
    )
    plotter.plot(orbit_initial, label=f"{orbit1_name} (i=0°)", color='blue')
    
    # Órbita final (inclinada)
    orbit_final = Orbit.from_classical(
        Earth,
        r2_km * u.km,
        0 * u.one,           # circular
        delta_i_deg * u.deg, # inclinada
        0 * u.deg,
        0 * u.deg,
        0 * u.deg
    )
    plotter.plot(orbit_final, label=f"{orbit2_name} (i={delta_i_deg}°)", color='green')
    
    # Órbita de transferencia (intermedia)
    a_transfer = (r1_km + r2_km) / 2
    e_transfer = abs(r2_km - r1_km) / (r2_km + r1_km)
    
    orbit_transfer = Orbit.from_classical(
        Earth,
        a_transfer * u.km,
        e_transfer * u.one,
        delta_i_deg/2 * u.deg,  # Inclinación intermedia
        0 * u.deg,
        0 * u.deg,
        0 * u.deg
    )
    plotter.plot(orbit_transfer, label="Transfer orbit", color='orange')
    
    return plotter


def visualize_multiple_orbits(orbit_keys):
    """
    Visualiza múltiples órbitas simultáneamente.
    
    Parameters
    ----------
    orbit_keys : list of str
        Lista de keys de ORBITS_EARTH
    
    Returns
    -------
    plotter : OrbitPlotter3D
    """
    
    plotter = OrbitPlotter3D()
    
    colors = ['blue', 'green', 'red', 'orange', 'purple', 'cyan']
    
    for i, key in enumerate(orbit_keys):
        orbit_data = get_orbit(key)
        r_km = orbit_data['radius_m'] / 1000
        inc_deg = orbit_data.get('inclination_deg', 0)
        
        orbit = Orbit.from_classical(
            Earth,
            r_km * u.km,
            0 * u.one,        # circular
            inc_deg * u.deg,
            0 * u.deg,
            0 * u.deg,
            0 * u.deg
        )
        
        color = colors[i % len(colors)]
        plotter.plot(orbit, label=orbit_data['name'], color=color)
    
    return plotter


def visualize_interplanetary(planet1_name="Earth", planet2_name="Mars"):
    """
    Visualiza transferencia interplanetaria.
    
    Parameters
    ----------
    planet1_name : str
        Planeta origen
    planet2_name : str
        Planeta destino
    
    Returns
    -------
    plotter : OrbitPlotter3D
    """
    
    # Crear plotter heliocéntrico
    plotter = OrbitPlotter3D()
    
    # Órbitas planetarias
    if planet1_name == "Earth":
        orbit1 = Orbit.circular(Sun, 1.0 * u.AU)
        plotter.plot(orbit1, label="Earth orbit", color='blue')
    
    if planet2_name == "Mars":
        orbit2 = Orbit.circular(Sun, 1.524 * u.AU)
        plotter.plot(orbit2, label="Mars orbit", color='red')
    
    # Órbita de transferencia (Hohmann heliocéntrico)
    a_transfer = (1.0 + 1.524) / 2  # AU
    e_transfer = (1.524 - 1.0) / (1.524 + 1.0)
    
    orbit_transfer = Orbit.from_classical(
        Sun,
        a_transfer * u.AU,
        e_transfer * u.one,
        0 * u.deg,
        0 * u.deg,
        0 * u.deg,
        0 * u.deg
    )
    plotter.plot(orbit_transfer, label="Hohmann transfer", color='orange')
    
    return plotter


def save_plot_html(plotter, filename):
    """
    Guarda visualización como HTML interactivo.
    
    Parameters
    ----------
    plotter : OrbitPlotter3D
    filename : str
        Nombre del archivo (sin extensión)
    """
    
    import os
    os.makedirs('docs/interactive', exist_ok=True)
    
    filepath = f'docs/interactive/{filename}.html'
    
    # Exportar HTML
    plotter._figure.write_html(filepath)
    
    print(f"\n✓ Visualización guardada: {filepath}")
    print(f"  Abre este archivo en tu navegador para interactuar")


# ============================================================================
# FUNCIONES DE ALTO NIVEL PARA CALCULADORA
# ============================================================================

def quick_visualize_mission(r1_km, r2_km, name1="Initial", name2="Final", 
                           show=True, save=False, filename=None):
    """
    Función rápida para visualizar desde calculadora.
    
    Parameters
    ----------
    r1_km : float
    r2_km : float
    name1 : str
    name2 : str
    show : bool
        Si True, muestra en navegador
    save : bool
        Si True, guarda HTML
    filename : str
        Nombre archivo para guardar
    """
    
    plotter = visualize_hohmann_transfer(r1_km, r2_km, name1, name2)
    
    if save and filename:
        save_plot_html(plotter, filename)
    
    if show:
        plotter.show()
    
    return plotter


if __name__ == "__main__":
    """
    Tests y ejemplos de uso.
    """
    
    print("\n" + "="*70)
    print(" "*20 + "3D VISUALIZATION TESTS")
    print("="*70 + "\n")
    
    # Test 1: Hohmann simple
    print("Test 1: LEO → GEO")
    plotter1 = visualize_hohmann_transfer(6771, 42157, "LEO", "GEO")
    save_plot_html(plotter1, "test_hohmann_leo_geo")
    
    # Test 2: Múltiples órbitas
    print("\nTest 2: Múltiples órbitas")
    plotter2 = visualize_multiple_orbits(['LEO_typical', 'ISS', 'GEO', 'Polar_SSO'])
    save_plot_html(plotter2, "test_multiple_orbits")
    
    # Test 3: Cambio de plano
    print("\nTest 3: Plane change")
    plotter3 = visualize_plane_change_transfer(6771, 42157, 28.5, "LEO", "GEO")
    save_plot_html(plotter3, "test_plane_change")
    
    # Test 4: Interplanetario
    print("\nTest 4: Earth → Mars")
    plotter4 = visualize_interplanetary("Earth", "Mars")
    save_plot_html(plotter4, "test_interplanetary")
    
    print("\n" + "="*70)
    print("✓ Todos los tests completados")
    print("  Ver archivos HTML en docs/interactive/")
    print("="*70 + "\n")