"""
Mission Database

Base de datos de órbitas, misiones y cuerpos celestes comunes.

Author: Damián Zúñiga Avelar
Date: Abril 2026
"""

import numpy as np
from astropy import constants as const

# ============================================================================
# CONSTANTES FÍSICAS
# ============================================================================

# Tierra
GM_earth = const.GM_earth.value  # m³/s²
R_earth = 6371000  # m
J2_earth = 1.08263e-3

# Luna
GM_moon = 4.9048695e12  # m³/s²
R_moon = 1737400  # m

# Sol
GM_sun = const.GM_sun.value
R_sun = 696000000  # m

# Marte
GM_mars = 4.282837e13  # m³/s²
R_mars = 3389500  # m

# Venus
GM_venus = 3.24859e14  # m³/s²
R_venus = 6051800  # m

# Júpiter
GM_jupiter = 1.26686534e17  # m³/s²
R_jupiter = 69911000  # m


# ============================================================================
# ÓRBITAS TERRESTRES COMUNES
# ============================================================================

ORBITS_EARTH = {
    'LEO_low': {
        'name': 'Low Earth Orbit (bajo)',
        'altitude_km': 200,
        'radius_m': R_earth + 200e3,
        'description': 'Órbita mínima sostenible (alta resistencia)'
    },
    
    'LEO_typical': {
        'name': 'LEO típico',
        'altitude_km': 400,
        'radius_m': R_earth + 400e3,
        'description': 'Altitud común para satélites y estaciones'
    },
    
    'ISS': {
        'name': 'International Space Station',
        'altitude_km': 408,
        'radius_m': R_earth + 408e3,
        'inclination_deg': 51.6,
        'description': 'Estación Espacial Internacional'
    },
    
    'Starlink': {
        'name': 'Starlink operational',
        'altitude_km': 550,
        'radius_m': R_earth + 550e3,
        'inclination_deg': 53.0,
        'description': 'Órbita operacional Starlink'
    },
    
    'Polar_SSO': {
        'name': 'Sun-Synchronous Orbit',
        'altitude_km': 800,
        'radius_m': R_earth + 800e3,
        'inclination_deg': 98.6,
        'description': 'Órbita polar heliosincrónica (observación Tierra)'
    },
    
    'MEO_GPS': {
        'name': 'GPS constellation',
        'altitude_km': 20200,
        'radius_m': R_earth + 20200e3,
        'inclination_deg': 55.0,
        'description': 'Órbita GPS (MEO)'
    },
    
    'GEO': {
        'name': 'Geostationary Orbit',
        'altitude_km': 35786,
        'radius_m': R_earth + 35786e3,
        'inclination_deg': 0.0,
        'description': 'Órbita geoestacionaria (periodo = 24h)'
    },
    
    'Molniya': {
        'name': 'Molniya orbit',
        'periapsis_km': 548,
        'apoapsis_km': 39931,
        'semi_major_km': 26610,
        'eccentricity': 0.74,
        'inclination_deg': 63.4,
        'period_hours': 12.0,
        'description': 'Órbita altamente elíptica rusa (2 pases/día)'
    },
    
    'Tundra': {
        'name': 'Tundra orbit',
        'periapsis_km': 24000,
        'apoapsis_km': 47000,
        'inclination_deg': 63.4,
        'period_hours': 24.0,
        'description': 'Órbita elíptica (periodo 24h)'
    },
    
    'Lunar_transfer': {
        'name': 'Lunar transfer orbit',
        'periapsis_km': 400,
        'apoapsis_km': 384400,
        'description': 'Órbita de transferencia a la Luna'
    }
}


# ============================================================================
# ÓRBITAS PLANETARIAS (HELIOCÉNTRICAS)
# ============================================================================

PLANETS = {
    'Mercury': {
        'name': 'Mercurio',
        'semi_major_au': 0.387,
        'semi_major_m': 5.791e10,
        'period_days': 88,
        'GM': 2.2032e13
    },
    
    'Venus': {
        'name': 'Venus',
        'semi_major_au': 0.723,
        'semi_major_m': 1.082e11,
        'period_days': 225,
        'GM': GM_venus
    },
    
    'Earth': {
        'name': 'Tierra',
        'semi_major_au': 1.000,
        'semi_major_m': 1.496e11,
        'period_days': 365.25,
        'GM': GM_earth
    },
    
    'Mars': {
        'name': 'Marte',
        'semi_major_au': 1.524,
        'semi_major_m': 2.279e11,
        'period_days': 687,
        'GM': GM_mars
    },
    
    'Jupiter': {
        'name': 'Júpiter',
        'semi_major_au': 5.203,
        'semi_major_m': 7.786e11,
        'period_days': 4333,
        'GM': GM_jupiter
    }
}


