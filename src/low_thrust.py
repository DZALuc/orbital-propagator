"""
Low-Thrust Trajectory Optimization

Propagación y optimización de trayectorias con propulsión eléctrica
(bajo empuje continuo).

Author: Damián Zúñiga Avelar
Date: Abril 2026
"""

import numpy as np
from scipy.integrate import solve_ivp
from scipy.optimize import minimize
from astropy import constants as const


class SpacecraftModel:
    """
    Modelo de nave con propulsor eléctrico.
    """
    
    def __init__(self, thrust, isp, m_dry, m_propellant):
        """
        Parameters
        ----------
        thrust : float
            Empuje máximo (N)
        isp : float
            Impulso específico (s)
        m_dry : float
            Masa seca de la nave (kg)
        m_propellant : float
            Masa de propelente inicial (kg)
        """
        self.thrust = thrust
        self.isp = isp
        self.m_dry = m_dry
        self.m_prop = m_propellant
        self.m_total = m_dry + m_propellant
        
        # Constantes
        self.g0 = 9.80665  # m/s² (gravedad estándar)
    
    def mass_flow_rate(self):
        """
        Tasa de consumo de masa.
        
        Returns
        -------
        mdot : float
            dm/dt en kg/s
        """
        return self.thrust / (self.isp * self.g0)
    
    def __repr__(self):
        return (f"SpacecraftModel(T={self.thrust:.3f}N, "
                f"Isp={self.isp:.0f}s, "
                f"m_total={self.m_total:.1f}kg)")


class LowThrustPropagator:
    """
    Propagador para trayectorias con bajo empuje continuo.
    """
    
    def __init__(self, mu=const.GM_earth.value):
        """
        Parameters
        ----------
        mu : float
            Parámetro gravitacional (m³/s²)
        """
        self.mu = mu
    
    def equations_of_motion_thrust(self, t, state, spacecraft, 
                                     thrust_direction_func):
        """
        Ecuaciones de movimiento con empuje continuo.
        
        state = [x, y, z, vx, vy, vz, m]
        
        Parameters
        ----------
        t : float
            Tiempo actual (s)
        state : array_like
            Estado [r, v, m]
        spacecraft : SpacecraftModel
            Modelo de nave
        thrust_direction_func : callable
            Función u(t, state) que retorna dirección empuje
        
        Returns
        -------
        derivatives : ndarray
            [dr/dt, dv/dt, dm/dt]
        """
        # Extraer estado
        r_vec = state[0:3]
        v_vec = state[3:6]
        m = state[6]
        
        r = np.linalg.norm(r_vec)
        
        # Aceleración gravitacional
        a_grav = -(self.mu / r**3) * r_vec
        
        # Aceleración por empuje
        if m > spacecraft.m_dry:
            # Dirección de empuje (vector unitario)
            u = thrust_direction_func(t, state)
            u_norm = np.linalg.norm(u)
            
            if u_norm > 1e-10:
                u_hat = u / u_norm
            else:
                u_hat = np.zeros(3)
            
            # Magnitud de empuje (puede ser variable)
            T = spacecraft.thrust * min(u_norm, 1.0)
            
            # Aceleración: a = T/m · û
            a_thrust = (T / m) * u_hat
            
            # Consumo de masa
            m_dot = -spacecraft.mass_flow_rate() * min(u_norm, 1.0)
        else:
            # Sin propelente, sin empuje
            a_thrust = np.zeros(3)
            m_dot = 0.0
        
        # Aceleración total
        a_total = a_grav + a_thrust
        
        # Derivadas
        derivatives = np.concatenate([v_vec, a_total, [m_dot]])
        
        return derivatives
    
    def propagate_with_thrust(self, r0, v0, m0, t_span, 
                               spacecraft, thrust_direction_func,
                               dt=60.0, method='DOP853', 
                               rtol=1e-9, atol=1e-11):
        """
        Propaga trayectoria con empuje continuo.
        
        Parameters
        ----------
        r0 : array_like
            Posición inicial [x, y, z] (m)
        v0 : array_like
            Velocidad inicial [vx, vy, vz] (m/s)
        m0 : float
            Masa inicial (kg)
        t_span : tuple
            (t_start, t_end) (s)
        spacecraft : SpacecraftModel
            Modelo de nave
        thrust_direction_func : callable
            Función que da dirección de empuje
        dt : float
            Paso de salida (s)
        
        Returns
        -------
        solution : dict
            't', 'r', 'v', 'm', 'success', 'message'
        """
        # Estado inicial
        state0 = np.concatenate([r0, v0, [m0]])
        
        # Puntos de evaluación
        t_eval = np.arange(t_span[0], t_span[1], dt)
        
        # Integrar
        sol = solve_ivp(
            fun=lambda t, y: self.equations_of_motion_thrust(
                t, y, spacecraft, thrust_direction_func
            ),
            t_span=t_span,
            y0=state0,
            method=method,
            t_eval=t_eval,
            rtol=rtol,
            atol=atol
        )
        
        # Extraer resultados
        return {
            't': sol.t,
            'r': sol.y[0:3, :].T,
            'v': sol.y[3:6, :].T,
            'm': sol.y[6, :],
            'success': sol.success,
            'message': sol.message
        }


