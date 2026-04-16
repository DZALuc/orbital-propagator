"""
Visualization Module for Orbital Propagator

Provides 2D and 3D plotting utilities for orbital trajectories,
ground tracks, and orbital elements analysis.

Author: Damián Zúñiga Avelar
Date: April 2026
"""

import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
from matplotlib.patches import Circle
import mpl_toolkits.mplot3d.art3d as art3d


def plot_orbit_2d(solution, R_body=6371e3, title="Orbital Trajectory - 2D Projection", 
                  save_path=None, show=True):
    """
    Plot orbital trajectory in 2D (XY plane projection).
    
    Parameters
    ----------
    solution : dict
        Solution dictionary from OrbitalPropagator.propagate()
        Must contain 'r' (positions) and 't' (times)
    R_body : float, optional
        Radius of central body in meters (default: Earth = 6371 km)
    title : str, optional
        Plot title
    save_path : str, optional
        Path to save figure. If None, doesn't save.
    show : bool, optional
        Whether to display plot (default: True)
    
    Returns
    -------
    fig, ax : matplotlib figure and axis objects
    """
    # Extract data
    r = solution['r']
    t = solution['t']
    
    # Convert to km for plotting
    x = r[:, 0] / 1e3
    y = r[:, 1] / 1e3
    R_body_km = R_body / 1e3
    
    # Create figure
    fig, ax = plt.subplots(figsize=(10, 10))
    
    # Plot central body (Earth)
    earth = Circle((0, 0), R_body_km, color='#2E86AB', alpha=0.3, label='Earth')
    ax.add_patch(earth)
    
    # Plot orbit trajectory
    ax.plot(x, y, 'b-', linewidth=1.5, alpha=0.8, label='Orbit')
    
    # Mark initial position
    ax.plot(x[0], y[0], 'go', markersize=10, label='Start', zorder=5)
    
    # Mark final position
    ax.plot(x[-1], y[-1], 'ro', markersize=10, label='End', zorder=5)
    
    # Add direction arrows (every 10% of orbit)
    n_arrows = 5
    indices = np.linspace(0, len(x)-1, n_arrows+1, dtype=int)[:-1]
    
    for idx in indices:
        dx = x[idx+1] - x[idx]
        dy = y[idx+1] - y[idx]
        ax.arrow(x[idx], y[idx], dx*0.5, dy*0.5, 
                head_width=R_body_km*0.15, head_length=R_body_km*0.2,
                fc='red', ec='red', alpha=0.6, zorder=4)
    
    # Formatting
    ax.set_aspect('equal')
    ax.grid(True, alpha=0.3, linestyle='--')
    ax.set_xlabel('X Position (km)', fontsize=12)
    ax.set_ylabel('Y Position (km)', fontsize=12)
    ax.set_title(title, fontsize=14, fontweight='bold')
    ax.legend(loc='upper right', fontsize=10)
    
    # Add info text
    orbital_period_min = (t[-1] - t[0]) / 60
    info_text = f"Period: {orbital_period_min:.2f} min\nPoints: {len(t)}"
    ax.text(0.02, 0.98, info_text, transform=ax.transAxes,
            verticalalignment='top', fontsize=10,
            bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.5))
    
    plt.tight_layout()
    
    if save_path:
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
        print(f"✓ Figure saved: {save_path}")
    
    if show:
        plt.show()
    
    return fig, ax


