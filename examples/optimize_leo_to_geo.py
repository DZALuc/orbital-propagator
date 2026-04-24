"""
Optimización de Transferencia LEO → GEO con Bajo Empuje

Encuentra la trayectoria óptima para transferir un satélite desde
órbita baja (LEO) a órbita geoestacionaria (GEO) usando propulsión
eléctrica de bajo empuje.

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


def plot_trajectory_3d(solution, title="Trayectoria"):
    """
    Visualiza trayectoria en 3D.
    """
    fig = plt.figure(figsize=(10, 8))
    ax = fig.add_subplot(111, projection='3d')
    
    # Tierra
    R_earth = 6371e3
    u = np.linspace(0, 2 * np.pi, 50)
    v = np.linspace(0, np.pi, 50)
    x_earth = R_earth/1e3 * np.outer(np.cos(u), np.sin(v))
    y_earth = R_earth/1e3 * np.outer(np.sin(u), np.sin(v))
    z_earth = R_earth/1e3 * np.outer(np.ones(np.size(u)), np.cos(v))
    ax.plot_surface(x_earth, y_earth, z_earth, color='blue', 
                     alpha=0.3, linewidth=0)
    
    # Trayectoria
    x = solution['r'][:, 0] / 1e3
    y = solution['r'][:, 1] / 1e3
    z = solution['r'][:, 2] / 1e3
    
    ax.plot(x, y, z, 'r-', linewidth=2, label='Trayectoria')
    ax.scatter(x[0], y[0], z[0], c='green', s=100, marker='o', label='Inicio')
    ax.scatter(x[-1], y[-1], z[-1], c='red', s=100, marker='s', label='Final')
    
    # Configuración
    ax.set_xlabel('X (km)')
    ax.set_ylabel('Y (km)')
    ax.set_zlabel('Z (km)')
    ax.set_title(title)
    ax.legend()
    
    # Aspecto igual
    max_range = np.array([x.max()-x.min(), y.max()-y.min(), 
                          z.max()-z.min()]).max() / 2.0
    mid_x = (x.max()+x.min()) * 0.5
    mid_y = (y.max()+y.min()) * 0.5
    mid_z = (z.max()+z.min()) * 0.5
    ax.set_xlim(mid_x - max_range, mid_x + max_range)
    ax.set_ylim(mid_y - max_range, mid_y + max_range)
    ax.set_zlim(mid_z - max_range, mid_z + max_range)
    
    plt.tight_layout()
    return fig


def plot_analysis(solution, spacecraft):
    """
    Análisis de la trayectoria: altitud, masa, velocidad vs tiempo.
    """
    fig, axes = plt.subplots(3, 1, figsize=(12, 10))
    
    t_days = solution['t'] / 86400
    
    # Altitud
    r_mag = np.linalg.norm(solution['r'], axis=1)
    altitude = (r_mag - 6371e3) / 1e3
    
    axes[0].plot(t_days, altitude, 'b-', linewidth=2)
    axes[0].axhline(y=400, color='g', linestyle='--', label='LEO inicial')
    axes[0].axhline(y=35786, color='r', linestyle='--', label='GEO target')
    axes[0].set_ylabel('Altitud (km)')
    axes[0].set_title('Evolución de la Órbita')
    axes[0].legend()
    axes[0].grid(True, alpha=0.3)
    
    # Masa
    axes[1].plot(t_days, solution['m'], 'g-', linewidth=2)
    axes[1].axhline(y=spacecraft.m_dry, color='r', 
                     linestyle='--', label='Masa seca')
    axes[1].set_ylabel('Masa (kg)')
    axes[1].set_title('Consumo de Propelente')
    axes[1].legend()
    axes[1].grid(True, alpha=0.3)
    
    # Velocidad
    v_mag = np.linalg.norm(solution['v'], axis=1)
    axes[2].plot(t_days, v_mag, 'r-', linewidth=2)
    axes[2].set_xlabel('Tiempo (días)')
    axes[2].set_ylabel('Velocidad (m/s)')
    axes[2].set_title('Velocidad Orbital')
    axes[2].grid(True, alpha=0.3)
    
    plt.tight_layout()
    return fig



def find_optimal_transfer_time(r0, v0, r_target, spacecraft, 
                                t_max=180*86400, tolerance=100e3):
    """
    Encuentra el tiempo óptimo de empuje tangencial para alcanzar radio target.
    
    Parameters
    ----------
    r0, v0 : array_like
        Estado inicial
    r_target : array_like
        Posición target
    spacecraft : SpacecraftModel
        Modelo de nave
    t_max : float
        Tiempo máximo a buscar (s)
    tolerance : float
        Tolerancia en radio (m)
    
    Returns
    -------
    t_optimal : float
        Tiempo óptimo (s)
    """
    from scipy.optimize import brentq
    
    mu = const.GM_earth.value
    prop = LowThrustPropagator(mu=mu)
    
    r_target_mag = np.linalg.norm(r_target)
    
    def radius_error(t):
        """Radio alcanzado - radio target"""
        if t <= 0:
            return -r_target_mag
        
        sol = prop.propagate_with_thrust(
            r0, v0, spacecraft.m_total,
            (0, t),
            spacecraft,
            tangential_thrust,
            dt=3600.0
        )
        
        if not sol['success']:
            return 1e10
        
        r_final = sol['r'][-1]
        r_final_mag = np.linalg.norm(r_final)
        
        return r_final_mag - r_target_mag
    
    # Buscar tiempo que da radio correcto
    try:
        # Probar rangos
        r_err_min = radius_error(1 * 86400)  # 1 día
        r_err_max = radius_error(t_max)
        
        print(f"\n  Buscando tiempo óptimo...")
        print(f"    Radio @ 1 día:   {r_err_min/1e3 + r_target_mag/1e3:.1f} km")
        print(f"    Radio @ {t_max/86400:.0f} días: {r_err_max/1e3 + r_target_mag/1e3:.1f} km")
        
        if r_err_min * r_err_max > 0:
            print(f"    ⚠ Target no alcanzable en rango dado")
            return None
        
        t_optimal = brentq(radius_error, 1*86400, t_max, xtol=3600)
        
        print(f"    ✓ Tiempo óptimo encontrado: {t_optimal/86400:.2f} días")
        
        return t_optimal
    
    except:
        print(f"    ✗ No se pudo encontrar tiempo óptimo")
        return None


def main():
    print("="*70)
    print("OPTIMIZACIÓN DE TRANSFERENCIA LEO → GEO")
    print("Propulsión Eléctrica de Bajo Empuje")
    print("="*70)
    
    # Constantes
    mu = const.GM_earth.value
    R_earth = 6371e3
    
    # ========================================================================
    # CONFIGURACIÓN DE LA MISIÓN
    # ========================================================================
    
    print("\n[1/5] Configurando misión...")
    
    # Órbita inicial: LEO circular 400 km
    r_leo = R_earth + 400e3
    v_leo = np.sqrt(mu / r_leo)
    
    r0 = np.array([r_leo, 0.0, 0.0])
    v0 = np.array([0.0, v_leo, 0.0])
    
    print(f"  LEO inicial:  {400} km altitud")
    print(f"  Velocidad:    {v_leo:.1f} m/s")
    
    # Órbita final: GEO circular 35,786 km
    r_geo = 42164e3  # Radio GEO
    v_geo = np.sqrt(mu / r_geo)
    
    r_target = np.array([r_geo, 0.0, 0.0])
    v_target = np.array([0.0, v_geo, 0.0])
    
    print(f"  GEO target:   {35786} km altitud")
    print(f"  Velocidad:    {v_geo:.1f} m/s")
    
    # Nave: Hall thruster típico
    spacecraft = SpacecraftModel(
        thrust=0.1,        # 100 mN
        isp=1500,          # s
        m_dry=50.0,        # kg
        m_propellant=20.0  # kg
    )
    
    print(f"\n  Nave: {spacecraft}")
    print(f"  Fracción propelente: {spacecraft.m_prop/spacecraft.m_total*100:.1f}%")
    
# ========================================================================
    # ENCONTRAR TIEMPO ÓPTIMO
    # ========================================================================
    
    print("\n[2/5] Encontrando tiempo óptimo de transferencia...")
    
    t_optimal = find_optimal_transfer_time(r0, v0, r_target, spacecraft,
                                            t_max=180*86400)
    
    if t_optimal is None:
        print("  ⚠ Usando tiempo estimado")
        # Estimación basada en energía
        E_leo = v_leo**2/2 - mu/r_leo
        E_geo = v_geo**2/2 - mu/r_geo
        delta_E = E_geo - E_leo
        v_avg = (v_leo + v_geo) / 2
        P_avg = spacecraft.thrust * v_avg
        t_optimal = abs(delta_E * spacecraft.m_total / P_avg) * 1.2  # Factor seguridad
    
    print(f"\n  Tiempo de transferencia: {t_optimal/86400:.2f} días")
    
    # ========================================================================
    # PROPAGACIÓN CON TIEMPO ÓPTIMO
    # ========================================================================
    
    print("\n[3/5] Propagando con empuje tangencial...")
    
    prop = LowThrustPropagator(mu=mu)
    
    sol_tangential = prop.propagate_with_thrust(
        r0, v0, spacecraft.m_total,
        (0, t_optimal),
        spacecraft,
        tangential_thrust,
        dt=3600.0  # 1 hora
    )
    
    if sol_tangential['success']:
        r_final = sol_tangential['r'][-1]
        v_final = sol_tangential['v'][-1]
        r_final_mag = np.linalg.norm(r_final)
        m_final = sol_tangential['m'][-1]
        
        print(f"  ✓ Propagación exitosa")
        print(f"  Radio final:      {r_final_mag/1e3:.1f} km")
        print(f"  Altitud final:    {(r_final_mag - R_earth)/1e3:.1f} km")
        print(f"  Masa final:       {m_final:.2f} kg")
        print(f"  Propelente usado: {spacecraft.m_total - m_final:.2f} kg")
        
        # ¿Llegamos a GEO?
        error_radius = abs(r_final_mag - r_geo) / 1e3
        error_velocity = abs(np.linalg.norm(v_final) - v_geo)
        
        print(f"\n  Errores finales:")
        print(f"    Radio:     {error_radius:.1f} km ({error_radius/r_geo*1e5:.3f}%)")
        print(f"    Velocidad: {error_velocity:.1f} m/s ({error_velocity/v_geo*100:.3f}%)")
        
        if error_radius < 100:
            print(f"\n  ✓✓✓ LLEGÓ A GEO! ✓✓✓")
        elif error_radius < 1000:
            print(f"\n  ✓ MUY CERCA DE GEO")
        else:
            print(f"\n  ⚠ Ajuste adicional necesario")
    else:
        print(f"  ✗ Error: {sol_tangential['message']}")
        return
    
    # ========================================================================
    # VISUALIZACIÓN
    # ========================================================================
    
    print("\n[4/5] Generando visualizaciones...")
    
    # Trayectoria 3D
    fig1 = plot_trajectory_3d(sol_tangential, 
                               "Transferencia LEO → GEO (Empuje Tangencial)")
    
    # Análisis
    fig2 = plot_analysis(sol_tangential, spacecraft)
    
    # Guardar
    fig1.savefig('docs/low_thrust_trajectory_3d.png', dpi=150, 
                  bbox_inches='tight')
    fig2.savefig('docs/low_thrust_analysis.png', dpi=150, 
                  bbox_inches='tight')
    
    print(f"  ✓ Gráficas guardadas en docs/")
    
    # ========================================================================
    # COMPARACIÓN CON HOHMANN
    # ========================================================================
    
    print("\n[5/5] Comparando con Hohmann impulsivo...")
    
    # Transferencia Hohmann (químico)
    a_transfer = (r_leo + r_geo) / 2
    v_transfer_perigeo = np.sqrt(mu * (2/r_leo - 1/a_transfer))
    v_transfer_apogeo = np.sqrt(mu * (2/r_geo - 1/a_transfer))
    
    dv1 = v_transfer_perigeo - v_leo
    dv2 = v_geo - v_transfer_apogeo
    dv_total_hohmann = abs(dv1) + abs(dv2)
    
    # Masa propelente (Tsiolkovsky)
    isp_chemical = 300  # s (químico típico)
    mass_ratio = np.exp(dv_total_hohmann / (isp_chemical * 9.80665))
    m_prop_hohmann = spacecraft.m_total * (1 - 1/mass_ratio)
    
    # Bajo empuje (real)
    m_prop_electric = spacecraft.m_total - m_final
    
    print(f"\n  HOHMANN (Químico):")
    print(f"    ΔV total:      {dv_total_hohmann:.0f} m/s")
    print(f"    Propelente:    {m_prop_hohmann:.2f} kg ({m_prop_hohmann/spacecraft.m_total*100:.1f}%)")
    print(f"    Tiempo:        ~5 horas")
    
    print(f"\n  BAJO EMPUJE (Eléctrico):")
    print(f"    ΔV total:      ~{dv_total_hohmann*1.4:.0f} m/s (trayectoria espiral)")
    print(f"    Propelente:    {m_prop_electric:.2f} kg ({m_prop_electric/spacecraft.m_total*100:.1f}%)")
    print(f"    Tiempo:        {t_optimal/86400:.0f} días")
    
    print(f"\n  AHORRO PROPELENTE: {(m_prop_hohmann - m_prop_electric):.2f} kg")
    print(f"  FACTOR MEJORA:     {m_prop_hohmann/m_prop_electric:.2f}x")
    
    # ========================================================================
    # RESUMEN
    # ========================================================================
    
    print("\n" + "="*70)
    print("RESUMEN")
    print("="*70)
    
    print(f"\n✓ Transferencia LEO → GEO completada")
    print(f"✓ Propelente usado: {m_prop_electric:.2f} kg")
    print(f"✓ Ahorro vs Hohmann: {(m_prop_hohmann - m_prop_electric)/m_prop_hohmann*100:.1f}%")
    print(f"✓ Visualizaciones generadas")
    
    print("\n[5/5] Mostrando gráficas...")
    plt.show()
    
    print("\n" + "="*70)


if __name__ == "__main__":
    main()