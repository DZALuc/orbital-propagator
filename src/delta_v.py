"""
Mission ΔV Calculator

Módulo para calcular ΔV de maniobras orbitales comunes.

Funciones principales:
- hohmann_transfer: Transferencia Hohmann circular-circular
- bielliptic_transfer: Transferencia bi-elíptica
- plane_change: Cambio de plano orbital
- combined_maneuver: Cambio combinado órbita + plano
- escape_velocity: Velocidad de escape planetaria

Author: Damián Zúñiga Avelar
Project: Orbital Propagator - Mission ΔV Calculator
Date: Abril 2026
Version: 3.0.0
"""

import numpy as np
from astropy import constants as const

# Constantes
GM_earth = const.GM_earth.value  # m^3/s^2
R_earth = 6371000  # m


def circular_velocity(r, mu=GM_earth):
    """
    Velocidad orbital circular.
    
    Parameters:
    -----------
    r : float
        Radio orbital (m)
    mu : float, optional
        Parámetro gravitacional GM (m^3/s^2)
    
    Returns:
    --------
    v : float
        Velocidad circular (m/s)
    """
    return np.sqrt(mu / r)


def hohmann_transfer(r1, r2, mu=GM_earth):
    """
    Calcula ΔV para transferencia Hohmann entre dos órbitas circulares.
    
    La transferencia Hohmann es la maniobra de dos impulsos más eficiente
    para transferir entre órbitas circulares coplanares.
    
    Parameters:
    -----------
    r1 : float
        Radio de órbita inicial (m)
    r2 : float
        Radio de órbita final (m)
    mu : float, optional
        Parámetro gravitacional GM (m^3/s^2)
    
    Returns:
    --------
    result : dict
        - 'delta_v_1': ΔV del primer impulso en periapsis (m/s)
        - 'delta_v_2': ΔV del segundo impulso en apoapsis (m/s)
        - 'delta_v_total': ΔV total requerido (m/s)
        - 'transfer_time': Tiempo de transferencia (s)
        - 'semi_major': Semieje mayor de la órbita de transferencia (m)
    
    Examples:
    ---------
    >>> # LEO (400 km) a GEO (35,786 km)
    >>> r_leo = 6371e3 + 400e3
    >>> r_geo = 6371e3 + 35786e3
    >>> result = hohmann_transfer(r_leo, r_geo)
    >>> print(f"ΔV total: {result['delta_v_total']:.1f} m/s")
    ΔV total: 3857.4 m/s
    
    References:
    -----------
    Curtis, H. (2013). Orbital Mechanics for Engineering Students, 
    Chapter 6: Orbital Maneuvers.
    """
    # Velocidades circulares iniciales y finales
    v1 = circular_velocity(r1, mu)
    v2 = circular_velocity(r2, mu)
    
    # Semieje mayor de órbita de transferencia
    a_transfer = (r1 + r2) / 2
    
    # Velocidades en la órbita de transferencia
    # En periapsis (r1):
    v_transfer_peri = np.sqrt(mu * (2/r1 - 1/a_transfer))
    
    # En apoapsis (r2):
    v_transfer_apo = np.sqrt(mu * (2/r2 - 1/a_transfer))
    
    # ΔV de cada impulso
    delta_v_1 = abs(v_transfer_peri - v1)
    delta_v_2 = abs(v2 - v_transfer_apo)
    delta_v_total = delta_v_1 + delta_v_2
    
    # Tiempo de transferencia (medio periodo de la órbita de transferencia)
    transfer_time = np.pi * np.sqrt(a_transfer**3 / mu)
    
    return {
        'delta_v_1': delta_v_1,
        'delta_v_2': delta_v_2,
        'delta_v_total': delta_v_total,
        'transfer_time': transfer_time,
        'semi_major': a_transfer,
        'description': f'Hohmann transfer: r1={r1/1e3:.1f} km → r2={r2/1e3:.1f} km'
    }


def hohmann_with_elliptic(r_peri_1, r_apo_1, r_peri_2, r_apo_2, mu=GM_earth):
    """
    Transferencia Hohmann entre órbitas elípticas generales.
    
    Calcula el ΔV para transferir entre dos órbitas elípticas arbitrarias
    usando una órbita de transferencia que toca ambas.
    
    Parameters:
    -----------
    r_peri_1, r_apo_1 : float
        Periapsis y apoapsis de órbita inicial (m)
    r_peri_2, r_apo_2 : float
        Periapsis y apoapsis de órbita final (m)
    mu : float, optional
        Parámetro gravitacional GM (m^3/s^2)
    
    Returns:
    --------
    result : dict
        Similar a hohmann_transfer() pero con más detalles
    
    Notes:
    ------
    Asume que las órbitas son coplanares y el transfer ocurre
    en la línea de ápsides común.
    """
    # Semiejes mayores
    a1 = (r_peri_1 + r_apo_1) / 2
    a2 = (r_peri_2 + r_apo_2) / 2
    
    # Determinar punto de contacto óptimo
    # Típicamente: periapsis de órbita más alta, apoapsis de más baja
    if a2 > a1:
        # Transferencia ascendente
        r_contact_1 = r_apo_1  # Apoapsis de órbita baja
        r_contact_2 = r_peri_2  # Periapsis de órbita alta
    else:
        # Transferencia descendente
        r_contact_1 = r_peri_1
        r_contact_2 = r_apo_2
    
    # Velocidades en los puntos de contacto
    # Órbita inicial
    v1_contact = np.sqrt(mu * (2/r_contact_1 - 1/a1))
    
    # Órbita final
    v2_contact = np.sqrt(mu * (2/r_contact_2 - 1/a2))
    
    # Órbita de transferencia
    a_transfer = (r_contact_1 + r_contact_2) / 2
    v_transfer_1 = np.sqrt(mu * (2/r_contact_1 - 1/a_transfer))
    v_transfer_2 = np.sqrt(mu * (2/r_contact_2 - 1/a_transfer))
    
    # ΔV
    delta_v_1 = abs(v_transfer_1 - v1_contact)
    delta_v_2 = abs(v2_contact - v_transfer_2)
    delta_v_total = delta_v_1 + delta_v_2
    
    # Tiempo de transferencia
    transfer_time = np.pi * np.sqrt(a_transfer**3 / mu)
    
    return {
        'delta_v_1': delta_v_1,
        'delta_v_2': delta_v_2,
        'delta_v_total': delta_v_total,
        'transfer_time': transfer_time,
        'semi_major': a_transfer,
        'contact_points': (r_contact_1, r_contact_2),
        'description': f'Elliptic Hohmann: a1={a1/1e3:.1f} km → a2={a2/1e3:.1f} km'
    }


