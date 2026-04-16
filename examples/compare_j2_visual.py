"""
Comparación Visual 3D: Órbitas con/sin J2

Genera visualización 3D mostrando divergencia de órbitas.
"""

import numpy as np
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from src.propagator import OrbitalPropagator, orbital_period
from src.orbital_elements import keplerian_to_cartesian
from src.visualization import plot_j2_comparison_3d
from astropy import constants as const

def main():
    print("=" * 70)
    print("COMPARACIÓN VISUAL 3D: EFECTOS DE PERTURBACIÓN J2")
    print("=" * 70)
    
    # Parámetros
    R_earth = 6378137.0
    mu = const.GM_earth.value
    J2 = 1.08263e-3
    
    # Configurar órbita inclinada para ver efectos J2 claramente
    a = 7171e3          # ~800 km altitud
    e = 0.08            # Ligeramente elíptica
    i = np.radians(70)  # Inclinación alta
    RAAN = np.radians(0)
    omega = np.radians(90)
    nu = np.radians(0)
    
    T = orbital_period(a, mu)
    
    print(f"\nConfiguración de Órbita:")
    print(f"  Semieje mayor: {a/1e3:.1f} km")
    print(f"  Excentricidad: {e:.3f}")
    print(f"  Inclinación: {np.degrees(i):.0f}°")
    print(f"  Periodo: {T/60:.2f} min")
    
    # Convertir a Cartesiano
    r0, v0 = keplerian_to_cartesian(a, e, i, RAAN, omega, nu, mu)
    
    # Propagar por 20 órbitas (~33 horas)
    n_orbits = 20
    t_span = (0, T * n_orbits)
    
    print(f"\nPropagando {n_orbits} órbitas ({T*n_orbits/3600:.1f} horas)...")
    
    prop = OrbitalPropagator(mu=mu)
    
    # Sin J2
    print("[1/2] Sin J2...")
    sol_no_j2 = prop.propagate(r0, v0, t_span, dt=300.0)
    
    # Con J2
    print("[2/2] Con J2...")
    sol_j2 = prop.propagate_j2(r0, v0, t_span, dt=300.0, J2=J2, R_earth=R_earth)
    
    if sol_no_j2['success'] and sol_j2['success']:
        print("\n✓ Propagaciones exitosas!")
        
        # Calcular divergencia
        divergence = np.linalg.norm(sol_j2['r'][-1] - sol_no_j2['r'][-1])
        
        print(f"\nResultados:")
        print(f"  Tiempo simulado: {t_span[1]/3600:.1f} horas")
        print(f"  Puntos calculados: {len(sol_j2['t'])}")
        print(f"  Divergencia final: {divergence/1e3:.1f} km")
        
        # Crear directorio
        docs_dir = os.path.join(os.path.dirname(__file__), '..', 'docs')
        os.makedirs(docs_dir, exist_ok=True)
        
        # Generar visualización 3D
        print("\nGenerando visualización 3D...")
        
        plot_j2_comparison_3d(
            sol_no_j2,
            sol_j2,
            R_body=6371e3,
            title=f"Comparación 3D: Propagación con/sin J2 ({n_orbits} órbitas)",
            save_path=os.path.join(docs_dir, 'j2_comparison_3d.png'),
            show=True
        )
        
        print("\n" + "=" * 70)
        print("INTERPRETACIÓN:")
        print("=" * 70)
        print("\nLa gráfica 3D muestra:")
        print("  • Órbita AZUL (sin J2): plano orbital fijo en el espacio")
        print("  • Órbita ROJA (con J2): plano orbital rotando (precesión)")
        print(f"  • Divergencia de {divergence/1e3:.0f} km después de {n_orbits} órbitas")
        print("\nLa órbita roja 'gira' alrededor del eje polar debido al")
        print("achatamiento terrestre. Este efecto es crucial para:")
        print("  - Predicción precisa de trayectorias satelitales")
        print("  - Diseño de órbitas heliosíncronas")
        print("  - Planificación de maniobras orbitales")
        
        print("\n" + "=" * 70)
        print("✓ Visualización completa!")
        print(f"✓ Guardada: docs/j2_comparison_3d.png")
        print("=" * 70)
        
    else:
        print("\n✗ Error en propagación!")

if __name__ == "__main__":
    main()