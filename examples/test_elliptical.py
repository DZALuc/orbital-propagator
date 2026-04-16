"""
Prueba de propagación de órbita elíptica

Este script valida el propagador con una órbita elíptica (excentricidad > 0)
y compara parámetros orbitales con valores teóricos.
"""

import numpy as np
import sys
import os

# Añadir src al path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from src.propagator import OrbitalPropagator, orbital_period, orbital_energy
from astropy import constants as const

def calculate_orbital_elements(r, v, mu):
    """
    Calcula elementos orbitales desde estado cartesiano.
    
    Parameters
    ----------
    r : array_like, shape (3,)
        Vector de posición [x, y, z] en metros
    v : array_like, shape (3,)
        Vector de velocidad [vx, vy, vz] en m/s
    mu : float
        Parámetro gravitacional en m³/s²
    
    Returns
    -------
    elements : dict
        Diccionario con elementos orbitales:
        - a: semieje mayor (m)
        - e: excentricidad
        - i: inclinación (rad)
        - h: momento angular específico (m²/s)
        - energy: energía específica (J/kg)
    """
    # Magnitudes
    r_mag = np.linalg.norm(r)
    v_mag = np.linalg.norm(v)
    
    # Momento angular específico h = r × v
    h_vec = np.cross(r, v)
    h = np.linalg.norm(h_vec)
    
    # Energía específica
    energy = (v_mag**2) / 2 - mu / r_mag
    
    # Semieje mayor: a = -μ/(2ε)
    a = -mu / (2 * energy)
    
    # Vector de excentricidad: e = (1/μ)[(v² - μ/r)r - (r·v)v]
    e_vec = (1/mu) * ((v_mag**2 - mu/r_mag) * r - np.dot(r, v) * v)
    e = np.linalg.norm(e_vec)
    
    # Inclinación: i = arccos(hz/h)
    i = np.arccos(h_vec[2] / h)
    
    return {
        'a': a,
        'e': e,
        'i': i,
        'h': h,
        'energy': energy
    }

