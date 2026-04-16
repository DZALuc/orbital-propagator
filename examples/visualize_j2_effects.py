"""
Visualización de Efectos de Perturbación J2

Compara evolución de elementos orbitales con y sin J2.
Demuestra efectos de precesión nodal y rotación de línea de ápsides.
"""

import numpy as np
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from src.propagator import OrbitalPropagator, orbital_period
from src.orbital_elements import keplerian_to_cartesian
from src.visualization import plot_orbital_elements_evolution
from astropy import constants as const

def main():
    print("=" * 70)
    print("VISUALIZACIÓN DE EFECTOS J2 EN ELEMENTOS ORBITALES")
    print("=" * 70)
    
    # Parámetros
    R_earth = 6378137.0  # Radio ecuatorial (para J2)
    mu = const.GM_earth.value
    J2 = 1.08263e-3
    
    # Configurar órbita usando elementos Keplerianos
    # Órbita LEO elíptica inclinada (para ver todos los efectos J2)
    a = 7171e3          # Semieje mayor: 800 km de altitud nominal
    e = 0.05            # Excentricidad pequeña (órbita casi circular)
    i = np.radians(65)  # Inclinación 65° (para ver precesión nodal fuerte)
    RAAN = np.radians(45)  # RAAN inicial 45° (para ver cambios)
    omega = np.radians(30)  # Argumento del perigeo 30°
    nu = np.radians(0)   # Anomalía verdadera: comenzar en perigeo
    
    T = orbital_period(a, mu)
    
    print(f"\nConfiguración de Órbita:")
    print(f"  Semieje mayor: {a/1e3:.1f} km")
    print(f"  Excentricidad: {e:.3f}")
    print(f"  Inclinación: {np.degrees(i):.1f}°")
    print(f"  RAAN inicial: {np.degrees(RAAN):.1f}°")
    print(f"  Arg. perigeo: {np.degrees(omega):.1f}°")
    print(f"  Periodo: {T/60:.2f} min")
    
    # Convertir a estado Cartesiano
    r0, v0 = keplerian_to_cartesian(a, e, i, RAAN, omega, nu, mu)
    
    print(f"\nEstado Cartesiano Inicial:")
    print(f"  Posición: [{r0[0]/1e3:.3f}, {r0[1]/1e3:.3f}, {r0[2]/1e3:.3f}] km")
    print(f"  Velocidad: [{v0[0]/1e3:.6f}, {v0[1]/1e3:.6f}, {v0[2]/1e3:.6f}] km/s")
    
    # Propagar por 50 órbitas (~3 días) para ver efectos acumulativos
    n_orbits = 50
    t_span = (0, T * n_orbits)
    
    print(f"\nPropagando {n_orbits} órbitas ({T*n_orbits/3600:.1f} horas = {T*n_orbits/86400:.2f} días)...")
    print("Esto tomará ~1-2 minutos...")
    
    # Crear propagador
    prop = OrbitalPropagator(mu=mu)
    
    # Propagación SIN J2
    print("\n[1/2] Propagando sin J2 (modelo ideal de dos cuerpos)...")
    sol_no_j2 = prop.propagate(r0, v0, t_span, dt=300.0)  # dt=5 min
    
    # Propagación CON J2
    print("[2/2] Propagando con J2 (modelo realista)...")
    sol_j2 = prop.propagate_j2(r0, v0, t_span, dt=300.0, J2=J2, R_earth=R_earth)
    
    if sol_no_j2['success'] and sol_j2['success']:
        print("\n✓ Ambas propagaciones exitosas!")
        print(f"  Puntos de datos: {len(sol_no_j2['t'])}")
        
        # Crear directorio docs si no existe
        docs_dir = os.path.join(os.path.dirname(__file__), '..', 'docs')
        os.makedirs(docs_dir, exist_ok=True)
        
        # Generar visualización
        print("\nGenerando gráficas de elementos orbitales...")
        print("(Calculando elementos Keplerianos en cada punto... ~30-60 seg)")
        
        plot_orbital_elements_evolution(
            sol_no_j2,
            mu=mu,
            solution_j2=sol_j2,
            title=f"Efectos de J2 en Elementos Orbitales - Órbita LEO (a={a/1e3:.0f} km, e={e:.2f}, i={np.degrees(i):.0f}°)",
            save_path=os.path.join(docs_dir, 'j2_orbital_elements_evolution.png'),
            show=True
        )
        
        print("\n" + "=" * 70)
        print("INTERPRETACIÓN DE RESULTADOS:")
        print("=" * 70)
        
        # Calcular tasas de cambio
        from src.orbital_elements import cartesian_to_keplerian
        
        elem_j2_0 = cartesian_to_keplerian(sol_j2['r'][0], sol_j2['v'][0], mu)
        elem_j2_f = cartesian_to_keplerian(sol_j2['r'][-1], sol_j2['v'][-1], mu)
        
        delta_RAAN = np.degrees(elem_j2_f['RAAN'] - elem_j2_0['RAAN'])
        delta_omega = np.degrees(elem_j2_f['omega'] - elem_j2_0['omega'])
        
        RAAN_rate = delta_RAAN / (t_span[1] / 86400)  # grados/día
        omega_rate = delta_omega / (t_span[1] / 86400)  # grados/día
        
        print("\nEfectos Cuantificados de J2:")
        print(f"\n1. Precesión Nodal (RAAN):")
        print(f"   - Cambio en {n_orbits} órbitas: {delta_RAAN:.3f}°")
        print(f"   - Tasa de precesión: {RAAN_rate:.3f} °/día")
        if RAAN_rate < 0:
            print(f"   - Tipo: REGRESIVA (plano orbital rota hacia oeste)")
        else:
            print(f"   - Tipo: PROGRESIVA (plano orbital rota hacia este)")
        
        print(f"\n2. Rotación de Ápsides (ω):")
        print(f"   - Cambio en {n_orbits} órbitas: {delta_omega:.3f}°")
        print(f"   - Tasa de rotación: {omega_rate:.3f} °/día")
        if omega_rate > 0:
            print(f"   - Tipo: PROGRESIVA (línea de ápsides rota)")
        
        print(f"\n3. Elementos Constantes (verificación):")
        print(f"   - Semieje mayor: {elem_j2_0['a']/1e3:.3f} km → {elem_j2_f['a']/1e3:.3f} km")
        print(f"     Cambio: {abs(elem_j2_f['a'] - elem_j2_0['a']):.2f} m (ruido numérico)")
        print(f"   - Excentricidad: {elem_j2_0['e']:.6f} → {elem_j2_f['e']:.6f}")
        print(f"     Cambio: {abs(elem_j2_f['e'] - elem_j2_0['e']):.2e}")
        print(f"   - Inclinación: {np.degrees(elem_j2_0['i']):.4f}° → {np.degrees(elem_j2_f['i']):.4f}°")
        
        print("\nFÍSICA DETRÁS DE J2:")
        print("- Achatamiento terrestre → masa concentrada en ecuador")
        print("- Más gravedad en ecuador → perturba órbitas inclinadas")
        print("- Efecto proporcional a: (R_earth/a)² × cos(i)")
        print("- Para i=63.4° (Molniya): precesión nodal ≈ 0 (órbita crítica)")
        
        print("\nAPLICACIONES:")
        print("✓ Órbitas heliosíncronas: RAAN precede ~1°/día (sigue al Sol)")
        print("✓ GPS/GLONASS: compensa J2 en predicción de efemérides")
        print("✓ Satélites espía: usan J2 para optimizar cobertura")
        
        print("\n" + "=" * 70)
        print("✓ Visualización completa!")
        print(f"✓ Archivo guardado: docs/j2_orbital_elements_evolution.png")
        print("=" * 70)
        
    else:
        print("\n✗ Error en propagación!")
        if not sol_no_j2['success']:
            print(f"  Sin J2: {sol_no_j2['message']}")
        if not sol_j2['success']:
            print(f"  Con J2: {sol_j2['message']}")

if __name__ == "__main__":
    main()