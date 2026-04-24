"""
Comparación de Estrategias de Empuje

Compara tres estrategias para transferencia LEO → GEO:
1. Hohmann impulsivo (químico)
2. Empuje tangencial continuo (eléctrico simple)
3. Empuje variable optimizado (eléctrico avanzado)

Author: Damián Zúñiga Avelar
Date: Abril 2026
"""

import numpy as np
import sys
import os
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from src.low_thrust import (LowThrustPropagator, TrajectoryOptimizer,
                              SpacecraftModel, tangential_thrust)
from src.orbital_elements import keplerian_to_cartesian
from astropy import constants as const


def plot_comparison_3d(sol_tangential, sol_optimized, title="Comparación"):
    """
    Compara dos trayectorias en 3D.
    """
    fig = plt.figure(figsize=(14, 6))
    
    # Subplot 1: Tangencial
    ax1 = fig.add_subplot(121, projection='3d')
    
    R_earth = 6371e3
    u = np.linspace(0, 2 * np.pi, 30)
    v = np.linspace(0, np.pi, 30)
    x_earth = R_earth/1e3 * np.outer(np.cos(u), np.sin(v))
    y_earth = R_earth/1e3 * np.outer(np.sin(u), np.sin(v))
    z_earth = R_earth/1e3 * np.outer(np.ones(np.size(u)), np.cos(v))
    
    ax1.plot_surface(x_earth, y_earth, z_earth, color='blue', 
                      alpha=0.2, linewidth=0)
    
    x1 = sol_tangential['r'][:, 0] / 1e3
    y1 = sol_tangential['r'][:, 1] / 1e3
    z1 = sol_tangential['r'][:, 2] / 1e3
    
    ax1.plot(x1, y1, z1, 'g-', linewidth=2, label='Tangencial')
    ax1.scatter(x1[0], y1[0], z1[0], c='green', s=100, marker='o')
    ax1.scatter(x1[-1], y1[-1], z1[-1], c='red', s=100, marker='s')
    
    ax1.set_xlabel('X (km)')
    ax1.set_ylabel('Y (km)')
    ax1.set_zlabel('Z (km)')
    ax1.set_title('Empuje Tangencial')
    ax1.legend()
    
    # Subplot 2: Optimizado
    ax2 = fig.add_subplot(122, projection='3d')
    
    ax2.plot_surface(x_earth, y_earth, z_earth, color='blue', 
                      alpha=0.2, linewidth=0)
    
    x2 = sol_optimized['r'][:, 0] / 1e3
    y2 = sol_optimized['r'][:, 1] / 1e3
    z2 = sol_optimized['r'][:, 2] / 1e3
    
    ax2.plot(x2, y2, z2, 'r-', linewidth=2, label='Optimizado')
    ax2.scatter(x2[0], y2[0], z2[0], c='green', s=100, marker='o')
    ax2.scatter(x2[-1], y2[-1], z2[-1], c='red', s=100, marker='s')
    
    ax2.set_xlabel('X (km)')
    ax2.set_ylabel('Y (km)')
    ax2.set_zlabel('Z (km)')
    ax2.set_title('Empuje Optimizado')
    ax2.legend()
    
    plt.suptitle(title)
    plt.tight_layout()
    
    return fig


def plot_thrust_profile(directions, times):
    """
    Visualiza el perfil de empuje optimizado.
    """
    fig, axes = plt.subplots(3, 1, figsize=(12, 8))
    
    # Crear escalera de direcciones
    t_plot = []
    ux_plot = []
    uy_plot = []
    uz_plot = []
    
    for i in range(len(directions)):
        t_start = times[i] / 86400  # días
        t_end = times[i+1] / 86400 if i < len(directions)-1 else times[-1] / 86400
        
        t_plot.extend([t_start, t_end])
        ux_plot.extend([directions[i, 0], directions[i, 0]])
        uy_plot.extend([directions[i, 1], directions[i, 1]])
        uz_plot.extend([directions[i, 2], directions[i, 2]])
    
    # Componentes
    axes[0].plot(t_plot, ux_plot, 'r-', linewidth=2)
    axes[0].set_ylabel('ux')
    axes[0].set_title('Perfil de Empuje Optimizado')
    axes[0].grid(True, alpha=0.3)
    axes[0].axhline(y=0, color='k', linestyle='--', alpha=0.3)
    
    axes[1].plot(t_plot, uy_plot, 'g-', linewidth=2)
    axes[1].set_ylabel('uy')
    axes[1].grid(True, alpha=0.3)
    axes[1].axhline(y=0, color='k', linestyle='--', alpha=0.3)
    
    axes[2].plot(t_plot, uz_plot, 'b-', linewidth=2)
    axes[2].set_ylabel('uz')
    axes[2].set_xlabel('Tiempo (días)')
    axes[2].grid(True, alpha=0.3)
    axes[2].axhline(y=0, color='k', linestyle='--', alpha=0.3)
    
    plt.tight_layout()
    
    return fig


