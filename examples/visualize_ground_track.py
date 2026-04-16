"""
Visualización de Ground Track (Traza Terrestre)

Muestra la proyección de la órbita sobre la superficie terrestre.
"""

import numpy as np
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from src.propagator import OrbitalPropagator, orbital_period
from src.orbital_elements import keplerian_to_cartesian
from src.visualization import plot_ground_track
from astropy import constants as const

def main():
    print("=" * 70)
    print("GROUND TRACK - TRAZA TERRESTRE DEL SATÉLITE")
    print("=" * 70)
    
    # Parámetros
    mu = const.GM_earth.value
    
    # Configurar órbita tipo ISS (inclinación ~51.6°)
    # Altitud de 400 km
    a = 6771e3  # Radio orbital
    e = 0.0005  # Casi circular
    i = np.radians(51.6)  # Inclinación ISS
    RAAN = np.radians(0)
    omega = np.radians(0)
    nu = np.radians(0)
    
    T = orbital_period(a, mu)
    
    print(f"\nConfiguración de Órbita (tipo ISS):")
    print(f"  Altitud: ~400 km")
    print(f"  Inclinación: 51.6°")
    print(f"  Periodo: {T/60:.2f} min")
    
    # Convertir a Cartesiano
    r0, v0 = keplerian_to_cartesian(a, e, i, RAAN, omega, nu, mu)
    
    # Propagar por 5 órbitas (~8 horas)
    # Suficiente para ver regresión nodal
    n_orbits = 5
    t_span = (0, T * n_orbits)
    
    print(f"\nPropagando {n_orbits} órbitas ({T*n_orbits/3600:.1f} horas)...")
    
    prop = OrbitalPropagator(mu=mu)
    
    # Propagación simple (sin J2 para esta demo)
    sol = prop.propagate(r0, v0, t_span, dt=60.0)
    
    if sol['success']:
        print("✓ Propagación exitosa!")
        print(f"  Puntos calculados: {len(sol['t'])}")
        
        # Crear directorio
        docs_dir = os.path.join(os.path.dirname(__file__), '..', 'docs')
        os.makedirs(docs_dir, exist_ok=True)
        
        # Generar ground track
        print("\nGenerando ground track...")
        print("(Esto puede tomar 10-20 segundos por el renderizado del mapa...)")
        
        plot_ground_track(
            sol,
            title=f"Ground Track - Órbita tipo ISS ({n_orbits} órbitas)",
            earth_rotation=True,
            save_path=os.path.join(docs_dir, 'ground_track.png'),
            show=True
        )
        
        print("\n" + "=" * 70)
        print("INTERPRETACIÓN:")
        print("=" * 70)
        print("\nLa traza terrestre muestra:")
        print("  • Latitud máxima = Inclinación orbital (51.6°)")
        print("  • Cada pasada se desplaza hacia el OESTE")
        print("    (por rotación terrestre bajo el satélite)")
        print("  • Después de ~24 horas, las trazas se repiten")
        print("\nPara órbitas con J2, las trazas NO se repiten exactamente")
        print("debido a la precesión nodal.")
        
        print("\nAPLICACIONES:")
        print("  - Planificación de cobertura de sensores")
        print("  - Predicción de pases sobre estaciones terrestres")
        print("  - Análisis de tiempos de comunicación")
        print("  - Diseño de constelaciones satelitales")
        
        print("\n" + "=" * 70)
        print("✓ Ground track generado!")
        print(f"✓ Guardado: docs/ground_track.png")
        print("=" * 70)
        
    else:
        print("✗ Error en propagación!")
        print(f"  {sol['message']}")

if __name__ == "__main__":
    main()