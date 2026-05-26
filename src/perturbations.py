"""
Orbital Perturbations

Implementación de fuerzas perturbadoras orbitales.

Author: Damián Zúñiga Avelar
Date: Mayo 2026
"""

import numpy as np


# Constantes
MU_EARTH = 398600.4418  # km³/s²
R_EARTH = 6371.0  # km
J2 = 1.08263e-3  # Coeficiente J2
RHO_0 = 1.225  # kg/m³ (densidad atmosférica a nivel del mar)
H_SCALE = 8.5  # km (escala de altura atmosférica)
P_SOLAR = 4.56e-6  # N/m² (presión radiación solar a 1 AU)
C_LIGHT = 299792.458  # km/s


def j2_acceleration(r_vec, mu=MU_EARTH, j2=J2, R=R_EARTH):
    """
    Calcula aceleración debida a J2 (oblateness terrestre).
    
    La Tierra no es una esfera perfecta, está achatada en los polos.
    Esto causa precesión de la línea de nodos y del argumento del periapsis.
    
    Parameters
    ----------
    r_vec : array_like
        Vector posición [x, y, z] (km)
    mu : float
        Parámetro gravitacional (km³/s²)
    j2 : float
        Coeficiente J2
    R : float
        Radio ecuatorial (km)
    
    Returns
    -------
    a_j2 : ndarray
        Vector aceleración J2 [ax, ay, az] (km/s²)
    
    Notes
    -----
    Ecuación:
    a_J2 = -(3/2) * (μ * J2 * R²) / r⁵ * 
           [(1 - 5(z/r)²) * x,
            (1 - 5(z/r)²) * y,
            (3 - 5(z/r)²) * z]
    """
    
    r_vec = np.array(r_vec, dtype=float)
    x, y, z = r_vec
    
    r = np.linalg.norm(r_vec)
    
    if r == 0:
        return np.zeros(3)
    
    # Factor común
    factor = -(3.0/2.0) * (mu * j2 * R**2) / r**5
    
    # Componentes
    z_r_sq = (z / r)**2
    
    ax = factor * (1 - 5*z_r_sq) * x
    ay = factor * (1 - 5*z_r_sq) * y
    az = factor * (3 - 5*z_r_sq) * z
    
    return np.array([ax, ay, az])


def atmospheric_drag_acceleration(r_vec, v_vec, Cd=2.2, A_m=0.01, rho_0=RHO_0, H=H_SCALE):
    """
    Calcula aceleración debida a drag atmosférico.
    
    El drag reduce la energía orbital, causando decay de la órbita.
    Es más significativo en LEO.
    
    Parameters
    ----------
    r_vec : array_like
        Vector posición [x, y, z] (km)
    v_vec : array_like
        Vector velocidad [vx, vy, vz] (km/s)
    Cd : float
        Coeficiente de drag (típico: 2.0-2.5)
    A_m : float
        Área/masa del satélite (m²/kg)
        Típico: CubeSat ~0.01, Satélite grande ~0.001
    rho_0 : float
        Densidad atmosférica a nivel del mar (kg/m³)
    H : float
        Escala de altura atmosférica (km)
    
    Returns
    -------
    a_drag : ndarray
        Vector aceleración drag [ax, ay, az] (km/s²)
    
    Notes
    -----
    Ecuación:
    a_drag = -(1/2) * Cd * (A/m) * ρ * v * v̂
    
    Modelo exponencial de atmósfera:
    ρ(h) = ρ₀ * exp(-h/H)
    """
    
    r_vec = np.array(r_vec, dtype=float)
    v_vec = np.array(v_vec, dtype=float)
    
    r = np.linalg.norm(r_vec)
    v = np.linalg.norm(v_vec)
    
    if v == 0:
        return np.zeros(3)
    
    # Altitud
    h = r - R_EARTH
    
    # Densidad atmosférica (modelo exponencial simplificado)
    if h < 0:
        h = 0
    
    rho = rho_0 * np.exp(-h / H)
    
    # Aceleración drag
    # Factor: -(1/2) * Cd * (A/m) * ρ * v
    # Conversión: km → m para consistencia
    factor = -0.5 * Cd * A_m * rho * v * 1000  # 1000 para convertir km/s a m/s en cálculo
    
    # Dirección: opuesta a la velocidad
    v_hat = v_vec / v
    
    a_drag = (factor * v_hat) / 1e6  # Convertir de m/s² a km/s²
    
    return a_drag


