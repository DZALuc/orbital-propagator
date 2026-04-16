"""
Prueba de conversión de elementos orbitales

Valida conversión Cartesiano ↔ Kepleriano con diferentes tipos de órbitas.
"""

import numpy as np
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from src.orbital_elements import (cartesian_to_keplerian, keplerian_to_cartesian,
                                   print_orbital_elements, orbital_period_from_elements)
from astropy import constants as const

def test_conversion_accuracy(r_original, v_original, mu, orbit_name):
    """
    Prueba precisión de conversión ida y vuelta: Cartesiano → Kepleriano → Cartesiano
    """
    print(f"\n{'='*70}")
    print(f"PRUEBA: {orbit_name}")
    print('='*70)
    
    print("\nEstado Cartesiano Original:")
    print(f"  Posición:  [{r_original[0]/1e3:.3f}, {r_original[1]/1e3:.3f}, {r_original[2]/1e3:.3f}] km")
    print(f"  Velocidad: [{v_original[0]/1e3:.6f}, {v_original[1]/1e3:.6f}, {v_original[2]/1e3:.6f}] km/s")
    
    # Convertir a Keplerianos
    elements = cartesian_to_keplerian(r_original, v_original, mu)
    
    # Imprimir elementos
    print_orbital_elements(elements, degrees=True)
    
    # Convertir de vuelta a Cartesianos
    r_converted, v_converted = keplerian_to_cartesian(
        elements['a'], elements['e'], elements['i'],
        elements['RAAN'], elements['omega'], elements['nu'],
        mu
    )
    
    print("\nEstado Cartesiano Reconstruido:")
    print(f"  Posición:  [{r_converted[0]/1e3:.3f}, {r_converted[1]/1e3:.3f}, {r_converted[2]/1e3:.3f}] km")
    print(f"  Velocidad: [{v_converted[0]/1e3:.6f}, {v_converted[1]/1e3:.6f}, {v_converted[2]/1e3:.6f}] km/s")
    
    # Calcular errores
    r_error = np.linalg.norm(r_converted - r_original)
    v_error = np.linalg.norm(v_converted - v_original)
    
    print("\nErrores de Conversión (ida y vuelta):")
    print(f"  Error de posición:  {r_error:.6e} m ({r_error/1e3:.6e} km)")
    print(f"  Error de velocidad: {v_error:.6e} m/s")
    
    # Validación
    tolerance_r = 1e-6  # 1 micrómetro
    tolerance_v = 1e-9  # 1 nanómetro/segundo
    
    if r_error < tolerance_r and v_error < tolerance_v:
        print("\n  ✓ Conversión EXITOSA (precisión de máquina)")
        return True
    else:
        print("\n  ✗ Error excede tolerancia")
        return False


def main():
    print("="*70)
    print("PRUEBAS DE CONVERSIÓN DE ELEMENTOS ORBITALES")
    print("="*70)
    
    mu = const.GM_earth.value
    R_earth = 6371e3
    
    results = []
    
    # ================================================================
    # PRUEBA 1: Órbita Circular Ecuatorial (caso más simple)
    # ================================================================
    r1 = np.array([R_earth + 400e3, 0.0, 0.0])
    v1 = np.array([0.0, 7669.0, 0.0])
    results.append(test_conversion_accuracy(r1, v1, mu, "Órbita Circular Ecuatorial (ISS-like)"))
    
    # ================================================================
    # PRUEBA 2: Órbita Elíptica Ecuatorial
    # ================================================================
    r2 = np.array([R_earth + 400e3, 0.0, 0.0])  # Perigeo
    v2 = np.array([0.0, 8500.0, 0.0])  # Velocidad mayor → elíptica
    results.append(test_conversion_accuracy(r2, v2, mu, "Órbita Elíptica Ecuatorial"))
    
    # ================================================================
    # PRUEBA 3: Órbita Polar Circular
    # ================================================================
    r3 = np.array([R_earth + 800e3, 0.0, 0.0])
    v3 = np.array([0.0, 0.0, 7448.0])  # Velocidad en Z → polar
    results.append(test_conversion_accuracy(r3, v3, mu, "Órbita Polar Circular"))
    
    # ================================================================
    # PRUEBA 4: Órbita Inclinada Elíptica (caso general)
    # ================================================================
    # Iniciar en perigeo, 45° de inclinación
    a4 = 7500e3
    e4 = 0.2
    i4 = np.radians(45)
    RAAN4 = np.radians(30)
    omega4 = np.radians(60)
    nu4 = np.radians(0)  # En perigeo
    
    r4, v4 = keplerian_to_cartesian(a4, e4, i4, RAAN4, omega4, nu4, mu)
    results.append(test_conversion_accuracy(r4, v4, mu, "Órbita Inclinada Elíptica (45°, e=0.2)"))
    
    # ================================================================
    # PRUEBA 5: Órbita Geoestacionaria (GEO)
    # ================================================================
    # GEO: circular, ecuatorial, ~35,786 km de altitud
    r_geo = 42164e3  # Radio GEO
    v_geo = np.sqrt(mu / r_geo)
    
    r5 = np.array([r_geo, 0.0, 0.0])
    v5 = np.array([0.0, v_geo, 0.0])
    results.append(test_conversion_accuracy(r5, v5, mu, "Órbita Geoestacionaria (GEO)"))
    
    # ================================================================
    # PRUEBA 6: Órbita Altamente Elíptica (Molniya-type)
    # ================================================================
    # Tipo Molniya: e~0.7, i=63.4°
    a6 = 26600e3
    e6 = 0.74
    i6 = np.radians(63.4)
    RAAN6 = np.radians(0)
    omega6 = np.radians(270)  # Apogeo sobre polo norte
    nu6 = np.radians(0)
    
    r6, v6 = keplerian_to_cartesian(a6, e6, i6, RAAN6, omega6, nu6, mu)
    results.append(test_conversion_accuracy(r6, v6, mu, "Órbita Molniya (e=0.74, i=63.4°)"))
    
    # ================================================================
    # RESUMEN
    # ================================================================
    print("\n" + "="*70)
    print("RESUMEN DE PRUEBAS")
    print("="*70)
    
    total = len(results)
    passed = sum(results)
    
    print(f"\nTotal de pruebas: {total}")
    print(f"Exitosas:         {passed}")
    print(f"Fallidas:         {total - passed}")
    
    if passed == total:
        print("\n✓ TODAS LAS PRUEBAS PASARON")
        print("  Las conversiones Cartesiano ↔ Kepleriano son precisas a nivel de máquina.")
    else:
        print("\n✗ ALGUNAS PRUEBAS FALLARON")
    
    print("="*70)

if __name__ == "__main__":
    main()