def main():
    print("=" * 70)
    print("PROPAGADOR ORBITAL - Prueba de Órbita Elíptica")
    print("=" * 70)
    
    # Parámetros de la Tierra
    R_earth = 6371e3  # metros
    mu = const.GM_earth.value
    
    # Configuración de órbita elíptica
    # Perigeo: 400 km, Apogeo: 2000 km
    r_perigee = R_earth + 400e3   # 6771 km
    r_apogee = R_earth + 2000e3   # 8371 km
    
    # Semieje mayor: a = (rp + ra) / 2
    a = (r_perigee + r_apogee) / 2
    
    # Excentricidad: e = (ra - rp) / (ra + rp)
    e = (r_apogee - r_perigee) / (r_apogee + r_perigee)
    
    # Velocidad en perigeo: vp = sqrt(μ(1+e)/a(1-e))
    v_perigee = np.sqrt(mu * (1 + e) / (a * (1 - e)))
    
    print(f"\nConfiguración de Órbita Elíptica:")
    print(f"  Perigeo: {r_perigee/1e3:.1f} km ({(r_perigee-R_earth)/1e3:.0f} km altitud)")
    print(f"  Apogeo: {r_apogee/1e3:.1f} km ({(r_apogee-R_earth)/1e3:.0f} km altitud)")
    print(f"  Semieje mayor: {a/1e3:.1f} km")
    print(f"  Excentricidad: {e:.6f}")
    print(f"  Velocidad en perigeo: {v_perigee:.2f} m/s ({v_perigee/1e3:.3f} km/s)")
    
    # Periodo orbital
    T = orbital_period(a, mu)
    print(f"  Periodo orbital: {T/60:.2f} minutos ({T/3600:.2f} horas)")
    
    # Condiciones iniciales (en perigeo)
    r0 = np.array([r_perigee, 0.0, 0.0])  # En perigeo sobre eje X
    v0 = np.array([0.0, v_perigee, 0.0])  # Velocidad perpendicular
    
    # Calcular elementos orbitales teóricos
    elements_initial = calculate_orbital_elements(r0, v0, mu)
    
    print(f"\nElementos Orbitales Iniciales:")
    print(f"  Semieje mayor: {elements_initial['a']/1e3:.1f} km")
    print(f"  Excentricidad: {elements_initial['e']:.6f}")
    print(f"  Inclinación: {np.degrees(elements_initial['i']):.2f}°")
    print(f"  Momento angular: {elements_initial['h']:.2e} m²/s")
    print(f"  Energía: {elements_initial['energy']:.2f} J/kg")
    
    # Crear propagador
    prop = OrbitalPropagator(mu=mu)
    
    # Propagar por un periodo completo
    t_span = (0, T)
    
    print(f"\nPropagando por {T/60:.2f} minutos...")
    
    solution = prop.propagate(r0, v0, t_span, dt=60.0)
    
    if solution['success']:
        print("✓ Integración exitosa!")
        print(f"  Mensaje: {solution['message']}")
        print(f"  Número de pasos: {len(solution['t'])}")
        
        # Verificar cierre de órbita
        r_final = solution['r'][-1]
        r_error = np.linalg.norm(r_final - r0)
        
        print(f"\nVerificación de Cierre de Órbita:")
        print(f"  Posición final: [{r_final[0]/1e3:.3f}, {r_final[1]/1e3:.3f}, {r_final[2]/1e3:.3f}] km")
        print(f"  Error de posición: {r_error:.2f} m ({r_error/1e3:.6f} km)")
        
        # Calcular elementos orbitales finales
        elements_final = calculate_orbital_elements(
            solution['r'][-1], 
            solution['v'][-1], 
            mu
        )
        
        print(f"\nElementos Orbitales Finales:")
        print(f"  Semieje mayor: {elements_final['a']/1e3:.1f} km")
        print(f"  Excentricidad: {elements_final['e']:.6f}")
        print(f"  Inclinación: {np.degrees(elements_final['i']):.2f}°")
        
        # Verificar conservación de elementos orbitales
        a_error = abs(elements_final['a'] - elements_initial['a'])
        e_error = abs(elements_final['e'] - elements_initial['e'])
        h_error = abs(elements_final['h'] - elements_initial['h'])
        
        print(f"\nConservación de Elementos Orbitales:")
        print(f"  Error en semieje mayor: {a_error:.2f} m ({a_error/a*100:.2e}%)")
        print(f"  Error en excentricidad: {e_error:.2e}")
        print(f"  Error en momento angular: {h_error:.2e} m²/s ({h_error/elements_initial['h']*100:.2e}%)")
        
        # Verificar conservación de energía
        E_all = orbital_energy(solution['r'], solution['v'], mu)
        E_max = E_all.max()
        E_min = E_all.min()
        E_mean = E_all.mean()
        E_variation = E_max - E_min
        
        print(f"\nConservación de Energía:")
        print(f"  Energía media: {E_mean:.2f} J/kg")
        print(f"  Variación: {E_variation:.2e} J/kg")
        print(f"  Error relativo: {E_variation/abs(E_mean):.2e}")
        
        if E_variation/abs(E_mean) < 1e-8:
            print("  ✓ ¡Energía conservada a precisión de máquina!")
        
        # Encontrar perigeo y apogeo en la trayectoria
        r_magnitudes = np.linalg.norm(solution['r'], axis=1)
        r_min = r_magnitudes.min()
        r_max = r_magnitudes.max()
        
        print(f"\nVerificación de Perigeo/Apogeo:")
        print(f"  Perigeo calculado: {r_min/1e3:.3f} km (esperado: {r_perigee/1e3:.3f} km)")
        print(f"  Apogeo calculado: {r_max/1e3:.3f} km (esperado: {r_apogee/1e3:.3f} km)")
        print(f"  Error perigeo: {abs(r_min - r_perigee):.2f} m")
        print(f"  Error apogeo: {abs(r_max - r_apogee):.2f} m")
        
    else:
        print("✗ ¡Integración falló!")
        print(f"  Mensaje: {solution['message']}")
    
    print("\n" + "=" * 70)
    print("¡Prueba completa!")
    print("=" * 70)

if __name__ == "__main__":
    main()