def main():
    print("="*70)
    print("COMPARACIÓN DE ESTRATEGIAS DE EMPUJE")
    print("="*70)
    
    # Constantes
    mu = const.GM_earth.value
    R_earth = 6371e3
    
    # ========================================================================
    # CONFIGURACIÓN
    # ========================================================================
    
    print("\n[1/6] Configuración...")
    
    # Órbitas
    r_leo = R_earth + 400e3
    v_leo = np.sqrt(mu / r_leo)
    r0 = np.array([r_leo, 0.0, 0.0])
    v0 = np.array([0.0, v_leo, 0.0])
    
    r_geo = 42164e3
    v_geo = np.sqrt(mu / r_geo)
    r_target = np.array([r_geo, 0.0, 0.0])
    v_target = np.array([0.0, v_geo, 0.0])
    
    # Nave
    spacecraft = SpacecraftModel(
        thrust=0.1,
        isp=1500,
        m_dry=50.0,
        m_propellant=20.0
    )
    
    print(f"  Nave: {spacecraft}")
    
# Encontrar tiempo óptimo para empuje tangencial
    print(f"\n  Buscando tiempo óptimo...")
    
    from scipy.optimize import brentq
    
    def radius_at_time(t):
        """Radio alcanzado - radio GEO"""
        if t <= 0:
            return -r_geo
        
        sol_temp = prop.propagate_with_thrust(
            r0, v0, spacecraft.m_total,
            (0, t),
            spacecraft,
            tangential_thrust,
            dt=3600.0
        )
        
        if not sol_temp['success']:
            return 1e10
        
        r_final = sol_temp['r'][-1]
        return np.linalg.norm(r_final) - r_geo
    
    # Buscar tiempo que da radio GEO
    try:
        t_transfer = brentq(radius_at_time, 1*86400, 180*86400, xtol=3600)
        print(f"  ✓ Tiempo óptimo: {t_transfer/86400:.1f} días")
    except:
        t_transfer = 32 * 86400  # fallback
        print(f"  ⚠ Usando tiempo estimado: {t_transfer/86400:.0f} días")

    # ========================================================================
    # ESTRATEGIA 1: HOHMANN (BASELINE)
    # ========================================================================
    
    print("\n[2/6] Calculando Hohmann (químico)...")
    
    a_transfer = (r_leo + r_geo) / 2
    v_transfer_p = np.sqrt(mu * (2/r_leo - 1/a_transfer))
    v_transfer_a = np.sqrt(mu * (2/r_geo - 1/a_transfer))
    
    dv1 = v_transfer_p - v_leo
    dv2 = v_geo - v_transfer_a
    dv_total = abs(dv1) + abs(dv2)
    
    isp_chem = 300
    mass_ratio = np.exp(dv_total / (isp_chem * 9.80665))
    m_prop_hohmann = spacecraft.m_total * (1 - 1/mass_ratio)
    
    print(f"  ΔV total:     {dv_total:.0f} m/s")
    print(f"  Propelente:   {m_prop_hohmann:.2f} kg ({m_prop_hohmann/spacecraft.m_total*100:.1f}%)")
    
    # ========================================================================
    # ESTRATEGIA 2: TANGENCIAL
    # ========================================================================
    
    print("\n[3/6] Propagando empuje tangencial...")
    
    prop = LowThrustPropagator(mu=mu)
    
    sol_tangential = prop.propagate_with_thrust(
        r0, v0, spacecraft.m_total,
        (0, t_transfer),
        spacecraft,
        tangential_thrust,
        dt=1800.0  # 30 min
    )
    
    m_final_tang = sol_tangential['m'][-1]
    m_prop_tang = spacecraft.m_total - m_final_tang
    
    r_final_tang = sol_tangential['r'][-1]
    r_error_tang = np.linalg.norm(r_final_tang - r_target) / 1e3
    
    print(f"  ✓ Completado")
    print(f"  Propelente:   {m_prop_tang:.2f} kg ({m_prop_tang/spacecraft.m_total*100:.1f}%)")
    print(f"  Error final:  {r_error_tang:.1f} km")
    
    # ========================================================================
    # ESTRATEGIA 3: OPTIMIZADO
    # ========================================================================
    
    print("\n[4/6] Optimizando dirección variable...")
    
    optimizer = TrajectoryOptimizer(mu=mu)
    
    result_opt = optimizer.optimize_variable_direction(
        r0, v0, r_target, v_target,
        spacecraft,
        t_transfer,
        n_segments=3
    )
    
    sol_optimized = result_opt['solution']
    m_final_opt = sol_optimized['m'][-1]
    m_prop_opt = spacecraft.m_total - m_final_opt
    
    r_final_opt = sol_optimized['r'][-1]
    r_error_opt = np.linalg.norm(r_final_opt - r_target) / 1e3
    
    print(f"\n  Propelente:   {m_prop_opt:.2f} kg ({m_prop_opt/spacecraft.m_total*100:.1f}%)")
    print(f"  Error final:  {r_error_opt:.1f} km")
    
    # ========================================================================
    # COMPARACIÓN
    # ========================================================================
    
    print("\n" + "="*70)
    print("COMPARACIÓN DE RESULTADOS")
    print("="*70)
    
    print(f"\n{'Estrategia':<25} {'Propelente (kg)':<18} {'% Masa':<12} {'Tiempo':<12}")
    print("-"*70)
    print(f"{'Hohmann (químico)':<25} {m_prop_hohmann:>8.2f} kg       {m_prop_hohmann/spacecraft.m_total*100:>6.1f}%      5 horas")
    print(f"{'Tangencial (eléctrico)':<25} {m_prop_tang:>8.2f} kg       {m_prop_tang/spacecraft.m_total*100:>6.1f}%      {t_transfer/86400:.0f} días")
    print(f"{'Optimizado (eléctrico)':<25} {m_prop_opt:>8.2f} kg       {m_prop_opt/spacecraft.m_total*100:>6.1f}%      {t_transfer/86400:.0f} días")
    
    print(f"\n{'Mejoras:':<25}")
    mejora_tang = (m_prop_hohmann - m_prop_tang) / m_prop_hohmann * 100
    mejora_opt = (m_prop_hohmann - m_prop_opt) / m_prop_hohmann * 100
    mejora_opt_vs_tang = (m_prop_tang - m_prop_opt) / m_prop_tang * 100
    
    print(f"  Tangencial vs Hohmann:   {mejora_tang:>6.1f}%")
    print(f"  Optimizado vs Hohmann:   {mejora_opt:>6.1f}%")
    print(f"  Optimizado vs Tangencial: {mejora_opt_vs_tang:>6.1f}%")
    
    # ========================================================================
    # VISUALIZACIONES
    # ========================================================================
    
    print("\n[5/6] Generando visualizaciones...")
    
    # Comparación trayectorias
    fig1 = plot_comparison_3d(sol_tangential, sol_optimized,
                               "Comparación: Tangencial vs Optimizado")
    fig1.savefig('docs/thrust_comparison_3d.png', dpi=150, bbox_inches='tight')
    
    # Perfil de empuje
    fig2 = plot_thrust_profile(result_opt['directions'], result_opt['times'])
    fig2.savefig('docs/thrust_profile.png', dpi=150, bbox_inches='tight')
    
    print(f"  ✓ Gráficas guardadas")
    
    # ========================================================================
    # RESUMEN
    # ========================================================================
    
    print("\n" + "="*70)
    print("CONCLUSIÓN")
    print("="*70)
    
    print(f"\n✓ Tres estrategias evaluadas")
    print(f"✓ Químico: rápido pero ineficiente")
    print(f"✓ Eléctrico tangencial: eficiente y simple")
    print(f"✓ Eléctrico optimizado: MÁS eficiente")
    
    if mejora_opt_vs_tang > 1:
        print(f"\n🎉 Optimización avanzada logró {mejora_opt_vs_tang:.1f}% mejora adicional")
    
    print("\n[6/6] Mostrando gráficas...")
    plt.show()
    
    print("\n" + "="*70)


if __name__ == "__main__":
    main()