def plot_orbit_3d(solution, R_body=6371e3, title="Orbital Trajectory - 3D View",
                  save_path=None, show=True):
    """
    Plot orbital trajectory in 3D.
    
    Parameters
    ----------
    solution : dict
        Solution dictionary from OrbitalPropagator.propagate()
    R_body : float, optional
        Radius of central body in meters
    title : str, optional
        Plot title
    save_path : str, optional
        Path to save figure
    show : bool, optional
        Whether to display plot
    
    Returns
    -------
    fig, ax : matplotlib figure and axis objects
    """
    # Extract data
    r = solution['r']
    t = solution['t']
    
    # Convert to km
    x = r[:, 0] / 1e3
    y = r[:, 1] / 1e3
    z = r[:, 2] / 1e3
    R_body_km = R_body / 1e3
    
    # Create 3D figure
    fig = plt.figure(figsize=(12, 10))
    ax = fig.add_subplot(111, projection='3d')
    
    # Draw Earth as wireframe sphere
    u = np.linspace(0, 2 * np.pi, 50)
    v = np.linspace(0, np.pi, 50)
    x_sphere = R_body_km * np.outer(np.cos(u), np.sin(v))
    y_sphere = R_body_km * np.outer(np.sin(u), np.sin(v))
    z_sphere = R_body_km * np.outer(np.ones(np.size(u)), np.cos(v))
    
    ax.plot_surface(x_sphere, y_sphere, z_sphere, 
                    color='#2E86AB', alpha=0.2, shade=True)
    
    # Plot orbit trajectory
    ax.plot(x, y, z, 'b-', linewidth=2, alpha=0.8, label='Orbit')
    
    # Mark positions
    ax.scatter(x[0], y[0], z[0], color='green', s=100, 
               label='Start', marker='o', zorder=5)
    ax.scatter(x[-1], y[-1], z[-1], color='red', s=100, 
               label='End', marker='o', zorder=5)
    
    # Draw coordinate axes
    axis_length = R_body_km * 1.5
    ax.plot([0, axis_length], [0, 0], [0, 0], 'r-', linewidth=1, alpha=0.5)
    ax.plot([0, 0], [0, axis_length], [0, 0], 'g-', linewidth=1, alpha=0.5)
    ax.plot([0, 0], [0, 0], [0, axis_length], 'b-', linewidth=1, alpha=0.5)
    
    # Labels
    ax.text(axis_length, 0, 0, 'X', color='red', fontsize=12)
    ax.text(0, axis_length, 0, 'Y', color='green', fontsize=12)
    ax.text(0, 0, axis_length, 'Z', color='blue', fontsize=12)
    
    # Formatting
    ax.set_xlabel('X (km)', fontsize=11)
    ax.set_ylabel('Y (km)', fontsize=11)
    ax.set_zlabel('Z (km)', fontsize=11)
    ax.set_title(title, fontsize=14, fontweight='bold', pad=20)
    ax.legend(loc='upper left', fontsize=10)
    
    # Equal aspect ratio
    max_range = np.max([x.max()-x.min(), y.max()-y.min(), z.max()-z.min()]) / 2
    mid_x = (x.max() + x.min()) / 2
    mid_y = (y.max() + y.min()) / 2
    mid_z = (z.max() + z.min()) / 2
    ax.set_xlim(mid_x - max_range, mid_x + max_range)
    ax.set_ylim(mid_y - max_range, mid_y + max_range)
    ax.set_zlim(mid_z - max_range, mid_z + max_range)
    
    # Set viewing angle
    ax.view_init(elev=25, azim=45)
    
    plt.tight_layout()
    
    if save_path:
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
        print(f"✓ Figure saved: {save_path}")
    
    if show:
        plt.show()
    
    return fig, ax


