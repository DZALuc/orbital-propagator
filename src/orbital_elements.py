"""
Módulo de Elementos Orbitales Keplerianos

Conversión entre coordenadas Cartesianas y elementos orbitales.
Incluye cálculos de parámetros orbitales derivados.

Author: Damián Zúñiga Avelar
Date: April 2026
"""

import numpy as np


def cartesian_to_keplerian(r_vec, v_vec, mu=3.986004418e14):
    """
    Convierte estado Cartesiano a elementos orbitales Keplerianos.
    
    Parameters
    ----------
    r_vec : array_like, shape (3,)
        Vector de posición [x, y, z] en metros
    v_vec : array_like, shape (3,)
        Vector de velocidad [vx, vy, vz] en m/s
    mu : float, optional
        Parámetro gravitacional en m³/s² (default: Tierra)
    
    Returns
    -------
    elements : dict
        Diccionario con elementos orbitales:
        - a: semieje mayor (m)
        - e: excentricidad (adimensional)
        - i: inclinación (radianes)
        - RAAN: ascensión recta del nodo ascendente (radianes)
        - omega: argumento del perigeo (radianes)
        - nu: anomalía verdadera (radianes)
        - h: momento angular específico (m²/s)
        - energy: energía específica (J/kg)
    
    Notes
    -----
    Implementa el algoritmo estándar de Curtis (2013).
    Maneja casos especiales: órbitas circulares y ecuatoriales.
    Incluye protección contra errores numéricos en arccos.
    
    References
    ----------
    Curtis, H. (2013). Orbital Mechanics for Engineering Students, 3rd ed.
    """
    
    def safe_arccos(x):
        """Arccos seguro que maneja errores de redondeo."""
        return np.arccos(np.clip(x, -1.0, 1.0))
    
    # Magnitudes
    r = np.linalg.norm(r_vec)
    v = np.linalg.norm(v_vec)
    
    # Vector de momento angular específico: h = r × v
    h_vec = np.cross(r_vec, v_vec)
    h = np.linalg.norm(h_vec)
    
    # Vector del nodo: N = k × h (apunta hacia nodo ascendente)
    k = np.array([0, 0, 1])  # Vector unitario en Z
    N_vec = np.cross(k, h_vec)
    N = np.linalg.norm(N_vec)
    
    # Vector de excentricidad: e = (1/μ)[(v² - μ/r)r - (r·v)v]
    e_vec = (1/mu) * ((v**2 - mu/r) * r_vec - np.dot(r_vec, v_vec) * v_vec)
    e = np.linalg.norm(e_vec)
    
    # Energía específica: ε = v²/2 - μ/r
    energy = (v**2) / 2 - mu / r
    
    # Semieje mayor: a = -μ/(2ε)
    # Para órbitas parabólicas (e=1), a es infinito
    if abs(e - 1.0) > 1e-10:  # No es parabólica
        a = -mu / (2 * energy)
    else:
        a = np.inf
    
    # Inclinación: i = arccos(hz/h)
    i = safe_arccos(h_vec[2] / h)
    
    # Ascensión recta del nodo ascendente (RAAN): Ω = arccos(Nx/N)
    if N > 1e-10:  # Órbita no ecuatorial
        RAAN = safe_arccos(N_vec[0] / N)
        # Cuadrante: si Ny < 0, entonces Ω está en [π, 2π]
        if N_vec[1] < 0:
            RAAN = 2 * np.pi - RAAN
    else:
        # Órbita ecuatorial: RAAN no definido, usar 0
        RAAN = 0.0
    
    # Argumento del perigeo: ω = arccos(N·e / (N*e))
    if e > 1e-10:  # Órbita no circular
        if N > 1e-10:  # No ecuatorial
            omega = safe_arccos(np.dot(N_vec, e_vec) / (N * e))
            # Cuadrante: si ez < 0, ω está en [π, 2π]
            if e_vec[2] < 0:
                omega = 2 * np.pi - omega
        else:
            # Órbita ecuatorial: ω medido desde dirección X
            omega = safe_arccos(e_vec[0] / e)
            if e_vec[1] < 0:
                omega = 2 * np.pi - omega
    else:
        # Órbita circular: ω no definido, usar 0
        omega = 0.0
    
    # Anomalía verdadera: ν = arccos(e·r / (e*r))
    if e > 1e-10:  # Órbita no circular
        nu = safe_arccos(np.dot(e_vec, r_vec) / (e * r))
        # Cuadrante: si r·v < 0, estamos después del apogeo
        if np.dot(r_vec, v_vec) < 0:
            nu = 2 * np.pi - nu
    else:
        # Órbita circular: ν medido desde nodo ascendente (o desde X si ecuatorial)
        if N > 1e-10:  # No ecuatorial
            nu = safe_arccos(np.dot(N_vec, r_vec) / (N * r))
            if r_vec[2] < 0:
                nu = 2 * np.pi - nu
        else:
            # Ecuatorial y circular
            nu = safe_arccos(r_vec[0] / r)
            if r_vec[1] < 0:
                nu = 2 * np.pi - nu
    
    return {
        'a': a,
        'e': e,
        'i': i,
        'RAAN': RAAN,
        'omega': omega,
        'nu': nu,
        'h': h,
        'energy': energy
    }