def bielliptic_transfer(r1, r2, r_intermediate, mu=GM_earth):
    """
    Calcula ΔV para transferencia bi-elíptica.
    
    Una transferencia bi-elíptica usa tres impulsos:
    1. Impulso en r1 para llegar a r_intermediate
    2. Impulso en r_intermediate para apuntar a r2
    3. Impulso en r2 para circularizar
    
    Para ratios r2/r1 > 11.94, la bi-elíptica puede ser más eficiente
    que Hohmann si r_intermediate es suficientemente grande.
    
    Parameters:
    -----------
    r1 : float
        Radio de órbita inicial (m)
    r2 : float
        Radio de órbita final (m)
    r_intermediate : float
        Radio del punto intermedio (apoapsis de primera elipse) (m)
        Debe ser > max(r1, r2)
    mu : float, optional
        Parámetro gravitacional GM (m^3/s^2)
    
    Returns:
    --------
    result : dict
        - 'delta_v_1': Primer impulso en r1 (m/s)
        - 'delta_v_2': Segundo impulso en r_intermediate (m/s)
        - 'delta_v_3': Tercer impulso en r2 (m/s)
        - 'delta_v_total': ΔV total (m/s)
        - 'transfer_time': Tiempo total (s)
        - 'is_better_than_hohmann': bool
    
    Examples:
    ---------
    >>> # LEO a órbita muy alta (ratio > 12)
    >>> r1 = 6771e3
    >>> r2 = 100000e3
    >>> r_int = 200000e3
    >>> result = bielliptic_transfer(r1, r2, r_int)
    
    References:
    -----------
    Curtis, H. (2013). Orbital Mechanics for Engineering Students,
    Section 6.3: Bi-elliptic Hohmann transfer.
    """
    if r_intermediate <= max(r1, r2):
        raise ValueError("r_intermediate debe ser mayor que r1 y r2")
    
    # Velocidades circulares
    v1 = circular_velocity(r1, mu)
    v2 = circular_velocity(r2, mu)
    
    # Primera elipse: r1 (periapsis) → r_intermediate (apoapsis)
    a_first = (r1 + r_intermediate) / 2
    v_first_peri = np.sqrt(mu * (2/r1 - 1/a_first))
    v_first_apo = np.sqrt(mu * (2/r_intermediate - 1/a_first))
    
    # Segunda elipse: r_intermediate (apoapsis) → r2 (periapsis)
    a_second = (r_intermediate + r2) / 2
    v_second_apo = np.sqrt(mu * (2/r_intermediate - 1/a_second))
    v_second_peri = np.sqrt(mu * (2/r2 - 1/a_second))
    
    # ΔV de cada impulso
    delta_v_1 = abs(v_first_peri - v1)
    delta_v_2 = abs(v_second_apo - v_first_apo)
    delta_v_3 = abs(v2 - v_second_peri)
    delta_v_total = delta_v_1 + delta_v_2 + delta_v_3
    
    # Tiempo de transferencia
    t_first = np.pi * np.sqrt(a_first**3 / mu)
    t_second = np.pi * np.sqrt(a_second**3 / mu)
    transfer_time = t_first + t_second
    
    # Comparar con Hohmann
    hohmann = hohmann_transfer(r1, r2, mu)
    is_better = delta_v_total < hohmann['delta_v_total']
    
    return {
        'delta_v_1': delta_v_1,
        'delta_v_2': delta_v_2,
        'delta_v_3': delta_v_3,
        'delta_v_total': delta_v_total,
        'transfer_time': transfer_time,
        'hohmann_delta_v': hohmann['delta_v_total'],
        'savings_vs_hohmann': hohmann['delta_v_total'] - delta_v_total,
        'is_better_than_hohmann': is_better,
        'description': f'Bi-elliptic: {r1/1e3:.0f} → {r_intermediate/1e3:.0f} → {r2/1e3:.0f} km'
    }


def find_optimal_bielliptic(r1, r2, mu=GM_earth, r_int_min=None, r_int_max=None):
    """
    Encuentra el r_intermediate óptimo para transferencia bi-elíptica.
    
    Busca el radio intermedio que minimiza el ΔV total.
    
    Parameters:
    -----------
    r1, r2 : float
        Radios inicial y final (m)
    mu : float, optional
        Parámetro gravitacional
    r_int_min, r_int_max : float, optional
        Límites de búsqueda para r_intermediate
        Si None, usa valores razonables automáticos
    
    Returns:
    --------
    result : dict
        Resultado de bielliptic_transfer() con r_intermediate óptimo
    """
    from scipy.optimize import minimize_scalar
    
    r_max = max(r1, r2)
    
    # Límites de búsqueda
    if r_int_min is None:
        r_int_min = r_max * 1.1
    if r_int_max is None:
        r_int_max = r_max * 50
    
    # Función objetivo
    def objective(r_int):
        try:
            result = bielliptic_transfer(r1, r2, r_int, mu)
            return result['delta_v_total']
        except:
            return np.inf
    
    # Optimizar
    opt_result = minimize_scalar(
        objective,
        bounds=(r_int_min, r_int_max),
        method='bounded'
    )
    
    r_optimal = opt_result.x
    
    # Resultado con r_intermediate óptimo
    result = bielliptic_transfer(r1, r2, r_optimal, mu)
    result['r_intermediate_optimal'] = r_optimal
    
    return result


def compare_hohmann_bielliptic(r1, r2, mu=GM_earth):
    """
    Compara transferencia Hohmann vs Bi-elíptica óptima.
    
    Parameters:
    -----------
    r1, r2 : float
        Radios inicial y final (m)
    mu : float, optional
        Parámetro gravitacional
    
    Returns:
    --------
    comparison : dict
        Resultados de ambas estrategias + recomendación
    """
    # Hohmann
    hohmann = hohmann_transfer(r1, r2, mu)
    
    # Bi-elliptic óptima
    try:
        bielliptic = find_optimal_bielliptic(r1, r2, mu)
    except:
        bielliptic = None
    
    # Ratio de radios
    ratio = r2 / r1
    
    # Recomendación
    if bielliptic and bielliptic['is_better_than_hohmann']:
        recommendation = "Bi-elliptic"
        savings = bielliptic['savings_vs_hohmann']
    else:
        recommendation = "Hohmann"
        savings = 0.0
    
    return {
        'hohmann': hohmann,
        'bielliptic': bielliptic,
        'ratio': ratio,
        'recommendation': recommendation,
        'savings_m_s': savings,
        'savings_percent': (savings / hohmann['delta_v_total']) * 100 if hohmann['delta_v_total'] > 0 else 0
    }




