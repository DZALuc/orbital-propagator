"""
Hohmann Transfer Animated

Simulador VTK de transferencia Hohmann completa con animación.

Author: Damián Zúñiga Avelar
Date: Mayo 2026
"""

import vtk
import numpy as np
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../..'))

from src.propagator import circular_velocity, orbital_period as calc_orbital_period
from src.delta_v import hohmann_transfer


class HohmannTransferSimulator:
    """Simulador de transferencia Hohmann animada."""
    
    def __init__(self, h1_km=400, h2_km=35786):
        """
        Parameters
        ----------
        h1_km : float
            Altitud órbita inicial (km)
        h2_km : float
            Altitud órbita final (km)
        """
        
        print(f"\n{'='*70}")
        print(f"  HOHMANN TRANSFER SIMULATOR")
        print(f"{'='*70}\n")
        
        self.R_earth = 6371.0  # km
        self.h1 = h1_km
        self.h2 = h2_km
        self.r1 = self.R_earth + h1_km
        self.r2 = self.R_earth + h2_km
        
        # Calcular parámetros de transferencia
        r1_m = self.r1 * 1000
        r2_m = self.r2 * 1000
        
        # Usar nuestra función de delta_v
        transfer_data = hohmann_transfer(r1_m, r2_m)
        
        # Parámetros orbitales
        self.v1 = circular_velocity(r1_m)  # Velocidad en LEO
        self.v2 = circular_velocity(r2_m)  # Velocidad en GEO
        
        self.period1 = calc_orbital_period(r1_m)  # Periodo LEO
        self.period2 = calc_orbital_period(r2_m)  # Periodo GEO
        
        # Parámetros de transferencia
        self.a_transfer = transfer_data['semi_major']  # Semi-eje mayor (m)
        self.transfer_time = transfer_data['transfer_time']  # Tiempo (s)
        self.delta_v1 = transfer_data['delta_v_1']  # Primer impulso
        self.delta_v2 = transfer_data['delta_v_2']  # Segundo impulso
        self.delta_v_total = transfer_data['delta_v_total']
        
        # Periodo de transferencia (medio periodo de la elipse)
        self.period_transfer = 2 * self.transfer_time
        
        # Estado de la simulación
        self.phase = 'initial'  # 'initial', 'transfer', 'final'
        self.time_in_phase = 0.0
        self.total_time = 0.0
        self.speed = 50.0  # Multiplicador de velocidad
        self.paused = False
        self.current_angle = 0.0
        
        # VTK objects
        self.renderer = None
        self.render_window = None
        self.interactor = None
        self.satellite_actor = None
        self.text_actor = None
        
        print(f"Configuración:")
        print(f"  LEO:  {h1_km} km (r = {self.r1:.0f} km)")
        print(f"  GEO:  {h2_km} km (r = {self.r2:.0f} km)")
        print(f"\nParámetros de transferencia:")
        print(f"  ΔV₁: {self.delta_v1:.1f} m/s")
        print(f"  ΔV₂: {self.delta_v2:.1f} m/s")
        print(f"  ΔV total: {self.delta_v_total:.1f} m/s")
        print(f"  Tiempo: {self.transfer_time/3600:.2f} horas")
        print(f"  Semi-eje mayor: {self.a_transfer/1000:.0f} km\n")
    
    
    def create_earth(self):
        """Crea Tierra con textura."""
        
        sphere = vtk.vtkSphereSource()
        sphere.SetCenter(0, 0, 0)
        sphere.SetRadius(self.R_earth)
        sphere.SetThetaResolution(100)
        sphere.SetPhiResolution(100)
        
        # Coordenadas de textura
        texture_coords = vtk.vtkTextureMapToSphere()
        texture_coords.SetInputConnection(sphere.GetOutputPort())
        texture_coords.PreventSeamOn()
        
        # Intentar cargar textura
        texture = None
        texture_file = 'models/textures/earth_day.jpg'
        
        if os.path.exists(texture_file):
            try:
                reader = vtk.vtkJPEGReader()
                reader.SetFileName(texture_file)
                reader.Update()
                
                texture = vtk.vtkTexture()
                texture.SetInputConnection(reader.GetOutputPort())
                texture.InterpolateOn()
            except:
                texture = None
        
        mapper = vtk.vtkPolyDataMapper()
        mapper.SetInputConnection(texture_coords.GetOutputPort())
        
        actor = vtk.vtkActor()
        actor.SetMapper(mapper)
        
        if texture:
            actor.SetTexture(texture)
        else:
            actor.GetProperty().SetColor(0.2, 0.5, 0.9)
        
        return actor
    
    
    def create_orbit_line(self, radius, color=(1, 1, 1), width=2):
        """Crea línea de órbita circular."""
        
        n_points = 100
        points = vtk.vtkPoints()
        
        for i in range(n_points + 1):
            angle = 2 * np.pi * i / n_points
            x = radius * np.cos(angle)
            y = radius * np.sin(angle)
            z = 0.0
            points.InsertNextPoint(x, y, z)
        
        line = vtk.vtkPolyLine()
        line.GetPointIds().SetNumberOfIds(n_points + 1)
        for i in range(n_points + 1):
            line.GetPointIds().SetId(i, i)
        
        cells = vtk.vtkCellArray()
        cells.InsertNextCell(line)
        
        polydata = vtk.vtkPolyData()
        polydata.SetPoints(points)
        polydata.SetLines(cells)
        
        mapper = vtk.vtkPolyDataMapper()
        mapper.SetInputData(polydata)
        
        actor = vtk.vtkActor()
        actor.SetMapper(mapper)
        actor.GetProperty().SetColor(color)
        actor.GetProperty().SetLineWidth(width)
        
        return actor
    
    
    def create_elliptical_orbit(self, r_peri, r_apo, color=(1, 0.5, 0), width=3):
        """
        Crea órbita elíptica de transferencia.
        
        Parameters
        ----------
        r_peri : float
            Radio periapsis (km)
        r_apo : float
            Radio apoapsis (km)
        color : tuple
            Color RGB
        width : float
            Ancho de línea
        """
        
        a = (r_peri + r_apo) / 2  # Semi-eje mayor
        e = (r_apo - r_peri) / (r_apo + r_peri)  # Excentricidad
        
        n_points = 200
        points = vtk.vtkPoints()
        
        for i in range(n_points + 1):
            # True anomaly
            nu = 2 * np.pi * i / n_points
            
            # Ecuación de órbita en coordenadas polares
            r = a * (1 - e**2) / (1 + e * np.cos(nu))
            
            x = r * np.cos(nu)
            y = r * np.sin(nu)
            z = 0.0
            
            points.InsertNextPoint(x, y, z)
        
        line = vtk.vtkPolyLine()
        line.GetPointIds().SetNumberOfIds(n_points + 1)
        for i in range(n_points + 1):
            line.GetPointIds().SetId(i, i)
        
        cells = vtk.vtkCellArray()
        cells.InsertNextCell(line)
        
        polydata = vtk.vtkPolyData()
        polydata.SetPoints(points)
        polydata.SetLines(cells)
        
        mapper = vtk.vtkPolyDataMapper()
        mapper.SetInputData(polydata)
        
        actor = vtk.vtkActor()
        actor.SetMapper(mapper)
        actor.GetProperty().SetColor(color)
        actor.GetProperty().SetLineWidth(width)
        
        return actor
    
    
    def create_impulse_marker(self, position, color=(1, 0, 0), label="ΔV"):
        """Crea marcador de impulso."""
        
        # Esfera
        sphere = vtk.vtkSphereSource()
        sphere.SetCenter(position)
        sphere.SetRadius(300)
        sphere.SetThetaResolution(20)
        sphere.SetPhiResolution(20)
        
        mapper = vtk.vtkPolyDataMapper()
        mapper.SetInputConnection(sphere.GetOutputPort())
        
        actor = vtk.vtkActor()
        actor.SetMapper(mapper)
        actor.GetProperty().SetColor(color)
        
        return actor
    
    
    def create_satellite(self):
        """Crea satélite."""
        
        cube = vtk.vtkCubeSource()
        cube.SetXLength(500)
        cube.SetYLength(500)
        cube.SetZLength(750)
        
        mapper = vtk.vtkPolyDataMapper()
        mapper.SetInputConnection(cube.GetOutputPort())
        
        actor = vtk.vtkActor()
        actor.SetMapper(mapper)
        actor.GetProperty().SetColor(1, 1, 1)
        
        return actor
    
    
    def get_satellite_position(self):
        """
        Calcula posición del satélite según fase actual.
        
        Returns
        -------
        position : tuple
            (x, y, z) en km
        """
        
        if self.phase == 'initial':
            # Órbita circular en LEO
            x = self.r1 * np.cos(self.current_angle)
            y = self.r1 * np.sin(self.current_angle)
            z = 0.0
            
        elif self.phase == 'transfer':
            # Órbita elíptica de transferencia
            a = self.a_transfer / 1000  # km
            e = (self.r2 - self.r1) / (self.r2 + self.r1)
            
            # True anomaly basado en tiempo (simplificado)
            # Para animación, usamos progresión lineal en ángulo
            progress = self.time_in_phase / self.transfer_time
            nu = np.pi * progress  # De 0 a π (medio periodo)
            
            r = a * (1 - e**2) / (1 + e * np.cos(nu))
            
            x = r * np.cos(nu)
            y = r * np.sin(nu)
            z = 0.0
            
        elif self.phase == 'final':
            # Órbita circular en GEO
            x = self.r2 * np.cos(self.current_angle)
            y = self.r2 * np.sin(self.current_angle)
            z = 0.0
        
        return (x, y, z)
    
    
    def update_simulation(self, dt):
        """
        Actualiza estado de la simulación.
        
        Parameters
        ----------
        dt : float
            Delta tiempo (segundos simulados)
        """
        
        self.total_time += dt
        self.time_in_phase += dt
        
        if self.phase == 'initial':
            # Orbitar en LEO hasta completar 1 órbita
            omega1 = 2 * np.pi / self.period1
            self.current_angle += omega1 * dt
            
            if self.current_angle >= 2 * np.pi:
                # Completó órbita inicial, comenzar transferencia
                print(f"\n⚡ IMPULSO 1: +{self.delta_v1:.1f} m/s")
                self.phase = 'transfer'
                self.time_in_phase = 0.0
                self.current_angle = 0.0
        
        elif self.phase == 'transfer':
            # En transferencia
            if self.time_in_phase >= self.transfer_time:
                # Completó transferencia, aplicar segundo impulso
                print(f"⚡ IMPULSO 2: +{self.delta_v2:.1f} m/s")
                self.phase = 'final'
                self.time_in_phase = 0.0
                self.current_angle = np.pi
        
        elif self.phase == 'final':
            # Orbitar en GEO
            omega2 = 2 * np.pi / self.period2
            self.current_angle += omega2 * dt
    
    
    def create_info_text(self):
        """Crea texto informativo."""
        
        text = vtk.vtkTextActor()
        text.GetTextProperty().SetFontSize(16)
        text.GetTextProperty().SetColor(1, 1, 1)
        text.GetTextProperty().SetBold(True)
        text.SetPosition(10, 10)
        
        return text
    
    
    def update_info_text(self):
        """Actualiza texto con estado actual."""
        
        phase_names = {
            'initial': 'ÓRBITA INICIAL (LEO)',
            'transfer': 'TRANSFERENCIA HOHMANN',
            'final': 'ÓRBITA FINAL (GEO)'
        }
        
        phase_colors = {
            'initial': '🔵',
            'transfer': '🟠',
            'final': '🟢'
        }
        
        status = "⏸️ PAUSADO" if self.paused else "▶️ ACTIVO"
        
        info = f"""HOHMANN TRANSFER SIMULATOR

Estado: {status}
Fase:   {phase_colors[self.phase]} {phase_names[self.phase]}
Tiempo total:     {self.total_time:.1f} s ({self.total_time/60:.2f} min)
Tiempo en fase:   {self.time_in_phase:.1f} s
Velocidad sim:    {self.speed:.0f}x

Parámetros:
  ΔV₁: {self.delta_v1:.1f} m/s  |  ΔV₂: {self.delta_v2:.1f} m/s
  ΔV total: {self.delta_v_total:.1f} m/s
  Tiempo transferencia: {self.transfer_time/3600:.2f} h

[+/-] Velocidad  [SPACE] Pausa  [R] Reset  [Q] Salir
"""
        self.text_actor.SetInput(info)
    
    
    def setup_renderer(self):
        """Configura renderer y escena."""
        
        # Renderer
        self.renderer = vtk.vtkRenderer()
        self.renderer.SetBackground(0, 0, 0)
        
        # Ventana
        self.render_window = vtk.vtkRenderWindow()
        self.render_window.SetSize(1600, 1000)
        self.render_window.AddRenderer(self.renderer)
        self.render_window.SetWindowName("Hohmann Transfer Simulator")
        
        # Interactor
        self.interactor = vtk.vtkRenderWindowInteractor()
        self.interactor.SetRenderWindow(self.render_window)
        
        # Tierra
        earth = self.create_earth()
        self.renderer.AddActor(earth)
        
        # Órbita inicial (azul)
        orbit1 = self.create_orbit_line(self.r1, color=(0.3, 0.5, 1.0), width=3)
        self.renderer.AddActor(orbit1)
        
        # Órbita final (verde)
        orbit2 = self.create_orbit_line(self.r2, color=(0.3, 1.0, 0.3), width=3)
        self.renderer.AddActor(orbit2)
        
        # Órbita de transferencia (naranja)
        transfer_orbit = self.create_elliptical_orbit(
            self.r1, self.r2, 
            color=(1.0, 0.6, 0.0), 
            width=4
        )
        self.renderer.AddActor(transfer_orbit)
        
        # Marcadores de impulso
        # ΔV₁ en periapsis (rojo)
        impulse1 = self.create_impulse_marker(
            (self.r1, 0, 0), 
            color=(1, 0, 0), 
            label="ΔV₁"
        )
        self.renderer.AddActor(impulse1)
        
        # ΔV₂ en apoapsis (verde)
        impulse2 = self.create_impulse_marker(
            (self.r2, 0, 0), 
            color=(0, 1, 0), 
            label="ΔV₂"
        )
        self.renderer.AddActor(impulse2)
        
        # Satélite
        self.satellite_actor = self.create_satellite()
        self.renderer.AddActor(self.satellite_actor)
        
        # Luz
        light = vtk.vtkLight()
        light.SetPosition(50000, 0, 0)
        light.SetFocalPoint(0, 0, 0)
        self.renderer.AddLight(light)
        
        # Texto
        self.text_actor = self.create_info_text()
        self.renderer.AddActor2D(self.text_actor)
        
        # Cámara
        camera = self.renderer.GetActiveCamera()
        camera.SetPosition(50000, 50000, 30000)
        camera.SetFocalPoint(0, 0, 0)
        self.renderer.ResetCamera()
        
        # Actualizar posición inicial
        pos = self.get_satellite_position()
        self.satellite_actor.SetPosition(pos)
        self.update_info_text()
    
    
    def animation_callback(self, obj, event):
        """Callback de animación."""
        
        if self.paused:
            return
        
        dt_real = 0.033  # ~30 FPS
        dt_sim = dt_real * self.speed
        
        self.update_simulation(dt_sim)
        
        pos = self.get_satellite_position()
        self.satellite_actor.SetPosition(pos)
        
        self.update_info_text()
        self.render_window.Render()
    
    
    def key_press_callback(self, obj, event):
        """Callback de teclado."""
        
        key = self.interactor.GetKeySym()
        
        if key in ['plus', 'equal']:
            self.speed *= 1.5
            print(f"Velocidad: {self.speed:.0f}x")
        
        elif key == 'minus':
            self.speed /= 1.5
            if self.speed < 1:
                self.speed = 1
            print(f"Velocidad: {self.speed:.0f}x")
        
        elif key == 'space':
            self.paused = not self.paused
            print("PAUSADO" if self.paused else "ACTIVO")
        
        elif key == 'r':
            self.phase = 'initial'
            self.time_in_phase = 0
            self.total_time = 0
            self.current_angle = 0
            print("RESET")
    
    
    def run(self):
        """Ejecuta simulación."""
        
        self.setup_renderer()
        
        # Callbacks
        self.interactor.AddObserver('TimerEvent', self.animation_callback)
        self.interactor.CreateRepeatingTimer(33)
        self.interactor.AddObserver('KeyPressEvent', self.key_press_callback)
        
        print("\n" + "─"*70)
        print("Controles:")
        print("  [+/-]   Velocidad simulación")
        print("  [SPACE] Pausar/Reanudar")
        print("  [R]     Reset")
        print("  Mouse   Rotar/Zoom/Pan")
        print("  [Q]     Salir")
        print("\nEl satélite completará:")
        print("  1. Una órbita en LEO (azul)")
        print("  2. Aplicar ΔV₁ (marcador rojo)")
        print("  3. Transferencia Hohmann (naranja)")
        print("  4. Aplicar ΔV₂ (marcador verde)")
        print("  5. Continuar en GEO (verde)")
        print("─"*70 + "\n")
        
        self.render_window.Render()
        self.interactor.Start()
        
        print("\n✓ Simulación cerrada\n")


if __name__ == "__main__":
    sim = HohmannTransferSimulator(h1_km=400, h2_km=35786)
    sim.run()