def plot_orbital_elements(solution, mu=3.986004418e14, save_path=None, show=True):
    """
    Plot orbital elements evolution over time.
    
    Shows altitude, velocity magnitude, and energy conservation.
    
    Parameters
    ----------
    solution : dict
        Solution from propagator
    mu : float
        Gravitational parameter
    save_path : str, optional
        Save path
    show : bool, optional
        Display plot
    
    Returns
    -------
    fig, axes : figure and axes array
    """
    r = solution['r']
    v = solution['v']
    t = solution['t'] / 60  # Convert to minutes
    
    # Calculate orbital parameters
    altitude = (np.linalg.norm(r, axis=1) - 6371e3) / 1e3  # km
    velocity = np.linalg.norm(v, axis=1) / 1e3  # km/s
    
    # Energy
    r_mag = np.linalg.norm(r, axis=1)
    v_mag = np.linalg.norm(v, axis=1)
    energy = (v_mag**2) / 2 - mu / r_mag
    energy_error = (energy - energy[0]) / abs(energy[0]) * 100  # Percentage
    
    # Create subplots
    fig, axes = plt.subplots(3, 1, figsize=(12, 10))
    
    # Plot 1: Altitude
    axes[0].plot(t, altitude, 'b-', linewidth=1.5)
    axes[0].set_ylabel('Altitude (km)', fontsize=11)
    axes[0].set_title('Orbital Parameters Evolution', fontsize=13, fontweight='bold')
    axes[0].grid(True, alpha=0.3)
    axes[0].set_xlim(t[0], t[-1])
    
    # Plot 2: Velocity
    axes[1].plot(t, velocity, 'g-', linewidth=1.5)
    axes[1].set_ylabel('Velocity (km/s)', fontsize=11)
    axes[1].grid(True, alpha=0.3)
    axes[1].set_xlim(t[0], t[-1])
    
    # Plot 3: Energy error
    axes[2].plot(t, energy_error, 'r-', linewidth=1.5)
    axes[2].set_ylabel('Energy Error (%)', fontsize=11)
    axes[2].set_xlabel('Time (minutes)', fontsize=11)
    axes[2].grid(True, alpha=0.3)
    axes[2].set_xlim(t[0], t[-1])
    axes[2].axhline(y=0, color='k', linestyle='--', alpha=0.5)
    
    # Add statistics
    stats_text = f"Max altitude variation: {altitude.max() - altitude.min():.3f} km\n"
    stats_text += f"Max velocity variation: {(velocity.max() - velocity.min())*1000:.3f} m/s\n"
    stats_text += f"Max energy error: {abs(energy_error).max():.2e} %"
    
    axes[2].text(0.98, 0.97, stats_text, transform=axes[2].transAxes,
                verticalalignment='top', horizontalalignment='right',
                fontsize=9, bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.5))
    
    plt.tight_layout()
    
    if save_path:
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
        print(f"✓ Figure saved: {save_path}")
    
    if show:
        plt.show()
    
    return fig, axes


def plot_position_components(solution, save_path=None, show=True):
    """
    Plot X, Y, Z position components over time.
    
    Useful for understanding orbital geometry.
    
    Parameters
    ----------
    solution : dict
        Solution from propagator
    save_path : str, optional
        Save path
    show : bool, optional
        Display plot
    
    Returns
    -------
    fig, ax : figure and axis
    """
    r = solution['r'] / 1e3  # Convert to km
    t = solution['t'] / 60   # Convert to minutes
    
    fig, ax = plt.subplots(figsize=(12, 6))
    
    ax.plot(t, r[:, 0], 'r-', linewidth=1.5, label='X', alpha=0.8)
    ax.plot(t, r[:, 1], 'g-', linewidth=1.5, label='Y', alpha=0.8)
    ax.plot(t, r[:, 2], 'b-', linewidth=1.5, label='Z', alpha=0.8)
    
    ax.set_xlabel('Time (minutes)', fontsize=12)
    ax.set_ylabel('Position (km)', fontsize=12)
    ax.set_title('Position Components vs Time', fontsize=13, fontweight='bold')
    ax.grid(True, alpha=0.3)
    ax.legend(loc='best', fontsize=11)
    ax.axhline(y=0, color='k', linestyle='--', alpha=0.3)
    
    plt.tight_layout()
    
    if save_path:
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
        print(f"✓ Figure saved: {save_path}")
    
    if show:
        plt.show()
    
    return fig, ax