def simple_plane_change(v, delta_i):
    """
    Calcula ΔV para cambio simple de inclinación orbital.
    
    Un cambio de plano puro (sin cambio de órbita) se hace con un
    impulso perpendicular al plano orbital actual.
    
    Parameters:
    -----------
    v : float
        Velocidad orbital actual (m/s)
    delta_i : float
        Cambio de inclinación deseado (grados)
    
    Returns:
    --------
    delta_v : float
        ΔV requerido (m/s)
    
    Notes:
    ------
    La ecuación es: ΔV = 2 × v × sin(Δi/2)
    
    Para Δi = 90° (plano ecuatorial → polar): ΔV = √2 × v ≈ 1.41v
    Para Δi pequeños: ΔV ≈ v × Δi (en radianes)
    
    Examples:
    ---------
    >>> # Cambiar ISS (51.6°) a polar (90°)
    >>> v_iss = 7669  # m/s
    >>> delta_i = 90 - 51.6  # 38.4°
    >>> dv = simple_plane_change(v_iss, delta_i)
    >>> print(f"ΔV: {dv:.1f} m/s")
    ΔV: 5018.3 m/s
    
    References:
    -----------
    Curtis, H. (2013). Section 6.4: Plane Change Maneuvers
    """
    # Convertir a radianes
    delta_i_rad = np.deg2rad(delta_i)
    
    # Ecuación de cambio de plano
    delta_v = 2 * v * np.sin(delta_i_rad / 2)
    
    return delta_v


def combined_plane_change(r1, r2, delta_i, mu=GM_earth):
    """
    Cambio combinado: transferencia Hohmann + cambio de inclinación.
    
    Dos estrategias posibles:
    1. Cambiar plano al inicio (en r1)
    2. Cambiar plano al final (en r2) ← Generalmente mejor
    
    La estrategia óptima depende de las velocidades en cada punto.
    Como regla general: hacer el cambio de plano donde la velocidad
    sea MENOR (típicamente en r2 si r2 > r1).
    
    Parameters:
    -----------
    r1, r2 : float
        Radios inicial y final (m)
    delta_i : float
        Cambio de inclinación (grados)
    mu : float, optional
        Parámetro gravitacional
    
    Returns:
    --------
    result : dict
        - 'strategy_at_r1': ΔV total si cambio en r1
        - 'strategy_at_r2': ΔV total si cambio en r2
        - 'optimal_strategy': 'r1' o 'r2'
        - 'optimal_delta_v': Menor de los dos
        - 'savings': Diferencia entre estrategias
    
    Examples:
    ---------
    >>> # LEO → GEO con cambio de inclinación
    >>> r_leo = 6771e3
    >>> r_geo = 42157e3
    >>> result = combined_plane_change(r_leo, r_geo, delta_i=28.5)
    """
    # Velocidades circulares
    v1 = circular_velocity(r1, mu)
    v2 = circular_velocity(r2, mu)
    
    # Transferencia Hohmann base (sin cambio de plano)
    hohmann = hohmann_transfer(r1, r2, mu)
    
    # ESTRATEGIA 1: Cambio de plano en r1 (inicio)
    # Paso 1: Cambiar plano en r1
    dv_plane_r1 = simple_plane_change(v1, delta_i)
    # Paso 2: Hohmann normal
    dv_hohmann = hohmann['delta_v_total']
    strategy_r1_total = dv_plane_r1 + dv_hohmann
    
    # ESTRATEGIA 2: Cambio de plano en r2 (final)
    # Paso 1: Hohmann hasta r2
    dv_hohmann_only = hohmann['delta_v_1'] + hohmann['delta_v_2']
    # Paso 2: Cambiar plano en r2 (velocidad menor)
    dv_plane_r2 = simple_plane_change(v2, delta_i)
    strategy_r2_total = dv_hohmann_only + dv_plane_r2
    
    # ESTRATEGIA 3 (óptima): Combinar en apoapsis
    # Hacer cambio de plano simultáneamente con circularización en r2
    # Vector velocity en apoapsis de transfer orbit
    a_transfer = (r1 + r2) / 2
    v_transfer_apo = np.sqrt(mu * (2/r2 - 1/a_transfer))
    
    # Cambio vectorial: de v_transfer_apo (inclinación vieja) a v2 (inclinación nueva)
    # Usando ley de cosenos
    delta_i_rad = np.deg2rad(delta_i)
    dv_combined_r2 = np.sqrt(v_transfer_apo**2 + v2**2 - 
                             2*v_transfer_apo*v2*np.cos(delta_i_rad))
    
    strategy_combined_total = hohmann['delta_v_1'] + dv_combined_r2
    
    # Determinar estrategia óptima
    strategies = {
        'plane_at_r1': strategy_r1_total,
        'plane_at_r2': strategy_r2_total,
        'combined_at_r2': strategy_combined_total
    }
    
    optimal_strategy = min(strategies, key=strategies.get)
    optimal_delta_v = strategies[optimal_strategy]
    
    return {
        'hohmann_only': hohmann['delta_v_total'],
        'plane_change_only': simple_plane_change(v1, delta_i),
        'strategy_plane_at_r1': strategy_r1_total,
        'strategy_plane_at_r2': strategy_r2_total,
        'strategy_combined_at_r2': strategy_combined_total,
        'optimal_strategy': optimal_strategy,
        'optimal_delta_v': optimal_delta_v,
        'penalty_vs_hohmann': optimal_delta_v - hohmann['delta_v_total'],
        'description': f'Combined: {r1/1e3:.0f} km → {r2/1e3:.0f} km, Δi={delta_i}°'
    }


def plane_change_cost_analysis(r, delta_i_range=None, mu=GM_earth):
    """
    Analiza costo de cambio de plano para diferentes ángulos.
    
    Parameters:
    -----------
    r : float
        Radio orbital (m)
    delta_i_range : array-like, optional
        Rango de ángulos a analizar (grados)
        Default: [0, 5, 10, 20, 30, 45, 60, 90]
    mu : float, optional
        Parámetro gravitacional
    
    Returns:
    --------
    results : dict
        Contiene arrays de ángulos y ΔVs correspondientes
    """
    if delta_i_range is None:
        delta_i_range = np.array([0, 5, 10, 20, 30, 45, 60, 90])
    
    v = circular_velocity(r, mu)
    delta_vs = np.array([simple_plane_change(v, di) for di in delta_i_range])
    
    return {
        'radius': r,
        'velocity': v,
        'delta_i_degrees': delta_i_range,
        'delta_v_m_s': delta_vs,
        'delta_v_fraction': delta_vs / v
    }




