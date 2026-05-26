"""
Multi-Satellite Demo

Simulador VTK con múltiples satélites simultáneos.
Cada uno con diferentes parámetros de transferencia.

Author: Damián Zúñiga Avelar
Date: Mayo 2026
"""

import vtk
import numpy as np
import sys
import os
from collections import deque

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../..'))

from src.propagator import circular_velocity, orbital_period as calc_orbital_period
from src.delta_v import hohmann_transfer


class Satellite:
    """
    Clase que representa un satélite individual.
    """
    
    def __init__(self, name, h1_km, h2_km, color, start_angle=0.0):
        """
        Parameters
        ----------
        name : str
            Nombre del satélite
        h1_km : float
            Altitud inicial (km)
        h2_km : float
            Altitud final (km)
        color : tuple
            Color RGB (0-1)
        start_angle : float
            Ángulo inicial en órbita (radianes)
        """
        
        self.name = name
        self.h1 = h1_km
        self.h2 = h2_km
        self.color = color
        
        self.R_earth = 6371.0
        self.r1 = self.R_earth + h1_km
        self.r2 = self.R_earth + h2_km
        
        # Calcular parámetros
        r1_m = self.r1 * 1000
        r2_m = self.r2 * 1000
        
        transfer_data = hohmann_transfer(r1_m, r2_m)
        
        self.v1 = circular_velocity(r1_m)
        self.v2 = circular_velocity(r2_m)
        self.period1 = calc_orbital_period(r1_m)
        self.period2 = calc_orbital_period(r2_m)
        
        self.a_transfer = transfer_data['semi_major']
        self.transfer_time = transfer_data['transfer_time']
        self.delta_v1 = transfer_data['delta_v_1']
        self.delta_v2 = transfer_data['delta_v_2']
        self.delta_v_total = transfer_data['delta_v_total']
        
        # Estado
        self.phase = 'initial'
        self.time_in_phase = 0.0
        self.total_time = 0.0
        self.current_angle = start_angle
        
        # VTK actors
        self.actor = None
        self.trail_points = deque(maxlen=100)
        self.trail_actor = None
        
        print(f"  {name}: {h1_km} → {h2_km} km | ΔV: {self.delta_v_total:.0f} m/s")
    
    
    def create_actor(self):
        """Crea actor VTK del satélite."""
        
        # Geometría diferente según satélite
        cube = vtk.vtkCubeSource()
        cube.SetXLength(400)
        cube.SetYLength(400)
        cube.SetZLength(600)
        
        mapper = vtk.vtkPolyDataMapper()
        mapper.SetInputConnection(cube.GetOutputPort())
        
        actor = vtk.vtkActor()
        actor.SetMapper(mapper)
        actor.GetProperty().SetColor(self.color)
        actor.GetProperty().SetSpecular(0.6)
        actor.GetProperty().SetSpecularPower(30)
        
        self.actor = actor
        return actor
    
    
    def create_trail(self):
        """Crea estela del satélite."""
        
        self.trail_polydata = vtk.vtkPolyData()
        self.trail_points_vtk = vtk.vtkPoints()
        self.trail_polydata.SetPoints(self.trail_points_vtk)
        
        mapper = vtk.vtkPolyDataMapper()
        mapper.SetInputData(self.trail_polydata)
        
        actor = vtk.vtkActor()
        actor.SetMapper(mapper)
        actor.GetProperty().SetColor(self.color)
        actor.GetProperty().SetLineWidth(2)
        actor.GetProperty().SetOpacity(0.5)
        
        self.trail_actor = actor
        return actor
    
    
    def update_trail(self, position):
        """Actualiza estela."""
        
        self.trail_points.append(position)
        
        self.trail_points_vtk.Reset()
        for p in self.trail_points:
            self.trail_points_vtk.InsertNextPoint(p)
        
        if len(self.trail_points) > 1:
            line = vtk.vtkPolyLine()
            line.GetPointIds().SetNumberOfIds(len(self.trail_points))
            for i in range(len(self.trail_points)):
                line.GetPointIds().SetId(i, i)
            
            cells = vtk.vtkCellArray()
            cells.InsertNextCell(line)
            
            self.trail_polydata.SetLines(cells)
        
        self.trail_polydata.Modified()
    
    
    def get_position(self):
        """
        Calcula posición actual.
        
        Returns
        -------
        position : tuple
            (x, y, z) en km
        """
        
        if self.phase == 'initial':
            x = self.r1 * np.cos(self.current_angle)
            y = self.r1 * np.sin(self.current_angle)
            z = 0.0
            
        elif self.phase == 'transfer':
            a = self.a_transfer / 1000
            e = (self.r2 - self.r1) / (self.r2 + self.r1)
            
            progress = self.time_in_phase / self.transfer_time
            nu = np.pi * progress
            
            r = a * (1 - e**2) / (1 + e * np.cos(nu))
            
            x = r * np.cos(nu)
            y = r * np.sin(nu)
            z = 0.0
            
        elif self.phase == 'final':
            x = self.r2 * np.cos(self.current_angle)
            y = self.r2 * np.sin(self.current_angle)
            z = 0.0
        
        return (x, y, z)
    
    
    def update(self, dt):
        """
        Actualiza estado del satélite.
        
        Parameters
        ----------
        dt : float
            Delta tiempo (segundos)
        """
        
        self.total_time += dt
        self.time_in_phase += dt
        
        if self.phase == 'initial':
            omega1 = 2 * np.pi / self.period1
            self.current_angle += omega1 * dt
            
            if self.current_angle >= 2 * np.pi:
                self.phase = 'transfer'
                self.time_in_phase = 0.0
                self.current_angle = 0.0
                self.trail_points.clear()
        
        elif self.phase == 'transfer':
            if self.time_in_phase >= self.transfer_time:
                self.phase = 'final'
                self.time_in_phase = 0.0
                self.current_angle = np.pi  # Empezar en apoapsis
        
        elif self.phase == 'final':
            omega2 = 2 * np.pi / self.period2
            self.current_angle += omega2 * dt
        
        # Actualizar posición y trail
        pos = self.get_position()
        self.actor.SetPosition(pos)
        self.update_trail(pos)