def plot_orbital_elements_evolution(solution, mu=3.986004418e14, 
                                     solution_j2=None, 
                                     title="Evolución de Elementos Orbitales",
                                     save_path=None, show=True):
    """
    Grafica evolución de elementos orbitales en el tiempo.
    
    Muestra cómo los 6 elementos Keplerianos cambian durante la propagación.
    Si se proporciona solution_j2, compara con/sin perturbación J2.
    
    Parameters
    ----------
    solution : dict
        Solución de propagación (sin J2 o referencia)
    mu : float, optional
        Parámetro gravitacional
    solution_j2 : dict, optional
        Solución con J2 para comparación
    title : str, optional
        Título de la figura
    save_path : str, optional
        Ruta para guardar figura
    show : bool, optional
        Mostrar figura
    
    Returns
    -------
    fig, axes : matplotlib figure y array de axes
    """
    from src.orbital_elements import cartesian_to_keplerian
    
    # Calcular elementos orbitales para cada punto
    n_points = len(solution['t'])
    
    elements_base = {
        'a': np.zeros(n_points),
        'e': np.zeros(n_points),
        'i': np.zeros(n_points),
        'RAAN': np.zeros(n_points),
        'omega': np.zeros(n_points),
        'nu': np.zeros(n_points)
    }
    
    print("Calculando elementos orbitales base...")
    for idx in range(n_points):
        elem = cartesian_to_keplerian(solution['r'][idx], solution['v'][idx], mu)
        elements_base['a'][idx] = elem['a']
        elements_base['e'][idx] = elem['e']
        elements_base['i'][idx] = elem['i']
        elements_base['RAAN'][idx] = elem['RAAN']
        elements_base['omega'][idx] = elem['omega']
        elements_base['nu'][idx] = elem['nu']
    
    # Si hay solución J2, calcular elementos para ella también
    if solution_j2 is not None:
        elements_j2 = {
            'a': np.zeros(n_points),
            'e': np.zeros(n_points),
            'i': np.zeros(n_points),
            'RAAN': np.zeros(n_points),
            'omega': np.zeros(n_points),
            'nu': np.zeros(n_points)
        }
        
        print("Calculando elementos orbitales con J2...")
        for idx in range(n_points):
            elem = cartesian_to_keplerian(solution_j2['r'][idx], solution_j2['v'][idx], mu)
            elements_j2['a'][idx] = elem['a']
            elements_j2['e'][idx] = elem['e']
            elements_j2['i'][idx] = elem['i']
            elements_j2['RAAN'][idx] = elem['RAAN']
            elements_j2['omega'][idx] = elem['omega']
            elements_j2['nu'][idx] = elem['nu']
    
    # Tiempo en horas
    t_hours = solution['t'] / 3600
    
    # Crear figura con 6 subplots (3 filas, 2 columnas)
    fig, axes = plt.subplots(3, 2, figsize=(14, 12))
    fig.suptitle(title, fontsize=16, fontweight='bold', y=0.995)
    
    # Plot 1: Semieje Mayor
    ax = axes[0, 0]
    ax.plot(t_hours, elements_base['a']/1e3, 'b-', linewidth=1.5, label='Sin J2' if solution_j2 else 'Propagación')
    if solution_j2 is not None:
        ax.plot(t_hours, elements_j2['a']/1e3, 'r--', linewidth=1.5, label='Con J2')
    ax.set_ylabel('Semieje mayor (km)', fontsize=11)
    ax.set_title('(a) Semieje Mayor', fontsize=12, fontweight='bold')
    ax.grid(True, alpha=0.3)
    ax.legend(loc='best', fontsize=9)
    
    # Plot 2: Excentricidad
    ax = axes[0, 1]
    ax.plot(t_hours, elements_base['e'], 'b-', linewidth=1.5, label='Sin J2' if solution_j2 else 'Propagación')
    if solution_j2 is not None:
        ax.plot(t_hours, elements_j2['e'], 'r--', linewidth=1.5, label='Con J2')
    ax.set_ylabel('Excentricidad', fontsize=11)
    ax.set_title('(b) Excentricidad', fontsize=12, fontweight='bold')
    ax.grid(True, alpha=0.3)
    ax.legend(loc='best', fontsize=9)
    
    # Plot 3: Inclinación
    ax = axes[1, 0]
    ax.plot(t_hours, np.degrees(elements_base['i']), 'b-', linewidth=1.5, label='Sin J2' if solution_j2 else 'Propagación')
    if solution_j2 is not None:
        ax.plot(t_hours, np.degrees(elements_j2['i']), 'r--', linewidth=1.5, label='Con J2')
    ax.set_ylabel('Inclinación (°)', fontsize=11)
    ax.set_title('(c) Inclinación', fontsize=12, fontweight='bold')
    ax.grid(True, alpha=0.3)
    ax.legend(loc='best', fontsize=9)
    
    # Plot 4: RAAN (¡Aquí se ve el efecto J2!)
    ax = axes[1, 1]
    
    # Unwrap RAAN para evitar saltos 2π → 0
    RAAN_base_unwrapped = np.unwrap(elements_base['RAAN'])
    ax.plot(t_hours, np.degrees(RAAN_base_unwrapped), 'b-', linewidth=1.5, label='Sin J2' if solution_j2 else 'Propagación')
    
    if solution_j2 is not None:
        RAAN_j2_unwrapped = np.unwrap(elements_j2['RAAN'])
        ax.plot(t_hours, np.degrees(RAAN_j2_unwrapped), 'r--', linewidth=1.5, label='Con J2')
    
    ax.set_ylabel('RAAN - Ω (°)', fontsize=11)
    ax.set_title('(d) Ascensión Recta del Nodo Ascendente', fontsize=12, fontweight='bold')
    ax.grid(True, alpha=0.3)
    ax.legend(loc='best', fontsize=9)
    
    # Plot 5: Argumento del Perigeo
    ax = axes[2, 0]
    omega_base_unwrapped = np.unwrap(elements_base['omega'])
    ax.plot(t_hours, np.degrees(omega_base_unwrapped), 'b-', linewidth=1.5, label='Sin J2' if solution_j2 else 'Propagación')
    
    if solution_j2 is not None:
        omega_j2_unwrapped = np.unwrap(elements_j2['omega'])
        ax.plot(t_hours, np.degrees(omega_j2_unwrapped), 'r--', linewidth=1.5, label='Con J2')
    
    ax.set_ylabel('Argumento Perigeo - ω (°)', fontsize=11)
    ax.set_xlabel('Tiempo (horas)', fontsize=11)
    ax.set_title('(e) Argumento del Perigeo', fontsize=12, fontweight='bold')
    ax.grid(True, alpha=0.3)
    ax.legend(loc='best', fontsize=9)
    
    # Plot 6: Anomalía Verdadera (opcional) o Altitud
    ax = axes[2, 1]
    
    # Calcular altitud (más útil que anomalía verdadera)
    R_earth = 6371e3
    altitude_base = (np.linalg.norm(solution['r'], axis=1) - R_earth) / 1e3
    ax.plot(t_hours, altitude_base, 'b-', linewidth=1.5, label='Sin J2' if solution_j2 else 'Propagación')
    
    if solution_j2 is not None:
        altitude_j2 = (np.linalg.norm(solution_j2['r'], axis=1) - R_earth) / 1e3
        ax.plot(t_hours, altitude_j2, 'r--', linewidth=1.5, label='Con J2')
    
    ax.set_ylabel('Altitud (km)', fontsize=11)
    ax.set_xlabel('Tiempo (horas)', fontsize=11)
    ax.set_title('(f) Altitud sobre la Tierra', fontsize=12, fontweight='bold')
    ax.grid(True, alpha=0.3)
    ax.legend(loc='best', fontsize=9)
    
    plt.tight_layout()
    
    if save_path:
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
        print(f"✓ Figura guardada: {save_path}")
    
    if show:
        plt.show()
    
    return fig, axes    




