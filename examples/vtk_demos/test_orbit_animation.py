"""
VTK Orbit Animation

Simulador con animación de órbita en tiempo real.

Author: Damián Zúñiga Avelar
Date: Abril 2026
"""

import vtk
import numpy as np
import sys
import os

# Añadir path para importar nuestros módulos
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../..'))

from src.propagator import circular_velocity, orbital_period


class OrbitSimulator:
    """Simulador de órbita con VTK."""
    
    def __init__(self, altitude_km=400):
        """
        Parameters
        ----------
        altitude_km : float
            Altitud de la órbita (km)
        """
        
        self.R_earth = 6371.0  # km
        self.altitude = altitude_km
        self.orbital_radius = self.R_earth + altitude_km
        
        # Calcular parámetros orbitales
        r_meters = self.orbital_radius * 1000
        self.orbital_velocity = circular_velocity(r_meters)  # m/s
        self.orbital_period = orbital_period(r_meters)  # seconds
        
        # Estado actual
        self.current_angle = 0.0  # radianes
        self.time_elapsed = 0.0  # segundos
        self.speed_multiplier = 100.0  # Multiplicador de velocidad
        
        # VTK objects
        self.renderer = None
        self.render_window = None
        self.interactor = None
        self.satellite_actor = None
        self.marker_actor = None
        self.orbit_actor = None
        self.text_actor = None
        
        print(f"\n{'='*70}")
        print(f"  ORBIT SIMULATOR - LEO {altitude_km} km")
        print(f"{'='*70}")
        print(f"\nParámetros orbitales:")
        print(f"  Radio órbita:     {self.orbital_radius:.1f} km")
        print(f"  Velocidad:        {self.orbital_velocity:.1f} m/s ({self.orbital_velocity/1000:.2f} km/s)")
        print(f"  Periodo:          {self.orbital_period/60:.2f} min")
        print(f"  Velocidad sim:    {self.speed_multiplier}x\n")
    
    
    def create_earth(self):
        """Crea Tierra."""
        
        sphere = vtk.vtkSphereSource()
        sphere.SetCenter(0, 0, 0)
        sphere.SetRadius(self.R_earth)
        sphere.SetThetaResolution(50)
        sphere.SetPhiResolution(50)
        
        mapper = vtk.vtkPolyDataMapper()
        mapper.SetInputConnection(sphere.GetOutputPort())
        
        actor = vtk.vtkActor()
        actor.SetMapper(mapper)
        actor.GetProperty().SetColor(0.2, 0.4, 0.8)
        
        return actor
    
    
    def create_orbit_line(self):
        """Crea línea de órbita circular."""
        
        # Crear puntos de la órbita
        n_points = 100
        points = vtk.vtkPoints()
        
        for i in range(n_points + 1):
            angle = 2 * np.pi * i / n_points
            x = self.orbital_radius * np.cos(angle)
            y = self.orbital_radius * np.sin(angle)
            z = 0.0
            points.InsertNextPoint(x, y, z)
        
        # Crear línea
        line = vtk.vtkPolyLine()
        line.GetPointIds().SetNumberOfIds(n_points + 1)
        for i in range(n_points + 1):
            line.GetPointIds().SetId(i, i)
        
        # Crear celda
        cells = vtk.vtkCellArray()
        cells.InsertNextCell(line)
        
        # Crear polydata
        polydata = vtk.vtkPolyData()
        polydata.SetPoints(points)
        polydata.SetLines(cells)
        
        # Mapper
        mapper = vtk.vtkPolyDataMapper()
        mapper.SetInputData(polydata)
        
        # Actor
        actor = vtk.vtkActor()
        actor.SetMapper(mapper)
        actor.GetProperty().SetColor(0.5, 0.5, 0.5)
        actor.GetProperty().SetLineWidth(2)
        
        return actor
    
    
    def create_satellite(self):
        """Crea satélite (cubo)."""
        
        cube = vtk.vtkCubeSource()
        cube.SetXLength(500)
        cube.SetYLength(500)
        cube.SetZLength(750)
        
        mapper = vtk.vtkPolyDataMapper()
        mapper.SetInputConnection(cube.GetOutputPort())
        
        actor = vtk.vtkActor()
        actor.SetMapper(mapper)
        actor.GetProperty().SetColor(1, 0.8, 0)
        
        return actor
    
    
    def create_marker(self):
        """Crea marcador (esfera roja)."""
        
        sphere = vtk.vtkSphereSource()
        sphere.SetRadius(200)
        sphere.SetThetaResolution(20)
        sphere.SetPhiResolution(20)
        
        mapper = vtk.vtkPolyDataMapper()
        mapper.SetInputConnection(sphere.GetOutputPort())
        
        actor = vtk.vtkActor()
        actor.SetMapper(mapper)
        actor.GetProperty().SetColor(1.0, 0.2, 0.2)
        
        return actor
    
    
    def update_satellite_position(self):
        """Actualiza posición del satélite basado en ángulo actual."""
        
        x = self.orbital_radius * np.cos(self.current_angle)
        y = self.orbital_radius * np.sin(self.current_angle)
        z = 0.0
        
        # Actualizar satélite
        self.satellite_actor.SetPosition(x, y, z)
        
        # Actualizar marcador
        self.marker_actor.SetPosition(x, y, z)
    
    
    def create_info_text(self):
        """Crea texto informativo."""
        
        text = vtk.vtkTextActor()
        text.GetTextProperty().SetFontSize(16)
        text.GetTextProperty().SetColor(1.0, 1.0, 1.0)
        text.SetPosition(10, 10)
        
        return text
    
    
    def update_info_text(self):
        """Actualiza texto con info actual."""
        
        orbits_completed = self.time_elapsed / self.orbital_period
        
        info = f"""ORBIT SIMULATOR - LEO {self.altitude} km
        
Tiempo:           {self.time_elapsed:.1f} s ({self.time_elapsed/60:.2f} min)
Ángulo:           {np.degrees(self.current_angle):.1f}°
Órbitas:          {orbits_completed:.2f}
Velocidad sim:    {self.speed_multiplier:.0f}x

Controles:
  [+/-]  Velocidad simulación
  [SPACE] Pausar/Reanudar
  [R]    Reset
  [Q]    Salir
"""
        self.text_actor.SetInput(info)
    
    
    def setup_renderer(self):
        """Configura renderer y ventana."""
        
        # Renderer
        self.renderer = vtk.vtkRenderer()
        self.renderer.SetBackground(0.05, 0.05, 0.05)
        
        # Ventana
        self.render_window = vtk.vtkRenderWindow()
        self.render_window.SetSize(1400, 900)
        self.render_window.AddRenderer(self.renderer)
        self.render_window.SetWindowName(f"Orbit Simulator - LEO {self.altitude} km")
        
        # Interactor
        self.interactor = vtk.vtkRenderWindowInteractor()
        self.interactor.SetRenderWindow(self.render_window)
        
        # Añadir objetos
        earth = self.create_earth()
        self.renderer.AddActor(earth)
        
        self.orbit_actor = self.create_orbit_line()
        self.renderer.AddActor(self.orbit_actor)
        
        self.satellite_actor = self.create_satellite()
        self.renderer.AddActor(self.satellite_actor)
        
        self.marker_actor = self.create_marker()
        self.renderer.AddActor(self.marker_actor)
        
        # Ejes
        axes = vtk.vtkAxesActor()
        axes.SetTotalLength(10000, 10000, 10000)
        self.renderer.AddActor(axes)
        
        # Luz
        light = vtk.vtkLight()
        light.SetPosition(15000, 15000, 15000)
        light.SetFocalPoint(0, 0, 0)
        self.renderer.AddLight(light)
        
        # Texto
        self.text_actor = self.create_info_text()
        self.renderer.AddActor2D(self.text_actor)
        
        # Cámara
        camera = self.renderer.GetActiveCamera()
        camera.SetPosition(15000, 15000, 15000)
        camera.SetFocalPoint(0, 0, 0)
        self.renderer.ResetCamera()
        
        # Posición inicial
        self.update_satellite_position()
        self.update_info_text()
    
    
    def animation_callback(self, obj, event):
        """Callback para animación."""
        
        # Incremento de tiempo (en segundos reales)
        dt_real = 0.033  # ~30 FPS
        dt_sim = dt_real * self.speed_multiplier
        
        # Actualizar tiempo
        self.time_elapsed += dt_sim
        
        # Actualizar ángulo (velocidad angular = 2π / T)
        omega = 2 * np.pi / self.orbital_period  # rad/s
        self.current_angle += omega * dt_sim
        
        # Mantener ángulo en [0, 2π]
        if self.current_angle >= 2 * np.pi:
            self.current_angle -= 2 * np.pi
        
        # Actualizar posición
        self.update_satellite_position()
        self.update_info_text()
        
        # Re-renderizar
        self.render_window.Render()
    
    
    def key_press_callback(self, obj, event):
        """Callback para teclas."""
        
        key = self.interactor.GetKeySym()
        
        if key == 'plus' or key == 'equal':
            # Aumentar velocidad
            self.speed_multiplier *= 1.5
            print(f"Velocidad: {self.speed_multiplier:.0f}x")
        
        elif key == 'minus':
            # Disminuir velocidad
            self.speed_multiplier /= 1.5
            if self.speed_multiplier < 1.0:
                self.speed_multiplier = 1.0
            print(f"Velocidad: {self.speed_multiplier:.0f}x")
        
        elif key == 'space':
            # Pausar/reanudar
            if self.speed_multiplier > 0:
                self.paused_speed = self.speed_multiplier
                self.speed_multiplier = 0.0
                print("PAUSADO")
            else:
                self.speed_multiplier = self.paused_speed
                print(f"REANUDADO - Velocidad: {self.speed_multiplier:.0f}x")
        
        elif key == 'r':
            # Reset
            self.current_angle = 0.0
            self.time_elapsed = 0.0
            self.update_satellite_position()
            self.update_info_text()
            print("RESET")
    
    
    def run(self):
        """Ejecuta simulación."""
        
        self.setup_renderer()
        
        # Timer para animación
        self.interactor.AddObserver('TimerEvent', self.animation_callback)
        timer_id = self.interactor.CreateRepeatingTimer(33)  # ~30 FPS
        
        # Keyboard events
        self.interactor.AddObserver('KeyPressEvent', self.key_press_callback)
        
        # Variable para pausar
        self.paused_speed = self.speed_multiplier
        
        print("Simulación iniciada...")
        print("\nControles:")
        print("  [+/-]   Ajustar velocidad")
        print("  [SPACE] Pausar/Reanudar")
        print("  [R]     Reset")
        print("  Mouse   Rotar/Zoom/Pan")
        print("  [Q]     Salir\n")
        
        # Iniciar
        self.render_window.Render()
        self.interactor.Start()
        
        print("\n✓ Simulación cerrada\n")


if __name__ == "__main__":
    # Crear simulador en LEO
    sim = OrbitSimulator(altitude_km=400)
    sim.run()