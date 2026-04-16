"""
Prueba de perturbación J2

Compara propagación con y sin J2 para demostrar efectos de achatamiento terrestre.
"""

import numpy as np
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from src.propagator import OrbitalPropagator, orbital_period, circular_velocity
from astropy import constants as const

def main():
    print("=" * 70)
    print("PERTURBACIÓN J2 - Comparación con/sin Achatamiento Terrestre")
    print("=" * 70)
    
    # Parámetros de la Tierra
    R_earth = 6371e3
    mu = const.GM_earth.value
    J2 = 1.08263e-3
    
    # Órbita polar (inclinación 90°) - máximo efecto J2
    # Altitud: 800 km
    altitude = 800e3
    r_orbit = R_earth + altitude
    v_circ = circular_velocity(r_orbit, mu)
    T = orbital_period(r_orbit, mu)
    
    print(f"\nConfiguración de Órbita:")
    print(f"  Tipo: Órbita polar (inclinación 90°)")
    print(f"  Altitud: {altitude/1e3:.0f} km")
    print(f"  Radio orbital: {r_orbit/1e3:.1f} km")
    print(f"  Velocidad circular: {v_circ/1e3:.3f} km/s")
    print(f"  Periodo: {T/60:.2f} minutos")
    print(f"  Coeficiente J2: {J2:.6e}")
    
    # Condiciones iniciales: órbita polar
    # Posición en ecuador, velocidad hacia el polo norte
    r0 = np.array([r_orbit, 0.0, 0.0])  # Sobre ecuador
    v0 = np.array([0.0, 0.0, v_circ])   # Velocidad hacia polo
    
    print(f"\nCondiciones Iniciales:")
    print(f"  Posición: [{r0[0]/1e3:.1f}, {r0[1]/1e3:.1f}, {r0[2]/1e3:.1f}] km")
    print(f"  Velocidad: [{v0[0]/1e3:.3f}, {v0[1]/1e3:.3f}, {v0[2]/1e3:.3f}] km/s")
    
    # Propagar por 5 órbitas para ver efectos acumulativos
    n_orbits = 5
    t_span = (0, T * n_orbits)
    
    print(f"\nPropagando por {n_orbits} órbitas ({T*n_orbits/3600:.2f} horas)...")
    
    # Crear propagador
    prop = OrbitalPropagator(mu=mu)
    
    # Propagación SIN J2 (modelo ideal)
    print("\n1. Propagación sin J2 (modelo ideal de dos cuerpos)...")
    sol_no_j2 = prop.propagate(r0, v0, t_span, dt=120.0)
    
    # Propagación CON J2 (modelo realista)
    print("2. Propagación con J2 (modelo realista)...")
    sol_j2 = prop.propagate_j2(r0, v0, t_span, dt=120.0, J2=J2)
    
    if sol_no_j2['success'] and sol_j2['success']:
        print("\n✓ Ambas integraciones exitosas!")
        
        # Comparar posiciones finales
        r_final_no_j2 = sol_no_j2['r'][-1]
        r_final_j2 = sol_j2['r'][-1]
        
        position_difference = np.linalg.norm(r_final_j2 - r_final_no_j2)
        
        print(f"\nPosición Final:")
        print(f"  Sin J2: [{r_final_no_j2[0]/1e3:.3f}, {r_final_no_j2[1]/1e3:.3f}, {r_final_no_j2[2]/1e3:.3f}] km")
        print(f"  Con J2: [{r_final_j2[0]/1e3:.3f}, {r_final_j2[1]/1e3:.3f}, {r_final_j2[2]/1e3:.3f}] km")
        print(f"  Diferencia: {position_difference/1e3:.3f} km ({position_difference:.1f} m)")
        
        # Analizar desviación en cada eje
        diff_vec = r_final_j2 - r_final_no_j2
        print(f"\nDiferencia por Componente:")
        print(f"  ΔX: {diff_vec[0]/1e3:.3f} km ({diff_vec[0]:.1f} m)")
        print(f"  ΔY: {diff_vec[1]/1e3:.3f} km ({diff_vec[1]:.1f} m)")
        print(f"  ΔZ: {diff_vec[2]/1e3:.3f} km ({diff_vec[2]:.1f} m)")
        
        # Calcular desviación máxima durante toda la trayectoria
        max_deviation = 0
        max_deviation_time = 0
        
        for i in range(len(sol_j2['t'])):
            dev = np.linalg.norm(sol_j2['r'][i] - sol_no_j2['r'][i])
            if dev > max_deviation:
                max_deviation = dev
                max_deviation_time = sol_j2['t'][i]
        
        print(f"\nDesviación Máxima Durante Propagación:")
        print(f"  Magnitud: {max_deviation/1e3:.3f} km ({max_deviation:.1f} m)")
        print(f"  Tiempo: {max_deviation_time/60:.2f} minutos")
        print(f"  Órbita: {max_deviation_time/T:.2f}")
        
        # Calcular magnitud de aceleración J2 vs two-body
        r_sample = sol_j2['r'][len(sol_j2['r'])//2]  # Punto medio
        x, y, z = r_sample
        r_mag = np.linalg.norm(r_sample)
        
        # Aceleración two-body
        a_two_body = mu / r_mag**2
        
        # Aceleración J2 (aproximada)
        factor = (3.0/2.0) * J2 * mu * (6378137.0)**2 / r_mag**4
        a_j2_approx = factor * abs(5*(z/r_mag)**2 - 1)
        
        print(f"\nMagnitud de Aceleraciones (punto medio de trayectoria):")
        print(f"  Two-body: {a_two_body:.6f} m/s²")
        print(f"  J2 (aprox): {a_j2_approx:.6e} m/s²")
        print(f"  Ratio J2/Two-body: {a_j2_approx/a_two_body:.6e} ({a_j2_approx/a_two_body*100:.4f}%)")
        
        print(f"\n" + "="*70)
        print("INTERPRETACIÓN:")
        print("="*70)
        print(f"Después de {n_orbits} órbitas polares a {altitude/1e3:.0f} km de altitud:")
        print(f"  - La perturbación J2 causó una desviación de {position_difference/1e3:.2f} km")
        print(f"  - El efecto J2 es ~{a_j2_approx/a_two_body*100:.3f}% de la gravedad principal")
        print(f"  - Para predicción precisa de trayectorias, J2 es ESENCIAL")
        print(f"\nEsto demuestra por qué los sistemas de navegación satelital (GPS, etc.)")
        print(f"deben incluir J2 en sus modelos de propagación orbital.")
        
    else:
        print("✗ Error en integración!")
        if not sol_no_j2['success']:
            print(f"  Sin J2: {sol_no_j2['message']}")
        if not sol_j2['success']:
            print(f"  Con J2: {sol_j2['message']}")
    
    print("\n" + "=" * 70)
    print("¡Prueba completa!")
    print("=" * 70)

if __name__ == "__main__":
    main()