def escape_velocity(r, mu=GM_earth):
    """
    Calcula velocidad de escape desde radio r.
    
    La velocidad de escape es la velocidad mínima necesaria para
    escapar completamente de la influencia gravitacional del cuerpo.
    
    Parameters:
    -----------
    r : float
        Radio desde el centro del cuerpo (m)
    mu : float, optional
        Parámetro gravitacional GM (m^3/s^2)
    
    Returns:
    --------
    v_escape : float
        Velocidad de escape (m/s)
    
    Notes:
    ------
    v_escape = √(2μ/r) = √2 × v_circular
    
    Examples:
    ---------
    >>> # Escape desde superficie de la Tierra
    >>> v_esc = escape_velocity(R_earth)
    >>> print(f"Escape desde superficie: {v_esc:.1f} m/s")
    Escape desde superficie: 11186.1 m/s
    
    >>> # Escape desde LEO (400 km)
    >>> v_esc_leo = escape_velocity(R_earth + 400e3)
    >>> print(f"Escape desde LEO: {v_esc_leo:.1f} m/s")
    Escape desde LEO: 10929.3 m/s
    """
    return np.sqrt(2 * mu / r)


def delta_v_to_escape(r, v_initial=None, mu=GM_earth):
    """
    Calcula ΔV necesario para escapar desde órbita circular.
    
    Parameters:
    -----------
    r : float
        Radio de órbita inicial (m)
    v_initial : float, optional
        Velocidad inicial (m/s). Si None, asume órbita circular.
    mu : float, optional
        Parámetro gravitacional
    
    Returns:
    --------
    result : dict
        - 'v_circular': Velocidad circular en r (m/s)
        - 'v_escape': Velocidad de escape desde r (m/s)
        - 'delta_v': ΔV necesario para escapar (m/s)
        - 'v_infinity': Velocidad en infinito (m/s) - será 0
    
    Examples:
    ---------
    >>> # Escapar desde LEO
    >>> result = delta_v_to_escape(6771e3)
    >>> print(f"ΔV para escape: {result['delta_v']:.1f} m/s")
    ΔV para escape: 3165.4 m/s
    """
    if v_initial is None:
        v_initial = circular_velocity(r, mu)
    
    v_esc = escape_velocity(r, mu)
    delta_v = v_esc - v_initial
    
    return {
        'v_initial': v_initial,
        'v_circular': circular_velocity(r, mu),
        'v_escape': v_esc,
        'delta_v': delta_v,
        'v_infinity': 0.0,  # Para escape mínimo
        'description': f'Escape from r={r/1e3:.0f} km'
    }


def hyperbolic_excess_velocity(r, v_infinity, mu=GM_earth):
    """
    Calcula velocidad necesaria en r para alcanzar v∞ específica.
    
    En misiones interplanetarias, necesitas no solo escapar, sino
    hacerlo con cierta velocidad "en el infinito" (v∞) para seguir
    la trayectoria heliocéntrica deseada.
    
    Parameters:
    -----------
    r : float
        Radio de partida (m)
    v_infinity : float
        Velocidad hiperbólica en infinito deseada (m/s)
    mu : float, optional
        Parámetro gravitacional
    
    Returns:
    --------
    v_periapsis : float
        Velocidad necesaria en periapsis (m/s)
    
    Notes:
    ------
    Para órbita hiperbólica:
    v² = v∞² + 2μ/r
    
    Examples:
    ---------
    >>> # Misión a Marte: necesitas v∞ = 2.95 km/s al salir de Tierra
    >>> v_needed = hyperbolic_excess_velocity(6771e3, 2950)
    >>> print(f"Velocidad en LEO: {v_needed:.1f} m/s")
    Velocidad en LEO: 11246.8 m/s
    
    References:
    -----------
    Curtis, H. (2013). Chapter 8: Interplanetary Trajectories
    """
    v_periapsis = np.sqrt(v_infinity**2 + 2*mu/r)
    return v_periapsis


def delta_v_to_hyperbolic(r, v_infinity, mu=GM_earth):
    """
    ΔV para alcanzar trayectoria hiperbólica con v∞ específica.
    
    Parameters:
    -----------
    r : float
        Radio de órbita de partida (m)
    v_infinity : float
        Velocidad hiperbólica deseada (m/s)
    mu : float, optional
        Parámetro gravitacional
    
    Returns:
    --------
    result : dict
        Información completa de la maniobra
    """
    v_circular = circular_velocity(r, mu)
    v_needed = hyperbolic_excess_velocity(r, v_infinity, mu)
    delta_v = v_needed - v_circular
    
    # Energía específica de la hipérbola
    C3 = v_infinity**2  # km²/s² si v_infinity en km/s
    
    return {
        'v_circular': v_circular,
        'v_needed': v_needed,
        'delta_v': delta_v,
        'v_infinity': v_infinity,
        'C3': C3,
        'description': f'Hyperbolic escape: v∞={v_infinity:.0f} m/s from r={r/1e3:.0f} km'
    }


