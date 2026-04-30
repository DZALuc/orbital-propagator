"""
Delta-V Visualization Tool

Genera gráficas comparativas de estrategias de transferencia orbital.

Author: Damián Zúñiga Avelar
Date: Abril 2026
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from src.delta_v import *
from src.mission_database import ORBITS_EARTH
import matplotlib.pyplot as plt
import numpy as np


def plot_hohmann_vs_bielliptic():
    """
    Gráfica: Hohmann vs Bi-elliptic en función del ratio r2/r1.
    """
    print("Generando: Hohmann vs Bi-elliptic...")
    
    # Rango de ratios
    ratios = np.linspace(2, 30, 100)
    r1 = 6771e3  # LEO
    
    delta_v_hohmann = []
    delta_v_bielliptic = []
    
    for ratio in ratios:
        r2 = r1 * ratio
        
        # Hohmann
        h = hohmann_transfer(r1, r2)
        delta_v_hohmann.append(h['delta_v_total'])
        
        # Bi-elliptic (óptima)
        try:
            b = find_optimal_bielliptic(r1, r2)
            delta_v_bielliptic.append(b['delta_v_total'])
        except:
            delta_v_bielliptic.append(np.nan)
    
    # Crear figura
    fig, ax = plt.subplots(figsize=(10, 6))
    
    ax.plot(ratios, np.array(delta_v_hohmann)/1000, 'b-', linewidth=2, label='Hohmann')
    ax.plot(ratios, np.array(delta_v_bielliptic)/1000, 'r--', linewidth=2, label='Bi-elliptic (óptima)')
    
    # Línea crítica
    ax.axvline(11.94, color='gray', linestyle=':', alpha=0.5, label='Ratio crítico (11.94)')
    
    ax.set_xlabel('Ratio r₂/r₁', fontsize=12)
    ax.set_ylabel('ΔV total (km/s)', fontsize=12)
    ax.set_title('Comparación Hohmann vs Bi-elliptic', fontsize=14, fontweight='bold')
    ax.legend(fontsize=11)
    ax.grid(True, alpha=0.3)
    
    plt.tight_layout()
    plt.savefig('docs/delta_v_hohmann_vs_bielliptic.png', dpi=300, bbox_inches='tight')
    print("  ✓ Guardado: docs/delta_v_hohmann_vs_bielliptic.png")
    
    return fig


def plot_plane_change_cost():
    """
    Gráfica: Costo de cambio de plano vs ángulo para diferentes altitudes.
    """
    print("Generando: Plane change cost...")
    
    # Ángulos
    angles = np.linspace(0, 90, 100)
    
    # Altitudes
    altitudes = {
        'LEO (400 km)': 6771e3,
        'MEO (10,000 km)': 6371e3 + 10000e3,
        'GEO (35,786 km)': 6371e3 + 35786e3
    }
    
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6))
    
    # Panel 1: ΔV absoluto
    for name, r in altitudes.items():
        v = circular_velocity(r)
        delta_vs = [simple_plane_change(v, angle) for angle in angles]
        ax1.plot(angles, np.array(delta_vs)/1000, linewidth=2, label=name)
    
    ax1.set_xlabel('Cambio de inclinación (grados)', fontsize=12)
    ax1.set_ylabel('ΔV requerido (km/s)', fontsize=12)
    ax1.set_title('Costo de Cambio de Plano', fontsize=14, fontweight='bold')
    ax1.legend(fontsize=10)
    ax1.grid(True, alpha=0.3)
    
    # Panel 2: ΔV como fracción de v_circular
    for name, r in altitudes.items():
        v = circular_velocity(r)
        delta_vs = [simple_plane_change(v, angle) for angle in angles]
        fractions = np.array(delta_vs) / v
        ax2.plot(angles, fractions, linewidth=2, label=name)
    
    ax2.set_xlabel('Cambio de inclinación (grados)', fontsize=12)
    ax2.set_ylabel('ΔV / v_circular', fontsize=12)
    ax2.set_title('Costo Relativo (fracción de velocidad orbital)', fontsize=14, fontweight='bold')
    ax2.legend(fontsize=10)
    ax2.grid(True, alpha=0.3)
    
    plt.tight_layout()
    plt.savefig('docs/delta_v_plane_change.png', dpi=300, bbox_inches='tight')
    print("  ✓ Guardado: docs/delta_v_plane_change.png")
    
    return fig


def plot_combined_maneuver_strategies():
    """
    Gráfica: Comparación de estrategias para maniobra combinada.
    """
    print("Generando: Combined maneuver strategies...")
    
    # LEO → GEO con diferentes cambios de inclinación
    r_leo = 6771e3
    r_geo = 6371e3 + 35786e3
    
    inclinations = np.linspace(0, 60, 25)
    
    # Calcular para cada estrategia
    hohmann_only = []
    plane_at_r1 = []
    plane_at_r2 = []
    combined_at_r2 = []
    
    for delta_i in inclinations:
        if delta_i < 0.1:
            # Sin cambio de plano
            h = hohmann_transfer(r_leo, r_geo)
            hohmann_only.append(h['delta_v_total'])
            plane_at_r1.append(h['delta_v_total'])
            plane_at_r2.append(h['delta_v_total'])
            combined_at_r2.append(h['delta_v_total'])
        else:
            result = combined_plane_change(r_leo, r_geo, delta_i)
            hohmann_only.append(result['hohmann_only'])
            plane_at_r1.append(result['strategy_plane_at_r1'])
            plane_at_r2.append(result['strategy_plane_at_r2'])
            combined_at_r2.append(result['strategy_combined_at_r2'])
    
    # Crear figura
    fig, ax = plt.subplots(figsize=(10, 7))
    
    ax.plot(inclinations, np.array(hohmann_only)/1000, 'k--', linewidth=2, 
            label='Hohmann solo (sin cambio plano)', alpha=0.5)
    ax.plot(inclinations, np.array(plane_at_r1)/1000, 'r-', linewidth=2, 
            label='Cambio plano en r₁ (LEO)', alpha=0.7)
    ax.plot(inclinations, np.array(plane_at_r2)/1000, 'orange', linewidth=2, 
            label='Cambio plano en r₂ (GEO)', alpha=0.7)
    ax.plot(inclinations, np.array(combined_at_r2)/1000, 'g-', linewidth=3, 
            label='Combinado en r₂ (ÓPTIMO)')
    
    ax.set_xlabel('Cambio de inclinación (grados)', fontsize=12)
    ax.set_ylabel('ΔV total (km/s)', fontsize=12)
    ax.set_title('LEO → GEO: Estrategias para Maniobra Combinada', 
                 fontsize=14, fontweight='bold')
    ax.legend(fontsize=10, loc='upper left')
    ax.grid(True, alpha=0.3)
    
    # Anotación
    ax.text(30, 7.5, 'Cambiar plano en LEO\nes MUY costoso', 
            bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.5),
            fontsize=10, ha='center')
    
    plt.tight_layout()
    plt.savefig('docs/delta_v_combined_strategies.png', dpi=300, bbox_inches='tight')
    print("  ✓ Guardado: docs/delta_v_combined_strategies.png")
    
    return fig


def plot_phasing_tradeoff():
    """
    Gráfica: Trade-off entre ΔV y tiempo en maniobras de phasing.
    """
    print("Generando: Phasing trade-off...")
    
    r_leo = 6771e3
    phase_angles = [30, 60, 90, 120, 180]
    
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6))
    
    # Panel 1: ΔV vs n_orbits para diferentes ángulos
    for phase in phase_angles:
        n_range = range(1, 21)
        delta_vs = []
        
        for n in n_range:
            try:
                result = phasing_orbit(r_leo, phase, n_orbits=n)
                delta_vs.append(result['delta_v_total'])
            except:
                delta_vs.append(np.nan)
        
        ax1.plot(n_range, np.array(delta_vs), marker='o', linewidth=2, 
                label=f'Δφ = {phase}°')
    
    ax1.set_xlabel('Número de órbitas', fontsize=12)
    ax1.set_ylabel('ΔV total (m/s)', fontsize=12)
    ax1.set_title('Trade-off: Más órbitas = Menor ΔV', fontsize=14, fontweight='bold')
    ax1.legend(fontsize=10)
    ax1.grid(True, alpha=0.3)
    ax1.set_yscale('log')
    
    # Panel 2: Tiempo vs ΔV para 90° de fase
    phase_test = 90
    n_range = range(1, 31)
    delta_vs = []
    times = []
    
    for n in n_range:
        try:
            result = phasing_orbit(r_leo, phase_test, n_orbits=n)
            delta_vs.append(result['delta_v_total'])
            times.append(result['phasing_time'] / 3600)  # horas
        except:
            continue
    
    # Scatter plot con colormap
    scatter = ax2.scatter(times, delta_vs, c=list(range(len(times))), 
                         cmap='viridis', s=100, edgecolors='black', linewidth=1.5)
    
    # Añadir números de órbitas
    for i, (t, dv) in enumerate(zip(times[::3], delta_vs[::3])):
        ax2.annotate(f'n={i*3+1}', (t, dv), fontsize=8, 
                    xytext=(5, 5), textcoords='offset points')
    
    ax2.set_xlabel('Tiempo (horas)', fontsize=12)
    ax2.set_ylabel('ΔV (m/s)', fontsize=12)
    ax2.set_title(f'Corrección de {phase_test}° en LEO', fontsize=14, fontweight='bold')
    ax2.grid(True, alpha=0.3)
    
    # Colorbar
    cbar = plt.colorbar(scatter, ax=ax2)
    cbar.set_label('Número de órbitas', fontsize=10)
    
    plt.tight_layout()
    plt.savefig('docs/delta_v_phasing_tradeoff.png', dpi=300, bbox_inches='tight')
    print("  ✓ Guardado: docs/delta_v_phasing_tradeoff.png")
    
    return fig


def plot_mission_comparison():
    """
    Gráfica: Comparación de misiones comunes.
    """
    print("Generando: Mission comparison...")
    
    # Misiones a comparar
    missions = {
        'LEO → ISS\n(resupply)': {
            'r1': ORBITS_EARTH['LEO_typical']['radius_m'],
            'r2': ORBITS_EARTH['ISS']['radius_m'],
            'delta_i': 0
        },
        'LEO → Starlink\n(deployment)': {
            'r1': ORBITS_EARTH['LEO_low']['radius_m'],
            'r2': ORBITS_EARTH['Starlink']['radius_m'],
            'delta_i': 0
        },
        'LEO → GPS\n(MEO)': {
            'r1': ORBITS_EARTH['LEO_typical']['radius_m'],
            'r2': ORBITS_EARTH['MEO_GPS']['radius_m'],
            'delta_i': 0
        },
        'LEO → GEO\n(comms)': {
            'r1': ORBITS_EARTH['LEO_typical']['radius_m'],
            'r2': ORBITS_EARTH['GEO']['radius_m'],
            'delta_i': 0
        },
        'Cape → GEO\n(28.5° change)': {
            'r1': ORBITS_EARTH['LEO_typical']['radius_m'],
            'r2': ORBITS_EARTH['GEO']['radius_m'],
            'delta_i': 28.5
        },
        'ISS → Polar\n(51.6° change)': {
            'r1': ORBITS_EARTH['ISS']['radius_m'],
            'r2': ORBITS_EARTH['Polar_SSO']['radius_m'],
            'delta_i': 51.6
        }
    }
    
    # Calcular ΔV para cada misión
    mission_names = []
    delta_vs = []
    times = []
    
    for name, params in missions.items():
        mission_names.append(name)
        
        if params['delta_i'] > 0.1:
            result = combined_plane_change(params['r1'], params['r2'], params['delta_i'])
            delta_vs.append(result['optimal_delta_v'])
            # Tiempo aproximado (no disponible en combined)
            h = hohmann_transfer(params['r1'], params['r2'])
            times.append(h['transfer_time'] / 3600)
        else:
            result = hohmann_transfer(params['r1'], params['r2'])
            delta_vs.append(result['delta_v_total'])
            times.append(result['transfer_time'] / 3600)
    
    # Crear figura con dos subplots
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 7))
    
    # Panel 1: ΔV
    colors = plt.cm.viridis(np.linspace(0, 1, len(mission_names)))
    bars1 = ax1.barh(mission_names, np.array(delta_vs)/1000, color=colors, edgecolor='black')
    ax1.set_xlabel('ΔV total (km/s)', fontsize=12)
    ax1.set_title('Comparación de ΔV por Misión', fontsize=14, fontweight='bold')
    ax1.grid(True, alpha=0.3, axis='x')
    
    # Añadir valores
    for bar, dv in zip(bars1, delta_vs):
        width = bar.get_width()
        ax1.text(width + 0.1, bar.get_y() + bar.get_height()/2, 
                f'{dv/1000:.2f}', ha='left', va='center', fontsize=9)
    
    # Panel 2: Tiempo
    bars2 = ax2.barh(mission_names, times, color=colors, edgecolor='black')
    ax2.set_xlabel('Tiempo de transferencia (horas)', fontsize=12)
    ax2.set_title('Tiempo de Transferencia', fontsize=14, fontweight='bold')
    ax2.grid(True, alpha=0.3, axis='x')
    
    # Añadir valores
    for bar, t in zip(bars2, times):
        width = bar.get_width()
        label = f'{t:.1f}h' if t < 24 else f'{t/24:.1f}d'
        ax2.text(width + 0.5, bar.get_y() + bar.get_height()/2, 
                label, ha='left', va='center', fontsize=9)
    
    plt.tight_layout()
    plt.savefig('docs/delta_v_mission_comparison.png', dpi=300, bbox_inches='tight')
    print("  ✓ Guardado: docs/delta_v_mission_comparison.png")
    
    return fig


def plot_propellant_mass_fraction():
    """
    Gráfica: Fracción de masa de propelente vs ΔV para diferentes Isp.
    """
    print("Generando: Propellant mass fraction...")
    
    # Rango de ΔV
    delta_vs = np.linspace(0, 12000, 200)  # m/s
    
    # Diferentes Isp
    isps = {
        'Monoprop (Isp=220s)': 220,
        'Químico bajo (Isp=300s)': 300,
        'Químico alto (Isp=450s)': 450,
        'Hall thruster (Isp=1500s)': 1500,
        'Ion engine (Isp=3000s)': 3000
    }
    
    fig, ax = plt.subplots(figsize=(10, 7))
    
    for name, isp in isps.items():
        mass_ratios = np.exp(delta_vs / (isp * 9.81))
        propellant_fractions = (mass_ratios - 1) / mass_ratios
        
        ax.plot(delta_vs/1000, propellant_fractions * 100, linewidth=2.5, label=name)
    
    ax.set_xlabel('ΔV total (km/s)', fontsize=12)
    ax.set_ylabel('Propelente requerido (% masa total)', fontsize=12)
    ax.set_title('Ecuación de Tsiolkovsky: Propelente vs ΔV', 
                 fontsize=14, fontweight='bold')
    ax.legend(fontsize=10, loc='upper left')
    ax.grid(True, alpha=0.3)
    
    # Líneas de referencia
    ax.axhline(90, color='red', linestyle='--', alpha=0.5)
    ax.text(11, 92, '90% (límite práctico)', fontsize=9, color='red')
    
    # Anotaciones de misiones
    ax.axvline(3.9, color='gray', linestyle=':', alpha=0.5)
    ax.text(4.0, 5, 'LEO→GEO', fontsize=9, rotation=90, va='bottom')
    
    ax.axvline(11.0, color='gray', linestyle=':', alpha=0.5)
    ax.text(11.1, 5, 'Dawn\n(asteroides)', fontsize=9, rotation=90, va='bottom')
    
    plt.tight_layout()
    plt.savefig('docs/delta_v_propellant_fraction.png', dpi=300, bbox_inches='tight')
    print("  ✓ Guardado: docs/delta_v_propellant_fraction.png")
    
    return fig


def generate_all_plots():
    """Genera todas las visualizaciones."""
    print("\n" + "="*70)
    print(" "*15 + "DELTA-V VISUALIZATION TOOL")
    print("="*70 + "\n")
    
    # Crear directorio si no existe
    os.makedirs('docs', exist_ok=True)
    
    # Generar cada gráfica
    figs = []
    
    figs.append(plot_hohmann_vs_bielliptic())
    figs.append(plot_plane_change_cost())
    figs.append(plot_combined_maneuver_strategies())
    figs.append(plot_phasing_tradeoff())
    figs.append(plot_mission_comparison())
    figs.append(plot_propellant_mass_fraction())
    
    print("\n" + "="*70)
    print("✓ Todas las visualizaciones generadas")
    print("  Total: 6 gráficas en docs/")
    print("="*70 + "\n")
    
    return figs


if __name__ == "__main__":
    figs = generate_all_plots()
    
    # Mostrar todas
    show = input("¿Mostrar gráficas? (s/n): ").lower()
    if show == 's':
        plt.show()