def solar_radiation_pressure_acceleration(r_vec, r_sun_vec, Cr=1.5, A_m=0.01, 
                                          P=P_SOLAR, in_shadow=False):
    """
    Calcula aceleración debida a presión de radiación solar.
    
    La luz solar ejerce presión sobre el satélite.
    Efecto pequeño pero acumulativo, importante para misiones largas.
    
    Parameters
    ----------
    r_vec : array_like
        Vector posición satélite [x, y, z] (km)
    r_sun_vec : array_like
        Vector posición Sol [x, y, z] (km)
    Cr : float
        Coeficiente de reflectividad (1.0-2.0)
        1.0 = absorción total, 2.0 = reflexión especular
    A_m : float
        Área/masa (m²/kg)
    P : float
        Presión radiación solar (N/m²)
    in_shadow : bool
        Si el satélite está en sombra de la Tierra
    
    Returns
    -------
    a_srp : ndarray
        Vector aceleración SRP [ax, ay, az] (km/s²)
    
    Notes
    -----
    Ecuación:
    a_srp = -Cr * (A/m) * P * ŝ
    
    donde ŝ es el vector unitario del Sol al satélite.
    """
    
    if in_shadow:
        return np.zeros(3)
    
    r_vec = np.array(r_vec, dtype=float)
    r_sun_vec = np.array(r_sun_vec, dtype=float)
    
    # Vector del Sol al satélite
    r_sat_sun = r_vec - r_sun_vec
    
    dist = np.linalg.norm(r_sat_sun)
    
    if dist == 0:
        return np.zeros(3)
    
    # Vector unitario
    s_hat = r_sat_sun / dist
    
    # Aceleración
    # P está en N/m², necesitamos km/s²
    factor = -Cr * A_m * P  # N/kg = m/s²
    
    a_srp = (factor * s_hat) / 1e6  # m/s² a km/s²
    
    return a_srp


def check_earth_shadow(r_sat, r_sun):
    """
    Verifica si el satélite está en la sombra de la Tierra.
    
    Modelo simplificado: sombra cilíndrica.
    
    Parameters
    ----------
    r_sat : array_like
        Posición satélite [x, y, z] (km)
    r_sun : array_like
        Posición Sol [x, y, z] (km)
    
    Returns
    -------
    in_shadow : bool
        True si está en sombra
    """
    
    r_sat = np.array(r_sat, dtype=float)
    r_sun = np.array(r_sun, dtype=float)
    
    # Vector del Sol al satélite
    r_rel = r_sat - r_sun
    
    # Si el satélite está del mismo lado del Sol que la Tierra, no hay sombra
    if np.dot(r_sat, r_sun) > 0:
        return False
    
    # Distancia perpendicular del satélite a la línea Sol-Tierra
    sun_dir = r_sun / np.linalg.norm(r_sun)
    
    # Proyección del satélite sobre línea Sol-Tierra
    proj = np.dot(r_sat, sun_dir)
    
    # Vector perpendicular
    r_perp = r_sat - proj * sun_dir
    
    # Distancia perpendicular
    d_perp = np.linalg.norm(r_perp)
    
    # Si la distancia perpendicular es menor que el radio de la Tierra, está en sombra
    return d_perp < R_EARTH