def interplanetary_hohmann(r1_planet, r2_planet, mu_sun=1.32712440018e20):
    """
    Transferencia Hohmann interplanetaria entre órbitas planetarias.
    
    Calcula el ΔV heliocéntrico (relativo al Sol) necesario para
    transferir entre órbitas de dos planetas.
    
    Parameters:
    -----------
    r1_planet : float
        Radio orbital del planeta de partida (m desde Sol)
    r2_planet : float
        Radio orbital del planeta destino (m desde Sol)
    mu_sun : float, optional
        Parámetro gravitacional del Sol (m³/s²)
    
    Returns:
    --------
    result : dict
        - 'delta_v_departure': ΔV en partida relativo al Sol
        - 'delta_v_arrival': ΔV en llegada relativo al Sol
        - 'v_infinity_departure': v∞ de salida del planeta
        - 'v_infinity_arrival': v∞ de llegada al planeta
        - 'transfer_time': Tiempo de transferencia (días)
    
    Examples:
    ---------
    >>> # Tierra → Marte
    >>> r_earth = 1.496e11  # 1 AU en metros
    >>> r_mars = 2.279e11   # 1.524 AU
    >>> result = interplanetary_hohmann(r_earth, r_mars)
    
    Notes:
    ------
    Este cálculo da ΔV heliocéntrico. Para obtener ΔV desde LEO,
    necesitas añadir el costo de escape de la Tierra con la v∞ adecuada.
    
    References:
    -----------
    Vallado, D. (2013). Chapter 6: Lambert's Problem and 
    Interplanetary Trajectories
    """
    # Velocidades orbitales de los planetas alrededor del Sol
    v1_planet = circular_velocity(r1_planet, mu_sun)
    v2_planet = circular_velocity(r2_planet, mu_sun)
    
    # Órbita de transferencia (Hohmann heliocéntrica)
    a_transfer = (r1_planet + r2_planet) / 2
    
    # Velocidades en la órbita de transferencia
    v_transfer_perihelion = np.sqrt(mu_sun * (2/r1_planet - 1/a_transfer))
    v_transfer_aphelion = np.sqrt(mu_sun * (2/r2_planet - 1/a_transfer))
    
    # ΔV heliocéntricos
    delta_v_departure = abs(v_transfer_perihelion - v1_planet)
    delta_v_arrival = abs(v2_planet - v_transfer_aphelion)
    
    # Velocidades hiperbólicas (v∞) relativas a cada planeta
    v_inf_departure = delta_v_departure
    v_inf_arrival = delta_v_arrival
    
    # Tiempo de transferencia
    transfer_time = np.pi * np.sqrt(a_transfer**3 / mu_sun)
    
    return {
        'delta_v_departure': delta_v_departure,
        'delta_v_arrival': delta_v_arrival,
        'v_infinity_departure': v_inf_departure,
        'v_infinity_arrival': v_inf_arrival,
        'transfer_time_seconds': transfer_time,
        'transfer_time_days': transfer_time / 86400,
        'v1_planet': v1_planet,
        'v2_planet': v2_planet,
        'description': f'Interplanetary: r1={r1_planet/1e9:.3f} Gm → r2={r2_planet/1e9:.3f} Gm'
    }


def earth_departure_delta_v(v_infinity, r_parking=6771e3, mu_earth=GM_earth):
    """
    ΔV total para salir de órbita de parking terrestre hacia
    trayectoria interplanetaria.
    
    Parameters:
    -----------
    v_infinity : float
        Velocidad hiperbólica requerida (m/s)
    r_parking : float, optional
        Radio de órbita de parking (default: LEO 400 km)
    mu_earth : float, optional
        Parámetro gravitacional Tierra
    
    Returns:
    --------
    delta_v : float
        ΔV total desde órbita de parking (m/s)
    """
    v_parking = circular_velocity(r_parking, mu_earth)
    v_needed = hyperbolic_excess_velocity(r_parking, v_infinity, mu_earth)
    
    return v_needed - v_parking



def phasing_orbit(r_target, phase_angle_degrees, n_orbits=1, mu=GM_earth):
    """
    Calcula órbita de espera para corregir diferencia de fase.
    
    Cuando dos satélites están en la misma órbita pero desfasados,
    uno puede usar una órbita de phasing (ligeramente diferente) para
    "adelantar" o "atrasar" y alcanzar el punto de encuentro.
    
    Parameters:
    -----------
    r_target : float
        Radio de la órbita objetivo (m)
    phase_angle_degrees : float
        Ángulo de fase a corregir (grados)
        Positivo: necesitas adelantar (órbita más baja)
        Negativo: necesitas atrasar (órbita más alta)
    n_orbits : int, optional
        Número de órbitas para completar la corrección
    mu : float, optional
        Parámetro gravitacional
    
    Returns:
    --------
    result : dict
        - 'r_phasing': Radio de la órbita de phasing (m)
        - 'delta_v_enter': ΔV para entrar a órbita de phasing
        - 'delta_v_exit': ΔV para volver a órbita target
        - 'delta_v_total': ΔV total
        - 'phasing_time': Tiempo en órbita de phasing (s)
        - 'phase_correction': Ángulo corregido por órbita (grados)
    
    Examples:
    ---------
    >>> # ISS está 45° adelante, queremos alcanzarla en 1 órbita
    >>> result = phasing_orbit(6771e3, phase_angle=45, n_orbits=1)
    >>> print(f"ΔV total: {result['delta_v_total']:.1f} m/s")
    >>> print(f"Tiempo: {result['phasing_time']/3600:.1f} horas")
    
    Notes:
    ------
    La órbita de phasing debe dar n vueltas mientras el target da
    (n ± Δφ/360) vueltas, donde Δφ es el ángulo a corregir.
    
    References:
    -----------
    Curtis, H. (2013). Section 7.2: Rendezvous
    """
    # Periodo de la órbita target
    T_target = 2 * np.pi * np.sqrt(r_target**3 / mu)
    
    # Ángulo que avanza el target en n_orbits
    angle_target = n_orbits * 360  # grados
    
    # Ángulo que debemos avanzar nosotros
    angle_phasing = angle_target - phase_angle_degrees
    
    # Número de órbitas de phasing en ese tiempo
    n_phasing = angle_phasing / 360
    
    # Periodo de la órbita de phasing
    T_phasing = (n_orbits / n_phasing) * T_target
    
    # Radio de la órbita de phasing (órbita circular)
    # Usando T = 2π√(r³/μ) → r = (μT²/4π²)^(1/3)
    r_phasing = (mu * T_phasing**2 / (4 * np.pi**2))**(1/3)
    
    # ΔV para cambiar entre órbitas
    v_target = circular_velocity(r_target, mu)
    v_phasing = circular_velocity(r_phasing, mu)
    
    delta_v_enter = abs(v_phasing - v_target)
    delta_v_exit = abs(v_target - v_phasing)
    delta_v_total = delta_v_enter + delta_v_exit
    
    # Tiempo en órbita de phasing
    phasing_time = n_phasing * T_phasing
    
    # Corrección de fase por órbita
    phase_per_orbit = phase_angle_degrees / n_orbits
    
    return {
        'r_target': r_target,
        'r_phasing': r_phasing,
        'altitude_change': (r_phasing - r_target),
        'T_target': T_target,
        'T_phasing': T_phasing,
        'n_orbits_target': n_orbits,
        'n_orbits_phasing': n_phasing,
        'delta_v_enter': delta_v_enter,
        'delta_v_exit': delta_v_exit,
        'delta_v_total': delta_v_total,
        'phasing_time': phasing_time,
        'phase_angle': phase_angle_degrees,
        'phase_per_orbit': phase_per_orbit,
        'description': f'Phasing: Δφ={phase_angle_degrees:.1f}° in {n_orbits} orbits'
    }