# ============================================================================
# MISIONES REALES HISTÓRICAS
# ============================================================================

MISSIONS = {
    'Apollo_11': {
        'name': 'Apollo 11',
        'year': 1969,
        'departure': 'LEO (185 km)',
        'destination': 'Lunar surface',
        'delta_v_total_km_s': 5.93,
        'description': 'Primera misión tripulada a la Luna'
    },
    
    'Space_Shuttle': {
        'name': 'Space Shuttle',
        'years': '1981-2011',
        'orbit': 'LEO (300-600 km)',
        'delta_v_capability_km_s': 0.3,
        'description': 'Transbordador espacial reutilizable'
    },
    
    'ISS_assembly': {
        'name': 'ISS assembly missions',
        'typical_delta_v_km_s': 0.15,
        'description': 'Rendezvous típico con ISS desde LEO'
    },
    
    'Voyager': {
        'name': 'Voyager 1 & 2',
        'year': 1977,
        'delta_v_earth_escape_km_s': 3.5,
        'trajectory': 'Gravity assists (Jupiter, Saturn, etc.)',
        'description': 'Misiones interestelares con asistencias gravitatorias'
    },
    
    'New_Horizons': {
        'name': 'New Horizons',
        'year': 2006,
        'destination': 'Pluto',
        'launch_delta_v_km_s': 16.26,
        'description': 'Lanzamiento más rápido de la historia'
    },
    
    'Dawn': {
        'name': 'Dawn',
        'year': 2007,
        'propulsion': 'Ion electric (Isp=3100s)',
        'delta_v_total_km_s': 11.0,
        'destinations': 'Vesta, Ceres',
        'description': 'Primera misión iónica a asteroides'
    },
    
    'BepiColombo': {
        'name': 'BepiColombo',
        'year': 2018,
        'destination': 'Mercury',
        'propulsion': 'Ion electric (4x T6)',
        'delta_v_total_km_s': '~15',
        'travel_time_years': 7,
        'description': 'ESA/JAXA misión a Mercurio con propulsión eléctrica'
    },
    
    'Starlink_deployment': {
        'name': 'Starlink satellite',
        'deployment_altitude_km': 350,
        'operational_altitude_km': 550,
        'delta_v_orbit_raising_m_s': 250,
        'propulsion': 'Hall thruster',
        'description': 'Satélites Starlink con Hall thrusters'
    },
    
    'Mars_Science_Laboratory': {
        'name': 'Curiosity rover (MSL)',
        'year': 2011,
        'delta_v_earth_mars_km_s': 2.95,
        'travel_time_days': 254,
        'description': 'Rover Curiosity a Marte'
    }
}


# ============================================================================
# DELTA-V BUDGETS TÍPICOS
# ============================================================================

DELTA_V_BUDGETS = {
    'LEO_to_GEO': {
        'delta_v_hohmann_m_s': 3857,
        'delta_v_low_thrust_m_s': 4000,
        'time_hohmann_hours': 5.3,
        'time_low_thrust_days': 32,
        'description': 'Transfer LEO (400 km) → GEO'
    },
    
    'LEO_to_Moon_surface': {
        'delta_v_total_m_s': 5930,
        'breakdown': {
            'LEO_escape': 3200,
            'Lunar_orbit_insertion': 900,
            'Descent': 1830
        },
        'description': 'LEO a superficie lunar (Apollo-style)'
    },
    
    'LEO_to_Mars_surface': {
        'delta_v_total_m_s': 9600,
        'breakdown': {
            'Earth_departure': 3600,
            'Mars_orbit_insertion': 2100,
            'Mars_descent': 3900
        },
        'description': 'LEO a superficie Marte (one-way)'
    },
    
    'Earth_to_Mars_Hohmann': {
        'delta_v_heliocentric_m_s': 5594,
        'travel_time_days': 259,
        'launch_window_days': 780,
        'description': 'Transferencia Hohmann Tierra-Marte'
    },
    
    'Plane_change_LEO': {
        '1_degree_m_s': 134,
        '10_degrees_m_s': 1338,
        '28_5_degrees_m_s': 3777,
        '90_degrees_m_s': 10851,
        'description': 'Cambios de inclinación en LEO (400 km)'
    }
}


# ============================================================================
# PROPULSION SYSTEMS
# ============================================================================