# ============================================================================
# LEYES DE EMPUJE PREDEFINIDAS
# ============================================================================

def radial_thrust(t, state):
    """
    Empuje en dirección radial (ineficiente, solo demo).
    
    Parameters
    ----------
    t : float
        Tiempo
    state : array_like
        Estado actual
    
    Returns
    -------
    u : ndarray
        Vector dirección empuje
    """
    r_vec = state[0:3]
    r = np.linalg.norm(r_vec)
    return r_vec / r  # Dirección radial


def tangential_thrust(t, state):
    """
    Empuje tangencial (más eficiente para aumentar energía).
    
    Parameters
    ----------
    t : float
        Tiempo
    state : array_like
        Estado actual
    
    Returns
    -------
    u : ndarray
        Vector dirección empuje
    """
    v_vec = state[3:6]
    v = np.linalg.norm(v_vec)
    
    if v > 1e-6:
        return v_vec / v  # Dirección velocidad
    else:
        return np.array([0, 1, 0])  # Default


def prograde_thrust(t, state):
    """
    Empuje prograde (igual que tangencial, nombre alternativo).
    """
    return tangential_thrust(t, state)



# ============================================================================
# OPTIMIZADOR DE TRAYECTORIAS
# ============================================================================

class TrajectoryOptimizer:
    """
    Optimiza trayectorias de bajo empuje para minimizar masa de propelente
    (maximizar masa final).
    """
    
    def __init__(self, mu=const.GM_earth.value):
        """
        Parameters
        ----------
        mu : float
            Parámetro gravitacional
        """
        self.mu = mu
        self.propagator = LowThrustPropagator(mu=mu)
    
    def constant_direction_thrust(self, direction):
        """
        Genera función de empuje con dirección constante.
        
        Parameters
        ----------
        direction : array_like
            Vector dirección [ux, uy, uz]
        
        Returns
        -------
        thrust_func : callable
            Función u(t, state)
        """
        direction = np.array(direction)
        direction_norm = np.linalg.norm(direction)
        
        if direction_norm > 1e-10:
            u_hat = direction / direction_norm
        else:
            u_hat = np.array([1, 0, 0])
        
        def thrust_function(t, state):
            return u_hat
        
        return thrust_function
    
    def optimize_constant_direction(self, r0, v0, r_target, v_target,
                                      spacecraft, t_max,
                                      initial_guess=None):
        """
        Optimiza trayectoria con dirección de empuje CONSTANTE.
        
        Este es el caso más simple - solo optimizamos la dirección.
        
        Parameters
        ----------
        r0, v0 : array_like
            Estado inicial
        r_target, v_target : array_like
            Estado final deseado
        spacecraft : SpacecraftModel
            Modelo de nave
        t_max : float
            Tiempo máximo de transferencia (s)
        initial_guess : array_like, optional
            Dirección inicial [ux, uy, uz]
        
        Returns
        -------
        result : dict
            'solution': trayectoria óptima
            'direction': dirección óptima
            'success': bool
            'message': str
        """
        from scipy.optimize import minimize
        
        # Guess inicial (prograde si no se especifica)
        if initial_guess is None:
            v0_norm = np.linalg.norm(v0)
            initial_guess = v0 / v0_norm if v0_norm > 0 else np.array([0, 1, 0])
        
        print("\n" + "="*70)
        print("OPTIMIZACIÓN DE TRAYECTORIA")
        print("="*70)
        print(f"Tiempo máximo: {t_max/86400:.1f} días")
        print(f"Dirección inicial: [{initial_guess[0]:.3f}, {initial_guess[1]:.3f}, {initial_guess[2]:.3f}]")
        


        # Función objetivo
        def objective(u_direction):
            """
            Minimiza: -m_final (maximiza masa final)
            """
            # Crear función de empuje
            thrust_func = self.constant_direction_thrust(u_direction)
            
            # Propagar
            try:
                sol = self.propagator.propagate_with_thrust(
                    r0, v0, spacecraft.m_total,
                    (0, t_max),
                    spacecraft,
                    thrust_func,
                    dt=3600.0  # 1 hora
                )
                
                if not sol['success']:
                    return 1e10  # Penalización grande
                
                # Estado final
                r_final = sol['r'][-1]
                v_final = sol['v'][-1]
                m_final = sol['m'][-1]
                
                # Error en condiciones finales
                r_error = np.linalg.norm(r_final - r_target)
                v_error = np.linalg.norm(v_final - v_target)
                
                # Función de costo: penalizar error + minimizar masa propelente
                cost = (spacecraft.m_total - m_final) + 1e-3 * (r_error + 1e3*v_error)
                
                return cost
            
            except:
                return 1e10
        
        # Optimizar
        print("\nOptimizando...")
        result = minimize(
            objective,
            initial_guess,
            method='Nelder-Mead',
            options={'maxiter': 100, 'disp': True}
        )
        
        # Propagar con solución óptima
        optimal_direction = result.x
        thrust_func = self.constant_direction_thrust(optimal_direction)
        
        sol_optimal = self.propagator.propagate_with_thrust(
            r0, v0, spacecraft.m_total,
            (0, t_max),
            spacecraft,
            thrust_func,
            dt=600.0  # 10 min para plotting
        )
        
        return {
            'solution': sol_optimal,
            'direction': optimal_direction,
            'cost': result.fun,
            'success': result.success,
            'message': result.message
        }
    


    def optimize_variable_direction(self, r0, v0, r_target, v_target,
                                        spacecraft, t_transfer,
                                        n_segments=5):
            """
            Optimiza trayectoria con dirección de empuje VARIABLE en el tiempo.
            
            Divide la trayectoria en segmentos con dirección constante por segmento,
            luego optimiza todas las direcciones simultáneamente.
            
            Parameters
            ----------
            r0, v0 : array_like
                Estado inicial
            r_target, v_target : array_like
                Estado final deseado
            spacecraft : SpacecraftModel
                Modelo de nave
            t_transfer : float
                Tiempo total de transferencia (s)
            n_segments : int
                Número de segmentos temporales
            
            Returns
            -------
            result : dict
                'solution': trayectoria óptima
                'directions': direcciones por segmento
                'times': tiempos de los segmentos
                'success': bool
                'message': str
            """
            from scipy.optimize import minimize, differential_evolution
            
            print("\n" + "="*70)
            print("OPTIMIZACIÓN CON DIRECCIÓN VARIABLE")
            print("="*70)
            print(f"Tiempo total:  {t_transfer/86400:.1f} días")
            print(f"Segmentos:     {n_segments}")
            print(f"Variables:     {n_segments * 3} (ux, uy, uz por segmento)")
            
            # Tiempos de los segmentos
            segment_times = np.linspace(0, t_transfer, n_segments + 1)
            
            # Guess inicial: empuje tangencial todo el tiempo
            v0_norm = np.linalg.norm(v0)
            if v0_norm > 0:
                u_initial = v0 / v0_norm
            else:
                u_initial = np.array([0, 1, 0])
            
            # Variables: [ux1, uy1, uz1, ux2, uy2, uz2, ...]
            x0 = np.tile(u_initial, n_segments)
            
            print(f"Optimizando...")
            
            # Función objetivo
            def objective(x):
                """
                Minimiza: masa de propelente + penalización por error final
                """
                # Reconstruir direcciones
                directions = x.reshape((n_segments, 3))
                
                # Crear función de empuje por segmentos
                thrust_func = self.time_varying_thrust(directions, segment_times)
                
                # Propagar
                try:
                    sol = self.propagator.propagate_with_thrust(
                        r0, v0, spacecraft.m_total,
                        (0, t_transfer),
                        spacecraft,
                        thrust_func,
                        dt=3600.0
                    )
                    
                    if not sol['success']:
                        return 1e10
                    
                    # Estado final
                    r_final = sol['r'][-1]
                    v_final = sol['v'][-1]
                    m_final = sol['m'][-1]
                    
                    # Errores
                    r_error = np.linalg.norm(r_final - r_target)
                    v_error = np.linalg.norm(v_final - v_target)
                    
                    # Costo: propelente usado + penalización error
                    m_prop_used = spacecraft.m_total - m_final
                    penalty = 1e-4 * r_error + 1e-2 * v_error
                    
                    cost = m_prop_used + penalty
                    
                    return cost
                
                except Exception as e:
                    return 1e10
            
            # Restricciones: |u| ≤ 1 para cada segmento
            bounds = [(-1, 1)] * (n_segments * 3)
            
            # Optimizar con algoritmo global
            result = differential_evolution(
                objective,
                bounds,
                maxiter=30,
                popsize=8,
                disp=True,
                workers=1,
                seed=42,
                atol=0.01,       # Tolerancia absoluta
            tol=0.01         # Tolerancia relativa
            )
            
            print(f"\n✓ Optimización completada")
            print(f"  Costo final: {result.fun:.6f}")
            print(f"  Iteraciones: {result.nit}")
            
            # Reconstruir solución óptima
            optimal_directions = result.x.reshape((n_segments, 3))
            thrust_func_optimal = self.time_varying_thrust(optimal_directions, 
                                                            segment_times)
            
            sol_optimal = self.propagator.propagate_with_thrust(
                r0, v0, spacecraft.m_total,
                (0, t_transfer),
                spacecraft,
                thrust_func_optimal,
                dt=600.0  # 10 min
            )
            
            return {
                'solution': sol_optimal,
                'directions': optimal_directions,
                'times': segment_times,
                'cost': result.fun,
                'success': result.success,
                'message': result.message if hasattr(result, 'message') else 'OK'
            }


    
    def time_varying_thrust(self, control_points, times):
            """
            Genera función de empuje con dirección variable en el tiempo.
            
            Parameters
            ----------
            control_points : ndarray
                Array (N, 3) con direcciones en N segmentos temporales
            times : array_like
                Tiempos de frontera de segmentos (N+1 elementos)
                Ej: [0, t1, t2, t3, t4, tf] para 5 segmentos
            
            Returns
            -------
            thrust_func : callable
                Función u(t, state) que retorna dirección de empuje
            """
            # times tiene N+1 elementos
            # control_points tiene N filas
            # Cada segmento i va desde times[i] hasta times[i+1]
            
            n_segments = len(control_points)
            
            def thrust_function(t, state):
                """
                Retorna dirección de empuje en tiempo t.
                Usa función constante por tramos (piecewise constant).
                """
                # Encontrar en qué segmento estamos
                segment_idx = 0
                for i in range(n_segments):
                    if t >= times[i] and t < times[i+1]:
                        segment_idx = i
                        break
                    elif t >= times[-1]:  # Último punto
                        segment_idx = n_segments - 1
                        break
                
                # Retornar dirección del segmento
                return control_points[segment_idx]
            
            return thrust_function