def plot_j2_comparison_3d(solution_no_j2, solution_j2, R_body=6371e3,
                          title="Comparación: Propagación con/sin J2",
                          save_path=None, show=True):
    """
    Compara dos trayectorias orbitales en 3D: con y sin perturbación J2.
    
    Muestra visualmente cómo las órbitas divergen debido a J2.
    
    Parameters
    ----------
    solution_no_j2 : dict
        Solución sin J2 (modelo ideal)
    solution_j2 : dict
        Solución con J2 (modelo realista)
    R_body : float, optional
        Radio del cuerpo central en metros
    title : str, optional
        Título de la figura
    save_path : str, optional
        Ruta para guardar
    show : bool, optional
        Mostrar figura
    
    Returns
    -------
    fig, ax : matplotlib figure y axis 3D
    """
    # Extraer datos
    r_no_j2 = solution_no_j2['r']
    r_j2 = solution_j2['r']
    
    # Convertir a km
    x_no_j2 = r_no_j2[:, 0] / 1e3
    y_no_j2 = r_no_j2[:, 1] / 1e3
    z_no_j2 = r_no_j2[:, 2] / 1e3
    
    x_j2 = r_j2[:, 0] / 1e3
    y_j2 = r_j2[:, 1] / 1e3
    z_j2 = r_j2[:, 2] / 1e3
    
    R_body_km = R_body / 1e3
    
    # Crear figura 3D
    fig = plt.figure(figsize=(14, 10))
    ax = fig.add_subplot(111, projection='3d')
    
    # Dibujar Tierra como esfera wireframe
    u = np.linspace(0, 2 * np.pi, 40)
    v = np.linspace(0, np.pi, 40)
    x_sphere = R_body_km * np.outer(np.cos(u), np.sin(v))
    y_sphere = R_body_km * np.outer(np.sin(u), np.sin(v))
    z_sphere = R_body_km * np.outer(np.ones(np.size(u)), np.cos(v))
    
    ax.plot_surface(x_sphere, y_sphere, z_sphere, 
                    color='#2E86AB', alpha=0.15, shade=True)
    
    # Plot órbita SIN J2 (azul)
    ax.plot(x_no_j2, y_no_j2, z_no_j2, 
            'b-', linewidth=2, alpha=0.7, label='Sin J2 (ideal)')
    
    # Plot órbita CON J2 (roja)
    ax.plot(x_j2, y_j2, z_j2, 
            'r--', linewidth=2, alpha=0.8, label='Con J2 (realista)')
    
    # Marcar puntos inicial y final
    # Inicial (verde)
    ax.scatter(x_no_j2[0], y_no_j2[0], z_no_j2[0], 
               color='green', s=150, marker='o', 
               label='Inicio', zorder=5, edgecolors='darkgreen', linewidths=2)
    
    # Final sin J2 (azul oscuro)
    ax.scatter(x_no_j2[-1], y_no_j2[-1], z_no_j2[-1], 
               color='darkblue', s=150, marker='s', 
               label='Final sin J2', zorder=5, edgecolors='blue', linewidths=2)
    
    # Final con J2 (rojo oscuro)
    ax.scatter(x_j2[-1], y_j2[-1], z_j2[-1], 
               color='darkred', s=150, marker='s', 
               label='Final con J2', zorder=5, edgecolors='red', linewidths=2)
    
    # Línea conectando posiciones finales (muestra divergencia)
    ax.plot([x_no_j2[-1], x_j2[-1]], 
            [y_no_j2[-1], y_j2[-1]], 
            [z_no_j2[-1], z_j2[-1]], 
            'k--', linewidth=2, alpha=0.5, label='Divergencia')
    
    # Calcular divergencia
    divergence = np.linalg.norm(r_j2[-1] - r_no_j2[-1])
    
    # Dibujar ejes coordenados
    axis_length = R_body_km * 1.8
    ax.plot([0, axis_length], [0, 0], [0, 0], 'r-', linewidth=1, alpha=0.4)
    ax.plot([0, 0], [0, axis_length], [0, 0], 'g-', linewidth=1, alpha=0.4)
    ax.plot([0, 0], [0, 0], [0, axis_length], 'b-', linewidth=1, alpha=0.4)
    
    # Etiquetas de ejes
    ax.text(axis_length*1.1, 0, 0, 'X', color='red', fontsize=11)
    ax.text(0, axis_length*1.1, 0, 'Y', color='green', fontsize=11)
    ax.text(0, 0, axis_length*1.1, 'Z', color='blue', fontsize=11)
    
    # Configuración de ejes
    ax.set_xlabel('X (km)', fontsize=11)
    ax.set_ylabel('Y (km)', fontsize=11)
    ax.set_zlabel('Z (km)', fontsize=11)
    ax.set_title(title, fontsize=14, fontweight='bold', pad=20)
    
    # Aspect ratio igual
    all_x = np.concatenate([x_no_j2, x_j2])
    all_y = np.concatenate([y_no_j2, y_j2])
    all_z = np.concatenate([z_no_j2, z_j2])
    
    max_range = np.max([all_x.max()-all_x.min(), 
                        all_y.max()-all_y.min(), 
                        all_z.max()-all_z.min()]) / 2
    
    mid_x = (all_x.max() + all_x.min()) / 2
    mid_y = (all_y.max() + all_y.min()) / 2
    mid_z = (all_z.max() + all_z.min()) / 2
    
    ax.set_xlim(mid_x - max_range, mid_x + max_range)
    ax.set_ylim(mid_y - max_range, mid_y + max_range)
    ax.set_zlim(mid_z - max_range, mid_z + max_range)
    
    # Ángulo de vista
    ax.view_init(elev=20, azim=45)
    
    # Leyenda (lado derecho superior)
    ax.legend(loc='upper right', fontsize=10, framealpha=0.9)
    
    # Texto con información de divergencia (lado izquierdo inferior)
    info_text = f"Divergencia final: {divergence/1e3:.1f} km\n"
    info_text += f"Tiempo simulado: {solution_j2['t'][-1]/3600:.1f} horas"
    
    ax.text2D(0.02, 0.12, info_text, transform=ax.transAxes,
              verticalalignment='bottom', fontsize=10,
              bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.8))
    plt.tight_layout()
    
    if save_path:
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
        print(f"✓ Figura guardada: {save_path}")
    
    if show:
        plt.show()
    
    return fig, ax    