PROPULSION_SYSTEMS = {
    'Chemical_RL10': {
        'name': 'RL-10 (upper stage)',
        'type': 'Chemical (LH2/LOX)',
        'thrust_N': 110000,
        'isp_s': 450,
        'description': 'Motor criogénico de etapa superior'
    },
    
    'Chemical_Merlin': {
        'name': 'Merlin 1D (Falcon 9)',
        'type': 'Chemical (RP-1/LOX)',
        'thrust_N': 845000,
        'isp_s': 282,
        'description': 'Motor Falcon 9 primer etapa'
    },
    
    'Hall_SPT100': {
        'name': 'SPT-100 Hall thruster',
        'type': 'Electric (Hall effect)',
        'thrust_mN': 83,
        'isp_s': 1600,
        'power_kW': 1.35,
        'description': 'Hall thruster ruso estándar'
    },
    
    'Ion_NSTAR': {
        'name': 'NSTAR ion engine',
        'type': 'Electric (Ion)',
        'thrust_mN': 92,
        'isp_s': 3100,
        'power_kW': 2.3,
        'description': 'Motor iónico de Dawn mission'
    },
    
    'Hall_Starlink': {
        'name': 'Starlink Hall thruster',
        'type': 'Electric (Hall)',
        'thrust_mN': 200,
        'isp_s': 2000,
        'description': 'Hall thruster de satélites Starlink'
    },
    
    'Monoprop_Hydrazine': {
        'name': 'Hydrazine monopropellant',
        'type': 'Chemical (monoprop)',
        'isp_s': 220,
        'description': 'Monopropelente para maniobras pequeñas'
    }
}


# ============================================================================
# FUNCIONES DE ACCESO
# ============================================================================

def get_orbit(orbit_name):
    """Obtener información de órbita por nombre."""
    if orbit_name in ORBITS_EARTH:
        return ORBITS_EARTH[orbit_name]
    else:
        available = ', '.join(ORBITS_EARTH.keys())
        raise ValueError(f"Órbita '{orbit_name}' no encontrada. Disponibles: {available}")


def get_planet(planet_name):
    """Obtener información de planeta por nombre."""
    if planet_name in PLANETS:
        return PLANETS[planet_name]
    else:
        available = ', '.join(PLANETS.keys())
        raise ValueError(f"Planeta '{planet_name}' no encontrado. Disponibles: {available}")


def get_mission(mission_name):
    """Obtener información de misión por nombre."""
    if mission_name in MISSIONS:
        return MISSIONS[mission_name]
    else:
        available = ', '.join(MISSIONS.keys())
        raise ValueError(f"Misión '{mission_name}' no encontrada. Disponibles: {available}")


def list_orbits():
    """Listar todas las órbitas disponibles."""
    print("\nÓRBITAS TERRESTRES DISPONIBLES:")
    print("=" * 70)
    for key, orbit in ORBITS_EARTH.items():
        print(f"\n{key}:")
        print(f"  Nombre: {orbit['name']}")
        if 'altitude_km' in orbit:
            print(f"  Altitud: {orbit['altitude_km']} km")
        if 'inclination_deg' in orbit:
            print(f"  Inclinación: {orbit['inclination_deg']}°")
        print(f"  Descripción: {orbit['description']}")


def list_missions():
    """Listar todas las misiones disponibles."""
    print("\nMISIONES HISTÓRICAS:")
    print("=" * 70)
    for key, mission in MISSIONS.items():
        print(f"\n{key}:")
        print(f"  {mission['name']}")
        print(f"  {mission['description']}")


def list_propulsion():
    """Listar sistemas de propulsión."""
    print("\nSISTEMAS DE PROPULSIÓN:")
    print("=" * 70)
    for key, prop in PROPULSION_SYSTEMS.items():
        print(f"\n{key}:")
        print(f"  {prop['name']} ({prop['type']})")
        if 'thrust_N' in prop:
            print(f"  Empuje: {prop['thrust_N']/1000:.1f} kN")
        if 'thrust_mN' in prop:
            print(f"  Empuje: {prop['thrust_mN']:.1f} mN")
        print(f"  Isp: {prop['isp_s']} s")


if __name__ == "__main__":
    print("\n" + "="*70)
    print(" "*20 + "MISSION DATABASE")
    print("="*70)
    
    list_orbits()
    print("\n" + "─"*70)
    list_missions()
    print("\n" + "─"*70)
    list_propulsion()
    
    print("\n" + "="*70)
    print("✓ Base de datos cargada")
    print("="*70 + "\n")