# ============================================================================
# TESTING
# ============================================================================

if __name__ == "__main__":
    print("="*70)
    print("TEST: Low-Thrust Propagator")
    print("="*70)
    
    # Configuración
    R_earth = 6371e3
    mu = const.GM_earth.value
    
    # Órbita inicial: LEO circular 400 km
    r0 = np.array([R_earth + 400e3, 0.0, 0.0])
    v0 = np.array([0.0, 7669.0, 0.0])
    
    # Nave: Hall thruster típico
    spacecraft = SpacecraftModel(
        thrust=0.1,        # 100 mN (típico Hall thruster)
        isp=1500,          # s (típico)
        m_dry=50.0,        # kg (CubeSat)
        m_propellant=10.0  # kg
    )
    
    print(f"\nNave: {spacecraft}")
    print(f"Masa total: {spacecraft.m_total:.1f} kg")
    print(f"Masa flow rate: {spacecraft.mass_flow_rate()*1e6:.2f} mg/s")
    
    # Propagar 10 días con empuje tangencial
    prop = LowThrustPropagator(mu=mu)
    t_days = 10
    t_span = (0, t_days * 86400)
    
    print(f"\nPropagando {t_days} días con empuje tangencial...")
    
    sol = prop.propagate_with_thrust(
        r0, v0, spacecraft.m_total,
        t_span,
        spacecraft,
        tangential_thrust,  # Empuje prograde
        dt=3600.0  # 1 hora
    )
    
    if sol['success']:
        print("✓ Propagación exitosa!")
        
        # Analizar resultados
        r_final = sol['r'][-1]
        v_final = sol['v'][-1]
        m_final = sol['m'][-1]
        
        # Órbitas inicial y final
        r_i = np.linalg.norm(r0)
        r_f = np.linalg.norm(r_final)
        
        v_i = np.linalg.norm(v0)
        v_f = np.linalg.norm(v_final)
        
        # Energía
        E_i = v_i**2/2 - mu/r_i
        E_f = v_f**2/2 - mu/r_f
        
        print(f"\nResultados:")
        print(f"  Radio inicial:  {r_i/1e3:.1f} km")
        print(f"  Radio final:    {r_f/1e3:.1f} km")
        print(f"  Cambio radio:   +{(r_f-r_i)/1e3:.1f} km")
        
        print(f"\n  Velocidad inicial: {v_i:.1f} m/s")
        print(f"  Velocidad final:   {v_f:.1f} m/s")
        
        print(f"\n  Masa inicial: {spacecraft.m_total:.2f} kg")
        print(f"  Masa final:   {m_final:.2f} kg")
        print(f"  Propelente usado: {spacecraft.m_total - m_final:.2f} kg")
        
        print(f"\n  Energía inicial: {E_i:.0f} J/kg")
        print(f"  Energía final:   {E_f:.0f} J/kg")
        print(f"  ΔE: {E_f - E_i:.0f} J/kg")
        
        print(f"\n✓ Test completado - Propagador funcional!")
    else:
        print(f"✗ Error: {sol['message']}")
    
    print("="*70)