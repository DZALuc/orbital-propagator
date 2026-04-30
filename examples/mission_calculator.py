"""
Interactive Mission ΔV Calculator

Calculadora interactiva para planear maniobras orbitales.

Author: Damián Zúñiga Avelar
Date: Abril 2026
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from src.delta_v import *
import numpy as np

from src.mission_database import ORBITS_EARTH, MISSIONS, get_orbit






def print_header():
    """Encabezado del programa."""
    print("\n" + "="*70)
    print(" "*15 + "MISSION ΔV CALCULATOR")
    print(" "*15 + "Proyecto 3 - Orbital Propagator")
    print("="*70)


def print_menu():
    """Menú principal."""
    print("\nMENÚ PRINCIPAL:")
    print("  [1] Hohmann Transfer")
    print("  [2] Bi-elliptic Transfer")
    print("  [3] Plane Change")
    print("  [4] Combined Transfer + Plane Change")
    print("  [5] Escape Velocity")
    print("  [6] Interplanetary (Earth → Mars)")
    print("  [7] Rendezvous Planning")
    print("  [8] Compare All Strategies")
    print("  [9] Common Missions (Database)") 
    print("  [0] Salir")
    print()


def get_altitude(prompt):
    """Obtener altitud del usuario (en km) y convertir a radio (m)."""
    while True:
        try:
            alt_km = float(input(prompt))
            if alt_km < 0:
                print("  ⚠️  Altitud debe ser positiva")
                continue
            return R_earth + alt_km * 1e3
        except ValueError:
            print("  ⚠️  Por favor ingresa un número válido")


def get_angle(prompt):
    """Obtener ángulo del usuario (grados)."""
    while True:
        try:
            angle = float(input(prompt))
            if angle < 0 or angle > 360:
                print("  ⚠️  Ángulo debe estar entre 0° y 360°")
                continue
            return angle
        except ValueError:
            print("  ⚠️  Por favor ingresa un número válido")


def option_hohmann():
    """Opción 1: Hohmann Transfer."""
    print("\n" + "─"*70)
    print("HOHMANN TRANSFER")
    print("─"*70)
    
    r1 = get_altitude("Altitud inicial (km): ")
    r2 = get_altitude("Altitud final (km): ")
    
    result = hohmann_transfer(r1, r2)
    
    print("\nRESULTADOS:")
    print(f"  ΔV₁ (primer impulso):   {result['delta_v_1']:,.1f} m/s")
    print(f"  ΔV₂ (segundo impulso):  {result['delta_v_2']:,.1f} m/s")
    print(f"  ΔV total:               {result['delta_v_total']:,.1f} m/s")
    print(f"  Tiempo de transferencia: {result['transfer_time']/3600:.2f} horas")
    
    # Propelente estimado
    print("\nPROPELENTE NECESARIO (estimado):")
    for isp in [300, 450, 1500]:  # Químico bajo, químico alto, eléctrico
        mass_ratio = np.exp(result['delta_v_total'] / (isp * 9.81))
        propellant_fraction = (mass_ratio - 1) / mass_ratio
        
        tipo = "Químico bajo" if isp == 300 else ("Químico alto" if isp == 450 else "Eléctrico")
        print(f"  {tipo:15s} (Isp={isp:4d}s): {propellant_fraction*100:.1f}% masa total")


def option_bielliptic():
    """Opción 2: Bi-elliptic Transfer."""
    print("\n" + "─"*70)
    print("BI-ELLIPTIC TRANSFER")
    print("─"*70)
    
    r1 = get_altitude("Altitud inicial (km): ")
    r2 = get_altitude("Altitud final (km): ")
    
    # Calcular ratio
    ratio = r2 / r1
    
    print(f"\nRatio r2/r1 = {ratio:.2f}")
    
    if ratio < 11.94:
        print("⚠️  Bi-elliptic probablemente NO es más eficiente que Hohmann")
        print("   (Ratio < 11.94)")
    
    proceed = input("\n¿Continuar con análisis? (s/n): ").lower()
    
    if proceed != 's':
        return
    
    # Comparar
    comparison = compare_hohmann_bielliptic(r1, r2)
    
    print("\nCOMPARACIÓN:")
    print(f"\n  Hohmann:")
    print(f"    ΔV total: {comparison['hohmann']['delta_v_total']:,.1f} m/s")
    print(f"    Tiempo:   {comparison['hohmann']['transfer_time']/3600:.1f} horas")
    
    if comparison['bielliptic']:
        print(f"\n  Bi-elliptic (óptima):")
        print(f"    r_intermediate: {comparison['bielliptic']['r_intermediate_optimal']/1e3:,.1f} km")
        print(f"    ΔV total: {comparison['bielliptic']['delta_v_total']:,.1f} m/s")
        print(f"    Tiempo:   {comparison['bielliptic']['transfer_time']/3600:.1f} horas")
        
        print(f"\n  → RECOMENDACIÓN: {comparison['recommendation']}")
        
        if comparison['recommendation'] == 'Bi-elliptic':
            print(f"  → AHORRO: {comparison['savings_m_s']:.1f} m/s ({comparison['savings_percent']:.1f}%)")
            print(f"  → Pero toma {comparison['bielliptic']['transfer_time']/86400:.1f} días más")


def option_plane_change():
    """Opción 3: Plane Change."""
    print("\n" + "─"*70)
    print("PLANE CHANGE")
    print("─"*70)
    
    r = get_altitude("Altitud de la órbita (km): ")
    delta_i = get_angle("Cambio de inclinación deseado (grados): ")
    
    v = circular_velocity(r)
    dv = simple_plane_change(v, delta_i)
    
    print("\nRESULTADOS:")
    print(f"  Velocidad orbital:     {v:,.1f} m/s")
    print(f"  ΔV requerido:          {dv:,.1f} m/s")
    print(f"  Fracción de v_orbital: {dv/v*100:.1f}%")
    
    # Advertencia
    if delta_i > 30:
        print("\n  ⚠️  ADVERTENCIA: Cambio de plano muy costoso!")
        print("     Considera lanzar a inclinación más cercana.")


def option_combined():
    """Opción 4: Combined Transfer + Plane Change."""
    print("\n" + "─"*70)
    print("COMBINED TRANSFER + PLANE CHANGE")
    print("─"*70)
    
    r1 = get_altitude("Altitud inicial (km): ")
    r2 = get_altitude("Altitud final (km): ")
    delta_i = get_angle("Cambio de inclinación (grados): ")
    
    result = combined_plane_change(r1, r2, delta_i)
    
    print("\nRESULTADOS:")
    print(f"  Hohmann solo:          {result['hohmann_only']:,.1f} m/s")
    print(f"  Plane change solo:     {result['plane_change_only']:,.1f} m/s")
    
    print("\n  ESTRATEGIAS:")
    print(f"    Plano en r1:         {result['strategy_plane_at_r1']:,.1f} m/s")
    print(f"    Plano en r2:         {result['strategy_plane_at_r2']:,.1f} m/s")
    print(f"    Combinado en r2:     {result['strategy_combined_at_r2']:,.1f} m/s ← ÓPTIMO")
    
    print(f"\n  → ΔV TOTAL ÓPTIMO:     {result['optimal_delta_v']:,.1f} m/s")
    print(f"  → Estrategia:          {result['optimal_strategy']}")


def option_escape():
    """Opción 5: Escape Velocity."""
    print("\n" + "─"*70)
    print("ESCAPE VELOCITY")
    print("─"*70)
    
    r = get_altitude("Altitud de órbita de partida (km): ")
    
    result = delta_v_to_escape(r)
    
    print("\nRESULTADOS:")
    print(f"  Velocidad circular:    {result['v_circular']:,.1f} m/s")
    print(f"  Velocidad de escape:   {result['v_escape']:,.1f} m/s")
    print(f"  ΔV necesario:          {result['delta_v']:,.1f} m/s")
    
    # Comparación
    print("\n  Nota: v_escape = √2 × v_circular = 1.414 × v_circular")


def option_interplanetary():
    """Opción 6: Earth → Mars."""
    print("\n" + "─"*70)
    print("INTERPLANETARY: EARTH → MARS")
    print("─"*70)
    
    r_earth = 1.496e11   # 1 AU
    r_mars = 2.279e11    # 1.524 AU
    
    result = interplanetary_hohmann(r_earth, r_mars)
    
    print("\nRESULTADOS:")
    print(f"  ΔV heliocéntrico salida:  {result['delta_v_departure']:,.1f} m/s")
    print(f"  ΔV heliocéntrico llegada: {result['delta_v_arrival']:,.1f} m/s")
    print(f"  v∞ salida de Tierra:      {result['v_infinity_departure']:,.1f} m/s")
    print(f"  v∞ llegada a Marte:       {result['v_infinity_arrival']:,.1f} m/s")
    print(f"  Tiempo de transferencia:  {result['transfer_time_days']:.1f} días")
    
    # ΔV desde LEO
    r_leo = R_earth + 400e3
    dv_from_leo = earth_departure_delta_v(result['v_infinity_departure'], r_leo)
    
    print(f"\n  ΔV desde LEO (400 km):    {dv_from_leo:,.1f} m/s")


def option_rendezvous():
    """Opción 7: Rendezvous Planning."""
    print("\n" + "─"*70)
    print("RENDEZVOUS PLANNING")
    print("─"*70)
    
    r1 = get_altitude("Altitud inicial (km): ")
    r2 = get_altitude("Altitud del target (km): ")
    phase = get_angle("Diferencia de fase (grados, 0-360): ")
    
    time_available = float(input("Tiempo disponible (horas, default=24): ") or "24")
    
    result = rendezvous_realistic(r1, r2, phase, time_available_hours=time_available)
    
    if not result['feasible']:
        print(f"\n  ❌ NO FACTIBLE: {result['reason']}")
        print(f"     Tiempo mínimo necesario: {result['time_needed']:.1f} horas")
        return
    
    print("\nRESULTADOS:")
    print(f"  PASO 1 - Hohmann Transfer:")
    print(f"    ΔV:     {result['hohmann']['delta_v_total']:,.1f} m/s")
    print(f"    Tiempo: {result['hohmann']['transfer_time']/60:.1f} min")
    
    print(f"\n  PASO 2 - Phasing:")
    print(f"    ΔV:     {result['phasing']['delta_v_total']:,.1f} m/s")
    print(f"    Tiempo: {result['phasing']['phasing_time']/3600:.1f} horas")
    print(f"    Órbitas: {result['phasing']['n_orbits_phasing']:.1f}")
    
    print(f"\n  TOTAL:")
    print(f"    ΔV:     {result['delta_v_total']:,.1f} m/s")
    print(f"    Tiempo: {result['time_total_hours']:.1f} horas")


def option_compare():
    """Opción 8: Compare all strategies."""
    print("\n" + "─"*70)
    print("COMPARE ALL STRATEGIES")
    print("─"*70)
    
    r1 = get_altitude("Altitud inicial (km): ")
    r2 = get_altitude("Altitud final (km): ")
    
    # Hohmann
    hohmann = hohmann_transfer(r1, r2)
    
    # Bi-elliptic (si aplica)
    ratio = r2 / r1
    if ratio > 11.94:
        try:
            bielliptic = find_optimal_bielliptic(r1, r2)
        except:
            bielliptic = None
    else:
        bielliptic = None
    
    # Escape (para comparar)
    escape = delta_v_to_escape(r2)
    
    print("\nCOMPARACIÓN:")
    print(f"\n  Ratio r2/r1: {ratio:.2f}")
    print("\n  Estrategia                ΔV (m/s)    Tiempo")
    print("  " + "─"*55)
    print(f"  Hohmann                   {hohmann['delta_v_total']:7,.1f}     {hohmann['transfer_time']/3600:5.1f} h")
    
    if bielliptic:
        print(f"  Bi-elliptic (óptima)      {bielliptic['delta_v_total']:7,.1f}     {bielliptic['transfer_time']/86400:5.1f} días")
    
    print(f"\n  Para referencia:")
    print(f"  Escape desde r2           {escape['delta_v']:7,.1f}     instantáneo")



def option_common_missions():
    """Opción 9: Misiones comunes desde base de datos."""
    print("\n" + "─"*70)
    print("COMMON MISSIONS (DATABASE)")
    print("─"*70)
    
    print("\nMISIONES DISPONIBLES:")
    missions_list = [
        ('1', 'LEO_typical', 'GEO', 'LEO → GEO (satélite comunicaciones)'),
        ('2', 'LEO_typical', 'ISS', 'LEO → ISS (resupply mission)'),
        ('3', 'ISS', 'Polar_SSO', 'ISS → Polar SSO (cambio radical)'),
        ('4', 'Starlink', 'MEO_GPS', 'Starlink → GPS altitude'),
    ]
    
    for num, _, _, desc in missions_list:
        print(f"  [{num}] {desc}")
    
    choice = input("\nSelecciona misión: ").strip()
    
    mission_map = {m[0]: (m[1], m[2]) for m in missions_list}
    
    if choice not in mission_map:
        print("  ⚠️  Opción no válida")
        return
    
    orbit1_key, orbit2_key = mission_map[choice]
    orbit1 = get_orbit(orbit1_key)
    orbit2 = get_orbit(orbit2_key)
    
    r1 = orbit1['radius_m']
    r2 = orbit2['radius_m']
    
    print(f"\n  Órbita inicial: {orbit1['name']} ({orbit1['altitude_km']} km)")
    print(f"  Órbita final:   {orbit2['name']} ({orbit2['altitude_km']} km)")
    
    # Hohmann
    result = hohmann_transfer(r1, r2)
    
    print("\n  HOHMANN TRANSFER:")
    print(f"    ΔV total: {result['delta_v_total']:,.1f} m/s")
    print(f"    Tiempo:   {result['transfer_time']/3600:.2f} horas")
    
    # Si hay cambio de inclinación
    i1 = orbit1.get('inclination_deg', 0)
    i2 = orbit2.get('inclination_deg', 0)
    delta_i = abs(i2 - i1)
    
    if delta_i > 0.1:
        combined = combined_plane_change(r1, r2, delta_i)
        print(f"\n  CON CAMBIO DE INCLINACIÓN ({delta_i:.1f}°):")
        print(f"    ΔV total: {combined['optimal_delta_v']:,.1f} m/s")
        print(f"    Penalización: +{combined['penalty_vs_hohmann']:,.1f} m/s")





def main():
    """Loop principal."""
    print_header()
    
    while True:
        print_menu()
        
        choice = input("Selecciona una opción: ").strip()
        
        if choice == '0':
            print("\n¡Hasta luego! 🚀\n")
            break
        elif choice == '1':
            option_hohmann()
        elif choice == '2':
            option_bielliptic()
        elif choice == '3':
            option_plane_change()
        elif choice == '4':
            option_combined()
        elif choice == '5':
            option_escape()
        elif choice == '6':
            option_interplanetary()
        elif choice == '7':
            option_rendezvous()
        elif choice == '8':
            option_compare()
        elif choice == '9':
            option_common_missions() 
        else:
            print("\n  ⚠️  Opción no válida")
        
        input("\nPresiona ENTER para continuar...")





if __name__ == "__main__":
    main()