class MultiSatelliteSimulator:
    """Simulador con múltiples satélites."""
    
    def __init__(self):
        """Inicializa simulador."""
        
        print(f"\n{'='*70}")
        print(f"  MULTI-SATELLITE SIMULATOR")
        print(f"{'='*70}\n")
        
        # Estado global
        self.speed = 100.0
        self.paused = False
        self.show_trails = True
        
        # VTK
        self.renderer = None
        self.render_window = None
        self.interactor = None
        self.text_actor = None
        
        # Crear flota de satélites
        print("Configurando satélites:\n")
        
        self.satellites = [
            Satellite("SAT-A", 400, 20200, (1.0, 0.3, 0.3), start_angle=0.0),      # Rojo - LEO→MEO
            Satellite("SAT-B", 400, 35786, (0.3, 1.0, 0.3), start_angle=np.pi/2),  # Verde - LEO→GEO
            Satellite("SAT-C", 550, 35786, (0.3, 0.3, 1.0), start_angle=np.pi),    # Azul - Starlink→GEO
            Satellite("SAT-D", 800, 20200, (1.0, 1.0, 0.3), start_angle=3*np.pi/2), # Amarillo - Custom
            Satellite("SAT-E", 1000, 35786, (1.0, 0.3, 1.0), start_angle=np.pi/4),  # Magenta - Custom
        ]
        
        print(f"\n{len(self.satellites)} satélites configurados\n")
    
    
    def create_earth(self):
        """Crea Tierra."""
        
        sphere = vtk.vtkSphereSource()
        sphere.SetCenter(0, 0, 0)
        sphere.SetRadius(6371.0)
        sphere.SetThetaResolution(100)
        sphere.SetPhiResolution(100)
        
        texture_coords = vtk.vtkTextureMapToSphere()
        texture_coords.SetInputConnection(sphere.GetOutputPort())
        texture_coords.PreventSeamOn()
        
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
                pass
        
        mapper = vtk.vtkPolyDataMapper()
        mapper.SetInputConnection(texture_coords.GetOutputPort())
        
        actor = vtk.vtkActor()
        actor.SetMapper(mapper)
        
        if texture:
            actor.SetTexture(texture)
        else:
            actor.GetProperty().SetColor(0.2, 0.5, 0.9)
        
        return actor
    
    
    def create_orbit_rings(self):
        """Crea anillos de órbitas comunes."""
        
        actors = []
        
        # Órbitas de referencia
        orbits = [
            (6771, (0.5, 0.5, 0.5), 1, "LEO 400 km"),      # Gris
            (26571, (0.7, 0.7, 0.3), 1, "MEO 20,200 km"),  # Amarillo pálido
            (42157, (0.3, 0.7, 0.3), 1, "GEO 35,786 km"),  # Verde pálido
        ]
        
        for radius, color, width, label in orbits:
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
            actor.GetProperty().SetOpacity(0.3)
            
            actors.append(actor)
        
        return actors
    
    
    def create_info_text(self):
        """Crea texto informativo."""
        
        text = vtk.vtkTextActor()
        text.GetTextProperty().SetFontSize(14)
        text.GetTextProperty().SetColor(1, 1, 1)
        text.GetTextProperty().SetBold(True)
        text.SetPosition(10, 10)
        
        return text
    
    
    def update_info_text(self):
        """Actualiza texto."""
        
        status = "⏸️ PAUSADO" if self.paused else "▶️ ACTIVO"
        trails = "ON" if self.show_trails else "OFF"
        
        # Contar satélites por fase
        phases = {'initial': 0, 'transfer': 0, 'final': 0}
        for sat in self.satellites:
            phases[sat.phase] += 1
        
        # Info de cada satélite
        sat_info = []
        for sat in self.satellites:
            phase_emoji = {
                'initial': '🔵',
                'transfer': '🟠',
                'final': '🟢'
            }
            emoji = phase_emoji[sat.phase]
            sat_info.append(f"{emoji} {sat.name}: {sat.total_time/60:.1f}min")
        
        info = f"""MULTI-SATELLITE SIMULATOR

Estado: {status} | Velocidad: {self.speed:.0f}x | Trails: {trails}

Satélites por fase:
  🔵 Inicial: {phases['initial']}  🟠 Transfer: {phases['transfer']}  🟢 Final: {phases['final']}

{chr(10).join(sat_info)}

[+/-] Velocidad  [SPACE] Pausa  [T] Trails  [R] Reset  [Q] Salir
"""
        self.text_actor.SetInput(info)
    
    
    def setup_renderer(self):
        """Configura escena."""
        
        self.renderer = vtk.vtkRenderer()
        self.renderer.SetBackground(0.0, 0.0, 0.05)  # Azul muy oscuro
        
        self.render_window = vtk.vtkRenderWindow()
        self.render_window.SetSize(1800, 1000)
        self.render_window.AddRenderer(self.renderer)
        self.render_window.SetWindowName("Multi-Satellite Simulator")
        
        self.interactor = vtk.vtkRenderWindowInteractor()
        self.interactor.SetRenderWindow(self.render_window)
        
        # Tierra
        earth = self.create_earth()
        self.renderer.AddActor(earth)
        
        # Anillos de órbitas
        for ring in self.create_orbit_rings():
            self.renderer.AddActor(ring)
        
        # Satélites y trails
        for sat in self.satellites:
            sat_actor = sat.create_actor()
            self.renderer.AddActor(sat_actor)
            
            trail_actor = sat.create_trail()
            self.renderer.AddActor(trail_actor)
        
        # Luz
        light = vtk.vtkLight()
        light.SetPosition(50000, 20000, 30000)
        light.SetFocalPoint(0, 0, 0)
        light.SetIntensity(1.2)
        self.renderer.AddLight(light)
        
        # Luz ambiental
        ambient = vtk.vtkLight()
        ambient.SetPosition(-50000, -20000, 30000)
        ambient.SetIntensity(0.3)
        self.renderer.AddLight(ambient)
        
        # Texto
        self.text_actor = self.create_info_text()
        self.renderer.AddActor2D(self.text_actor)
        
        # Cámara
        camera = self.renderer.GetActiveCamera()
        camera.SetPosition(60000, 60000, 40000)
        camera.SetFocalPoint(0, 0, 0)
        self.renderer.ResetCamera()
        
        self.update_info_text()
    
    
    def animation_callback(self, obj, event):
        """Callback animación."""
        
        if self.paused:
            return
        
        dt_real = 0.033
        dt_sim = dt_real * self.speed
        
        # Actualizar todos los satélites
        for sat in self.satellites:
            sat.update(dt_sim)
        
        self.update_info_text()
        self.render_window.Render()
    
    
    def key_press_callback(self, obj, event):
        """Callback teclado."""
        
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
        
        elif key == 't':
            self.show_trails = not self.show_trails
            for sat in self.satellites:
                sat.trail_actor.SetVisibility(self.show_trails)
            print(f"Trails: {'ON' if self.show_trails else 'OFF'}")
        
        elif key == 'r':
            # Reset todos los satélites
            for i, sat in enumerate(self.satellites):
                sat.phase = 'initial'
                sat.time_in_phase = 0
                sat.total_time = 0
                sat.current_angle = i * (2 * np.pi / len(self.satellites))
                sat.trail_points.clear()
            print("RESET ALL")
    
    
    def run(self):
        """Ejecuta simulación."""
        
        self.setup_renderer()
        
        self.interactor.AddObserver('TimerEvent', self.animation_callback)
        self.interactor.CreateRepeatingTimer(33)
        self.interactor.AddObserver('KeyPressEvent', self.key_press_callback)
        
        print("─"*70)
        print("CONTROLES:")
        print("  [+/-]   Velocidad")
        print("  [SPACE] Pausa")
        print("  [T]     Toggle trails")
        print("  [R]     Reset all")
        print("  Mouse   Rotar/Zoom/Pan")
        print("  [Q]     Salir")
        print("─"*70 + "\n")
        
        self.render_window.Render()
        self.interactor.Start()
        
        print("\n✓ Simulación cerrada\n")


if __name__ == "__main__":
    sim = MultiSatelliteSimulator()
    sim.run()