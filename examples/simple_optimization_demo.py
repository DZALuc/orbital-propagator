"""
Demo Simplificado de Optimización

Compara empuje tangencial vs optimizado de forma rápida.
"""

import numpy as np
import sys
import os
import matplotlib.pyplot as plt

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from src.low_thrust import (LowThrustPropagator, SpacecraftModel, 
                              tangential_thrust)
from astropy import constants as const


def main():
    print("="*70)
    print("DEMO: OPTIMIZACIÓN SIMPLIFICADA")
    print("="*70)
    
    mu = const.GM_earth.value
    R_earth = 6371e3
    
    # Configuración
    r_leo = R_earth + 400e3
    v_leo = np.sqrt(mu / r_leo)
    r0 = np.array([r_leo, 0.0, 0.0])
    v0 = np.array([0.0, v_leo, 0.0])
    
    r_geo = 42164e3
    v_geo = np.sqrt(mu / r_geo)
    
    spacecraft = SpacecraftModel(
        thrust=0.1,
        isp=1500,
        m_dry=50.0,
        m_propellant=20.0
    )
    
    print(f"\nNave: {spacecraft}")
    
    # ========================================================================
    # ESTRATEGIA 1: TANGENCIAL (32 DÍAS)
    # ========================================================================
    
    print("\n[1/3] Empuje tangencial (tiempo óptimo)...")
    
    prop = LowThrustPropagator(mu=mu)
    
    # Usar tiempo conocido del ejemplo anterior
    t_transfer = 32.01 * 86400
    
    sol_tang = prop.propagate_with_thrust(
        r0, v0, spacecraft.m_total,
        (0, t_transfer),
        spacecraft,
        tangential_thrust,
        dt=1800.0
    )
    
    m_final_tang = sol_tang['m'][-1]
    m_prop_tang = spacecraft.m_total - m_final_tang
    
    r_final_tang = sol_tang['r'][-1]
    r_error_tang = np.linalg.norm(r_final_tang) - r_geo
    
    print(f"  Propelente: {m_prop_tang:.2f} kg")
    print(f"  Error radio: {r_error_tang/1e3:.1f} km")
    
    # ========================================================================
    # ESTRATEGIA 2: RADIAL PRIMERO, TANGENCIAL DESPUÉS
    # ========================================================================
    
    print("\n[2/3] Estrategia híbrida (radial + tangencial)...")
    
    # Empuje radial primeras 2 semanas, tangencial después
    def hybrid_thrust(t, state):
        if t < 14 * 86400:  # Primeros 14 días
            r_vec = state[0:3]
            r = np.linalg.norm(r_vec)
            return r_vec / r  # Radial
        else:  # Después
            v_vec = state[3:6]
            v = np.linalg.norm(v_vec)
            return v_vec / v if v > 0 else np.array([0, 1, 0])  # Tangencial
    
    sol_hybrid = prop.propagate_with_thrust(
        r0, v0, spacecraft.m_total,
        (0, t_transfer),
        spacecraft,
        hybrid_thrust,
        dt=1800.0
    )
    
    m_final_hybrid = sol_hybrid['m'][-1]
    m_prop_hybrid = spacecraft.m_total - m_final_hybrid
    
    r_final_hybrid = sol_hybrid['r'][-1]
    r_error_hybrid = np.linalg.norm(r_final_hybrid) - r_geo
    
    print(f"  Propelente: {m_prop_hybrid:.2f} kg")
    print(f"  Error radio: {r_error_hybrid/1e3:.1f} km")
    
    # ========================================================================
    # ESTRATEGIA 3: 75% TANGENCIAL, 25% RADIAL
    # ========================================================================
    
    print("\n[3/3] Mezcla tangencial-radial...")
    
    def mixed_thrust(t, state):
        r_vec = state[0:3]
        v_vec = state[3:6]
        
        r = np.linalg.norm(r_vec)
        v = np.linalg.norm(v_vec)
        
        u_radial = r_vec / r if r > 0 else np.array([1, 0, 0])
        u_tangential = v_vec / v if v > 0 else np.array([0, 1, 0])
        
        # Mezcla: 75% tangencial, 25% radial
        u = 0.75 * u_tangential + 0.25 * u_radial
        u_norm = np.linalg.norm(u)
        
        return u / u_norm if u_norm > 0 else u_tangential
    
    sol_mixed = prop.propagate_with_thrust(
        r0, v0, spacecraft.m_total,
        (0, t_transfer),
        spacecraft,
        mixed_thrust,
        dt=1800.0
    )
    
    m_final_mixed = sol_mixed['m'][-1]
    m_prop_mixed = spacecraft.m_total - m_final_mixed
    
    r_final_mixed = sol_mixed['r'][-1]
    r_error_mixed = np.linalg.norm(r_final_mixed) - r_geo
    
    print(f"  Propelente: {m_prop_mixed:.2f} kg")
    print(f"  Error radio: {r_error_mixed/1e3:.1f} km")
    
    # ========================================================================
    # COMPARACIÓN
    # ========================================================================
    
    print("\n" + "="*70)
    print("COMPARACIÓN DE RESULTADOS")
    print("="*70)
    
    print(f"\n{'Estrategia':<30} {'Propelente (kg)':<15} {'Error Radio (km)'}")
    print("-"*70)
    print(f"{'Tangencial puro':<30} {m_prop_tang:>8.2f}        {abs(r_error_tang)/1e3:>8.1f}")
    print(f"{'Híbrido (radial→tangencial)':<30} {m_prop_hybrid:>8.2f}        {abs(r_error_hybrid)/1e3:>8.1f}")
    print(f"{'Mezcla 75/25':<30} {m_prop_mixed:>8.2f}        {abs(r_error_mixed)/1e3:>8.1f}")
    
    # Mejor estrategia
    strategies = [
        ('Tangencial', m_prop_tang, abs(r_error_tang)),
        ('Híbrido', m_prop_hybrid, abs(r_error_hybrid)),
        ('Mezcla', m_prop_mixed, abs(r_error_mixed))
    ]
    
    # Ordenar por propelente usado
    strategies.sort(key=lambda x: x[1])
    
    print(f"\n✓ Mejor estrategia: {strategies[0][0]}")
    print(f"  Propelente: {strategies[0][1]:.2f} kg")
    print(f"  Error: {strategies[0][2]/1e3:.1f} km")
    
    # ========================================================================
    # VISUALIZACIÓN RÁPIDA
    # ========================================================================
    
    print("\n[Visualización] Generando gráfica...")
    
    fig, ax = plt.subplots(figsize=(10, 6))
    
    # Altitudes
    t_days_tang = sol_tang['t'] / 86400
    alt_tang = (np.linalg.norm(sol_tang['r'], axis=1) - R_earth) / 1e3
    
    t_days_hybrid = sol_hybrid['t'] / 86400
    alt_hybrid = (np.linalg.norm(sol_hybrid['r'], axis=1) - R_earth) / 1e3
    
    t_days_mixed = sol_mixed['t'] / 86400
    alt_mixed = (np.linalg.norm(sol_mixed['r'], axis=1) - R_earth) / 1e3
    
    ax.plot(t_days_tang, alt_tang, 'b-', linewidth=2, label='Tangencial')
    ax.plot(t_days_hybrid, alt_hybrid, 'r--', linewidth=2, label='Híbrido')
    ax.plot(t_days_mixed, alt_mixed, 'g:', linewidth=2, label='Mezcla 75/25')
    
    ax.axhline(y=35786, color='k', linestyle='--', alpha=0.5, label='GEO target')
    
    ax.set_xlabel('Tiempo (días)')
    ax.set_ylabel('Altitud (km)')
    ax.set_title('Comparación de Estrategias de Empuje')
    ax.legend()
    ax.grid(True, alpha=0.3)
    
    plt.tight_layout()
    plt.savefig('docs/simple_optimization_comparison.png', dpi=150, bbox_inches='tight')
    
    print(f"  ✓ Gráfica guardada: docs/simple_optimization_comparison.png")
    
    plt.show()
    
    print("\n" + "="*70)


if __name__ == "__main__":
    main()