def optimize_phasing_orbits(r_target, phase_angle_degrees, max_orbits=10, mu=GM_earth):
    """
    Encuentra el número óptimo de órbitas para phasing (minimiza ΔV).
    
    Parameters:
    -----------
    r_target : float
        Radio de órbita objetivo (m)
    phase_angle_degrees : float
        Ángulo de fase a corregir (grados)
    max_orbits : int, optional
        Máximo número de órbitas a considerar
    mu : float, optional
        Parámetro gravitacional
    
    Returns:
    --------
    results : list of dict
        Lista con resultados para cada n_orbits,
        ordenada por ΔV total (menor primero)
    """
    results = []
    
    for n in range(1, max_orbits + 1):
        try:
            result = phasing_orbit(r_target, phase_angle_degrees, n, mu)
            result['n_orbits'] = n
            results.append(result)
        except:
            continue
    
    # Ordenar por ΔV total
    results.sort(key=lambda x: x['delta_v_total'])
    
    return results


def rendezvous_simple(r1, r2, phase_angle_degrees, mu=GM_earth):
    """
    Maniobra completa de rendezvous entre dos órbitas circulares.
    
    Combina:
    1. Hohmann transfer de r1 a r2
    2. Phasing maneuver para corregir fase
    
    Parameters:
    -----------
    r1 : float
        Radio de órbita inicial (m)
    r2 : float
        Radio de órbita del target (m)
    phase_angle_degrees : float
        Diferencia de fase inicial (grados)
    mu : float, optional
        Parámetro gravitacional
    
    Returns:
    --------
    result : dict
        Plan completo de rendezvous con ΔV total y tiempo
    
    Notes:
    ------
    Esta es una versión simplificada. En realidad, el phasing
    puede hacerse DURANTE el transfer Hohmann, o usar órbitas
    elípticas de phasing para mayor eficiencia.
    """
    # Paso 1: Transfer Hohmann
    hohmann = hohmann_transfer(r1, r2, mu)
    
    # Paso 2: Phasing en órbita final
    phasing_options = optimize_phasing_orbits(r2, phase_angle_degrees, max_orbits=20, mu=mu)
    phasing_optimal = phasing_options[0]  # Menor ΔV
    
    # ΔV total
    delta_v_total = hohmann['delta_v_total'] + phasing_optimal['delta_v_total']
    
    # Tiempo total
    time_total = hohmann['transfer_time'] + phasing_optimal['phasing_time']
    
    return {
        'hohmann': hohmann,
        'phasing': phasing_optimal,
        'delta_v_hohmann': hohmann['delta_v_total'],
        'delta_v_phasing': phasing_optimal['delta_v_total'],
        'delta_v_total': delta_v_total,
        'time_hohmann': hohmann['transfer_time'],
        'time_phasing': phasing_optimal['phasing_time'],
        'time_total': time_total,
        'description': f'Rendezvous: {r1/1e3:.0f} km → {r2/1e3:.0f} km, Δφ={phase_angle_degrees}°'
    }




def rendezvous_realistic(r1, r2, phase_angle_degrees, time_available_hours=24, mu=GM_earth):
    """
    Rendezvous más realista usando tiempo disponible.
    
    En vez de minimizar ΔV puro, optimiza para un tiempo dado,
    que es más parecido a cómo se planean misiones reales.
    
    Parameters:
    -----------
    r1, r2 : float
        Radios inicial y final (m)
    phase_angle_degrees : float
        Diferencia de fase (grados)
    time_available_hours : float, optional
        Tiempo disponible para completar rendezvous (horas)
    mu : float, optional
        Parámetro gravitacional
    
    Returns:
    --------
    result : dict
        Plan de rendezvous optimizado para tiempo dado
    """
    # Hohmann
    hohmann = hohmann_transfer(r1, r2, mu)
    
    # Tiempo restante para phasing
    time_phasing_available = (time_available_hours * 3600) - hohmann['transfer_time']
    
    if time_phasing_available <= 0:
        # No hay tiempo para phasing
        return {
            'feasible': False,
            'reason': 'Insufficient time for phasing',
            'time_needed': hohmann['transfer_time'] / 3600
        }
    
    # Periodo en órbita final
    T_target = 2 * np.pi * np.sqrt(r2**3 / mu)
    
    # Número de órbitas disponibles para phasing
    n_orbits_available = time_phasing_available / T_target
    
    # Calcular phasing con ese número de órbitas
    try:
        phasing = phasing_orbit(r2, phase_angle_degrees, n_orbits=int(n_orbits_available), mu=mu)
    except:
        # Si falla, usar menos órbitas
        phasing = phasing_orbit(r2, phase_angle_degrees, n_orbits=max(1, int(n_orbits_available/2)), mu=mu)
    
    # Total
    delta_v_total = hohmann['delta_v_total'] + phasing['delta_v_total']
    time_total = hohmann['transfer_time'] + phasing['phasing_time']
    
    return {
        'feasible': True,
        'hohmann': hohmann,
        'phasing': phasing,
        'delta_v_total': delta_v_total,
        'time_total_seconds': time_total,
        'time_total_hours': time_total / 3600,
        'time_constraint_hours': time_available_hours,
        'description': f'Realistic rendezvous in {time_available_hours}h'
    }



def coplanar_rendezvous_dv(delta_r, delta_v_tangent, delta_v_radial=0):
    """
    Aproximación de ΔV para rendezvous de rango cercano (< 100 km).
    
    Usando ecuaciones de Clohessy-Wiltshire (Hill equations) para
    movimiento relativo en órbita.
    
    Parameters:
    -----------
    delta_r : float
        Separación radial (m)
    delta_v_tangent : float
        Diferencia de velocidad tangencial (m/s)
    delta_v_radial : float, optional
        Diferencia de velocidad radial (m/s)
    
    Returns:
    --------
    delta_v_total : float
        ΔV aproximado para rendezvous (m/s)
    
    Notes:
    ------
    Para separaciones pequeñas (< 100 km), se puede usar
    aproximación lineal del movimiento relativo.
    
    Esta es una estimación simplificada. Rendezvous real
    requiere múltiples impulsos y guiado preciso.
    
    References:
    -----------
    Clohessy, W., Wiltshire, R. (1960). "Terminal Guidance System
    for Satellite Rendezvous". Journal of Aerospace Sciences.
    """
    # Estimación simplificada: suma vectorial
    delta_v_total = np.sqrt(delta_v_tangent**2 + delta_v_radial**2)
    
    # En realidad necesitas ~1.5-2x por ineficiencias de timing
    safety_factor = 1.5
    
    return delta_v_total * safety_factor