def plot_ground_track(solution, title="Ground Track - Trayectoria del Satélite",
                      earth_rotation=True, save_path=None, show=True):
    """
    Grafica la traza terrestre (ground track) del satélite.
    
    Proyecta la órbita 3D sobre la superficie terrestre mostrando
    latitud y longitud del sub-punto satelital.
    
    Parameters
    ----------
    solution : dict
        Solución de propagación orbital
    title : str, optional
        Título de la figura
    earth_rotation : bool, optional
        Si True, considera rotación terrestre (default: True)
    save_path : str, optional
        Ruta para guardar
    show : bool, optional
        Mostrar figura
    
    Returns
    -------
    fig, ax : matplotlib figure y axis
    """
    # Extraer datos
    r = solution['r']  # Posiciones en ECEF
    t = solution['t']  # Tiempos
    
    # Convertir coordenadas Cartesianas a Latitud/Longitud
    latitudes = []
    longitudes = []
    
    # Velocidad angular de la Tierra (rad/s)
    omega_earth = 7.2921159e-5  # rad/s
    
    for i, pos in enumerate(r):
        x, y, z = pos
        
        # Radio desde el centro
        r_mag = np.linalg.norm(pos)
        
        # Latitud (geodética simplificada)
        lat = np.arcsin(z / r_mag)
        
        # Longitud (considerando rotación terrestre si está habilitado)
        if earth_rotation:
            # La Tierra rota bajo el satélite
            lon = np.arctan2(y, x) - omega_earth * t[i]
        else:
            # Sin rotación terrestre (sistema inercial)
            lon = np.arctan2(y, x)
        
        # Normalizar longitud a [-π, π]
        lon = np.arctan2(np.sin(lon), np.cos(lon))
        
        # Convertir a grados
        latitudes.append(np.degrees(lat))
        longitudes.append(np.degrees(lon))
    
    latitudes = np.array(latitudes)
    longitudes = np.array(longitudes)
    
    # Crear figura
    fig, ax = plt.subplots(figsize=(16, 9))
    
    # Dibujar mapa base simple
    # Continentes simplificados (rectángulos aproximados)
    # Esto es solo decorativo - la traza es lo importante
    ax.fill([-180, 180, 180, -180], [-90, -90, 90, 90], 
            color='lightblue', alpha=0.3, label='Océanos')
    
    # Dibujar grid de lat/lon
    # Meridianos (longitud)
    for lon in range(-180, 181, 30):
        ax.plot([lon, lon], [-90, 90], 'k-', linewidth=0.5, alpha=0.3)
    
    # Paralelos (latitud)
    for lat in range(-90, 91, 30):
        ax.plot([-180, 180], [lat, lat], 'k-', linewidth=0.5, alpha=0.3)
    
    # Ecuador y meridiano de Greenwich (más gruesos)
    ax.plot([-180, 180], [0, 0], 'k-', linewidth=1.5, alpha=0.5, label='Ecuador')
    ax.plot([0, 0], [-90, 90], 'k-', linewidth=1.5, alpha=0.5, label='Meridiano 0°')
    
    # Plot ground track
    # Dividir en segmentos cuando cruza el anti-meridiano (±180°)
    segments = []
    current_segment_lon = []
    current_segment_lat = []
    
    for i in range(len(longitudes)):
        if i > 0 and abs(longitudes[i] - longitudes[i-1]) > 180:
            # Cruce del anti-meridiano
            if len(current_segment_lon) > 0:
                segments.append((current_segment_lon.copy(), current_segment_lat.copy()))
            current_segment_lon = [longitudes[i]]
            current_segment_lat = [latitudes[i]]
        else:
            current_segment_lon.append(longitudes[i])
            current_segment_lat.append(latitudes[i])
    
    # Añadir último segmento
    if len(current_segment_lon) > 0:
        segments.append((current_segment_lon, current_segment_lat))
    
    # Dibujar todos los segmentos
    for idx, (seg_lon, seg_lat) in enumerate(segments):
        if idx == 0:
            ax.plot(seg_lon, seg_lat, 'r-', linewidth=2.5, 
                   label='Traza satelital', zorder=3)
        else:
            ax.plot(seg_lon, seg_lat, 'r-', linewidth=2.5, zorder=3)
    
    # Marcar inicio y fin
    ax.plot(longitudes[0], latitudes[0], 'go', markersize=14, 
           label='Inicio', zorder=5,
           markeredgecolor='darkgreen', markeredgewidth=2)
    
    ax.plot(longitudes[-1], latitudes[-1], 'rs', markersize=14, 
           label='Fin', zorder=5,
           markeredgecolor='darkred', markeredgewidth=2)
    
    # Configuración de ejes
    ax.set_xlim(-180, 180)
    ax.set_ylim(-90, 90)
    ax.set_xlabel('Longitud (°)', fontsize=12)
    ax.set_ylabel('Latitud (°)', fontsize=12)
    ax.set_title(title, fontsize=14, fontweight='bold', pad=15)
    ax.grid(True, alpha=0.3, linestyle='--', linewidth=0.5)
    ax.legend(loc='lower left', fontsize=10, framealpha=0.9)
    ax.set_aspect('equal')
    
    # Etiquetas de grid
    ax.set_xticks(range(-180, 181, 60))
    ax.set_yticks(range(-90, 91, 30))
    
    # Información adicional
    info_text = f"Tiempo simulado: {t[-1]/3600:.1f} horas\n"
    info_text += f"Latitud: {latitudes.min():.1f}° a {latitudes.max():.1f}°\n"
    info_text += f"Órbitas: {len(segments)} segmentos\n"
    if earth_rotation:
        info_text += "Rotación terrestre: Habilitada"
    else:
        info_text += "Rotación terrestre: Deshabilitada"
    
    ax.text(0.98, 0.02, info_text, transform=ax.transAxes,
           verticalalignment='bottom', horizontalalignment='right',
           fontsize=10, bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.9))
    
    plt.tight_layout()
    
    if save_path:
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
        print(f"✓ Figura guardada: {save_path}")
    
    if show:
        plt.show()
    
    return fig, ax