def keplerian_to_cartesian(a, e, i, RAAN, omega, nu, mu=3.986004418e14):
    """
    Convierte elementos orbitales Keplerianos a estado Cartesiano.
    
    Parameters
    ----------
    a : float
        Semieje mayor (m)
    e : float
        Excentricidad (adimensional)
    i : float
        Inclinación (radianes)
    RAAN : float
        Ascensión recta del nodo ascendente (radianes)
    omega : float
        Argumento del perigeo (radianes)
    nu : float
        Anomalía verdadera (radianes)
    mu : float, optional
        Parámetro gravitacional (default: Tierra)
    
    Returns
    -------
    r_vec : ndarray, shape (3,)
        Vector de posición [x, y, z] en metros
    v_vec : ndarray, shape (3,)
        Vector de velocidad [vx, vy, vz] en m/s
    
    Notes
    -----
    Usa el sistema de coordenadas perifocales como paso intermedio.
    
    Referencias
    -----------
    Curtis, H. (2013). Orbital Mechanics for Engineering Students.
    """
    # Parámetro orbital: p = a(1 - e²)
    p = a * (1 - e**2)
    
    # Radio actual: r = p / (1 + e*cos(ν))
    r = p / (1 + e * np.cos(nu))
    
    # Posición en sistema perifocal
    r_pqw = np.array([
        r * np.cos(nu),
        r * np.sin(nu),
        0.0
    ])
    
    # Velocidad en sistema perifocal
    v_pqw = np.array([
        -np.sqrt(mu / p) * np.sin(nu),
        np.sqrt(mu / p) * (e + np.cos(nu)),
        0.0
    ])
    
    # Matriz de rotación de perifocal a geocéntrico ecuatorial
    # R = R3(-RAAN) * R1(-i) * R3(-omega)
    
    cos_RAAN = np.cos(RAAN)
    sin_RAAN = np.sin(RAAN)
    cos_i = np.cos(i)
    sin_i = np.sin(i)
    cos_omega = np.cos(omega)
    sin_omega = np.sin(omega)
    
    # Matriz de rotación completa
    R = np.array([
        [cos_RAAN*cos_omega - sin_RAAN*sin_omega*cos_i,
         -cos_RAAN*sin_omega - sin_RAAN*cos_omega*cos_i,
         sin_RAAN*sin_i],
        
        [sin_RAAN*cos_omega + cos_RAAN*sin_omega*cos_i,
         -sin_RAAN*sin_omega + cos_RAAN*cos_omega*cos_i,
         -cos_RAAN*sin_i],
        
        [sin_omega*sin_i,
         cos_omega*sin_i,
         cos_i]
    ])
    
    # Transformar al sistema geocéntrico
    r_vec = R @ r_pqw
    v_vec = R @ v_pqw
    
    return r_vec, v_vec


def print_orbital_elements(elements, degrees=True):
    """
    Imprime elementos orbitales de forma legible.
    
    Parameters
    ----------
    elements : dict
        Diccionario de elementos orbitales de cartesian_to_keplerian()
    degrees : bool, optional
        Si True, muestra ángulos en grados; si False, en radianes (default: True)
    """
    a = elements['a']
    e = elements['e']
    i = elements['i']
    RAAN = elements['RAAN']
    omega = elements['omega']
    nu = elements['nu']
    h = elements['h']
    energy = elements['energy']
    
    # Factor de conversión
    to_deg = np.degrees if degrees else lambda x: x
    unit = "°" if degrees else "rad"
    
    print("\nElementos Orbitales Keplerianos:")
    print("-" * 50)
    
    # Tamaño y forma
    print(f"  Semieje mayor (a):        {a/1e3:12.3f} km")
    print(f"  Excentricidad (e):        {e:12.6f}")
    
    # Tipo de órbita
    if e < 0.01:
        orbit_type = "Circular"
    elif e < 1.0:
        orbit_type = "Elíptica"
    elif abs(e - 1.0) < 1e-6:
        orbit_type = "Parabólica"
    else:
        orbit_type = "Hiperbólica"
    print(f"  Tipo de órbita:           {orbit_type}")
    
    # Orientación
    print(f"  Inclinación (i):          {to_deg(i):12.4f} {unit}")
    print(f"  RAAN (Ω):                 {to_deg(RAAN):12.4f} {unit}")
    print(f"  Arg. perigeo (ω):         {to_deg(omega):12.4f} {unit}")
    
    # Posición en órbita
    print(f"  Anomalía verdadera (ν):   {to_deg(nu):12.4f} {unit}")
    
    # Parámetros derivados
    print(f"\n  Momento angular (h):      {h:.6e} m²/s")
    print(f"  Energía específica (ε):   {energy:.2f} J/kg")
    
    # Si es elíptica, calcular perigeo y apogeo
    if e < 1.0 and e > 1e-10:
        rp = a * (1 - e)
        ra = a * (1 + e)
        print(f"\n  Radio perigeo:            {rp/1e3:12.3f} km")
        print(f"  Radio apogeo:             {ra/1e3:12.3f} km")
    
    print("-" * 50)


def orbital_period_from_elements(a, mu=3.986004418e14):
    """
    Calcula periodo orbital desde semieje mayor.
    
    Parameters
    ----------
    a : float
        Semieje mayor (m)
    mu : float, optional
        Parámetro gravitacional
    
    Returns
    -------
    T : float
        Periodo orbital (segundos)
    """
    T = 2 * np.pi * np.sqrt(a**3 / mu)
    return T