if __name__ == "__main__":
    # Tests básicos
    print("="*70)
    print("PROYECTO 3: MISSION ΔV CALCULATOR")
    print("="*70)
    
    # Test 1: LEO → GEO (Hohmann)
    print("\n[Test 1] LEO → GEO Transfer (Hohmann)")
    r_leo = 6371e3 + 400e3
    r_geo = 6371e3 + 35786e3
    
    result = hohmann_transfer(r_leo, r_geo)
    print(f"  r1 (LEO): {r_leo/1e3:.1f} km")
    print(f"  r2 (GEO): {r_geo/1e3:.1f} km")
    print(f"  Ratio r2/r1: {r_geo/r_leo:.2f}")
    print(f"  ΔV₁: {result['delta_v_1']:.1f} m/s")
    print(f"  ΔV₂: {result['delta_v_2']:.1f} m/s")
    print(f"  ΔV total: {result['delta_v_total']:.1f} m/s")
    print(f"  Tiempo: {result['transfer_time']/3600:.2f} horas")
    
    # Test 2: LEO → Órbita muy alta (Hohmann vs Bi-elliptic)
    print("\n[Test 2] LEO → Órbita muy alta (ratio = 15)")
    r_high = r_leo * 15
    
    comparison = compare_hohmann_bielliptic(r_leo, r_high)
    
    print(f"  r1: {r_leo/1e3:.1f} km")
    print(f"  r2: {r_high/1e3:.1f} km")
    print(f"  Ratio: {comparison['ratio']:.2f}")
    print(f"\n  Hohmann:")
    print(f"    ΔV: {comparison['hohmann']['delta_v_total']:.1f} m/s")
    print(f"    Tiempo: {comparison['hohmann']['transfer_time']/3600:.1f} horas")
    
    if comparison['bielliptic']:
        print(f"\n  Bi-elliptic (óptima):")
        print(f"    r_intermediate: {comparison['bielliptic']['r_intermediate_optimal']/1e3:.1f} km")
        print(f"    ΔV: {comparison['bielliptic']['delta_v_total']:.1f} m/s")
        print(f"    Tiempo: {comparison['bielliptic']['transfer_time']/3600:.1f} horas")
        print(f"\n  → Recomendación: {comparison['recommendation']}")
        print(f"  → Ahorro: {comparison['savings_m_s']:.1f} m/s ({comparison['savings_percent']:.1f}%)")
    
    # Test 3: ¿Cuándo se vuelve mejor bi-elliptic?
    print("\n[Test 3] Análisis: ¿Cuándo usar bi-elliptic?")
    print("  Ratio    Hohmann    Bi-elliptic   Mejor")
    print("  " + "-"*50)
    
    for ratio in [2, 5, 8, 11.94, 15, 20, 30]:
        r2_test = r_leo * ratio
        comp = compare_hohmann_bielliptic(r_leo, r2_test)
        
        h_dv = comp['hohmann']['delta_v_total']
        
        if comp['bielliptic']:
            b_dv = comp['bielliptic']['delta_v_total']
            better = "Bi-elliptic" if comp['bielliptic']['is_better_than_hohmann'] else "Hohmann"
        else:
            b_dv = np.nan
            better = "Hohmann"
        
        print(f"  {ratio:5.2f}    {h_dv:7.1f}    {b_dv:9.1f}      {better}")
    
    print("\n  Nota: Ratio crítico teórico = 11.94")
    print("        (Para r_intermediate → ∞)")
    
# Test 4: Plane changes
    print("\n[Test 4] Cambios de Plano (Plane Changes)")
    print("  Δi      ΔV (LEO)    ΔV (GEO)    Ratio")
    print("  " + "-"*50)
    
    v_leo_circ = circular_velocity(r_leo)
    v_geo_circ = circular_velocity(r_geo)
    
    for delta_i in [5, 10, 20, 30, 45, 60, 90]:
        dv_leo = simple_plane_change(v_leo_circ, delta_i)
        dv_geo = simple_plane_change(v_geo_circ, delta_i)
        
        print(f"  {delta_i:3d}°    {dv_leo:7.1f}     {dv_geo:7.1f}     {dv_leo/dv_geo:.2f}x")
    
    print(f"\n  Nota: Cambiar plano en órbita baja cuesta {v_leo_circ/v_geo_circ:.1f}x más")
    print(f"        → Siempre hacer cambio de plano en órbita más alta")
    
    # Test 5: Combined maneuver
    print("\n[Test 5] LEO → GEO con cambio de inclinación 28.5°")
    delta_i_test = 28.5
    
    combined = combined_plane_change(r_leo, r_geo, delta_i_test)
    
    print(f"  Hohmann solo: {combined['hohmann_only']:.1f} m/s")
    print(f"  Plano solo:   {combined['plane_change_only']:.1f} m/s")
    print(f"\n  Estrategias combinadas:")
    print(f"    Plano en r1:    {combined['strategy_plane_at_r1']:.1f} m/s")
    print(f"    Plano en r2:    {combined['strategy_plane_at_r2']:.1f} m/s")
    print(f"    Combinado r2:   {combined['strategy_combined_at_r2']:.1f} m/s ← ÓPTIMO")
    print(f"\n  → Mejor estrategia: {combined['optimal_strategy']}")
    print(f"  → ΔV total: {combined['optimal_delta_v']:.1f} m/s")
    print(f"  → Penalización vs Hohmann puro: {combined['penalty_vs_hohmann']:.1f} m/s")
    