def total_perturbation_acceleration(r_vec, v_vec, r_sun_vec=None, 
                                   include_j2=True, include_drag=True, 
                                   include_srp=False, **kwargs):
    """
    Calcula aceleración total de todas las perturbaciones.
    
    Parameters
    ----------
    r_vec : array_like
        Posición [x, y, z] (km)
    v_vec : array_like
        Velocidad [vx, vy, vz] (km/s)
    r_sun_vec : array_like, optional
        Posición del Sol [x, y, z] (km)
    include_j2 : bool
        Incluir J2
    include_drag : bool
        Incluir drag atmosférico
    include_srp : bool
        Incluir presión radiación solar
    **kwargs : dict
        Parámetros adicionales (Cd, A_m, Cr, etc.)
    
    Returns
    -------
    a_total : ndarray
        Aceleración total [ax, ay, az] (km/s²)
    components : dict
        Componentes individuales
    """
    
    a_total = np.zeros(3)
    components = {}
    
    if include_j2:
        a_j2 = j2_acceleration(r_vec)
        a_total += a_j2
        components['j2'] = a_j2
    else:
        components['j2'] = np.zeros(3)
    
    if include_drag:
        Cd = kwargs.get('Cd', 2.2)
        A_m = kwargs.get('A_m', 0.01)
        a_drag = atmospheric_drag_acceleration(r_vec, v_vec, Cd=Cd, A_m=A_m)
        a_total += a_drag
        components['drag'] = a_drag
    else:
        components['drag'] = np.zeros(3)
    
    if include_srp and r_sun_vec is not None:
        Cr = kwargs.get('Cr', 1.5)
        A_m = kwargs.get('A_m', 0.01)
        
        in_shadow = check_earth_shadow(r_vec, r_sun_vec)
        
        a_srp = solar_radiation_pressure_acceleration(
            r_vec, r_sun_vec, Cr=Cr, A_m=A_m, in_shadow=in_shadow
        )
        a_total += a_srp
        components['srp'] = a_srp
    else:
        components['srp'] = np.zeros(3)
    
    return a_total, components


def propagate_with_perturbations(r0, v0, dt, duration, 
                                 include_j2=True, include_drag=True, 
                                 include_srp=False, **kwargs):
    """
    Propaga órbita con perturbaciones usando RK4.
    
    Parameters
    ----------
    r0 : array_like
        Posición inicial [x, y, z] (km)
    v0 : array_like
        Velocidad inicial [vx, vy, vz] (km/s)
    dt : float
        Paso de tiempo (s)
    duration : float
        Duración total (s)
    include_j2 : bool
        Incluir J2
    include_drag : bool
        Incluir drag
    include_srp : bool
        Incluir SRP
    **kwargs : dict
        Parámetros (Cd, A_m, Cr, etc.)
    
    Returns
    -------
    trajectory : dict
        't': tiempos
        'r': posiciones
        'v': velocidades
        'perturbations': fuerzas por componente
    """
    
    r0 = np.array(r0, dtype=float)
    v0 = np.array(v0, dtype=float)
    
    n_steps = int(duration / dt)
    
    times = np.zeros(n_steps)
    positions = np.zeros((n_steps, 3))
    velocities = np.zeros((n_steps, 3))
    
    perturb_j2 = np.zeros((n_steps, 3))
    perturb_drag = np.zeros((n_steps, 3))
    perturb_srp = np.zeros((n_steps, 3))
    
    # Estado inicial
    r = r0.copy()
    v = v0.copy()
    
    positions[0] = r
    velocities[0] = v
    
    # Posición del Sol (simplificado: fijo en X positivo)
    r_sun = np.array([149597870.7, 0, 0])  # 1 AU en km
    
    for i in range(1, n_steps):
        # RK4 integrator
        def derivatives(r, v):
            # Gravedad puntual
            r_norm = np.linalg.norm(r)
            a_grav = -MU_EARTH * r / r_norm**3
            
            # Perturbaciones
            a_pert, comps = total_perturbation_acceleration(
                r, v, r_sun, include_j2, include_drag, include_srp, **kwargs
            )
            
            a_total = a_grav + a_pert
            
            return v, a_total, comps
        
        # RK4
        k1_v, k1_a, c1 = derivatives(r, v)
        k2_v, k2_a, c2 = derivatives(r + 0.5*dt*k1_v, v + 0.5*dt*k1_a)
        k3_v, k3_a, c3 = derivatives(r + 0.5*dt*k2_v, v + 0.5*dt*k2_a)
        k4_v, k4_a, c4 = derivatives(r + dt*k3_v, v + dt*k3_a)
        
        r = r + (dt/6.0) * (k1_v + 2*k2_v + 2*k3_v + k4_v)
        v = v + (dt/6.0) * (k1_a + 2*k2_a + 2*k3_a + k4_a)
        
        times[i] = i * dt
        positions[i] = r
        velocities[i] = v
        
        # Guardar componentes de perturbación
        perturb_j2[i] = c1['j2']
        perturb_drag[i] = c1['drag']
        perturb_srp[i] = c1['srp']
    
    return {
        't': times,
        'r': positions,
        'v': velocities,
        'perturbations': {
            'j2': perturb_j2,
            'drag': perturb_drag,
            'srp': perturb_srp
        }
    }