# Test 6: Escape velocities
    print("\n[Test 6] Velocidades de Escape")
    
    # Desde varios radios
    radii_test = {
        'Superficie': R_earth,
        'LEO (400 km)': r_leo,
        'GEO': r_geo,
        'Luna': 384400e3
    }
    
    print("  Ubicación          v_circular   v_escape    ΔV escape")
    print("  " + "-"*60)
    
    for name, r in radii_test.items():
        result = delta_v_to_escape(r)
        print(f"  {name:15s}    {result['v_circular']:7.1f}    {result['v_escape']:7.1f}     {result['delta_v']:7.1f}")
    
    print(f"\n  Nota: v_escape = √2 × v_circular")
    print(f"        Factor √2 ≈ 1.414")
    
    # Test 7: Misión interplanetaria (Tierra → Marte)
    print("\n[Test 7] Misión Interplanetaria: Tierra → Marte")
    
    # Órbitas planetarias (valores aproximados)
    r_earth_orbit = 1.496e11   # 1 AU (metros)
    r_mars_orbit = 2.279e11    # 1.524 AU (metros)
    mu_sun = 1.32712440018e20  # m³/s²
    
    mars_mission = interplanetary_hohmann(r_earth_orbit, r_mars_orbit, mu_sun)
    
    print(f"  Órbita Tierra: {r_earth_orbit/1e11:.3f} × 10¹¹ m (1.00 AU)")
    print(f"  Órbita Marte:  {r_mars_orbit/1e11:.3f} × 10¹¹ m (1.52 AU)")
    print(f"\n  ΔV heliocéntrico:")
    print(f"    Salida de Tierra: {mars_mission['delta_v_departure']:.1f} m/s")
    print(f"    Llegada a Marte:  {mars_mission['delta_v_arrival']:.1f} m/s")
    print(f"\n  Velocidades hiperbólicas:")
    print(f"    v∞ salida:  {mars_mission['v_infinity_departure']:.1f} m/s")
    print(f"    v∞ llegada: {mars_mission['v_infinity_arrival']:.1f} m/s")
    print(f"\n  Tiempo de transferencia: {mars_mission['transfer_time_days']:.1f} días")
    
    # ΔV desde LEO
    dv_from_leo = earth_departure_delta_v(mars_mission['v_infinity_departure'])
    print(f"\n  ΔV desde LEO (400 km): {dv_from_leo:.1f} m/s")
    print(f"  (Compara con escape mínimo: {delta_v_to_escape(r_leo)['delta_v']:.1f} m/s)")
    
# Test 8: Phasing maneuvers
    print("\n[Test 8] Maniobras de Phasing (Corrección de Fase)")
    print("\n  Escenario: Satélite está 45° detrás del target en LEO")
    print("  Objetivo: Alcanzarlo usando órbita de phasing\n")
    
    phase_angle_test = 45  # grados
    
    # Probar diferentes números de órbitas
    print("  n_órbitas   r_phasing    Δaltitud   ΔV total   Tiempo")
    print("  " + "-"*65)
    
    for n in [1, 2, 3, 5]:
        result = phasing_orbit(r_leo, phase_angle_test, n_orbits=n)
        
        alt_change = result['altitude_change'] / 1e3  # km
        dv = result['delta_v_total']
        time_h = result['phasing_time'] / 3600
        
        print(f"  {n:5d}       {result['r_phasing']/1e3:7.1f}    {alt_change:+7.1f}     {dv:6.1f}    {time_h:5.1f} h")
    
    print("\n  Nota: Más órbitas = menor ΔV pero más tiempo")
    
    # Optimización automática
    print("\n  Optimización automática (mejor ΔV):")
    optimal_options = optimize_phasing_orbits(r_leo, phase_angle_test, max_orbits=10)
    best = optimal_options[0]
    
    print(f"    Órbitas óptimas: {best['n_orbits_phasing']:.2f}")
    print(f"    ΔV total: {best['delta_v_total']:.1f} m/s")
    print(f"    Tiempo: {best['phasing_time']/3600:.1f} horas")
    
    # Test 9: Rendezvous completo
    print("\n[Test 9] Rendezvous Completo: LEO baja → ISS")
    print("  (Incluye Hohmann + Phasing)\n")
    
    r_departure = 6371e3 + 300e3  # LEO baja (300 km)
    r_iss = 6371e3 + 408e3        # ISS (408 km)
    phase_diff = 120              # 120° detrás
    
    rdv = rendezvous_simple(r_departure, r_iss, phase_diff)
    
    print(f"  Órbita inicial:  {r_departure/1e3:.1f} km")
    print(f"  Órbita ISS:      {r_iss/1e3:.1f} km")
    print(f"  Fase inicial:    {phase_diff}° detrás")
    print(f"\n  PASO 1 - Transfer Hohmann:")
    print(f"    ΔV: {rdv['delta_v_hohmann']:.1f} m/s")
    print(f"    Tiempo: {rdv['time_hohmann']/60:.1f} minutos")
    print(f"\n  PASO 2 - Phasing (corrección de fase):")
    print(f"    Órbitas: {rdv['phasing']['n_orbits_phasing']:.2f}")
    print(f"    ΔV: {rdv['delta_v_phasing']:.1f} m/s")
    print(f"    Tiempo: {rdv['time_phasing']/3600:.1f} horas")
    print(f"\n  TOTAL:")
    print(f"    ΔV: {rdv['delta_v_total']:.1f} m/s")
    print(f"    Tiempo: {rdv['time_total']/3600:.1f} horas")
    
    # Test 10: Comparación con casos reales
    print("\n[Test 10] Comparación con Misiones Reales")
    print("\n  Misión              ΔV calculado   ΔV real    Nota")
    print("  " + "-"*70)
    
    # Space Shuttle → ISS
    shuttle_dv = rendezvous_simple(r_departure, r_iss, 45)['delta_v_total']
    print(f"  Shuttle → ISS       {shuttle_dv:7.1f} m/s    ~150 m/s   (simplificado)")
    
    # Dragon → ISS
    dragon_dv = rendezvous_simple(r_departure, r_iss, 90)['delta_v_total']
    print(f"  Dragon → ISS        {dragon_dv:7.1f} m/s    ~100 m/s   (simplificado)")
    
    print("\n  Nota: Valores reales menores porque:")
    print("    • Optimización de trayectoria")
    print("    • Phasing durante transfer (no después)")
    print("    • Aprovechamiento de perturbaciones (J2)")
    


    # Test 11: Rendezvous realista (con constraint de tiempo)
    print("\n[Test 11] Rendezvous Realista (24 horas disponibles)")
    
    rdv_real = rendezvous_realistic(r_departure, r_iss, 120, time_available_hours=24)
    
    if rdv_real['feasible']:
        print(f"  Tiempo total: {rdv_real['time_total_hours']:.1f} horas")
        print(f"  ΔV total: {rdv_real['delta_v_total']:.1f} m/s")
        print(f"  Phasing: {rdv_real['phasing']['delta_v_total']:.1f} m/s ({rdv_real['phasing']['n_orbits_phasing']:.1f} órbitas)")
        print(f"\n  → Más realista que optimización pura de ΔV")



    
    print("\n" + "="*70)
    print("✓ Módulo delta_v.py - Sección 1-5 completa")
    print("  [✓] Hohmann transfers")
    print("  [✓] Bi-elliptic transfers")
    print("  [✓] Plane changes")
    print("  [✓] Escape & Interplanetary")
    print("  [✓] Phasing & Rendezvous")
    print("="*70)


